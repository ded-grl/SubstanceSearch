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

class TrieNode {
    constructor() {
        this.children = {};
        this.isEndOfWord = false;
        this.data = null;
    }
}

class Trie {
    constructor() {
        this.root = new TrieNode();
    }

    insert(word, data) {
        let current = this.root;
        for (let char of word.toLowerCase()) {
            if (!current.children[char]) {
                current.children[char] = new TrieNode();
            }
            current = current.children[char];
        }
        current.isEndOfWord = true;
        current.data = data;
    }

    search(prefix) {
        let current = this.root;
        let results = [];
        
        for (let char of prefix.toLowerCase()) {
            if (!current.children[char]) return results;
            current = current.children[char];
        }
        
x
        this._collectWords(current, prefix, results);
        return results;
    }

    _collectWords(node, prefix, results) {
        if (node.isEndOfWord) {
            results.push({
                term: prefix,
                data: node.data
            });
        }
                
        for (let char in node.children) {
            this._collectWords(node.children[char], prefix + char, results);
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search');
    const suggestions = document.getElementById('suggestions');
    const CACHE_DURATION = 5 * 60 * 1000;
    const cache = new LRUCache();
    const trie = new Trie();
    
    const handleSearch = debounce(function(query) {
        if (query.length > 1) {
            const trieResults = trie.search(query);
            if (trieResults.length > 0) {
                displayResults(trieResults.map(r => r.data));
                return;
            }

            const cached = cache.get(query);
            if (cached) {
                displayResults(cached);
                return;
            }

            suggestions.innerHTML = '<div class="loading">Searching...</div>';
            fetch(`/autocomplete?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    cache.set(query, data);
                    data.forEach(item => {
                        trie.insert(item.pretty_name, item);
                        if (item.aliases) {
                            item.aliases.forEach(alias => trie.insert(alias, item));
                        }
                    });
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
