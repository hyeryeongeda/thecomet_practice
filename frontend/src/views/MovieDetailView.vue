<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  fetchMovieDetail, 
  fetchMovieReviews, 
  fetchSimilarMovies, 
  fetchMovies, 
  toggleMovieLike, 
  fetchMyLikes, 
  createMovieReview,
  fetchReviewComments,
  createReviewComment,
  fetchMyActivity,
  toggleReviewLike,
  toggleMovieWish // [필수] 여기에 추가했습니다!
} from '@/api/comet'
import MovieRow from '@/components/movie/MovieRow.vue'

// 모달 컴포넌트
import ReviewWriteModal from '@/components/review/ReviewWriteModal.vue'
import ReviewListModal from '@/components/review/ReviewListModal.vue'
import ReviewDetailModal from '@/components/review/ReviewDetailModal.vue'

const route = useRoute()
const authStore = useAuthStore()
const tmdbId = computed(() => route.params.tmdbId)

const loading = ref(true)
const movie = ref(null)
const reviews = ref([])
const similarList = ref([])
const castRail = ref(null)

// 상태 변수
const isLiked = ref(false)
const isWished = ref(false)
const myReview = ref(null)

// 모달 상태
const showWriteModal = ref(false)
const showListModal = ref(false)
const showDetailModal = ref(false)

// 선택된 리뷰 및 댓글
const selectedReview = ref(null)
const reviewComments = ref([])

// Computed Helpers (기존 동일)
const posterSrc = computed(() => movie.value?.poster_path ? `https://image.tmdb.org/t/p/w500${movie.value.poster_path}` : '')
const backdropSrc = computed(() => movie.value?.backdrop_path ? `https://image.tmdb.org/t/p/original${movie.value.backdrop_path}` : '')
const releaseYear = computed(() => movie.value?.release_date?.slice(0, 4) || '')
const genreNames = computed(() => movie.value?.genres?.map(g => g.name).join('/') || '')
const country = computed(() => movie.value?.production_countries?.[0]?.name || '')
const voteScore = computed(() => movie.value?.vote_average ? Number(movie.value.vote_average).toFixed(1) : '0.0')
const starWidth = computed(() => `${(movie.value?.vote_average || 0) * 10}%`)
const allCast = computed(() => {
  if (!movie.value) return []
  const dirs = (movie.value.directors || []).map(p => ({ ...p, role_desc: '감독' }))
  const acts = (movie.value.cast || []).map(p => ({ ...p, role_desc: '출연' }))
  return [...dirs, ...acts]
})

// === 메인 로직 ===
async function loadAll() {
  loading.value = true
  isLiked.value = false
  isWished.value = false
  myReview.value = null

  try {
    const id = Number(tmdbId.value)
    const [m, r] = await Promise.all([fetchMovieDetail(id), fetchMovieReviews(id)])
    movie.value = m
    reviews.value = Array.isArray(r) ? r : (r.results || [])

    if (authStore.isLoggedIn) {
      try {
        const myLikes = await fetchMyLikes('movie')
        if (myLikes.find(item => item.tmdb_id === id)) isLiked.value = true
        
        const myActivity = await fetchMyActivity() 
        const found = myActivity.find(item => item.movie.tmdb_id === id)
        if (found) {
          myReview.value = found
          if (!found.watched) isWished.value = true 
        }
      } catch {}
    }

    try {
      const s = await fetchSimilarMovies(id)
      similarList.value = (s.length > 0) ? s : await fetchFallbackMovies(m.genres[0]?.id, m.id)
    } catch { similarList.value = [] }

  } catch (e) { console.error(e) } 
  finally { loading.value = false }
}

async function fetchFallbackMovies(genreId, currentId) {
  try {
    const res = await fetchMovies({ genre: genreId, page: 1 })
    return (res.results || []).filter(m => m.id !== currentId && m.tmdb_id !== currentId)
  } catch { return [] }
}

async function onToggleLike() {
  if (!authStore.isLoggedIn) return alert('로그인 필요')
  try {
    const res = await toggleMovieLike(Number(tmdbId.value))
    isLiked.value = res.liked
  } catch { alert('오류 발생') }
}

