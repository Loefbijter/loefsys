function initNavbar() {
    if (window.__navbarInitialized) {
        return;
    }
    window.__navbarInitialized = true;

    // handle any About toggles (desktop + mobile). Uses data-target attribute on the toggle button
    const toggles = document.querySelectorAll('.about-toggle');

    toggles.forEach(function(toggle) {
        const targetSelector = toggle.dataset.target;
        if (!targetSelector) return;
        const dropdown = document.querySelector(targetSelector);
        const chevron = toggle.querySelector('.about-chevron') || toggle.querySelector('svg');

        // initialize state
        if (dropdown && dropdown.classList.contains('hidden')) {
            if (chevron) chevron.style.transform = 'rotate(0deg)';
            toggle.setAttribute('aria-expanded', 'false');
        }

        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            if (!dropdown) return;
            const isHidden = dropdown.classList.contains('hidden');

            if (isHidden) {
                // open this dropdown
                dropdown.classList.remove('hidden');
                toggle.setAttribute('aria-expanded', 'true');
                if (chevron) chevron.style.transform = 'rotate(180deg)';
            } else {
                // close this dropdown
                dropdown.classList.add('hidden');
                toggle.setAttribute('aria-expanded', 'false');
                if (chevron) chevron.style.transform = 'rotate(0deg)';
            }
        });
    });

    // close when clicking outside any about dropdown
    document.addEventListener('click', function(e) {
        document.querySelectorAll('.about-dropdown').forEach(function(dropdown) {
            const selector = '#' + dropdown.id;
            const relatedToggle = Array.from(toggles).find(t => t.dataset.target === selector);
            if (!relatedToggle) return;
            if (!relatedToggle.contains(e.target) && !dropdown.contains(e.target)) {
                if (!dropdown.classList.contains('hidden')) {
                    dropdown.classList.add('hidden');
                    relatedToggle.setAttribute('aria-expanded', 'false');
                    const chevron = relatedToggle.querySelector('.about-chevron') || relatedToggle.querySelector('svg');
                    if (chevron) chevron.style.transform = 'rotate(0deg)';
                }
            }
        });
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const mobileToggleCheckbox = document.getElementById('mobile-menu-toggle-checkbox');
            if (mobileToggleCheckbox && mobileToggleCheckbox.checked) {
                mobileToggleCheckbox.checked = false;
            }
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavbar);
} else {
    initNavbar();
}
