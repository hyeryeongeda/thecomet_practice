<template>
  <div class="ai-recommend-layout">
    <aside class="chat-sidebar">
      <div class="sidebar-top">
        <h2 class="sidebar-title">채팅 목록</h2>
        <button class="new-chat-btn" @click="createNewChat" title="새로운 대화 시작">
          + 새 채팅
        </button>
      </div>
      
      <div class="chat-history-list">
        <div 
          v-for="(chat, idx) in allChats" 
          :key="chat.id" 
          class="history-item" 
          :class="{ active: currentChatIndex === idx }"
          @click="selectChat(idx)"
        >
          <p class="history-text">{{ chat.title || '새로운 대화' }}</p>
          <button class="delete-chat" @click.stop="deleteChat(idx)">×</button>
        </div>
      </div>
    </aside>

    <div class="main-panel">
      <div class="chat-layout-wrapper">
        
        <div class="chat-display" ref="chatWindow">
          <div v-for="(m, idx) in currentChat.messages" :key="idx" class="message-group">
            
            <div :class="['msg-row', m.role]">
              <div v-if="m.role === 'assistant'" class="bot-icon">🤖</div>
              <div class="bubble">{{ m.content }}</div>
            </div>

            <div v-if="m.movies && m.movies.length" class="movie-results-in-chat">
              <div 
                v-for="movie in m.movies" 
                :key="movie.tmdb_id" 
                class="horizontal-card"
                @click="goMovie(movie.tmdb_id)"
              >
                <div class="poster-box">
                  <img :src="posterUrl(movie.poster_path)" :alt="movie.title" loading="lazy" />
                </div>

                <div class="info-box">
                  <div class="info-top">
                    <h4 class="m-title">{{ movie.title }}</h4>
                    <span class="stars">★ {{ movie.vote_average ? movie.vote_average.toFixed(1) : '0.0' }}</span>
                  </div>

                  <div class="ai-reason-box" v-if="movie.ai_reason">
                    <span class="check-icon">✔</span>
                    <p class="reason-text">{{ movie.ai_reason }}</p>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <div v-if="chatLoading" class="msg-row assistant">
            <div class="bot-icon">🤖</div>
            <div class="bubble loading">열심히 영화를 찾고 있어요... 🎬</div>
          </div>
        </div>

        <section class="input-section">
          <div class="input-container">
            <textarea 
              v-model="chatInput" 
              placeholder="어떤 영화를 추천해드릴까요?"
              @keypress.enter.prevent="sendChat"
              :disabled="chatLoading"
            ></textarea>
            <button class="send-btn" @click="sendChat" :disabled="chatLoading || !chatInput.trim()">
              보내기
            </button>
          </div>

          <div class="quick-tags">
            <button v-for="tag in ['비 오는 날 감성', '코믹', '설레는 로맨스']" :key="tag" @click="chatInput = tag" class="tag-btn">
              {{ tag }}
            </button>
          </div>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { postTasteChat } from '@/api/comet'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const chatWindow = ref(null)

const allChats = ref([]) 
const currentChatIndex = ref(0) 
const chatInput = ref('')
const chatLoading = ref(false)
const authStore = useAuthStore()

const currentChat = computed(() => {
  return allChats.value[currentChatIndex.value] || { messages: [], title: '' }
})

const posterUrl = (p) => p ? `https://image.tmdb.org/t/p/w200${p}` : ''
const goMovie = (id) => router.push({ name: 'movie-detail', params: { tmdbId: id } })

const scrollToBottom = async () => { 
  await nextTick()
  if (chatWindow.value) {
    chatWindow.value.scrollTop = chatWindow.value.scrollHeight 
  }
}

onMounted(() => {
  const savedData = localStorage.getItem('comet_ai_history')
  if (savedData) {
    allChats.value = JSON.parse(savedData)
  } else {
    createNewChat()
  }
})

watch(allChats, (newVal) => {
  localStorage.setItem('comet_ai_history', JSON.stringify(newVal))
}, { deep: true })

function createNewChat() {
  const newChat = {
    id: Date.now(),
    title: '',
    messages: [{ role: 'assistant', content: '안녕하세요! 원하시는 영화의 분위기나 특징을 말씀해 주세요.', movies: [] }],
  }
  allChats.value.unshift(newChat)
  currentChatIndex.value = 0
  chatInput.value = ''
}

function selectChat(idx) {
  currentChatIndex.value = idx
  scrollToBottom()
}

function deleteChat(idx) {
  if (confirm('이 대화 내역을 삭제하시겠습니까?')) {
    allChats.value.splice(idx, 1)
    if (allChats.value.length === 0) createNewChat()
    else currentChatIndex.value = 0
  }
}

async function sendChat() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return

  const target = allChats.value[currentChatIndex.value]
  if (!target.title) target.title = text.substring(0, 10) + (text.length > 10 ? '...' : '')

  // 내 메시지 추가
  target.messages.push({ role: 'user', content: text, movies: [] })
  chatInput.value = ''
  chatLoading.value = true
  await scrollToBottom()

  try {
    const history = target.messages.map(m => ({ role: m.role, content: m.content }))
    const res = await postTasteChat({ message: text, history })

    const rawMovies = res.movies || []
    const reasons = res.recommended_reasons || {}
    
    // 👇 [핵심 수정] 영화 데이터를 메시지 안에 포함시킴
    const processedMovies = rawMovies.map(m => ({
      ...m,
      tmdb_id: m.tmdb_id || m.id,
      // 👇 [핵심 수정] 이유 매칭 로직 수정 (ID 기준)
      ai_reason: reasons[m.tmdb_id] || reasons[String(m.tmdb_id)] || reasons[m.id]
    }))

    target.messages.push({ 
      role: 'assistant', 
      content: res.answer, 
      movies: processedMovies // 영화 목록을 이 메시지에 붙임!
    })

  } catch (e) {
    target.messages.push({ role: 'assistant', content: '죄송합니다. 서버와 통신 중 오류가 발생했습니다.', movies: [] })
  } finally {
    chatLoading.value = false
    await scrollToBottom()
  }
}

