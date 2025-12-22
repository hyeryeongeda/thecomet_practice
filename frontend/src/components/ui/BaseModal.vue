<template>
  <Teleport to="body">
    <div v-if="open" class="modal-backdrop" @click="$emit('close')">
      <div class="modal-content" @click.stop>
        <header class="modal-header">
          <h3>{{ title }}</h3>
          <button class="close-btn" @click="$emit('close')">X</button>
        </header>
        <div class="modal-body">
          <slot></slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  open: Boolean,
  title: String
})

/** ✅ [수정 핵심] emits 선언을 추가하여 경고를 제거합니다. */
defineEmits(['close'])
</script>

<style scoped>

.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; padding: 20px; border-radius: 16px; min-width: 350px; position: relative; }
.close-btn { position: absolute; top: 15px; right: 15px; border: none; background: none; font-size: 18px; cursor: pointer; }
</style>