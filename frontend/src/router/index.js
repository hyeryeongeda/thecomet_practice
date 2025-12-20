import { createRouter, createWebHistory } from 'vue-router'
import { requiresAuthGuard } from '@/utils/guards'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/movies', name: 'movies', component: () => import('@/views/MoviesView.vue') },
    { path: '/movies/:tmdbId', name: 'movie-detail', component: () => import('@/views/MovieDetailView.vue') },


    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
    { path: '/signup', name: 'signup', component: () => import('@/views/SignupView.vue') },

    { path: '/taste', name: 'taste', component: () => import('@/views/TasteView.vue'), meta: { requiresAuth: true } },
    { path: '/recommend', name: 'recommend', component: () => import('@/views/RecommendView.vue'), meta: { requiresAuth: true } },
    { path: '/search', name: 'search', component: () => import('@/views/SearchView.vue') },

    { path: '/me', name: 'mypage', component: () => import('@/views/MyPageView.vue'), meta: { requiresAuth: true } },

    {
  path: '/users/:username',
  name: 'user-profile',
  component: () => import('@/views/UserProfileView.vue'),
  props: true,
},

    { path: '/:pathMatch(.*)*', name: 'notfound', component: () => import('@/views/NotFoundView.vue') },
  ],
})

router.beforeEach(requiresAuthGuard)
export default router
