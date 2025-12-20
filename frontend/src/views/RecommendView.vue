<template>
  <div class="page">
    <h1>추천</h1>
    <p class="muted">장르/인물/유저 추천 3블록은 다음 단계에서 붙임</p>

    <div class="grid">
      <div class="card">장르 기반 추천</div>
      <div class="card">인물 기반 추천</div>
      <div class="card">유저 기반 추천</div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.page{ padding: 18px; }
.muted{ color: var(--muted); }
.grid{
  margin-top: 14px;
  display:grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}
.card{
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 16px;
  padding: 16px;
  font-weight: 1000;
  transition: transform .15s ease;
}
.card:hover{ transform: translateY(-4px); }
</style>
