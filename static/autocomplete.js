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

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search');
    const suggestions = document.getElementById('suggestions');
    
    const handleSearch = debounce(function(query) {
        if (query.length > 1) {
            fetch(`/autocomplete?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.length === 0) {
                        suggestions.innerHTML = `No results found for "${query}"`;
                        return;
                    }

                    suggestions.innerHTML = '';
                    data.forEach(item => {
                        const li = document.createElement('li');
                        const aliases = item.aliases.length ? `(${item.aliases.join(', ')})` : '';
                        li.innerHTML = `<strong>${item.pretty_name}</strong> <small>${aliases}</small>`;
                        li.addEventListener('click', () => {
                            // Use the slug instead of pretty_name
                            window.location.href = `/substance/${item.slug}`;
                        });
                        suggestions.appendChild(li);
                    });
                });
        } else if (query.length === 1) {
            suggestions.innerHTML = 'Please enter at least two characters to search';
        } else {
            suggestions.innerHTML = '';
        }
    }, 300); // 300ms delay

    searchInput.addEventListener('input', function() {
        handleSearch(this.value);
    });
});
