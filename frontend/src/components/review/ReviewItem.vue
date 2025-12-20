<template>
  <div class="r">
    <div class="top">
      <button class="user" @click="goUser">@{{ username }}</button>
      <span class="dot">·</span>
      <button class="movie" @click="goMovie">{{ movieTitle }}</button>
      <span class="spacer"></span>
      <span v-if="rating" class="rating">★ {{ rating }}</span>
    </div>

    <p class="content">{{ content }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  review: { type: Object, required: true },
})

const router = useRouter()

const username = computed(() => {
  const r = props.review || {}
  return r.user?.username || r.username || r.author || 'unknown'
})

const movieTitle = computed(() => {
  const r = props.review || {}
  return r.movie?.title || r.movie_title || r.title || '영화'
})

const content = computed(() => props.review?.content || props.review?.text || '')

const rating = computed(() => {
  const v = props.review?.rating
  if (v === undefined || v === null) return ''
  return v
})

function goUser() {

  const r = props.review || {}
  const uid = r.user?.id || r.user_id || null
  if (uid) router.push({ name: 'movie-detail', params: { tmdbId } })

}

function goMovie() {
  const r = props.review || {}
  const tmdbId = r.movie?.tmdb_id || r.tmdb_id || r.movie_tmdb_id
  if (tmdbId) router.push(`/movies/${tmdbId}`)
}
</script>

<style scoped>
.r {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 14px;
  padding: 12px 14px;
}
.top {
  display: flex;
  align-items: center;
  gap: 8px;
}
.user, .movie {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
  font-weight: 800;
  color: #111;
}
.movie { font-weight: 700; color: #333; }
.dot { color: #bbb; }
.spacer { flex: 1; }
.rating {
  font-weight: 900;
}
.content {
  margin: 10px 0 0;
  color: #333;
  line-height: 1.4;
}
</style>
