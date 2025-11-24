/**
 * Composable for adaptive question flow using LangGraph.
 *
 * Handles:
 * - Starting adaptive question workflow (deep dive OR learning resources)
 * - Submitting structured inputs (deep dive answers)
 * - Refining answers based on quality feedback
 * - Getting learning resources for gaps
 * - Saving/retrieving learning plans
 */

export interface DeepDivePromptItem {
  id: string
  type: 'text' | 'textarea' | 'select' | 'multiselect' | 'number'
  question: string
  placeholder?: string
  options?: string[]
  required: boolean
  help_text?: string
}

export interface LearningResourceItem {
  id: string
  title: string
  description: string
  type: 'course' | 'project' | 'certification'
  provider: string
  url: string
  duration_days: number
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  cost: 'free' | 'paid' | 'freemium'
  skills_covered: string[]
  rating?: number
}

export interface AdaptiveQuestionResponse {
  question_id: string
  current_step: string
  deep_dive_prompts?: DeepDivePromptItem[]
  suggested_resources?: LearningResourceItem[]
  resume_addition?: string
  error?: string
}

export interface StructuredInputsResponse {
  question_id: string
  generated_answer: string
  quality_score?: number
  quality_issues?: string[]
  quality_strengths?: string[]
  improvement_suggestions?: Array<{
    type: string
    prompt: string
    help_text?: string
  }>
  final_answer?: string
  current_step: string
  error?: string
}

export interface RefinementResponse {
  question_id: string
  refined_answer: string
  quality_score?: number
  final_answer?: string
  current_step: string
  iteration: number
  error?: string
}

export interface LearningPathStep {
  resource_id: string
  resource_title: string
  type: string
  start_day: number
  end_day: number
  duration_days: number
}

export interface LearningPath {
  timeline: LearningPathStep[]
  total_days: number
  estimated_completion: string
  resources_in_path: number
}

export interface LearningResourcesResponse {
  resources: LearningResourceItem[]
  learning_path: LearningPath
  total_resources: number
  total_duration_days: number
  estimated_completion: string
  error?: string
}

export interface LearningPlanItem {
  id: string
  gap_title: string
  gap_description: string
  resource_ids: string[]
  status: 'suggested' | 'in_progress' | 'completed' | 'abandoned'
  created_at: string
  notes?: string
}

export interface LearningPlansResponse {
  plans: LearningPlanItem[]
  total: number
}

export const useAdaptiveQuestions = () => {
  const config = useRuntimeConfig()

  /**
   * Start adaptive question workflow.
   *
   * @param questionId - Unique question identifier
   * @param questionText - The question text
   * @param questionData - Full question object
   * @param gapInfo - Gap information from scoring phase
   * @param userId - User identifier
   * @param parsedCV - Parsed CV data
   * @param parsedJD - Parsed job description data
   * @param experienceCheckResponse - "yes", "no", or "willing_to_learn"
   * @param language - Content language (default: "english")
   */
  const startAdaptiveQuestion = async (
    questionId: string,
    questionText: string,
    questionData: any,
    gapInfo: any,
    userId: string,
    parsedCV: any,
    parsedJD: any,
    experienceCheckResponse: 'yes' | 'no' | 'willing_to_learn',
    language: string = 'english'
  ): Promise<AdaptiveQuestionResponse> => {
    try {
      const data = await $fetch<AdaptiveQuestionResponse>('/api/adaptive-questions/start', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          question_id: questionId,
          question_text: questionText,
          question_data: questionData,
          gap_info: gapInfo,
          user_id: userId,
          parsed_cv: parsedCV,
          parsed_jd: parsedJD,
          experience_check_response: experienceCheckResponse,
          language
        }
      })

      return data
    } catch (error) {
      console.error('Error starting adaptive question:', error)
      throw error
    }
  }

  /**
   * Submit structured inputs (deep dive answers).
   *
   * @param questionId - Question identifier
   * @param structuredData - User's responses to deep dive prompts
   */
  const submitStructuredInputs = async (
    questionId: string,
    structuredData: Record<string, any>
  ): Promise<StructuredInputsResponse> => {
    try {
      const data = await $fetch<StructuredInputsResponse>('/api/adaptive-questions/submit-inputs', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          question_id: questionId,
          structured_data: structuredData
        }
      })

      return data
    } catch (error) {
      console.error('Error submitting structured inputs:', error)
      throw error
    }
  }

  /**
   * Refine answer based on quality feedback.
   *
   * @param questionId - Question identifier
   * @param refinementData - Additional data for answer improvement
   */
  const refineAnswer = async (
    questionId: string,
    refinementData: Record<string, any>
  ): Promise<RefinementResponse> => {
    try {
      const data = await $fetch<RefinementResponse>('/api/adaptive-questions/refine-answer', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          question_id: questionId,
          refinement_data: refinementData
        }
      })

      return data
    } catch (error) {
      console.error('Error refining answer:', error)
      throw error
    }
  }

  /**
   * Get learning resources for a gap.
   *
   * @param gap - Gap information
   * @param userLevel - User's current skill level (default: "intermediate")
   * @param maxDays - Maximum duration in days (default: 10)
   * @param costPreference - Cost filter (default: "any")
   * @param limit - Maximum number of resources (default: 5)
   */
  const getLearningResources = async (
    gap: any,
    userLevel: 'beginner' | 'intermediate' | 'advanced' = 'intermediate',
    maxDays: number = 10,
    costPreference: 'free' | 'paid' | 'any' = 'any',
    limit: number = 5
  ): Promise<LearningResourcesResponse> => {
    try {
      const data = await $fetch<LearningResourcesResponse>('/api/adaptive-questions/get-learning-resources', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          gap,
          user_level: userLevel,
          max_days: maxDays,
          cost_preference: costPreference,
          limit
        }
      })

      return data
    } catch (error) {
      console.error('Error getting learning resources:', error)
      throw error
    }
  }

  /**
   * Save a learning plan for the user.
   *
   * @param userId - User identifier
   * @param gap - Gap information
   * @param resourceIds - List of selected resource IDs
   * @param notes - Optional user notes
   */
  const saveLearningPlan = async (
    userId: string,
    gap: any,
    resourceIds: string[],
    notes?: string
  ): Promise<{ plan_id: string; success: boolean; error?: string }> => {
    try {
      const data = await $fetch<{ plan_id: string; success: boolean; error?: string }>('/api/adaptive-questions/save-learning-plan', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          user_id: userId,
          gap,
          resource_ids: resourceIds,
          notes
        }
      })

      return data
    } catch (error) {
      console.error('Error saving learning plan:', error)
      throw error
    }
  }

  /**
   * Get all learning plans for a user.
   *
   * @param userId - User identifier
   * @param status - Optional status filter
   */
  const getLearningPlans = async (
    userId: string,
    status?: 'suggested' | 'in_progress' | 'completed' | 'abandoned'
  ): Promise<LearningPlansResponse> => {
    try {
      const data = await $fetch<LearningPlansResponse>('/api/adaptive-questions/get-learning-plans', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          user_id: userId,
          status
        }
      })

      return data
    } catch (error) {
      console.error('Error getting learning plans:', error)
      throw error
    }
  }

  return {
    startAdaptiveQuestion,
    submitStructuredInputs,
    refineAnswer,
    getLearningResources,
    saveLearningPlan,
    getLearningPlans
  }
}
