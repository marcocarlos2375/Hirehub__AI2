import type { GenerateQuestionsResult } from '~/composables/analysis/useAnalysisState'

export const useQuestionGenerator = () => {
  const config = useRuntimeConfig()

  const generateQuestions = async (
    parsedCV: any,
    parsedJD: any,
    scoreResult: any,
    language: string = 'english'
  ): Promise<GenerateQuestionsResult | null> => {
    // Deprecation warning
    console.warn(
      '[DEPRECATED] useQuestionGenerator is being phased out. ' +
      'Please use the new adaptive questions workflow instead. ' +
      'Toggle in settings or set useAdaptiveFlow = true in useAnalysisState'
    )

    try {
      const data = await $fetch<GenerateQuestionsResult>('/api/generate-questions', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          parsed_cv: parsedCV,
          parsed_jd: parsedJD,
          score_result: scoreResult,
          language
        }
      })

      return data
    } catch (error) {
      console.error('Error generating questions:', error)
      throw error
    }
  }

  return {
    generateQuestions
  }
}
