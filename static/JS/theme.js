// Colour theme switch: buttons marked data-theme-toggle cycle between following the
// device, light and dark. The choice is kept in localStorage; the inline script in
// base.html applies it before the page is drawn.
(function () {
  const ORDER = ['auto', 'light', 'dark'];
  const ICONS = { auto: 'bi-circle-half', light: 'bi-sun', dark: 'bi-moon-stars' };
  const root = document.documentElement;

  const current = () => root.dataset.theme || 'auto';

  function render() {
    const mode = current();
    document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
      const label = button.dataset['label' + mode[0].toUpperCase() + mode.slice(1)];
      button.setAttribute('aria-label', label);
      button.title = label;
      button.querySelector('i').className = 'bi ' + ICONS[mode];
      const text = button.querySelector('[data-theme-label]');
      if (text) text.textContent = label;
    });
  }

  function setTheme(mode) {
    if (mode === 'auto') delete root.dataset.theme;
    else root.dataset.theme = mode;
    try {
      if (mode === 'auto') localStorage.removeItem('theme');
      else localStorage.setItem('theme', mode);
    } catch (e) {
      // Storage can be unavailable (private mode); the choice then lasts for this page.
    }
    render();
  }

  document.addEventListener('click', (event) => {
    if (!event.target.closest('[data-theme-toggle]')) return;
    setTheme(ORDER[(ORDER.indexOf(current()) + 1) % ORDER.length]);
  });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', render);
  else render();
})();
