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

        <div v-if="isLoggedIn" class="user-menu-wrapper">
          <div class="user-icon-btn">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="user-icon">
              <path fill-rule="evenodd" d="M7.5 6a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM3.751 20.105a8.25 8.25 0 0 1 16.498 0 .75.75 0 0 1-.437.695A18.683 18.683 0 0 1 12 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 0 1-.437-.695Z" clip-rule="evenodd" />
            </svg>
          </div>

          <div class="dropdown-menu">
            <RouterLink :to="{ name: 'mypage' }" class="dropdown-item">마이페이지</RouterLink>
            <div class="dropdown-item" @click="onLogout">로그아웃</div>
            
            <div class="dropdown-item theme-item">
              <span>테마변경</span>
              <span class="arrow"> > </span>
              
              <div class="sub-dropdown">
                <div class="dropdown-item" @click="changeTheme('blackred')">Black Red</div>
                <div class="dropdown-item" @click="changeTheme('blue')">Blue</div>
              </div>
            </div>
          </div>
        </div>

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
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import logoUrl from '@/assets/comet_logo.png'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const themeStore = useThemeStore()

const q = ref('')

const isDetailPage = computed(() => route.name === 'movie-detail')
const isLoggedIn = computed(() => auth.isLoggedIn || auth.isAuthenticated) 

function goSearch() {
  const keyword = q.value.trim()
  if (!keyword) return
  router.push({ name: 'search', query: { q: keyword } })
  q.value = ''
}

function onLogout() {
  auth.logout()
  router.push('/')
}

// 🔥 테마 직접 변경 함수
function changeTheme(themeName) {
  themeStore.setTheme(themeName)
}
</script>

<style scoped>
.nav-container {
  position: fixed;
  top: 0; left: 0; right: 0;
  width: 100%; height: 60px;
  /* 테마 변수 적용 (투명도 50%) */
  background: var(--nav-bg); 
  backdrop-filter: blur(10px); /* 배경 흐림 효과를 주면 훨씬 고급스러워집니다 */
  border-bottom: 1px solid var(--nav-border);
  z-index: 9999;
  transition: all 0.3s ease;
}

/* 브랜드 텍스트 및 메뉴 링크 색상 */
.brand-text, .link {
  color: var(--nav-text);
  transition: color 0.3s;
}

/* [블랙레드 포인트] 마우스를 올리거나 활성화된 메뉴는 레드로 강조 */
.link:hover, .link.router-link-active {
  color: var(--primary);
  font-weight: 800;
}

/* 사람 아이콘 색상 */
.user-icon {
  width: 28px; height: 28px;
  color: var(--nav-text); /* 아이콘도 네비 텍스트 색상을 따라갑니다 */
}

.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  height: 100%;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-menu-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  height: 60px;
  cursor: pointer;
}

.user-icon { width: 28px; height: 28px; color: #444; }

/* 호버 시 드롭다운 표시 */
.user-menu-wrapper:hover .dropdown-menu { display: block; }
/* 검색창 스타일 조정 */
.search {
  width: 200px; padding: 7px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--input-bg);
  color: var(--text);
  outline: none;
  transition: all 0.2s;
}

/* 드롭다운 메뉴 스타일 */
.dropdown-menu {
  background: var(--card); /* 테마별 카드 배경색 사용 */
  border: 1px solid var(--border);
  color: var(--text);
}
.dropdown-item {
  color: var(--text);
}

.dropdown-item:hover {
  background: var(--primary-weak);
  color: var(--primary); /* 호버 시 레드 포인트 */
}

/* 상세페이지 투명 모드 (이 기능은 유지하되 변수와 조화롭게) */
.nav-container.transparent {
  background: transparent !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.dropdown-menu {
  display: none;
  position: absolute;
  top: 55px;
  right: 0;
  width: 150px;
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  overflow: visible; /* 하위 메뉴가 보여야 하므로 visible */
  z-index: 10000;
}

.dropdown-item {
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #444;
  text-decoration: none;
  transition: background 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f5f5f5;
  color: #000;
}

/* 🔥 테마변경 서브 메뉴 스타일 */
.theme-item {
  position: relative;
}

.arrow {
  font-size: 10px;
  color: #aaa;
}

/* 테마변경에 마우스 올리면 서브 드롭다운 표시 */
.theme-item:hover .sub-dropdown {
  display: block;
}

.sub-dropdown {
  display: none;
  position: absolute;
  top: 0;
  left: -150px; /* 메인 메뉴의 왼쪽에 위치 (오른쪽 공간 확보) */
  width: 150px;
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: -5px 5px 20px rgba(0,0,0,0.1);
}

/* 검색창 및 투명 모드 스타일 (기본 유지) */
.left { display: flex; align-items: center; gap: 20px; }
.brand { display: flex; align-items: center; gap: 8px; text-decoration: none; color: inherit; }
.logo { width: 28px; height: 28px; object-fit: contain; }
.brand-text { font-weight: 800; font-size: 18px; }
.menu { display: flex; gap: 16px; }
.link { text-decoration: none; color: #444; font-size: 15px; font-weight: 600; }
.right { display: flex; align-items: center; gap: 10px; }
.search { width: 200px; padding: 7px 12px; border: 1px solid #ddd; border-radius: 6px; background: #f5f5f5; outline: none; font-size: 13px; }

.btn { padding: 7px 12px; border-radius: 6px; font-size: 13px; font-weight: 700; border: 1px solid #333; background: #333; color: #fff; cursor: pointer; }
.btn.ghost { background: transparent; border: 1px solid transparent; color: #555; }
</style>