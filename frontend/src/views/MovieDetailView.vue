<template>
  <main class="page">
    <div v-if="loading" class="container">로딩중...</div>

    <div v-else-if="!movie" class="container">
      영화를 불러오지 못했습니다.
    </div>

    <div v-else class="container">
      <!-- 상단 히어로 -->
      <section class="hero">
        <div class="poster-wrap">
          <img v-if="posterSrc" :src="posterSrc" class="poster" />
          <div v-else class="poster-fallback">No Image</div>
        </div>

        <div class="info">
          <h1 class="title">{{ movie.title }}</h1>

          <p class="meta">
            <span v-if="movie.release_date">{{ movie.release_date.slice(0, 4) }}</span>
            <span v-if="movie.runtime"> · {{ movie.runtime }}분</span>
            <span v-if="movie.vote_average"> · ★ {{ Number(movie.vote_average).toFixed(1) }}</span>
          </p>

          <!-- 장르 -->
          <div class="chips" v-if="movie.genres?.length">
            <span class="chip" v-for="g in movie.genres" :key="g.tmdb_id ?? g.id">
              {{ g.name }}
            </span>
          </div>

          <p class="overview">
            {{ movie.overview || '줄거리가 없습니다.' }}
          </p>

          <!-- 예고편(일단 버튼만 - 트레일러 키 붙이는 단계는 다음) -->
          <button class="btn" disabled>
            예고편 (다음 단계에서 연결)
          </button>
        </div>
      </section>

      <!-- 리뷰 영역 -->
      <section class="reviews">
        <div class="reviews-head">
          <h2 class="h2">리뷰</h2>
        </div>

        <div v-if="!isLoggedIn" class="hint">
          리뷰 작성은 로그인 후 가능합니다.
        </div>

        <!-- 리뷰 작성 -->
        <ReviewForm
          v-if="isLoggedIn"
          :tmdb-id="Number(tmdbId)"
          @submitted="reloadReviews"
        />

        <!-- 리뷰 리스트 -->
        <ReviewList :tmdb-id="tmdbId" />
      </section>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import {
  fetchMovieDetail,
  fetchMovieReviews,
  toggleReviewLike,
  deleteReview,
  updateReview,
} from '@/api/comet'

// ✅ 유저가 이미 만들어둔 컴포넌트 사용
import ReviewForm from '@/components/review/ReviewForm.vue'
import ReviewList from '@/components/review/ReviewList.vue'

const route = useRoute()
const tmdbId = computed(() => route.params.tmdbId)

const loading = ref(true)
const movie = ref(null)
const reviews = ref([])

// 로그인 판별(간단 버전)
const isLoggedIn = computed(() => !!localStorage.getItem('access'))
const myUsername = computed(() => localStorage.getItem('username') || '') // 없으면 빈값

const posterSrc = computed(() => {
  const p = movie.value?.poster_path
  return p ? `https://image.tmdb.org/t/p/w500${p}` : ''
})

async function loadAll() {
  loading.value = true
  try {
    const [m, r] = await Promise.all([
      fetchMovieDetail(Number(tmdbId.value)),
      fetchMovieReviews(Number(tmdbId.value)),
    ])
    movie.value = m
    reviews.value = Array.isArray(r) ? r : (r?.results ?? [])
  } catch (e) {
    console.error('Movie detail load failed:', e)
    movie.value = null
    reviews.value = []
  } finally {
    loading.value = false
  }
}

async function reloadReviews() {
  try {
    const r = await fetchMovieReviews(Number(tmdbId.value))
    reviews.value = Array.isArray(r) ? r : (r?.results ?? [])
  } catch (e) {
    console.error('reloadReviews failed:', e)
  }
}

async function onLike(reviewId) {
  try {
    await toggleReviewLike(reviewId)
    await reloadReviews()
  } catch (e) {
    console.error('like failed:', e)
  }
}

async function onRemove(reviewId) {
  try {
    await deleteReview(reviewId)
    await reloadReviews()
  } catch (e) {
    console.error('delete failed:', e)
  }
}

async function onUpdate({ reviewId, payload }) {
  try {
    await updateReview(reviewId, payload)
    await reloadReviews()
  } catch (e) {
    console.error('update failed:', e)
  }
}

onMounted(loadAll)
watch(() => tmdbId.value, loadAll)
</script>

<style scoped>
.page {
  background: #fff;
  min-height: calc(100vh - 60px);
}

.container {
  width: min(1100px, 92vw);
  margin: 0 auto;
  padding: 22px 0 60px;
}

.hero {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 18px;
  align-items: start;
}

.poster-wrap {
  width: 220px;
  height: 330px;
  border-radius: 14px;
  overflow: hidden;
  background: #f2f2f2;
  box-shadow: 0 8px 18px rgba(0,0,0,0.08);
}

.poster { width: 100%; height: 100%; object-fit: cover; }
.poster-fallback { width: 100%; height: 100%; display: grid; place-items: center; color: #777; }

.title {
  margin: 0;
  font-size: 28px;
  font-weight: 900;
  color: #111;
}

.meta {
  margin: 8px 0 12px;
  color: #666;
  font-weight: 600;
}

.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.chip {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid #e7e7e7;
  background: #fafafa;
  font-size: 12px;
  color: #333;
  font-weight: 700;
}

.overview { color: #444; line-height: 1.55; }

.btn {
  margin-top: 14px;
  height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid #ddd;
  background: white;
  font-weight: 800;
}

.reviews { margin-top: 30px; }
.reviews-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.h2 { margin: 0; font-size: 20px; font-weight: 900; color: #111; }

.hint {
  padding: 12px 14px;
  border: 1px dashed #ddd;
  border-radius: 12px;
  background: #fafafa;
  color: #666;
  margin-bottom: 12px;
}
</style>
