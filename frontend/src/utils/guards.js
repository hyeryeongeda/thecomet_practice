import { useAuthStore } from '@/stores/auth'

export function requiresAuthGuard(to) {
  const auth = useAuthStore()

  if (to.meta?.requiresAuth && !auth.isAuthenticated) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }

  return true
}
