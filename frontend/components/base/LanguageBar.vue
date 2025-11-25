<template>
  <div class="language-item">
    <div class="language-name">{{ name }}</div>
    <div class="language-bar">
      <div class="language-progress" :style="{ width: `${level}%` }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

interface Props {
  name: string
  level: number
}

defineProps<Props>()
</script>

<style scoped>
.language-item {
  margin-bottom: 12px;
}

.language-name {
  font-size: 14px;
  margin-bottom: 4px;
}

.language-bar {
  height: 10px;
  background-color: #e0e0e0;
  border-radius: 0;
  overflow: hidden;
}

.language-progress {
  height: 100%;
  background-color: #222;
}
</style>
