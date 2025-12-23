<template>
  <div class="page">
    <section class="hero">
      <h1 class="hero-title">지금 뭐 볼까?</h1>
      <p class="hero-sub">인기 / 최신 / 극찬작을 한 번에 둘러보자.</p>
    </section>

    <section class="banner-section">
      <div class="banner-container">
        <div 
          class="banner-slide" 
          @click="goBannerLink(banners[currentIndex].link)"
        >
          <img :src="banners[currentIndex].image" class="banner-img" alt="메인 배너" />
        </div>

        <button class="banner-nav-btn prev" @click="prevBanner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>
        </button>
        <button class="banner-nav-btn next" @click="nextBanner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </button>

        <div class="dots-container">
          <span 
            v-for="(banner, index) in banners" 
            :key="index" 
            class="dot" 
            :class="{ active: index === currentIndex }"
            @click="setBanner(index)"
          ></span>
        </div>
      </div>
    </section>

    <hr class="divider" />

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">지금 뜨는 인기 영화</h2>
        <button class="more" @click="goMovies('popular')">더보기</button>
      </div>
      <MovieRow v-if="!loading" title="인기 영화" :movies="popular" @click-movie="goDetail" />
    </section>

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">최신 개봉 작품</h2>
        <button class="more" @click="goMovies('latest')">더보기</button>
      </div>
      <MovieRow v-if="!loading" title="최신 개봉작" :movies="nowPlaying" @click-movie="goDetail" />
    </section>

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">평론가가 극찬한 영화</h2>
        <button class="more" @click="goMovies('rating')">더보기</button>
      </div>
      <MovieRow v-if="!loading" title="평론가 극찬작" :movies="topRated" @click-movie="goDetail" />
    </section>

    <section class="sec">
      <div class="sec-head">
        <h2 class="sec-title">최근 코멘트</h2>
        <button class="more" @click="go('/mypage')">더보기</button>
      </div>
      <p v-if="reviewsLoading" class="muted">불러오는 중...</p>
      
      <div v-else class="review-slider-wrapper">
        <button class="slider-nav-btn left" @click="scrollPrev">‹</button>

        <div class="review-scroll-container" ref="scrollContainer">
          <ReviewCard
            v-for="r in recentReviews"
            :key="r.id"
            :review="r"
            class="slider-item"
            @click="openReviewModal(r)"
          />
        </div>

        <button class="slider-nav-btn right" @click="scrollNext">›</button>
      </div>
    </section>

    <ReviewDetailModal
      v-if="showDetailModal && selectedReview"
      :review="selectedReview"
      :replies="reviewComments"
      :movie="selectedReview.movie" 
      @close="closeDetailModal"
      @submit-reply="handleReplySubmit"
      @toggle-like="handleReviewLike"
      @delete-reply="handleReplyDelete"
      @delete-review="handleReviewDeleteLocal"
      @update-review="handleReviewUpdateLocal"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  fetchHomeSections, 
  fetchRecentReviews, 
  fetchReviewComments, 
  createReviewComment, 
  toggleReviewLike 
} from '@/api/comet.js'

import MovieRow from '@/components/movie/MovieRow.vue'
import ReviewCard from '@/components/review/ReviewCard.vue'
import ReviewDetailModal from '@/components/review/ReviewDetailModal.vue'

const router = useRouter()
const authStore = useAuthStore()

/* --- [배너 데이터 & 로직] --- */
const currentIndex = ref(0)
const banners = ref([
  { 
    image: 'https://via.placeholder.com/1600x685/111111/FFFFFF?text=21:9+AD+Banner+1', 
    link: '/movies' 
  },
  { 
    image: 'https://via.placeholder.com/1600x685/222222/FFFFFF?text=21:9+AD+Banner+2', 
    link: '/mypage'
  },
  { 
    image: 'https://via.placeholder.com/1600x685/333333/FFFFFF?text=21:9+AD+Banner+3', 
    link: '#'
  }
])

