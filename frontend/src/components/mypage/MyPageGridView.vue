<template>
  <div class="page">
    <header class="header">
      <h2 class="title">{{ pageTitle }}</h2>
      <SortDropdown 
        v-if="type !== 'liked_people'"
        v-model="currentSort" 
        @update:modelValue="loadData" 
      />
    </header>

    <div v-if="loading" class="loading">로딩중...</div>
    
    <div v-else-if="items.length > 0" class="grid-container">
      
      <template v-if="type === 'liked_people'">
        <PersonCard 
          v-for="item in items" 
          :key="item.tmdb_id" 
          :person="item" 
        />
      </template>

      <template v-else-if="type === 'liked_reviews'">
        <ReviewCard 
          v-for="item in items" 
          :key="item.id" 
          :review="item" 
        />
      </template>

      <template v-else>
        <MovieCard 
          v-for="item in items" 
          :key="item.id || item.tmdb_id" 
          :movie="item.movie || item" 
          class="card-item"
        />
      </template>

    </div>

    <div v-else class="empty">
      보관된 데이터가 없습니다.
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchMyActivity, fetchMyLikes } from '@/api/comet' 

// 컴포넌트 임포트
import SortDropdown from '@/components/ui/SortDropdown.vue'
import MovieCard from '@/components/movie/MovieCard.vue'
import PersonCard from '@/components/movie/PersonCard.vue' 
import ReviewCard from '@/components/review/ReviewCard.vue'

const route = useRoute()
const type = route.params.type 
const items = ref([])
const loading = ref(false)
const currentSort = ref('latest')

const pageTitle = computed(() => {
  const titles = {
    watched: '봤던 영화',
    wish: '보고싶은 영화',
    commented: '코멘트 작성한 영화',
    liked_people: '좋아요한 인물',
    liked_reviews: '좋아요한 코멘트'
  }
  return titles[type] || '목록'
})

async function loadData() {
  loading.value = true
  try {
    if (type === 'liked_people') {
      items.value = await fetchMyLikes('person')
    } else if (type === 'liked_reviews') {
      items.value = await fetchMyActivity({ status: 'liked', sort: currentSort.value })
    } else {
      items.value = await fetchMyActivity({ status: type, sort: currentSort.value })
    }
  } catch (e) {
    console.error("데이터 로딩 실패:", e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 20px 14px 60px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 2px solid #eee; }
.title { font-size: 22px; font-weight: 900; margin: 0; }
.loading, .empty { padding: 40px; text-align: center; color: #888; }

.grid-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

@media (min-width: 600px) { .grid-container { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 900px) { .grid-container { grid-template-columns: repeat(5, 1fr); } }
</style>