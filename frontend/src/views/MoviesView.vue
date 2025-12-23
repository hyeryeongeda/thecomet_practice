<template>
  <div class="page">
    <header class="head">
      <h1 class="title">영화</h1>
      <p class="sub">장르/정렬로 영화 탐색</p>
    </header>

    <!-- 필터 바 -->
    <section class="filters">
      <div class="filter-row">
        <div class="label">장르 선택</div>
        <div class="chips">
          <button
            class="chip"
            :class="{ active: !genre }"
            @click="setGenre(null)"
          >
            전체
          </button>

          <button
            v-for="g in genres"
            :key="g.tmdb_id ?? g.id"
            class="chip"
            :class="{ active: genre === String(g.tmdb_id ?? g.id) }"
            @click="setGenre(String(g.tmdb_id ?? g.id))"
          >
            {{ g.name }}
          </button>
        </div>
      </div>

      <div class="filter-row">
        <div class="label">정렬</div>
        <select class="select" v-model="sort" @change="applyQuery({ sort, page: 1 })">
          <option value="popular">인기순</option>
          <option value="latest">최신순</option>
          <option value="rating">평점순</option>
        </select>

        <div class="spacer"></div>

        <div class="searchbox" v-if="q">
          <span class="q">“{{ q }}”</span>
          <button class="clear" @click="applyQuery({ q: null, page: 1 })">검색 해제</button>
        </div>
      </div>
    </section>

    <!-- 결과 -->
    <section class="result">
      <div class="result-top">
        <div class="count">
          <strong>{{ total.toLocaleString() }}</strong>개 결과
        </div>
      </div>

      <p v-if="loading" class="muted">불러오는 중...</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <p v-else-if="movies.length === 0" class="muted">검색 결과가 없습니다.</p>

      <div v-else class="grid">
        <!-- 네 프로젝트에 MovieCard가 이미 있으니 그걸 활용 -->
        <MovieCard
          v-for="m in movies"
          :key="m.tmdb_id ?? m.id"
          :movie="m"
          @click="goDetail(m)"
        />
      </div>

      <!-- 페이지네이션 -->
      <div v-if="pages > 1" class="pager">
        <button class="pbtn" :disabled="page <= 1" @click="applyQuery({ page: page - 1 })">
          이전
        </button>

        <button
          v-for="p in pageButtons"
          :key="p"
          class="pnum"
          :class="{ active: p === page }"
          @click="applyQuery({ page: p })"
        >
          {{ p }}
        </button>

        <button class="pbtn" :disabled="page >= pages" @click="applyQuery({ page: page + 1 })">
          다음
        </button>

        <div class="goto">
          <span>Go to</span>
          <input class="goto-input" type="number" min="1" :max="pages" v-model.number="gotoPage" />
          <button class="pbtn" @click="goTo()">이동</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchMovies, fetchGenres } from '@/api/comet'
import MovieCard from '@/components/movie/MovieCard.vue'

const route = useRoute()
const router = useRouter()

// query state
const page = computed(() => Number(route.query.page || 1))
const sort = ref(route.query.sort || 'popular')
const genre = computed(() => (route.query.genre ? String(route.query.genre) : null))
const q = computed(() => (route.query.q ? String(route.query.q) : ''))

// data
const genres = ref([])
const movies = ref([])
const total = ref(0)
const pages = ref(1)
const loading = ref(false)
const error = ref('')

// pagination UI
const gotoPage = ref(1)
const pageButtons = computed(() => {
  // 현재 page 기준 앞뒤 2개씩만 보여주기 (너무 길면 UI 지저분해짐)
  const current = page.value
  const last = pages.value
  const start = Math.max(1, current - 2)
  const end = Math.min(last, current + 2)
  const arr = []
  for (let i = start; i <= end; i++) arr.push(i)
  return arr
})

function applyQuery(patch) {
  const next = { ...route.query, ...patch }

  // null/빈 값 제거
  Object.keys(next).forEach((k) => {
    if (next[k] === null || next[k] === undefined || next[k] === '') delete next[k]
  })

  router.push({ path: route.path, query: next })
}

