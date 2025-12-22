<template>
  <div class="app-wrapper">
    <TheNavbar />

    <div class="main-content">
      <RouterView />
    </div>

    <TheFooter />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import TheNavbar from '@/components/layout/TheNavbar.vue'
import TheFooter from '@/components/layout/TheFooter.vue'
</script>

<style>
/* 전역 스타일 리셋 */
* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: 'Pretendard', sans-serif; }

/* [핵심 수정 포인트]
  Navbar 높이(60px)만큼 padding-top을 줘서
  모든 페이지의 내용이 Navbar 아래부터 시작되게 만듭니다.
*/
.main-content {
  padding-top: 60px; 
  min-height: calc(100vh - 60px); /* 푸터가 바닥에 붙도록 최소 높이 확보 */
}
</style>