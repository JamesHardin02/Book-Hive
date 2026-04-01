import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      meta: { requiresAuth: true },
      component: () => import('../views/DashboardView.vue'),
    },
    {
      path: '/search',
      name: 'search',
      meta: { requiresAuth: true },
      component: () => import('../views/SearchView.vue'),
    },
    {
      path: '/checkout',
      name: 'checkout',
      meta: { requiresAuth: true },
      component: () => import('../views/CheckoutPage.vue'),
    },
    {
      path: '/inventory',
      name: 'inventory',
      meta: { requiresAuth: true },
      component: () => import('../views/InventoryView.vue'),
    },
    {
      path: '/inventory/add',
      name: 'inventory-add',
      meta: { requiresAuth: true },
      component: () => import('../views/AddBookView.vue'),
    },
    {
      path: '/members',
      name: 'members',
      meta: { requiresAuth: true },
      component: () => import('../views/MembersView.vue'),
    },
    {
      path: '/returns',
      name: 'returns',
      meta: { requiresAuth: true },
      component: () => import('../views/ReturnsView.vue'),
    },
    {
      path: '/sales',
      name: 'sales',
      meta: { requiresAuth: true },
      component: () => import('../views/SalesView.vue'),
    },
    {
      path: '/exports',
      name: 'exports',
      meta: { requiresAuth: true },
      component: () => import('../views/ExportsView.vue'),
    },
    {
      path: '/apistatus',
      name: 'api status',
      component: () => import('../views/ApiStatusView.vue'),
    },
    {
      path: '/chart/:type',
      name: 'chart',
      component: () => import('../views/ChartView.vue'),
    },
    {
      path: '/logout',
      name: 'logout',
      meta: { requiresAuth: false },
      component: () => import('../views/LogoutView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.init()

  // If logged-in user hits login/register, bounce them to dashboard
  if ((to.path === '/' || to.path === '/register') && auth.isAuthenticated) {
    return { path: '/dashboard' }
  }

  if (to.meta.requiresAuth === true && !auth.isAuthenticated) {
    return { path: '/', query: { redirect: to.fullPath } }
  }

  return true
})

export default router
