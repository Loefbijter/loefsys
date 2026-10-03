// The activities calendar: FullCalendar driven by our own header controls.
// Colours come from the `.cat-<key>` classes the event filler returns, so the
// calendar follows the same category tokens as the rest of the site.
document.addEventListener("DOMContentLoaded", () => {
  const el = document.getElementById("calendar");
  if (!el || !window.FullCalendar) return;

  const title = document.getElementById("cal-title");
  const birthdays = document.getElementById("cal-birthdays-toggle");
  const viewButtons = document.querySelectorAll("[data-cal-view]");
  const phone = window.matchMedia("(max-width: 47.99rem)");

  const source = () => ({
    url: el.dataset.eventsUrl,
    method: "GET",
    extraParams: { show_birthdays: birthdays && birthdays.checked ? "1" : "0" },
  });

  const time = (date) =>
    date.toLocaleTimeString(el.dataset.locale, { hour: "2-digit", minute: "2-digit", hour12: false });

  // List rows reuse the markup of <c-event-row> so they look the same everywhere.
  const listRow = (arg) => {
    const ev = arg.event;
    const row = document.createElement("a");
    row.className = "row";
    if (ev.url) row.href = ev.url;

    const tile = document.createElement("div");
    tile.className = "datetile";
    tile.setAttribute("aria-hidden", "true");
    const month = document.createElement("small");
    month.textContent = ev.start.toLocaleDateString(el.dataset.locale, { month: "short" }).replace(".", "");
    const day = document.createElement("b");
    day.textContent = ev.start.getDate();
    tile.append(month, day);

    const body = document.createElement("div");
    body.className = "row-body";
    const name = document.createElement("div");
    name.className = "row-title";
    name.textContent = ev.title;
    const meta = document.createElement("div");
    meta.className = "row-meta";
    const addMeta = (icon, text) => {
      const span = document.createElement("span");
      const i = document.createElement("i");
      i.className = `bi bi-${icon}`;
      i.setAttribute("aria-hidden", "true");
      span.append(i, text);
      meta.append(span);
    };
    const date = (d) => d.toLocaleDateString(el.dataset.locale, { weekday: "short", day: "numeric", month: "short" });
    // FullCalendar's end is exclusive for all-day events, so step back a moment.
    const last = ev.end && new Date(ev.end.getTime() - (ev.allDay ? 1 : 0));
    if (last && last.toDateString() !== ev.start.toDateString()) {
      addMeta("clock", `${date(ev.start)} – ${date(last)}`);
    } else {
      addMeta("clock", ev.allDay ? el.dataset.allDay : `${time(ev.start)}${ev.end ? `–${time(ev.end)}` : ""}`);
    }
    if (ev.extendedProps.location) addMeta("geo-alt", ev.extendedProps.location);
    body.append(name, meta);

    const end = document.createElement("div");
    end.className = "row-end";
    if (ev.extendedProps.category) {
      const cat = document.createElement("span");
      cat.className = `cat ${ev.classNames.join(" ")}`;
      cat.textContent = ev.extendedProps.category;
      end.append(cat);
    }
    const chevron = document.createElement("i");
    chevron.className = "bi bi-chevron-right";
    chevron.setAttribute("aria-hidden", "true");
    end.append(chevron);

    row.append(tile, body, end);
    return { domNodes: [row] };
  };

  const calendar = new FullCalendar.Calendar(el, {
    initialView: phone.matches ? "listMonth" : "dayGridMonth",
    headerToolbar: false,
    height: "auto",
    locale: el.dataset.locale,
    firstDay: 1,
    allDayText: el.dataset.allDay,
    noEventsText: el.dataset.noEvents,
    dayMaxEventRows: 3,
    eventDisplay: "block",
    eventTimeFormat: { hour: "2-digit", minute: "2-digit", hour12: false },
    events: source(),
    datesSet: (info) => {
      if (title) title.textContent = info.view.title;
      viewButtons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.calView === info.view.type)));
    },
    eventContent: (arg) => (arg.view.type.startsWith("list") ? listRow(arg) : true),
    // The list shows each activity once, on its first day; the rows carry their own date.
    eventDidMount: (arg) => {
      if (arg.view.type.startsWith("list") && !arg.isStart) arg.el.style.display = "none";
    },
  });
  calendar.render();

  document.getElementById("cal-prev")?.addEventListener("click", () => calendar.prev());
  document.getElementById("cal-next")?.addEventListener("click", () => calendar.next());
  document.getElementById("cal-today")?.addEventListener("click", () => calendar.today());
  viewButtons.forEach((b) => b.addEventListener("click", () => calendar.changeView(b.dataset.calView)));
  birthdays?.addEventListener("change", () => {
    calendar.getEventSources().forEach((s) => s.remove());
    calendar.addEventSource(source());
  });
});
