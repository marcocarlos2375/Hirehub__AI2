<template>
  <div class="relative flex items-center justify-center w-40 h-40">
    <!-- Pulsing circles -->
    <div class="absolute inset-0 flex items-center justify-center">
      <template v-for="index in numberOfCircles" :key="index">
        <div class="absolute rounded-3xl transition-all duration-200"
          :class="[`pulse-circle-${index}`]"
          :style="{
            width: `${100 - (index-1) * circleGap}%`,
            height: `${100 - (index-1) * circleGap}%`,
            backgroundColor: `rgb(59, 130, 246, ${0.3 + (index-1) * 0.05})`
          }">
        </div>
      </template>
    </div>
    <!-- Icon container -->
    <div class="relative z-10 w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg shadow-lg flex items-center justify-center">
      <!-- Default slot for icon/text -->
      <slot>
        <span class="text-2xl font-bold text-white">{{ letter }}</span>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

interface Props {
  letter?: string
  numberOfCircles?: number
  animationDuration?: number
  circleGap?: number
}

const props = withDefaults(defineProps<Props>(), {
  letter: 'K',
  numberOfCircles: 5,
  animationDuration: 2,
  circleGap: 10
})
</script>

<style scoped>
@keyframes pulse {
  0%, 100% { 
    transform: scale(1);
    opacity: 0.3;
  }
  50% { 
    transform: scale(1.2);
    opacity: 0.5;
  }
}

.pulse-circle-1 {
  animation: pulse 2s infinite;
}

.pulse-circle-2 {
  animation: pulse 2s infinite;
  animation-delay: -0.3s;
}

.pulse-circle-3 {
  animation: pulse 2s infinite;
  animation-delay: -0.6s;
}

.pulse-circle-4 {
  animation: pulse 2s infinite;
  animation-delay: -0.9s;
}

.pulse-circle-5 {
  animation: pulse 2s infinite;
  animation-delay: -1.2s;
}

.pulse-circle-6 {
  animation: pulse 2s infinite;
  animation-delay: -1.5s;
}

.pulse-circle-7 {
  animation: pulse 2s infinite;
  animation-delay: -1.8s;
}

.pulse-circle-8 {
  animation: pulse 2s infinite;
  animation-delay: -2.1s;
}

.pulse-circle-9 {
  animation: pulse 2s infinite;
  animation-delay: -2.4s;
}

.pulse-circle-10 {
  animation: pulse 2s infinite;
  animation-delay: -2.7s;
}
</style>
