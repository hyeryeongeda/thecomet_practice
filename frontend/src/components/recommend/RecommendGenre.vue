<template>
  <div class="wrap">
    <h2 class="h2">[장르 추천]</h2>

    <!-- 장르 탭(칩) -->
    <div class="chips" v-if="genres.length">
      <button
        v-for="g in genres"
        :key="g.tmdb_id"
        class="chip"
        :class="{ active: String(g.tmdb_id) === String(selectedGenreId) }"
        type="button"
        @click="selectGenre(g.tmdb_id)"
      >
        {{ g.name }}
      </button>

      <button class="chip arrow" type="button" @click="scrollChips('right')">›</button>
    </div>

    <div v-else class="chips-skeleton">
      <div class="chip sk" v-for="n in 5" :key="n"></div>
    </div>

    <!-- 영화 그리드 -->
    <div v-if="loadingMovies" class="loading">로딩중...</div>

    <div v-else-if="movies.length" class="grid">
      <button
        v-for="m in movies"
        :key="m.tmdb_id"
        class="card"
        type="button"
        @click="goMovie(m.tmdb_id)"
        :title="m.title"
      >
        <div class="poster">
          <img v-if="m.poster_path" :src="posterUrl(m.poster_path)" alt="" />
          <div v-else class="noimg">No Image</div>
        </div>

        <div class="meta">
          <p class="title">{{ m.title }}</p>
          <div class="stars">
            <span class="star" v-for="i in 5" :key="i" :class="{ on: i <= starCount(m.vote_average) }">★</span>
          </div>
        </div>
      </button>
    </div>

    <div v-else class="empty">해당 장르 추천 영화가 아직 없어요.</div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchGenreRecommends } from '@/api/comet'

const router = useRouter()

const genres = ref([])
const selectedGenreId = ref(null)

const movies = ref([])
const loadingGenres = ref(false)
const loadingMovies = ref(false)

function posterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w342${path}` : ''
}

// TMDB vote_average(0~10) -> 0~5 별로 변환
function starCount(voteAvg) {
  const v = Number(voteAvg || 0)
  return Math.max(0, Math.min(5, Math.round(v / 2)))
}

function goMovie(tmdbId) {
  router.push({ name: 'movie-detail', params: { tmdbId } })
}

async function loadGenres() {
  loadingGenres.value = true
  try {
    const res = await fetchGenreRecommends() // genre 없이 호출 => 장르 목록
    genres.value = Array.isArray(res?.genres) ? res.genres : []
    if (genres.value.length && !selectedGenreId.value) {
      selectedGenreId.value = genres.value[0].tmdb_id
    }
  } finally {
    loadingGenres.value = false
  }
}

async function loadMoviesByGenre(genreId) {
  if (!genreId) return
  loadingMovies.value = true
  try {
    const res = await fetchGenreRecommends({ genre: genreId }) // genre 파라미터 => 영화 리스트
    movies.value = Array.isArray(res?.results) ? res.results : []
  } finally {
    loadingMovies.value = false
  }
}

async function selectGenre(genreId) {
  selectedGenreId.value = genreId
  await loadMoviesByGenre(genreId)
}

// 칩이 많아질 때 대비(옵션)
function scrollChips() {
  // 지금은 간단 처리(필요하면 chips 컨테이너 ref로 스크롤 구현 가능)
}

onMounted(async () => {
  await loadGenres()
  await loadMoviesByGenre(selectedGenreId.value)
})
</script>

<style scoped>
.wrap {
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 16px;
  background: #fff;
}

.h2 {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 900;
}

/* chips */
.chips {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 14px;
  flex-wrap: nowrap;
  overflow-x: auto;
  padding-bottom: 4px;
}
.chips::-webkit-scrollbar { height: 6px; }
.chips::-webkit-scrollbar-thumb { background: #ddd; border-radius: 999px; }

.chip {
  height: 34px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid #e6e6e6;
  background: #f2f2f2;
  font-weight: 900;
  cursor: pointer;
  white-space: nowrap;
}
.chip.active {
  background: #111;
  border-color: #111;
  color: #fff;
}
.chip.arrow {
  margin-left: auto;
  width: 34px;
  padding: 0;
  border-radius: 10px;
}

/* skeleton */
.chips-skeleton {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}
.chip.sk {
  width: 80px;
  background: #f2f2f2;
  border-color: #f2f2f2;
}

/* grid */
.grid {
  margin-top: 14px;
  display: grid;
  gap: 14px;

  /* 핵심: 카드가 최소 160px ~ 최대 190px 안에서만 늘어남 */
  grid-template-columns: repeat(auto-fill, minmax(160px, 190px));
  justify-content: center; /* 남는 공간은 가운데로 */
  .wrap { max-width: 1000px; margin: 0 auto; }
}
@media (max-width: 900px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 560px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

.card {
  width: 100%;
  max-width: 190px;        /* grid max와 동일 */
  border: 0;
  padding: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.poster {
  width: 100%;
  aspect-ratio: 2 / 3;
  border-radius: 10px;
  overflow: hidden;
  background: #111;
  display: grid;
  place-items: center;
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.noimg { color: #fff; font-weight: 900; font-size: 12px; opacity: 0.8; }

.meta { padding-top: 8px; }
.title {
  margin: 0 0 6px;
  font-weight: 900;
  font-size: 13px;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stars { display: flex; gap: 2px; }
.star { font-size: 12px; color: #d9d9d9; }
.star.on { color: #f5c518; }

.loading, .empty {
  padding: 14px 0;
  font-weight: 800;
  color: #666;
}
</style>
