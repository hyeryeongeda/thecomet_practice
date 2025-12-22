<template>
  <main class="page">
    <div v-if="loading" class="loading-screen">로딩중...</div>

    <div v-else-if="!movie" class="error-screen">
      영화를 불러오지 못했습니다.
    </div>

    <div v-else>
      <section class="hero-header">
        <div 
          class="backdrop-bg" 
          :style="{ backgroundImage: `url(${backdropSrc || posterSrc})` }"
        ></div>
        
        <div class="backdrop-overlay"></div>

        <div class="container hero-content">
          <div class="main-info">
            <div class="poster-wrap">
              <img v-if="posterSrc" :src="posterSrc" class="poster-img" alt="poster" />
              <div v-else class="poster-fallback">No Image</div>
            </div>

            <div class="info-text">
              <h1 class="title">{{ movie.title }}</h1>
              
              <div class="meta">
                <span class="year">{{ releaseYear }}</span>
                <span class="dot">・</span>
                <span class="genre" v-for="g in movie.genres" :key="g.id">{{ g.name }} </span>
                <span class="dot">・</span>
                <span class="country">{{ country }}</span>
              </div>

              <div class="rating">
                <span class="star">★</span>
                <span class="score">{{ Number(movie.vote_average).toFixed(1) }}</span>
                <span class="count">({{ movie.vote_count?.toLocaleString() }}명)</span>
              </div>

              <div class="action-buttons">
                <button class="act-btn" @click="onToggleLike">
                  <span class="icon">♥</span>
                  <span class="label">좋아요</span>
                </button>
                
                <button class="act-btn" @click="openCommentModal">
                  <span class="icon">✏️</span>
                  <span class="label">코멘트</span>
                </button>
                
                <button class="act-btn" @click="onToggleWish">
                  <span class="icon">＋</span>
                  <span class="label">보고싶어요</span>
                </button>
                
                <button class="act-btn">
                  <span class="icon">⋯</span>
                  <span class="label">더보기</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div class="movie-body container">
        
        <section class="section-block">
          <h3 class="section-title">기본 정보</h3>
          <p class="overview">{{ movie.overview || '줄거리가 없습니다.' }}</p>
        </section>

        <div class="divider"></div>

        <section class="section-block" v-if="hasCast">
          <h3 class="section-title">출연/제작</h3>
          
          <div class="scroll-container">
            <button class="scroll-btn left" @click="scrollCast(-1)">‹</button>
            <button class="scroll-btn right" @click="scrollCast(1)">›</button>
            
            <div ref="castRail" class="horizontal-rail">
              <div v-for="p in movie.directors" :key="'dir-'+p.tmdb_id" class="cast-card">
                <div class="cast-photo">
                  <img v-if="p.profile_path" :src="`https://image.tmdb.org/t/p/w200${p.profile_path}`">
                  <div v-else class="no-photo">👤</div>
                </div>
                <div class="cast-info">
                  <div class="cast-name">{{ p.name }}</div>
                  <div class="cast-role">감독</div>
                </div>
              </div>
              
              <div v-for="p in movie.cast" :key="'act-'+p.tmdb_id" class="cast-card">
                <div class="cast-photo">
                  <img v-if="p.profile_path" :src="`https://image.tmdb.org/t/p/w200${p.profile_path}`">
                  <div v-else class="no-photo">👤</div>
                </div>
                <div class="cast-info">
                  <div class="cast-name">{{ p.name }}</div>
                  <div class="cast-role">출연</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div class="divider"></div>

        <section class="section-block">
          <div class="head-row">
            <h3 class="section-title">코멘트 <span class="cnt">{{ reviews.length }}</span></h3>
            <span class="more-link" v-if="reviews.length > 0">더보기 ></span>
          </div>

          <div v-if="reviews.length === 0" class="empty-review">
            아직 코멘트가 없습니다. 첫 번째 코멘트를 남겨보세요!
          </div>

          <div v-else class="comment-slider">
            <div v-for="review in reviews" :key="review.id" class="comment-card">
              <div class="comment-header">
                <div class="user-profile">
                  <img v-if="review.user.profile_image" :src="review.user.profile_image" class="u-img">
                  <div v-else class="u-icon">👤</div>
                  <span class="u-name">{{ review.user.username }}</span>
                </div>
                <div class="c-rating">★ {{ review.rating }}</div>
              </div>
              <div class="comment-body">
                {{ review.content }}
              </div>
              <div class="comment-footer">
                <span class="likes">👍 {{ review.likes_count }}</span>
                <span class="likes">💬 0</span>
              </div>
            </div>
          </div>
        </section>

        <div class="divider"></div>

        <section class="section-block" v-if="similarList.length > 0">
           <h3 class="section-title">비슷한 작품</h3>
           <MovieRow title="" :movies="similarList" />
        </section>

      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  fetchMovieDetail,
  fetchMovieReviews,
  fetchSimilarMovies
} from '@/api/comet'

