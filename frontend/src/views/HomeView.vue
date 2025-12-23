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
        <button class="more" @click="openListModal">더보기</button>
      </div>
      <p v-if="reviewsLoading" class="muted">불러오는 중...</p>
      
      <div v-else class="review-grid">
        <ReviewCard
          v-for="r in recentReviews"
          :key="r.id"
          :review="r"
          @click="openReviewModal(r)"
        />
      </div>
    </section>

    <HomeReviewListModal
      v-if="showListModal"
      :reviews="recentReviews"
      @close="showListModal = false"
      @sort="handleSort"
      @select="openReviewModal"
    />

    <ReviewDetailModal
      v-if="showDetailModal && selectedReview"
      :review="selectedReview"
      :replies="reviewComments"
      :movie="selectedReview.movie" 
      @close="closeDetailModal"
      @submit-reply="handleReplySubmit"
      @toggle-like="handleReviewLike"
      @delete-reply="handleReplyDelete" 
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
  toggleReviewLike,
  deleteReviewComment 
} from '@/api/comet.js'

import MovieRow from '@/components/movie/MovieRow.vue'
import ReviewCard from '@/components/review/ReviewCard.vue'
import ReviewDetailModal from '@/components/review/ReviewDetailModal.vue'
// ✅ [추가] 새로 만든 리스트 모달 import
import HomeReviewListModal from '@/components/review/HomeReviewListModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const popular = ref([])
const nowPlaying = ref([])
const topRated = ref([])
const reviewsLoading = ref(false)
const recentReviews = ref([])

// 모달 상태
const showDetailModal = ref(false)
const showListModal = ref(false) // ✅ 리스트 모달 상태 추가
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
    // ✅ 더보기를 위해 좀 더 많이 가져오도록 설정 (20개)
    const data = await fetchRecentReviews(20)
    recentReviews.value = Array.isArray(data) ? data : (data?.results || [])
  } finally {
    reviewsLoading.value = false
  }
}

// [모달 열기]
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

// ✅ [추가] 리스트 모달 열기
function openListModal() {
  showListModal.value = true
}

// ✅ [추가] 정렬 핸들러 (홈 화면용)
function handleSort(sortType) {
  if (sortType === 'likes') {
    recentReviews.value.sort((a, b) => (b.likes_count || 0) - (a.likes_count || 0))
  } else {
    // 최신순
    recentReviews.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
}

// [댓글 작성]
async function handleReplySubmit(content) {
  if (!authStore.isLoggedIn) return alert('로그인 후 이용해주세요.')
  
  // 삭제 후 갱신 요청(null)인 경우 목록만 다시 불러옴
  if (content === null) {
    reviewComments.value = await fetchReviewComments(selectedReview.value.id)
    return
  }

  try {
    await createReviewComment(selectedReview.value.id, content)
    reviewComments.value = await fetchReviewComments(selectedReview.value.id)
    
    // ✅ [추가] 카드 UI의 댓글 개수 즉시 증가
    if (selectedReview.value) {
      selectedReview.value.comments_count = (selectedReview.value.comments_count || 0) + 1
    }
  } catch (e) {
    alert('댓글 작성 실패')
  }
}

// ✅ [추가] 댓글 삭제 핸들러 (홈 화면 즉시 반영용)
function handleReplyDelete(commentId) {
  // 1. 모달 내부 리스트에서 제거
  reviewComments.value = reviewComments.value.filter(c => c.id !== commentId)

  // 2. 홈 화면 카드의 댓글 개수 감소
  if (selectedReview.value) {
    selectedReview.value.comments_count = Math.max(0, (selectedReview.value.comments_count || 0) - 1)
  }
}

// [좋아요 토글]
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

// 영화 상세페이지 이동 (포스터 클릭 등)
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
/* 🎨 레이아웃 구조는 유지하고 색상만 테마 변수로 교체 */

.page { 
  max-width: 1100px; 
  margin: 0 auto; 
  padding: 20px 14px 60px; 
  background: var(--bg); /* 배경색 대응 */
  color: var(--text);    /* 글자색 대응 */
}

.hero { padding: 26px 0 18px; }
.hero-title { 
  margin: 0; 
  font-size: 44px; 
  font-weight: 900; 
  letter-spacing: -0.02em; 
  color: var(--text); /* #111 -> var(--text) */
}
.hero-sub { 
  margin: 10px 0 0; 
  color: var(--muted); /* #666 -> var(--muted) */
  font-weight: 700; 
}

.divider { 
  border: none; 
  border-top: 1px solid var(--border); /* #eee -> var(--border) */
  margin: 18px 0 22px; 
}

.sec { margin-top: 18px; }
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
  color: var(--text); 
}

.more { 
  border: none; 
  background: transparent; 
  cursor: pointer; 
  color: var(--muted); /* #666 -> var(--muted) */
  font-weight: 900; 
  transition: color 0.2s;
}
.more:hover { 
  text-decoration: underline; 
  color: var(--primary); /* 호버 시 테마별 포인트 컬러 적용 */
}

.muted { 
  color: var(--muted); /* #777 -> var(--muted) */
  margin: 10px 0 0; 
}

/* 리뷰 그리드 레이아웃 유지 */
.review-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(3, 1fr); 
  gap: 20px;
}

@media (max-width: 900px) { .review-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .review-grid { grid-template-columns: 1fr; } }
</style>