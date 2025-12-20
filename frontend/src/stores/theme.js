import { defineStore } from 'pinia'
import api from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: localStorage.getItem('theme') || 'netflix', // 'netflix' | 'wavve'
  }),

  actions: {
    applyTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme)
    },

    async setTheme(theme, { syncServer = true } = {}) {
      this.theme = theme
      localStorage.setItem('theme', theme)
      this.applyTheme(theme)

      // ✅ 로그인 상태면 서버에도 저장(마이페이지/설정 연동)
      if (syncServer) {
        const auth = useAuthStore()
        if (auth.isAuthenticated) {
          try {
            await api.patch('/auth/me/theme/', { theme })
          } catch (e) {
            // 서버 저장 실패해도 로컬 UI는 유지
          }
        }
      }
    },

    async toggleTheme() {
      const next = this.theme === 'netflix' ? 'wavve' : 'netflix'
      await this.setTheme(next)
    },

    // 앱 시작 시 1번 호출 (로컬스토리지 값 적용)
    initTheme() {
      this.applyTheme(this.theme)
    },
  },
})
