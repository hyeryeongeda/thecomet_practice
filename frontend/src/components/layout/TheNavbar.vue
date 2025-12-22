<template>
  <nav :class="['navbar', { 'is-transparent': isDetailPage }]">
    <div class="navbar-inner">
      
      <div class="nav-left">
        <router-link to="/" class="logo-area">
          <img src="@/assets/comet_logo.png" alt="혜성" class="logo-img" /> 
          <span class="logo-text">혜성</span>
        </router-link>

        <div class="menu-links">
          <router-link to="/" class="menu-item">홈</router-link>
          <router-link :to="{ name: 'movies' }" class="menu-item">영화</router-link>
          <router-link :to="{ name: 'taste' }" class="menu-item">취향분석</router-link>
          <router-link :to="{ name: 'recommend' }" class="menu-item">추천</router-link>
        </div>
      </div>

      <div class="nav-right">
        <form @submit.prevent="onSearch" class="search-form">
          <input 
            v-model="keyword" 
            type="text" 
            placeholder="콘텐츠, 인물, 유저 검색" 
            class="search-input"
          />
        </form>

        <div class="auth-buttons">
          <template v-if="isLoggedIn">
            <button class="nav-btn outline" @click="goMyPage">마이페이지</button>
            <button class="nav-btn solid" @click="onLogout">로그아웃</button>
          </template>
          <template v-else>
            <button class="nav-btn text" @click="router.push('/login')">로그인</button>
            <button class="nav-btn solid" @click="router.push('/signup')">회원가입</button>
          </template>
        </div>
      </div>

    </div>
  </nav>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const keyword = ref('')

// 로그인 상태 체크 (Store 사용 권장)
const isLoggedIn = computed(() => authStore.isAuthenticated) // 또는 !!localStorage.getItem('access')

// [핵심] 현재 페이지가 '영화 상세'인지 확인
const isDetailPage = computed(() => route.name === 'movie-detail')

function onSearch() {
  if (!keyword.value.trim()) return
  router.push({ name: 'search', query: { q: keyword.value } })
}

function goMyPage() {
  router.push({ name: 'mypage' })
}

function onLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
/* 1. Navbar 기본 틀 (고정) */
.navbar {
  position: fixed; /* 상단 고정 */
  top: 0; left: 0; right: 0;
  height: 60px;
  background-color: #fff; /* 기본 흰색 배경 */
  border-bottom: 1px solid #eee;
  z-index: 100;
  transition: background-color 0.3s, border-color 0.3s;
}

/* 2. [핵심] 투명 모드 (상세페이지용) */
.navbar.is-transparent {
  background-color: transparent !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15); /* 살짝 라인 */
}

/* 투명 모드일 때 글자색 변경 */
.navbar.is-transparent .logo-text,
.navbar.is-transparent .menu-item {
  color: rgba(255, 255, 255, 0.9);
}
.navbar.is-transparent .menu-item:hover,
.navbar.is-transparent .menu-item.router-link-active {
  color: #fff;
}

/* 3. 레이아웃 중앙 정렬 (1100px) */
.navbar-inner {
  max-width: 1100px; /* 홈 화면과 동일한 너비 */
  margin: 0 auto;    /* 가운데 정렬 */
  height: 100%;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 좌측 영역 */
.nav-left { display: flex; align-items: center; gap: 30px; }
.logo-area { display: flex; align-items: center; gap: 8px; text-decoration: none; }
.logo-img { height: 28px; }
.logo-text { font-size: 20px; font-weight: 800; color: #000; letter-spacing: -0.5px; }

.menu-links { display: flex; gap: 20px; }
.menu-item {
  text-decoration: none; color: #777; font-size: 15px; font-weight: 600;
  transition: color 0.2s;
}
.menu-item:hover, .menu-item.router-link-active { color: #000; }

/* 우측 영역 */
.nav-right { display: flex; align-items: center; gap: 20px; }

/* 검색창 */
.search-form { position: relative; }
.search-input {
  background: #f5f5f5; border: 1px solid transparent;
  padding: 8px 12px; border-radius: 4px; font-size: 13px; width: 240px;
  transition: all 0.2s;
}
.search-input:focus { background: #fff; border-color: #ddd; outline: none; }

/* 투명 모드일 때 검색창 스타일 조정 (반투명) */
.navbar.is-transparent .search-input {
  background: rgba(0, 0, 0, 0.3); 
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
}
.navbar.is-transparent .search-input::placeholder { color: rgba(255, 255, 255, 0.6); }

/* 버튼 그룹 */
.auth-buttons { display: flex; gap: 8px; }
.nav-btn {
  padding: 6px 14px; border-radius: 4px; font-size: 13px; font-weight: 700; cursor: pointer;
  transition: all 0.2s;
}
.nav-btn.text { background: none; border: none; color: #666; }
.nav-btn.text:hover { color: #000; }

.nav-btn.outline {
  background: white; border: 1px solid #d1d1d1; color: #000;
}
.nav-btn.outline:hover { background: #f9f9f9; }

.nav-btn.solid {
  background: #111; border: 1px solid #111; color: white;
}
.nav-btn.solid:hover { background: #333; }

/* 투명 모드일 때 버튼 스타일 조정 */
.navbar.is-transparent .nav-btn.text { color: rgba(255, 255, 255, 0.8); }
.navbar.is-transparent .nav-btn.text:hover { color: #fff; }
</style>