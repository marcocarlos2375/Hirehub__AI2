<template>
  <fieldset
    :id="id"
    class="hb-fieldset"
    :class="[
      { 'focused': focused },
      { 'not-empty': modelValue },
      { 'fieldset-error': error },
      `size-${size}`,
      `appearance-${appearance}`
    ]"
  >
    <label
      v-if="label"
      :for="id"
    >
      {{ label }}<span v-if="required">*</span>
    </label>

    <div class="input-wrapper">
      <HbInput
        :id="`${id}-input`"
        :modelValue="formattedDate"
        :placeholder="placeholder"
        :disabled="disabled"
        size="sm"
        :appearance="appearance"
        readonly
        @click="togglePicker"
        @focus="togglePicker"
      >
        
      </HbInput>

      <!-- Date picker popup -->
      <div v-if="showPicker" class="date-picker-popup">
        <!-- Year navigation -->
        <div class="year-navigation">
          <button class="nav-button" @click="prevYear" :disabled="currentViewYear <= props.minYear">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          <div class="current-year">{{ currentViewYear }}</div>
          <button class="nav-button" @click="nextYear" :disabled="currentViewYear >= props.maxYear">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>
        
        <!-- Month Grid -->
        <div class="month-grid">
          <button 
            v-for="(month, index) in shortMonths" 
            :key="index"
            class="month-button"
            :class="{ 'selected': isSelectedMonth(index + 1) }"
            @click="selectAndApplyMonth(index + 1)"
          >
            {{ month }}
          </button>
        </div>
        
        <!-- Current Job Toggle for End Date -->
        <div v-if="isEndDate" class="current-job-option">
          <HbToggle
            :modelValue="currentValue"
            label="Currently work here"
            @update:modelValue="handleCurrentToggle"
          />
        </div>
      </div>
      

      <!-- Error and Helper Text -->
      <div v-if="error && typeof error === 'string'" class="error-msg">
        {{ error }}
      </div>
      
      <legend v-if="helperText">
        {{ helperText }}
      </legend>
    </div>
  </fieldset>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import HbToggle from './HbToggle.vue'
import HbInput from './HbInput.vue'

interface DateValue {
  month: number | string
  year: number | string
}

interface Props {
  modelValue?: string
  id?: string
  label?: string
  size?: 'sm' | 'md' | 'lg'
  appearance?: 'dark' | 'gray' | 'light' | 'white'
  required?: boolean
  disabled?: boolean
  error?: string | boolean
  helperText?: string
  minYear?: number
  maxYear?: number
  placeholder?: string
  isEndDate?: boolean
  currentValue?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
  (e: 'focus'): void
  (e: 'update:current', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  id: () => `date-${Math.random().toString(36).substr(2, 9)}`,
  label: '',
  size: 'sm',
  appearance: 'white',
  required: false,
  disabled: false,
  error: '',
  helperText: '',
  minYear: 1950,
  maxYear: () => new Date().getFullYear() + 5,
  placeholder: '',
  isEndDate: false,
  currentValue: false
})

const emit = defineEmits<Emits>()

// State
const focused = ref<boolean>(false)
const showPicker = ref<boolean>(false)
const date = ref<DateValue>({
  month: '',
  year: ''
})

// Current view year (for the picker)
const currentViewYear = ref<number>(new Date().getFullYear())

// Month names
const months: string[] = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'
]

// Short month names for the grid
const shortMonths: string[] = [
  'Jan', 'Feb', 'Mar', 'Apr',
  'May', 'Jun', 'Jul', 'Aug',
  'Sep', 'Oct', 'Nov', 'Dec'
]

// Formatted date for display
const formattedDate = computed<string>(() => {
  // If it's an end date and current job is checked, show "Present"
  if (props.isEndDate && props.currentValue) {
    return 'Present'
  }

  // Otherwise show the normal date format if available
  if (!date.value.month || !date.value.year) return ''

  const monthName = months[Number(date.value.month) - 1]
  return `${monthName} ${date.value.year}`
})

// Toggle date picker
function togglePicker(): void {
  if (props.disabled) return

  showPicker.value = !showPicker.value

  if (showPicker.value) {
    // Set current view year
    if (date.value.year) {
      currentViewYear.value = Number(date.value.year)
    } else {
      currentViewYear.value = new Date().getFullYear()
    }

    // Add click outside listener
    document.addEventListener('click', handleClickOutside)
  }

  focused.value = showPicker.value
}

// Close picker
function closePicker(): void {
  showPicker.value = false
  focused.value = false
  document.removeEventListener('click', handleClickOutside)
}

// Handle year navigation
function prevYear(): void {
  if (currentViewYear.value > props.minYear) {
    currentViewYear.value--
  }
}

