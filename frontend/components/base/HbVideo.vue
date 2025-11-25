<template>
  <div 
    class="hb-video" 
    :class="[
      { 'hb-video--rounded': rounded },
      { 'hb-video--has-error': error },
      { 'hb-video--is-fullscreen': isFullscreen },
      aspectRatioClass
    ]"
  >
    <!-- Video Title -->
    <div v-if="title" class="hb-video__title">{{ title }}</div>
    
    <!-- Video Container -->
    <div class="hb-video__container" ref="videoContainer">
      <!-- Loading State -->
      <div v-if="loading" class="hb-video__loading">
        <HbSpinner size="xl" color="white" />
      </div>
      
      <!-- Error State -->
      <div v-if="error" class="hb-video__error">
        <div class="hb-video__error-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <div class="hb-video__error-message">{{ error }}</div>
      </div>
      
      <!-- Thumbnail with Play Button (before play) -->
      <div 
        v-if="!isPlaying && thumbnail && !error" 
        class="hb-video__thumbnail"
        :style="{ backgroundImage: `url(${thumbnail})` }"
        @click="play"
      >
        <div class="hb-video__play-button">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
        </div>
      </div>
      
      <!-- Actual Video Element -->
      <video
        ref="videoElement"
        class="hb-video__element"
        :src="src"
        :poster="thumbnail"
        :autoplay="autoplay"
        :loop="loop"
        :muted="muted"
        :controls="showControls && isPlaying"
        :playsinline="playsinline"
        @play="onPlay"
        @pause="onPause"
        @ended="onEnded"
        @timeupdate="onTimeUpdate"
        @loadstart="onLoadStart"
        @loadeddata="onLoadedData"
        @error="onError"
        @click="togglePlay"
      ></video>
      
      <!-- Custom Controls (shown when showControls is true and native controls are hidden) -->
      <div 
        v-if="showCustomControls && isPlaying && !showControls" 
        class="hb-video__custom-controls"
        @click.stop
      >
        <div class="hb-video__progress">
          <div 
            class="hb-video__progress-bar"
            :style="{ width: `${progress}%` }"
          ></div>
          <input 
            type="range" 
            min="0" 
            max="100" 
            step="0.1"
            v-model="progress"
            class="hb-video__progress-input"
            @input="onProgressInput"
          />
        </div>
        
        <div class="hb-video__controls-buttons">
          <button 
            class="hb-video__control-button" 
            @click="togglePlay"
            aria-label="Play/Pause"
          >
            <svg v-if="isPlaying" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="6" y="4" width="4" height="16"></rect>
              <rect x="14" y="4" width="4" height="16"></rect>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
          </button>
          
          <button 
            class="hb-video__control-button" 
            @click="toggleMute"
            aria-label="Mute/Unmute"
          >
            <svg v-if="muted" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="1" y1="1" x2="23" y2="23"></line>
              <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
              <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
          </button>
          
          <div class="hb-video__time">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </div>
          
          <button 
            v-if="allowFullscreen"
            class="hb-video__control-button" 
            @click="toggleFullscreen"
            aria-label="Fullscreen"
          >
            <svg v-if="isFullscreen" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"></path>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Caption -->
    <div v-if="caption" class="hb-video__caption">{{ caption }}</div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import HbSpinner from './HbSpinner.vue'

interface Props {
  src: string
  title?: string
  caption?: string
  thumbnail?: string
  autoplay?: boolean
  muted?: boolean
  loop?: boolean
  showControls?: boolean
  showCustomControls?: boolean
  playsinline?: boolean
  aspectRatio?: '1:1' | '4:3' | '16:9' | '21:9'
  rounded?: boolean
  allowFullscreen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  src: '',
  title: '',
  caption: '',
  thumbnail: '',
  autoplay: false,
  muted: false,
  loop: false,
  showControls: false,
  showCustomControls: true,
  playsinline: true,
  aspectRatio: '16:9',
  rounded: false,
  allowFullscreen: true
})

const emit = defineEmits<{
  play: []
  pause: []
  ended: []
  timeupdate: [{ currentTime: number; duration: number }]
  error: [message: string]
}>()

// Refs
const videoElement = ref<HTMLVideoElement | null>(null)
const videoContainer = ref<HTMLDivElement | null>(null)

// State
const isPlaying = ref<boolean>(false)
const loading = ref<boolean>(true)
const error = ref<string>('')
const currentTime = ref<number>(0)
const duration = ref<number>(0)
const progress = ref<number>(0)
const isFullscreen = ref<boolean>(false)
const internalMuted = ref<boolean>(props.muted)

// Computed
const aspectRatioClass = computed<string>(() => {
  return `hb-video--aspect-${props.aspectRatio.replace(':', '-')}`
})

// Methods
function play(): void {
  if (videoElement.value) {
    videoElement.value.play().catch((err: Error) => {
      error.value = 'Failed to play video: ' + err.message
    })
  }
}

function pause(): void {
  if (videoElement.value) {
    videoElement.value.pause()
  }
}

function togglePlay(): void {
  if (isPlaying.value) {
    pause()
  } else {
    play()
  }
}

function toggleMute(): void {
  internalMuted.value = !internalMuted.value
  if (videoElement.value) {
    videoElement.value.muted = internalMuted.value
  }
}

function onProgressInput(): void {
  if (videoElement.value) {
    const time = (progress.value / 100) * duration.value
    videoElement.value.currentTime = time
  }
}

function onPlay(): void {
  isPlaying.value = true
  emit('play')
}

function onPause(): void {
  isPlaying.value = false
  emit('pause')
}

