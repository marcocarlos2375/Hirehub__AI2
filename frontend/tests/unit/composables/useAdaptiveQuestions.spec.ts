import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useAdaptiveQuestions } from '~/composables/adaptive-questions/useAdaptiveQuestions'

describe('useAdaptiveQuestions Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('evaluateAnswer', () => {
    it('should call API with correct parameters', async () => {
      const mockResponse = {
        success: true,
        question_id: 'test_q1',
        answer_text: 'I built a chatbot',
        quality_score: 4,
        quality_issues: ['Too vague', 'No metrics'],
        quality_strengths: [],
        improvement_suggestions: ['Add specific metrics', 'Add technical details'],
        is_acceptable: false,
        time_seconds: 1.5,
        model: 'gemini-2.0-flash-exp'
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { evaluateAnswer } = useAdaptiveQuestions()

      const result = await evaluateAnswer(
        'test_q1',
        'Describe your chatbot project',
        'I built a chatbot',
        { title: 'AI/Chatbot', description: 'Missing chatbot experience' },
        'english'
      )

      expect($fetch).toHaveBeenCalledWith('/api/evaluate-answer', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          question_id: 'test_q1',
          question_text: 'Describe your chatbot project',
          answer_text: 'I built a chatbot',
          gap_info: {
            title: 'AI/Chatbot',
            description: 'Missing chatbot experience'
          },
          language: 'english'
        }
      })

      expect(result).toEqual(mockResponse)
      expect(result.quality_score).toBe(4)
      expect(result.is_acceptable).toBe(false)
    })

    it('should handle API errors gracefully', async () => {
      vi.mocked($fetch).mockRejectedValueOnce(new Error('Network error'))

      const { evaluateAnswer } = useAdaptiveQuestions()

      await expect(
        evaluateAnswer(
          'test_q1',
          'Test question',
          'Test answer',
          { title: 'Test', description: 'Test gap' }
        )
      ).rejects.toThrow('Network error')
    })
  })

  describe('refineAnswer', () => {
    it('should call API with all required context fields', async () => {
      const mockResponse = {
        question_id: 'test_q1',
        refined_answer: 'I built a chatbot that served 50 users with 87% satisfaction rate...',
        quality_score: 8,
        current_step: 'quality_evaluation',
        iteration: 1
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { refineAnswer } = useAdaptiveQuestions()

      const result = await refineAnswer(
        'test_q1',
        'Describe your chatbot project',
        { id: 'test_q1', question_text: 'Describe your chatbot project', title: 'AI/Chatbot' },
        { title: 'AI/Chatbot', description: 'Missing chatbot experience' },
        'I built a chatbot',
        ['Too vague', 'No metrics'],
        {
          'Metrics': 'Served 50 users, 87% satisfaction',
          'Technical': 'Python, OpenAI API, Flask'
        }
      )

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/refine-answer', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          question_id: 'test_q1',
          question_text: 'Describe your chatbot project',
          question_data: expect.objectContaining({
            id: 'test_q1',
            question_text: 'Describe your chatbot project'
          }),
          gap_info: {
            title: 'AI/Chatbot',
            description: 'Missing chatbot experience'
          },
          generated_answer: 'I built a chatbot',
          quality_issues: ['Too vague', 'No metrics'],
          additional_data: {
            'Metrics': 'Served 50 users, 87% satisfaction',
            'Technical': 'Python, OpenAI API, Flask'
          }
        }
      })

      expect(result.quality_score).toBe(8)
      expect(result.refined_answer).toContain('50 users')
      expect(result.refined_answer).toContain('87%')
    })

    it('should throw error when API fails', async () => {
      vi.mocked($fetch).mockRejectedValueOnce(new Error('Refinement failed'))

      const { refineAnswer } = useAdaptiveQuestions()

      await expect(
        refineAnswer(
          'test_q1',
          'Test question',
          {},
          { title: 'Test', description: 'Test' },
          'Test answer',
          [],
          {}
        )
      ).rejects.toThrow('Refinement failed')
    })
  })

  describe('startAdaptiveQuestion', () => {
    it('should call start API with correct parameters', async () => {
      const mockResponse = {
        question_id: 'test_q1',
        current_step: 'deep_dive_prompts',
        deep_dive_prompts: [
          {
            id: 'prompt_1',
            type: 'text',
            question: 'What was the context?',
            required: true
          }
        ]
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { startAdaptiveQuestion } = useAdaptiveQuestions()

      const result = await startAdaptiveQuestion(
        'test_q1',
        'Test question',
        { id: 'test_q1' },
        { title: 'Test', description: 'Test gap' },
        'user_123',
        {},
        {},
        'yes',
        'english'
      )

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/start', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: expect.objectContaining({
          question_id: 'test_q1',
          experience_check_response: 'yes'
        })
      })

      expect(result.current_step).toBe('deep_dive_prompts')
    })

    it('should handle "willing_to_learn" experience level', async () => {
      const mockResponse = {
        question_id: 'test_q1',
        current_step: 'learning_resources',
        learning_resources: []
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { startAdaptiveQuestion } = useAdaptiveQuestions()

      await startAdaptiveQuestion(
        'test_q1',
        'Test question',
        { id: 'test_q1' },
        { title: 'Test', description: 'Test gap' },
        'user_123',
        {},
        {},
        'willing_to_learn'
      )

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/start', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: expect.objectContaining({
          experience_check_response: 'willing_to_learn'
        })
      })
    })

    it('should throw error when API fails', async () => {
      vi.mocked($fetch).mockRejectedValueOnce(new Error('Start workflow failed'))

      const { startAdaptiveQuestion } = useAdaptiveQuestions()

      await expect(
        startAdaptiveQuestion(
          'test_q1',
          'Test question',
          { id: 'test_q1' },
          { title: 'Test', description: 'Test gap' },
          'user_123',
          {},
          {},
          'yes'
        )
      ).rejects.toThrow('Start workflow failed')
    })
  })

  describe('submitStructuredInputs', () => {
    it('should submit structured data with correct format', async () => {
      const mockResponse = {
        question_id: 'test_q1',
        generated_answer: 'Comprehensive answer based on structured inputs...',
        quality_score: 8,
        current_step: 'quality_evaluation'
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { submitStructuredInputs } = useAdaptiveQuestions()

      const structuredData = {
        context: 'Led team of 5 engineers',
        duration: '2 years',
        technologies: ['React', 'Node.js'],
        impact: 'Increased performance by 40%',
        team_size: 5
      }

      const result = await submitStructuredInputs('test_q1', structuredData)

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/submit-inputs', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          question_id: 'test_q1',
          structured_data: structuredData
        }
      })

      expect(result.generated_answer).toBeTruthy()
      expect(result.quality_score).toBe(8)
    })

    it('should handle boolean and array values', async () => {
      const mockResponse = {
        question_id: 'test_q1',
        generated_answer: 'Answer',
        quality_score: 7,
        current_step: 'quality_evaluation'
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { submitStructuredInputs } = useAdaptiveQuestions()

      const structuredData = {
        hasExperience: true,
        technologies: ['Python', 'TensorFlow'],
        years: 3
      }

      await submitStructuredInputs('test_q1', structuredData)

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/submit-inputs', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          question_id: 'test_q1',
          structured_data: {
            hasExperience: true,
            technologies: ['Python', 'TensorFlow'],
            years: 3
          }
        }
      })
    })

    it('should throw error on API failure', async () => {
      vi.mocked($fetch).mockRejectedValueOnce(new Error('Submission failed'))

      const { submitStructuredInputs } = useAdaptiveQuestions()

      await expect(
        submitStructuredInputs('test_q1', { test: 'data' })
      ).rejects.toThrow('Submission failed')
    })
  })

  describe('getLearningResources', () => {
    it('should fetch learning resources with default parameters', async () => {
      const mockResponse = {
        resources: [
          {
            id: 'res_1',
            title: 'React Tutorial',
            url: 'https://example.com/react',
            type: 'tutorial',
            duration_days: 5,
            cost: 'free',
            level: 'intermediate'
          }
        ],
        learning_path: {
          timeline: [],
          total_days: 5,
          estimated_completion: '2024-01-15',
          resources_in_path: 1
        },
        total_resources: 1,
        total_duration_days: 5,
        estimated_completion: '2024-01-15'
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { getLearningResources } = useAdaptiveQuestions()

      const gap = { title: 'React', description: 'Missing React experience' }
      const result = await getLearningResources(gap)

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/get-learning-resources', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          gap,
          user_level: 'intermediate',
          max_days: 10,
          cost_preference: 'any',
          limit: 5
        }
      })

      expect(result.resources).toHaveLength(1)
      expect(result.total_duration_days).toBe(5)
    })

    it('should accept custom parameters', async () => {
      const mockResponse = {
        resources: [],
        learning_path: { timeline: [], total_days: 0, estimated_completion: '', resources_in_path: 0 },
        total_resources: 0,
        total_duration_days: 0,
        estimated_completion: ''
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { getLearningResources } = useAdaptiveQuestions()

      const gap = { title: 'Python', description: 'Need Python skills' }
      await getLearningResources(gap, 'beginner', 7, 'free', 10)

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/get-learning-resources', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          gap,
          user_level: 'beginner',
          max_days: 7,
          cost_preference: 'free',
          limit: 10
        }
      })
    })

    it('should handle API errors', async () => {
      vi.mocked($fetch).mockRejectedValueOnce(new Error('Search failed'))

      const { getLearningResources } = useAdaptiveQuestions()

      await expect(
        getLearningResources({ title: 'Test', description: 'Test gap' })
      ).rejects.toThrow('Search failed')
    })
  })

  describe('saveLearningPlan', () => {
    it('should save learning plan with correct data', async () => {
      const mockResponse = {
        plan_id: 'plan_123',
        success: true
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { saveLearningPlan } = useAdaptiveQuestions()

      const gap = { title: 'React', description: 'Missing React experience' }
      const resourceIds = ['res_1', 'res_2', 'res_3']
      const notes = 'Focus on hooks and state management'

      const result = await saveLearningPlan('user_123', gap, resourceIds, notes)

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/save-learning-plan', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          user_id: 'user_123',
          gap,
          resource_ids: resourceIds,
          notes
        }
      })

      expect(result.success).toBe(true)
      expect(result.plan_id).toBe('plan_123')
    })

    it('should save plan without notes', async () => {
      const mockResponse = {
        plan_id: 'plan_456',
        success: true
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { saveLearningPlan } = useAdaptiveQuestions()

      const gap = { title: 'Python', description: 'Need Python skills' }
      await saveLearningPlan('user_123', gap, ['res_1'])

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/save-learning-plan', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          user_id: 'user_123',
          gap,
          resource_ids: ['res_1'],
          notes: undefined
        }
      })
    })

    it('should handle save failures', async () => {
      vi.mocked($fetch).mockRejectedValueOnce(new Error('Save failed'))

      const { saveLearningPlan } = useAdaptiveQuestions()

      await expect(
        saveLearningPlan('user_123', { title: 'Test', description: 'Test' }, ['res_1'])
      ).rejects.toThrow('Save failed')
    })
  })

  describe('getLearningPlans', () => {
    it('should fetch all learning plans for user', async () => {
      const mockResponse = {
        plans: [
          {
            plan_id: 'plan_1',
            user_id: 'user_123',
            gap: { title: 'React', description: 'Missing React' },
            resource_ids: ['res_1', 'res_2'],
            status: 'in_progress',
            created_at: '2024-01-01',
            notes: 'Test notes'
          }
        ],
        total: 1
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { getLearningPlans } = useAdaptiveQuestions()

      const result = await getLearningPlans('user_123')

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/get-learning-plans', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          user_id: 'user_123',
          status: undefined
        }
      })

      expect(result.plans).toHaveLength(1)
      expect(result.total).toBe(1)
    })

    it('should filter plans by status', async () => {
      const mockResponse = {
        plans: [
          {
            plan_id: 'plan_1',
            user_id: 'user_123',
            gap: { title: 'React', description: 'Missing React' },
            resource_ids: ['res_1'],
            status: 'completed',
            created_at: '2024-01-01',
            notes: null
          }
        ],
        total: 1
      }

      vi.mocked($fetch).mockResolvedValueOnce(mockResponse)

      const { getLearningPlans } = useAdaptiveQuestions()

      await getLearningPlans('user_123', 'completed')

      expect($fetch).toHaveBeenCalledWith('/api/adaptive-questions/get-learning-plans', {
        method: 'POST',
        baseURL: 'http://localhost:8001',
        body: {
          user_id: 'user_123',
          status: 'completed'
        }
      })
    })

    it('should handle fetch errors', async () => {
      vi.mocked($fetch).mockRejectedValueOnce(new Error('Fetch failed'))

      const { getLearningPlans } = useAdaptiveQuestions()

      await expect(
        getLearningPlans('user_123')
      ).rejects.toThrow('Fetch failed')
    })
  })
})
