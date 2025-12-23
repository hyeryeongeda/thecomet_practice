<template>
  <section class="panel">
    <div class="top">
      <div class="header-row">
        <h2 class="h2">[인물 추천]</h2>
        <button class="refresh-btn" @click="loadDefault" :disabled="loading.search">
          🔄 다른 인물 보기
        </button>
      </div>

      <div class="search">
        <input
          v-model="q"
          class="input"
          placeholder="감독/배우 이름 검색 (예: 봉준호, 톰 크루즈)"
          @keyup.enter="searchPeople"
        />
        <button class="btn" type="button" @click="searchPeople" :disabled="loading.search">
          검색
        </button>
      </div>

      <p class="hint">
        * 추천 목록 중 무작위로 선정된 감독/배우의 대표작을 보여줍니다.
      </p>
    </div>

    <div class="chips" v-if="peopleList.length">
      <button
        v-for="p in peopleList"
        :key="p.tmdb_id"
        class="chip"
        :class="{ active: selected?.tmdb_id === p.tmdb_id }"
        @click="selectPerson(p)"
        type="button"
      >
        {{ p.name }}
      </button>
    </div>

    <div v-if="selected" class="hero">
      <div class="avatar">
        <img v-if="selected.profile_path" :src="profileUrl(selected.profile_path)" alt="profile" />
        <div v-else class="noimg">2:3</div>
      </div>

      <div class="info">
        <h3 class="name">{{ selected.name }}</h3>
        <p class="role-tag">{{ selected.known_for_department }}</p>
        <p class="bio">
          {{ selectedBio }}
        </p>
      </div>
    </div>

    <div class="works" v-if="selected">
      <p class="sub">
        <strong>{{ selected.name }}</strong> 감독/배우의 대표작 및 추천작
      </p>
      
      <div v-if="loading.detail" class="loading">작품 정보를 불러오는 중...</div>

      <div v-else-if="workMovies.length" class="grid">
        <button
          v-for="m in workMovies"
          :key="m.tmdb_id"
          class="card"
          type="button"
          @click="$router.push({ name: 'movie-detail', params: { tmdbId: m.tmdb_id } })"
        >
          <div class="poster">
            <img v-if="m.poster_path" :src="posterUrl(m.poster_path)" alt="poster" />
            <div v-else class="noimg">2:3</div>
          </div>

          <div class="meta">
            <p class="title">{{ m.title }}</p>
            <p class="rate"><span class="star">★</span> {{ Number(m.vote_average || 0).toFixed(1) }}</p>
          </div>
        </button>
      </div>

      <div v-else class="empty">등록된 작품 정보가 없습니다.</div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchPersonRecommends, fetchPersonDetail } from '@/api/comet'

const q = ref('')
const loading = ref({ search: false, detail: false })
const peopleList = ref([]) 
const selected = ref(null)
const personDetail = ref(null)
const workMovies = ref([])

function profileUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w342${path}` : ''
}
function posterUrl(path) {
  if (!path) return ''
  return path.startsWith('http') ? path : `https://image.tmdb.org/t/p/w342${path}`
}

function normalizePeople(res) {
  if (Array.isArray(res?.results)) return res.results
  if (Array.isArray(res)) return res
  return []
}

async function loadDefault() {
  loading.value.search = true
  try {
    const res = await fetchPersonRecommends()
    peopleList.value = normalizePeople(res)
    
    if (peopleList.value.length > 0) {
      const randomIndex = Math.floor(Math.random() * peopleList.value.length)
      await selectPerson(peopleList.value[randomIndex])
    }
  } finally {
    loading.value.search = false
  }
}

async function searchPeople() {
  const keyword = q.value.trim()
  if (!keyword) return
  loading.value.search = true
  try {
    const res = await fetchPersonRecommends({ q: keyword })
    peopleList.value = normalizePeople(res)
    if (peopleList.value.length) {
      await selectPerson(peopleList.value[0])
    }
  } finally {
    loading.value.search = false
  }
}

async function selectPerson(p) {
  selected.value = p
  personDetail.value = null
  workMovies.value = []
  loading.value.detail = true

  try {
    const detail = await fetchPersonDetail(p.tmdb_id || p.id)
    personDetail.value = detail
    const candidates = detail?.filmography || []
    const mapped = candidates.map((x) => ({
      tmdb_id: x.tmdb_id,
      title: x.title,
      poster_path: x.poster_path,
      vote_average: x.vote_average ?? 0, 
    })).filter(x => x.tmdb_id)

    workMovies.value = mapped.slice(0, 10)
  } catch (e) {
    console.error("인물 상세 로드 실패:", e)
  } finally {
    loading.value.detail = false
  }
}

