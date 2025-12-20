<template>
  <div class="page">
    <h1>취향 분석</h1>
    <p class="muted">AI 프롬프트 추천은 다음 단계에서 백엔드 연동</p>

    <div class="box">
      <input class="input" v-model="prompt" placeholder="예) 오늘 비 오는데 감성 로맨스 추천" />
      <button class="btn primary" @click="run" :disabled="!prompt">추천 요청</button>
    </div>

    <div v-if="result" class="result">
      <h3>결과</h3>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const prompt = ref('')
const result = ref('')

function run() {
  // 다음 단계에서 taste store + 백엔드 API로 연결
  result.value = `요청 프롬프트: ${prompt.value}\n(여기에 추천 결과가 들어올 예정)`
}
</script>

<style scoped>
.page{ padding: 18px; }
.muted{ color: var(--muted); }
.box{ display:flex; gap: 10px; align-items:center; margin-top: 14px; }
.box .input{ width: min(520px, 90vw); }
.result{
  margin-top: 14px;
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 16px;
  padding: 14px;
}
pre{ margin: 0; white-space: pre-wrap; }
</style>
