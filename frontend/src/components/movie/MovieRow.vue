<template>
  <section class="row">
    <div class="row-head">
      <h2 class="row-title">{{ title }}</h2>

      <div class="actions">
        <button class="nav-btn" @click="scrollLeft">‹</button>
        <button class="nav-btn" @click="scrollRight">›</button>
      </div>
    </div>

    <div ref="rail" class="rail">
      <MovieCard
        v-for="m in movies"
        :key="m.tmdb_id"
        :movie="m"
      />
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import MovieCard from './MovieCard.vue'

defineProps({
  title: { type: String, required: true },
  movies: { type: Array, default: () => [] },
})

const rail = ref(null)

function scrollLeft() {
  rail.value?.scrollBy({ left: -800, behavior: 'smooth' })
}
function scrollRight() {
  rail.value?.scrollBy({ left: 800, behavior: 'smooth' })
}
</script>

<style scoped>
.row {
  margin: 26px 0;
}

.row-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.row-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #111;
}

.actions {
  display: flex;
  gap: 8px;
}

.nav-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--card);
  cursor: pointer;
  font-size: 18px;
  color: var(--text);
}

.nav-btn:hover:not(:disabled) {
  background: var(--primary);     
  border-color: var(--primary);
  color: #ffffff;                  
  transform: scale(1.1);           
}

.nav-btn:hover:not(:disabled) {
  background: var(--primary);     
  border-color: var(--primary);
  color: #ffffff;                  
  transform: scale(1.1);         
}

.sec-title { margin: 0; font-size: 18px; font-weight: 900; color: var(--text); }
.more { 
  border: none; 
  background: transparent; 
  cursor: pointer; 
  color: var(--muted); 
  font-weight: 900; 
}
.more:hover { 
  text-decoration: underline; 
  color: var(--primary); 
}

.rail {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  padding: 4px 2px 12px;
  scroll-behavior: smooth;
}

.rail::-webkit-scrollbar {
  height: 8px;
}
.rail::-webkit-scrollbar-thumb {
  background: rgba(0,0,0,0.12);
  border-radius: 999px;
}
</style>
