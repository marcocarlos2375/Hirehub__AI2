<template>
  <div class="space-y-4">
    <!-- Tabs -->
    <div class="flex gap-2 border-b border-gray-200">
      <button
        @click="activeTab = 'text'"
        :class="[
          'px-4 py-2 font-medium text-sm transition-colors relative',
          activeTab === 'text'
            ? 'text-indigo-600 border-b-2 border-indigo-600'
            : 'text-gray-600 hover:text-gray-900'
        ]"
      >
        Text Answer
      </button>
      <button
        @click="activeTab = 'voice'"
        :class="[
          'px-4 py-2 font-medium text-sm transition-colors relative flex items-center gap-2',
          activeTab === 'voice'
            ? 'text-indigo-600 border-b-2 border-indigo-600'
            : 'text-gray-600 hover:text-gray-900'
        ]"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
        Voice Answer
      </button>
    </div>

    <!-- Text Input Tab -->
    <div v-show="activeTab === 'text'" class="space-y-3">
      <textarea
        v-model="textAnswer"
        :placeholder="placeholder"
        :disabled="disabled"
        rows="4"
        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none disabled:bg-gray-50 disabled:text-gray-500"
      />
      <button
        @click="handleTextSubmit"
        :disabled="!textAnswer.trim() || disabled"
        class="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        {{ submitButtonText }}
      </button>
    </div>

    <!-- Voice Input Tab -->
    <div v-show="activeTab === 'voice'" class="space-y-4">
      <!-- Recording Controls -->
      <div v-if="!isRecording && !audioBlob" class="text-center py-8">
        <button
          @click="startRecording"
          :disabled="disabled || isTranscribing"
          class="inline-flex items-center gap-3 px-6 py-3 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="8" />
          </svg>
          Start Recording
        </button>
        <p class="text-sm text-gray-500 mt-2">Click to start recording your answer</p>
      </div>

      <!-- Recording In Progress -->
      <div v-if="isRecording" class="text-center py-6 bg-red-50 rounded-lg border border-red-200">
        <div class="flex items-center justify-center gap-3 mb-4">
          <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
          <span class="text-lg font-semibold text-gray-900">
            {{ formatTime(recordingTime) }}
          </span>
        </div>

        <div class="flex items-center justify-center gap-3">
          <button
            v-if="!isPaused"
            @click="pauseRecording"
            class="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
          >
            Pause
          </button>
          <button
            v-else
            @click="resumeRecording"
            class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            Resume
          </button>
          <button
            @click="stopRecording"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Stop
          </button>
          <button
            @click="cancelRecording"
            class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>

      <!-- Audio Recorded - Ready to Transcribe -->
      <div v-if="audioBlob && !isRecording" class="space-y-4">
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-sm font-medium text-gray-900">
                Recording complete ({{ formatTime(recordingTime) }})
              </span>
            </div>
            <button
              @click="retryRecording"
              class="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
            >
              Re-record
            </button>
          </div>
        </div>

        <!-- Transcription -->
        <div v-if="isTranscribing" class="text-center py-4">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-2"></div>
          <p class="text-sm text-gray-600">Transcribing your answer...</p>
        </div>

        <div v-else-if="transcribedText" class="space-y-3">
          <label class="block text-sm font-medium text-gray-700">
            Transcribed Text (you can edit):
          </label>
          <textarea
            v-model="transcribedText"
            rows="4"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
          />
          <button
            @click="handleVoiceSubmit"
            :disabled="!transcribedText.trim() || disabled"
            class="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {{ submitButtonText }}
          </button>
        </div>

        <button
          v-else
          @click="transcribeAudio"
          :disabled="disabled"
          class="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Transcribe & Submit
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useVoiceRecorder } from '~/composables/useVoiceRecorder'
import { useAudioTranscriber } from '~/composables/useAudioTranscriber'

interface Props {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  submitButtonText?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'submit', value: string, type: 'text' | 'voice', transcriptionTime?: number): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Type your answer here...',
  submitButtonText: 'Submit Answer',
  disabled: false
})

const emit = defineEmits<Emits>()

const activeTab = ref<'text' | 'voice'>('text')
const textAnswer = ref(props.modelValue || '')
const transcribedText = ref('')
const isTranscribing = ref(false)

const {
  isRecording,
  isPaused,
  recordingTime,
  audioBlob,
  startRecording: startVoiceRecording,
  stopRecording: stopVoiceRecording,
  pauseRecording,
  resumeRecording,
  cancelRecording: cancelVoiceRecording,
  reset: resetVoiceRecorder,
  formatTime
} = useVoiceRecorder()

const { transcribeAudio: transcribeAudioAPI } = useAudioTranscriber()

const startRecording = async () => {
  try {
    await startVoiceRecording()
  } catch (error: any) {
    alert(error.message || 'Failed to start recording')
  }
}

const stopRecording = () => {
  stopVoiceRecording()
}

const cancelRecording = () => {
  cancelVoiceRecording()
  transcribedText.value = ''
}

const retryRecording = () => {
  resetVoiceRecorder()
  transcribedText.value = ''
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
}

watch(() => props.modelValue, (newValue) => {
  textAnswer.value = newValue || ''
})

watch(textAnswer, (newValue) => {
  emit('update:modelValue', newValue)
})
</script>
