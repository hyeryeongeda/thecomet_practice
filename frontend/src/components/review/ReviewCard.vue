<template>
  <div class="review-card" @click="goMovie">
    <div class="card-header">
      <div class="user-info">
        <div class="avatar-circle">
          <img v-if="review.user?.profile_image" :src="review.user.profile_image" alt="avatar" />
          <span v-else>👤</span>
        </div>
        <span class="username">{{ review.user?.username || '익명' }}</span>
      </div>
      <div class="rating-stars">
        <span v-for="i in 5" :key="i" class="star" :class="{ active: i <= (review.rating || 0) }">
          ★
        </span>
      </div>
    </div>

    <div class="card-body">
      <div class="mini-poster">
        <img v-if="review.movie?.poster_path" :src="posterUrl(review.movie.poster_path)" alt="movie" />
        <div v-else class="no-poster">2:3</div>
      </div>
      
      <div class="text-content">
        <p class="movie-title">{{ review.movie?.title || '영화 제목' }}</p>
        <p class="comment-text">{{ review.content }}</p>
      </div>
    </div>

    <div class="card-footer">
      <div class="likes">
        <span class="icon">👍</span> {{ review.likes_count || 0 }}
        <span class="icon" style="margin-left: 10px;">👎</span> 0
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router' // 1. 라우터 불러오기

const props = defineProps({
  review: { type: Object, required: true }
})

const router = useRouter() // 2. 라우터 인스턴스 생성

// 3. 영화 상세 페이지 이동 함수
const goMovie = () => {
  // 백엔드 데이터 구조에 따라 tmdb_id 혹은 movie.tmdb_id 확인
  const tmdbId = props.review.movie?.tmdb_id || props.review.movie_tmdb_id
  if (tmdbId) {
    router.push(`/movies/${tmdbId}`)
  } else {
    console.warn("영화 ID를 찾을 수 없습니다:", props.review)
  }
}

const posterUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `https://image.tmdb.org/t/p/w185${path}`
}
</script>

<style scoped>
.review-card {
  background: #fff;
  border-radius: 14px;
  padding: 16px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* 부드러운 그림자 */
  cursor: pointer;
  transition: transform 0.2s ease;
}

.review-card:hover { transform: translateY(-3px); }

/* 헤더: 유저와 별점 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.user-info { display: flex; align-items: center; gap: 8px; }
.avatar-circle {
  width: 24px; height: 24px; border-radius: 50%;
  background: #eee; overflow: hidden; display: flex; align-items: center; justify-content: center;
}
.avatar-circle img { width: 100%; height: 100%; object-fit: cover; }
.username { font-weight: 800; font-size: 13px; }

.rating-stars { color: #ddd; font-size: 12px; }
.star.active { color: #f5c518; }

/* 바디: 포스터 + 텍스트 */
.card-body {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}
.mini-poster {
  width: 50px;
  aspect-ratio: 2/3;
  border-radius: 4px;
  overflow: hidden;
  background: #111;
  flex-shrink: 0;
}
.mini-poster img { width: 100%; height: 100%; object-fit: cover; }
.no-poster { color: #fff; font-size: 10px; display: grid; place-items: center; height: 100%; }

.text-content { flex: 1; overflow: hidden; }
.movie-title {
  font-weight: 900; font-size: 13px; color: #111;
  margin: 0 0 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.comment-text {
  font-size: 12px; color: #555; font-weight: 600;
  line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 푸터: 소셜 수치 */
.card-footer {
  border-top: 1px solid #f9f9f9;
  padding-top: 10px;
  font-size: 12px;
  font-weight: 800;
  color: #999;
}
</style>