import type { ResumeRewriteResult, QuestionAnswer, QuestionItem } from './useAnalysisState'

export const useResumeRewriter = () => {
  const config = useRuntimeConfig()

  const rewriteResume = async (
    updatedCV: Record<string, any>,
    questions: QuestionItem[],
    answers: QuestionAnswer[],
    parsedJD: Record<string, any>,
    language: string = 'english'
  ): Promise<ResumeRewriteResult | null> => {
    try {
      const response = await $fetch<ResumeRewriteResult>('/api/rewrite-resume', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          updated_cv: updatedCV,
          questions: questions,
          answers: answers,
          parsed_jd: parsedJD,
          language: language
        }
      })

      return response
    } catch (error) {
      console.error('Failed to rewrite resume:', error)
      throw error
    }
  }

  return {
    rewriteResume
  }
}
