<template>
  <div class="relative" @click.stop>
    <!-- Text Input -->
    <div
      class="input-container"
      :class="{ 'input-container--focused': isFocused }"
    >
      <!-- Text Input -->
      <textarea
        ref="textareaRef"
        v-model="textAnswer"
        :placeholder="placeholder"
        :disabled="disabled"
        rows="1"
        class="input-field"
        @focus="isFocused = true"
        @blur="isFocused = false"
        @input="autoResize"
        @keydown.enter.exact.prevent="handleTextSubmit"
      />

      <!-- Bottom Row: Right icons -->
      <div class="input-actions">
        <!-- Microphone Button - Start Recording -->
        <button
          @click="handleMicrophoneClick"
          class="input-icon-button"
          type="button"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
        </button>

        <!-- Send Button -->
        <button
          @click="handleTextSubmit"
          :disabled="!textAnswer.trim() || disabled"
          class="input-send-button"
          type="button"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M5 10l7-7m0 0l7 7m-7-7v18"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Voice Recording Modal (No Overlay) -->
    <div
      v-if="showVoiceModal"
      class="voice-modal"
      @click.stop
    >
      <div>
        <!-- Recording In Progress -->
        <div v-if="isRecording" class="py-2">
          <div class="flex items-center gap-3">
            <!-- Scrolling Waveform -->
            <div class="waveform-container flex-1">
              <div class="waveform-scroll">
                <div
                  v-for="(height, index) in waveformHistory"
                  :key="index"
                  class="waveform-bar"
                  :style="{ height: Math.max(height, 2) + 'px' }"
                ></div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex items-center gap-2">
              <!-- Cancel Button -->
              <button
                @click="cancelRecording"
                class="record-action-button"
                type="button"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              <!-- Stop & Transcribe Button -->
              <button
                @click="stopAndTranscribe"
                class="record-action-button"
                type="button"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Transcribing -->
        <div v-if="showTranscribing || isTranscribing" class="py-2">
          <div class="flex items-center gap-3">
            <!-- Waveform -->
            <div class="waveform-container">
              <div class="waveform-scroll">
                <div
                  v-for="(height, index) in waveformHistory"
                  :key="index"
                  class="waveform-bar waveform-bar--static"
                  :style="{ height: height + 'px' }"
                ></div>
              </div>
            </div>

            <!-- Transcribing Status -->
            <div class="flex items-center gap-2">
              <HbSpinner size="sm" />
              <span class="text-sm font-semibold text-white whitespace-nowrap">Transcribing...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AnswerInputProps, AnswerInputEmits } from '~/types/component-props'
import { useVoiceRecorder } from '~/composables/audio/useVoiceRecorder'
import { useAudioTranscriber } from '~/composables/audio/useAudioTranscriber'

const props = withDefaults(defineProps<AnswerInputProps>(), {
  placeholder: 'Type your answer here...',
  submitButtonText: 'Submit Answer',
  disabled: false
})

const emit = defineEmits<AnswerInputEmits>()

// Voice modal state
const showVoiceModal = ref(false)

// Text input state
const textAnswer = ref(props.modelValue || '')
const transcribedText = ref('')
const isTranscribing = ref(false)
const isFocused = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const showTranscribing = ref(false)

// Audio visualization
const audioContext = ref<AudioContext | null>(null)
const analyser = ref<AnalyserNode | null>(null)
const dataArray = ref<Uint8Array | null>(null)
const animationFrame = ref<number | null>(null)
const waveformHistory = ref<number[]>([]) // Store all waveform bars as they're created
let frameCount = 0 // Counter to slow down bar generation

// Auto-resize textarea
const autoResize = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
  }
}

