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
                <div class="dropdown-item" @click="changeTheme('midnight')">Midnight Gold</div>
                <div class="dropdown-item" @click="changeTheme('purple')">Cyber Purple</div>
                <div class="dropdown-item" @click="changeTheme('forest')">Forest Green</div>
                <div class="dropdown-item" @click="changeTheme('sunset')">Sunset Orange</div>
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

function changeTheme(themeName) {
  themeStore.setTheme(themeName)
}
</script>

<style scoped>
/* 네비게이션 컨테이너 */
.nav-container {
  position: fixed;
  top: 0; left: 0; right: 0;
  width: 100%; height: 60px;
  background: var(--nav-bg); 
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--nav-border);
  z-index: 9999;
  transition: all 0.3s ease;
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

/* 브랜드 및 링크 색상 */
.brand-text, .link {
  color: var(--nav-text);
  transition: color 0.3s;
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
}

.link:hover, .link.router-link-active {
  color: var(--primary);
  font-weight: 800;
}

/* 유저 아이콘 */
.user-menu-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  height: 60px;
  cursor: pointer;
}

.user-icon {
  width: 28px; height: 28px;
  color: var(--nav-text);
  transition: color 0.3s;
}

.user-menu-wrapper:hover .dropdown-menu { display: block; }

/* 검색창 */
.search {
  width: 200px; padding: 7px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--input-bg);
  color: var(--text);
  outline: none;
  transition: all 0.2s;
  font-size: 13px;
}

/* 드롭다운 공통 스타일 (테마 변수 적용) */
.dropdown-menu, .sub-dropdown {
  background: var(--card); 
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--shadow);
  z-index: 10000;
}

.dropdown-menu {
  display: none;
  position: absolute;
  top: 55px;
  right: 0;
  width: 160px;
  overflow: visible;
}

.dropdown-item {
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  text-decoration: none;
  transition: background 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.dropdown-item:hover {
  background: var(--primary-weak);
  color: var(--primary);
}

/* 서브 드롭다운 */
.theme-item { position: relative; }
.theme-item:hover .sub-dropdown { display: block; }

.sub-dropdown {
  display: none;
  position: absolute;
  top: 0;
  left: -160px; /* 메인 메뉴 왼쪽으로 펼침 */
  width: 160px;
}

.arrow { font-size: 10px; color: var(--muted); }

/* 투명 모드 스타일 */
.nav-container.transparent {
  background: transparent !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* 공통 버튼 스타일 */
.btn {
  padding: 7px 12px; border-radius: 6px;
  text-decoration: none; cursor: pointer; font-size: 13px; font-weight: 700;
  border: 1px solid var(--primary); background: var(--primary); color: #fff;
}
.btn.ghost {
  background: transparent; border: 1px solid transparent; color: var(--nav-text);
}

.left { display: flex; align-items: center; gap: 20px; }
.brand { display: flex; align-items: center; gap: 8px; text-decoration: none; }
.logo { width: 28px; height: 28px; object-fit: contain; }
.brand-text { font-weight: 800; font-size: 18px; }
.menu { display: flex; gap: 16px; }
.right { display: flex; align-items: center; gap: 10px; }
</style>