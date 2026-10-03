// Client-side filtering for grouped lists such as the skippers page.
// Inside a [data-list-filter] container:
//   [data-filter-input]           text box; matches against [data-filter-item] values
//   [data-filter-group-button=X]  shows only the [data-filter-group=X] section ("" shows all)
//   [data-filter-empty]           shown when nothing matches
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-list-filter]").forEach((root) => {
    const input = root.querySelector("[data-filter-input]");
    const buttons = root.querySelectorAll("[data-filter-group-button]");
    const groups = root.querySelectorAll("[data-filter-group]");
    const empty = root.querySelector("[data-filter-empty]");
    let group = "";

    const apply = () => {
      const query = (input ? input.value : "").trim().toLowerCase();
      let anyVisible = false;
      groups.forEach((section) => {
        let visibleItems = 0;
        section.querySelectorAll("[data-filter-item]").forEach((item) => {
          const match = item.dataset.filterItem.includes(query);
          item.hidden = !match;
          if (match) visibleItems += 1;
        });
        const show = (!group || section.dataset.filterGroup === group) && visibleItems > 0;
        section.hidden = !show;
        anyVisible ||= show;
      });
      if (empty) empty.hidden = anyVisible;
    };

    input?.addEventListener("input", apply);
    buttons.forEach((button) =>
      button.addEventListener("click", () => {
        group = button.dataset.filterGroupButton;
        buttons.forEach((b) => b.setAttribute("aria-pressed", String(b === button)));
        apply();
      }),
    );
  });
});
