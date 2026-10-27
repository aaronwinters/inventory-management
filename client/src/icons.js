// Inline SVG nav icons (24x24 viewBox, stroke follows currentColor).
// Rendered via v-html; the strings are static constants, never user input.
const svg = (body) =>
  `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`

export const icons = {
  overview: svg('<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>'),
  inventory: svg('<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/>'),
  orders: svg('<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="M9 11h6M9 15h6"/>'),
  finance: svg('<path d="M3 7a2 2 0 012-2h13v4"/><path d="M3 7v11a2 2 0 002 2h14a1 1 0 001-1V9a1 1 0 00-1-1H5a2 2 0 01-2-1z"/><circle cx="16" cy="14" r="1"/>'),
  demand: svg('<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>'),
  reports: svg('<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'),
  collapse: svg('<path d="M11 17l-5-5 5-5M18 17l-5-5 5-5"/>'),
  expand: svg('<path d="M13 17l5-5-5-5M6 17l5-5-5-5"/>'),
  menu: svg('<path d="M4 6h16M4 12h16M4 18h16"/>')
}
