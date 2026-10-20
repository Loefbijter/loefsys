// Tabs and fold-out cards on the information pages (skippership levels,
// training and skippership). Tabs are [data-tab-trigger] buttons that show the
// [data-tab-panel] with id "panel-<data-tab>"; a [data-accordion-trigger] opens
// the element its aria-controls points to.
document.addEventListener("DOMContentLoaded", function () {
    var tabTriggers = document.querySelectorAll("[data-tab-trigger]");
    var tabPanels = document.querySelectorAll("[data-tab-panel]");

    tabTriggers.forEach(function (trigger) {
        trigger.addEventListener("click", function () {
            var target = trigger.getAttribute("data-tab");

            tabTriggers.forEach(function (t) {
                var active = t === trigger;
                t.setAttribute("aria-selected", active ? "true" : "false");
                t.classList.toggle("bg-primary", active);
                t.classList.toggle("text-white", active);
                t.classList.toggle("text-foreground/60", !active);
            });

            tabPanels.forEach(function (panel) {
                var isTarget = panel.id === "panel-" + target;
                panel.style.gridTemplateRows = isTarget ? "1fr" : "0fr";
                panel.toggleAttribute("inert", !isTarget);
            });
        });
    });

    document.querySelectorAll("[data-accordion-trigger]").forEach(function (trigger) {
        trigger.addEventListener("click", function () {
            var expanded = trigger.getAttribute("aria-expanded") === "true";
            var content = document.getElementById(trigger.getAttribute("aria-controls"));
            var chevron = trigger.querySelector("[data-chevron]");

            trigger.setAttribute("aria-expanded", expanded ? "false" : "true");
            content.style.gridTemplateRows = expanded ? "0fr" : "1fr";
            if (chevron) {
                chevron.style.transform = expanded ? "rotate(0deg)" : "rotate(180deg)";
            }
        });
    });
});
