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

// Quality feedback item with label and description
export interface QualityFeedbackItem {
  label: string
  description: string
}

// Improvement suggestion with title and examples
export interface ImprovementSuggestion {
  type: string
  title: string
  examples: string[]
  help_text: string
}

// Quality evaluation
export interface QualityEvaluation {
  quality_score: number
  quality_issues?: QualityFeedbackItem[]
  quality_strengths?: QualityFeedbackItem[]
  improvement_suggestions?: ImprovementSuggestion[]
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
  qualityIssues?: QualityFeedbackItem[]
  qualityStrengths?: QualityFeedbackItem[]
  improvementSuggestions?: ImprovementSuggestion[]
  finalAnswer?: string
  formattedAnswer?: FormattedAnswer

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
  quality_issues: QualityFeedbackItem[]
  quality_strengths: QualityFeedbackItem[]
  improvement_suggestions?: ImprovementSuggestion[]
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
  quality_score: number | null  // Always null after refinement (no re-evaluation)
  current_step: string  // "answer_generation" (return to answer input)
  iteration: number  // Always 1
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

// Formatted answer with AI-generated structure - supports multiple CV entry types
export interface FormattedAnswer {
  type: 'project' | 'job' | 'course' | 'research' | 'volunteer' | 'publication' | 'certification' | 'award' | 'conference' | 'patent' | 'other'
  name: string  // Generated name/title appropriate for the type
  description?: string  // 2-3 sentence description (15-30 words)

  // Common metadata (all types)
  duration?: string  // Timeframe (e.g., "3 months", "2 years")
  date?: string  // Specific date (e.g., "June 2024", "2023")
  bullet_points: string[]  // 3-5 professional bullet points
  technologies: string[]  // Tech stack, tools, or relevant technologies

  // Job-specific
  company?: string  // Company name for jobs
  team_size?: string  // Team size for projects/jobs

  // Course-specific
  provider?: string  // Education provider for courses
  skills_gained?: string[]  // Skills learned from courses

  // Publication-specific
  publisher?: string  // Publisher/venue for publications
  authors?: string[]  // Co-authors for publications/patents

  // Certification/Award-specific
  issuer?: string  // Issuing organization
  credential_id?: string  // Credential ID for certifications

  // Conference-specific
  venue?: string  // Conference/event venue

  // General
  url?: string  // Verification/reference URL
  raw_answer: string  // Original refined answer
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

// Skill Gap Analysis types (for "No Experience" flow)
export interface SkillGapAnalysis {
  case: 'A' | 'B'
  skill_missing: string
  skill_exist: string | null
  intro: string  // Opening 1-3 sentences
  key_points: string[]  // 3-5 bullet points from original message
  message: string  // Full message (backward compatibility)
}
