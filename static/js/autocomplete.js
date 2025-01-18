const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

const STORAGE_KEYS = {
    LRU: 'autocomplete_lru',
    LAST_CLEANUP: 'autocomplete_cleanup'
};

const CACHE_DURATION = 5 * 60 * 1000;

class LRUCache {
    constructor(maxSize = 100) {
        this.cache = new Map();
        this.maxSize = maxSize;
    }

    get(key) {
        const item = this.cache.get(key);
        if (item && Date.now() - item.timestamp < CACHE_DURATION) {
            this.cache.delete(key);
            this.cache.set(key, item);
            return item.data;
        }
        return null;
    }

    set(key, value) {
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(key, {
            data: value,
            timestamp: Date.now()
        });
    }
}

class PersistentLRUCache extends LRUCache {
    constructor(maxSize = 100) {
        super(maxSize);
        this.loadFromStorage();
    }

    loadFromStorage() {
        const stored = localStorage.getItem(STORAGE_KEYS.LRU);
        if (stored) {
            const data = JSON.parse(stored);
            data.forEach(([key, value]) => {
                if (value == null) {
                    return;
                }
                this.cache.set(key, value.data);
            });
        }
    }

    saveToStorage() {
        const data = Array.from(this.cache.entries());
        localStorage.setItem(STORAGE_KEYS.LRU, JSON.stringify(data));
    }

    set(key, value) {
        super.set(key, value);
        this.saveToStorage();
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search');
    const suggestions = document.getElementById('suggestions');

    const cache = new PersistentLRUCache();

    function cleanupOldCache() {
        const lastCleanup = localStorage.getItem(STORAGE_KEYS.LAST_CLEANUP);
        const now = Date.now();

        if (!lastCleanup || now - parseInt(lastCleanup) > CACHE_DURATION) {
            const stored = localStorage.getItem(STORAGE_KEYS.LRU);
            if (stored) {
                const data = JSON.parse(stored);
                const validData = data.filter(([_, value]) =>
                    value?.timestamp != null && now - value.timestamp < CACHE_DURATION
                );
                localStorage.setItem(STORAGE_KEYS.LRU, JSON.stringify(validData));
            }

            localStorage.setItem(STORAGE_KEYS.LAST_CLEANUP, now.toString());
        }
    }

    cleanupOldCache();

    const handleSearch = debounce(function(query) {
        if (query.length > 1) {
            const results = cache.get(query);
            if (results) {
                displayResults(results);
                return;
            }

            suggestions.innerHTML = '<div class="loading">Searching...</div>';
            fetch(`/autocomplete?query=${encodeURIComponent(query)}`)
                .then(response => {
                    if (response.status < 400) {
                        return response;
                    }

                    throw new Error(response.statusText);
                })
                .then(response => response.json())
                .then(data => {
                    if (data == null) {
                        throw new Error('No autocomplete data returned');
                    }

                    cache.set(query, data);
                    displayResults(data);
                })
                .catch(error => {
                    suggestions.innerHTML = 'An error occurred while searching';
                    console.error('Search error:', error);
                });
        } else if (query.length === 1) {
            suggestions.innerHTML = 'Please enter at least two characters to search';
        } else {
            suggestions.innerHTML = '';
        }
    }, 300);

    function displayResults(data) {
        if (data.length === 0) {
            suggestions.innerHTML = `No results found for "${searchInput.value}"`;
            return;
        }

        suggestions.innerHTML = '';
        data.forEach(item => {
            const li = document.createElement('li');
            const aliases = item.aliases.length ? `(${item.aliases.join(', ')})` : '';
            li.innerHTML = `<strong>${item.pretty_name}</strong> <small>${aliases}</small>`;
            li.addEventListener('click', () => {
                window.location.href = `/substance/${item.slug}`;
            });
            suggestions.appendChild(li);
        });
    }

    searchInput.addEventListener('input', function() {
        handleSearch(this.value);
    });
});
