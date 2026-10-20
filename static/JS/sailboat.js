// Moves the sailboat along the bottom wave as the page scrolls (desktop only).
// The boat only shows on pages that are at least twice the window height.
// The wave formula must match loefsys/theme/templatetags/waves.py ("bottom", front layer).
(function () {
  const BASE = 66, AMP = 6, PHASE = 2.2;
  const waveY = (x) => {
    const tau = Math.PI * 2;
    return BASE + AMP * (0.62 * Math.sin(x * tau * 1.3 + PHASE) + 0.38 * Math.sin(x * tau * 3.1 + PHASE * 1.7));
  };

  function init() {
    const wave = document.querySelector('.footwave');
    const boat = wave && wave.querySelector('.sailboat');
    if (!boat) return;

    let queued = false;
    function place() {
      queued = false;
      const doc = document.documentElement;
      const width = wave.clientWidth;
      const scrollable = doc.scrollHeight - window.innerHeight;
      const visible = width > 0 && doc.scrollHeight >= 2 * window.innerHeight;
      boat.classList.toggle('is-visible', visible);
      if (!visible) return;

      const progress = scrollable > 0 ? Math.min(1, Math.max(0, window.scrollY / scrollable)) : 0;
      const x = 30 + progress * (width - 60);
      const y = waveY(x / width);
      const slope = (waveY((x + 2) / width) - waveY((x - 2) / width)) / 4;
      boat.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) rotate(${(Math.atan(slope) * 180 / Math.PI).toFixed(1)}deg)`;
    }
    const schedule = () => { if (!queued) { queued = true; requestAnimationFrame(place); } };

    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    if ('ResizeObserver' in window) new ResizeObserver(schedule).observe(document.body);
    place();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
