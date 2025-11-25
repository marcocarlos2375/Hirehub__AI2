<template>
  <div>
    <div class="min-h-screen py-16 page-with-bg">
      <div class="container mx-auto px-4">
        <div class="card-container-shadow">
          <!-- Loading State -->
          <div v-if="isLoading" class="bg-white py-24 px-8 rounded-lg max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[400px]">
            <HbSpinner size="xl" />
            <p class="text-gray-600 mt-4 font-medium">Loading...</p>
          </div>

          <!-- Wizard Layout -->
          <div v-else class="layout bg-white rounded-lg max-w-7xl mx-auto">
            
       
            
            <!-- Sidebar -->
            <div class="sidebar bg-primary-900 text-white">
              <div class="p-6">
                <div class="flex items-center justify-between mb-6">
                  <h2 class="text-lg font-semibold">Job Match Analysis</h2>
                </div>

                <!-- Pipeline Steps Navigation -->
                <nav class="space-y-1 sidebar-nav-scrollable">
                  <button
                    v-for="(tool, index) in editorTools"
                    :key="tool.id"
                    @click="handleToolClick(tool.id)"
                    class="step-button w-full text-left"
                    :class="{
                      'step-button--active': activeStep === tool.id,
                      'step-button--disabled': isToolDisabled(tool.id)
                    }"
                    :disabled="isToolDisabled(tool.id)"
                  >
                    <div class="flex items-center gap-3 p-3 rounded-lg transition-all">
                      <div class="step-number">
                        {{ index + 1 }}
                      </div>
                      <div class="step-info">
                        <div class="step-title">{{ tool.title }}</div>
                        <div class="step-subtitle">{{ tool.subtitle }}</div>
                      </div>
                    </div>
                  </button>
                </nav>
              </div>
              
             
            </div>

            <!-- Main Content Area -->
            <div class="content">

              <!-- Job Parsing Step -->
              <div v-if="activeStep === 'job-parsing'" class="content-animated">
                <div class="content">
                  <h2 class="text-2xl font-semibold text-gray-900 mb-4">Job Parsing</h2>
                  <p class="text-gray-600 mb-6">Parse job description content will go here</p>
                </div>
              </div>
              
              <!-- AI Versions Modal -->
              <div v-if="showAIVersions" class="ai-modal-overlay" @click="showAIVersions = false">
                <div class="ai-modal" @click.stop>
                  <div class="ai-modal-header">
                    <h3 class="text-xl font-semibold text-gray-900">AI Generated Versions</h3>
                    <button @click="showAIVersions = false" class="close-btn">
                      <i class="ri-close-line"></i>
                    </button>
                  </div>

                  <div v-if="isGeneratingAI" class="ai-modal-loading">
                    <HbSpinner size="xl" />
                    <p class="mt-4 text-gray-600">Generating AI versions...</p>
                  </div>
                  
                  <div v-else class="ai-versions-grid">
                    <div v-for="version in aiGeneratedVersions" :key="version.id" 
                      @click="selectAIVersion(version)" class="ai-version-card">
                      <div class="ai-version-preview">
                        <img :src="version.preview" :alt="version.name" />
                      </div>
                      <div class="ai-version-info">
                        <h4 class="font-semibold text-gray-900">{{ version.name }}</h4>
                        <p class="text-sm text-gray-600">{{ version.description }}</p>
                      </div>
                      <HbButton variant="primary" size="sm" class="w-full mt-2">Select</HbButton>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Resume Parsing Step -->
              <div v-else-if="activeStep === 'cv-parsing'" class="content-animated">
                <div class="content">
                  <h2 class="text-2xl font-semibold text-gray-900 mb-4">Resume Parsing</h2>
                  <p class="text-gray-600 mb-6">Parse CV/Resume content will go here</p>
                </div>
              </div>

              <!-- Score Calculation Step -->
              <div v-else-if="activeStep === 'score-calc'" class="content-animated">
                <div class="content">
                  <h2 class="text-2xl font-semibold text-gray-900 mb-4">Score Calculation</h2>
                  <p class="text-gray-600 mb-6">Compatibility score content will go here</p>
                </div>
              </div>

              <!-- Smart Questions Step -->
              <div v-else-if="activeStep === 'smart-questions'" class="content-animated">
                <div class="content">
                  <h2 class="text-2xl font-semibold text-gray-900 mb-4">Smart Questions</h2>
                  <p class="text-gray-600 mb-6">Smart questions content will go here</p>
                </div>
              </div>

              <!-- Resume Rewrite Step -->
              <div v-else-if="activeStep === 'resume-rewrite'" class="content-animated">
                <div class="content">
                  <h2 class="text-2xl font-semibold text-gray-900 mb-4">Resume Rewrite</h2>
                  <p class="text-gray-600 mb-6">Optimized resume content will go here</p>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed } from 'vue'
