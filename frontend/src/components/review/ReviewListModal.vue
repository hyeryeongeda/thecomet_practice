<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>코멘트 <span class="count">{{ reviews.length }}</span></h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      
      <div class="sort-bar">
        <select class="sort-select" :value="currentSort" @change="$emit('sort', $event.target.value)">
          <option value="likes">좋아요 순</option>
          <option value="latest">최신 순</option>
        </select>
      </div>

      <div class="modal-body list-body">
        <div 
          v-for="review in reviews" 
          :key="review.id" 
          class="comment-item"
          @click="$emit('select', review)"
        >
          <div class="item-header">
            <div class="user">
              <img v-if="review.user.profile_image" :src="review.user.profile_image" class="u-img">
              <div v-else class="u-icon">👤</div>
              <span class="name">{{ review.user.username }}</span>
            </div>
            <div class="rating">★ {{ review.rating }}</div>
          </div>
          <div class="item-content">{{ review.content }}</div>
          <div class="item-footer">
            <span>👍 {{ review.likes_count }}</span>
            <span>💬 {{ review.comments_count || 0 }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  reviews: { type: Array, default: () => [] },
  currentSort: { type: String, default: 'likes' }
})
defineEmits(['close', 'sort', 'select'])
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 2000;
  display: flex; align-items: center; justify-content: center;
}
.modal-content {
  background: white; width: 600px; height: 80vh; border-radius: 12px;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

/* 헤더 */
.modal-header {
  padding: 16px 20px; border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center;
}
.modal-header h3 { margin: 0; font-size: 18px; font-weight: 700; }
.count { color: #ff2f6e; margin-left: 6px; }
.close-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }

/* 정렬 바 */
.sort-bar {
  padding: 10px 20px; border-bottom: 1px solid #f5f5f5; background: #fff;
  text-align: right;
}
.sort-select {
  padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px;
  font-size: 13px; color: #555; outline: none; cursor: pointer;
}

/* 리스트 바디 */
.list-body { flex: 1; overflow-y: auto; padding: 20px; background: #f8f8f8; }

/* 리뷰 아이템 (카드 스타일) */
.comment-item {
  background: white; border-radius: 8px; padding: 16px; margin-bottom: 12px;
  border: 1px solid #eee; cursor: pointer; transition: all 0.2s;
}
.comment-item:hover { border-color: #ccc; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

.item-header { display: flex; justify-content: space-between; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #f9f9f9; }
.user { display: flex; align-items: center; gap: 8px; }
.u-img { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
.u-icon { font-size: 24px; }
.name { font-size: 14px; font-weight: 700; color: #333; }
.rating { font-size: 13px; background: #eee; padding: 2px 8px; border-radius: 12px; font-weight: 600; }

.item-content { font-size: 15px; color: #444; line-height: 1.5; margin-bottom: 12px; white-space: pre-wrap; }
.item-footer { font-size: 13px; color: #888; display: flex; gap: 16px; }

@media (max-width: 768px) {
  .modal-content { width: 100%; height: 100vh; border-radius: 0; }
}
</style>