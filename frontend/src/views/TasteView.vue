<template>
  <div class="taste-page">
    <h1 class="page-title">나의 영화 DNA</h1>

    <section class="summary-section">
      <div class="info-card clickable" @click="openModal('all')">
        <p class="label">시청한 영화</p>
        <p class="value"><span>{{ stats.watchedCount }}</span>편</p>
        <p class="more-hint">전체 목록 보기 ></p> 
      </div>
      <div class="info-card clickable" @click="openModal('genre')">
        <p class="label">최애 장르</p>
        <p class="value">{{ stats.topGenre }}</p>
        <p class="more-hint">장르별 모아보기 ></p>
      </div>
      <div class="info-card clickable" @click="openModal('rating')">
        <p class="label">평균 별점</p>
        <p class="value">{{ stats.avgRating }}</p>
        <p class="more-hint">평점별 모아보기 ></p>
      </div>
    </section>

    <section class="chart-section">
      <div class="chart-wrapper">
        <Radar :data="chartData" :options="chartOptions" />
      </div>
    </section>

    <div class="section-divider"></div>

    <section class="recommend-section">
      <h2 class="recommend-title">
        최근 본 <b>[{{ stats.recentMovieTitle || '영화' }}]</b> 이 좋았다면
      </h2>

      <div v-if="recommendedMovies.length" class="movie-grid">
        <button
          v-for="movie in recommendedMovies"
          :key="movie.tmdb_id"
          class="movie-card"
          type="button"
          @click="goDetail(movie.tmdb_id)"
        >
          <div class="poster-box">
            <img v-if="movie.poster_path" :src="tmdbPoster(movie.poster_path)" alt="poster" />
          </div>
          <p class="movie-title">{{ movie.title }}</p>
        </button>
      </div>
      <p v-else class="empty">추천 영화 데이터를 불러오는 중입니다.</p>
    </section>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <header class="modal-header">
            <h2 class="modal-title">{{ modalTitle }}</h2>
            
            <div class="modal-filters">
              <select v-if="filterType === 'genre'" v-model="selectedGenre" class="filter-select">
                <option value="">모든 장르</option>
                <option v-for="g in GENRE_LABELS" :key="g" :value="g">{{ g }}</option>
              </select>

              <select v-if="filterType === 'rating'" v-model="selectedRating" class="filter-select">
                <option :value="0">모든 평점</option>
                <option v-for="n in [5, 4, 3, 2, 1]" :key="n" :value="n">{{ n }}점 준 영화</option>
              </select>
            </div>

            <button class="close-btn" @click="showModal = false">×</button>
          </header>
          
          <div class="modal-body">
            <div v-if="filteredMovies.length" class="movie-grid modal-grid">
              <button
                v-for="movie in filteredMovies"
                :key="movie.tmdb_id"
                class="movie-card"
                type="button"
                @click="goDetail(movie.tmdb_id)"
              >
                <div class="poster-box">
                  <img v-if="movie.poster_path" :src="tmdbPoster(movie.poster_path)" alt="poster" />
                  <div class="rating-badge" v-if="movie.my_rating">
                    ⭐ {{ movie.my_rating }}
                  </div>
                </div>
                <p class="movie-title">{{ movie.title }}</p>
              </button>
            </div>
            <p v-else class="empty-state">해당 조건에 맞는 영화가 없습니다.</p>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'
import { Radar } from 'vue-chartjs'
import { fetchTasteDNA, fetchMyActivity } from '@/api/comet'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const router = useRouter()

// 고정 설정값
const GENRE_LABELS = ['드라마','SF','판타지','로맨스','뮤지컬','애니메이션','전쟁','가족','다큐멘터리','스릴러','공포','액션']

// 상태 변수
const stats = ref({ watchedCount: 0, topGenre: '-', avgRating: 0, recentMovieTitle: '' })
const watchedMovies = ref([]) 
const recommendedMovies = ref([])
const radarScores = ref({})

// 모달 및 필터 상태
const showModal = ref(false)
const filterType = ref('all') 
const selectedGenre = ref('')
const selectedRating = ref(0)

const modalTitle = computed(() => {
  if (filterType.value === 'genre') return '장르별 시청 기록'
  if (filterType.value === 'rating') return '평점별 시청 기록'
  return '내가 본 영화 전체 목록'
})

