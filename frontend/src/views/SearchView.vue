<template>
  <div class="page">
    <h1>검색</h1>

    <div class="bar">
      <input class="input" v-model.trim="q" placeholder="영화/인물 검색" @keydown.enter="run" />
      <button class="btn primary" @click="run">검색</button>
    </div>

    <div class="tabs">
      <button class="tab" :class="{ active: type === 'movie' }" @click="setType('movie')">영화</button>
      <button class="tab" :class="{ active: type === 'person' }" @click="setType('person')">인물</button>
    </div>

    <p v-if="loading" class="muted">불러오는 중...</p>

    <div v-else>
      <!-- 영화 결과 -->
      <div v-if="type === 'movie'" class="grid">
        <div v-for="m in results" :key="m.tmdb_id" class="movie" @click="goDetail(m.tmdb_id)">
          <div class="poster">
            <img v-if="m.poster_path" :src="img(m.poster_path)" />
            <div v-else class="empty">No Image</div>
          </div>
          <div class="title">{{ m.title }}</div>
          <div class="meta">⭐ {{ (m.vote_average ?? 0).toFixed(1) }}</div>
        </div>
      </div>

      <!-- 인물 결과 -->
      <div v-else class="people">
        <div v-for="p in results" :key="p.tmdb_id" class="person">
          <div class="avatar">
            <img v-if="p.profile_path" :src="img(p.profile_path)" />
            <div v-else class="empty">No</div>
          </div>
          <div class="info">
            <div class="name">{{ p.name }}</div>
            <div class="muted">{{ p.known_for_department || '' }}</div>
          </div>
        </div>
      </div>

      <p v-if="!results.length && q" class="muted">검색 결과가 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { searchComet } from '@/api/comet'

const route = useRoute()
const router = useRouter()

const q = ref(route.query.q ? String(route.query.q) : '')
const type = ref(route.query.type ? String(route.query.type) : 'movie')
const loading = ref(false)
const results = ref([])

const TMDB_IMG = 'https://image.tmdb.org/t/p/w342'
const img = (path) => `${TMDB_IMG}${path}`

function goDetail(tmdbId) {
  router.push(`/movies/${tmdbId}`)
}

function setType(next) {
  type.value = next
  router.replace({ path: '/search', query: { q: q.value, type: next } })
}

async function run() {
  if (!q.value) return
  loading.value = true
  try {
    const data = await searchComet({ q: q.value, type: type.value })
    results.value = data.results || []
    router.replace({ path: '/search', query: { q: q.value, type: type.value } })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (q.value) run()
})

watch(
  () => route.query.q,
  (next) => {
    if (next == null) return
    q.value = String(next)
  }
)
</script>

<style scoped>
.page{ padding: 18px; }
.bar{ display:flex; gap: 10px; align-items:center; margin: 12px 0; }
.bar .input{ width: min(520px, 90vw); }

.tabs{ display:flex; gap: 8px; margin: 10px 0 14px; }
.tab{
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  cursor: pointer;
  font-weight: 900;
}
.tab.active{
  background: var(--primary);
  border-color: transparent;
  color: #fff;
}

.muted{ color: var(--muted); }

.grid{
  display:grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}
.movie{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow:hidden;
  cursor:pointer;
  transition: transform .15s ease;
}
.movie:hover{ transform: translateY(-3px); }
.poster{ aspect-ratio: 2/3; background: rgba(255,255,255,.06); display:flex; align-items:center; justify-content:center; }
.poster img{ width:100%; height:100%; object-fit:cover; }
.empty{ opacity:.7; }
.title{ padding: 10px 10px 0; font-weight: 900; }
.meta{ padding: 6px 10px 10px; color: var(--muted); font-size: 13px; }

.people{ display:flex; flex-direction:column; gap: 10px; }
.person{
  display:flex;
  gap: 10px;
  align-items:center;
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 14px;
  padding: 10px;
}
.avatar{
  width: 48px;
  height: 48px;
  border-radius: 999px;
  overflow:hidden;
  border: 1px solid var(--border);
  background: rgba(255,255,255,.06);
  display:flex; align-items:center; justify-content:center;
}
.avatar img{ width:100%; height:100%; object-fit:cover; }
.name{ font-weight: 900; }
</style>