// [수정됨] 보고싶어요 토글 로직 (여기가 핵심!)
async function onToggleWish() {
  if (!authStore.isLoggedIn) return alert('로그인 필요')
  
  try {
    // createMovieReview 대신 toggleMovieWish 사용 (별점 0 허용)
    const res = await toggleMovieWish(Number(tmdbId.value))
    
    // 백엔드 응답에 따라 상태 변경 (res.wished: true/false)
    isWished.value = res.wished
    
    if (res.wished) {
      alert('보고싶은 영화에 추가되었습니다.')
    } else {
      // 취소된 경우 내 리뷰 정보 초기화
      myReview.value = null
      alert('보고싶은 영화에서 삭제되었습니다.')
    }
    // 데이터 갱신 (확실하게 하기 위해)
    loadAll()
    
  } catch (err) {
    // 이미 감상(watched=True)한 작품인 경우 에러 메시지 표시
    if (err.response && err.response.data.detail) {
      alert(err.response.data.detail)
    } else {
      console.error(err)
      alert('오류가 발생했습니다.')
    }
  }
}

// [모달] 작성 핸들러
function openWriteModal() {
  if (!authStore.isLoggedIn) return alert('로그인 필요')
  showWriteModal.value = true
}

async function handleWriteSubmit(payload) {
  // payload: { content: "내용", rating: 4 }
  try {
    await createMovieReview(Number(tmdbId.value), {
      content: payload.content,
      rating: payload.rating, // 별점 반영!
      watched: true
    })
    alert('코멘트가 등록되었습니다.')
    showWriteModal.value = false
    loadAll()
  } catch { alert('이미 작성한 리뷰가 있습니다.') }
}

// [모달] 목록 핸들러
function openListModal() { showListModal.value = true }
function handleSort(sortType) {
  if (sortType === 'likes') reviews.value.sort((a, b) => b.likes_count - a.likes_count)
  else if (sortType === 'latest') reviews.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
}

// [모달] 상세 핸들러
async function openDetailModal(review) {
  selectedReview.value = review
  try {
    reviewComments.value = await fetchReviewComments(review.id)
  } catch { reviewComments.value = [] }
  showDetailModal.value = true
}

// [기능 추가] 리뷰 좋아요
async function handleReviewLike(reviewId) {
  if (!authStore.isLoggedIn) return alert('로그인 필요')
  try {
    const res = await toggleReviewLike(reviewId)
    // 현재 보고 있는 상세 모달의 리뷰 업데이트
    if (selectedReview.value && selectedReview.value.id === reviewId) {
      selectedReview.value.is_liked = res.liked
      selectedReview.value.likes_count = res.like_count
    }
    // 목록에서도 업데이트
    const target = reviews.value.find(r => r.id === reviewId)
    if (target) {
      target.is_liked = res.liked
      target.likes_count = res.like_count
    }
  } catch { alert('좋아요 실패') }
}

// [기능 추가] 댓글 작성
async function handleReplySubmit(content) {
  if (!authStore.isLoggedIn) return alert('로그인 필요')
  try {
    await createReviewComment(selectedReview.value.id, content)
    // 댓글 목록 갱신
    reviewComments.value = await fetchReviewComments(selectedReview.value.id)
    // 댓글 수 갱신 (선택 사항)
    selectedReview.value.comments_count = (selectedReview.value.comments_count || 0) + 1
  } catch { alert('댓글 작성 실패') }
}

function scrollCast(dir) { if(castRail.value) castRail.value.scrollBy({ left: dir*300, behavior:'smooth' }) }

onMounted(loadAll)
watch(() => tmdbId.value, loadAll)
</script>

