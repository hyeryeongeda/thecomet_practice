<template>
  <article class="card" @click="goDetail" role="button" tabindex="0">
    <div class="poster-wrap">
      <img v-if="posterSrc" :src="posterSrc" :alt="movie?.title" class="poster" />
      <div v-else class="poster-fallback">No Image</div>
    </div>

    <div class="meta">
      <p class="title">{{ movie?.title }}</p>
      <p class="sub">
        <span v-if="movie?.release_date">{{ movie.release_date?.slice?.(0, 4) }}</span>
        <span v-if="movie?.vote_average"> · ★ {{ Number(movie.vote_average).toFixed(1) }}</span>
      </p>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  movie: { type: Object, required: true },
})

const router = useRouter()

const posterSrc = computed(() => {
  const p = props.movie?.poster_path
  if (!p) return ''
  return `https://image.tmdb.org/t/p/w500${p}`
})

function goDetail() {
  const tmdbId = props.movie?.tmdb_id
  if (!tmdbId) return
  router.push({ name: 'movie-detail', params: { tmdbId } })
}
</script>

<style scoped>
.card {
  width: 160px;
  cursor: pointer;
  user-select: none;
}

.poster-wrap {
  width: 160px;
  height: 240px;
  border-radius: 12px;
  overflow: hidden;
  background: #f2f2f2;
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}

.poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-fallback {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: #777;
  font-size: 12px;
}

.meta {
  margin-top: 8px;
}

.title {
  font-size: 13px;
  font-weight: 700;
  margin: 0;
  line-height: 1.3;
  color: #111;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #666;
}
</style>
