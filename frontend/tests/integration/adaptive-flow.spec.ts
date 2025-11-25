/**
 * Adaptive Question Flow Integration Tests
 *
 * Tests the complete end-to-end adaptive question workflow including:
 * - Store state management (useQuestionsStore)
 * - API interactions (useAdaptiveQuestions)
 * - Deep dive path (for experienced users)
 * - Learning resources path (for willing to learn users)
 * - Quality evaluation and refinement cycles
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useQuestionsStore } from '~/stores/questions/useQuestionsStore'
import { useAdaptiveQuestions } from '~/composables/adaptive-questions/useAdaptiveQuestions'
import type { QuestionData } from '~/types/api-responses'

describe('Adaptive Question Flow Integration', () => {
  beforeEach(() => {
    // Create fresh Pinia instance for each test
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Deep Dive Path (Experienced User)', () => {
    it('should complete full deep dive workflow: start → prompts → generate → evaluate → accept', async () => {
      const store = useQuestionsStore()
      const { startAdaptiveQuestion, submitStructuredInputs, evaluateAnswer } = useAdaptiveQuestions()

      const question: QuestionData = {
        id: 'q1',
        text: 'Describe your experience with microservices architecture',
        gap_info: {
          title: 'Microservices Architecture',
          description: 'Missing microservices experience',
          category: 'hard_skill',
          impact: 'critical'
        },
        context: 'Job requires extensive microservices experience',
        examples: ['Designed service mesh', 'Implemented API gateway'],
        follow_up_questions: [],
        expected_answer_length: 'long',
        tips: ['Be specific about technologies']
      }

      // Step 1: Open adaptive modal
      store.openAdaptiveModal(question)
      expect(store.showAdaptiveModal).toBe(true)
      expect(store.currentAdaptiveQuestion).toEqual(question)

      // Step 2: User selects "Yes, I have some experience" → Start deep dive
      const startResponse = {
        question_id: 'q1',
        current_step: 'deep_dive_prompts',
        deep_dive_prompts: [
          {
            id: 'context',
            type: 'text',
            question: 'What was the business context?',
            required: true
          },
          {
            id: 'scale',
            type: 'number',
            question: 'How many microservices did you manage?',
            required: true
          },
          {
            id: 'technologies',
            type: 'multiselect',
            question: 'Which technologies did you use?',
            options: ['Docker', 'Kubernetes', 'Service Mesh', 'API Gateway'],
            required: true
          }
        ]
      }

      vi.mocked($fetch).mockResolvedValueOnce(startResponse)

      await startAdaptiveQuestion(
        'q1',
        question.text,
        question,
        question.gap_info,
        'user_123',
        {}, // parsedCV
        {}, // parsedJD
        'some', // experience level
        'english'
      )

      store.startAdaptiveFlow('q1', 'some')
      store.closeAdaptiveModal()

      expect(store.isInAdaptiveFlow('q1')).toBe(true)
      expect(store.getAdaptiveExperienceLevel('q1')).toBe('some')

      // Step 3: User fills deep dive prompts
      const structuredData = {
        context: 'E-commerce platform serving 1M daily users',
        scale: 15,
        technologies: ['Docker', 'Kubernetes', 'Service Mesh'],
        duration: '2 years',
        team_size: 8
      }

      const generateResponse = {
        question_id: 'q1',
        generated_answer: 'I designed and implemented a microservices architecture for an e-commerce platform serving 1M daily users. Managed 15 microservices using Docker and Kubernetes with a service mesh for inter-service communication. Led a team of 8 engineers over 2 years to migrate from monolithic architecture.',
        quality_score: 8,
        current_step: 'quality_evaluation',
        iteration: 0
      }

      vi.mocked($fetch).mockResolvedValueOnce(generateResponse)

      const generated = await submitStructuredInputs('q1', structuredData)

      // Store the generated answer
      store.setAnswer('q1', generated.generated_answer, 'text')

      expect(generated.generated_answer).toContain('microservices')
      expect(generated.generated_answer).toContain('1M daily users')
      expect(generated.generated_answer).toContain('15 microservices')

      // Step 4: Evaluate quality
      const evaluationResponse = {
        success: true,
        question_id: 'q1',
        answer_text: generated.generated_answer,
        quality_score: 8,
        quality_issues: [],
        quality_strengths: [
          'Specific scale metrics',
          'Clear technology stack',
          'Quantified team size and duration'
        ],
        improvement_suggestions: [],
        is_acceptable: true,
        time_seconds: 1.8,
        model: 'gemini-2.0-flash'
      }

      vi.mocked($fetch).mockResolvedValueOnce(evaluationResponse)

      store.startEvaluation('q1')
      const evaluation = await evaluateAnswer(
        'q1',
        question.text,
        generated.generated_answer,
        { title: question.gap_info.title, description: question.gap_info.description }
      )

      store.setEvaluation('q1', evaluation)

      expect(store.evaluatingQuestionId).toBeNull()
      expect(evaluation.is_acceptable).toBe(true)
      expect(evaluation.quality_score).toBeGreaterThanOrEqual(7)

      // Step 5: Accept answer and complete flow
      store.acceptAnswer('q1')
      store.completeAdaptiveFlow('q1')

      expect(store.isInAdaptiveFlow('q1')).toBe(false)
      expect(store.isQuestionAnswered('q1')).toBe(true)
      expect(store.getEvaluationById('q1')?.is_acceptable).toBe(true)
    })

    it('should handle refinement cycle in deep dive path', async () => {
      const store = useQuestionsStore()
      const { submitStructuredInputs, evaluateAnswer, refineAnswer } = useAdaptiveQuestions()

      const questionId = 'q2'
      const questionText = 'Describe your React experience'

      // Step 1: Generate initial answer with low quality
      const generateResponse = {
        question_id: questionId,
        generated_answer: 'I used React for some projects',
        quality_score: 4,
        current_step: 'quality_evaluation',
        iteration: 0
      }

      vi.mocked($fetch).mockResolvedValueOnce(generateResponse)

      const generated = await submitStructuredInputs(questionId, {
        experience: 'some',
        projects: 'a few'
      })

      store.setAnswer(questionId, generated.generated_answer, 'text')

      // Step 2: Evaluation finds it unacceptable
      const poorEvaluation = {
        success: true,
        question_id: questionId,
        answer_text: generated.generated_answer,
        quality_score: 4,
        quality_issues: ['Too vague', 'No metrics'],
        quality_strengths: [],
        improvement_suggestions: ['Add specific projects', 'Include metrics'],
        is_acceptable: false,
        time_seconds: 1.2,
        model: 'gemini-2.0-flash'
      }

      vi.mocked($fetch).mockResolvedValueOnce(poorEvaluation)

      const evaluation = await evaluateAnswer(
        questionId,
        questionText,
        generated.generated_answer,
        { title: 'React', description: 'Missing React experience' }
      )

      store.setEvaluation(questionId, evaluation)

      expect(evaluation.is_acceptable).toBe(false)
      expect(store.getRefinementData(questionId)).toBeDefined()

      // Step 3: User provides refinement data
      store.updateRefinementField(questionId, 'specific_projects', 'E-commerce dashboard, Admin panel')
      store.updateRefinementField(questionId, 'metrics', '40% performance improvement')
      store.updateRefinementField(questionId, 'duration', '3 years')

      store.incrementRefinementIteration(questionId)

      // Step 4: Refine answer
      const refinedResponse = {
        question_id: questionId,
        refined_answer: 'I have 3 years of React experience building production applications including an e-commerce dashboard and admin panel. Achieved 40% performance improvement through code splitting and lazy loading.',
        quality_score: 8,
        quality_issues: [],
        is_acceptable: true,
        current_step: 'final_answer',
        iteration: 1
      }

      vi.mocked($fetch).mockResolvedValueOnce(refinedResponse)

      const refined = await refineAnswer(
        questionId,
        questionText,
        { id: questionId, text: questionText },
        { title: 'React', description: 'Missing React experience' },
        evaluation.answer_text,
        evaluation.quality_issues,
        {
          specific_projects: 'E-commerce dashboard, Admin panel',
          metrics: '40% performance improvement',
          duration: '3 years'
        }
      )

      // Update store with refined answer
      store.setAnswer(questionId, refined.refined_answer, 'text')

      expect(refined.quality_score).toBeGreaterThan(evaluation.quality_score)
      expect(refined.is_acceptable).toBe(true)
      expect(store.getRefinementIteration(questionId)).toBe(1)

      // Accept the refined answer
      store.acceptAnswer(questionId)
      expect(store.hasRefinementData(questionId)).toBe(false)
    })
  })

  describe('Learning Resources Path (Willing to Learn)', () => {
    it('should complete learning resources workflow: start → search → display → save plan', async () => {
      const store = useQuestionsStore()
      const { startAdaptiveQuestion, getLearningResources, saveLearningPlan } = useAdaptiveQuestions()

      const question: QuestionData = {
        id: 'q3',
        text: 'Describe your experience with GraphQL',
        gap_info: {
          title: 'GraphQL',
          description: 'No GraphQL experience',
          category: 'hard_skill',
          impact: 'important'
        },
        context: 'Job requires GraphQL knowledge',
        examples: [],
        follow_up_questions: [],
        expected_answer_length: 'medium',
        tips: []
      }

      // Step 1: User selects "Willing to Learn"
      store.openAdaptiveModal(question)

      const startResponse = {
        question_id: 'q3',
        current_step: 'learning_resources',
        learning_resources: []
      }

      vi.mocked($fetch).mockResolvedValueOnce(startResponse)

      await startAdaptiveQuestion(
        'q3',
        question.text,
        question,
        question.gap_info,
        'user_123',
        {},
        {},
        'willing_to_learn',
        'english'
      )

      store.startAdaptiveFlow('q3', 'willing_to_learn')
      store.closeAdaptiveModal()

      // Step 2: Get learning resources
      const resourcesResponse = {
        resources: [
          {
            id: 'res_1',
            title: 'GraphQL Fundamentals Course',
            url: 'https://example.com/graphql-course',
            type: 'tutorial',
            duration_days: 7,
            cost: 'free',
            level: 'beginner',
            provider: 'FreeCodeCamp'
          },
          {
            id: 'res_2',
            title: 'Building GraphQL APIs',
            url: 'https://example.com/graphql-api',
            type: 'tutorial',
            duration_days: 5,
            cost: 'free',
            level: 'intermediate',
            provider: 'YouTube'
          },
          {
            id: 'res_3',
            title: 'GraphQL Best Practices',
            url: 'https://example.com/graphql-best',
            type: 'article',
            duration_days: 1,
            cost: 'free',
            level: 'intermediate',
            provider: 'Medium'
          }
        ],
        learning_path: {
          timeline: [
            { week: 1, resources: ['res_1'], milestone: 'Learn GraphQL basics' },
            { week: 2, resources: ['res_2'], milestone: 'Build first API' },
            { week: 3, resources: ['res_3'], milestone: 'Study best practices' }
          ],
          total_days: 13,
          estimated_completion: '2024-02-15',
          resources_in_path: 3
        },
        total_resources: 3,
        total_duration_days: 13,
        estimated_completion: '2024-02-15'
      }

      vi.mocked($fetch).mockResolvedValueOnce(resourcesResponse)

      const resources = await getLearningResources(
        question.gap_info,
        'beginner',
        14,
        'free',
        5
      )

      expect(resources.resources).toHaveLength(3)
      expect(resources.total_duration_days).toBe(13)
      expect(resources.learning_path.timeline).toHaveLength(3)

      // Step 3: User saves learning plan
      const saveResponse = {
        plan_id: 'plan_graphql_123',
        success: true
      }

      vi.mocked($fetch).mockResolvedValueOnce(saveResponse)

      const saved = await saveLearningPlan(
        'user_123',
        question.gap_info,
        ['res_1', 'res_2', 'res_3'],
        'Focus on practical examples'
      )

      expect(saved.success).toBe(true)
      expect(saved.plan_id).toBeTruthy()

      // Complete the adaptive flow
      store.completeAdaptiveFlow('q3')
      expect(store.isInAdaptiveFlow('q3')).toBe(false)
    })
  })

  describe('Multiple Questions Workflow', () => {
    it('should handle multiple questions with different paths simultaneously', async () => {
      const store = useQuestionsStore()
      const { submitStructuredInputs, getLearningResources } = useAdaptiveQuestions()

      // Question 1: Deep dive (experienced)
      store.startAdaptiveFlow('q1', 'some')

      vi.mocked($fetch).mockResolvedValueOnce({
        question_id: 'q1',
        generated_answer: 'Detailed answer for Q1',
        quality_score: 8
      })

      await submitStructuredInputs('q1', { experience: 'detailed' })
      store.setAnswer('q1', 'Detailed answer for Q1', 'text')

      // Question 2: Learning path (willing to learn)
      store.startAdaptiveFlow('q2', 'willing_to_learn')

      vi.mocked($fetch).mockResolvedValueOnce({
        resources: [{ id: 'res_1', title: 'Tutorial', url: 'url', type: 'tutorial', duration_days: 5, cost: 'free', level: 'beginner' }],
        learning_path: { timeline: [], total_days: 5, estimated_completion: '', resources_in_path: 1 },
        total_resources: 1,
        total_duration_days: 5,
        estimated_completion: ''
      })

      await getLearningResources({ title: 'Python', description: 'Need Python' })

      // Question 3: No experience (skipped)
      // User clicks "No experience" button - just marks as skipped

      // Verify store state
      expect(store.isInAdaptiveFlow('q1')).toBe(true)
      expect(store.isInAdaptiveFlow('q2')).toBe(true)
      expect(store.getAdaptiveExperienceLevel('q1')).toBe('some')
      expect(store.getAdaptiveExperienceLevel('q2')).toBe('willing_to_learn')
      expect(store.isQuestionAnswered('q1')).toBe(true)
      expect(store.isQuestionAnswered('q2')).toBe(false) // Learning doesn't create answer

      // Complete workflows
      store.completeAdaptiveFlow('q1')
      store.completeAdaptiveFlow('q2')

      expect(store.isInAdaptiveFlow('q1')).toBe(false)
      expect(store.isInAdaptiveFlow('q2')).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully and maintain store state', async () => {
      const store = useQuestionsStore()
      const { startAdaptiveQuestion } = useAdaptiveQuestions()

      const question: QuestionData = {
        id: 'q_error',
        text: 'Test question',
        gap_info: { title: 'Test', description: 'Test', category: 'hard_skill', impact: 'critical' },
        context: 'Test',
        examples: [],
        follow_up_questions: [],
        expected_answer_length: 'short',
        tips: []
      }

      store.openAdaptiveModal(question)

      // API call fails
      vi.mocked($fetch).mockRejectedValueOnce(new Error('API Error'))

      await expect(
        startAdaptiveQuestion(
          'q_error',
          question.text,
          question,
          question.gap_info,
          'user_123',
          {},
          {},
          'some'
        )
      ).rejects.toThrow('API Error')

      // Store state should remain consistent
      expect(store.showAdaptiveModal).toBe(true) // Still open for retry
      expect(store.currentAdaptiveQuestion).toEqual(question)
    })

    it('should allow retry after error', async () => {
      const store = useQuestionsStore()
      const { submitStructuredInputs } = useAdaptiveQuestions()

      store.startAdaptiveFlow('q_retry', 'some')

      // First attempt fails
      vi.mocked($fetch).mockRejectedValueOnce(new Error('Network error'))

      await expect(
        submitStructuredInputs('q_retry', { data: 'test' })
      ).rejects.toThrow('Network error')

      // Retry succeeds
      vi.mocked($fetch).mockResolvedValueOnce({
        question_id: 'q_retry',
        generated_answer: 'Success on retry',
        quality_score: 7
      })

      const result = await submitStructuredInputs('q_retry', { data: 'test' })

      expect(result.generated_answer).toBe('Success on retry')
    })
  })

  describe('Store State Cleanup', () => {
    it('should properly clean up state after completing workflow', async () => {
      const store = useQuestionsStore()

      // Set up complete workflow state
      const question: QuestionData = {
        id: 'q_cleanup',
        text: 'Test',
        gap_info: { title: 'Test', description: 'Test', category: 'hard_skill', impact: 'critical' },
        context: 'Test',
        examples: [],
        follow_up_questions: [],
        expected_answer_length: 'short',
        tips: []
      }

      store.openAdaptiveModal(question)
      store.startAdaptiveFlow('q_cleanup', 'some')
      store.setAnswer('q_cleanup', 'Test answer', 'text')
      store.setEvaluation('q_cleanup', {
        question_id: 'q_cleanup',
        answer_text: 'Test answer',
        quality_score: 8,
        quality_issues: [],
        quality_strengths: [],
        improvement_suggestions: [],
        is_acceptable: true,
        time_seconds: 1.0,
        model: 'gemini-2.0-flash'
      })

      // Complete workflow
      store.completeAdaptiveFlow('q_cleanup')
      store.closeAdaptiveModal()

      // Verify state
      expect(store.isInAdaptiveFlow('q_cleanup')).toBe(false)
      expect(store.showAdaptiveModal).toBe(false)
      expect(store.currentAdaptiveQuestion).toBeNull()
      expect(store.isQuestionAnswered('q_cleanup')).toBe(true) // Answer persists
      expect(store.getEvaluationById('q_cleanup')).toBeDefined() // Evaluation persists
    })

    it('should allow starting new workflow after cleanup', async () => {
      const store = useQuestionsStore()

      // First workflow
      store.startAdaptiveFlow('q1', 'some')
      store.setAnswer('q1', 'Answer 1', 'text')
      store.completeAdaptiveFlow('q1')

      // Second workflow
      store.startAdaptiveFlow('q2', 'willing_to_learn')
      store.completeAdaptiveFlow('q2')

      // Both should be independent
      expect(store.isInAdaptiveFlow('q1')).toBe(false)
      expect(store.isInAdaptiveFlow('q2')).toBe(false)
      expect(store.isQuestionAnswered('q1')).toBe(true)
      expect(store.isQuestionAnswered('q2')).toBe(false)
    })
  })
})
