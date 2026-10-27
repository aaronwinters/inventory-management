# Polish Checklist

Run through this before Step 6.

## Spacing and layout
- [ ] All padding, margins, and gaps come from the `--space-*` scale
- [ ] Cards use one padding value (usually `--space-6`) across the app
- [ ] Grids of cards share one gap value (usually `--space-6`)
- [ ] Page header to first content block spacing is the same on every view
- [ ] Content area is fluid; no leftover max-width centering from the old layout unless intentional
- [ ] No horizontal page scroll at 390px; wide tables scroll inside their own container
- [ ] No orphaned or over-stretched last card in a row of KPI cards: size cards as fractions of the row per breakpoint (for 5 cards: `flex: 1 1 calc((100% - 4 * gap) / 5)`, then 3 per row so it wraps 3 + 2, then 1 per row on phones). A plain `flex: 1 1 <min>` leaves one card stretched across a whole row.
- [ ] Large KPI values (long currency totals) stay inside their card at every breakpoint (`overflow-wrap: anywhere`)
- [ ] The page title appears once (either the top bar or the page heading, not both)
- [ ] Sidebar brand and subtitle are fully readable (wrap, don't ellipsize)

## Surfaces
- [ ] Cards: surface background, 1px border, `--radius-lg`, `--shadow-xs` or none
- [ ] Hover lift only on clickable cards, not static ones
- [ ] Table headers: muted background, uppercase `--text-xs` labels, muted text
- [ ] Table rows: border-bottom dividers, hover background on clickable rows
- [ ] Badges: soft background + strong text from the same status family, `--radius-full`
- [ ] Modals: `--radius-lg`, `--shadow-lg`, backdrop, sit above sidebar and top bar

## Typography
- [ ] One heading scale: page title `--text-2xl`, card title `--text-lg`, labels `--text-sm`/`--text-xs`
- [ ] Numbers in KPI cards and tables use `font-variant-numeric: tabular-nums`
- [ ] Muted text only for secondary information, never for primary values

## Interaction
- [ ] Every interactive element has a visible `:focus-visible` state
- [ ] Transitions use `--transition`; nothing animates layout properties on hover
- [ ] Active nav item matches the current route, including nested routes
- [ ] Mobile drawer: opens, closes on backdrop click, Esc, and navigation

## States
- [ ] Loading and error states are styled consistently (centered, muted, inside a card)
- [ ] Empty tables and charts show a message rather than collapsing

## Consistency
- [ ] No new hardcoded hex values outside chart palettes and the token block
- [ ] Respects project rules from CLAUDE.md (for example, no emojis)
- [ ] Existing i18n keys, props, emits, and API calls unchanged
