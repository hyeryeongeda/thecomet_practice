// frontend/src/api/comet.js
import api from './axios'

// =========================
// 공통: Authorization 헤더 (인터셉터로 이미 붙이면 이거 없어도 됨)
// =========================
function authConfig(extra = {}) {
  const token = localStorage.getItem('access')
  if (!token) return extra
  return {
    ...extra,
    headers: {
      ...(extra.headers || {}),
      Authorization: `Bearer ${token}`,
    },
  }
}

// =========================
// movies
// =========================
export async function fetchHomeSections(page = 1) {
  const res = await api.get('/movies/home/', { params: { page } })
  return res.data
}

export async function fetchMovies(params = {}) {
  // ✅ 백엔드가 /movies/list/
  const res = await api.get('/movies/list/', { params })
  return res.data
}

export async function fetchGenres() {
  const res = await api.get('/movies/genres/')
  return res.data
}

export async function fetchMovieDetail(tmdbId) {
  const res = await api.get(`/movies/${tmdbId}/`)
  return res.data
}

export async function searchMulti(q, page = 1) {
  const res = await api.get('/movies/search/', { params: { q, page } })
  return res.data
}

export async function fetchPersonDetail(tmdbId) {
  const res = await api.get(`/movies/people/${tmdbId}/`)
  return res.data
}

// =========================
// reviews
// =========================
export async function fetchRecentReviews(limit = 12) {
  const res = await api.get('/reviews/recent/', { params: { limit } })
  return res.data
}

export async function fetchMovieReviews(tmdbId) {
  const res = await api.get(`/reviews/movie/${tmdbId}/`)
  return res.data
}

export async function createMovieReview(tmdbId, payload) {
  const res = await api.post(`/reviews/movie/${tmdbId}/create/`, payload)
  return res.data
}

export async function updateReview(reviewId, payload) {
  const res = await api.put(`/reviews/${reviewId}/`, payload)
  return res.data
}

export async function deleteReview(reviewId) {
  const res = await api.delete(`/reviews/${reviewId}/`)
  return res.data
}

export async function toggleReviewLike(reviewId) {
  const res = await api.post(`/reviews/${reviewId}/like/`)
  return res.data
}

// =========================
// accounts
// =========================
export async function signup(payload) {
  const res = await api.post('/auth/signup/', payload)
  return res.data
}

export async function login(payload) {
  const res = await api.post('/auth/login/', payload)
  return res.data
}

export async function fetchMe() {
  const res = await api.get('/auth/me/')
  return res.data
}

// export async function updateMyProfile(payload) {
//   const res = await api.patch('/auth/me/profile/', payload)
//   return res.data
// }

export async function updateMyTheme(theme) {
  const res = await api.patch('/auth/me/theme/', { theme })
  return res.data
}

export async function fetchUserProfile(username) {
  const res = await api.get(`/auth/users/${encodeURIComponent(username)}/`)
  return res.data
}

export async function toggleFollow(username) {
  const res = await api.post(`/auth/users/${encodeURIComponent(username)}/follow/`)
  return res.data
}

// =========================
// recommends (취향분석/추천)
// =========================

// 1) AI 챗봇(취향분석/맞춤추천 공용)
export async function postTasteChat(payload) {
  const { data } = await api.post('/recommends/ai/', payload, {
    headers: authHeaders(),
  })
  return data
}


// 2) 장르 추천
// GET /recommends/genres/
export async function fetchGenreRecommends(params = {}) {
  const res = await api.get('/recommends/genres/', authConfig({ params }))
  return res.data
}

// 3) 인물 추천
// GET /recommends/people/
export async function fetchPersonRecommends(params = {}) {
  const res = await api.get('/recommends/people/', authConfig({ params }))
  return res.data
}

// 4) 유저 추천
// GET /recommends/users/
export async function fetchUserRecommends(params = {}) {
  const res = await api.get('/recommends/users/', authConfig({ params }))
  return res.data
}


function authHeaders() {
  const token = localStorage.getItem('access')
  return token ? { Authorization: `Bearer ${token}` } : {}
}


// 검색

export const searchComet = (params) => {
  return api.get('/movies/search/', { params })
    .then(res => res.data)
}

// =========================
// (taste page)
// =========================
export async function fetchTasteDNA() {
  const { data } = await api.get('/recommends/taste/')
  return data
}








// =========================
// 마이페이지
// =========================
export async function fetchMyActivity(params = {}) {
  const res = await api.get('/reviews/my/', authConfig({ params }))
  return res.data
}

// [추가] 좋아요한 인물/장르 가져오기
export async function fetchMyLikes(type) {
  const res = await api.get('/movies/likes/', authConfig({ params: { type } }))
  return res.data
}


// export async function updateMyProfile(payload) {
//   const res = await api.patch('/auth/me/profile/', payload)
//   return res.data
// } 이거 수정 할게요 
export async function updateMyProfile(formData) {
  // 파일 전송을 위해 Content-Type 헤더를 multipart/form-data로 설정하는 것은
  // axios가 FormData를 감지하면 자동으로 처리하므로 별도 설정 불필요할 수 있으나,
  // 안전하게 authConfig 내부 동작 확인 필요. 보통은 그냥 보내면 됨.
  const res = await api.patch('/accounts/profile/', formData, authConfig()) 
  return res.data
}






// 영화 디테일 페이지 
// [추가] 비슷한 영화 가져오기
export async function fetchSimilarMovies(tmdbId) {
  // 백엔드 URL이 /movies/{id}/similar/ 라고 가정
  // 만약 백엔드에 이 기능이 없다면, 우선은 fetchMovies()로 대체해서 목록만 채워드릴게요.
  try {
    const res = await api.get(`/movies/${tmdbId}/similar/`)
    return res.data
  } catch (e) {
    console.warn("비슷한 영화 API가 없어서 추천 API로 대체합니다.")
    return [] // 혹은 fetchMovies({ page: 1 }) 호출
  }
}