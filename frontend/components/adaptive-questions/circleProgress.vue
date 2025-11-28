<template>
  <div class="circle-progress-container">
    <div class="circle-progress" :style="{ width: containerSize, height: containerSize }">
      <div
        v-for="(segment, index) in totalSegments"
        :key="index"
        class="segment"
        :class="{ active: index < activeSegments }"
        :style="getSegmentStyle(index)"
      />
      <div class="center-content">
        <div class="center-label" :style="{ fontSize: labelFontSize }">{{ label }}</div>
        <div class="center-value" :style="{ color: currentColor, fontSize: valueFontSize }">
          {{ score }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CircleProgress',
  props: {
    score: {
      type: Number,
      required: true,
      validator: (value) => value >= 0 && value <= 10
    },
    label: {
      type: String,
      default: 'Score'
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['xs', 'sm', 'md', 'lg'].includes(value)
    }
  },
  data() {
    return {
      totalSegments: 24
    }
  },
  computed: {
    sizeConfig() {
      const configs = {
        xs: { container: 120, radius: 50, segment: { width: 4, height: 12 }, fontSize: 28, labelSize: 10 },
        sm: { container: 160, radius: 65, segment: { width: 5, height: 16 }, fontSize: 36, labelSize: 12 },
        md: { container: 200, radius: 80, segment: { width: 6, height: 20 }, fontSize: 48, labelSize: 14 },
        lg: { container: 260, radius: 105, segment: { width: 8, height: 26 }, fontSize: 64, labelSize: 16 }
      }
      return configs[this.size]
    },
    radius() {
      return this.sizeConfig.radius
    },
    containerSize() {
      return `${this.sizeConfig.container}px`
    },
    segmentWidth() {
      return `${this.sizeConfig.segment.width}px`
    },
    segmentHeight() {
      return `${this.sizeConfig.segment.height}px`
    },
    segmentRadius() {
      return `${this.sizeConfig.segment.width / 2}px`
    },
    valueFontSize() {
      return `${this.sizeConfig.fontSize}px`
    },
    labelFontSize() {
      return `${this.sizeConfig.labelSize}px`
    },
    activeSegments() {
      return Math.round(this.totalSegments * (this.score / 10))
    },
    currentColor() {
      if (this.score < 5) return '#ef4444' // red-500
      if (this.score < 7) return '#f59e0b' // amber-500
      return '#10b981' // success-500 (green-500)
    }
  },
  methods: {
    getSegmentStyle(index) {
      const angle = (index * 360 / this.totalSegments) - 90
      const radian = (angle * Math.PI) / 180
      const x = Math.cos(radian) * this.radius
      const y = Math.sin(radian) * this.radius

      const isActive = index < this.activeSegments
      const activeColor = this.currentColor
      const inactiveColor = this.getInactiveColor()

      return {
        transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px)) rotate(${angle + 90}deg)`,
        backgroundColor: isActive ? activeColor : inactiveColor,
        width: this.segmentWidth,
        height: this.segmentHeight,
        borderRadius: this.segmentRadius
      }
    },
    getInactiveColor() {
      if (this.score < 5) return '#fecaca' // red-200
      if (this.score < 7) return '#fde68a' // amber-200
      return '#a7f3d0' // green-200
    }
  }
}
</script>

<style scoped>
.circle-progress-container {
  display: inline-block;
}

.circle-progress {
  position: relative;
}

.segment {
  position: absolute;
  left: 50%;
  top: 50%;
  transform-origin: center center;
  transition: background-color 0.3s ease;
}

.center-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.center-label {
  color: #888;
  margin-bottom: 4px;
}

.center-value {
  font-weight: 300;
  transition: color 0.3s ease;
}
</style>
