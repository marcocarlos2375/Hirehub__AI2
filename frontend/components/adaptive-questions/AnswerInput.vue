<template>
  <div class="space-y-4">
    <!-- Tabs -->
    <HbTabs v-model="activeTabIndex" :tabs="tabsConfig" variant="underline">

      <!-- Text Input Tab -->
      <div v-show="activeTabIndex === 0" class="space-y-3">
        <HbInput
          v-model="textAnswer"
          type="textarea"
          :placeholder="placeholder"
          :disabled="disabled"
          :rows="4"
        />
        <HbButton
          @click="handleTextSubmit"
          :disabled="!textAnswer.trim() || disabled"
          variant="primary"
        >
          {{ submitButtonText }}
        </HbButton>
      </div>

      <!-- Voice Input Tab -->
      <div v-show="activeTabIndex === 1" class="space-y-4">
        <!-- Recording Controls -->
        <div v-if="!isRecording && !audioBlob" class="text-center py-8">
          <HbButton
            @click="startRecording"
            :disabled="disabled || isTranscribing"
            variant="danger"
            size="lg"
          >
            <template #leading-icon>
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="8" />
              </svg>
            </template>
            Start Recording
          </HbButton>
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
            <HbButton
              v-if="!isPaused"
              @click="pauseRecording"
              variant="secondary"
            >
              Pause
            </HbButton>
            <HbButton
              v-else
              @click="resumeRecording"
              variant="primary"
            >
              Resume
            </HbButton>
            <HbButton
              @click="stopRecording"
              variant="primary"
            >
              Stop
            </HbButton>
            <HbButton
              @click="cancelRecording"
              variant="outline"
            >
              Cancel
            </HbButton>
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
              <HbButton
                @click="retryRecording"
                variant="link"
                size="sm"
              >
                Re-record
              </HbButton>
            </div>
          </div>

          <!-- Transcription -->
          <div v-if="isTranscribing" class="text-center py-4">
            <HbSpinner size="lg" />
            <p class="text-sm text-gray-600 mt-2">Transcribing your answer...</p>
          </div>

          <div v-else-if="transcribedText" class="space-y-3">
            <label class="block text-sm font-medium text-gray-700">
              Transcribed Text (you can edit):
            </label>
            <HbInput
              v-model="transcribedText"
              type="textarea"
              :rows="4"
            />
            <HbButton
              @click="handleVoiceSubmit"
              :disabled="!transcribedText.trim() || disabled"
              variant="primary"
            >
              {{ submitButtonText }}
            </HbButton>
          </div>

          <HbButton
            v-else
            @click="transcribeAudio"
            :disabled="disabled"
            variant="primary"
          >
            Transcribe & Submit
          </HbButton>
        </div>
      </div>
    </HbTabs>
  </div>
</template>

<script setup lang="ts">
import { useVoiceRecorder } from '~/composables/audio/useVoiceRecorder'
import { useAudioTranscriber } from '~/composables/audio/useAudioTranscriber'

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

// Tabs configuration for HbTabs
const activeTabIndex = ref(0)
const tabsConfig = [
  {
    label: 'Text Answer'
  },
  {
    label: 'Voice Answer',
    icon: 'microphone' // Optional icon
  }
]

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