//  로그인 유저별 저장 키
const storageKey = computed(() => {
  const u = authStore.user
  const keyPart = u?.id ?? u?.username
  return keyPart ? `comet_ai_history_${keyPart}` : null
})

function loadChats() {
  if (!storageKey.value) return
  const saved = localStorage.getItem(storageKey.value)
  if (saved) {
    allChats.value = JSON.parse(saved)
    currentChatIndex.value = 0
  } else {
    allChats.value = []
    createNewChat()
  }
}

watch(storageKey, (k) => {
  if (!k) return
  loadChats()
}, { immediate: true })

watch(allChats, (newVal) => {
  if (!storageKey.value) return
  localStorage.setItem(storageKey.value, JSON.stringify(newVal))
}, { deep: true })
</script>

<style scoped>
.ai-recommend-layout { display: flex; gap: 20px; max-width: 1100px; margin: 0 auto; height: 650px; }

/* 왼쪽 사이드바 */
.chat-sidebar { width: 220px; border: 1px solid var(--border); border-radius: 16px; padding: 15px; display: flex; flex-direction: column; background: var(--card); }
.sidebar-top { margin-bottom: 20px; }
.sidebar-title { font-size: 16px; font-weight: 900; margin-bottom: 12px; color: var(--text); }
.new-chat-btn { width: 100%; padding: 10px; background: var(--primary); color: #fff; border: none; border-radius: 10px; font-weight: 800; cursor: pointer; transition: 0.2s; }
.new-chat-btn:hover { opacity: 0.8; }
.chat-layout-wrapper {  display: flex;  flex-direction: column;  height: 100%;  gap: 20px;}
.chat-history-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.history-item { padding: 10px; border-radius: 8px; border: 1px solid var(--border); cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: var(--bg); }
.history-item.active { border-color: var(--primary); background: var(--primary-weak); font-weight: bold; }
.history-text { font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin: 0; color: var(--text); }
.delete-chat { border: none; background: none; color: var(--muted); cursor: pointer; font-size: 16px; }

/* 메인 채팅 판넬 */
.main-panel { height: 100%; flex: 1; display: flex; flex-direction: column; gap: 20px; }
.input-section {  background: var(--card);  border: 1px solid var(--border);  border-radius: 20px;  padding: 15px 20px;  box-shadow: var(--shadow); }
.input-container {  display: flex;  gap: 10px;  background: var(--bg);  padding: 8px 12px;  border-radius: 12px;  border: 1px solid var(--border);}
textarea { flex: 1; border: none; outline: none; resize: none; height: 60px; font-size: 14px; font-weight: 600; line-height: 1.5; background: transparent; color: var(--text); }
.send-btn { background: var(--primary); color: #fff; border: none; padding: 0 18px; border-radius: 10px; cursor: pointer; font-weight: 800; }
.send-btn:disabled { opacity: 0.3; }
.quick-tags { display: flex; gap: 8px; margin-top: 12px; }
.tag-btn { padding: 6px 12px; border-radius: 15px; border: 1px solid var(--border); background: var(--bg); color: var(--text); font-size: 12px; font-weight: 800; cursor: pointer; min-height: 0; }

/* 채팅 출력 영역 */
.chat-display { flex: 1; background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 24px; }
.message-group { display: flex; flex-direction: column; gap: 10px; } /* 메시지와 영화 카드를 묶는 그룹 */

.msg-row { display: flex; gap: 10px; align-items: flex-start; }
.msg-row.user { justify-content: flex-end; }
.bot-icon { font-size: 24px; padding: 4px; border-radius: 50%; border: 1px solid var(--border); background: var(--bg); }
.bubble { max-width: 75%; padding: 12px 16px; border-radius: 14px; font-size: 14px; font-weight: 600; line-height: 1.5; }
.assistant .bubble { background: var(--bg); border: 1px solid var(--border); color: var(--text); }
.user .bubble { background: var(--primary); color: #fff; }

/* 메시지 내부 영화 결과 스타일 (채팅 흐름 안에 위치) */
.movie-results-in-chat { display: flex; flex-direction: column; gap: 15px; padding-left: 45px; margin-top: 5px; }
.horizontal-card { display: flex; gap: 15px; padding: 12px; border: 1px solid var(--border); border-radius: 14px; background: var(--bg); box-shadow: 0 4px 6px rgba(0,0,0,0.02); cursor: pointer; transition: 0.2s; }
.horizontal-card:hover { transform: scale(1.01); border-color: var(--primary); }
.poster-box { width: 70px; aspect-ratio: 2/3; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: #000; }
.poster-box img { width: 100%; height: 100%; object-fit: cover; }

.info-box { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.info-top { display: flex; justify-content: space-between; align-items: flex-start; }
.m-title { font-size: 15px; font-weight: 900; margin: 0; color: var(--text); }
.stars { font-size: 13px; font-weight: 800; color: #f1c40f; }

/* AI 추천 이유 박스 */
.ai-reason-box { background: var(--nav-bg); color: var(--text); border: 1px solid var(--nav-border); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 8px; margin-top: 10px; }
.check-icon { background: var(--primary); color: #fff; width: 18px; height: 18px; border-radius: 50%; font-size: 10px; display: grid; place-items: center; }
.reason-text { font-size: 12px; font-weight: 600; margin: 0; opacity: 0.9; }
</style>