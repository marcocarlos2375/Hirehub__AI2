/**
 * Centralized API Response Type Definitions
 *
 * These types eliminate `any` usage in composables and provide
 * type safety for all API interactions with the backend.
 *
 * IMPORTANT: These types must match the backend API response structure.
 * See Backend/app/main.py for the source of truth.
 */

/**
 * Parsed CV/Resume Structure
 *
 * Represents a parsed resume from the /api/parse-cv endpoint
 */
export interface ParsedCV {
  personal_info: {
    first_name: string
    last_name: string
    email: string
    phone?: string
    location?: string
    job_title?: string
    social_links?: {
      linkedin?: string
      github?: string
      portfolio?: string
      twitter?: string
    }
  }
  work_experience: Array<{
    job_title: string
    company: string
    location: string
    start_date: string
    end_date?: string
    responsibilities: string[]
    achievements?: string[]
    technologies?: string[]
  }>
  education: Array<{
    degree: string
    field_of_study?: string
    institution: string
    graduation_date: string
    gpa?: string
    honors?: string[]
  }>
  skills: Array<{
    skill: string
    proficiency?: string
    years_of_experience?: number
    category?: string
  }>
  projects?: Array<{
    title: string
    description: string
    technologies: string[]
    achievements?: string[]
    url?: string
    start_date?: string
    end_date?: string
  }>
  certifications?: Array<{
    title: string
    issuer: string
    date: string
    credential_id?: string
    url?: string
  }>
  languages?: Array<{
    language: string
    proficiency: string
  }>
  professional_summary?: string
  total_years_experience?: number
}

/**
 * Parsed Job Description Structure
 *
 * Represents a parsed job posting from the /api/parse endpoint
 */
export interface ParsedJobDescription {
  job_title: string
  company: string
  location?: string
  job_type?: string // 'full-time' | 'part-time' | 'contract' | 'remote'
  salary_range?: {
    min?: number
    max?: number
    currency?: string
  }
  required_skills: Array<{
    skill: string
    priority: string // 'must-have' | 'required' | 'important'
    years_required?: number
  }>
  preferred_skills?: Array<{
    skill: string
    priority: string // 'nice-to-have' | 'preferred' | 'bonus'
  }>
  responsibilities: string[]
  qualifications?: string[]
  experience_level: string // 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'principal'
  education_requirements?: string[]
  benefits?: string[]
  company_description?: string
  team_size?: string
  reports_to?: string
  remote_policy?: string
}

/**
 * Gap Information
 *
 * Represents a skill/experience gap identified during compatibility scoring
 */
export interface GapInfo {
  title: string
  description: string
  category: string // 'hard_skill' | 'soft_skill' | 'experience' | 'education' | 'certification'
  impact: string // 'critical' | 'important' | 'nice-to-have' | 'logistical'
  severity?: number // 0-10 scale
  suggestions?: string[]
}

/**
 * Question Data
 *
 * Represents a personalized question generated for the user
 */
export interface QuestionData {
  id: string
  text: string
  gap_info: GapInfo
  context: string
  examples?: string[]
  follow_up_questions?: string[]
  expected_answer_length?: string // 'short' | 'medium' | 'long'
  tips?: string[]
}

/**
 * Compatibility Score Result
 *
 * Complete scoring response from /api/calculate-score endpoint
 */
export interface CompatibilityScoreResult {
  overall_score: number // 0-100
  category_scores: {
    hard_skills: number
    soft_skills: number
    experience_level: number
    education: number
    domain_expertise: number
    industry_match: number
    role_similarity: number
    portfolio_quality: number
    location_logistics: number
  }
  gaps: {
    critical: GapInfo[]
    important: GapInfo[]
    nice_to_have: GapInfo[]
    logistical: GapInfo[]
  }
  strengths: Array<{
    category: string
    description: string
    evidence: string[]
  }>
  application_viability: {
    should_apply: boolean
    confidence: string // 'high' | 'medium' | 'low'
    reasoning: string
    success_probability: number // 0-100
  }
  recommendations: string[]
  time_seconds: number
  model: string
}

