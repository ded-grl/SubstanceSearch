const THEME_CFG = {
	COOKIE_NAME: "Theme",
	ACCEPTED: Object.freeze({
		Light: "light",
		Dark: "dark",
	}),
};

const cookies = Cookies.withAttributes({
	expires: 365,
	secure: window.location.protocol === "https:",
	sameSite: "strict",
})

function fetchTheme() {
	let theme = cookies.get(THEME_CFG.COOKIE_NAME);
	if (theme) {
		// if user has theme cookie set but it's not in the
		// accepted list, default to the first theme in the list
		// (light theme)
		if (!Object.values(THEME_CFG.ACCEPTED).includes(theme)) {
			theme = THEME_CFG.ACCEPTED.Light;
			setTheme(theme);
		}

		return theme;
	}

	// check if user has dark mode enabled
	if (window.matchMedia?.("(prefers-color-scheme: dark)")?.matches) {
		return THEME_CFG.ACCEPTED.Dark;
	}

	// default to light theme
	return THEME_CFG.ACCEPTED.Light;
}

function setTheme(theme) {
	if (!Object.values(THEME_CFG.ACCEPTED).includes(theme)) {
		theme = THEME_CFG.ACCEPTED.Light;
	}

	cookies.set(THEME_CFG.COOKIE_NAME, theme);

	updateBodyTheme(theme);
	updateThemeToggle(theme);
}

function toggleTheme() {
	const theme = fetchTheme();
	const newTheme =
		theme === THEME_CFG.ACCEPTED.Light
			? THEME_CFG.ACCEPTED.Dark
			: THEME_CFG.ACCEPTED.Light;

	setTheme(newTheme);
}

function updateBodyTheme(theme) {
	if (document.body.classList.contains(theme)) return;
	const acceptedThemes = Object.values(THEME_CFG.ACCEPTED);
	document.body.classList.remove(...acceptedThemes);
	document.body.classList.add(theme);
}

function updateThemeToggle(theme) {
	if (!theme) theme = fetchTheme();

	const iconName = theme === THEME_CFG.ACCEPTED.Light ? "moon" : "sun";
	const iconSelector = `#theme-icon-${iconName}`;
	const icon = document.querySelector(iconSelector);
	if (!icon) return;

	if (icon.style.display === "block") return;
	icon.style.display = "block";

	// hide all existing icons
	const icons = document.querySelectorAll(`.theme-icon:not(${iconSelector})`);
	icons.forEach((icon) => (icon.style.display = "none"));
}

function checkTheme() {
	const theme = fetchTheme();
	updateBodyTheme(theme);
	updateThemeToggle(theme);
}

document.addEventListener("DOMContentLoaded", () => {
	checkTheme();
});

window.addEventListener("pageshow", (ev) => {
	if (!ev.persisted) return;
	checkTheme();
});
