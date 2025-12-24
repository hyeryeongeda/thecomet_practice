<template>
  <div class="page">
    <section class="hero">
      <h1 class="hero-title">지금 뭐 볼까?</h1>
      <p class="hero-sub">인기 / 최신 / 극찬작을 한 번에 둘러보자.</p>
    </section>

    <section class="banner-section" v-if="banners.length > 0">
      <div 
        class="banner-container"
        @mouseenter="stopAutoSlide"
        @mouseleave="startAutoSlide"
      >
        <div 
          class="banner-slide" 
          @click="goBannerLink(banners[currentIndex].link)"
        >
          <img :src="banners[currentIndex].image" class="banner-img" alt="메인 배너" />
          <div class="banner-overlay">
            <span class="banner-label">{{ banners[currentIndex].label }}</span>
            <h2 class="banner-title">{{ banners[currentIndex].title }}</h2>
            <p class="banner-desc">{{ banners[currentIndex].desc }}</p>
          </div>
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
        <button class="more" @click="showListModal = true">더보기</button>
      </div>
      <ReviewListModal
        v-if="showListModal"
        :reviews="recentReviews"
        @close="showListModal = false"
        @sort="handleSort"
        @select="openReviewModalFromList"
      />
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
import { onMounted, onUnmounted, ref } from 'vue'
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
import ReviewListModal from '@/components/review/ReviewListModal.vue'
const router = useRouter()
const authStore = useAuthStore()
const TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/original'

// 배너 배열 구성 함수
const currentIndex = ref(0)
const banners = ref([])
const slideTimer = ref(null)

// 배너 배열 구성 함수
function setupBanners() {
  const list = []

  // 1. 최신 개봉작 랜덤 배너 (기존 유지)
  if (nowPlaying.value.length > 0) {
    const randomIdx = Math.floor(Math.random() * nowPlaying.value.length)
    const movie = nowPlaying.value[randomIdx]
    list.push({
      image: movie.backdrop_path ? `${TMDB_IMAGE_BASE}${movie.backdrop_path}` : 'https://via.placeholder.com/1600x685?text=Comet+Movie',
      link: `/movies/${movie.tmdb_id || movie.id}`,
      label: '최신 개봉작',
      title: movie.title,
      desc: '지금 바로 혜성에서 상세 정보를 확인하세요.'
    })
  }

  // 2. 최근 리뷰 배너 (수정됨: 본인 제외 & 랜덤 추출)
  if (recentReviews.value.length > 0) {
    const myUsername = authStore.user?.username
    
    // 내 아이디와 다른 유저의 리뷰만 필터링
    const othersReviews = recentReviews.value.filter(r => r.user?.username !== myUsername)
    
    // 보여줄 리뷰 후보 선정 (남의 리뷰가 있으면 그 중에서, 없으면 전체에서)
    const targetPool = othersReviews.length > 0 ? othersReviews : recentReviews.value
    
    // 랜덤 인덱스 선택
    const randomReviewIdx = Math.floor(Math.random() * targetPool.length)
    const review = targetPool[randomReviewIdx]

    list.push({
      image: review.movie?.backdrop_path ? `${TMDB_IMAGE_BASE}${review.movie.backdrop_path}` : 'https://via.placeholder.com/1600x685?text=User+Review',
      link: `/movies/${review.movie?.tmdb_id}`,
      label: '베스트 코멘트',
      title: review.content.length > 25 ? review.content.substring(0, 25) + '...' : review.content,
      desc: `${review.user?.username || '사용자'}님의 솔직한 리뷰`
    })
  }

  // 3. 가이드 페이지 배너 (기존 유지)
  list.push({
    image: 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2000&auto=format&fit=crop',
    link: '/guide',
    label: '이용 가이드',
    title: '혜성, 어떻게 이용하나요?',
    desc: '서비스 사용법과 꿀팁을 확인해보세요.'
  })

  banners.value = list
}

// 자동 슬라이드 시작
function startAutoSlide() {
  stopAutoSlide() // 중복 방지
  slideTimer.value = setInterval(() => {
    nextBanner()
  }, 5000) // 5초마다 전환
}

// 자동 슬라이드 정지
function stopAutoSlide() {
  if (slideTimer.value) clearInterval(slideTimer.value)
}

