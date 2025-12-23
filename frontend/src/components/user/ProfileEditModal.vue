<template>
  <BaseModal :open="true" title="프로필 수정" @close="$emit('close')">
    <div class="form">
      
      <div class="image-edit">
        <div class="avatar-preview">
          <img :src="previewUrl || user?.profile_image || '/default-avatar.png'" />
        </div>
        <input type="file" ref="fileInput" @change="onFileChange" accept="image/*" hidden />
        <button class="btn-sub" @click="$refs.fileInput.click()">사진 변경</button>
      </div>

      <label class="label">아이디</label>
      <input class="input readonly" :value="user?.username" readonly />

      <label class="label">이름</label>
      <input class="input" v-model="form.name" placeholder="이름을 입력하세요" />

      <hr class="divider" />
      <h4 class="sub-title">비밀번호 변경</h4>
      
      <label class="label">현재 비밀번호</label>
      <input class="input" v-model="form.old_password" type="password" placeholder="기존 비밀번호" />

      <label class="label">새 비밀번호</label>
      <input class="input" v-model="form.new_password" type="password" placeholder="새 비밀번호 (선택)" />

      <div class="modal-actions">
        <button class="btn ghost" @click="$emit('close')">취소</button>
        <button class="btn" @click="handleSave" :disabled="loading">
          {{ loading ? '저장 중...' : '저장하기' }}
        </button>
      </div>

      <p v-if="error" class="err-msg">{{ error }}</p>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { updateMyProfile } from '@/api/comet'

// ✅ [에러 해결 핵심] BaseModal을 반드시 임포트해야 합니다!
import BaseModal from '@/components/ui/BaseModal.vue'

const props = defineProps({
  user: Object
})
const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const error = ref('')
const previewUrl = ref(null)
const selectedFile = ref(null)

const form = reactive({
  name: props.user?.name || '',
  old_password: '',
  new_password: '',
})

// 사진 변경 시 미리보기 생성
function onFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

async function handleSave() {
  loading.value = true
  error.value = ''

  // 파일 업로드를 위해 FormData 사용
  const formData = new FormData()
  formData.append('name', form.name)
  
  if (selectedFile.value) {
    formData.append('profile_image', selectedFile.value)
  }
  
  // 비밀번호 변경 요청이 있는 경우
  if (form.old_password && form.new_password) {
    formData.append('old_password', form.old_password)
    formData.append('new_password', form.new_password)
  }

  try {
    const updatedUser = await updateMyProfile(formData)
    emit('saved', updatedUser)
    emit('close')
  } catch (err) {
    // 백엔드에서 보낸 에러 메시지(예: 현재 비밀번호 불일치) 표시
    error.value = err.response?.data?.detail || '수정에 실패했습니다. 정보를 확인해 주세요.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 🎨 레이아웃 구조는 유지하고 색상만 테마 변수로 교체 */

.form { display: flex; flex-direction: column; gap: 10px; padding: 10px; }
.image-edit { display: flex; flex-direction: column; align-items: center; gap: 10px; margin-bottom: 15px; }

.avatar-preview { 
  width: 90px; height: 90px; 
  border-radius: 50%; overflow: hidden; 
  border: 2px solid var(--border); /* #f0f0f0 -> var(--border) */
  background: var(--bg);
}
.avatar-preview img { width: 100%; height: 100%; object-fit: cover; }

.btn-sub { 
  font-size: 12px; padding: 4px 8px; cursor: pointer; 
  background: var(--bg); /* #eee -> var(--bg) */
  border: 1px solid var(--border); /* #ddd -> var(--border) */
  border-radius: 4px; 
  color: var(--text);
  transition: background 0.2s;
}
.btn-sub:hover {
  background: var(--primary-weak);
}

.label { 
  font-size: 13px; font-weight: 800; 
  color: var(--muted); /* #666 -> var(--muted) */
  margin-top: 5px; 
}

.input { 
  padding: 10px; border-radius: 8px; 
  border: 1px solid var(--border); /* #ddd -> var(--border) */
  background: var(--input-bg);    /* 배경 대응 */
  color: var(--text);             /* 글자색 대응 */
  outline: none;
  transition: border-color 0.2s;
}
.input:focus {
  border-color: var(--primary);
}

/* 읽기 전용 상태 (아이디 등) */
.input.readonly { 
  background: var(--primary-weak); /* #f9f9f9 -> var(--primary-weak) */
  color: var(--muted);            /* #999 -> var(--muted) */
  border-color: var(--border);
  opacity: 0.7;
  outline: none; 
}

.divider { 
  margin: 15px 0; border: 0; 
  border-top: 1px solid var(--border); /* #eee -> var(--border) */
}

.sub-title { 
  font-size: 14px; font-weight: 900; margin-bottom: 5px; 
  color: var(--text);
}

.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

.btn { 
  padding: 10px 20px; border-radius: 8px; font-weight: 800; cursor: pointer; 
  border: 1px solid var(--primary); /* #111 -> var(--primary) */
  transition: all 0.2s;
}

/* 취소 버튼 스타일 */
.btn.ghost { 
  background: var(--card); /* #fff -> var(--card) */
  color: var(--text);      /* #111 -> var(--text) */
  border-color: var(--border);
}
.btn.ghost:hover {
  background: var(--bg);
}

/* 저장 버튼 스타일 */
.btn:not(.ghost) { 
  background: var(--primary); /* #111 -> var(--primary) */
  color: #ffffff;             /* 버튼 위 글자는 흰색 고정 */
}
.btn:not(.ghost):hover {
  filter: brightness(1.1);
  box-shadow: var(--shadow);
}

.err-msg { 
  color: #ff4d4f; /* 에러 색상은 유지하되 테마별 가독성 확인 */
  font-size: 12px; text-align: center; margin-top: 10px; font-weight: 700; 
}
</style>