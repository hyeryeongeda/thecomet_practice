<template>
  <div class="page">
    <h1 class="title">마이페이지</h1>

    <!-- 프로필 카드 -->
    <section class="card">
      <div class="profile">
        <div class="avatar">
          <img v-if="me?.profile_image" :src="me.profile_image" alt="profile" />
          <div v-else class="fallback">🚀</div>
        </div>

        <div class="info">
          <div class="row">
            <div class="name">{{ me?.username || '...' }}</div>
            <div class="email">{{ me?.email || '' }}</div>
          </div>

          <div class="counts">
            <button class="chip" @click="go(`/users/${me?.username}`)" :disabled="!me?.username">
              프로필 보기
            </button>
            <span class="sep">·</span>
            <span class="muted">팔로잉</span>
            <b>{{ me?.following_count ?? 0 }}</b>
            <span class="muted">팔로워</span>
            <b>{{ me?.followers_count ?? 0 }}</b>
          </div>

          <div class="actions">
            <button class="btn ghost" @click="openEdit = true">프로필 수정</button>
            <button class="btn" @click="logout">로그아웃</button>
          </div>
        </div>
      </div>
    </section>

    <!-- 탭 -->
    <section class="tabs">
      <button class="tab" :class="{ on: tab === 'reviews' }" @click="tab = 'reviews'">내 리뷰</button>
      <button class="tab" :class="{ on: tab === 'vault' }" @click="tab = 'vault'">보관함</button>
      <button class="tab" :class="{ on: tab === 'likes' }" @click="tab = 'likes'">좋아요</button>
    </section>

    <!-- 내 리뷰 -->
    <section v-if="tab === 'reviews'" class="section">
      <h2 class="h2">내 리뷰</h2>

      <p v-if="loadingReviews" class="muted">불러오는 중...</p>
      <p v-else-if="myReviews.length === 0" class="muted">아직 작성한 리뷰가 없습니다.</p>

      <div v-else class="list">
        <ReviewItem
          v-for="r in myReviews"
          :key="r.id"
          :review="r"
          :my-username="me?.username || ''"
          @click-user="goUser"
          @click-movie="goMovie"
          @toggle-like="toggleLike"
          @delete="removeReview"
        />
      </div>
    </section>

    <!-- 보관함 -->
    <section v-else-if="tab === 'vault'" class="section">
      <h2 class="h2">보관함</h2>
      <ComingSoonView />
    </section>

    <!-- 좋아요 -->
    <section v-else class="section">
      <h2 class="h2">좋아요</h2>
      <ComingSoonView />
    </section>

    <!-- 프로필 수정 모달 -->
    <BaseModal v-model:open="openEdit" title="프로필 수정">
      <div class="form">
        <label class="label">이메일</label>
        <input class="input" v-model.trim="edit.email" placeholder="email" />

        <label class="label">이름</label>
        <input class="input" v-model.trim="edit.name" placeholder="name" />

        <div class="modal-actions">
          <button class="btn ghost" @click="openEdit = false">닫기</button>
          <button class="btn" @click="saveProfile" :disabled="saving">
            {{ saving ? '저장 중...' : '저장' }}
          </button>
        </div>

        <p v-if="err" class="err">{{ err }}</p>
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchMe, updateMyProfile, toggleReviewLike, deleteReview } from '@/api/comet'
import ReviewItem from '@/components/review/ReviewItem.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import ComingSoonView from '@/views/ComingSoonView.vue'

const router = useRouter()
const auth = useAuthStore()

const tab = ref('reviews')

const me = ref(null)

const openEdit = ref(false)
const saving = ref(false)
const err = ref('')
const edit = ref({ email: '', name: '' })

const loadingReviews = ref(false)
const myReviews = ref([])

// ✅ 내 리뷰 API가 아직 없으면: "최근 리뷰"를 가져오는 임시 방식도 가능
// 근데 지금은 '내 리뷰' 엔드포인트를 백에 추가하는게 정석이라,
// 일단 프론트는 함수만 만들어두고 백이 있으면 바로 연결됨.
async function loadMe() {
  me.value = await fetchMe()
  edit.value.email = me.value?.email || ''
  edit.value.name = me.value?.name || ''
}

