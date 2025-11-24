<template>
  <div class="cover-letter-result">
    <div class="header">
      <h2 class="title">📧 Cover Letter Generated</h2>
      <p class="subtitle">Your personalized cover letter is ready</p>
      <div class="meta-info">
        <span class="word-count">{{ wordCount }} words</span>
        <span v-if="timeSeconds" class="time-badge">Generated in {{ timeSeconds }}s</span>
      </div>
    </div>

    <!-- Cover Letter Display -->
    <div class="cover-letter-container">
      <div class="cover-letter-paper">
        <div class="cover-letter-text" v-html="formattedCoverLetter"></div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="actions">
      <button class="action-button primary" @click="copyToClipboard">
        {{ copied ? '✓ Copied!' : '📋 Copy to Clipboard' }}
      </button>
      <button class="action-button secondary" @click="downloadAsText">
        📥 Download as .txt
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  coverLetter: string
  wordCount: number
  timeSeconds?: number
}

const props = defineProps<Props>()

const copied = ref(false)

// Format cover letter with HTML line breaks
const formattedCoverLetter = computed(() => {
  return props.coverLetter
    .split('\n\n')
    .map(paragraph => `<p>${paragraph.trim()}</p>`)
    .join('')
})

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.coverLetter)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
    alert('Failed to copy to clipboard')
  }
}

const downloadAsText = () => {
  const blob = new Blob([props.coverLetter], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'cover_letter.txt'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
</script>

<style scoped>
.cover-letter-result {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.125rem;
  color: #4a5568;
  margin-bottom: 1rem;
}

.meta-info {
  display: flex;
  justify-content: center;
  gap: 1rem;
  align-items: center;
}

.word-count {
  font-size: 0.875rem;
  color: #718096;
  font-weight: 500;
}

.time-badge {
  display: inline-block;
  background-color: #48bb78;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.cover-letter-container {
  background-color: #f7fafc;
  padding: 2rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
}

.cover-letter-paper {
  background-color: white;
  max-width: 750px;
  margin: 0 auto;
  padding: 3rem 2.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border-radius: 0.5rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  min-height: 500px;
}

.cover-letter-text {
  color: #2d3748;
  line-height: 1.8;
  font-size: 1rem;
  white-space: pre-wrap;
}

.cover-letter-text :deep(p) {
  margin-bottom: 1.25rem;
}

.cover-letter-text :deep(p:last-child) {
  margin-bottom: 0;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.action-button.primary {
  background-color: #3182ce;
  color: white;
}

.action-button.primary:hover {
  background-color: #2c5282;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.action-button.secondary {
  background-color: #48bb78;
  color: white;
}

.action-button.secondary:hover {
  background-color: #38a169;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.action-button:active {
  transform: translateY(0);
}
</style>