function nextBanner() {
  currentIndex.value = (currentIndex.value + 1) % banners.value.length
}
function prevBanner() {
  currentIndex.value = (currentIndex.value - 1 + banners.value.length) % banners.value.length
}
function setBanner(index) {
  currentIndex.value = index
}
function goBannerLink(link) {
  if (link && link !== '#') router.push(link)
}

/* --- [댓글 슬라이더 로직] --- */
const scrollContainer = ref(null)

const scrollPrev = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollBy({
      left: -scrollContainer.value.clientWidth, // 화면 너비만큼 왼쪽 이동
      behavior: 'smooth'
    })
  }
}

const scrollNext = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollBy({
      left: scrollContainer.value.clientWidth, // 화면 너비만큼 오른쪽 이동
      behavior: 'smooth'
    })
  }
}

/* --- [기본 데이터 로딩] --- */
const loading = ref(false)
const popular = ref([])
const nowPlaying = ref([])
const topRated = ref([])
const reviewsLoading = ref(false)
const recentReviews = ref([])

// 모달 상태
const showDetailModal = ref(false)
const selectedReview = ref(null)
const reviewComments = ref([])

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

/* --- [모달 및 기능 함수들] --- */
async function openReviewModal(review) {
  selectedReview.value = review
  try {
    const res = await fetchReviewComments(review.id)
    reviewComments.value = res || []
  } catch (e) {
    reviewComments.value = []
  }
  showDetailModal.value = true
}

function closeDetailModal() {
  showDetailModal.value = false
  selectedReview.value = null
}

function handleReviewDeleteLocal(reviewId) {
  recentReviews.value = recentReviews.value.filter(r => r.id !== reviewId)
  closeDetailModal()
}

function handleReviewUpdateLocal(updatedReview) {
  const idx = recentReviews.value.findIndex(r => r.id === updatedReview.id)
  if (idx !== -1) {
    recentReviews.value[idx] = { ...recentReviews.value[idx], ...updatedReview }
  }
  if (selectedReview.value && selectedReview.value.id === updatedReview.id) {
    selectedReview.value = { ...selectedReview.value, ...updatedReview }
  }
}

async function handleReplySubmit(content) {
  if (!authStore.isLoggedIn) return alert('로그인 후 이용해주세요.')
  try {
    await createReviewComment(selectedReview.value.id, content)
    reviewComments.value = await fetchReviewComments(selectedReview.value.id)
  } catch (e) {
    alert('댓글 작성 실패')
  }
}

function handleReplyDelete(commentId) {
  reviewComments.value = reviewComments.value.filter(c => c.id !== commentId)
}

async function handleReviewLike(reviewId) {
  if (!authStore.isLoggedIn) return alert('로그인 후 이용해주세요.')
  try {
    const res = await toggleReviewLike(reviewId)
    if (selectedReview.value) {
      selectedReview.value.is_liked = res.liked
      selectedReview.value.likes_count = res.like_count
    }
    const target = recentReviews.value.find(r => r.id === reviewId)
    if (target) {
      target.is_liked = res.liked
      target.likes_count = res.like_count
    }
  } catch (e) {
    alert('오류 발생')
  }
}

function goDetail(movie) {
  const tmdbId = movie?.tmdb_id ?? movie?.id
  if (tmdbId) router.push(`/movies/${tmdbId}`)
}

function goMovies(sort) {
  router.push({ path: '/movies', query: { sort } })
}

function go(path) {
  router.push(path)
}

onMounted(() => {
  loadHome()
  loadRecentReviews()
})
</script>

<style scoped>
/* =========================================
   1. 공통 레이아웃
   ========================================= */
