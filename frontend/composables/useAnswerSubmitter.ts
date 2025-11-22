import type { SubmitAnswersResult, QuestionItem, QuestionAnswer } from './useAnalysisState'

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