import HbButton from '~/components/base/HbButton.vue'
import HbSpinner from '~/components/base/HbSpinner.vue'

interface EditorTool {
  id: string
  title: string
  subtitle: string
  icon: string
}

interface AIVersion {
  id: number
  name: string
  preview: string
  description: string
}

interface Guides {
  horizontal: number[]
  vertical: number[]
}


const isLoading = ref<boolean>(false)
const activeStep = ref<string>('job-parsing')

// Image State
const currentImage = ref<string | null>(null)
const uploadedImage = ref<string | null>(null)
const aiGeneratedVersions = ref<AIVersion[]>([])
const isGeneratingAI = ref<boolean>(false)
const showAIVersions = ref<boolean>(false)

// Tool Values
const zoomLevel = ref<number>(100)
const brightness = ref<number>(100)
const contrast = ref<number>(100)
const saturation = ref<number>(100)
const rotation = ref<number>(0)
const imageWidth = ref<number>(800)
const imageHeight = ref<number>(600)

// Guides and Rulers
const showRulers = ref<boolean>(true)
const showGuides = ref<boolean>(true)
const guides = ref<Guides>({
  horizontal: [],
  vertical: []
})

const editorTools = computed<EditorTool[]>(() => [
  { id: 'job-parsing', title: 'Job Parsing', subtitle: 'Parse job description', icon: 'ri-briefcase-line' },
  { id: 'cv-parsing', title: 'Resume Parsing', subtitle: 'Parse CV/Resume', icon: 'ri-file-user-line' },
  { id: 'score-calc', title: 'Score Calculation', subtitle: 'Calculate compatibility', icon: 'ri-pie-chart-line' },
  { id: 'smart-questions', title: 'Smart Questions', subtitle: 'Answer questions', icon: 'ri-question-answer-line' },
  { id: 'resume-rewrite', title: 'Resume Rewrite', subtitle: 'Generate optimized resume', icon: 'ri-file-edit-line' }
])

// Step completion tracking
const completedSteps = ref<Set<string>>(new Set())

// Check if a step should be disabled (sequential flow)
const isToolDisabled = (stepId: string): boolean => {
  // Job parsing is always enabled (first step)
  if (stepId === 'job-parsing') return false

  // For other steps, check if previous step is completed
  const stepOrder = ['job-parsing', 'cv-parsing', 'score-calc', 'smart-questions', 'resume-rewrite']
  const currentIndex = stepOrder.indexOf(stepId)

  if (currentIndex === -1 || currentIndex === 0) return true

  // Check if previous step is completed
  const previousStep = stepOrder[currentIndex - 1]
  return previousStep ? !completedSteps.value.has(previousStep) : true
}

// Handle step clicks with validation
const handleToolClick = (stepId: string): void => {
  if (isToolDisabled(stepId)) {
    // Show a notification or do nothing
    console.log('Please complete previous steps first')
    return
  }
  activeStep.value = stepId
}

// Mark a step as completed
const markStepCompleted = (stepId: string): void => {
  completedSteps.value.add(stepId)
}

const openFileUpload = (): void => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = (e) => handleFileUpload(e as Event)
  input.click()
}

const handleFileUpload = async (event: Event): Promise<void> => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const result = e.target?.result as string
    uploadedImage.value = result
    currentImage.value = result

    // Unlock all tools by generating AI versions
    generateAIVersions()
  }
  reader.readAsDataURL(file)
}

const generateAIVersions = async (): Promise<void> => {
  isGeneratingAI.value = true
  showAIVersions.value = true

  // Simulate AI generation (replace with actual API call)
  setTimeout(() => {
    aiGeneratedVersions.value = [
      { id: 1, name: 'Professional', preview: uploadedImage.value!, description: 'Enhanced lighting & colors' },
      { id: 2, name: 'Portrait Mode', preview: uploadedImage.value!, description: 'Background blur effect' },
      { id: 3, name: 'Studio Quality', preview: uploadedImage.value!, description: 'Professional retouching' }
    ]
    isGeneratingAI.value = false
  }, 2000)
}

const selectAIVersion = (version: AIVersion): void => {
  currentImage.value = version.preview
  showAIVersions.value = false
  activeStep.value = 'cv-parsing'
}

const resetAdjustments = (): void => {
  brightness.value = 100
  contrast.value = 100
  saturation.value = 100
}

const rotateImage = (degrees: number): void => {
  rotation.value = (rotation.value + degrees) % 360
}

const flipImage = (direction: string): void => {
  // Implement flip logic
  console.log(`Flipping ${direction}`)
}

const toggleRulers = (): void => {
  showRulers.value = !showRulers.value
}

const toggleGuides = (): void => {
  showGuides.value = !showGuides.value
}

