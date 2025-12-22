<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <div class="user-profile">
          <img v-if="review.user.profile_image" :src="review.user.profile_image" class="u-img">
          <div v-else class="u-icon">👤</div>
          <span class="u-name">{{ review.user.username }}</span>
        </div>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div class="modal-body">

        <div class="review-meta-row">
          <div class="small-poster" v-if="posterUrl" @click="goToMovieDetail">
            <img :src="posterUrl" alt="Poster">
          </div>

          <div class="meta-info">
            <div class="movie-title" v-if="review.movie" @click="goToMovieDetail">
              {{ review.movie.title }}
            </div>
            <div class="rating-date">
              <span class="star">★ {{ review.rating }}</span>
              <span class="date">{{ formatDate(review.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="review-content">
          {{ review.content }}
        </div>

        <div class="action-bar">
          <button
            class="action-btn"
            :class="{ active: review.is_liked }"
            @click="$emit('toggle-like', review.id)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
            좋아요 {{ review.likes_count }}
          </button>

          <div class="action-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path fill-rule="evenodd" d="M4.804 21.644A6.707 6.707 0 006 21.75a6.721 6.721 0 003.583-1.029c.774.182 1.584.279 2.417.279 5.322 0 9.75-3.97 9.75-9 0-5.03-4.428-9-9.75-9s-9.75 3.97-9.75 9c0 2.409 1.025 4.562 2.632 6.19l-2.484 3.032.006.003zM12 12.75a.75.75 0 01-.75-.75V9a.75.75 0 011.5 0v3a.75.75 0 01-.75.75zm0-6a.75.75 0 01.75-.75h.008a.75.75 0 01.75.75v.008a.75.75 0 01-.75.75H12a.75.75 0 01-.75-.75V6.75z" clip-rule="evenodd" />
            </svg>
            댓글 {{ replies.length }}
          </div>
        </div>

        <div class="divider"></div>

        <div class="replies-list">
          <div v-for="reply in replies" :key="reply.id" class="reply-item">
            <div class="r-head">
              <span class="r-user">{{ reply.user.username }}</span>
              <div class="r-right">
                <span class="r-date">{{ formatDate(reply.created_at) }}</span>
                <button
                  v-if="authStore.user?.id === reply.user.id"
                  class="del-reply-btn"
                  @click="onDeleteReply(reply.id)"
                >삭제</button>
              </div>
            </div>
            <div class="r-body">{{ reply.content }}</div>
          </div>
          <div v-if="replies.length === 0" class="no-replies">
            아직 댓글이 없습니다.
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <input
          type="text"
          v-model="replyText"
          class="reply-input"
          placeholder="댓글을 작성해주세요..."
          @keyup.enter="onSubmit"
        />
        <button class="submit-btn" :disabled="!replyText.trim()" @click="onSubmit">등록</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { deleteReviewComment } from '@/api/comet'

const props = defineProps({
  review: { type: Object, required: true },
  replies: { type: Array, default: () => [] },
  movie: { type: Object, default: null }
})

// ✅ delete-reply 이벤트만 추가 (기존 건드리지 않음)
const emit = defineEmits(['close', 'submit-reply', 'toggle-like', 'delete-reply'])

const router = useRouter()
const authStore = useAuthStore()
const replyText = ref('')

const posterUrl = computed(() => {
  const m = props.review.movie || props.movie
  if (m?.poster_path) return `https://image.tmdb.org/t/p/w200${m.poster_path}`
  return null
})

function onSubmit() {
  if (replyText.value.trim()) {
    emit('submit-reply', replyText.value)
    replyText.value = ''
  }
}

async function onDeleteReply(commentId) {
  if (!confirm('댓글을 삭제하시겠습니까?')) return
  try {
    await deleteReviewComment(commentId)
    // ✅ 여기 핵심: 부모에게 "이 id 지웠다" 알려서 즉시 화면에서 제거
    emit('delete-reply', commentId)
  } catch (e) {
    alert('삭제 실패')
  }
}

function goToMovieDetail() {
  const m = props.review.movie || props.movie
  if (m) {
    router.push(`/movies/${m.tmdb_id || m.id}`)
    emit('close')
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  const d = new Date(dateString)
  return `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}`
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 9999;
  display: flex; align-items: center; justify-content: center;
}

.modal-card {
  width: 600px; height: 700px; background: white; border-radius: 12px;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

/* 1. 헤더 */
.modal-header {
  height: 60px; padding: 0 20px; border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;
}
.user-profile { display: flex; align-items: center; gap: 10px; }
.u-img { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; }
.u-icon { font-size: 28px; color: #ccc; }
.u-name { font-weight: 700; font-size: 15px; color: #333; }
.close-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }

/* 2. 본문 */
.modal-body { flex: 1; overflow-y: auto; padding: 20px; }

/* 메타 정보 (포스터 + 제목/별점) */
.review-meta-row { display: flex; gap: 16px; margin-bottom: 16px; }
.small-poster {
  width: 60px; height: 90px; border-radius: 4px; overflow: hidden;
  flex-shrink: 0; cursor: pointer; background: #eee;
}
.small-poster img { width: 100%; height: 100%; object-fit: cover; }
.meta-info { display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.movie-title { font-weight: 700; font-size: 16px; color: #333; cursor: pointer; }
.movie-title:hover { text-decoration: underline; }
.rating-date { font-size: 13px; color: #888; display: flex; gap: 8px; }
.star { color: #ffad1f; font-weight: 700; }

/* 리뷰 텍스트 */
.review-content {
  font-size: 15px; line-height: 1.6; color: #333; margin-bottom: 20px; white-space: pre-wrap;
}

/* 액션 바 */
.action-bar {
  display: flex; gap: 16px; align-items: center; padding-bottom: 16px;
}
.action-btn, .action-item {
  display: flex; align-items: center; gap: 6px; font-size: 13px; color: #777;
  background: none; border: none; padding: 0; cursor: pointer;
}
.action-item { cursor: default; }
.action-btn:hover { color: #333; }
.action-btn.active { color: #ff2f6e; font-weight: 700; }

.divider { height: 1px; background: #f0f0f0; margin-bottom: 16px; }

/* 대댓글 리스트 */
.replies-list { display: flex; flex-direction: column; gap: 16px; }
.no-replies { text-align: center; color: #ccc; padding: 20px 0; font-size: 13px; }
.reply-item { background: #f9f9f9; padding: 12px; border-radius: 8px; }
.r-head { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px; }
.r-user { font-weight: 700; color: #444; }
.r-right { display: flex; align-items: center; gap: 8px; }
.r-date { color: #aaa; }
.del-reply-btn { font-size: 11px; color: #999; border: none; background: none; cursor: pointer; text-decoration: underline; padding: 0; }
.del-reply-btn:hover { color: #ff2f6e; }
.r-body { font-size: 14px; color: #333; line-height: 1.4; }

/* 3. 하단 푸터 (입력창) */
.modal-footer {
  height: 70px; padding: 0 20px; border-top: 1px solid #eee;
  display: flex; align-items: center; gap: 10px; background: #fff; flex-shrink: 0;
}
.reply-input {
  flex: 1; padding: 12px 16px; border: 1px solid #ddd; border-radius: 99px;
  outline: none; font-size: 14px; background: #f8f8f8;
}
.reply-input:focus { background: white; border-color: #bbb; }
.submit-btn {
  background: #e0e0e0; color: #777; border: none; padding: 10px 20px;
  border-radius: 99px; font-weight: 700; cursor: default; transition: all 0.2s;
}
.submit-btn:not(:disabled) { background: #ff2f6e; color: white; cursor: pointer; }
.submit-btn:not(:disabled):hover { background: #fa0050; }

@media (max-width: 600px) {
  .modal-card { width: 95%; height: 80vh; }
}
</style>
