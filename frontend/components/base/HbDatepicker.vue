<template>
  <div 
    class="hb-fieldset hb-datepicker"
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
      <input
        :id="id"
        ref="datepicker"
        :value="displayValue"
        readonly
        :name="id"
        :required="required"
        :disabled="disabled"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        @focus="onFocus"
        @click="showCalendar = true"
      >
      
      <div
        class="calendar-icon trailing-icon"
        @click="showCalendar = true"
      >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect
              x="3"
              y="4"
              width="18"
              height="18"
              rx="2"
              ry="2"
            />
            <line
              x1="16"
              y1="2"
              x2="16"
              y2="6"
            />
            <line
              x1="8"
              y1="2"
              x2="8"
              y2="6"
            />
            <line
              x1="3"
              y1="10"
              x2="21"
              y2="10"
            />
          </svg>
      </div>
      
      <Teleport to="body">
        <div
          v-if="showCalendar"
          class="calendar-dropdown"
          :style="dropdownStyle"
        >
          <ClientOnly>
            <DatePicker
              v-model="selectedDate"
              :min-date="minDate"
              :max-date="maxDate"
              mode="date"
              :popover="false"
              :is-expanded="true"
              @update:model-value="selectDate"
            />
          </ClientOnly>
          <div class="calendar-actions">
            <HbButton
              variant="outline"
              size="sm"
              type="button"
              @click="clearDate"
            >
              Clear
            </HbButton>
            <HbButton
              variant="primary"
              size="sm"
              type="button"
              @click="showCalendar = false"
            >
              Done
            </HbButton>
          </div>
        </div>
      </Teleport>
    </div>

    <legend v-if="helperText">
      {{ helperText }}
    </legend>

    <div
      v-if="error"
      class="error-msg"
    >
      {{ error }}
    </div>
  </div>
</template>
  
<script setup lang="ts">
// @ts-strict
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch, Teleport } from 'vue'
import CalendarIcon from 'vue-material-design-icons/Calendar.vue'
import HbButton from './HbButton.vue'
import { DatePicker } from 'v-calendar'

interface DropdownStyle {
  position?: 'absolute' | 'fixed' | 'relative' | 'static' | 'sticky'
  left?: string
  top?: string
  bottom?: string
  width?: string
  zIndex?: number
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
  placeholder?: string
  autocomplete?: string
  minAge?: number
  maxAge?: number
  mindate?: string | Date | null
  maxdate?: string | Date | null
  format?: 'DD.MM.YYYY' | 'YYYY-MM-DD' | 'MM/DD/YYYY'
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
  (e: 'focus'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  id: () => `datepicker-${Math.random().toString(36).substr(2, 9)}`,
  label: '',
  size: 'md',
  appearance: 'white',
  required: false,
  disabled: false,
  error: '',
  helperText: '',
  placeholder: 'DD.MM.YYYY',
  autocomplete: 'bday',
  minAge: 14,
  maxAge: 100,
  mindate: null,
  maxdate: null,
  format: 'DD.MM.YYYY'
})

const emit = defineEmits<Emits>()

// State
const focused = ref<boolean>(false)
const showCalendar = ref<boolean>(false)
const datepicker = ref<HTMLInputElement | null>(null)
const selectedDate = ref<Date | null>(null)
const dropdownStyle = ref<DropdownStyle>({})

// Computed
const displayValue = computed<string>(() => {
  if (!props.modelValue) return ''

  // If modelValue is ISO format (YYYY-MM-DD), convert to display format
  if (props.modelValue.includes('-')) {
    const date = new Date(props.modelValue)
    return formatDate(date)
  }

  return props.modelValue
})

const maxDate = computed<Date>(() => {
  // If explicit maxdate prop is provided, use it
  if (props.maxdate) {
    if (props.maxdate instanceof Date) {
      return props.maxdate
    }
    // Parse string date (supports ISO format YYYY-MM-DD)
    return new Date(props.maxdate)
  }

  // Otherwise, fall back to age-based calculation (for birth date fields)
  const today = new Date()
  const maxYear = today.getFullYear() - props.minAge
  return new Date(maxYear, today.getMonth(), today.getDate())
})

const minDate = computed<Date>(() => {
  // If explicit mindate prop is provided, use it
  if (props.mindate) {
    if (props.mindate instanceof Date) {
      return props.mindate
    }
    // Parse string date (supports ISO format YYYY-MM-DD)
    return new Date(props.mindate)
  }

  // Otherwise, fall back to age-based calculation (for birth date fields)
  const today = new Date()
  const minYear = today.getFullYear() - props.maxAge
  return new Date(minYear, today.getMonth(), today.getDate())
})