function nextBanner() {
  currentIndex.value = (currentIndex.value + 1) % banners.value.length
}
function prevBanner() {
  currentIndex.value = (currentIndex.value - 1 + banners.value.length) % banners.value.length
}
function setBanner(index) {
  currentIndex.value = index
  startAutoSlide() // 클릭 시 타이머 리셋
}
function goBannerLink(link) {
  if (link && link !== '#') router.push(link)
}

const loading = ref(false)
const popular = ref([])
const nowPlaying = ref([])
const topRated = ref([])
const reviewsLoading = ref(false)
const recentReviews = ref([])
const scrollContainer = ref(null)

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
    setupBanners() // 데이터 로드 후 배너 설정
  } finally {
    loading.value = false
  }
}

async function loadRecentReviews() {
  reviewsLoading.value = true
  try {
    const data = await fetchRecentReviews(12)
    recentReviews.value = Array.isArray(data) ? data : (data?.results || [])
    setupBanners() // 리뷰 로드 후 배너 다시 설정
  } finally {
    reviewsLoading.value = false
  }
}

// 슬라이더 이동
const scrollPrev = () => scrollContainer.value?.scrollBy({ left: -scrollContainer.value.clientWidth, behavior: 'smooth' })
const scrollNext = () => scrollContainer.value?.scrollBy({ left: scrollContainer.value.clientWidth, behavior: 'smooth' })

// 모달/액션 함수 (기존과 동일)
async function openReviewModal(review) {
  selectedReview.value = review
  try { reviewComments.value = await fetchReviewComments(review.id) || [] } catch (e) { reviewComments.value = [] }
  showDetailModal.value = true
}
function closeDetailModal() { showDetailModal.value = false; selectedReview.value = null; }
function handleReviewDeleteLocal(id) { recentReviews.value = recentReviews.value.filter(r => r.id !== id); closeDetailModal(); }
function handleReviewUpdateLocal(updated) {
  const idx = recentReviews.value.findIndex(r => r.id === updated.id)
  if (idx !== -1) recentReviews.value[idx] = { ...recentReviews.value[idx], ...updated }
  if (selectedReview.value?.id === updated.id) selectedReview.value = { ...selectedReview.value, ...updated }
}
async function handleReplySubmit(content) {
  if (!authStore.isLoggedIn) return alert('로그인 후 이용해주세요.')
  try {
    await createReviewComment(selectedReview.value.id, content)
    reviewComments.value = await fetchReviewComments(selectedReview.value.id)
  } catch (e) { alert('댓글 작성 실패') }
}
function handleReplyDelete(id) { reviewComments.value = reviewComments.value.filter(c => c.id !== id) }
async function handleReviewLike(id) {
  if (!authStore.isLoggedIn) return alert('로그인 후 이용해주세요.')
  try {
    const res = await toggleReviewLike(id)
    if (selectedReview.value) { selectedReview.value.is_liked = res.liked; selectedReview.value.likes_count = res.like_count; }
    const target = recentReviews.value.find(r => r.id === id)
    if (target) { target.is_liked = res.liked; target.likes_count = res.like_count; }
  } catch (e) { alert('오류 발생') }
}

function goDetail(movie) {
  const tmdbId = movie?.tmdb_id ?? movie?.id
  if (tmdbId) router.push(`/movies/${tmdbId}`)
}
function goMovies(sort) { router.push({ path: '/movies', query: { sort } }) }
function go(path) { router.push(path) }

onMounted(() => {
  loadHome()
  loadRecentReviews()
  startAutoSlide()
})

onUnmounted(() => {
  stopAutoSlide()
})

const showListModal = ref(false)

