<!-- frontend/src/components/review/ReviewList.vue -->
<template>
  <div class="wrap">
    <h3>리뷰</h3>

    <p v-if="loading" class="muted">불러오는 중...</p>
    <p v-else-if="reviews.length === 0" class="muted">아직 작성된 리뷰가 없습니다.</p>

    <div v-else class="list">
      <ReviewItem
        v-for="r in reviews"
        :key="r.id"
        :review="r"
        @delete="remove"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { deleteReview, fetchMovieReviews } from '@/api/comet'
import { useReviewStore } from '@/stores/review'
import ReviewItem from './ReviewItem.vue'

const props = defineProps({
  tmdbId: { type: Number, required: true },
})

const store = useReviewStore()

const loading = ref(false)
const reviews = ref([])

async function load() {
  if (!props.tmdbId) return
  loading.value = true
  try {
    const data = await fetchMovieReviews(props.tmdbId)
    reviews.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (e) {
    console.error('review load failed:', e)
    reviews.value = []
  } finally {
    loading.value = false
  }
}

async function remove(reviewId) {
  try {
    await deleteReview(reviewId)
    await load()
  } catch (e) {
    alert(e?.response?.data?.detail || '삭제 실패')
  }
}

/**
 * ✅ 핵심:
 * - tmdbId가 준비되는 순간 load()
 * - 리뷰 작성 후 store.bumpReload()로도 load()
 */
watch(
  () => props.tmdbId,
  () => load(),
  { immediate: true }
)

watch(
  () => store.reloadKey,
  () => load()
)
</script>

<style scoped>
.wrap{ margin-top: 14px; }
.list{ display:flex; flex-direction:column; gap: 10px; margin-top: 10px; }
.muted{ color: var(--muted); }
</style>
