import { describe, it, expect, beforeEach } from 'vitest'
import { useAnalysisState } from '~/composables/analysis/useAnalysisState'
import type { ParsedJobResult, ParsedCVResult, QuestionItem, GenerateQuestionsResult, SubmitAnswersResult, ResumeRewriteResult, CoverLetterResult } from '~/composables/analysis/useAnalysisState'
import type { ScoreResponse } from '~/composables/analysis/useScoreCalculator'
import type { AdaptiveQuestionState } from '~/types/adaptive-questions'

describe('useAnalysisState', () => {
  let state: ReturnType<typeof useAnalysisState>

  beforeEach(() => {
    // Clear all Nuxt useState instances between tests
    ;(global as any).clearAllState()

    // Create fresh instance
    state = useAnalysisState()
  })

  describe('Initial State', () => {
    it('should initialize with empty input fields', () => {
      expect(state.inputJD.value).toBe('')
      expect(state.inputCV.value).toBe('')
      expect(state.selectedLanguage.value).toBe('english')
    })

    it('should initialize with null parsed results', () => {
      expect(state.parsedJD.value).toBeNull()
      expect(state.parsedCV.value).toBeNull()
      expect(state.scoreResult.value).toBeNull()
    })

    it('should initialize with empty questions and answers', () => {
      expect(state.questionsResult.value).toBeNull()
      expect(state.answers.value).toEqual([])
      expect(state.answersResult.value).toBeNull()
    })

    it('should initialize with adaptive flow enabled', () => {
      expect(state.useAdaptiveFlow.value).toBe(true)
    })

    it('should initialize with pending steps', () => {
      expect(state.steps.value).toHaveLength(6)
      state.steps.value.forEach(step => {
        expect(step.status).toBe('pending')
        expect(step.progress).toBe(0)
      })
    })

    it('should initialize with job-parsing as selected step', () => {
      expect(state.selectedStepId.value).toBe('job-parsing')
    })
  })

  describe('setInput', () => {
    it('should set input data with default language', () => {
      const jd = 'Senior Software Engineer job...'
      const cv = 'John Doe resume...'

      state.setInput(jd, cv)

      expect(state.inputJD.value).toBe(jd)
      expect(state.inputCV.value).toBe(cv)
      expect(state.selectedLanguage.value).toBe('english')
    })

    it('should set input data with custom language', () => {
      const jd = 'Ingénieur logiciel senior...'
      const cv = 'Jean Dupont CV...'

      state.setInput(jd, cv, 'french')

      expect(state.inputJD.value).toBe(jd)
      expect(state.inputCV.value).toBe(cv)
      expect(state.selectedLanguage.value).toBe('french')
    })
  })

  describe('setParsedJD', () => {
    it('should set parsed job description and time', () => {
      const mockParsedJD: ParsedJobResult = {
        company_name: 'Tech Corp',
        position_title: 'Senior Engineer',
        location: 'Remote',
        work_mode: 'remote',
        salary_range: '$120k-$180k',
        experience_years_required: 5,
        experience_level: 'senior',
        hard_skills_required: [{ skill: 'TypeScript', priority: 'must-have' }],
        soft_skills_required: ['leadership'],
        responsibilities: ['Lead team'],
        tech_stack: ['React', 'Node.js'],
        domain_expertise: { industry: ['tech'], specific_knowledge: ['web'] },
        implicit_requirements: [],
        company_culture_signals: [],
        ats_keywords: []
      }

      state.setParsedJD(mockParsedJD, 2.5)

      expect(state.parsedJD.value).toEqual(mockParsedJD)
      expect(state.jdParseTime.value).toBe(2.5)
    })
  })

  describe('setParsedCV', () => {
    it('should set parsed CV and time', () => {
      const mockParsedCV: ParsedCVResult = {
        personal_info: {
          name: 'John Doe',
          email: 'john@example.com',
          phone: '555-0100',
          location: 'San Francisco',
          linkedin: 'linkedin.com/in/johndoe',
          github: 'github.com/johndoe',
          portfolio: 'johndoe.com'
        },
        professional_summary: 'Experienced software engineer...',
        technical_skills: ['TypeScript', 'React'],
        tools: ['Git', 'Docker'],
        soft_skills: ['communication'],
        work_experience: [],
        education: [],
        projects: [],
        certifications: [],
        languages: [],
        internships: [],
        publications: []
      }

      state.setParsedCV(mockParsedCV, 3.2)

      expect(state.parsedCV.value).toEqual(mockParsedCV)
      expect(state.cvParseTime.value).toBe(3.2)
    })
  })

  describe('setScore', () => {
    it('should set score result and time', () => {
      const mockScore: ScoreResponse = {
        overall_score: 82,
        category_scores: {
          hard_skills: 85,
          soft_skills: 75,
          experience_level: 90,
          domain_expertise: 80,
          industry_match: 70,
          role_similarity: 85,
          portfolio_quality: 75,
          location_logistics: 100
        },
        gaps: {
          critical: [],
          important: [],
          nice_to_have: [],
          logistical: []
        },
        strengths: [],
        application_viability: {
          should_apply: true,
          confidence: 'high',
          reasoning: 'Strong match',
          success_probability: 85
        },
        recommendations: [],
        time_seconds: 4.5,
        model: 'gemini-2.0-flash'
      }

      state.setScore(mockScore, 4.5)

      expect(state.scoreResult.value).toEqual(mockScore)
      expect(state.scoreCalcTime.value).toBe(4.5)
    })
  })

  describe('setQuestions', () => {
    it('should set questions result and time', () => {
      const mockQuestions: GenerateQuestionsResult = {
        success: true,
        questions: [
          {
            id: 'q1',
            number: 1,
            title: 'React Experience',
            priority: 'CRITICAL',
            impact: 'High impact on application',
            question_text: 'Describe your React experience',
            context_why: 'Required for this role',
            examples: ['Example 1']
          }
        ],
        total_questions: 1,
        critical_count: 1,
        high_count: 0,
        medium_count: 0,
        rag_context_used: true,
        time_seconds: 2.1,
        model: 'gemini-2.5-flash'
      }

      state.setQuestions(mockQuestions, 2.1)

      expect(state.questionsResult.value).toEqual(mockQuestions)
      expect(state.questionsGenTime.value).toBe(2.1)
    })
  })

  describe('setAnswer', () => {
    it('should add new text answer', () => {
      state.setAnswer('q1', 'I have 5 years of React experience', 'text')

      expect(state.answers.value).toHaveLength(1)
      expect(state.answers.value[0]).toEqual({
        question_id: 'q1',
        answer_text: 'I have 5 years of React experience',
        answer_type: 'text',
        transcription_time: undefined
      })
    })

    it('should add new voice answer with transcription time', () => {
      state.setAnswer('q1', 'Transcribed voice answer', 'voice', 1.5)

      expect(state.answers.value).toHaveLength(1)
      expect(state.answers.value[0]).toEqual({
        question_id: 'q1',
        answer_text: 'Transcribed voice answer',
        answer_type: 'voice',
        transcription_time: 1.5
      })
    })

    it('should update existing answer', () => {
      state.setAnswer('q1', 'First answer', 'text')
      state.setAnswer('q1', 'Updated answer', 'text')

      expect(state.answers.value).toHaveLength(1)
      expect(state.answers.value[0]?.answer_text).toBe('Updated answer')
    })

    it('should handle multiple answers for different questions', () => {
      state.setAnswer('q1', 'Answer 1', 'text')
      state.setAnswer('q2', 'Answer 2', 'voice', 2.0)
      state.setAnswer('q3', 'Answer 3', 'text')

      expect(state.answers.value).toHaveLength(3)
      expect(state.answers.value.map(a => a.question_id)).toEqual(['q1', 'q2', 'q3'])
    })
  })

  describe('setAnswersResult', () => {
    it('should set answers analysis result and time', () => {
      const mockResult: SubmitAnswersResult = {
        success: true,
        updated_score: 87,
        score_improvement: 5,
        category_improvements: { hard_skills: 3, soft_skills: 2 },
        uncovered_experiences: ['Led team of 5 engineers'],
        updated_cv: { skills: ['React', 'Node.js'] },
        time_seconds: 6.3,
        model: 'gemini-2.0-flash'
      }

      state.setAnswersResult(mockResult, 6.3)

      expect(state.answersResult.value).toEqual(mockResult)
      expect(state.answersAnalysisTime.value).toBe(6.3)
    })
  })

  describe('Adaptive Question State Management', () => {
    it('should set adaptive question state', () => {
      const mockState: AdaptiveQuestionState = {
        questionId: 'q1',
        status: 'deep_dive',
        experienceLevel: 'some',
        deepDivePrompts: [],
        userInputs: {},
        generatedAnswer: null,
        qualityScore: null,
        qualityIssues: [],
        improvementSuggestions: [],
        refinementIteration: 0
      }

      state.setAdaptiveQuestionState('q1', mockState)

      const retrieved = state.getAdaptiveQuestionState('q1')
      expect(retrieved).toEqual(mockState)
    })

    it('should get undefined for non-existent question', () => {
      const retrieved = state.getAdaptiveQuestionState('non-existent')
      expect(retrieved).toBeUndefined()
    })

    it('should clear specific adaptive question state', () => {
      const mockState: AdaptiveQuestionState = {
        questionId: 'q1',
        status: 'completed',
        experienceLevel: 'intermediate',
        deepDivePrompts: [],
        userInputs: {},
        generatedAnswer: 'Answer',
        qualityScore: 8,
        qualityIssues: [],
        improvementSuggestions: [],
        refinementIteration: 0
      }

      state.setAdaptiveQuestionState('q1', mockState)
      state.clearAdaptiveQuestionState('q1')

      expect(state.getAdaptiveQuestionState('q1')).toBeUndefined()
    })

    it('should clear all adaptive question states', () => {
      const mockState1: AdaptiveQuestionState = {
        questionId: 'q1',
        status: 'completed',
        experienceLevel: 'some',
        deepDivePrompts: [],
        userInputs: {},
        generatedAnswer: null,
        qualityScore: null,
        qualityIssues: [],
        improvementSuggestions: [],
        refinementIteration: 0
      }
      const mockState2: AdaptiveQuestionState = {
        ...mockState1,
        questionId: 'q2'
      }

      state.setAdaptiveQuestionState('q1', mockState1)
      state.setAdaptiveQuestionState('q2', mockState2)

      state.clearAllAdaptiveQuestionStates()

      expect(state.adaptiveQuestionStates.value.size).toBe(0)
    })
  })

  describe('setRewrittenResume', () => {
    it('should set rewritten resume result', () => {
      const mockResume: ResumeRewriteResult = {
        success: true,
        sample_format: { resumeId: 'r1', content: {} },
        parsed_format: { personal_info: {} },
        enhancements_made: ['Added metrics', 'Optimized keywords'],
        time_seconds: 8.5,
        model: 'gemini-2.0-flash'
      }

      state.setRewrittenResume(mockResume)

      expect(state.rewrittenResume.value).toEqual(mockResume)
    })
  })

  describe('setCoverLetter', () => {
    it('should set cover letter result', () => {
      const mockCoverLetter: CoverLetterResult = {
        success: true,
        cover_letter: 'Dear Hiring Manager...',
        word_count: 350,
        time_seconds: 5.2,
        model: 'gemini-2.0-flash'
      }

      state.setCoverLetter(mockCoverLetter)

      expect(state.coverLetter.value).toEqual(mockCoverLetter)
    })
  })

  describe('updateStepProgress', () => {
    it('should update step status to loading', () => {
      state.updateStepProgress('job-parsing', 50, 'loading')

      const step = state.steps.value.find(s => s.id === 'job-parsing')
      expect(step?.status).toBe('loading')
      expect(step?.progress).toBe(50)
    })

    it('should update step status to complete', () => {
      state.updateStepProgress('cv-parsing', 100, 'complete')

      const step = state.steps.value.find(s => s.id === 'cv-parsing')
      expect(step?.status).toBe('complete')
      expect(step?.progress).toBe(100)
    })

    it('should update step with error', () => {
      const errorMsg = 'Failed to parse job description'
      state.updateStepProgress('job-parsing', 0, 'error', errorMsg)

      const step = state.steps.value.find(s => s.id === 'job-parsing')
      expect(step?.status).toBe('error')
      expect(step?.error).toBe(errorMsg)
    })

    it('should handle non-existent step gracefully', () => {
      // Should not throw error
      expect(() => {
        state.updateStepProgress('non-existent', 50, 'loading')
      }).not.toThrow()
    })
  })

  describe('toggleWorkflowMode', () => {
    it('should toggle from adaptive to legacy', () => {
      expect(state.useAdaptiveFlow.value).toBe(true)

      state.toggleWorkflowMode()

      expect(state.useAdaptiveFlow.value).toBe(false)
    })

    it('should toggle from legacy to adaptive', () => {
      state.useAdaptiveFlow.value = false

      state.toggleWorkflowMode()

      expect(state.useAdaptiveFlow.value).toBe(true)
    })

    it('should toggle multiple times', () => {
      const initial = state.useAdaptiveFlow.value

      state.toggleWorkflowMode()
      expect(state.useAdaptiveFlow.value).toBe(!initial)

      state.toggleWorkflowMode()
      expect(state.useAdaptiveFlow.value).toBe(initial)
    })
  })

  describe('reset', () => {
    it('should reset all state to initial values', () => {
      // Set up some state
      state.setInput('Job description', 'Resume', 'french')
      state.setAnswer('q1', 'Answer', 'text')
      state.setParsedJD({
        company_name: 'Test',
        position_title: 'Engineer',
        location: 'Remote',
        work_mode: 'remote',
        salary_range: null,
        experience_years_required: 3,
        experience_level: 'mid',
        hard_skills_required: [],
        soft_skills_required: [],
        responsibilities: [],
        tech_stack: [],
        domain_expertise: { industry: [], specific_knowledge: [] },
        implicit_requirements: [],
        company_culture_signals: [],
        ats_keywords: []
      }, 2.0)
      state.updateStepProgress('job-parsing', 100, 'complete')
      state.selectedStepId.value = 'cv-parsing'

      // Reset
      state.reset()

      // Verify everything is reset
      expect(state.inputJD.value).toBe('')
      expect(state.inputCV.value).toBe('')
      expect(state.selectedLanguage.value).toBe('english')
      expect(state.parsedJD.value).toBeNull()
      expect(state.parsedCV.value).toBeNull()
      expect(state.scoreResult.value).toBeNull()
      expect(state.answers.value).toEqual([])
      expect(state.answersResult.value).toBeNull()
      expect(state.adaptiveQuestionStates.value.size).toBe(0)
      expect(state.rewrittenResume.value).toBeNull()
      expect(state.coverLetter.value).toBeNull()
      expect(state.selectedStepId.value).toBe('job-parsing')
      expect(state.steps.value.every(s => s.status === 'pending' && s.progress === 0)).toBe(true)
    })
  })

  describe('Readonly State Properties', () => {
    it('should expose state as readonly', () => {
      // These should be readonly and not directly mutable
      // TypeScript would catch this at compile time, but we can verify structure
      expect(state.inputJD).toHaveProperty('value')
      expect(state.parsedJD).toHaveProperty('value')
      expect(state.steps).toHaveProperty('value')
    })
  })

  describe('Complete Workflow Simulation', () => {
    it('should handle complete analysis workflow', () => {
      // Step 1: Input
      state.setInput('Senior React Developer...', 'John Doe, React expert...', 'english')
      expect(state.inputJD.value).toBeTruthy()

      // Step 2: Parse JD
      state.updateStepProgress('job-parsing', 50, 'loading')
      state.setParsedJD({
        company_name: 'Tech Corp',
        position_title: 'Senior React Developer',
        location: 'Remote',
        work_mode: 'remote',
        salary_range: '$150k',
        experience_years_required: 5,
        experience_level: 'senior',
        hard_skills_required: [{ skill: 'React', priority: 'must-have' }],
        soft_skills_required: [],
        responsibilities: [],
        tech_stack: ['React'],
        domain_expertise: { industry: [], specific_knowledge: [] },
        implicit_requirements: [],
        company_culture_signals: [],
        ats_keywords: []
      }, 2.3)
      state.updateStepProgress('job-parsing', 100, 'complete')

      // Step 3: Parse CV
      state.updateStepProgress('cv-parsing', 100, 'complete')

      // Step 4: Score
      state.setScore({
        overall_score: 85,
        category_scores: {
          hard_skills: 90,
          soft_skills: 80,
          experience_level: 85,
          domain_expertise: 80,
          industry_match: 80,
          role_similarity: 90,
          portfolio_quality: 85,
          location_logistics: 100
        },
        gaps: { critical: [], important: [], nice_to_have: [], logistical: [] },
        strengths: [],
        application_viability: {
          should_apply: true,
          confidence: 'high',
          reasoning: 'Great match',
          success_probability: 90
        },
        recommendations: [],
        time_seconds: 3.5,
        model: 'gemini-2.0-flash'
      }, 3.5)
      state.updateStepProgress('score-calc', 100, 'complete')

      // Step 5: Questions
      state.setQuestions({
        success: true,
        questions: [],
        total_questions: 5,
        critical_count: 2,
        high_count: 2,
        medium_count: 1,
        rag_context_used: true,
        time_seconds: 2.8,
        model: 'gemini-2.5-flash'
      }, 2.8)

      // Step 6: Answers
      state.setAnswer('q1', 'Answer 1', 'text')
      state.setAnswer('q2', 'Answer 2', 'voice', 1.2)

      // Verify workflow state
      expect(state.parsedJD.value?.company_name).toBe('Tech Corp')
      expect(state.scoreResult.value?.overall_score).toBe(85)
      expect(state.questionsResult.value?.total_questions).toBe(5)
      expect(state.answers.value).toHaveLength(2)

      const jobParsingStep = state.steps.value.find(s => s.id === 'job-parsing')
      expect(jobParsingStep?.status).toBe('complete')
    })
  })
})
