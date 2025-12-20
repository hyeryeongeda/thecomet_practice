<template>
  <div class="wrap">
    <div class="divider">
      <span></span><p>OR</p><span></span>
    </div>

    <div class="icons">
      <button class="icon kakao" @click="social('kakao')" aria-label="kakao">K</button>
      <button class="icon google" @click="social('google')" aria-label="google">G</button>
      <button class="icon x" @click="social('x')" aria-label="x">X</button>
      <button class="icon apple" @click="social('apple')" aria-label="apple"></button>
      <button class="icon line" @click="social('line')" aria-label="line">L</button>
    </div>
  </div>
</template>

<script setup>
import api from '@/api/axios'

async function social(provider) {
  // 지금은 backend에서 501 placeholder로 응답하도록 만들어뒀던 endpoint
  try {
    await api.post(`/auth/social/${provider}/`)
  } catch (e) {
    alert(`${provider.toUpperCase()} 소셜 로그인은 다음 단계에서 실제 연동을 붙일 거야.`)
  }
}
</script>

<style scoped>
.wrap{ margin-top: 18px; }
.divider{
  display:flex; align-items:center; gap: 10px; margin: 16px 0;
  color: rgba(0,0,0,.5);
}
.divider span{ flex:1; height:1px; background: rgba(0,0,0,.15); }
.divider p{ font-size: 12px; margin:0; letter-spacing: .08em; }

.icons{ display:flex; justify-content:center; gap: 14px; margin-top: 8px; }
.icon{
  width: 44px; height: 44px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.12);
  background: #fff;
  display:flex; align-items:center; justify-content:center;
  font-weight: 900;
  cursor:pointer;
  transition: transform .15s ease;
}
.icon:hover{ transform: translateY(-2px); }

.kakao{ background:#FEE500; border-color: rgba(0,0,0,.06); }
.google{ background:#fff; }
.x{ background:#fff; }
.apple{ background:#000; color:#fff; border-color:#000; }
.line{ background:#06C755; color:#fff; border-color:#06C755; }
</style>