const addGuide = (type: string, position: number): void => {
  if (type === 'horizontal') {
    guides.value.horizontal.push(position)
  } else {
    guides.value.vertical.push(position)
  }
}

const saveImage = (): void => {
  console.log('Saving image...')
  // Implement save logic
}

const exportImage = (): void => {
  console.log('Exporting image...')
  // Implement export logic
}

const cancelAction = (): void => {
  // Reset to initial state or go back
  if (confirm('Are you sure you want to cancel? All unsaved changes will be lost.')) {
    currentImage.value = null
    uploadedImage.value = null
    activeStep.value = 'job-parsing'
    completedSteps.value.clear()
    resetAdjustments()
  }
}

const openParameters = (): void => {
  console.log('Opening parameters...')
  // Open parameters/settings modal
}

const openHelp = (): void => {
  console.log('Opening help...')
  // Open help documentation or modal
}
</script>

<style scoped lang="scss">
.page-with-bg {
  position: relative;
  background-size: cover;
  background-position: center top;
  background-repeat: no-repeat;
  background-attachment: fixed;
  
  > * {
    position: relative;
    z-index: 1;
  }
}

/* Editor Layout */
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  height: 85vh;
  overflow: hidden;
  border-radius: 0.5rem;
}

/* Simple Navigation Bar */
.nav-bar {
  height: 25px;
  display: flex;
  align-items: center;
  gap: 0;
  background: #f9fafb;
}

.nav-link {
  height: 100%;
  padding: 0 1rem;
  background: transparent;
  border: none;
  font-size: 0.75rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  

  
  &:hover:not(:disabled) {
    background: #e5e7eb;
    color: #111827;
  }
  
  &--disabled {
    opacity: 0.4;
    cursor: not-allowed;
    
    &:hover {
      background: transparent;
      color: #374151;
    }
  }
  
  &:disabled {
    pointer-events: none;
  }
}

.sidebar {
  position: sticky;
  top: 0;
  height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-top-left-radius: 0.5rem;
  border-bottom-left-radius: 0.5rem;
}

.sidebar-nav-scrollable {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none;
  
  &::-webkit-scrollbar {
    display: none;
  }
}

.content {
  height: 85vh;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-top-right-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
}

.content-animated {
  flex: 1;
  overflow-y: auto;
}

.content {
  padding: 2rem;
}

.footer {
  display: flex;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  background-color: white;
}

/* Sidebar Steps */
.step-button {
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  background: transparent;
  border-radius: 0.5rem;
  position: relative;

  &:hover:not(:disabled) {
    background-color: rgba(255, 255, 255, 0.05);
  }

  &--active {
    background-color: rgba(255, 255, 255, 0.1);
  }

  &--disabled {
    opacity: 0.4;
    cursor: not-allowed;

    .step-number {
      background-color: rgba(255, 255, 255, 0.05);
    }

    .step-title,
    .step-subtitle {
      color: rgba(255, 255, 255, 0.5);
    }
  }

  &:disabled {
    pointer-events: none;
  }
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 600;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  flex-shrink: 0;

  .step-button--active & {
    background-color: var(--primary-500);
  }
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-subtitle {
  font-size: 0.75rem;
  opacity: 0.7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 0.5rem;
}

.sidebar-action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 0.375rem;
  color: white;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.15);
  }
  
  &--primary {
    background: var(--primary-500);
    
    &:hover {
      background: var(--primary-600);
    }
  }
}

/* Import Cards */
.import-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  border: 2px dashed #d1d5db;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  
  i {
    font-size: 3rem;
    color: var(--primary-500);
    margin-bottom: 1rem;
  }
  
  h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.5rem;
  }
  
  p {
    font-size: 0.875rem;
    color: #6b7280;
  }
  
  &:hover {
    border-color: var(--primary-500);
    background: var(--primary-50);
    transform: translateY(-2px);
  }
}

/* Canvas Workspace */
.canvas-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  position: relative;
}

.canvas-workspace {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.with-rulers {
    padding: 20px 0 0 20px;
  }
}

.canvas-area {
  position: relative;
  max-width: 90%;
  max-height: 90%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.canvas-image {
  max-width: 100%;
  max-height: 100%;
  display: block;
  transition: transform 0.3s ease, filter 0.3s ease;
}

/* Rulers */
.ruler {
  position: absolute;
  background: #e5e7eb;
  z-index: 10;
  
  &.ruler-horizontal {
    top: 0;
    left: 20px;
    right: 0;
    height: 20px;
    background: repeating-linear-gradient(
      to right,
      #d1d5db 0px,
      #d1d5db 1px,
      transparent 1px,
      transparent 10px
    );
  }
  
  &.ruler-vertical {
    left: 0;
    top: 20px;
    bottom: 0;
    width: 20px;
    background: repeating-linear-gradient(
      to bottom,
      #d1d5db 0px,
      #d1d5db 1px,
      transparent 1px,
      transparent 10px
    );
  }
}

/* Guides */
.guide {
  position: absolute;
  background: #3b82f6;
  opacity: 0.5;
  z-index: 20;
  
  &.guide-horizontal {
    left: 0;
    right: 0;
    height: 1px;
  }
  
  &.guide-vertical {
    top: 0;
    bottom: 0;
    width: 1px;
  }
}

/* AI Modal */
.ai-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

.ai-modal {
  background: white;
  border-radius: 1rem;
  max-width: 900px;
  width: 90%;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.ai-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f3f4f6;
    color: #111827;
  }
}

