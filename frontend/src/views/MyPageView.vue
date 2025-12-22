<template>
  <div class="page">
    <MyPageProfileCard :user="user" @edit="openEdit = true" />

    <MyPageTabs v-model="tab" />

    <div v-if="tab === 'vault'" class="content">
      <MyPageSection 
        title="코멘트 영화 (작성한)" 
        :moreLink="{ name: 'mypage-grid', params: { type: 'commented' }}"
        :isEmpty="commentedList.length === 0"
        emptyMsg="작성한 코멘트가 없습니다."
      >
        <MovieCard v-for="item in commentedList.slice(0, 5)" :key="item.id" :movie="item.movie" />
      </MyPageSection>

      <MyPageSection 
        title="보고싶은 영화" 
        :moreLink="{ name: 'mypage-grid', params: { type: 'wish' }}"
        :isEmpty="wishList.length === 0"
        emptyMsg="보고싶은 영화가 없습니다."
      >
        <MovieCard v-for="item in wishList.slice(0, 5)" :key="item.id" :movie="item.movie" />
      </MyPageSection>

      <MyPageSection 
        title="봤던 영화" 
        :moreLink="{ name: 'mypage-grid', params: { type: 'watched' }}"
        :isEmpty="watchedList.length === 0"
        emptyMsg="봤던 영화가 없습니다."
      >
        <MovieCard v-for="item in watchedList.slice(0, 5)" :key="item.id" :movie="item.movie" />
      </MyPageSection>
    </div>

    <div v-else class="content">
      <MyPageSection 
        title="인물 (자신이 좋아요를 누른)" 
        :moreLink="{ name: 'mypage-grid', params: { type: 'liked_people' }}"
        :isEmpty="likedPeople.length === 0"
        emptyMsg="좋아요한 인물이 없습니다."
      >
        <PersonCard v-for="p in likedPeople.slice(0, 5)" :key="p.tmdb_id" :person="p" />
      </MyPageSection>

      <MyPageSection title="장르 (자신이 좋아요를 누른)" :isEmpty="likedGenres.length === 0" emptyMsg="좋아요한 장르가 없습니다.">
        <div class="genre-list">
          <div v-for="g in likedGenres" :key="g.tmdb_id" class="genre-pill">{{ g.name }}</div>
        </div>
      </MyPageSection>

      <MyPageSection 
        title="코멘트 (자신이 좋아요를 누른)" 
        :moreLink="{ name: 'mypage-grid', params: { type: 'liked_reviews' }}"
        :isEmpty="likedReviews.length === 0"
        emptyMsg="좋아요한 코멘트가 없습니다."
      >
        <ReviewCard v-for="r in likedReviews.slice(0, 5)" :key="r.id" :review="r" />
      </MyPageSection>
    </div>

    <ProfileEditModal v-if="openEdit" :user="user" @close="openEdit = false" @saved="onProfileSaved" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { fetchMyActivity, fetchMyLikes } from '@/api/comet' 

// 분리된 컴포넌트 임포트
import MyPageProfileCard from '@/components/mypage/MyPageProfileCard.vue'
import MyPageTabs from '@/components/mypage/MyPageTabs.vue'
import MyPageSection from '@/components/mypage/MyPageSection.vue'

// 공통 컴포넌트 임포트
import MovieCard from '@/components/movie/MovieCard.vue'
import PersonCard from '@/components/movie/PersonCard.vue' 
import ReviewCard from '@/components/review/ReviewCard.vue'
import ProfileEditModal from '@/components/user/ProfileEditModal.vue' 

const auth = useAuthStore()
const user = computed(() => auth.user)

const tab = ref('vault')
const openEdit = ref(false)

const commentedList = ref([])
const wishList = ref([])
const watchedList = ref([])
const likedPeople = ref([])
const likedGenres = ref([])
const likedReviews = ref([])

function onProfileSaved(updatedUser) {
  // Pinia 스토어의 유저 정보를 업데이트합니다.
  // computed로 연결된 화면의 user도 자동으로 바뀝니다.
  auth.user = { ...auth.user, ...updatedUser }
}


onMounted(async () => {
  try {
    const [commented, wish, watched, people, genres, reviews] = await Promise.all([
      fetchMyActivity({ status: 'commented', sort: 'latest' }),
      fetchMyActivity({ status: 'wish', sort: 'latest' }),
      fetchMyActivity({ status: 'watched', sort: 'latest' }),
      fetchMyLikes('person'),
      fetchMyLikes('genre'),
      fetchMyActivity({ status: 'liked', sort: 'latest' })
    ])
    
    commentedList.value = commented || []
    wishList.value = wish || []
    watchedList.value = watched || []
    likedPeople.value = people || []
    likedGenres.value = genres || []
    likedReviews.value = reviews || []
  } catch (error) {
    console.error("데이터 로드 실패:", error)
  }
})
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 30px 14px; }
.genre-list { display: flex; flex-wrap: wrap; gap: 10px; }
.genre-pill { padding: 8px 16px; border-radius: 99px; background: var(--input-bg); border: 1px solid var(--border); color: var(--text); font-weight: 700; font-size: 14px; }
</style>