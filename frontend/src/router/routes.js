// frontend/src/router/routes.js

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/movies', name: 'movies', component: () => import('@/views/MoviesView.vue') },
  {
    path: '/movies/:tmdbId',
    name: 'movie-detail',
    component: () => import('@/views/MovieDetailView.vue'),
    props: true,
  },

  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  { path: '/signup', name: 'signup', component: () => import('@/views/SignupView.vue') },

  {
    path: '/taste',
    name: 'taste',
    component: () => import('@/views/TasteView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/recommend',
    name: 'recommend',
    component: () => import('@/views/RecommendView.vue'),
    meta: { requiresAuth: true },
  },
  { path: '/search', name: 'search', component: () => import('@/views/SearchView.vue') },

  // ✅ 마이페이지는 /mypage로 통일
  {
    path: '/mypage',
    name: 'mypage',
    component: () => import('@/views/MyPageView.vue'),
    meta: { requiresAuth: true },
  },

  // ✅ 기존 /me 호환
  { path: '/me', redirect: { name: 'mypage' } },

  {
    path: '/users/:username',
    name: 'user-profile',
    component: () => import('@/views/UserProfileView.vue'),
    props: true,
  },

  { path: '/:pathMatch(.*)*', name: 'notfound', component: () => import('@/views/NotFoundView.vue') },
  { path: '/people/:tmdbId', name: 'person-detail', component: () => import('@/views/PersonDetailView.vue'), props: true },
// src/router/index.js (또는 routes.js) 파일 내 해당 부분 찾기

{
  path: '/mypage/grid/:type',
  name: 'mypage-grid',
  /**
   * [수정 핵심] import 경로를 새 폴더 위치로 변경합니다.
   * @는 보통 src 폴더를 가리킵니다.
   */
  component: () => import('@/components/mypage/MyPageGridView.vue'),
  
  // 만약 @를 사용하지 않는 환경이라면 상대 경로로 작성하세요:
  // component: () => import('../components/mypage/MyPageGridView.vue'),
  
  props: true // URL 파라미터를 props로 전달하고 싶을 때 사용
}






]

export default routes