.page { 
  max-width: 1100px; 
  margin: 0 auto; 
  padding: 20px 14px 60px; 
  color: var(--text);
}
.hero { padding: 26px 0 18px; }
.hero-title { margin: 0; font-size: 44px; font-weight: 900; letter-spacing: -0.02em; color: var(--text); }
.hero-sub { margin: 10px 0 0; color: #666; font-weight: 700; }

.divider { border: none; border-top: 1px solid #eee; margin: 18px 0 22px; }
.sec { margin-top: 18px; }
.sec-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px; }
.sec-title { margin: 0; font-size: 18px; font-weight: 900; color: var(--text); }
.more { border: none; background: transparent; cursor: pointer; color: #666; font-weight: 900; }
.more:hover { text-decoration: underline; color: var(--primary); }
.muted { color: #777; margin: 10px 0 0; }


/* =========================================
   2. 배너 섹션 스타일 (21:9)
   ========================================= */
.banner-section { margin-top: 10px; margin-bottom: 30px; }
.banner-container { 
  position: relative; 
  width: 100%; 
  aspect-ratio: 21 / 9; 
  border-radius: 12px; 
  overflow: hidden; 
  background: #000;
}
.banner-slide { width: 100%; height: 100%; cursor: pointer; }
.banner-img { width: 100%; height: 100%; object-fit: cover; }

/* 배너 전용 버튼 (투명하고 큰 영역) */
.banner-nav-btn {
  position: absolute;
  top: 0; bottom: 0;
  width: 15%;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.3s;
  z-index: 5;
}
.banner-nav-btn:hover { color: rgba(255, 255, 255, 1); }
.banner-nav-btn.prev { left: 0; justify-content: flex-start; padding-left: 20px; }
.banner-nav-btn.next { right: 0; justify-content: flex-end; padding-right: 20px; }
.banner-nav-btn svg { width: 40px; height: 40px; filter: drop-shadow(0 0 4px rgba(0,0,0,0.5)); }

/* 배너 점(Pagination) */
.dots-container {
  position: absolute; bottom: 16px; left: 50%;
  transform: translateX(-50%);
  display: flex; gap: 8px; z-index: 10;
}
.dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer; transition: all 0.2s;
}
.dot:hover { background: rgba(255, 255, 255, 0.8); }
.dot.active { background: #fff; transform: scale(1.2); }


/* =========================================
   3. 리뷰 슬라이더 스타일 (새로운 기능)
   ========================================= */
.review-slider-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.review-scroll-container {
  display: grid;
  grid-template-rows: repeat(2, 1fr); /* 2줄 고정 */
  grid-auto-flow: column; /* 가로 흐름 */
  grid-auto-columns: calc(33.333% - 10.7px); /* 3개씩 보기 */
  gap: 16px;
  overflow-x: auto;
  scroll-behavior: smooth;
  scroll-snap-type: x mandatory;
  padding: 10px 0;
  
  /* 스크롤바 숨김 */
  scrollbar-width: none; 
  -ms-overflow-style: none;
}
.review-scroll-container::-webkit-scrollbar { display: none; }

.slider-item {
  width: 100%;
  scroll-snap-align: start;
}

/* 슬라이더 전용 버튼 (작은 동그라미) */
.slider-nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px; height: 44px;
  border-radius: 50%;
  background: var(--card, #fff);
  border: 1px solid #eee;
  color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  z-index: 10;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  font-size: 24px; line-height: 1;
}
.slider-nav-btn:hover {
  background: var(--primary, #ff2f6e);
  color: #fff;
  border-color: var(--primary, #ff2f6e);
  transform: translateY(-50%) scale(1.1);
}
.slider-nav-btn.left { left: -22px; }
.slider-nav-btn.right { right: -22px; }

/* 반응형 */
@media (max-width: 900px) {
  .review-scroll-container { grid-auto-columns: calc(50% - 8px); } /* 태블릿: 2개씩 */
}
@media (max-width: 600px) {
  .review-scroll-container { 
    grid-template-rows: 1fr; /* 모바일: 1줄 */
    grid-auto-columns: 85%; /* 옆에꺼 살짝 보이게 */
  }
}
</style>