// 필터링 로직
const filteredMovies = computed(() => {
  let list = [...watchedMovies.value]
  
  if (filterType.value === 'genre' && selectedGenre.value) {
    list = list.filter(m => m.genres?.includes(selectedGenre.value))
  } else if (filterType.value === 'rating' && selectedRating.value > 0) {
    list = list.filter(m => Math.floor(m.my_rating) === Number(selectedRating.value))
  }
  
  return list
})

function openModal(type) {
  filterType.value = type
  if (type === 'genre') {
    selectedGenre.value = stats.value.topGenre.split('/')[0]
  } else if (type === 'rating') {
    selectedRating.value = Math.round(stats.value.avgRating)
  }
  showModal.value = true
}

// 데이터 변환 함수
function normalizeActivityList(list) {
  if (!list) return []
  return list.map(item => ({
    tmdb_id: item.movie.id || item.movie.tmdb_id, 
    title: item.movie.title,
    poster_path: item.movie.poster_path,
    genres: item.movie.genres || [],
    my_rating: item.rating || item.movie.my_rating || 0 
  }))
}

function normalizeTastePayload(payload) {
  const data = payload || {}
  return {
    watchedCount: data.watched_count ?? 0, // 덮어씌워질 예정
    topGenre: data.top_genre ?? '-',
    avgRating: data.avg_rating ?? 0,      // 덮어씌워질 예정
    recentMovieTitle: data.recent_movie_title ?? '',
    radar: data.genre_scores ?? {},
    recMovies: data.recommended_movies ?? [],
  }
}

function normalizeMovies(list) {
  return list.map(m => ({
    tmdb_id: m.tmdb_id || m.id,
    title: m.title || '제목 없음',
    poster_path: m.poster_path,
    genres: m.genres || [],
    my_rating: m.my_rating || 0
  }))
}

// 차트 설정
const chartData = computed(() => ({
  labels: GENRE_LABELS,
  datasets: [{
    label: '선호도',
    data: GENRE_LABELS.map(l => radarScores.value[l] || 0),
    backgroundColor: 'rgba(140, 140, 255, 0.3)',
    borderColor: 'rgba(140, 140, 255, 1)',
    borderWidth: 2,
    pointBackgroundColor: 'rgba(140, 140, 255, 1)',
  }]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      suggestedMin: 0,
      suggestedMax: 100,
      ticks: { display: false },
      pointLabels: { font: { size: 12, weight: '600' } }
    }
  }
}

function tmdbPoster(path) { return path ? `https://image.tmdb.org/t/p/w342${path}` : '' }

function goDetail(tmdbId) {
  showModal.value = false
  router.push({ name: 'movie-detail', params: { tmdbId } })
}

// ✅ [수정] loadTaste 함수: 개수 및 평균 별점 직접 계산 로직 추가
async function loadTaste() {
  try {
    const [tastePayload, activityList] = await Promise.all([
      fetchTasteDNA(),
      fetchMyActivity({ status: 'commented', sort: 'latest' })
    ])
    
    // 1. API 통계 데이터 우선 적용 (장르, 차트 등)
    const normalized = normalizeTastePayload(tastePayload)
    stats.value = { ...normalized }
    radarScores.value = normalized.radar
    recommendedMovies.value = normalizeMovies(normalized.recMovies)

    // 2. 실제 리스트 데이터 적용
    watchedMovies.value = normalizeActivityList(activityList)
    
    // 🔥 [핵심 수정 1] 개수 동기화
    const realCount = watchedMovies.value.length
    stats.value.watchedCount = realCount

    // 🔥 [핵심 수정 2] 평균 별점 직접 계산 (0점인 보고싶은 영화 제외 효과)
    if (realCount > 0) {
      // 리스트에 있는 모든 평점을 더함
      const sum = watchedMovies.value.reduce((acc, cur) => acc + cur.my_rating, 0)
      // 평균 계산 후 소수점 한 자리까지 표현
      stats.value.avgRating = (sum / realCount).toFixed(1)
    } else {
      stats.value.avgRating = 0
    }

  } catch (err) {
    console.error("Taste DNA 및 목록 로드 실패:", err)
  }
}

onMounted(loadTaste)
</script>


<style scoped>
/* 🎨 레이아웃 구조는 유지하고 색상만 테마 변수로 교체 */

.taste-page { 
  max-width: 1000px; 
  margin: 0 auto; 
  padding: 40px 20px; 
  background: var(--bg); /* 배경색 대응 */
  color: var(--text);    /* 글자색 대응 */
}
.page-title { font-size: 26px; font-weight: 900; margin-bottom: 35px; color: var(--text); }

