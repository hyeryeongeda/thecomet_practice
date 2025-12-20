<!-- frontend/src/views/HomeView.vue -->
<template>
  <div class="page">
    <!-- HERO -->
    <section class="hero">
      <h1 class="hero-title">지금 뭐 볼까?</h1>
      <p class="hero-sub">인기 / 최신 / 극찬작을 한 번에 둘러보자.</p>
    </section>

    <hr class="divider" />

    <!-- 1) POPULAR -->
    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">지금 뜨는 인기 영화</h2>
        <button class="more" @click="goMovies('popular')">더보기</button>
      </div>

      <p v-if="loading" class="muted">불러오는 중...</p>
      <p v-else-if="popular.length === 0" class="muted">데이터가 없습니다.</p>

      <MovieRow v-else :movies="popular" @click-movie="goDetail" />
    </section>

    <!-- 2) NOW_PLAYING -->
    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">최신 개봉작</h2>
        <button class="more" @click="goMovies('latest')">더보기</button>
      </div>

      <p v-if="loading" class="muted">불러오는 중...</p>
      <p v-else-if="nowPlaying.length === 0" class="muted">데이터가 없습니다.</p>

      <MovieRow v-else :movies="nowPlaying" @click-movie="goDetail" />
    </section>

    <!-- 3) TOP_RATED -->
    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">평론가가 극찬한 영화 (Top Rated)</h2>
        <button class="more" @click="goMovies('rating')">더보기</button>
      </div>

      <p v-if="loading" class="muted">불러오는 중...</p>
      <p v-else-if="topRated.length === 0" class="muted">데이터가 없습니다.</p>

      <MovieRow v-else :movies="topRated" @click-movie="goDetail" />
    </section>

    <!-- RECENT REVIEWS -->
    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">최근 코멘트</h2>
        <button class="more" @click="go('/mypage')">더보기</button>
      </div>

      <p v-if="reviewsLoading" class="muted">불러오는 중...</p>
      <p v-else-if="recentReviews.length === 0" class="muted">아직 작성된 리뷰가 없습니다.</p>

      <div v-else class="review-grid">
        <RecentReviewCard
          v-for="r in recentReviews"
          :key="r.id"
          :review="r"
          @click="goReviewTarget(r)"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchHomeSections, fetchRecentReviews } from '@/api/comet.js'

import MovieRow from '@/components/movie/MovieRow.vue'
import RecentReviewCard from '@/components/review/ReviewCard.vue' // ✅ 여기 핵심

const router = useRouter()

const loading = ref(false)
const popular = ref([])
const nowPlaying = ref([])
const topRated = ref([])

const reviewsLoading = ref(false)
const recentReviews = ref([])

function pickTmdbId(m) {
  return m?.tmdb_id ?? m?.tmdbId ?? m?.id ?? null
}

async function loadHome() {
  loading.value = true
  try {
    const data = await fetchHomeSections(1)

    // ✅ 백 응답 키에 맞춰서만 받기 (괜히 섞지 말고 확정)
    popular.value = data?.popular ?? []
    nowPlaying.value = data?.now_playing ?? []
    topRated.value = data?.top_rated ?? []
  } catch (e) {
    console.error('home load failed:', e)
    popular.value = []
    nowPlaying.value = []
    topRated.value = []
  } finally {
    loading.value = false
  }
}

async function loadRecentReviews() {
  reviewsLoading.value = true
  try {
    const data = await fetchRecentReviews(12)
    recentReviews.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (e) {
    console.error('recent reviews failed:', e)
    recentReviews.value = []
  } finally {
    reviewsLoading.value = false
  }
}

function go(path) {
  router.push(path)
}

function goDetail(movie) {
  const tmdbId = pickTmdbId(movie)
  if (!tmdbId) return
  router.push(`/movies/${tmdbId}`)
}

function goMovies(sort) {
  router.push({ path: '/movies', query: { sort } })
}

function goReviewTarget(r) {
  // ✅ 최근리뷰는 백에서 movie_tmdb_id를 내려주는 걸 기준으로
  const tmdbId = r?.movie_tmdb_id ?? r?.tmdb_id ?? null
  if (tmdbId) router.push(`/movies/${tmdbId}`)
}

onMounted(() => {
  loadHome()
  loadRecentReviews()
})
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px 14px 60px;
}
.hero {
  padding: 26px 0 18px;
}
.hero-title {
  margin: 0;
  font-size: 44px;
  font-weight: 900;
  letter-spacing: -0.02em;
}
.hero-sub {
  margin: 10px 0 0;
  color: #666;
  font-weight: 700;
}
.divider {
  border: none;
  border-top: 1px solid #eee;
  margin: 18px 0 22px;
}
.sec {
  margin-top: 18px;
}
.sec-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}
.sec-title {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
}
.more {
  border: none;
  background: transparent;
  cursor: pointer;
  color: #666;
  font-weight: 900;
}
.more:hover {
  text-decoration: underline;
}
.muted {
  color: #777;
  margin: 10px 0 0;
}
.review-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 900px) {
  .review-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 640px) {
  .hero-title {
    font-size: 34px;
  }
  .review-grid {
    grid-template-columns: 1fr;
  }
}
</style>
