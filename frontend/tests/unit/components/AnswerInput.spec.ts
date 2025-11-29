import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AnswerInput from '~/components/adaptive-questions/forms/AnswerInput.vue'

// Mock composables
vi.mock('~/composables/audio/useVoiceRecorder', () => ({
  useVoiceRecorder: () => ({
    isRecording: ref(false),
    isPaused: ref(false),
    recordingTime: ref(0),
    audioBlob: ref(null),
    startRecording: vi.fn(async () => {}),
    stopRecording: vi.fn(),
    pauseRecording: vi.fn(),
    resumeRecording: vi.fn(),
    cancelRecording: vi.fn(),
    reset: vi.fn(),
    formatTime: (seconds: number) => `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, '0')}`
  })
}))

vi.mock('~/composables/audio/useAudioTranscriber', () => ({
  useAudioTranscriber: () => ({
    transcribeAudio: vi.fn(async () => ({
      success: true,
      transcribed_text: 'Mocked transcription',
      time_seconds: 1.5
    }))
  })
}))

describe('AnswerInput Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render text input tab by default', () => {
    const wrapper = mount(AnswerInput)

    expect(wrapper.find('textarea').exists()).toBe(true)
    expect(wrapper.text()).toContain('Text Answer')
    expect(wrapper.text()).toContain('Voice Answer')
  })

  it('should switch to voice tab when clicked', async () => {
    const wrapper = mount(AnswerInput)

    const voiceTab = wrapper.findAll('button').find(btn =>
      btn.text().includes('Voice Answer')
    )
    await voiceTab!.trigger('click')

    expect(wrapper.text()).toContain('Start Recording')
  })

  it('should emit submit event on text submission', async () => {
    const wrapper = mount(AnswerInput)

    const textarea = wrapper.find('textarea')
    await textarea.setValue('My test answer')

    const submitButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Submit Answer')
    )
    await submitButton!.trigger('click')

    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')?.[0]).toEqual(['My test answer', 'text'])
  })

  it('should disable submit button when text is empty', () => {
    const wrapper = mount(AnswerInput)

    const submitButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Submit Answer')
    )
    expect(submitButton!.attributes('disabled')).toBeDefined()
  })

  it('should enable submit button when text is entered', async () => {
    const wrapper = mount(AnswerInput)

    const textarea = wrapper.find('textarea')
    await textarea.setValue('Some answer')

    const submitButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Submit Answer')
    )
    expect(submitButton!.attributes('disabled')).toBeUndefined()
  })

  it('should respect disabled prop', () => {
    const wrapper = mount(AnswerInput, {
      props: {
        disabled: true
      }
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.attributes('disabled')).toBeDefined()

    const submitButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Submit Answer')
    )
    expect(submitButton!.attributes('disabled')).toBeDefined()
  })

  it('should display custom placeholder', () => {
    const customPlaceholder = 'Enter your custom answer here'
    const wrapper = mount(AnswerInput, {
      props: {
        placeholder: customPlaceholder
      }
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.attributes('placeholder')).toBe(customPlaceholder)
  })

  it('should display custom submit button text', () => {
    const customText = 'Send Answer'
    const wrapper = mount(AnswerInput, {
      props: {
        submitButtonText: customText
      }
    })

    expect(wrapper.text()).toContain(customText)
  })

  it('should update v-model on text input', async () => {
    const wrapper = mount(AnswerInput, {
      props: {
        modelValue: 'Initial value'
      }
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.element.value).toBe('Initial value')

    await textarea.setValue('Updated value')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['Updated value'])
  })

  it('should show recording controls in voice tab', async () => {
    const wrapper = mount(AnswerInput)

    const voiceTab = wrapper.findAll('button').find(btn =>
      btn.text().includes('Voice Answer')
    )
    await voiceTab!.trigger('click')

    expect(wrapper.text()).toContain('Start Recording')
    expect(wrapper.text()).toContain('Click to start recording your answer')
  })

  it('should not submit empty whitespace-only text', async () => {
    const wrapper = mount(AnswerInput)

    const textarea = wrapper.find('textarea')
    await textarea.setValue('   ')

    const submitButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Submit Answer')
    )

    // Button should still be disabled for whitespace-only content
    expect(submitButton!.attributes('disabled')).toBeDefined()
  })

  it('should apply active tab styling correctly', async () => {
    const wrapper = mount(AnswerInput)

    const textTab = wrapper.findAll('button').find(btn =>
      btn.text() === 'Text Answer'
    )
    expect(textTab!.classes()).toContain('text-indigo-600')

    const voiceTab = wrapper.findAll('button').find(btn =>
      btn.text().includes('Voice Answer')
    )
    expect(voiceTab!.classes()).toContain('text-gray-600')

    // Switch tabs
    await voiceTab!.trigger('click')

    expect(voiceTab!.classes()).toContain('text-indigo-600')
  })

  it('should maintain separate state between text and voice tabs', async () => {
    const wrapper = mount(AnswerInput)

    // Enter text in text tab
    const textarea = wrapper.find('textarea')
    await textarea.setValue('Text answer')

    // Switch to voice tab
    const voiceTab = wrapper.findAll('button').find(btn =>
      btn.text().includes('Voice Answer')
    )
    await voiceTab!.trigger('click')

    // Switch back to text tab
    const textTab = wrapper.findAll('button').find(btn =>
      btn.text() === 'Text Answer'
    )
    await textTab!.trigger('click')

    // Text should still be there
    expect(textarea.element.value).toBe('Text answer')
  })
})