.ai-modal-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.ai-versions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  padding: 1.5rem;
  overflow-y: auto;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.ai-version-card {
  cursor: pointer;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1rem;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--primary-500);
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }
}

.ai-version-preview {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 1rem;
  background: #f3f4f6;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.ai-version-info {
  margin-bottom: 0.75rem;
  
  h4 {
    font-size: 1rem;
    margin-bottom: 0.25rem;
  }
  
  p {
    font-size: 0.875rem;
  }
}

/* Tool Panels */
.tool-panel {
  max-width: 500px;
}

.control-group {
  label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.5rem;
  }
}

.slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e5e7eb;
  outline: none;
  
  &::-webkit-slider-thumb {
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--primary-500);
    cursor: pointer;
  }
}

.dimension-input {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  
  &:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
  }
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  
  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
}

.color-picker {
  width: 100%;
  height: 50px;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
}

/* Preset Buttons */
.zoom-presets,
.size-presets,
.aspect-ratio-grid,
.rotate-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.75rem;
}

.preset-btn,
.aspect-btn,
.control-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f9fafb;
    border-color: var(--primary-500);
  }
}

.control-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  i {
    font-size: 1.125rem;
  }
}

/* Filters Grid */
.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
}

.filter-card {
  cursor: pointer;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 0.75rem;
  background: white;
  transition: all 0.2s ease;
  
  span {
    display: block;
    text-align: center;
    font-size: 0.75rem;
    color: #374151;
    margin-top: 0.5rem;
  }
  
  &:hover {
    border-color: var(--primary-500);
    transform: translateY(-2px);
  }
}

.filter-preview {
  width: 100%;
  aspect-ratio: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0.375rem;
  
  &.filter-bw {
    background: linear-gradient(135deg, #333 0%, #999 100%);
  }
  
  &.filter-sepia {
    background: linear-gradient(135deg, #b8860b 0%, #cd853f 100%);
  }
  
  &.filter-vintage {
    background: linear-gradient(135deg, #8b4513 0%, #daa520 100%);
  }
}

/* Enhance Options */
.enhance-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  width: 100%;
  
  i {
    font-size: 2rem;
    color: var(--primary-500);
  }
  
  h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.25rem;
  }
  
  p {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0;
  }
  
  &:hover {
    border-color: var(--primary-500);
    background: var(--primary-50);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Mobile Header */
.mobile-steps-header {
  display: none;
}

/* Mobile Responsive */
@media (max-width: 640px) {
  .page-with-bg {
    padding: 0;
    min-height: 100vh;
  }

  .mobile-steps-header {
    display: block;
    background: var(--primary-700);
    border-radius: 0;
  }

  .mobile-steps-title {
    padding: 1rem 1rem 0;
    
    h2 {
      margin: 0;
    }
  }

  .mobile-steps-scroll {
    overflow-x: auto;
    scrollbar-width: none;
    
    &::-webkit-scrollbar {
      display: none;
    }
  }

  .mobile-steps-container {
    display: flex;
    gap: 0.5rem;
    padding: 1rem;
  }

  .mobile-step-item {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.375rem;
    padding: 0.5rem 0.75rem;
    background: rgba(255, 255, 255, 0.15);
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 80px;
    
    &--active {
      background: white;
      
      .mobile-step-icon {
        background: var(--primary-700);
        color: white;
      }
      
      .mobile-step-label {
        color: var(--primary-700);
        font-weight: 600;
      }
    }
    
    &--completed {
      .mobile-step-icon {
        background: #32BEA6;
        color: white;
      }
    }
  }

  .mobile-step-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
    background: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.9);
  }

  .mobile-step-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.9);
    white-space: nowrap;
    text-align: center;
  }

  .wizard-sidebar {
    display: none !important;
  }

  .wizard-layout {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 100vh;
    border-radius: 0;
  }

  .wizard-content {
    height: auto;
    border-radius: 0;
  }

  .wizard-step-content {
    padding: 1rem;
  }

  .wizard-step-footer {
    padding: 1rem;
    gap: 0.5rem;
    
    :deep(button) {
      flex: 1;
    }
  }
}
</style>