function onEnded(): void {
  isPlaying.value = false
  emit('ended')
}

function onTimeUpdate(): void {
  if (videoElement.value) {
    currentTime.value = videoElement.value.currentTime
    duration.value = videoElement.value.duration || 0
    progress.value = (currentTime.value / duration.value) * 100 || 0
    emit('timeupdate', { currentTime: currentTime.value, duration: duration.value })
  }
}

function onLoadStart(): void {
  loading.value = true
  error.value = ''
}

function onLoadedData(): void {
  loading.value = false
  duration.value = videoElement.value?.duration || 0
}

function onError(): void {
  loading.value = false
  error.value = 'Failed to load video'
  emit('error', error.value)
}

function formatTime(seconds: number): string {
  if (!seconds || isNaN(seconds)) return '0:00'

  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs < 10 ? '0' + secs : secs}`
}

function toggleFullscreen(): void {
  if (!videoContainer.value) return

  if (!isFullscreen.value) {
    if (videoContainer.value.requestFullscreen) {
      videoContainer.value.requestFullscreen()
    } else if ((videoContainer.value as any).webkitRequestFullscreen) {
      (videoContainer.value as any).webkitRequestFullscreen()
    } else if ((videoContainer.value as any).msRequestFullscreen) {
      (videoContainer.value as any).msRequestFullscreen()
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    } else if ((document as any).webkitExitFullscreen) {
      (document as any).webkitExitFullscreen()
    } else if ((document as any).msExitFullscreen) {
      (document as any).msExitFullscreen()
    }
  }
}

// Fullscreen change event handler
function handleFullscreenChange(): void {
  isFullscreen.value = !!(
    document.fullscreenElement ||
    (document as any).webkitFullscreenElement ||
    (document as any).msFullscreenElement
  )
}

// Watch for muted prop changes
watch(() => props.muted, (newValue: boolean) => {
  internalMuted.value = newValue
  if (videoElement.value) {
    videoElement.value.muted = internalMuted.value
  }
})

// Lifecycle hooks
onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('msfullscreenchange', handleFullscreenChange)

  if (videoElement.value) {
    videoElement.value.muted = internalMuted.value
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('msfullscreenchange', handleFullscreenChange)
})
</script>

<style lang="scss" scoped>
.hb-video {
  width: 100%;
  margin-bottom: var(--spacing-4);
  
  &__title {
    font-weight: var(--font-medium);
    font-size: var(--text-base);
    margin-bottom: var(--spacing-2);
  }
  
  &__container {
    position: relative;
    width: 100%;
    background-color: var(--gray-900);
    overflow: hidden;
  }
  
  &__element {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
  }
  
  &__thumbnail {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.3);
    }
  }
  
  &__play-button {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background-color: rgba(var(--primary-500-rgb), 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
    transition: transform var(--transition-normal) var(--transition-ease), 
                background-color var(--transition-normal) var(--transition-ease);
    
    svg {
      margin-left: 4px;
    }
    
    &:hover {
      transform: scale(1.1);
      background-color: rgba(var(--primary-600-rgb), 0.9);
    }
  }
  
  &__loading {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 3;
  }
  
  &__error {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: rgba(var(--danger-500-rgb), 0.1);
    color: var(--danger-500);
    z-index: 3;
    padding: var(--spacing-4);
    text-align: center;
  }
  
  &__error-icon {
    margin-bottom: var(--spacing-2);
    
    svg {
      width: 48px;
      height: 48px;
    }
  }
  
  &__error-message {
    font-weight: var(--font-medium);
  }
  
  &__custom-controls {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
    padding: var(--spacing-2) var(--spacing-4);
    opacity: 0;
    transition: opacity var(--transition-normal) var(--transition-ease);
    z-index: 2;
    
    .hb-video__container:hover & {
      opacity: 1;
    }
  }
  
  &__progress {
    position: relative;
    height: 8px;
    margin-bottom: var(--spacing-2);
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: var(--radius-full);
    overflow: hidden;
  }
  
  &__progress-bar {
    height: 100%;
    background-color: var(--primary-500);
    border-radius: var(--radius-full);
    transition: width 0.1s linear;
  }
  
  &__progress-input {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
    margin: 0;
  }
  
  &__controls-buttons {
    display: flex;
    align-items: center;
    color: white;
  }
  
  &__control-button {
    background: none;
    border: none;
    color: white;
    padding: var(--spacing-1);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity var(--transition-fast) var(--transition-ease);
    
    &:hover {
      opacity: 0.8;
    }
    
    &:focus {
      outline: none;
    }
  }
  
  &__time {
    margin: 0 var(--spacing-2);
    font-size: var(--text-xs);
    flex: 1;
  }
  
  &__caption {
    margin-top: var(--spacing-2);
    font-size: var(--text-sm);
    color: var(--gray-600);
  }
  
  // Aspect ratios
  &--aspect-1-1 &__container {
    padding-top: 100%;
  }
  
  &--aspect-4-3 &__container {
    padding-top: 75%;
  }
  
  &--aspect-16-9 &__container {
    padding-top: 56.25%;
  }
  
  &--aspect-21-9 &__container {
    padding-top: 42.85%;
  }
  
  &--rounded {
    .hb-video__container {
      border-radius: var(--radius-md);
      overflow: hidden;
    }
  }
  
  &--is-fullscreen {
    .hb-video__container {
      padding-top: 0;
    }
  }
  
  &--has-error {
    .hb-video__container {
      border: 1px solid var(--danger-500);
    }
  }
}
</style>
