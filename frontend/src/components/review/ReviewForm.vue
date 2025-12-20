<template>
  <div class="box">
    <h3>리뷰 작성</h3>

    <div class="row">
      <label class="check">
        <input type="checkbox" v-model="watched" />
        <span>봤어요</span>
      </label>

      <div class="rating">
        <span class="label">별점</span>
        <select v-model.number="rating" class="select">
          <option :value="0">선택</option>
          <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>
    </div>

    <textarea
      v-model.trim="content"
      class="textarea"
      maxlength="200"
      placeholder="한줄평을 작성해 주세요 (최대 200자)"
    />

    <div class="actions">
      <button class="btn primary" @click="submit" :disabled="loading">
        {{ loading ? '등록 중...' : '등록' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { createMovieReview } from '@/api/comet'
import { useReviewStore } from '@/stores/review'

const props = defineProps({
  tmdbId: { type: Number, required: true },
})

const store = useReviewStore()

const watched = ref(false)
const rating = ref(0)
const content = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''

  if (!watched.value) {
    error.value = "리뷰 작성은 '봤어요' 체크가 필요합니다."
    return
  }
  if (!rating.value) {
    error.value = '별점은 필수입니다.'
    return
  }
  if (!content.value) {
    error.value = '한줄평을 입력해 주세요.'
    return
  }

  loading.value = true
  try {
    await createMovieReview(props.tmdbId, {
      watched: true,
      rating: rating.value,
      content: content.value,
    })
    // 입력 초기화
    watched.value = false
    rating.value = 0
    content.value = ''
    store.bumpReload()
  } catch (e) {
    error.value = e?.response?.data?.detail || '리뷰 등록 실패'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.box{
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 14px;
  padding: 14px;
}
h3{ margin: 0 0 10px; }
.row{ display:flex; align-items:center; justify-content:space-between; gap: 10px; }
.check{ display:flex; align-items:center; gap: 8px; font-weight: 900; }
.rating{ display:flex; align-items:center; gap: 8px; }
.label{ color: var(--muted); font-size: 13px; }
.select{
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--input-bg);
  color: var(--text);
}
.textarea{
  width: 100%;
  margin-top: 10px;
  min-height: 90px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--input-bg);
  color: var(--text);
  outline: none;
  resize: vertical;
}
.actions{ display:flex; align-items:center; gap: 10px; margin-top: 10px; }
.error{ color: #ff4d4f; margin:0; font-size: 13px; }
</style>
