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
        title="좋아요 한 영화" 
        :moreLink="{ name: 'mypage-grid', params: { type: 'movie_likes' }}"
        :isEmpty="movieLikesList.length === 0"
        emptyMsg="좋아요 한 영화가 없습니다."
      >
        <MovieCard v-for="item in movieLikesList.slice(0, 5)" :key="item.id" :movie="item" />
      </MyPageSection>

      <MyPageSection 
        title="보고싶은 영화" 
        :moreLink="{ name: 'mypage-grid', params: { type: 'wish' }}"
        :isEmpty="wishList.length === 0"
        emptyMsg="보고싶은 영화가 없습니다."
      >
        <MovieCard v-for="item in wishList.slice(0, 5)" :key="item.id" :movie="item.movie" />
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

// 컴포넌트 임포트 (경로 확인해주세요!)
import MyPageProfileCard from '@/components/mypage/MyPageProfileCard.vue'
import MyPageTabs from '@/components/mypage/MyPageTabs.vue'
import MyPageSection from '@/components/mypage/MyPageSection.vue'
import MovieCard from '@/components/movie/MovieCard.vue'
import PersonCard from '@/components/movie/PersonCard.vue' 
import ReviewCard from '@/components/review/ReviewCard.vue'
import ProfileEditModal from '@/components/user/ProfileEditModal.vue' 

const auth = useAuthStore()
const user = computed(() => auth.user)

const tab = ref('vault')
const openEdit = ref(false)

// 데이터 상태 변수들
const commentedList = ref([])   // 내가 쓴 리뷰
const movieLikesList = ref([])  // [추가] 내가 좋아요(하트) 누른 영화
const wishList = ref([])        // 보고싶어요 (리뷰 썼지만 안 본 영화)
const likedPeople = ref([])     // 좋아요 인물
const likedReviews = ref([])    // 좋아요 누른 리뷰

function onProfileSaved(updatedUser) {
  auth.user = { ...auth.user, ...updatedUser }
}

onMounted(async () => {
  try {
    // Promise.all로 모든 데이터 한 번에 병렬 요청
    const [
      commented, 
      movieLikes,  // [추가] 영화 좋아요
      wish, 
      people, 
      reviews
    ] = await Promise.all([
      fetchMyActivity({ status: 'commented', sort: 'latest' }), // 1. 작성한 리뷰
      fetchMyLikes('movie'),                                    // 2. [중요] 영화 좋아요 목록
      fetchMyActivity({ status: 'wish', sort: 'latest' }),      // 3. 보고싶어요 (watched=False)
      fetchMyLikes('person'),                                   // 4. 인물 좋아요
      fetchMyActivity({ status: 'liked', sort: 'latest' })      // 5. 좋아요 누른 리뷰
    ])
    
    // 데이터 할당
    commentedList.value = commented || []
    movieLikesList.value = movieLikes || [] // [연결]
    wishList.value = wish || []
    likedPeople.value = people || []
    likedReviews.value = reviews || []

  } catch (error) {
    console.error("마이페이지 데이터 로드 실패:", error)
  }
})
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 30px 14px; padding-bottom: 100px; }
</style>