const COOKIE_NAME = 'Theme';
const ACCEPTED_THEMES = ['light', 'dark'];
let currentTheme;

function fetchTheme() {
	let theme = Cookies.get(COOKIE_NAME);
	if (theme) {
		// if user has theme cookie set but it's not in the
		// accepted list, default to the first theme in the list
		// (light theme)
		if (!ACCEPTED_THEMES.includes(theme)) {
			theme = ACCEPTED_THEMES[0];
			setTheme(theme);
		}

		currentTheme = theme;
		return theme;
	}

	// check if user has dark mode enabled
	if (window.matchMedia?.('(prefers-color-scheme: dark)')?.matches) {
		setTheme('dark');
		return 'dark';
	}

	// default to light theme
	setTheme('light');
	return 'light';
}

function setTheme(theme) {
	if (!ACCEPTED_THEMES.includes(theme)) theme = ACCEPTED_THEMES[0];

	currentTheme = theme;
	Cookies.set(COOKIE_NAME, theme);
	document.body.classList.remove(...ACCEPTED_THEMES);
	document.body.classList.add(theme);
	updateToggleButton();
}

function toggleTheme() {
	const currentTheme = fetchTheme();
	const newTheme = currentTheme === 'light' ? 'dark' : 'light';
	setTheme(newTheme);
}

function updateToggleButton() {
	// show the icon for the current theme
	const iconName = `#theme-icon-${currentTheme === 'light' ? 'moon' : 'sun'}`;
	const icon = document.querySelector(iconName);
	if (icon) {
		if (icon.style.display === 'block') return;
		icon.style.display = 'block';
	}


	// hide all existing icons
	const icons = document.querySelectorAll(`.theme-icon:not(${iconName})`);
	icons.forEach(icon => icon.style.display = 'none');
}

function pollTheme() {
	const theme = fetchTheme();
	updateToggleButton();

	if (!document.body.classList.contains(theme)) {
		document.body.classList.remove(...ACCEPTED_THEMES);
		document.body.classList.add(theme);
	}
}

/** Fetch and set theme on page load */
document.addEventListener('DOMContentLoaded', () => {
	pollTheme();
	setInterval(() => pollTheme(), 1000);
});

