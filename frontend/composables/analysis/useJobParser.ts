export interface ParseRequest {
  job_description: string
  language: string
}

export interface ParseResponse {
  success: boolean
  data: Record<string, any> | null
  error: string | null
  time_seconds: number
  model: string
  language: string
}

export const useJobParser = () => {
  const config = useRuntimeConfig()
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<ParseResponse | null>(null)

  const parseJob = async (jobDescription: string, language: string = 'english'): Promise<ParseResponse | null> => {
    if (!jobDescription || jobDescription.trim().length < 50) {
      error.value = 'Job description must be at least 50 characters'
      return null
    }

    // Auto-truncate if over 6200 characters
    const truncatedDescription = jobDescription.length > 6200
      ? jobDescription.substring(0, 6200)
      : jobDescription

    isLoading.value = true
    error.value = null
    result.value = null

    try {
      const response = await $fetch<ParseResponse>('/api/parse', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          job_description: truncatedDescription,
          language: language
        }
      })

      result.value = response
      return response
    } catch (err: any) {
      const errorMessage = err?.data?.detail || err?.message || 'Failed to parse job description'
      error.value = errorMessage
      console.error('Parse error:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    parseJob,
    isLoading: readonly(isLoading),
    error: readonly(error),
    result: readonly(result)
  }
}
