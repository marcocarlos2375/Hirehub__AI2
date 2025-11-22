import type { ScoreResponse } from './useScoreCalculator'

export interface AnalysisStep {
  id: string
  label: string
  status: 'pending' | 'loading' | 'complete' | 'error'
  progress: number
  error?: string
}

export interface ParsedJobResult {
  company_name: string
  position_title: string
  location: string
  work_mode: string
  salary_range: string | null
  experience_years_required: number
  experience_level: string | null
  hard_skills_required: Array<{ skill: string; priority: string }>
  soft_skills_required: string[]
  responsibilities: string[]
  tech_stack: string[]
  domain_expertise: {
    industry: string[]
    specific_knowledge: string[]
  }
  implicit_requirements: string[]
  company_culture_signals: string[]
  ats_keywords: string[]
}

export interface ParsedCVResult {
  personal_info: {
    name: string
    email: string | null
    phone: string | null
    location: string | null
    linkedin: string | null
    github: string | null
    portfolio: string | null
  }
  professional_summary: string | null
  technical_skills: string[]
  tools: string[]
  soft_skills: string[]
  work_experience: Array<{
    role: string
    company: string
    location: string | null
    start_date: string
    end_date: string
    duration: string
    achievements: string[]
  }>
  education: Array<{
    degree: string
    institution: string
    location: string | null
    graduation_date: string | null
    gpa: string | null
    honors: string | null
  }>
  projects: Array<{
    name: string
    description: string
    technologies: string[]
    link: string | null
  }>
  certifications: string[]
  languages: Array<{
    language: string
    proficiency: string
  }>
  internships: Array<{
    role: string
    company: string
    duration: string
    description: string
  }>
  publications: Array<{
    title: string
    publication: string
    date: string | null
    link: string | null
  }>
}

// Phase 4 interfaces
export interface QuestionItem {
  id: string
  number: number
  title: string
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM'
  impact: string
  question_text: string
  context_why: string
  examples: string[]
}

export interface QuestionAnswer {
  question_id: string
  answer_text: string
  answer_type: 'text' | 'voice'
  transcription_time?: number
}

export interface GenerateQuestionsResult {
  success: boolean
  questions: QuestionItem[]
  total_questions: number
  critical_count: number
  high_count: number
  medium_count: number
  rag_context_used: boolean
  time_seconds: number
  model: string
}

export interface SubmitAnswersResult {
  success: boolean
  updated_score: number
  score_improvement: number
  category_improvements: Record<string, number>
  uncovered_experiences: string[]
  updated_cv: Record<string, any>
  time_seconds: number
  model: string
}

// Phase 5: Resume Rewrite
export interface ResumeRewriteResult {
  success: boolean
  sample_format: Record<string, any>  // camelCase, HTML descriptions
  parsed_format: Record<string, any>  // snake_case, plain text
  enhancements_made: string[]
  time_seconds: number
  model: string
}