<template>
  <main class="page">
    <div v-if="loading" class="loading-screen">로딩중...</div>
    <div v-else-if="!movie" class="error-screen">영화를 불러오지 못했습니다.</div>

    <div v-else>
      <section class="hero-header">
        <div 
          class="backdrop-bg" 
          :style="{ backgroundImage: `url(${backdropSrc})` }"
        ></div>
        <div class="backdrop-overlay"></div>

        <div class="container hero-content">
          <div class="hero-text">
            <h1 class="title">{{ movie.title }}</h1>
            <p class="original-title">{{ movie.original_title }}</p>
            
            <div class="meta-info">
              <span>{{ releaseYear }}</span>
              <span class="dot">・</span>
              <span>{{ genreNames }}</span>
              <span class="dot">・</span>
              <span>{{ country }}</span>
            </div>

            <div class="bottom-stats">
              예매 순위 1위 (64%) ・ 누적 관객 {{ movie.vote_count?.toLocaleString() }}명
            </div>
          </div>
        </div>
      </section>

      <div class="container body-wrapper">
        <div class="top-section">
          
          <div class="poster-area">
            <div class="poster-card">
              <img v-if="posterSrc" :src="posterSrc" class="poster-img" alt="poster" />
              <div v-else class="poster-fallback">No Image</div>
            </div>
          </div>

          <div class="info-area">
            <div class="rating-row">
              <div class="rating-stars">
                <div class="star-bg">★★★★★★★★★★</div>
                <div class="star-fill" :style="{ width: starWidth }">★★★★★★★★★★</div>
              </div>
              <div class="rating-score">
                <span class="score-num">{{ voteScore }}</span>
                <span class="score-label">평균 별점 ({{ movie.vote_count }}명)</span>
              </div>
            </div>

            <div class="divider"></div>

            <div class="action-row">
              <button class="act-btn" :class="{ active: isLiked }" @click="onToggleLike">
                <div class="icon-box">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="svg-icon heart">
                    <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
                  </svg>
                </div>
                <span class="act-label">좋아요</span>
              </button>

              <button class="act-btn" @click="openWriteModal">
                <div class="icon-box">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="svg-icon"><path d="M21.731 2.269a2.625 2.625 0 00-3.712 0l-1.157 1.157 3.712 3.712 1.157-1.157a2.625 2.625 0 000-3.712zM19.513 8.199l-3.712-3.712-12.15 12.15a5.25 5.25 0 00-1.32 2.214l-.8 2.685a.75.75 0 00.933.933l2.685-.8a5.25 5.25 0 002.214-1.32L19.513 8.2z" /></svg>
                </div>
                <span class="act-label">코멘트</span>
              </button>

              <button class="act-btn" :class="{ active: isWished }" @click="onToggleWish">
                <div class="icon-box">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="svg-icon"><path d="M12 15a3 3 0 100-6 3 3 0 000 6z" /><path fill-rule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM17.25 12a5.25 5.25 0 11-10.5 0 5.25 5.25 0 0110.5 0z" clip-rule="evenodd" /></svg>
                </div>
                <span class="act-label">보고싶어요</span>
              </button>

              <button class="act-btn">
                <div class="icon-box">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="svg-icon"><path fill-rule="evenodd" d="M4.5 12a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0zm6 0a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0zm6 0a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0z" clip-rule="evenodd" /></svg>
                </div>
                <span class="act-label">더보기</span>
              </button>
            </div>

            <div class="divider"></div>

            <div class="event-banner">
              여기는 이벤트 관련 사진 등이 들어갈 예정입니다.
            </div>
            <p class="overview">{{ movie.overview || '등록된 줄거리가 없습니다.' }}</p>

          </div>
        </div>

        <div class="section-divider"></div>

        <section class="sub-section">
          <h3 class="sub-title">출연/제작</h3>
          
          <div class="scroll-wrapper">
            <button class="circle-arrow-btn left" @click="scrollCast(-1)">‹</button>
            <div ref="castRail" class="horizontal-scroll">
              <div v-for="p in allCast" :key="p.tmdb_id" class="cast-card">
                <div class="cast-img-box">
                  <img v-if="p.profile_path" :src="`https://image.tmdb.org/t/p/w200${p.profile_path}`" />
                  <div v-else class="no-img">👤</div>
                </div>
                <div class="cast-text">
                  <div class="c-name">{{ p.name }}</div>
                  <div class="c-role">{{ p.role_desc }}</div>
                </div>
              </div>
            </div>
            <button class="circle-arrow-btn right" @click="scrollCast(1)">›</button>
          </div>
        </section>

        <div class="section-divider"></div>

        <section class="sub-section">
          <div class="head-row">
            <h3 class="sub-title">코멘트 <span class="cnt">{{ reviews.length }}+</span></h3>
            <span class="more-link" @click="openListModal">더보기 ></span>
          </div>

          <div v-if="reviews.length === 0" class="no-data">아직 코멘트가 없습니다.</div>
          
          <div v-else class="comment-grid">
            <div 
              v-for="review in reviews.slice(0, 8)" 
              :key="review.id" 
              class="comment-card"
              @dblclick="openDetailModal(review)"
            >
              <div class="card-header">
                <div class="u-info">
                  <img v-if="review.user.profile_image" :src="review.user.profile_image" class="u-profile">
                  <div v-else class="u-icon">👤</div>
                  <span class="u-name">{{ review.user.username }}</span>
                </div>
                <div class="star-badge">★ {{ review.rating }}</div>
              </div>
              <div class="card-body">
                {{ review.content }}
              </div>
              <div class="card-footer">
                <span>👍 {{ review.likes_count }}</span>
                <span>💬 {{ review.comments_count || 0 }}</span>
              </div>
            </div>
          </div>
        </section>

        <div class="section-divider"></div>

        <section class="sub-section">
          <h3 class="sub-title">비슷한 작품</h3>
          <MovieRow v-if="similarList.length > 0" title="" :movies="similarList" />
          <div v-else class="no-data">관련 영화 정보를 불러오는 중입니다...</div>
        </section>

      </div>
    </div>

    <ReviewWriteModal 
      v-if="showWriteModal"
      :movieTitle="movie ? movie.title : ''"
      @close="showWriteModal = false"
      @submit="handleWriteSubmit"
    />

    <ReviewListModal
      v-if="showListModal"
      :reviews="reviews"
      @close="showListModal = false"
      @sort="handleSort"
      @select="openDetailModal"
    />

    <ReviewDetailModal
      v-if="showDetailModal && selectedReview"
      :review="selectedReview"
      :replies="reviewComments"
      @close="showDetailModal = false"
      @submit-reply="handleReplySubmit"
      @toggle-like="handleReviewLike"
    />

  </main>
