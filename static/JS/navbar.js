// Navigation menus: the "About us" dropdown in the top banner and the vertical
// menu that folds out of the bottom wave on phones. Both use a button with
// aria-controls pointing at the menu it opens.
(function () {
  function init() {
    if (window.__navbarInitialized) return;
    window.__navbarInitialized = true;

    const toggles = Array.from(document.querySelectorAll('[data-menu-toggle]'));

    function setOpen(toggle, open) {
      const menu = document.getElementById(toggle.getAttribute('aria-controls'));
      if (!menu) return;
      menu.hidden = !open;
      toggle.setAttribute('aria-expanded', String(open));
      const backdrop = toggle.dataset.backdrop && document.getElementById(toggle.dataset.backdrop);
      if (backdrop) backdrop.hidden = !open;
    }
    const closeAll = (except) => toggles.forEach((t) => { if (t !== except) setOpen(t, false); });

    toggles.forEach((toggle) => {
      toggle.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        const open = toggle.getAttribute('aria-expanded') !== 'true';
        closeAll(toggle);
        setOpen(toggle, open);
      });
    });

    document.addEventListener('click', (event) => {
      toggles.forEach((toggle) => {
        const menu = document.getElementById(toggle.getAttribute('aria-controls'));
        if (menu && !menu.contains(event.target)) setOpen(toggle, false);
      });
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeAll();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
