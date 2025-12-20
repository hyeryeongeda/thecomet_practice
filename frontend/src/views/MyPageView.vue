<template>
  <div class="page">
    <h1 class="title">마이페이지</h1>

    <div v-if="loading" class="muted">로딩중...</div>

    <div v-else class="card">
      <div class="row">
        <img class="avatar" :src="me.profile_image || fallback" alt="profile" />
        <div class="info">
          <div class="name">{{ me.username }}</div>
          <div class="muted">{{ me.email }}</div>
          <div class="muted">팔로워 {{ me.followers_count }} · 팔로잉 {{ me.following_count }}</div>
        </div>
      </div>

      <div class="section">
        <h3>설정</h3>

        <label class="label">테마</label>
        <select class="input" v-model="theme" @change="onChangeTheme">
          <option value="white">White</option>
          <option value="netflix">Netflix</option>
          <option value="wavve">Wavve</option>
        </select>

        <button class="btn" @click="onLogout">로그아웃</button>
      </div>

      <div class="section">
        <h3>보관함 / 좋아요 분석</h3>
        <p class="muted">다음 단계에서 리뷰/보고싶은/봤던/장르 막대차트/좋아요 분석을 붙인다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { fetchMe, updateMyTheme } from '@/api/comet'

const auth = useAuthStore()

const loading = ref(true)
const me = ref({})
const theme = ref('white')
const fallback = 'https://placehold.co/96x96?text=%F0%9F%9A%80'

onMounted(async () => {
  loading.value = true
  const data = await fetchMe()
  me.value = data
  theme.value = data.theme || 'white'
  loading.value = false
})

async function onChangeTheme() {
  await updateMyTheme(theme.value)
  // 테마 적용은 theme store를 붙일 때 같이 처리하면 됨(다음 단계)
}

async function onLogout() {
  await auth.logout()
  location.href = '/'
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
.section{ margin-top: 16px; }
.label{ font-weight: 900; font-size: 13px; margin-top: 6px; display:block; }
.input{
  width: 100%;
  border: 1px solid var(--border);
  background: var(--input-bg);
  border-radius: 12px;
  padding: 10px 12px;
  margin-top: 6px;
}
.btn{
  margin-top: 10px;
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 12px;
  padding: 10px 12px;
  cursor:pointer;
  font-weight: 1000;
}
.btn:hover{ background: var(--primary-weak); }
</style>
