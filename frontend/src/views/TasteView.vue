<template>
  <div class="taste-page">
    <h1 class="page-title">나의 영화 DNA</h1>

    <section class="summary-section">
      <div class="info-card">
        <p class="label">시청한 영화</p>
        <p class="value"><span>{{ stats.watchedCount }}</span>편</p>
      </div>
      <div class="info-card">
        <p class="label">최애 장르</p>
        <p class="value">{{ stats.topGenre }}</p>
      </div>
      <div class="info-card">
        <p class="label">평균 별점</p>
        <p class="value">{{ stats.avgRating }}</p>
      </div>
    </section>

    <section class="chart-section">
      <div class="chart-wrapper">
        <Radar :data="chartData" :options="chartOptions" />
      </div>
    </section>

    <section class="recommend-section">
      <h2 class="recommend-title">
        최근 본 <b>[{{ stats.recentMovieTitle || '영화' }}]</b> 이 좋았다면
      </h2>

      <div v-if="recommendedMovies.length" class="movie-grid">
        <button
          v-for="movie in recommendedMovies"
          :key="movie.tmdb_id ?? movie.id"
          class="movie-card"
          type="button"
          @click="goDetail(movie.tmdb_id ?? movie.id)"
        >
          <div class="poster-box">
            <img
              v-if="movie.poster_path"
              :src="tmdbPoster(movie.poster_path)"
              alt="poster"
            />
            <span v-else class="ratio-text">2:3</span>
          </div>
          <p class="movie-title">{{ movie.title }}</p>
        </button>
      </div>

      <p v-else class="empty">추천 영화가 아직 없어요.</p>
    </section>
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
import { fetchTasteDNA } from '@/api/comet'

// Chart.js 필수 플러그인 등록
ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const router = useRouter()

/** ✅ 화면 고정 라벨(시안 기준) */
const GENRE_LABELS = [
  '드라마','SF','판타지','로맨스','뮤지컬','애니메이션','전쟁','가족','다큐멘터리','스릴러','공포','액션'
]

/** ✅ stats: 화면에서 쓰는 형태로 통일 */
const stats = ref({
  watchedCount: 0,
  topGenre: '-',
  avgRating: 0,
  recentMovieTitle: ''
})

/** ✅ 추천 영화(최근 본 영화 기반) */
const recommendedMovies = ref([])

/** ✅ 백 payload → 프론트 형태로 정규화 */
function normalizeTastePayload(payload) {
  // stats 부분
  const watchedCount =
    payload?.watchedCount ??
    payload?.watched_count ??
    payload?.stats?.watched_count ??
    payload?.stats?.watchedCount ??
    0

  // top genre는 문자열/배열 둘 다 대응
  const topGenreRaw =
    payload?.topGenre ??
    payload?.top_genre ??
    payload?.stats?.top_genre ??
    payload?.stats?.topGenre ??
    '-'

  const topGenre = Array.isArray(topGenreRaw) ? topGenreRaw.join('/') : (topGenreRaw || '-')

  // avg rating: 백에서 10점 만점으로 줄 수도 있어서 보정
  let avgRating =
    payload?.avgRating ??
    payload?.avg_rating ??
    payload?.stats?.avg_rating ??
    payload?.stats?.avgRating ??
    0

  avgRating = Number(avgRating || 0)
  if (avgRating > 5) avgRating = avgRating / 2
  avgRating = Number(avgRating.toFixed(1))

  const recentMovieTitle =
    payload?.recentMovieTitle ??
    payload?.recent_movie_title ??
    payload?.stats?.recent_movie_title ??
    payload?.recent_movie?.title ??
    payload?.recentMovie?.title ??
    ''

  // radar score (장르별 선호도)
  const radar =
    payload?.radar ??
    payload?.genre_scores ??
    payload?.genreScores ??
    payload?.stats?.radar ??
    payload?.stats?.genre_scores ??
    payload?.stats?.genreScores ??
    {}

  // 추천 영화 리스트
  const movies =
    payload?.recommendedMovies ??
    payload?.recommended_movies ??
    payload?.recommended ??
    payload?.movies ??
    payload?.results ??
    []

  return { watchedCount, topGenre, avgRating, recentMovieTitle, radar, movies }
}

