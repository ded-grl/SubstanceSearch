let timeout;
function debounce(func, wait = 250) {
	return function (...args) {
		clearTimeout(timeout);

		timeout = setTimeout(() => {
			clearTimeout(timeout);
			func.apply(this, args);
		}, wait);
	};
}

document.addEventListener('DOMContentLoaded', () => {
	const searchInput = document.getElementById('search');
	const suggestions = document.getElementById('suggestions');

	searchInput.addEventListener('input', function () {
		const query = this.value;
		if (query.length > 1) {
			debounce(() => {
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
				},
				250,
			)();
		} else if (query.length === 1) {
			suggestions.innerHTML = 'Please enter at least two characters to search';
		} else {
			suggestions.innerHTML = '';
		}
	});
});