export const useAnalysisState = () => {
  // Input data
  const inputJD = useState<string>('inputJD', () => '')
  const inputCV = useState<string>('inputCV', () => '')
  const selectedLanguage = useState<string>('selectedLanguage', () => 'english')

  // Parsed results
  const parsedJD = useState<ParsedJobResult | null>('parsedJD', () => null)
  const parsedCV = useState<ParsedCVResult | null>('parsedCV', () => null)
  const scoreResult = useState<ScoreResponse | null>('scoreResult', () => null)

  // Phase 4: Questions & Answers
  const questionsResult = useState<GenerateQuestionsResult | null>('questionsResult', () => null)
  const answers = useState<QuestionAnswer[]>('answers', () => [])
  const answersResult = useState<SubmitAnswersResult | null>('answersResult', () => null)

  // Phase 5: Resume Rewrite
  const rewrittenResume = useState<ResumeRewriteResult | null>('rewrittenResume', () => null)

  // Processing times
  const jdParseTime = useState<number | null>('jdParseTime', () => null)
  const cvParseTime = useState<number | null>('cvParseTime', () => null)
  const scoreCalcTime = useState<number | null>('scoreCalcTime', () => null)
  const questionsGenTime = useState<number | null>('questionsGenTime', () => null)
  const answersAnalysisTime = useState<number | null>('answersAnalysisTime', () => null)

  // Analysis steps
  const steps = useState<AnalysisStep[]>('analysisSteps', () => [
    { id: 'job-parsing', label: 'Job Parsing', status: 'pending', progress: 0 },
    { id: 'cv-parsing', label: 'Resume Parsing', status: 'pending', progress: 0 },
    { id: 'score-calc', label: 'Score Calculating', status: 'pending', progress: 0 },
    { id: 'smart-questions', label: 'Smart Questions', status: 'pending', progress: 0 },
    { id: 'resume-rewrite', label: 'Resume Rewrite', status: 'pending', progress: 0 }
  ])

  // Currently selected step
  const selectedStepId = useState<string>('selectedStepId', () => 'job-parsing')

  // Methods
  const setInput = (jd: string, cv: string, language: string = 'english') => {
    inputJD.value = jd
    inputCV.value = cv
    selectedLanguage.value = language
  }

  const setParsedJD = (data: ParsedJobResult, timeSeconds: number) => {
    parsedJD.value = data
    jdParseTime.value = timeSeconds
  }

  const setParsedCV = (data: ParsedCVResult, timeSeconds: number) => {
    parsedCV.value = data
    cvParseTime.value = timeSeconds
  }

  const setScore = (data: ScoreResponse, timeSeconds: number) => {
    scoreResult.value = data
    scoreCalcTime.value = timeSeconds
  }

  const setQuestions = (data: GenerateQuestionsResult, timeSeconds: number) => {
    questionsResult.value = data
    questionsGenTime.value = timeSeconds
  }

  const setAnswer = (questionId: string, answerText: string, answerType: 'text' | 'voice', transcriptionTime?: number) => {
    const existingIndex = answers.value.findIndex(a => a.question_id === questionId)
    const newAnswer: QuestionAnswer = {
      question_id: questionId,
      answer_text: answerText,
      answer_type: answerType,
      transcription_time: transcriptionTime
    }

    if (existingIndex !== -1) {
      answers.value[existingIndex] = newAnswer
    } else {
      answers.value.push(newAnswer)
    }
  }

  const setAnswersResult = (data: SubmitAnswersResult, timeSeconds: number) => {
    answersResult.value = data
    answersAnalysisTime.value = timeSeconds
  }

  const setRewrittenResume = (data: ResumeRewriteResult) => {
    rewrittenResume.value = data
  }

  const updateStepProgress = (stepId: string, progress: number, status: AnalysisStep['status'], error?: string) => {
    const stepIndex = steps.value.findIndex(s => s.id === stepId)
    if (stepIndex !== -1) {
      const currentStep = steps.value[stepIndex]
      if (currentStep) {
        steps.value[stepIndex] = {
          id: currentStep.id,
          label: currentStep.label,
          progress,
          status,
          error
        }
      }
    }
  }

  const reset = () => {
    inputJD.value = ''
    inputCV.value = ''
    selectedLanguage.value = 'english'
    parsedJD.value = null
    parsedCV.value = null
    scoreResult.value = null
    questionsResult.value = null
    answers.value = []
    answersResult.value = null
    rewrittenResume.value = null
    jdParseTime.value = null
    cvParseTime.value = null
    scoreCalcTime.value = null
    questionsGenTime.value = null
    answersAnalysisTime.value = null
    steps.value = [
      { id: 'job-parsing', label: 'Job Parsing', status: 'pending', progress: 0 },
      { id: 'cv-parsing', label: 'Resume Parsing', status: 'pending', progress: 0 },
      { id: 'score-calc', label: 'Score Calculating', status: 'pending', progress: 0 },
      { id: 'smart-questions', label: 'Smart Questions', status: 'pending', progress: 0 },
      { id: 'resume-rewrite', label: 'Resume Rewrite', status: 'pending', progress: 0 }
    ]
    selectedStepId.value = 'job-parsing'
  }

  return {
    // State
    inputJD: readonly(inputJD),
    inputCV: readonly(inputCV),
    selectedLanguage: readonly(selectedLanguage),
    parsedJD: readonly(parsedJD),
    parsedCV: readonly(parsedCV),
    scoreResult: readonly(scoreResult),
    questionsResult: readonly(questionsResult),
    answers: readonly(answers),
    answersResult: readonly(answersResult),
    rewrittenResume: readonly(rewrittenResume),
    jdParseTime: readonly(jdParseTime),
    cvParseTime: readonly(cvParseTime),
    scoreCalcTime: readonly(scoreCalcTime),
    questionsGenTime: readonly(questionsGenTime),
    answersAnalysisTime: readonly(answersAnalysisTime),
    steps: readonly(steps),
    selectedStepId,

    // Methods
    setInput,
    setParsedJD,
    setParsedCV,
    setScore,
    setQuestions,
    setAnswer,
    setAnswersResult,
    setRewrittenResume,
    updateStepProgress,
    reset
  }
}
