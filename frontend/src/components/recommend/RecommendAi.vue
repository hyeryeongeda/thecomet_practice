<template>
  <div class="panel">
    <div class="chat-box" ref="chatWindow">
      <div v-for="(m, idx) in chatMessages" :key="idx" class="msg" :class="m.role">
        <span class="bubble">{{ m.content }}</span>
      </div>
      <div v-if="chatLoading" class="msg assistant">
        <span class="bubble">추천 영화를 분석하고 있습니다... 🎬</span>
      </div>
    </div>

    <form class="input-row" @submit.prevent="sendChat">
      <input
        v-model="chatInput"
        class="input"
        placeholder="예) 겨울에 어울리는 따뜻한 로맨스 영화 추천해줘"
        :disabled="chatLoading"
      />
      <button class="btn" type="submit" :disabled="chatLoading || !chatInput.trim()">
        보내기
      </button>
    </form>

    <div v-if="chatMovies.length > 0" class="movie-section">
      <h3 class="result-title">AI 맞춤 추천 목록</h3>
      <div class="movie-grid">
        <button
          v-for="m in chatMovies"
          :key="m.tmdb_id"
          class="movie-card"
          type="button"
          @click="goMovie(m.tmdb_id)"
        >
          <div class="thumb">
            <img v-if="m.poster_path" :src="posterUrl(m.poster_path)" alt="poster" />
            <div v-else class="noimg">No Image</div>
          </div>
          <div class="mmeta">
            <p class="mtitle">{{ m.title }}</p>
            <p class="msub">★ {{ Number(m.vote_average || 0).toFixed(1) }}</p>
          </div>
        </button>
      </div>
    </div>
    
    <div v-else-if="!chatLoading && chatMessages.length > 1" class="empty-movies">
      해당하는 추천 영화 데이터를 찾을 수 없습니다. 다시 질문해 보세요!
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { postTasteChat } from '@/api/comet'

const router = useRouter()
const chatWindow = ref(null)

const chatMessages = ref([
  { role: 'assistant', content: '안녕하세요! 어떤 스타일의 영화를 찾으시나요? 분위기나 장르를 말씀해주세요.' },
])
const chatInput = ref('')
const chatLoading = ref(false)
const chatMovies = ref([])

// 포스터 URL 처리 (이미 전체 경로인 경우와 아닌 경우 구분)
function posterUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w342${path}`
}

function goMovie(tmdbId) {
  router.push({ name: 'movie-detail', params: { tmdbId } })
}

// 스크롤을 가장 아래로 내리는 함수
const scrollToBottom = async () => {
  await nextTick()
  if (chatWindow.value) {
    chatWindow.value.scrollTop = chatWindow.value.scrollHeight
  }
}

async function sendChat() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return

  // 1. 유저 메시지 추가 및 화면 갱신
  chatMessages.value.push({ role: 'user', content: text })
  chatInput.value = ''
  chatLoading.value = true
  await scrollToBottom()

  try {
    // 2. 대화 기록 정리 (API 전송용)
    const history = chatMessages.value.map((m) => ({ role: m.role, content: m.content }))
    
    // 3. API 호출
    const res = await postTasteChat({ message: text, history })
    console.log("AI 응답 데이터:", res) // 디버깅용: 여기서 데이터 구조를 꼭 확인하세요!

    // 4. AI 답변 추가
    const reply = res?.answer || '추천 결과입니다.'
    chatMessages.value.push({ role: 'assistant', content: reply })

    /**
     * 5. 영화 목록 처리 (정규화 로직 추가)
     * 백엔드에 따라 movies 혹은 results로 올 수 있으므로 둘 다 체크합니다.
     */
    const rawList = res?.movies || res?.results || []
    
    chatMovies.value = rawList.map(m => ({
      // id만 올 경우 tmdb_id로 변환해주는 방어 로직
      tmdb_id: m.tmdb_id || m.id,
      title: m.title || m.name || '제목 없음',
      poster_path: m.poster_path || '',
      vote_average: m.vote_average ?? 0
    })).filter(m => m.tmdb_id) // ID가 있는 것만 남김

  } catch (e) {
    console.error("AI 추천 에러:", e)
    chatMessages.value.push({ role: 'assistant', content: '죄송합니다. 서버와 연결이 원활하지 않습니다.' })
  } finally {
    chatLoading.value = false
    await scrollToBottom()
  }
}
</script>

<style scoped>
.panel { border: 1px solid #eee; border-radius: 16px; padding: 18px; background: #fff; }

.chat-box {
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 16px;
  background: #f9f9f9;
  height: 350px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 스크롤바 디자인 (선택사항) */
.chat-box::-webkit-scrollbar { width: 6px; }
.chat-box::-webkit-scrollbar-thumb { background: #ccc; border-radius: 10px; }

.msg { display: flex; }
.msg.user { justify-content: flex-end; }
.msg.assistant { justify-content: flex-start; }

.bubble {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.5;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.msg.user .bubble { background: #111; color: #fff; border-bottom-right-radius: 4px; }
.msg.assistant .bubble { background: #fff; color: #222; border: 1px solid #eee; border-bottom-left-radius: 4px; }

.input-row { margin-top: 15px; display: flex; gap: 10px; }
.input {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  border: 1px solid #ddd;
  padding: 0 15px;
  font-size: 14px;
  font-weight: 600;
}
.btn {
  width: 80px;
  border-radius: 12px;
  background: #111;
  color: #fff;
  font-weight: 900;
  cursor: pointer;
  border: none;
}
.btn:disabled { opacity: 0.4; }

.movie-section { margin-top: 25px; border-top: 2px solid #f5f5f5; pt: 20px; }
.result-title { font-size: 16px; font-weight: 900; margin-bottom: 15px; color: #333; }

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 15px;
}

.movie-card {
  border: 1px solid #eee;
  border-radius: 14px;
  background: #fff;
  padding: 8px;
  text-align: left;
  transition: transform 0.2s;
}
.movie-card:hover { transform: translateY(-5px); }

.thumb {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 10px;
  overflow: hidden;
  background: #eee;
}
.thumb img { width: 100%; height: 100%; object-fit: cover; }
.noimg { height: 100%; display: grid; place-items: center; color: #999; font-size: 12px; }

.mmeta { margin-top: 10px; padding: 0 4px; }
.mtitle { 
  margin: 0; 
  font-weight: 800; 
  font-size: 13px; 
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
}
.msub { margin: 4px 0 0; color: #ff9900; font-weight: 800; font-size: 12px; }

.empty-movies { 
  margin-top: 20px; 
  text-align: center; 
  color: #999; 
  font-size: 14px; 
  font-weight: 700; 
}
</style>