<template>
  <div class="category-line-graph">
    <div class="category-line-graph__label" :style="{ color: lineColor }">{{ label }}</div>
    <div class="category-line-graph__chart-container">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface CategoryScore {
  score: number
  weight: number
  status: string
}

interface Props {
  categoryScores: Record<string, CategoryScore>
  label: string
  overallScore: number
}

const props = defineProps<Props>()

// Extract category names and scores
const categories = computed(() => Object.keys(props.categoryScores))
const scores = computed(() => Object.values(props.categoryScores).map(c => c.score))

// Line color based on overall score
const lineColor = computed(() => {
  const score = props.overallScore
  if (score >= 70) return '#5bd692' // Green (--secondary-500)
  if (score >= 50) return '#f59e0b' // Yellow/Orange (--warning-500)
  return '#ef4444'                  // Red (--danger-500)
})

// Gradient color with transparency
const gradientColor = computed(() => {
  const score = props.overallScore
  if (score >= 70) return 'rgba(91, 214, 146, 0.2)' // Green with transparency
  if (score >= 50) return 'rgba(245, 158, 11, 0.2)' // Yellow with transparency
  return 'rgba(239, 68, 68, 0.2)'                   // Red with transparency
})

// Chart data configuration
const chartData = computed(() => ({
  labels: categories.value,
  datasets: [
    {
      data: scores.value,
      borderColor: lineColor.value,
      backgroundColor: gradientColor.value,
      borderWidth: 2.5,
      fill: true,
      tension: 0.4, // Smooth curves
      pointRadius: 0, // Hide dots
      pointHoverRadius: 0 // Hide dots on hover too
    }
  ]
}))

// Chart options configuration
const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2,
  plugins: {
    legend: {
      display: false // Hide legend
    },
    tooltip: {
      enabled: false // Disable tooltips for visual-only display
    }
  },
  scales: {
    x: {
      display: false // Hide x-axis
    },
    y: {
      display: true,
      min: 0,
      max: 100,
      ticks: {
        stepSize: 25,
        color: '#9ca3af', // Gray color
        font: {
          size: 10
        }
      },
      grid: {
        color: 'rgba(229, 231, 235, 0.5)', // Subtle gray grid lines
        lineWidth: 1
      },
      border: {
        display: false
      }
    }
  },
  interaction: {
    mode: undefined // Disable interactions
  }
}
</script>

<style lang="scss" scoped>
.category-line-graph {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.category-line-graph__label {
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.category-line-graph__chart-container {
  width: 100%;
  max-width: 200px;
  height: 120px;

  @media (max-width: 768px) {
    max-width: 150px;
    height: 100px;
  }
}
</style>