/** ✅ 영화 데이터도 키 통일(tmdb_id / poster_path) */
function normalizeMovies(list) {
  if (!Array.isArray(list)) return []
  return list.map((m) => ({
    tmdb_id: m.tmdb_id ?? m.tmdbId ?? m.id,
    title: m.title ?? m.name ?? '',
    poster_path: m.poster_path ?? m.posterPath ?? null,
  })).filter(m => m.tmdb_id && m.title)
}

/** ✅ Radar 차트 데이터: 백 radar가 있으면 반영, 없으면 0 */
const radarScores = ref({}) // { '드라마': 80, 'SF': 50, ... } 또는 키가 장르명이 아닌 경우도 대비는 백에서 맞춰주는게 베스트

const chartData = computed(() => {
  const dataArr = GENRE_LABELS.map((label) => {
    const v = radarScores.value?.[label]
    return Number.isFinite(Number(v)) ? Number(v) : 0
  })

  return {
    labels: GENRE_LABELS,
    datasets: [
      {
        label: '선호도',
        data: dataArr,
        backgroundColor: 'rgba(160, 160, 255, 0.35)',
        borderColor: 'rgba(140, 140, 255, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(140, 140, 255, 1)',
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      angleLines: { display: true, color: '#eee' },
      grid: { color: '#eee' },
      pointLabels: { font: { size: 12, weight: '600' }, color: '#666' },
      ticks: { display: false },
      suggestedMin: 0,
      suggestedMax: 100
    }
  },
  plugins: { legend: { display: false } }
}

function tmdbPoster(path) {
  return path ? `https://image.tmdb.org/t/p/w342${path}` : ''
}

function goDetail(tmdbId) {
  if (!tmdbId) return
  router.push({ name: 'movie-detail', params: { tmdbId } })
}

/** ✅ 실제 데이터 로드 */
async function loadTaste() {
  const payload = await fetchTasteDNA()
  console.log("백엔드에서 온 원본 데이터:", payload) // <--- 이 줄을 추가해서 F12 콘솔을 보세요.
  
  const normalized = normalizeTastePayload(payload)

  stats.value.watchedCount = normalized.watchedCount
  stats.value.topGenre = normalized.topGenre
  stats.value.avgRating = normalized.avgRating
  stats.value.recentMovieTitle = normalized.recentMovieTitle

  radarScores.value = normalized.radar || {}
  recommendedMovies.value = normalizeMovies(normalized.movies)
}

onMounted(loadTaste)
</script>

<style scoped>
.taste-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
  font-family: sans-serif;
}

.page-title {
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 30px;
}

.summary-section {
  display: flex;
  gap: 20px;
  margin-bottom: 50px;
}

.info-card {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  border: 1px solid #f0f0f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.info-card .label {
  font-size: 14px;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.info-card .value {
  font-size: 28px;
  font-weight: 800;
  color: #000;
}

.chart-section {
  display: flex;
  justify-content: center;
  margin-bottom: 60px;
}

.chart-wrapper {
  width: 100%;
  max-width: 450px;
  height: 400px;
}

.recommend-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 25px;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.movie-card {
  text-align: center;
  cursor: pointer;
  background: transparent;
  border: 0;
  padding: 0;
}

.poster-box {
  width: 100%;
  aspect-ratio: 2 / 3;
  background: #111;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

.poster-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ratio-text {
  color: rgba(255,255,255,0.3);
  font-weight: bold;
}

.movie-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.empty {
  margin-top: 12px;
  color: #777;
  font-weight: 700;
}

@media (max-width: 768px) {
  .summary-section { flex-direction: column; }
  .movie-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
