<template>
  <article class="review">
    <div class="top">
      <p class="user">@{{ username }}</p>
      <p class="rating" v-if="ratingText">{{ ratingText }}</p>
    </div>

    <p class="content">{{ contentText }}</p>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  review: { type: Object, required: true },
})

const username = computed(() => {
  return (
    props.review?.user?.username ||
    props.review?.username ||
    'anonymous'
  )
})

const ratingText = computed(() => {
  const r = props.review?.rating
  if (r === null || r === undefined || r === '') return ''
  return `★ ${Number(r).toFixed?.(1) ?? r}`
})

const contentText = computed(() => {
  return props.review?.content || props.review?.text || '리뷰 내용이 없습니다.'
})
</script>

<style scoped>
.review {
  width: 280px;
  border: 1px solid #eee;
  border-radius: 14px;
  padding: 14px 14px;
  background: white;
  box-shadow: 0 8px 18px rgba(0,0,0,0.06);
}

.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.user {
  margin: 0;
  font-weight: 800;
  color: #111;
  font-size: 13px;
}

.rating {
  margin: 0;
  color: #333;
  font-size: 13px;
  font-weight: 700;
}

.content {
  margin: 0;
  color: #444;
  font-size: 13px;
  line-height: 1.45;

  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