async function loadMyReviews() {
  loadingReviews.value = true
  try {
    // ✅ 백에 /api/reviews/my/ 같은게 있으면 그걸 쓰는게 베스트
    // 지금은 임시로 "내가 쓴 리뷰가 movie 정보 포함해서 오는 구조"라고 가정
    // 없으면, 다음 메시지에서 백 엔드포인트를 바로 만들어줄게.
    const res = await auth.api.get('/reviews/my/') // ⚠️ auth.api가 없다면 아래처럼 바꿔야 함
    myReviews.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (e) {
    // 엔드포인트 없으면 빈 리스트로 두고, 다음 단계에서 백 추가
    myReviews.value = []
  } finally {
    loadingReviews.value = false
  }
}

function go(path) {
  router.push(path)
}
function goUser(username) {
  router.push(`/users/${encodeURIComponent(username)}`)
}
function goMovie(tmdbId) {
  if (tmdbId) router.push(`/movies/${tmdbId}`)
}

async function toggleLike(reviewId) {
  try {
    const res = await toggleReviewLike(reviewId)
    const idx = myReviews.value.findIndex(r => r.id === reviewId)
    if (idx >= 0) {
      myReviews.value[idx] = {
        ...myReviews.value[idx],
        is_liked: res.liked,
        likes_count: res.likes_count,
      }
    }
  } catch (e) {
    alert(e?.response?.data?.detail || '좋아요 실패')
  }
}

async function removeReview(reviewId) {
  try {
    await deleteReview(reviewId)
    myReviews.value = myReviews.value.filter(r => r.id !== reviewId)
  } catch (e) {
    alert(e?.response?.data?.detail || '삭제 실패')
  }
}

async function saveProfile() {
  err.value = ''
  saving.value = true
  try {
    await updateMyProfile({
      email: edit.value.email,
      name: edit.value.name,
    })
    openEdit.value = false
    await loadMe()
  } catch (e) {
    err.value = e?.response?.data?.detail || '저장 실패'
  } finally {
    saving.value = false
  }
}

function logout() {
  auth.logout()
  router.push('/')
}

onMounted(async () => {
  await loadMe()
  await loadMyReviews()
})
</script>

<style scoped>
.page{ max-width:1100px; margin:0 auto; padding:20px 14px 60px; }
.title{ margin:0 0 12px; font-size:28px; font-weight:900; }
.card{ border:1px solid var(--border); background:var(--card); border-radius:16px; padding:16px; }
.profile{ display:flex; gap:14px; align-items:center; }
.avatar{ width:64px; height:64px; border-radius:18px; overflow:hidden; border:1px solid var(--border); background:var(--input-bg); display:flex; align-items:center; justify-content:center; }
.avatar img{ width:100%; height:100%; object-fit:cover; }
.fallback{ font-size:28px; }
.info{ flex:1; }
.row{ display:flex; align-items:baseline; gap:10px; }
.name{ font-size:18px; font-weight:900; }
.email{ color:var(--muted); font-weight:700; }
.counts{ margin-top:8px; display:flex; align-items:center; gap:8px; color:var(--text); }
.chip{ border:1px solid var(--border); background:var(--input-bg); border-radius:999px; padding:6px 10px; cursor:pointer; font-weight:900; }
.sep{ color:#bbb; }
.muted{ color:var(--muted); }
.actions{ margin-top:10px; display:flex; gap:8px; }

.btn{
  border:1px solid #111;
  background:#111;
  color:#fff;
  padding:8px 12px;
  border-radius:10px;
  cursor:pointer;
  font-weight:900;
}
.btn.ghost{ background:transparent; color:#111; border-color:var(--border); }

.tabs{ margin-top:14px; display:flex; gap:8px; }
.tab{ border:1px solid var(--border); background:var(--card); padding:10px 12px; border-radius:12px; cursor:pointer; font-weight:900; }
.tab.on{ border-color:#111; }

.section{ margin-top:14px; }
.h2{ margin:0 0 10px; font-size:18px; font-weight:900; }
.list{ display:flex; flex-direction:column; gap:10px; }

.form{ display:flex; flex-direction:column; gap:8px; }
.label{ font-weight:900; font-size:13px; color:var(--muted); margin-top:6px; }
.input{ padding:10px 12px; border-radius:12px; border:1px solid var(--border); background:var(--input-bg); color:var(--text); outline:none; }
.modal-actions{ margin-top:10px; display:flex; justify-content:flex-end; gap:8px; }
.err{ color:#ff4d4f; margin:8px 0 0; font-weight:800; }
</style>