import MovieRow from '@/components/movie/MovieRow.vue'

const route = useRoute()
const tmdbId = computed(() => route.params.tmdbId)

const loading = ref(true)
const movie = ref(null)
const reviews = ref([])
const similarList = ref([])
const castRail = ref(null)

const posterSrc = computed(() => movie.value?.poster_path ? `https://image.tmdb.org/t/p/w500${movie.value.poster_path}` : '')
const backdropSrc = computed(() => movie.value?.backdrop_path ? `https://image.tmdb.org/t/p/original${movie.value.backdrop_path}` : '')

const releaseYear = computed(() => movie.value?.release_date?.slice(0, 4) || '')
const country = computed(() => movie.value?.production_countries?.[0]?.name || '')
const hasCast = computed(() => (movie.value?.directors?.length || 0) + (movie.value?.cast?.length || 0) > 0)

async function loadAll() {
  loading.value = true
  try {
    const [m, r, s] = await Promise.all([
      fetchMovieDetail(Number(tmdbId.value)),
      fetchMovieReviews(Number(tmdbId.value)),
      fetchSimilarMovies(Number(tmdbId.value))
    ])
    movie.value = m
    reviews.value = Array.isArray(r) ? r : (r?.results ?? [])
    similarList.value = Array.isArray(s) ? s : (s?.results ?? [])
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function scrollCast(direction) {
  if (castRail.value) {
    castRail.value.scrollBy({ left: direction * 300, behavior: 'smooth' })
  }
}

function onToggleLike() { alert('좋아요 기능 연결 필요') }
function openCommentModal() { alert('코멘트 작성 모달 연결 필요') }
function onToggleWish() { alert('보고싶어요 기능 연결 필요') }

onMounted(loadAll)
watch(() => tmdbId.value, loadAll)
</script>

<style scoped>
.page { background-color: #fff; min-height: 100vh; padding-bottom: 80px; }
.loading-screen, .error-screen { padding: 100px; text-align: center; color: #888; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }

/* [섹션 1] 히어로 헤더 (16:9 ~ 16:5 사이의 넓은 비율) */
.hero-header {
  position: relative;
  width: 100%;
  /* Navbar 높이(약 60px)만큼 위로 끌어올려서 Navbar 뒤에 이미지가 깔리게 함.
    Navbar가 투명 배경이어야 효과가 보입니다. 
  */
  margin-top: -60px; 
  padding-top: 60px; /* 끌어올린 만큼 내부 패딩을 줘서 컨텐츠가 잘리지 않게 함 */
  
  height: 550px; /* 헤더 높이 넉넉하게 */
  display: flex;
  align-items: flex-end; /* 컨텐츠 하단 정렬 */
  color: white;
  overflow: hidden;
}

/* 배경 이미지 */
.backdrop-bg {
  position: absolute; inset: 0;
  background-size: cover;
  background-position: center top;
  z-index: 0;
}
/* 어두운 오버레이 (글자 가독성) */
.backdrop-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.8) 100%);
  z-index: 1;
}

/* 헤더 내용 (포스터 + 텍스트) */
.hero-content {
  position: relative; z-index: 2;
  width: 100%;
  padding-bottom: 40px; /* 하단 여백 */
}

.main-info {
  display: flex;
  align-items: flex-end; /* 포스터 하단과 텍스트 하단 맞춤 */
  gap: 30px;
}

/* 포스터 (흰색 테두리 효과) */
.poster-wrap {
  width: 160px;
  flex-shrink: 0;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.3);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  overflow: hidden;
}
.poster-img { width: 100%; display: block; }
.poster-fallback { width: 100%; height: 240px; background: #333; color: #fff; display: flex; align-items: center; justify-content: center; }

/* 텍스트 정보 (흰색) */
.info-text { flex-grow: 1; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }

.title { font-size: 40px; font-weight: 800; margin: 0 0 12px; line-height: 1.2; }
.meta { font-size: 15px; color: rgba(255,255,255,0.8); margin-bottom: 12px; }
.dot { margin: 0 6px; opacity: 0.5; }

.rating { display: flex; align-items: center; margin-bottom: 24px; font-size: 16px; }
.star { color: #ff2f6e; font-size: 22px; margin-right: 6px; }
.score { font-size: 22px; font-weight: 700; margin-right: 8px; }
.count { font-size: 13px; opacity: 0.7; }

/* 액션 버튼들 (투명 배경 + 흰색 아이콘/글자) */
.action-buttons { display: flex; gap: 40px; }
.act-btn {
  background: transparent; border: none; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  color: white; padding: 0; min-width: 60px;
  transition: transform 0.2s;
}
.act-btn:hover { transform: scale(1.1); }
.act-btn .icon { font-size: 24px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
.act-btn .label { font-size: 12px; font-weight: 500; opacity: 0.9; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }

/* 바디 컨텐츠 */
.divider { height: 1px; background: #f0f0f0; margin: 0; width: 100%; }
.section-block { padding: 40px 0; }
.section-title { font-size: 20px; font-weight: 800; color: #000; margin-bottom: 20px; }
.overview { font-size: 16px; line-height: 1.7; color: #4a4a4a; white-space: pre-wrap; }

/* 가로 스크롤 & 버튼 */
.scroll-container { position: relative; }
.horizontal-rail {
  display: flex; gap: 14px; overflow-x: auto; scroll-behavior: smooth; padding-bottom: 10px;
  -ms-overflow-style: none; scrollbar-width: none;
}
.horizontal-rail::-webkit-scrollbar { display: none; }

.scroll-btn {
  position: absolute; top: 50%; transform: translateY(-50%);
  width: 40px; height: 40px; border-radius: 50%;
  background: white; border: 1px solid #e3e3e3;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-size: 20px; line-height: 1; color: #666; cursor: pointer; z-index: 10;
  display: flex; align-items: center; justify-content: center;
}
.scroll-btn:hover { color: #000; border-color: #ccc; }
.scroll-btn.left { left: -20px; }
.scroll-btn.right { right: -20px; }

/* 출연진 카드 */
.cast-card { width: 110px; flex-shrink: 0; }
.cast-photo { width: 100%; height: 110px; border-radius: 6px; overflow: hidden; margin-bottom: 8px; border: 1px solid #eee; }
.cast-photo img { width: 100%; height: 100%; object-fit: cover; }
.no-photo { width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 30px; }
.cast-info { padding: 0 2px; }
.cast-name { font-size: 14px; font-weight: 500; color: #000; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cast-role { font-size: 12px; color: #888; }

/* 코멘트 카드 */
.head-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.cnt { color: #ff2f6e; margin-left: 4px; }
.more-link { color: #ff2f6e; font-size: 14px; font-weight: 700; cursor: pointer; }

.comment-slider { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 10px; }
.comment-card {
  width: 260px; flex-shrink: 0;
  background: #fdfdfd; border: 1px solid #eee; border-radius: 8px;
  padding: 16px; display: flex; flex-direction: column;
}
.comment-header { display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #f5f5f5; padding-bottom: 8px; }
.user-profile { display: flex; align-items: center; gap: 6px; }
.u-img { width: 24px; height: 24px; border-radius: 50%; object-fit: cover; }
.u-icon { font-size: 20px; }
.u-name { font-size: 13px; font-weight: 600; color: #333; }
.c-rating { font-size: 12px; background: #eee; padding: 2px 6px; border-radius: 4px; font-weight: 700; }
.comment-body { font-size: 14px; color: #555; line-height: 1.5; margin-bottom: 12px; flex-grow: 1; height: 64px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }
.comment-footer { font-size: 12px; color: #999; display: flex; gap: 10px; }
.empty-review { padding: 30px; text-align: center; color: #999; background: #fafafa; border-radius: 8px; }
</style>