<template>
  <main class="page">
    <section class="container">
      <h1 class="title">추천</h1>

      <div class="tabs">
        <button class="tab" :class="{ active: tab === 'chat' }" @click="tab = 'chat'">AI 맞춤</button>
        <button class="tab" :class="{ active: tab === 'genre' }" @click="tab = 'genre'">장르</button>
        <button class="tab" :class="{ active: tab === 'person' }" @click="tab = 'person'">인물</button>
        <button class="tab" :class="{ active: tab === 'user' }" @click="tab = 'user'">유저</button>
      </div>

      <RecommendAi v-if="tab === 'chat'" />
      <RecommendGenre v-else-if="tab === 'genre'" />
      <RecommendPerson v-else-if="tab === 'person'" />
      <RecommendUser v-else />
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import RecommendAi from '@/components/recommend/RecommendAi.vue'
import RecommendGenre from '@/components/recommend/RecommendGenre.vue'
import RecommendPerson from '@/components/recommend/RecommendPerson.vue'
import RecommendUser from '@/components/recommend/RecommendUser.vue'

const tab = ref('chat')
</script>

<style scoped>
.page { min-height: calc(100vh - 60px); background: #fff; }
.container { width: min(1000px, 92vw); margin: 0 auto; padding: 22px 0 60px; }
.title { margin: 0 0 14px; font-size: 26px; font-weight: 900; }

.tabs { display: flex; gap: 8px; margin-bottom: 14px; }
.tab {
  height: 38px; padding: 0 12px; border-radius: 12px;
  border: 1px solid #e6e6e6; background: #fff;
  font-weight: 900; cursor: pointer;
}
.tab.active { border-color: #111; background: #111; color: #fff; }
</style>