// Reset textarea height when text is cleared
watch(textAnswer, (newVal) => {
  if (!newVal && textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
})

// Initialize textarea height on mount
onMounted(() => {
  if (textareaRef.value && textAnswer.value) {
    autoResize()
  }
})

const {
  isRecording,
  isPaused,
  recordingTime,
  audioBlob,
  mediaStream,
  startRecording: startVoiceRecording,
  stopRecording: stopVoiceRecording,
  pauseRecording,
  resumeRecording,
  cancelRecording: cancelVoiceRecording,
  reset: resetVoiceRecorder,
  formatTime
} = useVoiceRecorder()

const { transcribeAudio: transcribeAudioAPI } = useAudioTranscriber()

const setupAudioVisualization = async (stream: MediaStream) => {
  try {
    // Create audio context and analyser
    audioContext.value = new AudioContext()
    analyser.value = audioContext.value.createAnalyser()
    analyser.value.fftSize = 256

    const source = audioContext.value.createMediaStreamSource(stream)
    source.connect(analyser.value)

    const bufferLength = analyser.value.frequencyBinCount
    dataArray.value = new Uint8Array(bufferLength)

    // Start visualization loop
    updateWaveform()
  } catch (error) {
    console.error('Error setting up audio visualization:', error)
  }
}

const updateWaveform = () => {
  if (!analyser.value || !dataArray.value || !isRecording.value) {
    console.log('updateWaveform stopped - analyser:', !!analyser.value, 'dataArray:', !!dataArray.value, 'isRecording:', isRecording.value)
    return
  }

  frameCount++

  // Only add a bar every 5 frames (slows down to ~12 bars per second instead of 60)
  if (frameCount % 5 === 0) {
    analyser.value.getByteTimeDomainData(dataArray.value! as Uint8Array<ArrayBuffer>)

    // Calculate average volume across all data
    const sum = dataArray.value.reduce((acc, val) => {
      const normalized = (val - 128) / 128 // Normalize to -1 to 1
      return acc + normalized * normalized
    }, 0)
    const rms = Math.sqrt(sum / dataArray.value.length)

    // Amplify the signal for more sensitivity
    const amplified = rms * 4

    // Map to height range
    const minHeight = 2
    const maxHeight = 80
    const barHeight = minHeight + Math.min(amplified, 1) * (maxHeight - minHeight)

    // Add new bar to history
    waveformHistory.value.push(barHeight)

    if (waveformHistory.value.length % 30 === 0) {
      console.log('Waveform history length:', waveformHistory.value.length, 'Last bar height:', barHeight)
    }

    // Keep only recent bars (limit to prevent memory issues)
    if (waveformHistory.value.length > 300) {
      waveformHistory.value.shift()
    }
  }

  animationFrame.value = requestAnimationFrame(updateWaveform)
}

const stopAudioVisualization = () => {
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
    animationFrame.value = null
  }

  if (audioContext.value) {
    audioContext.value.close()
    audioContext.value = null
  }

  analyser.value = null
  dataArray.value = null
  frameCount = 0
  // Keep waveformHistory to show during transcription
}

const handleMicrophoneClick = async () => {
  showVoiceModal.value = true
  // Start recording immediately
  await startRecording()
}

const startRecording = async () => {
  try {
    await startVoiceRecording()

    console.log('Recording started, mediaStream:', mediaStream.value)

    // Setup visualization using the stream from voice recorder
    if (mediaStream.value) {
      await setupAudioVisualization(mediaStream.value)
      console.log('Visualization setup complete')
    } else {
      console.error('No media stream available')
    }
  } catch (error: any) {
    console.error('Recording error:', error)
    alert(error.message || 'Failed to start recording')
  }
}

const stopRecording = () => {
  stopAudioVisualization()
  stopVoiceRecording()
}

const stopAndTranscribe = async () => {
  stopAudioVisualization()
  stopVoiceRecording()

  // Set transcribing flag immediately to show the "Transcribing..." message
  showTranscribing.value = true

  // Wait for the audioBlob to be ready
  await new Promise(resolve => setTimeout(resolve, 200))

  // Start transcription
  await transcribeAudio()

  // Hide the transcribing message after transcription completes
  showTranscribing.value = false

  // Append transcribed text to the main input instead of overwriting
  if (transcribedText.value) {
    // Add space if there's already text
    if (textAnswer.value.trim()) {
      textAnswer.value = textAnswer.value + ' ' + transcribedText.value
    } else {
      textAnswer.value = transcribedText.value
    }
    // Close the modal
    closeVoiceModal()
  }
}

const cancelRecording = () => {
  stopAudioVisualization()
  cancelVoiceRecording()
  transcribedText.value = ''
  showTranscribing.value = false
  waveformHistory.value = []
  showVoiceModal.value = false
}

