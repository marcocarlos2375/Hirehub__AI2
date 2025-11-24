export interface CVParseRequest {
  resume_text: string
  language: string
}

export interface CVParseResponse {
  success: boolean
  data: Record<string, any> | null
  error: string | null
  time_seconds: number
  model: string
  language: string
}

export const useCVParser = () => {
  const config = useRuntimeConfig()
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<CVParseResponse | null>(null)

  const parseCV = async (resumeText: string, language: string = 'english'): Promise<CVParseResponse | null> => {
    if (!resumeText || resumeText.trim().length < 50) {
      error.value = 'Resume text must be at least 50 characters'
      return null
    }

    // Auto-truncate if over 6200 characters
    const truncatedText = resumeText.length > 6200
      ? resumeText.substring(0, 6200)
      : resumeText

    isLoading.value = true
    error.value = null
    result.value = null

    try {
      const response = await $fetch<CVParseResponse>('/api/parse-cv', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          resume_text: truncatedText,
          language: language
        }
      })

      result.value = response
      return response
    } catch (err: any) {
      const errorMessage = err?.data?.detail || err?.message || 'Failed to parse resume'
      error.value = errorMessage
      console.error('Parse error:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    parseCV,
    isLoading: readonly(isLoading),
    error: readonly(error),
    result: readonly(result)
  }
}
