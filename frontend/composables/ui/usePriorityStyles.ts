/**
 * Shared composable for priority and quality score styling
 *
 * Provides consistent styling across answer evaluation components:
 * - QuestionCard.vue
 * - AnswerQualityDisplay.vue
 * - QuestionsResult.vue
 * - RefinementSuggestionCard.vue
 */

export type BadgeVariant = 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light'

export const usePriorityStyles = () => {
  /**
   * Maps priority string to HbBadge variant
   * Ensures consistency across all components
   */
  const priorityBadgeVariant = (priority: string): BadgeVariant => {
    const p = priority.toUpperCase()
    switch (p) {
      case 'CRITICAL':
        return 'danger'
      case 'HIGH':
      case 'IMPORTANT':
        return 'warning'
      case 'MEDIUM':
        return 'info'
      case 'LOW':
      case 'NICE-TO-HAVE':
      default:
        return 'light'
    }
  }

  /**
   * Returns Tailwind border class for priority level
   */
  const priorityBorderClass = (priority: string): string => {
    const p = priority.toUpperCase()
    switch (p) {
      case 'CRITICAL':
        return 'border-red-300'
      case 'HIGH':
      case 'IMPORTANT':
        return 'border-orange-300'
      case 'MEDIUM':
        return 'border-yellow-300'
      case 'LOW':
      case 'NICE-TO-HAVE':
      default:
        return 'border-gray-300'
    }
  }

  /**
   * Returns Tailwind background class for priority level
   */
  const priorityBackgroundClass = (priority: string): string => {
    const p = priority.toUpperCase()
    switch (p) {
      case 'CRITICAL':
        return 'bg-red-50'
      case 'HIGH':
      case 'IMPORTANT':
        return 'bg-orange-50'
      case 'MEDIUM':
        return 'bg-yellow-50'
      case 'LOW':
      case 'NICE-TO-HAVE':
      default:
        return 'bg-gray-50'
    }
  }

  /**
   * Returns quality score styling classes
   * Replaces gradient backgrounds with flat colors
   */
  const qualityScoreClasses = (score: number) => {
    if (score >= 9) {
      return {
        container: 'bg-green-50 border-green-200',
        text: 'text-green-700',
        circle: 'bg-green-100 border-4 border-green-600'
      }
    }
    if (score >= 7) {
      return {
        container: 'bg-blue-50 border-blue-200',
        text: 'text-blue-700',
        circle: 'bg-blue-100 border-4 border-blue-600'
      }
    }
    if (score >= 5) {
      return {
        container: 'bg-amber-50 border-amber-200',
        text: 'text-amber-700',
        circle: 'bg-amber-100 border-4 border-amber-600'
      }
    }
    return {
      container: 'bg-red-50 border-red-200',
      text: 'text-red-700',
      circle: 'bg-red-100 border-4 border-red-600'
    }
  }

  return {
    priorityBadgeVariant,
    priorityBorderClass,
    priorityBackgroundClass,
    qualityScoreClasses
  }
}
