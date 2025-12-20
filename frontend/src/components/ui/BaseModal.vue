<!-- frontend/src/components/ui/BaseModal.vue -->
<template>
  <Teleport to="body">
    <div v-if="modelValue" class="overlay" @click.self="close">
      <div class="panel">
        <div class="head">
          <h3 class="title">{{ title }}</h3>
          <button class="x" @click="close">✕</button>
        </div>

        <div class="body">
          <slot />
        </div>

        <div v-if="$slots.footer" class="foot">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, required: true },
  title: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'close'])

function close() {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 9999;
}
.panel {
  width: min(520px, 92vw);
  background: var(--card, #fff);
  border: 1px solid var(--border, #eee);
  border-radius: 16px;
  overflow: hidden;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border, #eee);
}
.title {
  margin: 0;
  font-size: 16px;
  font-weight: 900;
}
.x {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
}
.body { padding: 14px; }
.foot {
  padding: 12px 14px;
  border-top: 1px solid var(--border, #eee);
}
</style>
