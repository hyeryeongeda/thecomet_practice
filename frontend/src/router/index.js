// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes.js'
import { requiresAuthGuard } from '@/utils/guards'

const router = createRouter({
  history: createWebHistory(),
  routes, 
})

router.beforeEach(requiresAuthGuard)

export default router
