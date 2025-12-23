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
      <section class="input-section">
        <div class="input-container">
          <textarea 
            v-model="chatInput" 
            placeholder="오늘 어떤 영화를 보고 싶으세요?&#10;(예 : 비도 오고 꿀꿀한데 위로가 되는 따뜻한 영화 추천해줘)"
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

      <div class="chat-display" ref="chatWindow">
        <div v-for="(m, idx) in currentChat.messages" :key="idx" :class="['msg-row', m.role]">
          <div v-if="m.role === 'assistant'" class="bot-icon">🤖</div>
          <div class="bubble">{{ m.content }}</div>
        </div>

        <div v-if="chatLoading" class="msg-row assistant">
          <div class="bot-icon">🤖</div>
          <div class="bubble loading">영화 3편을 엄선하고 있습니다... 🎬</div>
        </div>

        <div v-if="currentChat.movies && currentChat.movies.length > 0" class="movie-results">
          <div 
            v-for="movie in currentChat.movies" 
            :key="movie.tmdb_id" 
            class="horizontal-card" 
            @click="goMovie(movie.tmdb_id)"
          >
            <div class="poster-box">
              <img :src="posterUrl(movie.poster_path)" alt="poster">
            </div>
            <div class="info-box">
              <div class="info-top">
                <h4 class="m-title">{{ movie.title }}</h4>
                <div class="stars">⭐ {{ Number(movie.vote_average).toFixed(1) }}</div>
              </div>
              <div class="ai-reason-box">
                <div class="check-icon">✓</div>
                <div class="reason-content">
                  <span class="reason-label">AI 추천 내용</span>
                  <p class="reason-text">{{ movie.ai_reason || '당신의 취향에 딱 맞는 영화입니다.' }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { postTasteChat } from '@/api/comet'

const router = useRouter()
const chatWindow = ref(null)

const allChats = ref([])
const currentChatIndex = ref(0)
const chatInput = ref('')
const chatLoading = ref(false)

const currentChat = computed(() => {
  return allChats.value[currentChatIndex.value] || { messages: [], movies: [], title: '' }
})

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
    messages: [{ role: 'assistant', content: '안녕하세요! 취향에 딱 맞는 영화 3가지를 추천해 드릴게요.' }],
    movies: []
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

  target.messages.push({ role: 'user', content: text })
  chatInput.value = ''
  chatLoading.value = true
  await scrollToBottom()

  try {
    const history = target.messages.map(m => ({ role: m.role, content: m.content }))
    const res = await postTasteChat({ message: text, history })

    target.messages.push({ role: 'assistant', content: res.answer })
    
    // 🔥 백엔드 결과가 많더라도 프론트에서 3개로 제한 (slice)
    const rawMovies = (res.movies || []).slice(0, 3) 
    const reasons = res.recommended_reasons || {}
    
    target.movies = rawMovies.map(m => ({
      ...m,
      tmdb_id: m.tmdb_id || m.id,
      ai_reason: reasons[m.title] || reasons[m.name]
    }))

  } catch (e) {
    target.messages.push({ role: 'assistant', content: '서버 통신 중 오류가 발생했습니다.' })
  } finally {
    chatLoading.value = false
    await scrollToBottom()
  }
}

const posterUrl = (p) => p ? `https://image.tmdb.org/t/p/w200${p}` : ''
const goMovie = (id) => router.push({ name: 'movie-detail', params: { tmdbId: id } })
const scrollToBottom = async () => { 
  await nextTick()
  if (chatWindow.value) chatWindow.value.scrollTop = chatWindow.value.scrollHeight 
}
</script>

<style scoped>
.ai-recommend-layout { display: flex; gap: 20px; max-width: 1100px; margin: 0 auto; height: 750px; }

/* 사이드바 */
.chat-sidebar { width: 220px; border: 1px solid #eee; border-radius: 16px; padding: 15px; display: flex; flex-direction: column; background: #fff; }
.sidebar-top { margin-bottom: 20px; }
.sidebar-title { font-size: 16px; font-weight: 900; margin-bottom: 12px; }
.new-chat-btn { width: 100%; padding: 10px; background: #111; color: #fff; border: none; border-radius: 10px; font-weight: 800; cursor: pointer; transition: 0.2s; }

.chat-history-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.history-item { padding: 10px; border-radius: 8px; border: 1px solid #f0f0f0; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.history-item.active { border-color: #111; background: #f9f9f9; font-weight: bold; }
.history-text { font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin: 0; }
.delete-chat { border: none; background: none; color: #ccc; cursor: pointer; font-size: 16px; }

/* 메인 패널 */
.main-panel { flex: 1; display: flex; flex-direction: column; gap: 20px; }

.input-section { background: #fff; border: 2px solid #111; border-radius: 16px; padding: 18px; }
.input-container { display: flex; gap: 12px; }
textarea { flex: 1; border: none; outline: none; resize: none; height: 60px; font-size: 14px; font-weight: 600; line-height: 1.5; }
.send-btn { background: #111; color: #fff; border: none; padding: 0 18px; border-radius: 10px; cursor: pointer; font-weight: 800; }

.quick-tags { display: flex; gap: 8px; margin-top: 12px; }
.tag-btn { padding: 6px 12px; border-radius: 15px; border: 1px solid #eee; background: #f5f5f5; font-size: 12px; font-weight: 800; cursor: pointer; }

/* 채팅창 */
.chat-display { flex: 1; background: #fff; border: 1px solid #eee; border-radius: 16px; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
.msg-row { display: flex; gap: 10px; align-items: flex-start; }
.msg-row.user { justify-content: flex-end; }
.bot-icon { font-size: 24px; padding: 4px; border-radius: 50%; border: 1px solid #eee; background: #f9f9f9; }
.bubble { max-width: 75%; padding: 12px 16px; border-radius: 14px; font-size: 14px; font-weight: 600; line-height: 1.5; }
.assistant .bubble { background: #f0f0f0; border-top-left-radius: 2px; }
.user .bubble { background: #111; color: #fff; border-top-right-radius: 2px; }

/* 가로형 영화 카드 (3편 레이아웃) */
.movie-results { display: flex; flex-direction: column; gap: 15px; padding-left: 45px; }
.horizontal-card { display: flex; gap: 15px; padding: 12px; border: 1px solid #ddd; border-radius: 14px; background: #fff; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.horizontal-card:hover { transform: scale(1.01); box-shadow: 0 6px 15px rgba(0,0,0,0.1); }
.poster-box { width: 70px; aspect-ratio: 2/3; border-radius: 8px; overflow: hidden; flex-shrink: 0; }
.poster-box img { width: 100%; height: 100%; object-fit: cover; }

.info-box { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.info-top { display: flex; justify-content: space-between; align-items: flex-start; }
.m-title { font-size: 15px; font-weight: 900; margin: 0; }
.stars { font-size: 13px; font-weight: 800; color: #f1c40f; }

/* AI 추천 이유 박스 (스케치 스타일) */
.ai-reason-box { background: #666; color: #fff; border-radius: 10px; padding: 10px 14px; display: flex; align-items: flex-start; gap: 10px; margin-top: 10px; }
.check-icon { background: #444; width: 20px; height: 20px; border-radius: 50%; font-size: 11px; display: grid; place-items: center; flex-shrink: 0; margin-top: 2px; }
.reason-content { flex: 1; }
.reason-label { font-size: 11px; font-weight: 800; opacity: 0.8; display: block; margin-bottom: 2px; }
.reason-text { font-size: 12px; font-weight: 600; margin: 0; line-height: 1.4; }
</style>