</template>

<style scoped>
/* 기존 CSS 모두 유지 */
.page { background-color: #fff; padding-bottom: 100px; min-height: 100vh; }
.loading-screen, .error-screen { padding: 100px; text-align: center; color: #888; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }

.hero-header { position: relative; width: 100%; height: 400px; background: #000; margin-top: -60px; padding-top: 60px; display: flex; align-items: flex-end; overflow: hidden; }
.backdrop-bg { position: absolute; inset: 0; background-size: cover; background-position: center 20%; opacity: 0.6; z-index: 1; }
.backdrop-overlay { position: absolute; inset: 0; background: linear-gradient(to right, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.2) 100%); z-index: 2; }
.hero-content { position: relative; z-index: 3; width: 100%; padding-bottom: 30px; }
.hero-text { color: #fff; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
.title { font-size: 40px; font-weight: 900; margin: 0 0 6px; }
.original-title { font-size: 14px; opacity: 0.7; margin-bottom: 12px; }
.meta-info { font-size: 15px; opacity: 0.8; }
.dot { margin: 0 6px; opacity: 0.5; }
.bottom-stats { margin-top: 16px; font-size: 13px; opacity: 0.6; }

.body-wrapper { margin-top: 30px; }
.top-section { display: flex; gap: 30px; }
.poster-area { flex-shrink: 0; width: 240px; }
.poster-card { width: 100%; border-radius: 4px; overflow: hidden; border: 1px solid #e3e3e3; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.poster-img { width: 100%; display: block; }
.poster-fallback { height: 350px; background: #eee; display: flex; align-items: center; justify-content: center; color: #aaa; }
.info-area { flex-grow: 1; }

.rating-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0 20px; }
.rating-stars { position: relative; font-size: 32px; color: #eee; line-height: 1; letter-spacing: -2px; }
.star-bg { color: #e0e0e0; }
.star-fill { position: absolute; top: 0; left: 0; color: #ffad1f; overflow: hidden; white-space: nowrap; }
.rating-score { text-align: right; }
.score-num { font-size: 32px; font-weight: 700; color: #333; margin-right: 8px; }
.score-label { font-size: 13px; color: #888; }

.divider { height: 1px; background: #ededed; margin: 0; width: 100%; }

.action-row { display: flex; gap: 40px; padding: 20px 0; }
.act-btn { background: transparent; border: none; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 6px; color: #292a32; transition: all 0.2s; }
.act-btn:hover { color: #ff2f6e; transform: scale(1.05); }
.act-btn.active { color: #ff2f6e; }
.act-btn.active .svg-icon { fill: #ff2f6e; }

.icon-box { width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; }
.svg-icon { width: 24px; height: 24px; }
.act-label { font-size: 12px; color: #666; }

.event-banner { background: #f5f5f5; padding: 16px; border-radius: 6px; font-size: 13px; color: #666; margin: 20px 0; }
.overview { font-size: 15px; line-height: 1.6; color: #4a4a4a; white-space: pre-wrap; }
.section-divider { height: 1px; background: #e3e3e3; margin: 40px 0; }
.sub-title { font-size: 20px; font-weight: 800; color: #000; margin-bottom: 20px; }
.no-data { color: #999; font-size: 14px; padding: 20px 0; }

.scroll-wrapper { position: relative; }
.horizontal-scroll { display: flex; gap: 14px; overflow-x: auto; padding-bottom: 10px; -ms-overflow-style: none; scrollbar-width: none; }
.horizontal-scroll::-webkit-scrollbar { display: none; }
.cast-card { width: 110px; flex-shrink: 0; }
.cast-img-box { width: 110px; height: 110px; border-radius: 6px; overflow: hidden; background: #f8f8f8; border: 1px solid #eee; margin-bottom: 8px; }
.cast-img-box img { width: 100%; height: 100%; object-fit: cover; }
.no-img { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 30px; color: #ddd; }
.c-name { font-size: 13px; font-weight: 600; color: #333; margin-bottom: 2px; }
.c-role { font-size: 12px; color: #888; }
.circle-arrow-btn { position: absolute; top: 35px; width: 36px; height: 36px; border-radius: 50%; background: white; border: 1px solid #ddd; box-shadow: 0 2px 8px rgba(0,0,0,0.1); font-size: 22px; color: #666; cursor: pointer; display: flex; align-items: center; justify-content: center; padding-bottom: 3px; z-index: 10; }
.circle-arrow-btn:hover { border-color: #999; color: #000; }
.circle-arrow-btn.left { left: -15px; }
.circle-arrow-btn.right { right: -15px; }

.head-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.cnt { color: #ff2f6e; margin-left: 4px; }
.more-link { font-size: 14px; color: #ff2f6e; cursor: pointer; font-weight: 700; }
.comment-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.comment-card { background: #f2f2f2; border-radius: 8px; padding: 16px; height: 180px; display: flex; flex-direction: column; cursor: pointer; transition: background 0.2s; }
.comment-card:hover { background: #e8e8e8; }
.card-header { display: flex; justify-content: space-between; border-bottom: 1px solid #e0e0e0; padding-bottom: 8px; margin-bottom: 10px; }
.u-info { display: flex; align-items: center; gap: 6px; }
.u-profile { width: 24px; height: 24px; border-radius: 50%; object-fit: cover; }
.u-icon { font-size: 20px; }
.u-name { font-size: 13px; font-weight: 600; color: #333; }
.star-badge { font-size: 12px; background: #fff; padding: 2px 6px; border-radius: 4px; border: 1px solid #ddd; }
.card-body { font-size: 14px; color: #555; line-height: 1.5; flex-grow: 1; overflow: hidden; }
.card-footer { font-size: 12px; color: #888; display: flex; gap: 10px; margin-top: 10px; }

@media (max-width: 768px) {
  .top-section { flex-direction: column; }
  .poster-area { width: 160px; margin: 0 auto; margin-top: -100px; position: relative; z-index: 10; }
  .poster-card { box-shadow: 0 5px 15px rgba(0,0,0,0.3); border: 2px solid white; }
  .hero-header { justify-content: center; text-align: center; }
  .comment-grid { grid-template-columns: 1fr; }
}
</style>