export interface CoverLetterRequest {
  parsed_resume: Record<string, any>
  parsed_jd: Record<string, any>
  score_data?: Record<string, any>
  language?: string
}

export interface CoverLetterResponse {
  success: boolean
  cover_letter: string
  word_count: number
  time_seconds: number
  model: string
}

export const useCoverLetterGenerator = () => {
  const config = useRuntimeConfig()
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<CoverLetterResponse | null>(null)

  const generateCoverLetter = async (
    parsedResume: Record<string, any>,
    parsedJD: Record<string, any>,
    scoreData?: Record<string, any>,
    language: string = 'english'
  ): Promise<CoverLetterResponse | null> => {
    if (!parsedResume || !parsedJD) {
      error.value = 'Both parsed resume and job description are required'
      return null
    }

    isLoading.value = true
    error.value = null
    result.value = null

    try {
      const response = await $fetch<CoverLetterResponse>('/api/generate-cover-letter', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          parsed_resume: parsedResume,
          parsed_jd: parsedJD,
          score_data: scoreData,
          language: language
        }
      })

      result.value = response
      return response
    } catch (err: any) {
      const errorMessage = err?.data?.detail || err?.message || 'Failed to generate cover letter'
      error.value = errorMessage
      console.error('Cover letter generation error:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    generateCoverLetter,
    isLoading: readonly(isLoading),
    error: readonly(error),
    result: readonly(result)
  }
}