// Initialize selectedDate from modelValue
if (props.modelValue) {
  if (props.modelValue.includes('-')) {
    // ISO format YYYY-MM-DD
    selectedDate.value = new Date(props.modelValue)
  } else if (props.modelValue.includes('.')) {
    // DD.MM.YYYY format
    const [day, month, year] = props.modelValue.split('.')
    selectedDate.value = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
  }
}

// Watch for changes in modelValue
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    selectedDate.value = null
    return
  }

  if (newValue.includes('-')) {
    selectedDate.value = new Date(newValue)
  } else if (newValue.includes('.')) {
    const [day, month, year] = newValue.split('.')
    selectedDate.value = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
  }
})

// Watch showCalendar to reposition dropdown
watch(showCalendar, (isShown) => {
  console.log('📅 Calendar visibility changed:', isShown)
  if (isShown) {
    nextTick(() => {
      positionDropdown()
      console.log('📍 Dropdown positioned at:', dropdownStyle.value)
    })
  }
})

// Methods
function formatDate(date: Date): string {
  if (!date) return ''

  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear()

  switch (props.format) {
    case 'YYYY-MM-DD':
      return `${year}-${month}-${day}`
    case 'MM/DD/YYYY':
      return `${month}/${day}/${year}`
    case 'DD.MM.YYYY':
    default:
      return `${day}.${month}.${year}`
  }
}

function selectDate(date: Date): void {
  selectedDate.value = date
  const formatted = formatDate(date)
  emit('update:modelValue', formatted)

  // Auto-close after selection (optional)
  setTimeout(() => {
    showCalendar.value = false
  }, 200)
}

function clearDate(): void {
  selectedDate.value = null
  emit('update:modelValue', '')
  showCalendar.value = false
}

function onFocus(): void {
  focused.value = true
  emit('focus')
  console.log('📅 Datepicker focused, showing calendar')
  showCalendar.value = true
}

async function positionDropdown(): Promise<void> {
  await nextTick()

  if (!datepicker.value) return

  const rect = datepicker.value.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom
  const spaceAbove = rect.top
  const dropdownWidth = Math.max(rect.width * 0.6, 280) // 60% of input width, minimum 280px

  // Position dropdown
  if (spaceBelow < 350 && spaceAbove > spaceBelow) {
    // Show above
    dropdownStyle.value = {
      position: 'fixed',
      left: `${rect.left}px`,
      bottom: `${window.innerHeight - rect.top + 5}px`,
      width: `${dropdownWidth}px`,
      zIndex: 9999
    }
  } else {
    // Show below
    dropdownStyle.value = {
      position: 'fixed',
      left: `${rect.left}px`,
      top: `${rect.bottom + 5}px`,
      width: `${dropdownWidth}px`,
      zIndex: 9999
    }
  }
}

function handleClickOutside(event: MouseEvent): void {
  const dropdown = document.querySelector('.calendar-dropdown')
  const target = event.target as HTMLElement

  if (dropdown && !dropdown.contains(target) &&
      datepicker.value && !datepicker.value.contains(target)) {
    showCalendar.value = false
    focused.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside as EventListener)
  window.addEventListener('scroll', positionDropdown)
  window.addEventListener('resize', positionDropdown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside as EventListener)
  window.removeEventListener('scroll', positionDropdown)
  window.removeEventListener('resize', positionDropdown)
})
</script>
  
