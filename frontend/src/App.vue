<template>
  <TheNavbar />
  <router-view />
  <TheFooter />
</template>

<script setup>
import { onMounted } from 'vue'
import TheNavbar from '@/components/layout/TheNavbar.vue'
import TheFooter from '@/components/layout/TheFooter.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onMounted(() => {
  auth.bootstrap()
})
</script>
