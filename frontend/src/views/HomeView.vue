<template>
  <div class="page">
    <section class="hero">
      <h1 class="hero-title">지금 뭐 볼까?</h1>
      <p class="hero-sub">인기 / 최신 / 극찬작을 한 번에 둘러보자.</p>
    </section>

    <hr class="divider" />

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">지금 뜨는 인기 영화</h2>
        <button class="more" @click="goMovies('popular')">더보기</button>
      </div>
      <p v-if="loading" class="muted">불러오는 중...</p>
      <p v-else-if="popular.length === 0" class="muted">데이터가 없습니다.</p>
      <MovieRow v-else title="인기 영화" :movies="popular" @click-movie="goDetail" />
    </section>

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">최신 개봉 작품</h2>
        <button class="more" @click="goMovies('latest')">더보기</button>
      </div>
      <p v-if="loading" class="muted">불러오는 중...</p>
      <p v-else-if="nowPlaying.length === 0" class="muted">데이터가 없습니다.</p>
      <MovieRow v-else title="최신 개봉작" :movies="nowPlaying" @click-movie="goDetail" />
    </section>

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">평론가가 극찬한 영화</h2>
        <button class="more" @click="goMovies('rating')">더보기</button>
      </div>
      <p v-if="loading" class="muted">불러오는 중...</p>
      <p v-else-if="topRated.length === 0" class="muted">데이터가 없습니다.</p>
      <MovieRow v-else title="평론가 극찬작" :movies="topRated" @click-movie="goDetail" />
    </section>

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">최근 코멘트</h2>
        <button class="more" @click="go('/mypage')">더보기</button>
      </div>
      <p v-if="reviewsLoading" class="muted">불러오는 중...</p>
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
import RecentReviewCard from '@/components/review/ReviewCard.vue'

const router = useRouter()
const loading = ref(false)
const popular = ref([])
const nowPlaying = ref([])
const topRated = ref([])
const reviewsLoading = ref(false)
const recentReviews = ref([])

async function loadHome() {
  loading.value = true
  try {
    const data = await fetchHomeSections(1)
    popular.value = data?.popular ?? []
    nowPlaying.value = data?.now_playing ?? []
    topRated.value = data?.top_rated ?? []
  } finally {
    loading.value = false
  }
}

async function loadRecentReviews() {
  reviewsLoading.value = true
  try {
    const data = await fetchRecentReviews(12)
    recentReviews.value = Array.isArray(data) ? data : (data?.results || [])
  } finally {
    reviewsLoading.value = false
  }
}

function goDetail(movie) {
  const tmdbId = movie?.tmdb_id ?? movie?.id
  if (tmdbId) router.push(`/movies/${tmdbId}`)
}

function goMovies(sort) {
  router.push({ path: '/movies', query: { sort } })
}

function goReviewTarget(r) {
  const tmdbId = r?.movie_tmdb_id ?? r?.tmdb_id
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
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(3, 1fr); 
  gap: 20px;
}

@media (max-width: 900px) {
  .review-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .review-grid { grid-template-columns: 1fr; }
}
</style>
