document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search');
    const suggestions = document.getElementById('suggestions');

    searchInput.addEventListener('input', function () {
        const query = this.value;
        if (query.length > 1) {
            fetch(`/autocomplete?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
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
        } else {
            suggestions.innerHTML = '';
        }
    });
});
