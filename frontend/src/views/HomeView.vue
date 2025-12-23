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
      
      <div v-else class="review-grid">
        <ReviewCard
          v-for="r in recentReviews"
          :key="r.id"
          :review="r"
          @click="openReviewModal(r)"
        />
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

// 🔥 [삭제 반영] 리스트에서 리뷰 삭제 (새로고침 없이 반영)
function handleReviewDeleteLocal(reviewId) {
  recentReviews.value = recentReviews.value.filter(r => r.id !== reviewId)
  closeDetailModal()
}

// 🔥 [수정 반영] 리스트에 수정 내용 덮어쓰기 (새로고침 없이 반영)
function handleReviewUpdateLocal(updatedReview) {
  // 리스트에서 찾아서 업데이트
  const idx = recentReviews.value.findIndex(r => r.id === updatedReview.id)
  if (idx !== -1) {
    recentReviews.value[idx] = { ...recentReviews.value[idx], ...updatedReview }
  }
  
  // 모달에 떠있는 데이터도 업데이트 (이게 없으면 모달 닫기 전까지 옛날 내용 보임)
  if (selectedReview.value && selectedReview.value.id === updatedReview.id) {
    selectedReview.value = { ...selectedReview.value, ...updatedReview }
  }
}

// [댓글 작성]
async function handleReplySubmit(content) {
  if (!authStore.isLoggedIn) return alert('로그인 후 이용해주세요.')
  try {
    await createReviewComment(selectedReview.value.id, content)
    reviewComments.value = await fetchReviewComments(selectedReview.value.id)
  } catch (e) {
    alert('댓글 작성 실패')
  }
}

// [댓글 삭제]
function handleReplyDelete(commentId) {
  reviewComments.value = reviewComments.value.filter(c => c.id !== commentId)
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
/* 기존 스타일 유지 */
.page { max-width: 1100px; margin: 0 auto; padding: 20px 14px 60px; }
.hero { padding: 26px 0 18px; }
.hero-title { margin: 0; font-size: 44px; font-weight: 900; letter-spacing: -0.02em; }
.hero-sub { margin: 10px 0 0; color: #666; font-weight: 700; }
.divider { border: none; border-top: 1px solid #eee; margin: 18px 0 22px; }
.sec { margin-top: 18px; }
.sec-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px; }
.sec-title { margin: 0; font-size: 18px; font-weight: 900; }
.more { border: none; background: transparent; cursor: pointer; color: #666; font-weight: 900; }
.more:hover { text-decoration: underline; }
.muted { color: #777; margin: 10px 0 0; }

.review-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(3, 1fr); 
  gap: 20px;
}

@media (max-width: 900px) { .review-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .review-grid { grid-template-columns: 1fr; } }
</style>