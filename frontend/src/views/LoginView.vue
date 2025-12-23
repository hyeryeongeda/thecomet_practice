<template>
  <div class="auth-backdrop">
    <div class="auth-card">
      <!-- 타이틀 -->
      <div class="brand">
        <img class="logo" :src="logoSrc" alt="혜성 로고" />
        <h1>혜성</h1>
      </div>

      <!-- 로그인 폼 -->
      <form class="form" @submit.prevent="onSubmit">
        <label class="label">아이디(Username)</label>
        <input
          v-model.trim="form.username"
          class="input"
          type="text"
          name="username"
          autocomplete="username"
          placeholder="user1"
        />

        <label class="label">비밀번호</label>
        <input
          v-model="form.password"
          class="input"
          type="password"
          name="password"
          autocomplete="current-password"
          placeholder="••••••••"
        />

        <button class="btn" type="submit" :disabled="loading">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>

        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <div class="footer">
        <p>
          아직 계정이 없나요?
          <a class="link" @click.prevent="goSignup">회원가입</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  username: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

const logoSrc = computed(() => new URL('@/assets/comet_logo.png', import.meta.url).href)

async function onSubmit() {
  error.value = ''
  loading.value = true

  try {
    // ✅ 여기 payload는 “반드시” 이런 형태여야 함
    const payload = {
      username: form.username,
      password: form.password,
    }

    // 디버그용(원하면 지워도 됨)
    console.log('LOGIN payload =>', payload)

    await auth.login(payload) // store에서 API 호출
    router.push('/') // 홈으로
  } catch (e) {
    const msg =
      e?.response?.data?.detail ||
      e?.response?.data?.message ||
      '로그인에 실패했습니다.'
    error.value = msg
  } finally {
    loading.value = false
  }
}

function goSignup() {
  router.push('/signup')
}

function onSocial(provider) {
  // 소셜은 다음 단계에서 실제 연동 붙이기
  alert(`${provider} 소셜 로그인은 다음 단계에서 연결할게요!`)
}
</script>

<style scoped>
.auth-backdrop {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, 0.6);
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.brand h1 {
  margin: 0;
  font-size: 20px;
}

.form {
  display: grid;
  gap: 10px;
}

.label {
  font-size: 12px;
  color: #555;
}

.input {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 12px;
  outline: none;
}

.input:focus {
  border-color: #aaa;
}

.btn {
  margin-top: 6px;
  padding: 12px;
  border-radius: 10px;
  border: 0;
  background: #111;
  color: #fff;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  margin: 8px 0 0;
  color: #d33;
  font-size: 13px;
}

.social {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 14px;
}

.social-btn {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #ddd;
  background: #fafafa;
  cursor: pointer;
}

.footer {
  margin-top: 16px;
  font-size: 13px;
  color: #666;
}

.link {
  color: #111;
  font-weight: 700;
  cursor: pointer;
  margin-left: 6px;
}
</style>
