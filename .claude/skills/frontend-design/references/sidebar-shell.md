# Sidebar Shell Reference

A reference root layout. Adapt names, label source (`t('...')` or literal), and the utilities in the top bar to the app. Match the project's component style (Options API `setup()` or `<script setup>`).

## Template

```vue
<template>
  <div class="app-shell" :class="{ 'is-collapsed': collapsed, 'is-drawer-open': drawerOpen, 'is-rail-expanded': railExpanded }">
    <aside id="app-sidebar" class="sidebar" :aria-label="'Main navigation'">
      <div class="sidebar-brand">
        <span class="brand-mark" aria-hidden="true">IM</span>
        <span class="brand-text">App Name</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :title="showTooltips ? item.label : null"
          :exact-active-class="item.exact ? 'is-active' : ''"
          :active-class="item.exact ? '' : 'is-active'"
        >
          <span class="nav-icon" aria-hidden="true" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button v-if="collapsible" class="collapse-toggle" @click="onSidebarToggle">
          {{ isRailMode ? (railExpanded ? 'Collapse' : 'Expand') : (collapsed ? 'Expand' : 'Collapse') }}
        </button>
      </div>
    </aside>

    <div class="sidebar-backdrop" @click="closeOverlays"></div>

    <div class="app-main">
      <header class="topbar">
        <button
          class="menu-toggle"
          aria-controls="app-sidebar"
          :aria-expanded="drawerOpen ? 'true' : 'false'"
          aria-label="Open navigation"
          @click="drawerOpen = !drawerOpen"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
        <!-- No page title here: views render their own page heading -->
        <div class="topbar-actions"><!-- language, profile, etc. --></div>
      </header>

      <!-- Optional global toolbar (filters) goes here, sticky below the top bar -->

      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>
```

Use the `exact` flag on the root route (`/`) so it is not active on every page.

## Responsive modes

| Width | Mode | Toggle |
|---|---|---|
| >= 1280px | Full sidebar (or user-collapsed rail) | Footer toggle; choice persisted |
| 768px to 1279px | Icons-only rail, `title` tooltips | Footer toggle expands as an overlay; not persisted |
| < 768px | Off-canvas drawer | Top bar menu button |

Drive the layout with CSS media queries so there is no flash on load. Use `matchMedia` only for the state the script needs (which toggle behavior applies, tooltips).

## Script essentials

```js
const drawerOpen = ref(false)
const railExpanded = ref(false)
const collapsed = ref(readCollapsed())

// Mid-size screens always start as an icon rail regardless of the saved preference
const railQuery = window.matchMedia('(min-width: 768px) and (max-width: 1279px)')
const isRailMode = ref(railQuery.matches)
const onRailChange = (e) => { isRailMode.value = e.matches; railExpanded.value = false }
onMounted(() => railQuery.addEventListener('change', onRailChange))
onUnmounted(() => railQuery.removeEventListener('change', onRailChange))

// Labels are hidden whenever the rail shows, so links need tooltips
const showTooltips = computed(() => (isRailMode.value && !railExpanded.value) || (!isRailMode.value && collapsed.value))

function onSidebarToggle() {
  // Overlay expansion on mid-size screens is temporary and must not overwrite the desktop preference
  if (isRailMode.value) { railExpanded.value = !railExpanded.value; return }
  toggleCollapsed()
}
function closeOverlays() { drawerOpen.value = false; railExpanded.value = false }

function readCollapsed() {
  // localStorage can throw in private mode or when storage is blocked
  try { return localStorage.getItem('sidebar-collapsed') === '1' } catch { return false }
}
function toggleCollapsed() {
  collapsed.value = !collapsed.value
  try { localStorage.setItem('sidebar-collapsed', collapsed.value ? '1' : '0') } catch {}
}

// Close the mobile drawer or rail overlay after navigating so the new page is visible
watch(() => route.fullPath, closeOverlays)

const onKeydown = (e) => { if (e.key === 'Escape') closeOverlays() }
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
```

## Styles

