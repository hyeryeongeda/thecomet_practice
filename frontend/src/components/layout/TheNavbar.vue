<template>
  <header :class="['nav-container', { 'transparent': isDetailPage }]">
    
    <div class="nav-inner">
      <div class="left">
        <RouterLink to="/" class="brand">
          <img :src="logoUrl" class="logo" alt="혜성 로고" />
          <span class="brand-text">혜성</span>
        </RouterLink>

        <nav class="menu">
          <RouterLink to="/" class="link">홈</RouterLink>
          <RouterLink :to="{ name: 'movies' }" class="link">영화</RouterLink>
          <RouterLink to="/taste" class="link">취향분석</RouterLink>
          <RouterLink to="/recommend" class="link">추천</RouterLink>
        </nav>
      </div>

      <div class="right">
        <input
          class="search"
          type="text"
          placeholder="검색"
          v-model="q"
          @keyup.enter="goSearch"
        />

        <template v-if="isLoggedIn">
          <RouterLink :to="{ name: 'mypage' }" class="btn ghost">마이페이지</RouterLink>
          <button class="btn" @click="onLogout">로그아웃</button>
        </template>

        <template v-else>
          <RouterLink to="/login" class="btn ghost">로그인</RouterLink>
          <RouterLink to="/signup" class="btn">회원가입</RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router' // useRoute 추가
import { useAuthStore } from '@/stores/auth'
import logoUrl from '@/assets/comet_logo.png'

const router = useRouter()
const route = useRoute() // 현재 주소 정보 가져오기
const auth = useAuthStore()

const q = ref('')

// [핵심] 현재 페이지가 영화 상세페이지인지 확인
const isDetailPage = computed(() => route.name === 'movie-detail')

// 로그인 상태 체크 (스토어 상태가 반응형으로 동작하도록)
const isLoggedIn = computed(() => auth.isLoggedIn || auth.isAuthenticated) 

function goSearch() {
  const keyword = q.value.trim()
  if (!keyword) return
  router.push({ name: 'search', query: { q: keyword } })
  q.value = ''
}

function onLogout() {
  auth.logout()
  router.push('/') // 로그아웃 후 홈으로 이동
}
</script>

<style scoped>
/* 1. 네비게이션 컨테이너 (배경 및 위치) */
.nav-container {
  position: fixed; /* 상단 고정 */
  top: 0; left: 0; right: 0;
  width: 100%;
  height: 60px; /* 높이 고정 */
  background: white; /* 기본 배경 */
  border-bottom: 1px solid #eee;
  z-index: 9999; /* 항상 맨 위에 */
  transition: background-color 0.3s, border-color 0.3s;
}

/* 2. 내부 컨텐츠 정렬 (1100px 제한) */
.nav-inner {
  max-width: 1100px;
  margin: 0 auto; /* 가운데 정렬 */
  height: 100%;
  padding: 0 20px; /* 좌우 여백 */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 3. 투명 모드 스타일 (상세페이지용) */
.nav-container.transparent {
  background-color: transparent !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* 투명 모드일 때 글자색 변경 (흰색) */
.nav-container.transparent .link,
.nav-container.transparent .brand-text,
.nav-container.transparent .btn.ghost {
  color: rgba(255, 255, 255, 0.9);
}

.nav-container.transparent .link:hover,
.nav-container.transparent .link.router-link-active {
  color: #fff;
  font-weight: 800;
}

/* 투명 모드일 때 검색창 반투명 처리 */
.nav-container.transparent .search {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}
.nav-container.transparent .search::placeholder {
  color: rgba(255, 255, 255, 0.7);
}


/* --- 기존 스타일 유지 --- */
.left { display: flex; align-items: center; gap: 20px; }
.brand { display: flex; align-items: center; gap: 8px; text-decoration: none; color: inherit; }
.logo { width: 28px; height: 28px; object-fit: contain; }
.brand-text { font-weight: 800; font-size: 18px; }

.menu { display: flex; gap: 16px; }
.link { text-decoration: none; color: #444; font-size: 15px; font-weight: 600; transition: color 0.2s; }
.link.router-link-active { color: #000; font-weight: 800; }

.right { display: flex; align-items: center; gap: 10px; }
.search {
  width: 200px; padding: 7px 12px;
  border: 1px solid #ddd; border-radius: 6px;
  background: #f5f5f5; outline: none; font-size: 13px;
  transition: all 0.2s;
}
.search:focus { background: white; border-color: #333; }

.btn {
  padding: 7px 12px; border-radius: 6px;
  text-decoration: none; cursor: pointer; font-size: 13px; font-weight: 700;
  border: 1px solid #333; background: #333; color: #fff;
  transition: opacity 0.2s;
}
.btn:hover { opacity: 0.8; }

.btn.ghost {
  background: transparent; border: 1px solid transparent; color: #555;
}
.btn.ghost:hover { color: #111; background: rgba(0,0,0,0.05); }
</style>