const retryRecording = async () => {
  stopAudioVisualization()
  resetVoiceRecorder()
  transcribedText.value = ''
  showTranscribing.value = false
  waveformHistory.value = []

  // Restart recording
  await startRecording()
}

const transcribeAudio = async () => {
  if (!audioBlob.value) return

  try {
    isTranscribing.value = true
    const result = await transcribeAudioAPI(audioBlob.value)

    if (result.success) {
      transcribedText.value = result.transcribed_text
    } else {
      throw new Error(result.error || 'Transcription failed')
    }
  } catch (error: any) {
    alert(error.message || 'Failed to transcribe audio')
  } finally {
    isTranscribing.value = false
  }
}

const handleTextSubmit = () => {
  if (!textAnswer.value.trim()) return
  emit('submit', textAnswer.value, 'text')
}

const handleVoiceSubmit = () => {
  if (!transcribedText.value.trim()) return
  emit('submit', transcribedText.value, 'voice', recordingTime.value)
  closeVoiceModal()
}

const closeVoiceModal = () => {
  showVoiceModal.value = false
  stopAudioVisualization()
  // Reset recording state when closing
  if (isRecording.value) {
    cancelVoiceRecording()
  }
  resetVoiceRecorder()
  transcribedText.value = ''
}

// Cleanup on unmount
onBeforeUnmount(() => {
  stopAudioVisualization()
})

watch(() => props.modelValue, (newValue) => {
  textAnswer.value = newValue || ''
})

watch(textAnswer, (newValue) => {
  emit('update:modelValue', newValue)
})
</script>

<style scoped>
/* Input Container Wrapper */
.input-container {
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: white;
  border-radius: 0.75rem;
  border: 2px solid #e5e7eb;
  transition: border-color 0.3s ease;
}

/* Animated Border Effect - appears on focus */
.input-container--focused {
  border-color: transparent;
  box-shadow: 0 0 0 2px var(--primary-400);
  animation: borderPulse 2s ease-in-out infinite;
}

@keyframes borderPulse {
  0%, 100% {
    box-shadow: 0 0 0 2px var(--primary-300);
  }
  50% {
    box-shadow: 0 0 0 2px var(--primary-500);
  }
}

/* Textarea Field */
.input-field {
  flex: 1;
  width: 100%;
  border: none;
  outline: none;
  resize: none;
  font-size: 0.875rem;
  line-height: 1.5;
  color: #1f2937;
  background: transparent;
  min-height: 24px;
  max-height: 200px;
  overflow-y: auto;
}

.input-field::placeholder {
  color: #9ca3af;
}

.input-field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Input Actions Row */
.input-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Icon Button (Microphone) */
.input-icon-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background: transparent;
  border: none;
  border-radius: 9999px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.input-icon-button:hover {
  background-color: #f3f4f6;
  color: #374151;
  transform: scale(1.05);
}

.input-icon-button:active {
  transform: scale(0.95);
}

/* Send Button */
.input-send-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background-color: var(--primary-400);
  border: none;
  border-radius: 9999px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.input-send-button:hover:not(:disabled) {
  background-color: var(--primary-500);
  transform: scale(1.05);
}

.input-send-button:active:not(:disabled) {
  transform: scale(0.95);
}

.input-send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Voice Modal */
.voice-modal {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 0.5rem;
  background-color: var(--primary-950);
  opacity: 0.95;
  border-radius: 1.5rem;
  padding: 0.5rem 0.75rem;
  z-index: 10;
  min-width: 400px;
  color: white;
}

/* Waveform Container */
.waveform-container {
  height: 40px;
  width: 300px;
  overflow: hidden;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 0.5rem;
  padding: 0 0.5rem;
}

.waveform-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.waveform-scroll {
  display: flex;
  flex-direction: row-reverse;
  align-items: center;
  gap: 1px;
  height: 100%;
  min-width: 100%;
  width: max-content;
  justify-content: flex-end;
}

/* Waveform Bars */
.waveform-bar {
  width: 3px;
  background-color: var(--primary-400);
  flex-shrink: 0;
  max-height: 30px;
}

.waveform-bar--static {
  opacity: 0.7;
}

/* Record Action Buttons */
.record-action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.record-action-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.record-action-button:active {
  transform: scale(0.95);
}
</style>
