//frontend/src/api/comet.js

import api from './axios'

// =========================
// movies
// =========================
export async function fetchHomeSections(page = 1) {
  const res = await api.get('/movies/home/', { params: { page } })
  return res.data
}

export async function fetchMovies(params = {}) {
  // ✅ 백엔드가 /movies/list/ 임
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

export async function updateMyProfile(payload) {
  const res = await api.patch('/auth/me/profile/', payload)
  return res.data
}

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
