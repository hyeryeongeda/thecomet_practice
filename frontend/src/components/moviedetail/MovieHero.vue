<template>
  <section class="hero-header">
    <div class="backdrop-bg" :style="{ backgroundImage: `url(https://image.tmdb.org/t/p/original${movie.backdrop_path})` }"></div>
    <div class="backdrop-overlay"></div>

    <div class="container hero-content">
      <div class="hero-text">
        <h1 class="title">{{ movie.title }}</h1>
        <p class="original-title">{{ movie.original_title }}</p>
        
        <div class="meta-info">
          <span>{{ movie.release_date?.slice(0, 4) }}</span>
          <span class="dot">・</span>
          <span>{{ movie.genres?.map(g => g.name).join('/') }}</span>
          <span class="dot">・</span>
          <span>{{ movie.production_countries?.[0]?.name }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  movie: { type: Object, required: true }
})
</script>

<style scoped>
/* MovieDetailView에서 .hero-header 관련 스타일을 가져오세요 */
.hero-header { position: relative; width: 100%; height: 400px; background: #000; margin-top: -60px; padding-top: 60px; display: flex; align-items: flex-end; overflow: hidden; }
.backdrop-bg { position: absolute; inset: 0; background-size: cover; background-position: center 20%; opacity: 0.6; z-index: 1; }
.backdrop-overlay { position: absolute; inset: 0; background: linear-gradient(to right, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.2) 100%); z-index: 2; }
.hero-content { position: relative; z-index: 3; width: 100%; padding-bottom: 30px; margin: 0 auto; max-width: 1100px; padding-left: 20px; }
.title { font-size: 40px; font-weight: 900; margin: 0 0 6px; color: #fff; }
.original-title { font-size: 14px; opacity: 0.7; margin-bottom: 12px; color: #fff; }
.meta-info { font-size: 15px; opacity: 0.8; color: #fff; }
.dot { margin: 0 6px; opacity: 0.5; }
.bottom-stats { margin-top: 16px; font-size: 13px; opacity: 0.6; color: #fff; }
</style>