/**
 * Generated Questions Response
 *
 * Response from /api/adaptive-questions/start or /api/generate-questions
 */
export interface GeneratedQuestionsResponse {
  questions: QuestionData[]
  total_questions: number
  priority_order: string[] // Array of question IDs in priority order
  estimated_time_minutes: number
  time_seconds: number
  model: string
}

/**
 * Answer Evaluation Response
 *
 * Response from /api/evaluate-answer endpoint
 */
export interface AnswerEvaluationResponse {
  question_id: string
  answer_text: string
  quality_score: number // 0-10
  quality_issues: string[]
  quality_strengths: string[]
  improvement_suggestions: Array<{
    issue: string
    suggestion: string
    priority: string // 'high' | 'medium' | 'low'
  }>
  is_acceptable: boolean // quality_score >= 7
  time_seconds: number
  model: string
  error?: string
}

/**
 * Submit Answers Response
 *
 * Response from /api/submit-answers endpoint (legacy)
 */
export interface SubmitAnswersResponse {
  success: boolean
  score_improvement: {
    before: number
    after: number
    absolute_change: number
    percentage_change: number
  }
  category_improvements: Array<{
    category: string
    before: number
    after: number
    change: number
  }>
  uncovered_experiences?: string[]
  new_skills_identified?: string[]
  updated_cv: ParsedCV
  time_seconds: number
  model: string
  error?: string
}

/**
 * Resume Rewrite Response
 *
 * Response from /api/rewrite-resume endpoint
 */
export interface ResumeRewriteResponse {
  sample_format: {
    resumeId: string
    content: {
      personalInfo: {
        firstName: string
        lastName: string
        email: string
        phone?: string
        location?: string
        jobTitle?: string
        socialLinks?: {
          linkedin?: string
          github?: string
          portfolio?: string
        }
      }
      professionalSummary?: string
      employmentHistory: Array<{
        jobTitle: string
        company: string
        location: string
        startDate: string
        endDate?: string
        description: string // HTML formatted
      }>
      projects?: Array<{
        title: string
        description: string
        technologies: string[]
        achievements?: string[]
      }>
      skills: Array<{
        skill: string
        proficiency?: string
      }>
      education: Array<{
        degree: string
        institution: string
        graduationDate: string
        gpa?: string
      }>
      certifications?: Array<{
        title: string
        issuer: string
        date: string
      }>
    }
  }
  parsed_format: ParsedCV
  enhancements_made: string[]
  time_seconds: number
  model: string
}

/**
 * Cover Letter Response
 *
 * Response from /api/generate-cover-letter endpoint
 */
export interface CoverLetterResponse {
  cover_letter: string
  word_count: number
  time_seconds: number
  model: string
}

/**
 * Domain Finder Response
 *
 * Response from /api/find-domain endpoint
 */
export interface DomainFinderResponse {
  recommended_domains: Array<{
    domain: string
    match_score: number // 0-100
    reasoning: string
    career_paths: string[]
    required_skills: string[]
    salary_range?: string
    growth_potential: string // 'high' | 'medium' | 'low'
  }>
  time_seconds: number
  model: string
}

/**
 * Job Search Queries Response
 *
 * Response from /api/generate-job-search-queries endpoint
 */
export interface JobSearchQueriesResponse {
  queries: Array<{
    query: string
    platform: string // 'google' | 'linkedin' | 'indeed' | 'glassdoor' | 'generic'
    reasoning: string
  }>
  time_seconds: number
  model: string
}

/**
 * Audio Transcription Response
 *
 * Response from /api/transcribe-audio endpoint
 */
export interface AudioTranscriptionResponse {
  transcription: string
  confidence?: number
  language?: string
  duration_seconds?: number
  service: string // 'parakeet' | 'whisper'
  time_seconds: number
}

/**
 * Error Response
 *
 * Standard error response from any API endpoint
 */
export interface ApiErrorResponse {
  detail: string
  error: string
  status_code: number
  timestamp?: string
}
