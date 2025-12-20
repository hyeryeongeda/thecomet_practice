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
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { fetchMovieReviews, deleteReview } from '@/api/comet'
import { useReviewStore } from '@/stores/review'
import ReviewItem from './ReviewItem.vue'

const props = defineProps({
  tmdbId: { type: Number, required: true },
})

const router = useRouter()
const store = useReviewStore()
const { reloadKey } = storeToRefs(store)

const loading = ref(false)
const reviews = ref([])

async function load() {
  // movie 데이터 늦게 들어오는 케이스 방어
  if (!props.tmdbId) return

  loading.value = true
  try {
    const data = await fetchMovieReviews(props.tmdbId)
    // 백엔드가 list 그대로 주면 배열, pagination 쓰면 results일 수 있어서 둘 다 대응
    reviews.value = Array.isArray(data) ? data : (data?.results ?? [])
  } catch (e) {
    reviews.value = []
    console.error(e)
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

// ✅ 핵심: tmdbId가 “나중에” 들어와도 자동 로드 + 작성/수정/삭제 bumpReload도 반응
watch([() => props.tmdbId, reloadKey], load, { immediate: true })
</script>

<style scoped>
.wrap { margin-top: 14px; }
.list { display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }
.muted { color: var(--muted); }
</style>
