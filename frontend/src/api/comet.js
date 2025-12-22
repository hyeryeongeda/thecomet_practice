import api from './axios'

/** * [공통] 토큰 포함 헤더 생성 함수 
 * interceptor를 사용 중이더라도, 명시적으로 headers를 보낼 때 유용합니다.
 */
function authConfig(extra = {}) {
  const token = localStorage.getItem('access')
  const config = { ...extra }
  if (token) {
    config.headers = {
      ...(config.headers || {}),
      Authorization: `Bearer ${token}`,
    }
  }
  return config
}

// =========================
// 1. Movies (영화)
// =========================
export const fetchHomeSections = (page = 1) => api.get('/movies/home/', { params: { page } }).then(res => res.data)
export const fetchMovies = (params = {}) => api.get('/movies/list/', { params }).then(res => res.data)
export const fetchGenres = () => api.get('/movies/genres/').then(res => res.data)
export const fetchMovieDetail = (tmdbId) => api.get(`/movies/${tmdbId}/`).then(res => res.data)
export const fetchPersonDetail = (tmdbId) => api.get(`/movies/people/${tmdbId}/`).then(res => res.data)
export const searchComet = (params) => api.get('/movies/search/', { params }).then(res => res.data)

// =========================
// 2. Reviews (리뷰)
// =========================
export const fetchRecentReviews = (limit = 12) => api.get('/reviews/recent/', { params: { limit } }).then(res => res.data)
export const fetchMovieReviews = (tmdbId) => api.get(`/reviews/movie/${tmdbId}/`).then(res => res.data)
export const createMovieReview = (tmdbId, payload) => api.post(`/reviews/movie/${tmdbId}/create/`, payload).then(res => res.data)
export const updateReview = (reviewId, payload) => api.put(`/reviews/${reviewId}/`, payload).then(res => res.data)
export const deleteReview = (reviewId) => api.delete(`/reviews/${reviewId}/`).then(res => res.data)
export const toggleReviewLike = (reviewId) => api.post(`/reviews/${reviewId}/like/`).then(res => res.data)

// ✅ [중요] 마이페이지 - 내 활동 목록
export const fetchMyActivity = (params = {}) => api.get('/reviews/my/', authConfig({ params })).then(res => res.data)

// =========================
// 3. Accounts (인증/프로필)
// =========================
export const signup = (payload) => api.post('/auth/signup/', payload).then(res => res.data)
export const login = (payload) => api.post('/auth/login/', payload).then(res => res.data)
export const fetchMe = () => api.get('/auth/me/', authConfig()).then(res => res.data)

/** * ✅ [수정 핵심] 프로필 수정 404 해결 
 * 백엔드 urls.py 설정에 따라 '/auth/profile/' 또는 '/accounts/profile/'로 맞춰야 합니다.
 * 이전 로그에서 /api/accounts/profile/이 404였다면, /api/auth/profile/일 확률이 높습니다.
 */
export async function updateMyProfile(formData) {
  // formData 전송 시에는 axios가 자동으로 multipart/form-data를 설정합니다.
  const res = await api.patch('/auth/profile/', formData, authConfig()) 
  return res.data
}

export const updateMyTheme = (theme) => api.patch('/auth/me/theme/', { theme }, authConfig()).then(res => res.data)
export const fetchUserProfile = (username) => api.get(`/auth/users/${encodeURIComponent(username)}/`).then(res => res.data)
export const toggleFollow = (username) => api.post(`/auth/users/${encodeURIComponent(username)}/follow/`, {}, authConfig()).then(res => res.data)

// =========================
// 4. Recommends (추천/분석)
// =========================
export const postTasteChat = (payload) => api.post('/recommends/ai/', payload, authConfig()).then(res => res.data)
export const fetchGenreRecommends = (params = {}) => api.get('/recommends/genres/', authConfig({ params })).then(res => res.data)
export const fetchPersonRecommends = (params = {}) => api.get('/recommends/people/', authConfig({ params })).then(res => res.data)
export const fetchUserRecommends = (params = {}) => api.get('/recommends/users/', authConfig({ params })).then(res => res.data)
export const fetchTasteDNA = () => api.get('/recommends/taste/', authConfig()).then(res => res.data)

// ✅ 좋아요한 인물/장르 가져오기
export const fetchMyLikes = (type) => api.get('/movies/likes/', authConfig({ params: { type } })).then(res => res.data)