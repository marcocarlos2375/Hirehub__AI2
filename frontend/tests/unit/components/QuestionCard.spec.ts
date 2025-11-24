import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import QuestionCard from '~/components/adaptive-questions/QuestionCard.vue'
import type { QuestionItem } from '~/composables/analysis/useAnalysisState'

describe('QuestionCard Component', () => {
  const createMockQuestion = (overrides?: Partial<QuestionItem>): QuestionItem => ({
    id: 'q1',
    number: 1,
    title: 'Backend Development Experience',
    priority: 'HIGH',
    impact: 'Missing skills: Python, FastAPI',
    question_text: 'Can you describe your experience with Python backend development?',
    context_why: 'The role requires strong Python and FastAPI knowledge',
    examples: [
      'Describe API endpoints you built',
      'Explain database integration you implemented'
    ],
    ...overrides
  })

  it('should render question details correctly', () => {
    const question = createMockQuestion()
    const wrapper = mount(QuestionCard, {
      props: { question }
    })

    expect(wrapper.text()).toContain('Q1')
    expect(wrapper.text()).toContain('Backend Development Experience')
    expect(wrapper.text()).toContain('HIGH')
    expect(wrapper.text()).toContain('Missing skills: Python, FastAPI')
    expect(wrapper.text()).toContain('Can you describe your experience with Python backend development?')
    expect(wrapper.text()).toContain('Why we\'re asking:')
    expect(wrapper.text()).toContain('The role requires strong Python and FastAPI knowledge')
  })

  it('should apply correct priority color classes', () => {
    const testCases = [
      { priority: 'CRITICAL' as const, expectedClass: 'bg-red-100 text-red-800' },
      { priority: 'HIGH' as const, expectedClass: 'bg-orange-100 text-orange-800' },
      { priority: 'MEDIUM' as const, expectedClass: 'bg-yellow-100 text-yellow-800' }
    ]

    for (const { priority, expectedClass } of testCases) {
      const question = createMockQuestion({ priority })
      const wrapper = mount(QuestionCard, {
        props: { question }
      })

      const priorityBadge = wrapper.find('.px-2\\.5')
      expect(priorityBadge.classes()).toContain(expectedClass.split(' ')[0])
    }
  })

  it('should toggle examples visibility when clicked', async () => {
    const question = createMockQuestion()
    const wrapper = mount(QuestionCard, {
      props: { question }
    })

    // Examples should be hidden initially
    expect(wrapper.text()).not.toContain('Describe API endpoints you built')
    expect(wrapper.text()).toContain('Show examples')

    // Click to show examples
    const toggleButton = wrapper.find('button')
    await toggleButton.trigger('click')

    // Examples should now be visible
    expect(wrapper.text()).toContain('Hide examples')
    expect(wrapper.text()).toContain('Describe API endpoints you built')
    expect(wrapper.text()).toContain('Explain database integration you implemented')

    // Click again to hide
    await toggleButton.trigger('click')
    expect(wrapper.text()).not.toContain('Describe API endpoints you built')
    expect(wrapper.text()).toContain('Show examples')
  })

  it('should emit need-help event when zero experience button clicked', async () => {
    const question = createMockQuestion()
    const wrapper = mount(QuestionCard, {
      props: { question }
    })

    // First, show examples to reveal the button
    const toggleButton = wrapper.find('button')
    await toggleButton.trigger('click')

    // Find and click the "zero experience" button
    const needHelpButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('I have zero experience')
    )
    expect(needHelpButton).toBeDefined()

    await needHelpButton!.trigger('click')

    // Check event was emitted
    expect(wrapper.emitted('need-help')).toBeTruthy()
    expect(wrapper.emitted('need-help')?.length).toBe(1)
  })

  it('should not render examples section if no examples provided', () => {
    const question = createMockQuestion({ examples: [] })
    const wrapper = mount(QuestionCard, {
      props: { question }
    })

    expect(wrapper.text()).not.toContain('Show examples')
    expect(wrapper.findAll('button').length).toBe(0)
  })

  it('should render slot content', () => {
    const question = createMockQuestion()
    const wrapper = mount(QuestionCard, {
      props: { question },
      slots: {
        default: '<div class="test-slot">Slot content here</div>'
      }
    })

    expect(wrapper.html()).toContain('test-slot')
    expect(wrapper.text()).toContain('Slot content here')
  })

  it('should handle questions without examples gracefully', () => {
    const question = createMockQuestion({ examples: undefined as any })
    const wrapper = mount(QuestionCard, {
      props: { question }
    })

    // Should still render the main content
    expect(wrapper.text()).toContain('Backend Development Experience')
    expect(wrapper.text()).not.toContain('Show examples')
  })
})