function nextYear(): void {
  if (currentViewYear.value < props.maxYear) {
    currentViewYear.value++
  }
}

// Select month and immediately apply it
function selectAndApplyMonth(month: number): void {
  date.value.month = month
  date.value.year = currentViewYear.value
  updateModelValue()
  closePicker()
}

// Check if a month is selected
function isSelectedMonth(month: number): boolean {
  return date.value.month === month && Number(date.value.year) === currentViewYear.value
}

// Handle click outside
function handleClickOutside(event: MouseEvent): void {
  const fieldset = document.getElementById(props.id)
  if (!fieldset) return

  const pickerElement = fieldset.querySelector('.date-picker-popup')
  const displayElement = fieldset.querySelector('.date-display')
  const target = event.target as HTMLElement

  if (pickerElement && !pickerElement.contains(target) &&
      displayElement && !displayElement.contains(target)) {
    closePicker()
  }
}

// Update the modelValue when month or year changes
function updateModelValue(): void {
  if (date.value.month && date.value.year) {
    // Format: YYYY-MM (e.g., "2023-05")
    const monthStr = date.value.month.toString().padStart(2, '0')
    emit('update:modelValue', `${date.value.year}-${monthStr}`)
  } else {
    emit('update:modelValue', '')
  }
}

// Parse the modelValue to set month and year
function parseModelValue(): void {
  if (props.modelValue) {
    try {
      // Expected format: YYYY-MM (e.g., "2023-05")
      const [year, month] = props.modelValue.split('-')
      date.value.year = parseInt(year, 10)
      date.value.month = parseInt(month, 10)
    } catch (e) {
      console.error('Invalid date format in modelValue', e)
    }
  }
}

// Handle current job toggle change
function handleCurrentToggle(newValue: boolean): void {
  // Store the previous date values before updating current status
  const previousDate = {
    month: date.value.month,
    year: date.value.year
  }

  emit('update:current', newValue)

  // We keep the date value but display "Present" in the UI when toggle is on
  // No need to restore dates as we're not clearing them anymore
}

// Clean up event listeners
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside as EventListener)
})

// Initialize component
onMounted(() => {
  parseModelValue()
})

// Watch for external modelValue changes
watch(() => props.modelValue, parseModelValue)
</script>

<style lang="scss" scoped>
.hb-fieldset {
  position: relative;
  .input-wrapper {
    position: relative;
  }
  
  /* Using HbInput component instead of custom date display */
  :deep(.hb-fieldset) {
    margin-bottom: 0;
  }
  
  :deep(input) {
    cursor: pointer;
  }
  
  /* Date picker popup */
  
  .date-picker-popup {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    width: 100%;
    background-color: white;
    
    border-radius: var(--radius-md);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 100;
    padding: var(--spacing-3);
    
    /* Year navigation */
    .year-navigation {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: var(--spacing-3);
      
      .current-year {
        font-weight: var(--font-medium);
        font-size: var(--text-base);
      }
      
      .nav-button {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: none;
        background: none;
        cursor: pointer;
        color: var(--gray-600);
        transition: all 0.2s ease;
        
        &:hover {
          background: var(--primary-500);
          color: white;
        }
        
        svg {
          width: 16px;
          height: 16px;
        }
      }
    }
    
    /* Month grid */
    .month-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: var(--spacing-2);
      margin-bottom: var(--spacing-3);
      font-family: var(--font-heading);

      
      .month-button {
        padding: var(--spacing-1) var(--spacing-2);
        border-radius: var(--radius-full);
        border: none;
        background: none;
        font-size: var(--text-xs);
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:hover {
          background-color: var(--gray-100);
        }
        
        &.selected {
          background: var(--primary-500);
          color: white;
          font-weight: var(--font-medium);
        }
      }
    }
    
    /* Current job option */
    .current-job-option {
      margin-top: var(--spacing-3);
      padding-top: var(--spacing-3);
      display: flex;
      justify-content: center;
      
      :deep(.hb-toggle) {
        margin-bottom: 0;
      }
    }
  }

  /* Size variants handled by HbInput component */

  /* Appearance variants handled by HbInput component */

  label {
    display: flex;
    align-items: center;
    font-weight: var(--font-medium);
    font-size: var(--text-xs);
    padding-bottom: var(--spacing-2);
    color: var(--gray-500);
    
    span {
      color: var(--error-500);
      margin-left: 2px;
    }
  }

  legend {
    font-size: var(--text-xs);
    color: var(--gray-500);
    margin-top: var(--spacing-1);
  }

  .error-msg {
    color: var(--error-500);
    font-size: var(--text-xs);
    margin-top: var(--spacing-1);
  }
  
  /* Error and focus states handled by HbInput component */
}
</style>
