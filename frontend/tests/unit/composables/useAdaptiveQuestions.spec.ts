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
  })
})
