<template>
  <div
    class="app-shell"
    :class="{ 'is-collapsed': collapsed, 'is-drawer-open': drawerOpen, 'is-overlay-open': overlayOpen }"
  >
    <aside id="app-sidebar" class="sidebar" aria-label="Main navigation">
      <div class="sidebar-brand">
        <span class="brand-mark" aria-hidden="true">{{ brandInitial }}</span>
        <div class="brand-text">
          <span class="brand-name">{{ t('nav.companyName') }}</span>
          <span class="brand-subtitle">{{ t('nav.subtitle') }}</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :exact-active-class="item.exact ? 'is-active' : ''"
          :active-class="item.exact ? '' : 'is-active'"
          :title="showTooltips ? item.label : null"
        >
          <span class="nav-icon" aria-hidden="true" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button
          class="collapse-toggle"
          type="button"
          aria-controls="app-sidebar"
          :aria-expanded="sidebarExpanded ? 'true' : 'false'"
          :aria-label="sidebarExpanded ? 'Collapse sidebar' : 'Expand sidebar'"
          :title="sidebarExpanded ? 'Collapse sidebar' : 'Expand sidebar'"
          @click="onSidebarToggle"
        >
          <span class="nav-icon" aria-hidden="true" v-html="sidebarExpanded ? icons.collapse : icons.expand"></span>
        </button>
      </div>
    </aside>

    <div class="sidebar-backdrop" @click="closeTransient"></div>

    <div class="app-main">
      <header class="topbar">
        <button
          class="menu-toggle"
          type="button"
          aria-controls="app-sidebar"
          :aria-expanded="drawerOpen ? 'true' : 'false'"
          aria-label="Toggle navigation"
          @click="drawerOpen = !drawerOpen"
        >
          <span aria-hidden="true" v-html="icons.menu"></span>
        </button>
        <div class="topbar-actions">
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </div>
      </header>

      <FilterBar />

      <main class="content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import { icons } from './icons'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])
    const route = useRoute()

    // Breakpoint modes (CSS media queries drive the layout; these refs only drive
    // JS-side behavior such as tooltips, aria state and which toggle handler runs):
    //   >= 1280px     full sidebar, manual collapse (persisted)
    //   768 - 1279px  automatic icons-only rail, temporary overlay expansion
    //   < 768px       off-canvas drawer opened from the topbar menu button
    const RAIL_QUERY = '(min-width: 768px) and (max-width: 1279px)'
    const DRAWER_QUERY = '(max-width: 767px)'
    const supportsMatchMedia = typeof window !== 'undefined' && typeof window.matchMedia === 'function'
    // Read synchronously in setup so the first render already matches the viewport
    const isRail = ref(supportsMatchMedia && window.matchMedia(RAIL_QUERY).matches)
    const isDrawer = ref(supportsMatchMedia && window.matchMedia(DRAWER_QUERY).matches)

    // Mobile drawer open state (<768px only; CSS ignores it elsewhere)
    const drawerOpen = ref(false)
    // Temporary full-width overlay in rail mode (768-1279px only; CSS ignores it elsewhere)
    const overlayOpen = ref(false)
    const closeTransient = () => {
      drawerOpen.value = false
      overlayOpen.value = false
    }

    // Desktop icon-rail state, persisted across reloads
    const readCollapsed = () => {
      // localStorage can throw in private mode or when storage is blocked
      try {
        return localStorage.getItem('sidebar-collapsed') === '1'
      } catch {
        return false
      }
    }
    // Manual preference; only applied by CSS at >= 1280px
    const collapsed = ref(readCollapsed())
    const toggleCollapsed = () => {
      collapsed.value = !collapsed.value
      try {
        localStorage.setItem('sidebar-collapsed', collapsed.value ? '1' : '0')
      } catch {
        // Ignore: the preference just will not persist
      }
    }

    // Overlay expansion is deliberately NOT persisted: it is a temporary peek over the
    // content, so it must not overwrite the user's saved desktop preference.
    const toggleOverlay = () => {
      overlayOpen.value = !overlayOpen.value
    }
    const onSidebarToggle = () => (isRail.value ? toggleOverlay() : toggleCollapsed())

    // Whether the sidebar currently shows labels (drives aria-expanded and the icon)
    const sidebarExpanded = computed(() => (isRail.value ? overlayOpen.value : !collapsed.value))
    // Tooltips are needed whenever labels are hidden: the rail (even if the stored
    // preference is "expanded") or the manually collapsed desktop sidebar. The drawer
    // always shows labels.
    const showTooltips = computed(() => {
      if (isDrawer.value) return false
      return isRail.value ? !overlayOpen.value : collapsed.value
    })

    // Computed so labels follow the active locale
    const navItems = computed(() => [
      { to: '/', exact: true, label: t('nav.overview'), icon: icons.overview },
      { to: '/inventory', label: t('nav.inventory'), icon: icons.inventory },
      { to: '/orders', label: t('nav.orders'), icon: icons.orders },
      { to: '/spending', label: t('nav.finance'), icon: icons.finance },
      { to: '/demand', label: t('nav.demandForecast'), icon: icons.demand },
      { to: '/reports', label: t('nav.reports'), icon: icons.reports }
    ])

    const brandInitial = computed(() => (t('nav.companyName') || '').trim().charAt(0).toUpperCase())

    // Close the drawer/overlay after navigating so the new page is visible
    watch(() => route.fullPath, closeTransient)

    const onKeydown = (e) => {
      if (e.key === 'Escape') closeTransient()
    }

    // Keep the refs in sync with the viewport. Crossing a breakpoint also resets any
    // open drawer/overlay so stale state cannot reappear when resizing back.
    let railMql = null
    let drawerMql = null
    const onRailChange = (e) => { isRail.value = e.matches; closeTransient() }
    const onDrawerChange = (e) => { isDrawer.value = e.matches; closeTransient() }

    onMounted(() => {
      window.addEventListener('keydown', onKeydown)
      if (!supportsMatchMedia) return
      railMql = window.matchMedia(RAIL_QUERY)
      drawerMql = window.matchMedia(DRAWER_QUERY)
      railMql.addEventListener('change', onRailChange)
      drawerMql.addEventListener('change', onDrawerChange)
    })
    // Remove every listener so a remounted App (e.g. HMR) does not leak handlers
    onUnmounted(() => {
      window.removeEventListener('keydown', onKeydown)
      if (railMql) railMql.removeEventListener('change', onRailChange)
      if (drawerMql) drawerMql.removeEventListener('change', onDrawerChange)
    })

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      icons,
      drawerOpen,
      overlayOpen,
      collapsed,
      closeTransient,
      onSidebarToggle,
      sidebarExpanded,
      showTooltips,
      navItems,
      brandInitial,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
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

  /* Accent: Blue (kept from the original design) */
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

  /* Dark sidebar theme */
  --sidebar-bg: #0f172a;
  --sidebar-border: #1e293b;
  --sidebar-text: #94a3b8;
  --sidebar-text-hover: #f1f5f9;
  --sidebar-item-hover: #1e293b;
  --sidebar-item-active-bg: rgba(255, 255, 255, 0.08);
  --sidebar-item-active-text: #ffffff;
  --sidebar-brand: #ffffff;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background: var(--color-bg);
  color: var(--color-text-secondary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ---------- Shell ---------- */
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100vh;
  transition: grid-template-columns 200ms ease;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  padding: var(--space-4) var(--space-3);
  z-index: var(--z-sidebar);
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-brand {
  display: flex;
  align-items: flex-start; /* mark stays aligned to the first line when text wraps */
  gap: var(--space-3);
  padding: var(--space-2) var(--space-2) var(--space-6);
  color: var(--sidebar-brand);
  min-height: 56px;
}

.brand-mark {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  background: var(--color-accent);
  color: #ffffff;
  display: grid;
  place-items: center;
  font-size: var(--text-sm);
  font-weight: 700;
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  font-size: var(--text-base);
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.2;
  white-space: normal;
}

.brand-subtitle {
  font-size: var(--text-xs);
  line-height: 1.25;
  color: var(--sidebar-text);
  white-space: normal;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  min-height: 40px;
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  text-decoration: none;
  font-weight: 500;
  font-size: var(--text-sm);
  white-space: nowrap;
  transition: background var(--transition), color var(--transition);
}

.nav-item:hover {
  background: var(--sidebar-item-hover);
  color: var(--sidebar-text-hover);
}

.nav-item.is-active {
  background: var(--sidebar-item-active-bg);
  color: var(--sidebar-item-active-text);
}

.nav-item:focus-visible,
.collapse-toggle:focus-visible,
.menu-toggle:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
}

