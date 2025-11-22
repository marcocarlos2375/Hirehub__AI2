import type { GenerateQuestionsResult } from './useAnalysisState'

export const useQuestionGenerator = () => {
  const config = useRuntimeConfig()

  const generateQuestions = async (
    parsedCV: any,
    parsedJD: any,
    scoreResult: any,
    language: string = 'english'
  ): Promise<GenerateQuestionsResult | null> => {
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