// 2. 정렬 함수 (ReviewListModal의 @sort 대응)
function handleSort(sortType) {
  if (sortType === 'likes') {
    recentReviews.value.sort((a, b) => (b.likes_count || 0) - (a.likes_count || 0))
  } else if (sortType === 'latest') {
    recentReviews.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
}

// 3. 리스트 모달에서 하나를 클릭했을 때의 처리
function openReviewModalFromList(review) {
  showListModal.value = false // 리스트 모달 닫기
  openReviewModal(review)    // 기존에 만든 상세 모달 열기 함수 호출
}
</script>

<style scoped>
/* =========================================
   1. 공통 레이아웃 및 텍스트
   ========================================= */
.page { 
  max-width: 1100px; 
  margin: 0 auto; 
  padding: 20px 14px 60px; 
  color: var(--text); 
}
.hero { padding: 30px 0 20px; }
.hero-title { 
  margin: 0; 
  font-size: 48px; 
  font-weight: 900; 
  letter-spacing: -0.03em; 
  color: var(--text);
  line-height: 1.1;
}
.hero-sub { 
  margin: 12px 0 0; 
  color: var(--muted, #888); 
  font-size: 18px;
  font-weight: 700; 
}

.divider { 
  border: none; 
  border-top: 1px solid var(--border, #eee); 
  margin: 20px 0 25px; 
}
.sec { margin-top: 24px; }
.sec-head { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  margin-bottom: 12px; 
}
.sec-title { 
  margin: 0; 
  font-size: 20px; 
  font-weight: 900; 
  color: var(--text);
  letter-spacing: -0.01em;
}
.more { 
  border: none; 
  background: transparent; 
  cursor: pointer; 
  color: var(--muted, #888); 
  font-weight: 800; 
  font-size: 14px;
  transition: 0.2s;
}
.more:hover { 
  color: var(--primary, #ff2f6e); 
  text-decoration: none; /* 깔끔하게 색상만 변경 */
}

/* =========================================
   2. 배너 섹션 (21:9 시네마틱)
   ========================================= */
.banner-section { margin-top: 10px; margin-bottom: 40px; }
.banner-container { 
  position: relative; 
  width: 100%; 
  aspect-ratio: 21 / 9; 
  border-radius: 16px; 
  overflow: hidden; 
  background: #000;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.banner-slide::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* 하단으로 갈수록 어두워지는 그라데이션 (넷플릭스 스타일) */
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0) 20%,   /* 상단은 투명 */
    rgba(0, 0, 0, 0.4) 60%, /* 중간부터 조금씩 어두워짐 */
    rgba(0, 0, 0, 0.8) 100% /* 하단 글자 영역은 확실히 어둡게 */
  );
  z-index: 1;
}
.banner-img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
  transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94); 
  opacity: 0.85; /* 텍스트 가독성을 위해 살짝 어둡게 */
}
.banner-slide:hover .banner-img { transform: scale(1.03); opacity: 1; }

/* 배너 텍스트 오버레이 */
.banner-overlay {
  position: absolute;
  left: 50px;
  bottom: 45px;
  color: #ffffff; /* 텍스트는 항상 흰색 유지 */
  z-index: 2;     /* 그라데이션(1)보다 위로 */
  max-width: 75%;
  pointer-events: none;
}
.banner-label {
  display: inline-block;
  background: var(--primary, #ff2f6e);
  color: #fff;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 800;
  margin-bottom: 14px;
  text-shadow: none;
}
/* 글자에 텍스트 그림자를 더 강하게 주어 가독성 끝판왕 만들기 */
.banner-title {
  font-size: 36px;
  font-weight: 900;
  margin: 0;
  line-height: 1.2;
  word-break: keep-all;
  color: rgba(255, 255, 255, 0.9); 
  /* 다중 그림자로 글자 테두리를 살짝 잡아줍니다 */
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 0, 0, 0.3);
}
.banner-desc {
  font-size: 18px;
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.9); /* 약간 투명한 흰색 */
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

/* 배너 네비게이션 */
/* 공통 스타일 (기존 유지) */
.banner-nav-btn {
  position: absolute; 
  top: 0; 
  bottom: 0; 
  width: 8%; /* 클릭 영역을 적절히 확보 */
  background: transparent; 
  border: none; 
  cursor: pointer;
  display: flex; 
  align-items: center; 
  justify-content: center;
  color: rgba(255, 255, 255, 0.4); 
  transition: all 0.3s; 
  z-index: 5;
}

/*왼쪽 버튼 위치 */
.banner-nav-btn.prev {
  left: 0;
  /* 살짝 왼쪽으로 그라데이션을 주면 더 고급스러워요 */
  background: linear-gradient(to right, rgba(0,0,0,0.2), transparent);
}

/*  오른쪽 버튼 위치 */
.banner-nav-btn.next {
  right: 0;
  /* 살짝 오른쪽으로 그라데이션 */
  background: linear-gradient(to left, rgba(0,0,0,0.2), transparent);
}

/* 호버 시 스타일 */
.banner-nav-btn:hover { 
  color: #fff; 
  background: rgba(0, 0, 0, 0.3); /* 호버 시 배경을 조금 더 어둡게 해서 버튼 강조 */
}

.banner-nav-btn svg { 
  width: 44px; 
  height: 44px; 
  filter: drop-shadow(0 0 8px rgba(0,0,0,0.8)); 
}
.dots-container {
  position: absolute;
  /* 텍스트(bottom: 45px)보다 약간 아래 혹은 비슷한 높이에 배치 */
  bottom: 10px; 
  left: 50%; 
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 10;
  
  /* [선택 사항] 점들이 배경에 묻힐까봐 걱정된다면 살짝 배경색을 줄 수도 있습니다. */
  background: rgba(0, 0, 0, 0.2);
  padding: 8px 12px;
  border-radius: 20px;
  backdrop-filter: blur(4px); /* 뒤쪽 이미지를 살짝 흐리게 해서 점들을 더 돋보이게 */
}
.dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.3); cursor: pointer; transition: 0.3s;
}
.dot.active { 
  background: var(--primary, #ff2f6e); 
  transform: scale(1.3); 
  box-shadow: 0 0 10px rgba(255, 47, 110, 0.5);
}

/* =========================================
   3. 리뷰 슬라이더 (그리드 레이아웃)
   ========================================= */
.review-slider-wrapper { position: relative; display: flex; align-items: center; width: 100%; }
.review-scroll-container {
  display: grid; 
  grid-template-rows: repeat(2, 1fr); 
  grid-auto-flow: column;
  grid-auto-columns: calc(33.333% - 10.7px); 
  gap: 16px;
  overflow-x: auto; 
  scroll-behavior: smooth; 
  scroll-snap-type: x mandatory;
  padding: 10px 0; 
  scrollbar-width: none;
}
.review-scroll-container::-webkit-scrollbar { display: none; }
.slider-item { 
  width: 100%; 
  scroll-snap-align: start; 
  cursor: pointer; 
  transition: transform 0.2s ease;
}
.slider-item:hover { transform: translateY(-5px); }

/* 슬라이더 화살표 버튼 */
.slider-nav-btn {
  position: absolute; top: 50%; transform: translateY(-50%);
  width: 44px; height: 44px; border-radius: 50%;
  background: var(--card, #fff); 
  border: 1px solid var(--border, #eee); 
  color: var(--text);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  cursor: pointer; z-index: 10; 
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; transition: all 0.2s ease;
}
.slider-nav-btn:hover { 
  background: var(--primary, #ff2f6e); 
  color: #fff; 
  border-color: var(--primary);
  transform: translateY(-50%) scale(1.1); 
}
.slider-nav-btn.left { left: -22px; }
.slider-nav-btn.right { right: -22px; }

/* =========================================
   4. 반응형 대응
   ========================================= */
@media (max-width: 900px) {
  .hero-title { font-size: 36px; }
  .banner-title { font-size: 28px; }
  .review-scroll-container { grid-auto-columns: calc(50% - 8px); }
}

@media (max-width: 600px) {
  .hero-title { font-size: 28px; }
  .hero-sub { font-size: 15px; }

  /* 배너 컨테이너 비율 조정 */
  .banner-container { aspect-ratio: 16 / 9; }

  /* 텍스트 위치를 요청하신 대로 45px로 상향 조정 */
  .banner-overlay { 
    left: 20px; 
    bottom: 45px; /* 텍스트가 더 위로 올라감 */
    max-width: 90%; 
  }
  .banner-title { font-size: 20px; }
  .banner-desc { font-size: 14px; }

  /* 텍스트와 겹치지 않게 점(dots)은 하단 구석이나 바닥에 배치 */
  .dots-container {
    right: 20px;      /* 오른쪽 구석 */
    bottom: 15px;     /* 텍스트(45px)보다 아래에 위치하여 겹침 방지 */
    left: auto;
    transform: none;
    padding: 4px 8px; /* 모바일용으로 더 작게 */
  }

  .banner-nav-btn { display: none; } /* 모바일 버튼 숨김 유지 */

  .review-scroll-container { 
    grid-template-rows: 1fr; 
    grid-auto-columns: 85%; 
  }
}
</style>