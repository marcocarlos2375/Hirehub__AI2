export interface TranscribeAudioResult {
  success: boolean
  transcribed_text: string
  time_seconds: number
  model: string
  error?: string
}

export const useAudioTranscriber = () => {
  const config = useRuntimeConfig()

  const transcribeAudio = async (audioBlob: Blob): Promise<TranscribeAudioResult> => {
    try {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.webm')

      const data = await $fetch<TranscribeAudioResult>('/api/transcribe-audio', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: formData
      })

      return data
    } catch (error) {
      console.error('Error transcribing audio:', error)
      throw error
    }
  }

  return {
    transcribeAudio
  }
}
