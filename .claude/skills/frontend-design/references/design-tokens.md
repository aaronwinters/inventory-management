# Design Tokens

Paste into the global stylesheet's `:root`, then swap in the chosen accent preset and sidebar theme. Seed neutrals from the app's existing palette when it is already a slate/gray family.

## Base set

```css
:root {
  /* Neutrals */
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-surface-muted: #f1f5f9;
  --color-border: #e2e8f0;
  --color-border-strong: #cbd5e1;
  --color-text: #0f172a;
  --color-text-secondary: #334155;
  --color-text-muted: #64748b;

  /* Accent (replace with a preset below) */
  --color-accent: #2563eb;
  --color-accent-hover: #1d4ed8;
  --color-accent-soft: #eff6ff;

  /* Status */
  --color-success: #15803d;
  --color-success-soft: #dcfce7;
  --color-warning: #b45309;
  --color-warning-soft: #fef3c7;
  --color-danger: #b91c1c;
  --color-danger-soft: #fee2e2;
  --color-info: #0369a1;
  --color-info-soft: #e0f2fe;

  /* Spacing: 4px scale */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 999px;

  /* Shadow */
  --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 16px 40px rgba(15, 23, 42, 0.16);

  /* Type */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 0.9375rem;
  --text-lg: 1.125rem;
  --text-xl: 1.375rem;
  --text-2xl: 1.75rem;

  /* Motion */
  --transition: 150ms ease;

  /* Layout */
  --sidebar-width: 248px;
  --sidebar-width-collapsed: 72px;
  --topbar-height: 64px;

  /* Z-index scale */
  --z-sticky: 20;
  --z-topbar: 30;
  --z-sidebar: 40;
  --z-backdrop: 50;
  --z-modal: 1000;
}
```

## Accent presets

| Preset | accent | accent-hover | accent-soft |
|---|---|---|---|
| Blue | `#2563eb` | `#1d4ed8` | `#eff6ff` |
| Indigo | `#4f46e5` | `#4338ca` | `#eef2ff` |
| Teal | `#0d9488` | `#0f766e` | `#f0fdfa` |
| Keep existing | the app's current primary | darken about 10% | lighten to about 95% |

## Sidebar themes

**Light**
```css
--sidebar-bg: var(--color-surface);
--sidebar-border: var(--color-border);
--sidebar-text: var(--color-text-muted);
--sidebar-text-hover: var(--color-text);
--sidebar-item-hover: var(--color-surface-muted);
--sidebar-item-active-bg: var(--color-accent-soft);
--sidebar-item-active-text: var(--color-accent);
--sidebar-brand: var(--color-text);
```

**Dark**
```css
--sidebar-bg: #0f172a;
--sidebar-border: #1e293b;
--sidebar-text: #94a3b8;
--sidebar-text-hover: #f1f5f9;
--sidebar-item-hover: #1e293b;
--sidebar-item-active-bg: rgba(255, 255, 255, 0.08);
--sidebar-item-active-text: #ffffff;
--sidebar-brand: #ffffff;
```

## Mapping old values

When tokenizing a scoped style block, map by role, not by exact hex:

- Page background grays → `--color-bg`
- White panels → `--color-surface`
- Light gray fills, table headers, hover rows → `--color-surface-muted`
- 1px dividers → `--color-border`
- Headings and body text → `--color-text` / `--color-text-secondary`
- Labels, captions, placeholder-ish text → `--color-text-muted`
- Brand blue → `--color-accent`
- Greens/ambers/reds/blues used for status → matching status token

Chart series colors can stay hardcoded if they form a deliberate palette; only align them if they clash with the accent.
