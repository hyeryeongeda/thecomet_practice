<template>
  <div class="page">
    <h1 class="title">유저 프로필</h1>

    <div v-if="loading" class="muted">로딩중...</div>

    <div v-else class="card">
      <div class="row">
        <img class="avatar" :src="user.profile_image || fallback" alt="profile" />
        <div class="info">
          <div class="name">{{ user.username }}</div>
          <div class="muted">{{ user.email }}</div>
          <div class="muted">팔로워 {{ user.followers_count }} · 팔로잉 {{ user.following_count }}</div>
        </div>
      </div>

      <div class="actions" v-if="canFollow">
        <button class="btn" @click="onToggleFollow">
          {{ isFollowing ? '언팔로우' : '팔로우' }}
        </button>
      </div>

      <p class="muted" style="margin-top: 12px;">
        다음 단계에서 이 유저의 리뷰 리스트/팔로워 목록 등을 붙인다.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchUserProfile, toggleFollow } from '@/api/comet'

const route = useRoute()
const auth = useAuthStore()

const loading = ref(true)
const user = ref({})
const isFollowing = ref(false)
const fallback = 'https://placehold.co/96x96?text=%F0%9F%91%A4'

const username = computed(() => route.params.username)

const canFollow = computed(() => {
  return auth.isAuthenticated && auth.user?.username && auth.user.username !== user.value.username
})

async function load() {
  loading.value = true
  const data = await fetchUserProfile(username.value)
  user.value = data
  isFollowing.value = !!data.is_following
  loading.value = false
}

onMounted(load)
watch(username, load)

async function onToggleFollow() {
  const res = await toggleFollow(username.value)
  isFollowing.value = res.is_following
  user.value.followers_count = res.followers_count
  user.value.following_count = res.following_count
}
</script>

<style scoped>
.page{ padding: 18px; }
.title{ margin: 0 0 12px; font-size: 28px; font-weight: 1000; }
.muted{ color: var(--muted); }
.card{
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 14px;
  background: var(--card);
  box-shadow: var(--shadow);
}
.row{ display:flex; gap: 12px; align-items:center; }
.avatar{ width: 72px; height: 72px; border-radius: 18px; object-fit: cover; border: 1px solid var(--border); }
.info .name{ font-weight: 1000; font-size: 18px; }
.actions{ margin-top: 12px; }
.btn{
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 12px;
  padding: 10px 12px;
  cursor:pointer;
  font-weight: 1000;
}
.btn:hover{ background: var(--primary-weak); }
</style>
