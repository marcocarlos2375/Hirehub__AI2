import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useQuestionsStore } from '~/stores/questions/useQuestionsStore'
import type { AnswerEvaluation, QuestionAnswer, SubmitAnswersResult } from '~/stores/questions/useQuestionsStore'
import type { QuestionData, ParsedCV } from '~/types/api-responses'
import type { ExperienceLevel } from '~/types/adaptive-questions'

describe('useQuestionsStore', () => {
  beforeEach(() => {
    // Create a fresh Pinia instance for each test
    setActivePinia(createPinia())
  })

  describe('Initial State', () => {
    it('should initialize with empty answers', () => {
      const store = useQuestionsStore()
      expect(store.answers.size).toBe(0)
    })

    it('should initialize with empty evaluations', () => {
      const store = useQuestionsStore()
      expect(store.answerEvaluations.size).toBe(0)
    })

    it('should initialize with empty adaptive flows', () => {
      const store = useQuestionsStore()
      expect(store.activeAdaptiveFlows.size).toBe(0)
    })

    it('should initialize with no submission state', () => {
      const store = useQuestionsStore()
      expect(store.isSubmitting).toBe(false)
      expect(store.hasSubmitted).toBe(false)
      expect(store.answersResult).toBeNull()
    })

    it('should initialize with no evaluating question', () => {
      const store = useQuestionsStore()
      expect(store.evaluatingQuestionId).toBeNull()
    })

    it('should initialize with closed adaptive modal', () => {
      const store = useQuestionsStore()
      expect(store.showAdaptiveModal).toBe(false)
      expect(store.currentAdaptiveQuestion).toBeNull()
    })
  })

  describe('Answer Management', () => {
    it('should set text answer', () => {
      const store = useQuestionsStore()
      store.setAnswer('q1', 'I have 5 years of experience', 'text')

      const answer = store.getAnswerById('q1')
      expect(answer).toBeDefined()
      expect(answer?.answer_text).toBe('I have 5 years of experience')
      expect(answer?.answer_type).toBe('text')
      expect(answer?.question_id).toBe('q1')
    })

    it('should set voice answer with transcription time', () => {
      const store = useQuestionsStore()
      store.setAnswer('q1', 'Transcribed answer', 'voice', 2.5)

      const answer = store.getAnswerById('q1')
      expect(answer?.answer_type).toBe('voice')
      expect(answer?.transcription_time).toBe(2.5)
    })

    it('should check if question is answered', () => {
      const store = useQuestionsStore()
      expect(store.isQuestionAnswered('q1')).toBe(false)

      store.setAnswer('q1', 'Answer', 'text')
      expect(store.isQuestionAnswered('q1')).toBe(true)
    })

    it('should check if all questions are answered', () => {
      const store = useQuestionsStore()
      expect(store.allQuestionsAnswered(3)).toBe(false)

      store.setAnswer('q1', 'Answer 1', 'text')
      store.setAnswer('q2', 'Answer 2', 'text')
      expect(store.allQuestionsAnswered(3)).toBe(false)

      store.setAnswer('q3', 'Answer 3', 'text')
      expect(store.allQuestionsAnswered(3)).toBe(true)
    })

    it('should get all answers as array', () => {
      const store = useQuestionsStore()
      store.setAnswer('q1', 'Answer 1', 'text')
      store.setAnswer('q2', 'Answer 2', 'voice', 1.0)

      const answers = store.answersArray
      expect(answers).toHaveLength(2)
      expect(answers.map(a => a.question_id)).toEqual(['q1', 'q2'])
    })
  })

  describe('Evaluation Management', () => {
    it('should set evaluation for answer', () => {
      const store = useQuestionsStore()
      const evaluation: AnswerEvaluation = {
        question_id: 'q1',
        answer_text: 'Improved answer',
        quality_score: 8,
        quality_issues: [],
        quality_strengths: ['Specific', 'Quantifiable'],
        improvement_suggestions: [],
        is_acceptable: true,
        time_seconds: 2.0,
        model: 'gemini-2.0-flash'
      }

      store.setEvaluation('q1', evaluation)

      const result = store.getEvaluationById('q1')
      expect(result).toEqual(evaluation)
      expect(store.evaluatingQuestionId).toBeNull()
    })

    it('should initialize refinement data for unacceptable answer', () => {
      const store = useQuestionsStore()
      const evaluation: AnswerEvaluation = {
        question_id: 'q1',
        answer_text: 'Poor answer',
        quality_score: 4,
        quality_issues: ['Too vague'],
        quality_strengths: [],
        improvement_suggestions: ['Add specifics'],
        is_acceptable: false,
        time_seconds: 1.5,
        model: 'gemini-2.0-flash'
      }

      store.setEvaluation('q1', evaluation)

      // Refinement data is initialized but empty, so hasRefinementData returns false
      const refinement = store.getRefinementData('q1')
      expect(refinement).toHaveProperty('duration_detail')
      expect(refinement).toHaveProperty('specific_tools')
      expect(refinement).toHaveProperty('metrics')
      expect(refinement?.duration_detail).toBe('')

      // Will return true only after user fills in some data
      expect(store.hasRefinementData('q1')).toBe(false)
    })

    it('should not initialize refinement data for acceptable answer', () => {
      const store = useQuestionsStore()
      const evaluation: AnswerEvaluation = {
        question_id: 'q1',
        answer_text: 'Good answer',
        quality_score: 8,
        quality_issues: [],
        quality_strengths: ['Clear'],
        improvement_suggestions: [],
        is_acceptable: true,
        time_seconds: 2.0,
        model: 'gemini-2.0-flash'
      }

      store.setEvaluation('q1', evaluation)

      expect(store.hasRefinementData('q1')).toBe(false)
    })

    it('should start and clear evaluation', () => {
      const store = useQuestionsStore()

      store.startEvaluation('q1')
      expect(store.evaluatingQuestionId).toBe('q1')

      store.clearEvaluation()
      expect(store.evaluatingQuestionId).toBeNull()
    })
  })

  describe('Refinement Management', () => {
    it('should set refinement data', () => {
      const store = useQuestionsStore()
      const refinement = {
        duration_detail: '2 years',
        specific_tools: 'React, TypeScript',
        metrics: '40% performance increase'
      }

      store.setRefinementData('q1', refinement)

      expect(store.getRefinementData('q1')).toEqual(refinement)
      expect(store.hasRefinementData('q1')).toBe(true)
    })

    it('should update refinement field', () => {
      const store = useQuestionsStore()
      store.setRefinementData('q1', { field1: 'value1', field2: 'value2' })

      store.updateRefinementField('q1', 'field1', 'updated value')

      const refinement = store.getRefinementData('q1')
      expect(refinement?.field1).toBe('updated value')
      expect(refinement?.field2).toBe('value2')
    })

    it('should initialize refinement data if not exists', () => {
      const store = useQuestionsStore()

      store.updateRefinementField('q1', 'new_field', 'new value')

      const refinement = store.getRefinementData('q1')
      expect(refinement?.new_field).toBe('new value')
    })

    it('should increment refinement iteration', () => {
      const store = useQuestionsStore()

      expect(store.getRefinementIteration('q1')).toBe(0)

      store.incrementRefinementIteration('q1')
      expect(store.getRefinementIteration('q1')).toBe(1)

      store.incrementRefinementIteration('q1')
      expect(store.getRefinementIteration('q1')).toBe(2)
    })

    it('should accept answer and clear refinement state', () => {
      const store = useQuestionsStore()
      store.setRefinementData('q1', { test: 'data' })
      store.incrementRefinementIteration('q1')

      store.acceptAnswer('q1')

      expect(store.hasRefinementData('q1')).toBe(false)
      expect(store.getRefinementIteration('q1')).toBe(0)
    })

    it('should check if refinement data has content', () => {
      const store = useQuestionsStore()

      // Empty refinement
      store.setRefinementData('q1', { field1: '', field2: '  ' })
      expect(store.hasRefinementData('q1')).toBe(false)

      // Has content
      store.setRefinementData('q2', { field1: 'value', field2: '' })
      expect(store.hasRefinementData('q2')).toBe(true)
    })
  })

  describe('Active Tab Management', () => {
    it('should set active tab for question', () => {
      const store = useQuestionsStore()

      expect(store.getActiveTab('q1')).toBe('original')

      store.setActiveTab('q1', 'followup')
      expect(store.getActiveTab('q1')).toBe('followup')
    })

    it('should default to original tab', () => {
      const store = useQuestionsStore()
      expect(store.getActiveTab('nonexistent')).toBe('original')
    })
  })

  describe('Adaptive Flow Management', () => {
    it('should start adaptive flow', () => {
      const store = useQuestionsStore()

      expect(store.isInAdaptiveFlow('q1')).toBe(false)

      store.startAdaptiveFlow('q1', 'some')
      expect(store.isInAdaptiveFlow('q1')).toBe(true)
      expect(store.getAdaptiveExperienceLevel('q1')).toBe('some')
    })

    it('should complete adaptive flow', () => {
      const store = useQuestionsStore()
      store.startAdaptiveFlow('q1', 'none')

      store.completeAdaptiveFlow('q1')
      expect(store.isInAdaptiveFlow('q1')).toBe(false)
    })

    it('should handle different experience levels', () => {
      const store = useQuestionsStore()

      store.startAdaptiveFlow('q1', 'none')
      store.startAdaptiveFlow('q2', 'some')
      store.startAdaptiveFlow('q3', 'intermediate')

      expect(store.getAdaptiveExperienceLevel('q1')).toBe('none')
      expect(store.getAdaptiveExperienceLevel('q2')).toBe('some')
      expect(store.getAdaptiveExperienceLevel('q3')).toBe('intermediate')
    })
  })

  describe('Adaptive Modal Management', () => {
    it('should open adaptive modal with question', () => {
      const store = useQuestionsStore()
      const question: QuestionData = {
        id: 'q1',
        text: 'Test question',
        gap_info: {
          title: 'React',
          description: 'Missing React experience',
          category: 'hard_skill',
          impact: 'critical'
        },
        context: 'Test context',
        examples: [],
        follow_up_questions: [],
        expected_answer_length: 'medium',
        tips: []
      }

      store.openAdaptiveModal(question)

      expect(store.showAdaptiveModal).toBe(true)
      expect(store.currentAdaptiveQuestion).toEqual(question)
    })

    it('should close adaptive modal', () => {
      const store = useQuestionsStore()
      const question: QuestionData = {
        id: 'q1',
        text: 'Test',
        gap_info: { title: 'Test', description: 'Test', category: 'hard_skill', impact: 'critical' },
        context: 'Test',
        examples: [],
        follow_up_questions: [],
        expected_answer_length: 'short',
        tips: []
      }

      store.openAdaptiveModal(question)
      store.closeAdaptiveModal()

      expect(store.showAdaptiveModal).toBe(false)
      expect(store.currentAdaptiveQuestion).toBeNull()
    })
  })

  describe('Submission Management', () => {
    it('should set submitting state', () => {
      const store = useQuestionsStore()

      store.setSubmitting(true)
      expect(store.isSubmitting).toBe(true)

      store.setSubmitting(false)
      expect(store.isSubmitting).toBe(false)
    })

    it('should set answers result', () => {
      const store = useQuestionsStore()
      const mockCV: ParsedCV = {
        personal_info: {
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '555-0100',
          location: 'SF',
          job_title: 'Engineer',
          social_links: {}
        },
        work_experience: [],
        education: [],
        skills: [],
        projects: [],
        certifications: [],
        languages: [],
        professional_summary: 'Summary',
        total_years_experience: 5
      }

      const result: SubmitAnswersResult = {
        success: true,
        score_improvement: {
          before: 75,
          after: 82,
          absolute_change: 7,
          percentage_change: 9.3
        },
        category_improvements: [],
        uncovered_experiences: ['Led team of 5'],
        updated_cv: mockCV,
        time_seconds: 5.0,
        model: 'gemini-2.0-flash'
      }

      store.setAnswersResult(result)

      expect(store.answersResult).toEqual(result)
      expect(store.hasSubmitted).toBe(true)
      expect(store.isSubmitting).toBe(false)
    })
  })

  describe('Clear Operations', () => {
    it('should clear all answers', () => {
      const store = useQuestionsStore()

      // Set up some state
      store.setAnswer('q1', 'Answer', 'text')
      store.setEvaluation('q1', {
        question_id: 'q1',
        answer_text: 'Answer',
        quality_score: 8,
        quality_issues: [],
        quality_strengths: [],
        improvement_suggestions: [],
        is_acceptable: true,
        time_seconds: 1.0,
        model: 'gemini-2.0-flash'
      })
      store.setRefinementData('q1', { test: 'data' })
      store.setActiveTab('q1', 'followup')
      store.startAdaptiveFlow('q1', 'some')
      store.startEvaluation('q1')

      // Clear
      store.clearAnswers()

      // Verify everything is cleared
      expect(store.answers.size).toBe(0)
      expect(store.answerEvaluations.size).toBe(0)
      expect(store.refinementData.size).toBe(0)
      expect(store.activeQuestionTab.size).toBe(0)
      expect(store.refinementIterations.size).toBe(0)
      expect(store.activeAdaptiveFlows.size).toBe(0)
      expect(store.evaluatingQuestionId).toBeNull()
    })

    it('should reset entire store', () => {
      const store = useQuestionsStore()

      // Set up comprehensive state
      store.setAnswer('q1', 'Answer', 'text')
      store.setSubmitting(true)
      store.setAnswersResult({
        success: true,
        score_improvement: { before: 75, after: 82, absolute_change: 7, percentage_change: 9.3 },
        category_improvements: [],
        updated_cv: {} as ParsedCV,
        time_seconds: 1.0,
        model: 'gemini-2.0-flash'
      })
      store.openAdaptiveModal({
        id: 'q1',
        text: 'Test',
        gap_info: { title: 'Test', description: 'Test', category: 'hard_skill', impact: 'critical' },
        context: 'Test',
        examples: [],
        follow_up_questions: [],
        expected_answer_length: 'short',
        tips: []
      })

      // Reset
      store.resetStore()

      // Verify everything is reset
      expect(store.answers.size).toBe(0)
      expect(store.isSubmitting).toBe(false)
      expect(store.hasSubmitted).toBe(false)
      expect(store.answersResult).toBeNull()
      expect(store.showAdaptiveModal).toBe(false)
      expect(store.currentAdaptiveQuestion).toBeNull()
    })

    it('should clear specific question state', () => {
      const store = useQuestionsStore()

      // Set up state for multiple questions
      store.setAnswer('q1', 'Answer 1', 'text')
      store.setAnswer('q2', 'Answer 2', 'text')
      store.setEvaluation('q1', {
        question_id: 'q1',
        answer_text: 'Answer 1',
        quality_score: 8,
        quality_issues: [],
        quality_strengths: [],
        improvement_suggestions: [],
        is_acceptable: true,
        time_seconds: 1.0,
        model: 'gemini-2.0-flash'
      })
      store.startAdaptiveFlow('q1', 'some')
      store.startAdaptiveFlow('q2', 'none')

      // Clear only q1
      store.clearQuestionState('q1')

      // Verify q1 is cleared but q2 remains
      expect(store.isQuestionAnswered('q1')).toBe(false)
      expect(store.isQuestionAnswered('q2')).toBe(true)
      expect(store.isInAdaptiveFlow('q1')).toBe(false)
      expect(store.isInAdaptiveFlow('q2')).toBe(true)
      expect(store.getEvaluationById('q1')).toBeUndefined()
    })
  })

  describe('Complete Workflow Simulation', () => {
    it('should handle complete question answering workflow', () => {
      const store = useQuestionsStore()

      // Step 1: User provides initial answer
      store.setAnswer('q1', 'I built a chatbot', 'text')
      expect(store.isQuestionAnswered('q1')).toBe(true)

      // Step 2: Start evaluation
      store.startEvaluation('q1')
      expect(store.evaluatingQuestionId).toBe('q1')

      // Step 3: Receive evaluation - not acceptable
      const evaluation: AnswerEvaluation = {
        question_id: 'q1',
        answer_text: 'I built a chatbot',
        quality_score: 4,
        quality_issues: ['Too vague', 'No metrics'],
        quality_strengths: [],
        improvement_suggestions: ['Add specific details'],
        is_acceptable: false,
        time_seconds: 1.5,
        model: 'gemini-2.0-flash'
      }
      store.setEvaluation('q1', evaluation)

      expect(store.evaluatingQuestionId).toBeNull()
      expect(store.getRefinementIteration('q1')).toBe(0)

      // Step 4: User provides refinement data
      store.updateRefinementField('q1', 'duration_detail', '6 months')
      store.updateRefinementField('q1', 'metrics', 'Served 100 users')
      store.updateRefinementField('q1', 'specific_tools', 'Python, OpenAI API')

      // Step 5: Increment iteration
      store.incrementRefinementIteration('q1')
      expect(store.getRefinementIteration('q1')).toBe(1)

      // Step 6: Re-evaluate with better answer
      const betterEvaluation: AnswerEvaluation = {
        question_id: 'q1',
        answer_text: 'I built a chatbot using Python and OpenAI API that served 100 users over 6 months',
        quality_score: 8,
        quality_issues: [],
        quality_strengths: ['Specific', 'Quantified', 'Technical'],
        improvement_suggestions: [],
        is_acceptable: true,
        time_seconds: 1.8,
        model: 'gemini-2.0-flash'
      }
      store.setEvaluation('q1', betterEvaluation)

      // Step 7: Accept answer
      store.acceptAnswer('q1')
      expect(store.hasRefinementData('q1')).toBe(false)
      expect(store.getRefinementIteration('q1')).toBe(0)
      expect(store.getEvaluationById('q1')?.is_acceptable).toBe(true)
    })

    it('should handle adaptive workflow', () => {
      const store = useQuestionsStore()
      const question: QuestionData = {
        id: 'q1',
        text: 'Describe your React experience',
        gap_info: {
          title: 'React',
          description: 'Missing React experience',
          category: 'hard_skill',
          impact: 'critical'
        },
        context: 'This is required for the role',
        examples: [],
        follow_up_questions: [],
        expected_answer_length: 'medium',
        tips: []
      }

      // Step 1: Open adaptive modal
      store.openAdaptiveModal(question)
      expect(store.showAdaptiveModal).toBe(true)

      // Step 2: User selects "some" experience
      store.startAdaptiveFlow('q1', 'some')
      store.closeAdaptiveModal()

      // Step 3: User completes deep dive prompts
      store.setAnswer('q1', 'Generated comprehensive answer', 'text')

      // Step 4: Complete adaptive flow
      store.completeAdaptiveFlow('q1')
      expect(store.isInAdaptiveFlow('q1')).toBe(false)
    })
  })
})
