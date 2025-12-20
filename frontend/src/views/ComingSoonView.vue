<template>
  <div class="page">
    <div class="box">
      <h2>{{ title }}</h2>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: { type: String, default: '준비중' },
})
</script>

<style scoped>
.page{ padding: 18px; }
.box{
  max-width: 900px; margin: 0 auto;
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 14px;
  padding: 18px;
}
.muted{ color: var(--muted); }
</style>
