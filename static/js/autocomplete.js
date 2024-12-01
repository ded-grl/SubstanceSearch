document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search');
    const suggestions = document.getElementById('suggestions');
    let debounceTimer;

    // Add error handling for missing elements
    if (!searchInput || !suggestions) {
        console.error('Required elements not found');
        return;
    }

    // Add keyboard navigation
    const handleKeyboard = (e) => {
        const items = suggestions.getElementsByTagName('li');
        const current = suggestions.querySelector('.selected');
        let next;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                next = current ? current.nextElementSibling || items[0] : items[0];
                break;
            case 'ArrowUp':
                e.preventDefault();
                next = current ? current.previousElementSibling || items[items.length - 1] : items[items.length - 1];
                break;
            case 'Enter':
                if (current) {
                    e.preventDefault();
                    current.click();
                }
                return;
            case 'Escape':
                suggestions.innerHTML = '';
                searchInput.blur();
                return;
        }

        if (next) {
            if (current) current.classList.remove('selected');
            next.classList.add('selected');
            next.scrollIntoView({ block: 'nearest' });
        }
    };

    // Debounced search handler
    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        debounceTimer = setTimeout(() => {
            if (query.length > 1) {
                fetchSuggestions(query);
            } else {
                suggestions.innerHTML = '';
            }
        }, 300); // 300ms debounce
    });

    // Separate fetch logic
    async function fetchSuggestions(query) {
        try {
            const response = await fetch(`/autocomplete?query=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            updateSuggestions(data);
        } catch (error) {
            console.error('Failed to fetch suggestions:', error);
            suggestions.innerHTML = '<li class="error">Failed to load suggestions</li>';
        }
    }

    // Separate DOM update logic
    function updateSuggestions(data) {
        suggestions.innerHTML = '';
        
        if (data.length === 0) {
            suggestions.innerHTML = '<li class="no-results">No matches found</li>';
            return;
        }

        data.forEach(item => {
            const li = document.createElement('li');
            const aliases = item.aliases?.length ? `(${item.aliases.join(', ')})` : '';
            
            li.innerHTML = `
                <strong>${escapeHtml(item.pretty_name)}</strong>
                <small>${escapeHtml(aliases)}</small>
            `;

            li.addEventListener('click', () => {
                window.location.href = `/substance/${encodeURIComponent(item.slug)}`;
            });

            suggestions.appendChild(li);
        });
    }

    // Helper function to prevent XSS
    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // Event listeners
    searchInput.addEventListener('keydown', handleKeyboard);
    document.addEventListener('click', (e) => {
        if (!suggestions.contains(e.target) && e.target !== searchInput) {
            suggestions.innerHTML = '';
        }
    });

    // Add some basic styling
    const style = document.createElement('style');
    style.textContent = `
        #suggestions li {
            cursor: pointer;
            padding: 8px;
        }
        #suggestions li:hover, #suggestions li.selected {
            background-color: #f0f0f0;
        }
        #suggestions li.error, #suggestions li.no-results {
            color: #666;
            font-style: italic;
        }
    `;
    document.head.appendChild(style);
});