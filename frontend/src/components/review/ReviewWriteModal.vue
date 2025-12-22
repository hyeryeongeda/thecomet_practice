<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ movieTitle }}</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      
      <div class="modal-body">
        <div class="rating-select-area">
          <span class="label">별점 선택</span>
          <div class="stars">
            <span 
              v-for="n in 5" 
              :key="n" 
              class="star-icon" 
              :class="{ active: n <= rating }"
              @click="rating = n"
            >★</span>
          </div>
          <span class="rating-text">{{ rating }}점</span>
        </div>

        <textarea 
          v-model="content" 
          placeholder="이 작품에 대한 생각을 자유롭게 표현해주세요." 
          class="review-input"
          maxlength="10000"
        ></textarea>
      </div>
      
      <div class="modal-footer">
        <button v-if="existingReview" class="delete-btn" @click="onDelete">삭제</button>

        <div class="right-group">
          <div class="text-counter">{{ content.length.toLocaleString() }}/10,000</div>
          <button 
            class="save-btn" 
            :disabled="content.trim().length === 0"
            @click="onSubmit"
          >
            저장
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  movieTitle: { type: String, default: '' },
  // ✅ [중요] 부모로부터 기존 리뷰 데이터 받기
  existingReview: { type: Object, default: null }
})
const emit = defineEmits(['close', 'submit', 'delete'])

const content = ref('')
const rating = ref(5)

// ✅ [중요] 모달 열릴 때 기존 데이터 채우기
onMounted(() => {
  if (props.existingReview) {
    content.value = props.existingReview.content || ''
    rating.value = props.existingReview.rating || 5
  }
})

function onSubmit() {
  if (content.value.trim().length > 0) {
    emit('submit', { content: content.value, rating: rating.value })
  }
}

// ✅ [추가] 삭제 핸들러
function onDelete() {
  if (confirm('정말 삭제하시겠습니까?')) {
    emit('delete', props.existingReview.id)
  }
}
</script>

<style scoped>
/* 기존 스타일 유지 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 2000; display: flex; align-items: center; justify-content: center; }
.modal-content { background: white; width: 600px; height: 500px; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
.modal-header { padding: 16px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 18px; font-weight: 700; color: #000; }
.close-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }
.modal-body { flex: 1; padding: 20px; display: flex; flex-direction: column; }
.rating-select-area { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #f5f5f5; }
.label { font-size: 14px; font-weight: 700; color: #333; }
.stars { display: flex; cursor: pointer; }
.star-icon { font-size: 24px; color: #e0e0e0; transition: color 0.2s; margin-right: 2px; }
.star-icon.active { color: #ffad1f; }
.rating-text { font-size: 14px; font-weight: 700; color: #ffad1f; margin-left: 4px; }
.review-input { width: 100%; flex: 1; border: none; outline: none; resize: none; font-size: 16px; line-height: 1.6; color: #333; }
.review-input::placeholder { color: #ccc; }

/* ✅ [수정] 푸터 레이아웃 (양쪽 정렬) */
.modal-footer { padding: 12px 20px; border-top: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }

/* ✅ [추가] 오른쪽 그룹 묶음 */
.right-group { display: flex; align-items: center; gap: 12px; }

/* ✅ [추가] 삭제 버튼 스타일 */
.delete-btn { background: none; border: none; color: #999; font-size: 14px; font-weight: 600; cursor: pointer; text-decoration: underline; }
.delete-btn:hover { color: #ff2f6e; }

.text-counter { font-size: 13px; color: #aaa; }
.save-btn { background: #ff2f6e; color: white; border: none; padding: 10px 24px; border-radius: 6px; font-weight: 700; font-size: 15px; cursor: pointer; transition: background 0.2s; }
.save-btn:disabled { background: #e0e0e0; color: #999; cursor: not-allowed; }
.save-btn:hover:not(:disabled) { background: #fa0050; }
@media (max-width: 768px) { .modal-content { width: 95%; height: 80vh; } }
</style>