const selectedBio = computed(() => {
  const bio = personDetail.value?.biography || personDetail.value?.overview || ''
  return bio ? bio : '이 인물의 대표작과 추천작을 모아 보여줄게요.'
})

onMounted(loadDefault)
</script>

<style scoped>
/* 🎨 레이아웃 구조는 유지하고 색상만 테마 변수로 교체 */

.panel {
  border: 1px solid var(--border); /* #eee -> var(--border) */
  border-radius: 20px;
  padding: 24px;
  background: var(--card); /* #fff -> var(--card) */
  color: var(--text);      /* 글자색 대응 추가 */
  box-shadow: var(--shadow);
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.refresh-btn {
  background: var(--bg); /* 기본 배경색 */
  border: 1px solid var(--border);
  color: var(--text);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}
.refresh-btn:hover { background: var(--primary-weak); }

.top { display: grid; gap: 12px; }
.h2 { margin: 0; font-size: 20px; font-weight: 900; color: var(--text); } /* #111 -> var(--text) */

.search {
  display: grid;
  grid-template-columns: 1fr 92px;
  gap: 10px;
}
.input {
  height: 44px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--input-bg); /* #f8f8f8 -> var(--input-bg) */
  color: var(--text);
  padding: 0 15px;
  font-weight: 700;
}
.btn {
  height: 44px;
  border-radius: 12px;
  background: var(--primary); /* #111 -> var(--primary) */
  color: #fff; /* 포인트 컬러 배경 위 글자는 흰색 유지 */
  font-weight: 900;
  cursor: pointer;
  border: none;
}

.hint { margin: 0; color: var(--primary); font-weight: 800; font-size: 12px; } /* #ff4d4d -> var(--primary)로 테마 연동 */

.chips {
  margin-top: 15px;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
}
.chip {
  flex: 0 0 auto;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text);
  font-weight: 800;
  cursor: pointer;
}
.chip.active { 
  background: var(--primary); /* #111 -> var(--primary) */
  color: #fff; 
  border-color: var(--primary); 
}

/* Hero Section */
.hero {
  margin-top: 20px;
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 24px;
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 24px;
  background: var(--bg); /* 패널보다 살짝 깊이감 있게 배경색 사용 */
}

.avatar {
  width: 180px;
  aspect-ratio: 2 / 3;
  border-radius: 16px;
  overflow: hidden;
  background: #111; /* 이미지 플레이스홀더 배경은 어둡게 유지 */
  display: grid;
  place-items: center;
}
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.noimg { color: rgba(255,255,255,0.4); font-weight: 900; font-size: 20px; }

.info { display: flex; flex-direction: column; justify-content: center; gap: 10px; }
.name { margin: 0; font-size: 24px; font-weight: 900; color: var(--text); }
.role-tag { color: var(--muted); font-weight: 800; font-size: 14px; margin: 0; }
.bio { 
  margin: 0; 
  color: var(--text); /* #444 -> var(--text) */
  opacity: 0.8;
  font-weight: 600; 
  line-height: 1.6; 
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.works { margin-top: 30px; }
.sub { margin: 0 0 15px; font-size: 16px; color: var(--text); } /* #333 -> var(--text) */
.sub strong { color: var(--text); font-weight: 900; }

/* 포스터 그리드 */
.grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
}

.card {
  border: none;
  padding: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s;
}
.card:hover { transform: translateY(-5px); }

.poster {
  width: 100%;
  aspect-ratio: 2 / 3;
  border-radius: 14px;
  overflow: hidden;
  background: #111;
  display: grid;
  place-items: center;
  margin-bottom: 10px;
}
.poster img { width: 100%; height: 100%; object-fit: cover; }

.meta { padding: 0 4px; }
.title {
  margin: 0 0 5px;
  font-weight: 900;
  font-size: 14px;
  color: var(--text); /* #111 -> var(--text) */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rate { color: var(--muted); font-weight: 800; font-size: 13px; margin: 0; }
.star { color: #f5c518; margin-right: 2px; } /* 별 색상은 테마 무관 고정 */

@media (max-width: 768px) {
  .hero { grid-template-columns: 120px 1fr; padding: 15px; }
  .avatar { width: 120px; }
}
</style>