<style lang="scss" scoped>
.hb-datepicker {
  position: relative;
  font-weight: normal;
  font-size: 14px;

  .input-wrapper {
    position: relative;
  }
  
  /* Size variants */
  &.size-sm {
    label {
      font-size: var(--text-xs);
      padding-bottom: var(--spacing-1);
    }
    
    input {
      height: calc(var(--input-height) * 0.6) !important;
      font-size: var(--text-xs);
      padding: 0 var(--spacing-3);
      padding-right: 2.5rem;
      min-height: calc(var(--input-height) * 0.8);
    }
    
    .trailing-icon {
      transform: scale(0.85) translateY(-50%);
      top: 45%;
    }
  }
  
  &.size-md {
    input {
      height: var(--input-height);
      min-height: var(--input-height);
    }
  }
  
  &.size-lg {
    label {
      font-size: var(--text-sm);
      padding-bottom: var(--spacing-2);
    }
    
    input {
      height: calc(var(--input-height) * 1.2);
      min-height: calc(var(--input-height) * 1.2);
      font-size: var(--text-base);
      padding: 0 var(--spacing-5);
      padding-right: 3rem;
    }
    
    .trailing-icon {
      transform: scale(1.15) translateY(-50%);
      top: 55%;
    }
  }

  label {
    display: flex;
    align-items: center;
    font-weight: var(--font-medium);
    font-size: var(--text-xs);
    padding-bottom: var(--spacing-2);
    color: var(--gray-500);
    
    span {
      color: var(--danger-500);
      margin-left: var(--spacing-1);
    } 
  }

  input {
    display: block;
    width: 100%;
    padding: 0 var(--spacing-4);
    padding-right: 2.5rem;
    margin: 0;
    transition: opacity .3s, border-color .3s, color .3s, background-color .3s;
    background-color: var(--white);
    border: 1px solid var(--gray-200);
    height: var(--input-height);
    border-radius: var(--input-border-radius);
    font-size: var(--text-sm);
    line-height: 1;
    appearance: none;
    -webkit-appearance: none;
    text-align: inherit;
    font-weight: var(--font-normal);
    color: var(--gray-800);
    cursor: pointer;
    
    &:disabled {
      cursor: not-allowed;
      color: var(--gray-400);
    }
    
    &:focus {
      outline: none;
      border: 1px solid var(--primary-500) !important;
      box-shadow: none;
    }
  }

  ::placeholder {
    color: var(--gray-400);
    font-size: var(--text-sm);
    font-weight: 400 !important;
  }

  .trailing-icon {
    position: absolute;
    top: 50%;
    right: var(--spacing-3);
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    color: var(--gray-500);
    cursor: pointer;
    
    &:hover {
      color: var(--primary-500);
    }
  }

  legend {
    margin-top: var(--spacing-2);
    font-size: var(--text-xs);
    color: var(--gray-500);
  }

  .error-msg {
    font-size: var(--text-sm);
    color: var(--danger-500);
    margin-top: var(--spacing-1);
  }

  &.focused {
    input {
      border-color: var(--primary-500) !important;
      border: 1px solid var(--primary-500) !important;
    }
  }

  &.fieldset-error {
    input {
      border-color: var(--danger-400);
    }

    ::placeholder {
      color: var(--danger-300);
    }
  }
  
  /* Appearance variants */
  &.appearance-white {
    input {
      background-color: var(--white) !important;
      border-color: var(--gray-200);
      color: var(--gray-800) !important;
    }
  }
  
  &.appearance-light {
    input {
      background-color: var(--gray-100) !important;
      border-color: var(--gray-100);
      color: var(--gray-800) !important;
    }
  }
  
  &.appearance-gray {
    input {
      background-color: var(--gray-100) !important;
      border-color: var(--gray-300);
      color: var(--gray-900) !important;
    }
    
    label {
      color: var(--gray-600) !important;
    }
  }
  
  &.appearance-dark {
    input {
      background-color: var(--gray-800) !important;
      border-color: var(--gray-700);
      color: var(--white) !important;
    }
    
    label {
      color: var(--gray-300) !important;
    }
    
    ::placeholder {
      color: var(--gray-500) !important;
    }
  }
}

.calendar-dropdown {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;

  :deep(.vc-container) {
    border: none;
    font-family: var(--font-body);
    width: 100% !important;
    
    .vc-pane-container {
      width: 100%;
    }
    
    .vc-pane {
      width: 100%;
      min-width: auto;
    }
    
    .vc-header {
      // Respect v-calendar's grid layout
      display: grid;
      align-items: center;
      
      .vc-title-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        grid-column: title;
        position: relative;
        top: -10px !important;
      }
      
      .vc-title {
        font-weight: var(--font-medium);
        color: var(--gray-800);
        font-size: var(--text-sm);
        background: transparent;
        border: none;
        cursor: pointer;
        padding: var(--spacing-2);
        border-radius: var(--radius-md);
        
        &:hover {
          background-color: var(--gray-100);
        }
      }
      
      .vc-arrow {
        color: var(--gray-600);
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius-md);
        background: transparent;
        border: none;
        cursor: pointer;
        
        &:hover {
          background-color: var(--gray-200);
        }
        
        svg {
          width: 18px;
          height: 18px;
        }
      }
      
      .vc-arrow.is-left {
        grid-column: prev;
      }
      
      .vc-arrow.is-right {
        grid-column: next;
      }
    }

    .vc-weeks {
      padding: var(--spacing-2);
      width: 100%;
    }
    
    .vc-weekdays {
      padding: 0 var(--spacing-2);
      margin-bottom: var(--spacing-1);
    }
    
    .vc-weekday {
      color: var(--gray-500);
      font-weight: var(--font-medium);
      font-size: var(--text-xs);
      padding: var(--spacing-1);
    }

    .vc-day {
      &.is-today {
        .vc-day-content {
          font-weight: var(--font-normal);
          border: 1px solid var(--primary-500);
        }
      }

      &:hover {
        .vc-day-content {
          background-color: var(--gray-100);
        }
      }
      
      .vc-highlight {
        background-color: var(--primary-500) !important;
      }
      
      .vc-day-content {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }
  }

  .calendar-actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-2);
    padding: var(--spacing-3);
    border-top: 1px solid var(--gray-200);
    background-color: var(--gray-50);
  }
}
</style>
  