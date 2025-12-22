<template>
  <section class="profile-card">
    <div class="avatar-area">
      <div class="avatar">
        <img v-if="user?.profile_image" :src="getProfileImageUrl(user.profile_image)" alt="profile" />
        <div v-else class="fallback">👤</div>
      </div>
      <div class="names">
        <h1 class="username">{{ user?.username || '사용자' }}</h1>
        <button class="btn-edit" @click="$emit('edit')">프로필 수정</button>
      </div>
    </div>
    <div class="stats">
      <div class="stat-item"><span>팔로잉</span> <b>{{ user?.following_count || 0 }}</b></div>
      <div class="stat-item"><span>팔로워</span> <b>{{ user?.followers_count || 0 }}</b></div>
    </div>
  </section>
</template>

<script setup>

  // MyPageProfileCard.vue 또는 MyPageView.vue

/** ✅ 이미지 URL 보정 함수 */
function getProfileImageUrl(path) {
  if (!path) return null
  if (path.startsWith('http')) return path // 이미 풀 경로면 그대로 반환
  return `http://127.0.0.1:8000${path}` // 백엔드 서버 주소 합치기
}

defineProps({
  user: Object
})
defineEmits(['edit'])
</script>

<style scoped>
.profile-card { text-align: center; margin-bottom: 30px; }
.avatar-area { margin-bottom: 20px; }
.avatar { width: 100px; height: 100px; background: #eee; border-radius: 50%; margin: 0 auto 10px; overflow: hidden; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border); }
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.fallback { font-size: 40px; }
.names { margin-top: 10px; }
.username { font-size: 24px; font-weight: 900; margin-bottom: 10px; color: var(--text); }
.btn-edit { padding: 6px 12px; border: 1px solid var(--border); background: var(--card); border-radius: 4px; cursor: pointer; font-size: 13px; color: var(--text); }
.stats { display: flex; justify-content: center; gap: 20px; color: var(--muted); font-size: 14px; }
.stats b { color: var(--text); font-weight: 900; margin-left: 4px; }
</style>