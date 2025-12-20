<template>
  <header class="nav">
    <div class="left">
      <RouterLink to="/" class="brand">
        <img :src="logoUrl" class="logo" alt="혜성 로고" />
        <span class="brand-text">혜성</span>
      </RouterLink>

      <nav class="menu">
        <RouterLink to="/" class="link">홈</RouterLink>
        <RouterLink to="/movies" class="link">영화</RouterLink>
        <RouterLink to="/taste" class="link">취향분석</RouterLink>
        <RouterLink to="/recommend" class="link">추천</RouterLink>
      </nav>
    </div>

    <div class="right">
      <input
        class="search"
        type="text"
        placeholder="Search"
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
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import logoUrl from '@/assets/comet_logo.png'

const router = useRouter()
const auth = useAuthStore()

const q = ref('')
const isLoggedIn = computed(() => auth.isLoggedIn)

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
</script>

<style scoped>
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: white;
  border-bottom: 1px solid #eee;
}

.left {
  display: flex;
  align-items: center;
  gap: 18px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
}

.logo {
  width: 28px;
  height: 28px;
  object-fit: contain;
}

.brand-text {
  font-weight: 800;
}

.menu {
  display: flex;
  gap: 14px;
}

.link {
  text-decoration: none;
  color: #222;
  font-size: 14px;
}

.link.router-link-active {
  font-weight: 700;
}

.right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search {
  width: 220px;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
}

.btn {
  border: 1px solid #222;
  background: #222;
  color: #fff;
  padding: 8px 12px;
  border-radius: 8px;
  text-decoration: none;
  cursor: pointer;
  font-size: 14px;
}

.btn.ghost {
  background: transparent;
  color: #222;
}
</style>