.sidebar-footer {
  padding-top: var(--space-3);
  border-top: 1px solid var(--sidebar-border);
  display: flex;
  justify-content: flex-end;
}

.collapse-toggle {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--sidebar-text);
  cursor: pointer;
  transition: background var(--transition), color var(--transition);
}

.collapse-toggle:hover {
  background: var(--sidebar-item-hover);
  color: var(--sidebar-text-hover);
}

/* Icons-only rail styling, shared by the manual collapse (>= 1280px) and the
   automatic rail (768-1279px). Labels stay reachable via title tooltips. */
@media (min-width: 1280px) {
  .app-shell.is-collapsed {
    grid-template-columns: var(--sidebar-width-collapsed) minmax(0, 1fr);
  }

  .is-collapsed .nav-label,
  .is-collapsed .brand-text {
    display: none;
  }

  .is-collapsed .sidebar-brand,
  .is-collapsed .nav-item {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }

  .is-collapsed .sidebar-footer {
    justify-content: center;
  }
}

.app-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* Topbar sticks at 0; FilterBar sticks directly below at var(--topbar-height) */
.topbar {
  position: sticky;
  top: 0;
  z-index: var(--z-topbar);
  height: var(--topbar-height);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: 0 var(--space-8);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.topbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* Only shown below 768px */
.menu-toggle {
  display: none;
}

.content {
  flex: 1;
  min-width: 0;
  padding: var(--space-8);
}

.sidebar-backdrop {
  display: none;
}

/* Rail (768-1279px): the grid column is always the rail width, regardless of the
   stored preference. Expanding overlays the content and never reflows the grid. */
@media (min-width: 768px) and (max-width: 1279px) {
  .app-shell,
  .app-shell.is-collapsed {
    grid-template-columns: var(--sidebar-width-collapsed) minmax(0, 1fr);
  }

  .app-shell:not(.is-overlay-open) .nav-label,
  .app-shell:not(.is-overlay-open) .brand-text {
    display: none;
  }

  .app-shell:not(.is-overlay-open) .sidebar-brand,
  .app-shell:not(.is-overlay-open) .nav-item {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }

  .app-shell:not(.is-overlay-open) .sidebar-footer {
    justify-content: center;
  }

  /* Overlay: the sidebar leaves the grid flow, so pin .app-main to column 2 or it
     would slide into the (now empty) first column. */
  .app-main {
    grid-column: 2;
  }

  .is-overlay-open .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    width: var(--sidebar-width);
    box-shadow: var(--shadow-lg);
    z-index: calc(var(--z-backdrop) + 1);
  }

  .is-overlay-open .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.4);
    z-index: var(--z-backdrop);
  }
}

