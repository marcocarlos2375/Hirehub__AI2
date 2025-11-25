import type { SubmitAnswersResult, QuestionItem, QuestionAnswer } from '~/composables/analysis/useAnalysisState'

export const useAnswerSubmitter = () => {
  const config = useRuntimeConfig()

  const submitAnswers = async (
    parsedCV: any,
    parsedJD: any,
    questions: QuestionItem[],
    answers: QuestionAnswer[],
    originalScore: number,
    language: string = 'english'
  ): Promise<SubmitAnswersResult | null> => {
    // Deprecation warning
    console.warn(
      '[DEPRECATED] useAnswerSubmitter is being phased out. ' +
      'Please use the new adaptive questions workflow with individual answer evaluation. ' +
      'Toggle in settings or set useAdaptiveFlow = true in useAnalysisState'
    )

    try {
      const data = await $fetch<SubmitAnswersResult>('/api/submit-answers', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          parsed_cv: parsedCV,
          parsed_jd: parsedJD,
          questions,
          answers,
          original_score: originalScore,
          language
        }
      })

      return data
    } catch (error) {
      console.error('Error submitting answers:', error)
      throw error
    }
  }

  return {
    submitAnswers
  }
}
