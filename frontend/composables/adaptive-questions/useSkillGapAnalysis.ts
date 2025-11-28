import type { SkillGapAnalysis } from '~/types/adaptive-questions'

/**
 * Composable for analyzing skill gaps when user has no experience
 *
 * Calls backend AI to determine if user has related skills (Case A)
 * or needs to start from scratch (Case B)
 */
export const useSkillGapAnalysis = () => {
  const config = useRuntimeConfig()

  const analyzeSkillGap = async (
    questionId: string,
    questionTitle: string,
    parsedCv: Record<string, any>,
    parsedJd: Record<string, any>
  ): Promise<SkillGapAnalysis> => {
    try {
      const response = await $fetch<SkillGapAnalysis>(`${config.public.apiBase}/api/analyze-skill-gap`, {
        method: 'POST',
        body: {
          question_id: questionId,
          question_title: questionTitle,
          parsed_cv: parsedCv,
          parsed_jd: parsedJd
        }
      })

      return response
    } catch (error) {
      console.error('Error analyzing skill gap:', error)
      // Fallback to Case B if API fails
      return {
        case: 'B',
        skill_missing: questionTitle,
        skill_exist: null,
        message: `You don't have experience in ${questionTitle} yet, but you can start learning the basics right now while creating your CV. I can provide a quick 'Basics' learning module to help you understand the fundamentals. Once you complete the basics, you can add the skill to your CV at the 'Basics acquired' level. This way, you'll already have the foundations by the time a company contacts you. Would you like to begin the basics module?`
      }
    }
  }

  return {
    analyzeSkillGap
  }
}
