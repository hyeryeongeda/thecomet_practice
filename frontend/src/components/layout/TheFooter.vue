<template>
  <footer class="footer">
    <div class="inner">
      <div class="left">
        <div class="brand">혜성 (The Comet)</div>
        <p class="desc">
          TMDB 기반 영화 정보 · 리뷰 · 취향분석/추천 플랫폼
        </p>
      </div>

      <div class="right">
        <a class="link" href="#" @click.prevent="scrollTop">맨 위로</a>
        <span class="dot">·</span>
        <span class="copy">© {{ year }} The Comet. All rights reserved.</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()

function scrollTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
/* 🎨 레이아웃 구조는 유지하고 색상만 테마 변수로 교체 */

.footer{
  margin-top: 30px;
  border-top: 1px solid var(--border);
  background: var(--card); /* #fff -> var(--card) 테마 대응 */
  transition: background-color 0.3s, color 0.3s;
}
.inner{
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px 14px;
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap: 12px;
}
.left{ display:flex; flex-direction:column; gap: 4px; }
.brand{ 
  font-weight: 1000; 
  letter-spacing: -0.2px; 
  color: var(--text); /* 글자색 대응 */
}
.desc{ margin:0; color: var(--muted); font-size: 13px; }

.right{
  display:flex;
  align-items:center;
  gap: 10px;
  color: var(--muted);
  font-size: 13px;
  white-space: nowrap;
}
.link{
  color: inherit;
  text-decoration:none;
  font-weight: 900;
}
.link:hover{ text-decoration: underline; color: var(--primary); } /* 호버 시 포인트 컬러 */
.dot{ opacity: 0.6; }

@media (max-width: 720px){
  .inner{ flex-direction:column; align-items:flex-start; }
  .right{ white-space: normal; }
}
</style>