function setGenre(v) {
  applyQuery({ genre: v, page: 1 })
}

function goTo() {
  const p = Number(gotoPage.value)
  if (!p || p < 1 || p > pages.value) return
  applyQuery({ page: p })
}

function goDetail(movie) {
  const tmdbId = movie?.tmdb_id ?? movie?.tmdbId ?? movie?.id
  if (!tmdbId) return
  router.push(`/movies/${tmdbId}`)
}

async function loadGenres() {
  try {
    genres.value = await fetchGenres()
  } catch (e) {
    // 장르 실패는 페이지 전체를 막지 않게
    genres.value = []
  }
}

async function loadMovies() {
  loading.value = true
  error.value = ''
  try {
    const params = {
      page: page.value,
      sort: sort.value,
    }
    if (genre.value) params.genre = genre.value
    if (q.value) params.q = q.value // 지금 백엔드는 q를 list에선 안 쓰지만, 나중 확장 대비로 넣어둠

    const data = await fetchMovies(params)

    // DRF PageNumberPagination 기본 형태: { count, next, previous, results }
    total.value = data.count ?? 0
    movies.value = data.results ?? []
    pages.value = Math.max(1, Math.ceil((total.value || 0) / 20))

    gotoPage.value = page.value
  } catch (e) {
    error.value = e?.response?.data?.detail || '영화 목록 불러오기 실패'
    total.value = 0
    movies.value = []
    pages.value = 1
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadGenres()
  await loadMovies()
})

watch(
  () => route.query,
  () => {
    // sort는 ref라 query 바뀌면 맞춰줌
    sort.value = route.query.sort || 'popular'
    loadMovies()
  }
)
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 18px 14px; }
.head { margin-bottom: 14px; }
.title { margin: 0; font-size: 22px; font-weight: 1000; }
.sub { margin: 6px 0 0; color: var(--muted); }

.filters{
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  margin-bottom: 14px;
}
.filter-row{ display:flex; align-items:center; gap: 12px; margin-bottom: 10px; }
.label{ width: 84px; font-weight: 900; font-size: 13px; color: #111; }
.chips{ display:flex; flex-wrap:wrap; gap: 8px; }
.chip{
  border: 1px solid var(--border);
  background: #fff;
  padding: 8px 10px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  font-weight: 800;
}
.chip.active{
  border-color: #111;
  box-shadow: 0 8px 18px rgba(0,0,0,0.06);
}
.select{
  padding: 9px 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--input-bg);
}
.spacer{ flex: 1; }
.searchbox{ display:flex; align-items:center; gap: 10px; }
.q{ font-weight: 900; }
.clear{
  border: 1px solid var(--border);
  background: #fff;
  border-radius: 10px;
  padding: 8px 10px;
  cursor: pointer;
  font-weight: 900;
}

.hint{ color: var(--muted); font-size: 12px; margin-top: 6px; }

.result-top{ display:flex; align-items:center; justify-content:space-between; margin: 10px 0; }
.count{ color:#111; }
.muted{ color: var(--muted); }
.error{ color:#ff4d4f; font-weight: 900; }

.grid{
  display:grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
}
@media (max-width: 1000px){ .grid{ grid-template-columns: repeat(4, 1fr); } }
@media (max-width: 820px){ .grid{ grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 560px){ .grid{ grid-template-columns: repeat(2, 1fr); } }

.pager{
  margin-top: 16px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap: 8px;
  flex-wrap: wrap;
}
.pbtn, .pnum{
  border: 1px solid var(--border);
  background: #fff;
  border-radius: 10px;
  padding: 8px 10px;
  cursor: pointer;
  font-weight: 900;
}
.pnum.active{
  border-color: #111;
}
.pbtn:disabled{
  opacity: 0.5;
  cursor: not-allowed;
}

.goto{ display:flex; align-items:center; gap: 8px; margin-left: 10px; color: var(--muted); }
.goto-input{
  width: 70px;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 10px;
}
</style>
