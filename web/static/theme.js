const themeToggle = document.getElementById('theme-toggle');
const htmlElement = document.documentElement;
const themeIcon = themeToggle.querySelector('.theme-icon');

const THEME_KEY = 'boozydb-theme';
const DARK_THEME = 'dark';
const LIGHT_THEME = 'light';

function setTheme(theme) {
    if (theme === LIGHT_THEME) {
        htmlElement.setAttribute('data-theme', 'light');
        themeIcon.textContent = '☀️';
    } else {
        htmlElement.removeAttribute('data-theme');
        themeIcon.textContent = '🌙';
    }
    localStorage.setItem(THEME_KEY, theme);
}

function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? DARK_THEME : LIGHT_THEME);
    setTheme(theme);
}

themeToggle.addEventListener('click', () => {
    const currentTheme = htmlElement.getAttribute('data-theme') === 'light' ? LIGHT_THEME : DARK_THEME;
    const newTheme = currentTheme === DARK_THEME ? LIGHT_THEME : DARK_THEME;
    setTheme(newTheme);
});

initTheme();