/* 요약 카드 디자인 */
.summary-section { display: flex; gap: 20px; margin-bottom: 50px; }
.info-card { 
  flex: 1; 
  background: var(--card); /* #fff -> var(--card) */
  border-radius: 20px; 
  padding: 28px; 
  text-align: center; 
  border: 1px solid var(--border); /* #f0f0f0 -> var(--border) */
  box-shadow: var(--shadow); 
}
.info-card.clickable { cursor: pointer; transition: all 0.25s ease; }
.info-card.clickable:hover { 
  transform: translateY(-7px); 
  border-color: var(--primary); /* #a0a0ff -> var(--primary) */
}
.info-card .label { font-size: 14px; font-weight: 700; color: var(--muted); margin-bottom: 12px; } /* #777 -> var(--muted) */
.info-card .value { font-size: 30px; font-weight: 900; color: var(--text); } /* #111 -> var(--text) */
.more-hint { font-size: 11px; color: var(--muted); margin-top: 8px; font-weight: bold; } /* #bbb -> var(--muted) */

.chart-section { display: flex; justify-content: center; margin-bottom: 60px; }
.chart-wrapper { width: 100%; max-width: 450px; height: 400px; }

/* 추천 섹션 */
.recommend-title { font-size: 22px; font-weight: 800; margin-bottom: 25px; color: var(--text); }
.section-divider { height: 1px; background: var(--border); margin: 45px 0; } /* #f0f0f0 -> var(--border) */

/* 그리드 레이아웃 */
.movie-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.movie-card { text-align: center; cursor: pointer; background: transparent; border: 0; padding: 0; }
.poster-box { 
  width: 100%; 
  aspect-ratio: 2 / 3; 
  background: var(--bg); /* #222 -> var(--bg) 포스터 로딩 전 배경 */
  border-radius: 12px; 
  position: relative; 
  overflow: hidden; 
  margin-bottom: 12px; 
  box-shadow: 0 5px 15px rgba(0,0,0,0.15); 
}
.poster-box img { width: 100%; height: 100%; object-fit: cover; }
.movie-title { 
  font-size: 14px; 
  font-weight: 700; 
  color: var(--text); /* #333 -> var(--text) */
  overflow: hidden; 
  text-overflow: ellipsis; 
  white-space: nowrap; 
}

/* 모달 디자인 */
.modal-overlay { 
  position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
  background: rgba(0,0,0,0.75); 
  display: flex; align-items: center; justify-content: center; 
  z-index: 2000; padding: 20px; 
}
.modal-content { 
  background: var(--card); /* #fff -> var(--card) */
  width: 100%; max-width: 850px; max-height: 85vh; 
  border-radius: 24px; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden; 
  animation: fadeIn 0.3s ease; 
  color: var(--text);
}
.modal-header { 
  padding: 24px 30px; 
  border-bottom: 1px solid var(--border); /* #f0f0f0 -> var(--border) */
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
}
.modal-title { font-size: 22px; font-weight: 900; margin: 0; color: var(--text); }
.modal-filters { margin: 0 25px; display: flex; gap: 10px; }
.filter-select { 
  padding: 8px 16px; 
  border-radius: 10px; 
  border: 1px solid var(--border); /* #eee -> var(--border) */
  background: var(--input-bg);
  color: var(--text);
  font-weight: 700; 
  font-size: 14px; 
  cursor: pointer; 
  outline: none; 
  transition: border-color 0.2s; 
}
.filter-select:focus { border-color: var(--primary); } /* #a0a0ff -> var(--primary) */
.close-btn { background: none; border: none; font-size: 32px; cursor: pointer; color: var(--muted); line-height: 1; } /* #bbb -> var(--muted) */

.modal-body { flex: 1; overflow-y: auto; padding: 30px; }
.modal-grid { grid-template-columns: repeat(4, 1fr); gap: 20px; }

/* 평점 배지는 가독성을 위해 기존 스타일(어두운 배경에 흰색 글자) 유지 혹은 보정 */
.rating-badge { 
  position: absolute; 
  bottom: 10px; 
  right: 10px; 
  background: rgba(0,0,0,0.8); 
  color: #fff; 
  padding: 4px 8px; 
  border-radius: 6px; 
  font-size: 11px; 
  font-weight: 800; 
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .summary-section { flex-direction: column; }
  .movie-grid, .modal-grid { grid-template-columns: repeat(2, 1fr); }
  .modal-header { flex-direction: column; gap: 15px; text-align: center; }
}
</style>