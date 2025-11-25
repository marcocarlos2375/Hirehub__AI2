<template>
  <div ref="counter">
    {{ displayNumber }}
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';

interface Props {
  endNumber: number
  duration?: number
  decimals?: number
}

const props = withDefaults(defineProps<Props>(), {
  duration: 2000,
  decimals: 0
});

const counter = ref<HTMLDivElement | null>(null);
const displayNumber = ref<number>(0);
const interval = ref<number | null>(null);
const startTime = ref<number | null>(null);
const observer = ref<IntersectionObserver | null>(null);
const hasStarted = ref<boolean>(false);

const startCounter = (): void => {
  if (hasStarted.value) return;
  hasStarted.value = true;
  startTime.value = Date.now();
  interval.value = requestAnimationFrame(updateCounter);
};

const updateCounter = (): void => {
  const currentTime = Date.now();
  const elapsed = currentTime - (startTime.value || 0);

  if (elapsed >= props.duration) {
    displayNumber.value = props.endNumber;
    if (interval.value !== null) {
      cancelAnimationFrame(interval.value);
    }
    return;
  }

  const progress = elapsed / props.duration;
  displayNumber.value = Math.round((props.endNumber * progress) * Math.pow(10, props.decimals)) / Math.pow(10, props.decimals);
  interval.value = requestAnimationFrame(updateCounter);
};

const observeVisibility = (): void => {
  observer.value = new IntersectionObserver((entries: IntersectionObserverEntry[]) => {
    const [entry] = entries;
    if (entry.isIntersecting) {
      startCounter();
      observer.value?.disconnect();
    }
  }, {
    threshold: 0.1 // Start when at least 10% of the element is visible
  });

  if (counter.value) {
    observer.value.observe(counter.value);
  }
};

onMounted(() => {
  observeVisibility();
});

onBeforeUnmount(() => {
  if (interval.value !== null) {
    cancelAnimationFrame(interval.value);
  }
  if (observer.value) {
    observer.value.disconnect();
  }
});

watch(() => props.endNumber, () => {
  hasStarted.value = false;
  displayNumber.value = 0;
  observeVisibility();
});
</script>
