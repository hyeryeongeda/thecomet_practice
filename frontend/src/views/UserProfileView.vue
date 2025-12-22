<template>
  <div class="page">
    <h1 class="title">유저 프로필</h1>

    <div v-if="loading" class="muted">로딩중...</div>

    <div v-else>
      <div class="card profile-card">
        <div class="row">
          <img class="avatar" :src="user.profile_image || fallback" alt="profile" />
          <div class="info">
            <div class="name">{{ user.username }}</div>
            <div class="muted">{{ user.email }}</div>
            <div class="muted">팔로워 {{ user.followers_count }} · 팔로잉 {{ user.following_count }}</div>
          </div>
        </div>

        <div class="actions" v-if="canFollow">
          <button class="btn" @click="onToggleFollow">
            {{ isFollowing ? '언팔로우' : '팔로우' }}
          </button>
        </div>
      </div>

      <div class="movie-section">
        <h2 class="sub-title">활동 내역 (리뷰한 영화)</h2>
        <div v-if="userMovies.length" class="grid">
          <div v-for="m in userMovies" :key="m.tmdb_id" class="movie-item" @click="goDetail(m.tmdb_id)">
            <div class="poster">
              <img :src="posterUrl(m.poster_path)" alt="poster" />
            </div>
            <div class="meta">
              <p class="m-title">{{ m.title }}</p>
              <p class="m-stars">★ {{ Number(m.vote_average || 0).toFixed(1) }}</p>
            </div>
          </div>
        </div>
        <div v-else class="muted">아직 활동 내역이 없습니다.</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router' // useRouter 추가
import { useAuthStore } from '@/stores/auth'
import { fetchUserProfile, toggleFollow } from '@/api/comet'

const route = useRoute()
const router = useRouter() // router 인스턴스 생성
const auth = useAuthStore()

const loading = ref(true)
const user = ref({})
const userMovies = ref([]) // 초기값 빈 배열로 선언
const isFollowing = ref(false)
const fallback = 'https://placehold.co/96x96?text=%F0%9F%91%A4'

const username = computed(() => route.params.username)

/**
 * [해결] 팔로우 버튼 노출 로직 수정
 * auth.isAuthenticated가 undefined로 뜰 경우를 대비해 !!를 붙여 확실히 불리언화합니다.
 */
const canFollow = computed(() => {
  const me = auth.user?.username
  const target = user.value?.username
  // auth.user가 존재한다면 로그인된 것으로 간주하는 방어 코드 추가
  const isLoggedIn = !!(auth.isAuthenticated || auth.user)
  
  console.log("--- 팔로우 버튼 체크 ---")
  console.log("로그인 여부:", isLoggedIn)
  console.log("내 이름(me):", me)
  console.log("상대 이름(target):", target)

  if (!isLoggedIn) return false
  if (!target) return false
  if (me === target) return false // 본인 프로필이면 숨김

  return true
})

/**
 * [추가] 포스터 URL 변환 함수
 */
function posterUrl(path) {
  if (!path) return 'https://placehold.co/342x513?text=No+Poster'
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w342${path}`
}

/**
 * [추가] 영화 상세 페이지 이동 함수
 */
function goDetail(tmdbId) {
  router.push({ name: 'movie-detail', params: { tmdbId } })
}

async function load() {
  loading.value = true
  try {
    const data = await fetchUserProfile(username.value)
    user.value = data
    // 백엔드 응답 필드명 확인 (reviewed_movies 또는 movies)
    userMovies.value = data.reviewed_movies || data.movies || [] 
    isFollowing.value = !!data.is_following
  } catch (err) {
    console.error("프로필 로드 에러:", err)
    userMovies.value = []
  } finally {
    loading.value = false
  }
}

async function onToggleFollow() {
  if (!(auth.isAuthenticated || auth.user)) {
    alert("로그인이 필요한 서비스입니다.")
    return
  }
  try {
    const res = await toggleFollow(username.value)
    isFollowing.value = res.is_following
    user.value.followers_count = res.followers_count
    user.value.following_count = res.following_count
  } catch (err) {
    console.error(err)
    alert("팔로우 처리 중 오류가 발생했습니다.")
  }
}

onMounted(async () => {
  // Pinia 스토어가 비어있다면 정보를 먼저 채움
  if (!auth.user?.username && auth.fetchMe) {
    await auth.fetchMe()
  }
  await load()
})

// 유저 페이지 간 이동(user1 -> user2) 시 데이터를 다시 불러오도록 감시
watch(username, () => {
  load()
})
</script>

<style scoped>
.page { padding: 18px; max-width: 1000px; margin: 0 auto; }
.title { margin: 0 0 20px; font-size: 28px; font-weight: 1000; }
.sub-title { margin: 30px 0 15px; font-size: 20px; font-weight: 900; }
.muted { color: var(--muted); font-weight: 600; }

.profile-card {
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 20px;
  background: var(--card);
  box-shadow: var(--shadow);
}

.row { display: flex; gap: 20px; align-items: center; }
.avatar { width: 80px; height: 80px; border-radius: 20px; object-fit: cover; border: 1px solid var(--border); }
.info .name { font-weight: 1000; font-size: 22px; }

.btn {
  margin-top: 15px;
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 12px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 1000;
  transition: background 0.2s;
}
.btn:hover {
  background: #eee;
}

/* 영화 그리드 스타일 */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}
.movie-item { cursor: pointer; transition: transform 0.2s; }
.movie-item:hover { transform: translateY(-5px); }
.poster { aspect-ratio: 2/3; border-radius: 12px; overflow: hidden; background: #000; }
.poster img { width: 100%; height: 100%; object-fit: cover; }
.meta { margin-top: 8px; }
.m-title { font-weight: 900; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.m-stars { color: #f5c518; font-weight: 800; font-size: 13px; }
</style>