/* Drawer (< 768px) */
@media (max-width: 767px) {
  .app-shell,
  .app-shell.is-collapsed {
    grid-template-columns: minmax(0, 1fr);
  }

  /* Off-canvas drawer; hidden state is a transform so it stays focus-order sane via backdrop/Esc */
  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    width: var(--sidebar-width);
    transform: translateX(-100%);
    transition: transform 200ms ease;
  }

  .is-drawer-open .sidebar {
    transform: translateX(0);
    box-shadow: var(--shadow-lg);
    z-index: calc(var(--z-backdrop) + 1);
  }

  .is-drawer-open .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.4);
    z-index: var(--z-backdrop);
  }

  /* The drawer always shows labels, so the rail toggle is hidden */
  .sidebar-footer {
    display: none;
  }

  .menu-toggle {
    display: inline-grid;
    place-items: center;
    width: 36px;
    height: 36px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
    color: var(--color-text);
    cursor: pointer;
  }

  .topbar,
  .content {
    padding-left: var(--space-4);
    padding-right: var(--space-4);
  }
}

/* ---------- Shared primitives ---------- */
.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-1);
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-surface);
  padding: var(--space-6);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-xs);
}

.stat-label {
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
  font-variant-numeric: tabular-nums;
}

.stat-card.warning .stat-value {
  color: var(--color-warning);
}

.stat-card.success .stat-value {
  color: var(--color-success);
}

.stat-card.danger .stat-value {
  color: var(--color-danger);
}

.stat-card.info .stat-value {
  color: var(--color-accent);
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-xs);
  margin-bottom: var(--space-6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

thead {
  background: var(--color-surface-muted);
}

th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  font-weight: 600;
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

tbody tr:last-child td {
  border-bottom: none;
}

tbody tr {
  transition: background-color var(--transition);
}

tbody tr:hover {
  background: var(--color-surface-muted);
}

.badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  background: var(--color-surface-muted);
  color: var(--color-text-secondary);
}

.badge.success,
.badge.increasing {
  background: var(--color-success-soft);
  color: var(--color-success);
}

.badge.warning,
.badge.medium {
  background: var(--color-warning-soft);
  color: var(--color-warning);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}

.badge.info,
.badge.low {
  background: var(--color-info-soft);
  color: var(--color-info);
}

.badge.stable {
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.loading {
  text-align: center;
  padding: var(--space-12);
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

.error {
  background: var(--color-danger-soft);
  border: 1px solid var(--color-danger-soft);
  color: var(--color-danger);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: var(--text-base);
}
</style>
