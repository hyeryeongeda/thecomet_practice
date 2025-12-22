<!-- frontend/src/components/recommend/RecommendUser.vue -->
<template>
  <section class="panel">
    <div class="head">
      <div>
        <h2 class="h2">[유저 추천]</h2>
        <p class="sub">취향이 비슷한 유저를 찾아 팔로우해보세요.</p>
      </div>

      <button class="ghost" type="button" @click="load" :disabled="loading">
        새로고침
      </button>
    </div>

    <div v-if="loading" class="loading">로딩중...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- ✅ 오늘의 유저 카드(시안 상단 큰 카드 느낌) -->
      <div v-if="spotlight" class="spotlight">
        <div class="avatar">👤</div>

        <div class="info">
          <p class="name">@{{ spotlight.username }}</p>
          <p class="desc">
            {{ spotlightDesc }}
          </p>

          <div class="stats">
            <span v-if="spotlight.reviews_count != null" class="pill"
              >리뷰 {{ spotlight.reviews_count }}</span
            >
            <span v-if="spotlight.received_likes != null" class="pill"
              >받은 좋아요 {{ spotlight.received_likes }}</span
            >
          </div>

          <div class="cta">
            <button class="btn" type="button" @click="goProfile(spotlight.username)">
              프로필 보기
            </button>

            <!-- suggested일 때만 팔로우 버튼 노출 -->
            <button
              v-if="spotlightSource === 'suggested'"
              class="btnOutline"
              type="button"
              :disabled="followLoadingMap[spotlight.username]"
              @click="follow(spotlight.username)"
            >
              {{ followLoadingMap[spotlight.username] ? '처리중...' : '팔로우' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ✅ 실시간 유저 랭킹(리뷰 TOP) -->
      <div class="section" v-if="topReviewers.length">
        <div class="sectionHead">
          <h3 class="h3">실시간 유저 활동 TOP</h3>
          <p class="hint">리뷰 작성이 많은 유저</p>
        </div>

        <div class="rankRow">
          <button
            v-for="(u, idx) in topReviewers"
            :key="u.id || u.username || idx"
            class="rankCard"
            type="button"
            @click="goProfile(u.username)"
          >
            <span class="rank">{{ idx + 1 }}</span>
            <div class="rankBody">
              <p class="rankName">@{{ u.username }}</p>
              <p class="rankMeta">리뷰 {{ u.reviews_count ?? 0 }}</p>
            </div>
          </button>
        </div>
      </div>

      <!-- ✅ 좋아요 TOP -->
      <div class="section" v-if="topLiked.length">
        <div class="sectionHead">
          <h3 class="h3">인기 유저 TOP</h3>
          <p class="hint">리뷰 좋아요를 많이 받은 유저</p>
        </div>

        <div class="rankRow">
          <button
            v-for="(u, idx) in topLiked"
            :key="u.id || u.username || idx"
            class="rankCard"
            type="button"
            @click="goProfile(u.username)"
          >
            <span class="rank">{{ idx + 1 }}</span>
            <div class="rankBody">
              <p class="rankName">@{{ u.username }}</p>
              <p class="rankMeta">받은 좋아요 {{ u.received_likes ?? 0 }}</p>
            </div>
          </button>
        </div>
      </div>

      <!-- ✅ 팔로우 추천(그리드) -->
      <div class="section" v-if="suggested.length">
        <div class="sectionHead">
          <h3 class="h3">팔로우 추천</h3>
          <p class="hint">아직 팔로우하지 않은 유저</p>
        </div>

        <div class="grid">
          <div v-for="u in suggested" :key="u.id || u.username" class="userCard">
            <div class="uTop">
              <div class="uAvatar">👤</div>
              <div class="uInfo">
                <p class="uName">@{{ u.username }}</p>
                <p class="uMeta">리뷰 {{ u.reviews_count ?? 0 }}</p>
              </div>
            </div>

            <div class="uActions">
              <button class="btnSmall" type="button" @click="goProfile(u.username)">
                프로필
              </button>
              <button
                class="btnSmallOutline"
                type="button"
                :disabled="followLoadingMap[u.username]"
                @click="follow(u.username)"
              >
                {{ followLoadingMap[u.username] ? '처리중...' : '팔로우' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <p v-if="!spotlight && !topReviewers.length && !topLiked.length && !suggested.length" class="empty">
        추천 유저가 아직 없어요.
      </p>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchUserRecommends, toggleFollow } from '@/api/comet'
// 1. Auth 스토어 임포트
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore() // 2. 스토어 사용

const loading = ref(false)
const error = ref('')
const payload = ref({
  top_reviewers: [],
  top_liked: [],
  suggested: [],
})

const followLoadingMap = ref({})

// 3. 내 이름 가져오기
const myName = computed(() => auth.user?.username)

// 4. 각 목록에서 나 자신(@username)을 제외하고 필터링
const topReviewers = computed(() => 
  (payload.value?.top_reviewers ?? []).filter(u => u.username !== myName.value)
)
const topLiked = computed(() => 
  (payload.value?.top_liked ?? []).filter(u => u.username !== myName.value)
)
const suggested = computed(() => 
  (payload.value?.suggested ?? []).filter(u => u.username !== myName.value)
)

// 상단 스포트라이트: 필터링된 목록을 기반으로 하므로 자동으로 나 자신이 제외됨
const spotlightSource = computed(() => {
  if (topLiked.value.length) return 'top_liked'
  if (topReviewers.value.length) return 'top_reviewers'
  if (suggested.value.length) return 'suggested'
  return ''
})

const spotlight = computed(() => {
  if (spotlightSource.value === 'top_liked') return topLiked.value[0]
  if (spotlightSource.value === 'top_reviewers') return topReviewers.value[0]
  if (spotlightSource.value === 'suggested') return suggested.value[0]
  return null
})

const spotlightDesc = computed(() => {
  if (!spotlight.value) return ''
  if (spotlightSource.value === 'top_liked') return '요즘 가장 인기 많은 유저예요. 리뷰 좋아요 반응이 좋아요.'
  if (spotlightSource.value === 'top_reviewers') return '리뷰 활동이 활발한 유저예요. 취향 참고하기 좋아요.'
  return '활동 유저 중 취향이 맞을 확률이 높은 유저를 추천했어요.'
})

function goProfile(username) {
  if (!username) return
  // ✅ 라우트 이름이 다르면 여기만 바꾸면 됨
  // (현재 프로젝트에서 /users/:username 형태면 아래가 가장 안전함)
  router.push(`/users/${encodeURIComponent(username)}`)
}

async function follow(username) {
  if (!username) return
  followLoadingMap.value = { ...followLoadingMap.value, [username]: true }
  try {
    await toggleFollow(username)
    // 팔로우 성공하면 suggested에서 제거(UX 깔끔)
    payload.value.suggested = (payload.value.suggested || []).filter((u) => u.username !== username)
  } catch (e) {
    console.error(e)
    alert('팔로우 처리 중 오류가 발생했어요.')
  } finally {
    followLoadingMap.value = { ...followLoadingMap.value, [username]: false }
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchUserRecommends()
    payload.value = res || { top_reviewers: [], top_liked: [], suggested: [] }
  } catch (e) {
    console.error(e)
    // 401이면 대부분 로그인/토큰 문제
    error.value = '유저 추천을 불러오지 못했어요. 로그인 상태/토큰을 확인해 주세요.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.panel {
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 16px;
  background: #fff;
}

.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
}
.sub {
  margin: 6px 0 0;
  color: #666;
  font-weight: 700;
}

.ghost {
  height: 34px;
  padding: 0 10px;
  border-radius: 12px;
  border: 1px solid #ddd;
  background: #fff;
  font-weight: 900;
  cursor: pointer;
}
.ghost:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading,
.error,
.empty {
  padding: 10px 0;
  font-weight: 800;
  color: #666;
}
.error {
  color: #b00020;
}

/* spotlight */
.spotlight {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 14px;
  border: 1px solid #eee;
  border-radius: 18px;
  padding: 14px;
  background: #fafafa;
  margin-bottom: 16px;
}
.avatar {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: #fff;
  border: 1px solid #eee;
  display: grid;
  place-items: center;
  font-size: 28px;
}
.info .name {
  margin: 0;
  font-weight: 900;
  font-size: 16px;
}
.info .desc {
  margin: 6px 0 0;
  color: #333;
  font-weight: 700;
  line-height: 1.45;
}
.stats {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pill {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid #e6e6e6;
  background: #fff;
  font-weight: 900;
  color: #111;
  font-size: 12px;
}
.cta {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}
.btn {
  height: 36px;
  padding: 0 12px;
  border-radius: 12px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-weight: 900;
  cursor: pointer;
}
.btnOutline {
  height: 36px;
  padding: 0 12px;
  border-radius: 12px;
  border: 1px solid #111;
  background: #fff;
  color: #111;
  font-weight: 900;
  cursor: pointer;
}
.btnOutline:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* sections */
.section {
  margin-top: 18px;
}
.sectionHead {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}
.h3 {
  margin: 0;
  font-weight: 900;
  font-size: 14px;
}
.hint {
  margin: 0;
  color: #888;
  font-weight: 800;
  font-size: 12px;
}

/* horizontal rank row */
.rankRow {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(160px, 200px);
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 6px;
}
.rankRow::-webkit-scrollbar {
  height: 8px;
}
.rankRow::-webkit-scrollbar-thumb {
  background: #e5e5e5;
  border-radius: 999px;
}

.rankCard {
  border: 1px solid #eee;
  background: #fff;
  border-radius: 16px;
  padding: 12px;
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 10px;
  text-align: left;
  cursor: pointer;
}
.rank {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  background: #111;
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 900;
  font-size: 12px;
}
.rankName {
  margin: 0;
  font-weight: 900;
}
.rankMeta {
  margin: 6px 0 0;
  color: #666;
  font-weight: 800;
  font-size: 12px;
}

/* suggested grid */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 560px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

.userCard {
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 12px;
  background: #fafafa;
}
.uTop {
  display: grid;
  grid-template-columns: 44px 1fr;
  gap: 10px;
  align-items: center;
}
.uAvatar {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: #fff;
  border: 1px solid #eee;
  display: grid;
  place-items: center;
}
.uName {
  margin: 0;
  font-weight: 900;
}
.uMeta {
  margin: 6px 0 0;
  color: #666;
  font-weight: 800;
  font-size: 12px;
}
.uActions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}
.btnSmall {
  height: 32px;
  padding: 0 10px;
  border-radius: 12px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-weight: 900;
  cursor: pointer;
}
.btnSmallOutline {
  height: 32px;
  padding: 0 10px;
  border-radius: 12px;
  border: 1px solid #111;
  background: #fff;
  color: #111;
  font-weight: 900;
  cursor: pointer;
}
.btnSmallOutline:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
