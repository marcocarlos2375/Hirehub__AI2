/**
 * TypeScript types for Adaptive Questions System
 */

// Experience check response types
export type ExperienceLevel = 'yes' | 'no' | 'willing_to_learn'

// Workflow steps
export type WorkflowStep = 'check' | 'deep_dive' | 'resources' | 'answer_generation' | 'quality_evaluation' | 'quality_eval' | 'complete'

// Deep dive prompt types
export type PromptType = 'text' | 'textarea' | 'select' | 'multiselect' | 'number'

export interface DeepDivePrompt {
  id: string
  type: PromptType
  question: string
  placeholder?: string
  options?: string[]
  required: boolean
  help_text?: string
}

// Learning resource interfaces
export interface LearningResource {
  id: string
  title: string
  description: string
  type: string // 'course' | 'project' | 'certification'
  provider: string
  url: string
  duration_days: number
  difficulty: string // 'beginner' | 'intermediate' | 'advanced'
  cost: string // 'free' | 'paid' | 'freemium'
  skills_covered: string[]
  rating?: number
  score?: number
}

export interface TimelineStep {
  resource_id: string
  resource_title: string
  type: string
  start_day: number
  end_day: number
  duration_days: number
}

// Quality evaluation
export interface QualityEvaluation {
  quality_score: number
  quality_issues?: string[]
  quality_strengths?: string[]
  improvement_suggestions?: Array<{
    issue: string
    suggestion: string
    priority: string
  }>
  is_acceptable: boolean
}

// Adaptive question state
export interface AdaptiveQuestionState {
  questionId: string
  gapTitle: string
  gapDescription: string
  experienceCheck: ExperienceLevel | null
  currentStep: WorkflowStep

  // Deep dive path
  deepDivePrompts?: DeepDivePrompt[]
  deepDiveData?: Record<string, any>
  generatedAnswer?: string
  qualityEvaluation?: QualityEvaluation
  // Flattened quality evaluation properties (for backward compatibility)
  qualityScore?: number
  qualityIssues?: string[]
  qualityStrengths?: string[]
  improvementSuggestions?: Array<{
    issue: string
    suggestion: string
    priority: string
  }>
  finalAnswer?: string

  // Learning resources path
  suggestedResources?: LearningResource[]
  selectedResourceIds?: string[]
  timeline?: TimelineStep[]
  planId?: string
  resumeAddition?: string

  // Metadata
  refinementIteration: number
  error?: string
  loading: boolean
}

// API Request/Response types
export interface StartWorkflowRequest {
  question_id: string
  question_text: string
  question_data: Record<string, any>
  gap_info: {
    title: string
    description: string
  }
  user_id: string
  parsed_cv: Record<string, any>
  parsed_jd: Record<string, any>
  experience_check_response: ExperienceLevel
  language?: string
}

export interface StartWorkflowResponse {
  question_id: string
  current_step: string
  deep_dive_prompts?: DeepDivePrompt[]
  suggested_resources?: LearningResource[]
  resume_addition?: string
  error?: string
}

export interface SubmitInputsRequest {
  question_id: string
  structured_data: Record<string, any>
}

export interface SubmitInputsResponse {
  question_id: string
  generated_answer: string
  quality_score: number
  quality_issues?: string[]
  quality_strengths?: string[]
  improvement_suggestions?: Array<{
    issue: string
    suggestion: string
    priority: string
  }>
  final_answer?: string
  current_step: string
  error?: string
}

export interface RefineAnswerRequest {
  question_id: string
  additional_data: Record<string, any>
}

export interface RefineAnswerResponse {
  question_id: string
  refined_answer: string
  quality_score: number
  quality_issues?: string[]
  quality_strengths?: string[]
  improvement_suggestions?: Array<{
    issue: string
    suggestion: string
    priority: string
  }>
  is_acceptable: boolean
  final_answer?: string
  current_step: string
  iteration: number
  error?: string
}

export interface SaveLearningPlanRequest {
  user_id: string
  gap_info: {
    title: string
    description: string
  }
  selected_resource_ids: string[]
  notes?: string
}

export interface SaveLearningPlanResponse {
  plan_id: string
  status: string
  error?: string
}

export interface LearningPlanItem {
  id: string
  gap_title: string
  gap_description: string
  resource_ids: string[]
  resources?: LearningResource[]
  status: string
  created_at: string
  notes?: string
}

// Helper type for form validation
export interface FormField {
  id: string
  value: any
  error?: string
  touched: boolean
}

// Event emitter types
export interface AdaptiveQuestionEvents {
  'experience-selected': (level: ExperienceLevel) => void
  'submit-inputs': (data: Record<string, any>) => void
  'refine-answer': (data: Record<string, any>) => void
  'accept-answer': (answer: string) => void
  'save-plan': (resourceIds: string[]) => void
  'answer-completed': (state: AdaptiveQuestionState) => void
  'plan-saved': (planId: string) => void
  'error': (error: string) => void
}
