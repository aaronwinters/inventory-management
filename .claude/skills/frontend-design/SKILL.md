---
name: frontend-design
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface with a left vertical sidebar navigation, design tokens, consistent spacing, and polished card layouts. Use when asked to redesign, modernize, restyle, or "make it look like a SaaS app", or to move a top nav bar into a sidebar, in a Vue 3 project.
---

# Frontend Design: Vue 3 SaaS Redesign

This skill turns an existing Vue 3 app into a polished SaaS interface: a vertical sidebar on the left, a slim top bar, token-driven styling, and consistent cards, tables, and spacing. It changes presentation only. Routes, data fetching, props, events, and i18n calls must behave exactly as before.

Follow the six steps in order. Do not skip the interview.

## Step 1: Discover

Build a picture of the app before touching anything:

1. **Project rules**: Read `CLAUDE.md` files (root and `client/` or `src/`). Obey them, including agent-delegation rules for `.vue` files, design-system constraints (for example "no emojis"), and port numbers.
2. **Root component**: Find `createApp(...)` (usually `src/main.js` or `main.ts`). The component passed in is the shell to restructure.
3. **Router**: List every route (`path`, component, any `meta.title`). These become sidebar items.
4. **Current nav**: Find the existing `router-link`s and how labels are produced (literal text or `t('...')` keys). Reuse the same label source.
5. **Global styles**: Find the unscoped `<style>` block or global CSS file, the font stack, and the dominant colors. Seed the tokens from these so the redesign feels related to the original.
6. **Layout dependencies**: Grep for `position: sticky`, `position: fixed`, `top:`, `z-index`, and `100vh`. Anything offset by the old header height must be updated in Step 4.
7. **Shared primitives**: Note global classes the views rely on (`.card`, `.stat-card`, `.page-header`, `.badge`, table styles, buttons, modals).

Summarize the findings in a few lines for the user before the interview.

## Step 2: Interview (required)

Use the **AskUserQuestion** tool once, with up to 4 questions. Put the recommended option first. Use `preview` with ASCII mockups for the visual choices.

| Question | Options |
|---|---|
| Sidebar theme | Light (white, subtle border) / Dark (slate-900) |
| Accent color | Keep existing / Blue / Indigo / Teal (see `references/design-tokens.md`) |
| Nav icons | Inline SVG (no dependency) / None |
| Sidebar behavior | Fixed width / Collapsible to an icon rail |

If the user picks "Other", adapt. Record the answers; they drive Steps 3 to 5.

## Step 3: Tokens first

Add CSS custom properties on `:root` in the global stylesheet, using `references/design-tokens.md`:

- Color: background, surface, surface-muted, border, text, text-muted, accent, accent-soft, status (success, warning, danger, info) with soft variants, and sidebar colors for the chosen theme.
- Spacing: a 4px scale (`--space-1` 4px through `--space-12` 48px).
- Radius, shadow, type scale, transition, and layout sizes (`--sidebar-width`, `--sidebar-width-collapsed`, `--topbar-height`).

Every later change must use these tokens rather than new hardcoded values.

## Step 4: Shell

Restructure the root component using `references/sidebar-shell.md`:

- Two-column CSS grid: `aside.sidebar` and a main column.
- Sidebar: brand at the top, nav links in the middle, optional footer slot. Active state comes from `router-link-active` / `router-link-exact-active`, not manual `$route` comparisons.
- Main column: a sticky top bar (height `--topbar-height`) holding page-level utilities (language, profile, global filters), then the routed content. Do not repeat the page title in the top bar if views already render their own page heading.
- Fix every sticky or fixed offset found in Step 1 to use the new tokens.
- Sidebar brand text wraps to two lines rather than truncating with an ellipsis.
- Three responsive modes (see `references/sidebar-shell.md`):
  - **>= 1280px**: full sidebar. If the user chose "Collapsible", a footer toggle collapses it to an icon rail and the choice persists in `localStorage` inside try/catch.
  - **768px to 1279px**: icons-only rail by default, with `title` tooltips. The footer toggle expands it as an overlay (no grid reflow, not persisted). Esc, backdrop click, and route change collapse it again.
  - **< 768px**: off-canvas drawer opened from a top bar button, with backdrop, `aria-expanded`, Esc to close, and auto-close on route change.
- Ensure modals sit above the sidebar and top bar (z-index scale in the tokens file).

## Step 5: Surfaces

1. Restyle global primitives with tokens: page header, stat/KPI cards, cards, card headers, tables, badges, buttons, inputs and selects, loading and error states.
2. Go view by view, largest first. In each scoped `<style>`, replace hardcoded colors, radii, shadows, and spacing with tokens. Align card padding, grid gaps, and section spacing to the scale.
3. Restyle modals: surface color, radius, shadow, header and footer spacing, backdrop.
4. Do not change template logic, script logic, props, emits, API calls, or i18n keys. Only add markup where the new layout needs it (wrappers, icon slots).
5. Add short comments for any non-obvious logic you introduce (drawer state, sticky offsets).

Run through `references/polish-checklist.md` before moving on.

## Step 6: Verify

1. `npm run build` (or the project's build script) succeeds.
2. With the dev server running, use browser automation (Playwright MCP if configured) to visit every route at 1440x900 and 390x844 and take screenshots.
3. Check the console for new errors or warnings.
4. Exercise one real interaction per view: a filter change still triggers the request, a modal opens above the shell, the nav highlights the current route, the mobile drawer opens and closes (including Esc).
5. Report what changed, what was verified, and anything that could not be verified.

## References

- `references/design-tokens.md`: Token values, accent presets, sidebar themes, z-index scale
- `references/sidebar-shell.md`: Reference shell component and responsive drawer
- `references/polish-checklist.md`: Final quality pass