```css
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100vh;
}
.app-shell.is-collapsed { grid-template-columns: var(--sidebar-width-collapsed) minmax(0, 1fr); }

.sidebar {
  position: sticky; top: 0; height: 100vh;
  display: flex; flex-direction: column;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  padding: var(--space-4) var(--space-3);
  z-index: var(--z-sidebar);
  overflow-y: auto;
}
.sidebar-brand { display: flex; align-items: flex-start; gap: var(--space-3); padding: var(--space-2) var(--space-3) var(--space-6); color: var(--sidebar-brand); font-weight: 700; }
/* Wrap long product names instead of truncating them */
.brand-text { white-space: normal; line-height: 1.25; min-width: 0; }
.brand-mark { width: 32px; height: 32px; flex-shrink: 0; border-radius: var(--radius-md); background: var(--color-accent); color: #fff; display: grid; place-items: center; font-size: var(--text-sm); }
.sidebar-nav { display: flex; flex-direction: column; gap: var(--space-1); flex: 1; }
.nav-item {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-2) var(--space-3); border-radius: var(--radius-md);
  color: var(--sidebar-text); text-decoration: none; font-weight: 500; font-size: var(--text-sm);
  transition: background var(--transition), color var(--transition);
}
.nav-item:hover { background: var(--sidebar-item-hover); color: var(--sidebar-text-hover); }
.nav-item.is-active { background: var(--sidebar-item-active-bg); color: var(--sidebar-item-active-text); }
.nav-item:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
.nav-icon { width: 20px; height: 20px; flex-shrink: 0; display: grid; place-items: center; }
.is-collapsed .nav-label, .is-collapsed .brand-text { display: none; }

.app-main { min-width: 0; display: flex; flex-direction: column; }
.topbar {
  position: sticky; top: 0; z-index: var(--z-topbar);
  height: var(--topbar-height);
  display: flex; align-items: center; gap: var(--space-4);
  padding: 0 var(--space-8);
  background: var(--color-surface); border-bottom: 1px solid var(--color-border);
}
.topbar-actions { margin-left: auto; display: flex; align-items: center; gap: var(--space-3); }
.menu-toggle { display: none; }
.content { padding: var(--space-8); }
.sidebar-backdrop { display: none; }

/* Mid-size: icons-only rail by default; expanding overlays content instead of reflowing the grid */
@media (min-width: 768px) and (max-width: 1279px) {
  .app-shell, .app-shell.is-collapsed { grid-template-columns: var(--sidebar-width-collapsed) minmax(0, 1fr); }
  .sidebar { width: var(--sidebar-width-collapsed); }
  .app-shell:not(.is-rail-expanded) .nav-label,
  .app-shell:not(.is-rail-expanded) .brand-text { display: none; }
  .is-rail-expanded .sidebar {
    position: fixed; inset: 0 auto 0 0; width: var(--sidebar-width);
    z-index: calc(var(--z-backdrop) + 1); box-shadow: var(--shadow-lg);
  }
  .is-rail-expanded .nav-label, .is-rail-expanded .brand-text { display: inline; }
  .is-rail-expanded .sidebar-backdrop { display: block; position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); z-index: var(--z-backdrop); }
}

@media (max-width: 767px) {
  .app-shell, .app-shell.is-collapsed { grid-template-columns: minmax(0, 1fr); }
  .sidebar {
    position: fixed; inset: 0 auto 0 0; width: var(--sidebar-width);
    transform: translateX(-100%); transition: transform 200ms ease;
  }
  .is-drawer-open .sidebar { transform: translateX(0); box-shadow: var(--shadow-lg); }
  .is-drawer-open .sidebar-backdrop { display: block; position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); z-index: var(--z-backdrop); }
  .is-drawer-open .sidebar { z-index: calc(var(--z-backdrop) + 1); }
  /* Collapsed rail makes no sense in a drawer: always show labels */
  .is-collapsed .nav-label, .is-collapsed .brand-text { display: inline; }
  .menu-toggle { display: inline-grid; place-items: center; width: 36px; height: 36px; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); color: var(--color-text); cursor: pointer; }
  .topbar, .content { padding-left: var(--space-4); padding-right: var(--space-4); }
}
```

## Inline SVG icons

Use 24x24 viewBox, `stroke="currentColor"`, `stroke-width="1.75"`, `fill="none"`, rendered at 20px. Keep them in a small `icons.js` map or inline in the nav items array. Typical mapping:

- Overview/Dashboard: grid of four squares
- Inventory: box/package
- Orders: clipboard or receipt
- Finance/Spending: wallet or currency
- Forecast/Demand: trending-up line
- Reports: bar chart / document
- Settings: gear
