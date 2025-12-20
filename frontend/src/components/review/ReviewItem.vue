<template>
  <div class="card">
    <div class="top">
      <!-- 유저 프로필 이동 -->
      <button class="user" @click="goUser">@{{ username }}</button>

      <span class="dot">·</span>
      <span class="meta">{{ createdAtText }}</span>

      <span class="spacer"></span>

      <span v-if="rating" class="rating">★ {{ rating }}</span>
    </div>

    <!-- 보기 모드 -->
    <template v-if="!editing">
      <p class="content">{{ content }}</p>

      <div class="actions">
        <!-- 좋아요(내 리뷰면 숨김) -->
        <button
          v-if="auth.isLoggedIn && !isMine"
          class="btn ghost"
          @click="onToggleLike"
          :disabled="liking"
        >
          {{ liked ? '❤️' : '🤍' }} {{ likeCount }}
        </button>

        <span class="spacer"></span>

        <!-- 내 리뷰면 수정/삭제 -->
        <template v-if="isMine">
          <button class="btn ghost" @click="startEdit">수정</button>
          <button class="btn danger" @click="onDelete" :disabled="deleting">
            {{ deleting ? '삭제중...' : '삭제' }}
          </button>
        </template>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
    </template>

    <!-- 수정 모드 -->
    <template v-else>
      <div class="edit-row">
        <label class="check">
          <input type="checkbox" v-model="form.watched" />
          <span>봤어요</span>
        </label>

        <div class="rating-select">
          <span class="label">별점</span>
          <select v-model.number="form.rating" class="select">
            <option :value="0">선택</option>
            <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
          </select>
        </div>
      </div>

      <textarea
        v-model.trim="form.content"
        class="textarea"
        maxlength="200"
        placeholder="한줄평 (최대 200자)"
      />

      <div class="actions">
        <button class="btn" @click="saveEdit" :disabled="saving">
          {{ saving ? '저장중...' : '저장' }}
        </button>
        <button class="btn ghost" @click="cancelEdit" :disabled="saving">취소</button>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
    </template>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useReviewStore } from '@/stores/review'
import { updateReview, deleteReview, toggleReviewLike } from '@/api/comet'

const props = defineProps({
  review: { type: Object, required: true },
})

const router = useRouter()
const auth = useAuthStore()
const reviewStore = useReviewStore()

const myUsername = computed(() => auth.user?.username || '')

const username = computed(() => {
  const r = props.review || {}
  return r.user?.username || r.username || 'unknown'
})

const isMine = computed(() => username.value && username.value === myUsername.value)

const rating = computed(() => props.review?.rating ?? '')
const content = computed(() => props.review?.content ?? '')

const createdAtText = computed(() => {
  const v = props.review?.created_at
  if (!v) return ''
  // 대충 표시 (필요하면 format utils로 빼도 됨)
  return String(v).slice(0, 10)
})

const likeCount = ref(props.review?.like_count ?? 0)
const liked = ref(!!props.review?.is_liked)

watch(
  () => props.review,
  (r) => {
    likeCount.value = r?.like_count ?? 0
    liked.value = !!r?.is_liked
  },
  { deep: true }
)

const editing = ref(false)
const saving = ref(false)
const deleting = ref(false)
const liking = ref(false)
const error = ref('')

const form = reactive({
  watched: false,
  rating: 0,
  content: '',
})

function goUser() {
  // ✅ 유저 프로필 라우트가 /users/:username 이라는 전제
  router.push(`/users/${encodeURIComponent(username.value)}`)
}

function startEdit() {
  error.value = ''
  form.watched = !!props.review?.watched
  form.rating = Number(props.review?.rating || 0)
  form.content = props.review?.content || ''
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  error.value = ''
}

async function saveEdit() {
  error.value = ''

  if (!form.watched) {
    error.value = "리뷰 수정도 '봤어요' 체크가 필요합니다."
    return
  }
  if (!form.rating) {
    error.value = '별점은 필수입니다.'
    return
  }
  if (!form.content) {
    error.value = '한줄평을 입력해 주세요.'
    return
  }

  saving.value = true
  try {
    await updateReview(props.review.id, {
      watched: true,
      rating: form.rating,
      content: form.content,
    })
    editing.value = false
    reviewStore.bumpReload()
  } catch (e) {
    error.value = e?.response?.data?.detail || '수정 실패'
  } finally {
    saving.value = false
  }
}

async function onDelete() {
  error.value = ''
  if (!confirm('리뷰를 삭제할까요?')) return

  deleting.value = true
  try {
    await deleteReview(props.review.id)
    reviewStore.bumpReload()
  } catch (e) {
    error.value = e?.response?.data?.detail || '삭제 실패'
  } finally {
    deleting.value = false
  }
}

async function onToggleLike() {
  error.value = ''
  liking.value = true
  try {
    const res = await toggleReviewLike(props.review.id)
    liked.value = !!res?.liked
    likeCount.value = Number(res?.like_count ?? likeCount.value)
  } catch (e) {
    error.value = e?.response?.data?.detail || '좋아요 실패'
  } finally {
    liking.value = false
  }
}
</script>

<style scoped>
.card{
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 14px;
  padding: 12px 14px;
}
.top{
  display:flex;
  align-items:center;
  gap: 8px;
}
.user{
  border:none;
  background:transparent;
  padding:0;
  cursor:pointer;
  font-weight: 900;
  color: var(--text);
}
.dot{ color: var(--muted); }
.meta{ color: var(--muted); font-size: 13px; }
.spacer{ flex:1; }
.rating{ font-weight: 900; }

.content{
  margin: 10px 0 0;
  color: var(--text);
  line-height: 1.45;
  white-space: pre-wrap;
}

.actions{
  display:flex;
  align-items:center;
  gap: 10px;
  margin-top: 10px;
}

.btn{
  border: 1px solid var(--border);
  background: var(--text);
  color: var(--bg);
  padding: 8px 12px;
  border-radius: 10px;
  cursor:pointer;
  font-weight: 900;
}
.btn.ghost{
  background: transparent;
  color: var(--text);
}
.btn.danger{
  background: transparent;
  color: #ff4d4f;
  border-color: #ffb3b6;
}

.edit-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 10px;
  margin-top: 10px;
}
.check{ display:flex; align-items:center; gap: 8px; font-weight: 900; }
.rating-select{ display:flex; align-items:center; gap: 8px; }
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

.error{ color: #ff4d4f; margin: 10px 0 0; font-size: 13px; }
</style>
