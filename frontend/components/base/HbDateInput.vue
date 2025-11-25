<template>
  <div 
    class="hb-date-input"
    :class="[
      { 'focused': focused },
      { 'not-empty': modelValue },
      { 'has-error': error }
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
        v-model="displayValue"
        type="text"
        readonly
        :name="id"
        :required="required"
        :disabled="disabled"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        @click="toggleCalendar"
        @focus="focused = true"
        @blur="focused = false"
      >
      <div
        class="calendar-icon"
        @click="toggleCalendar"
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
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
        </svg>
      </div>
      
      <Transition name="fade">
        <div
          v-if="showCalendar"
          class="calendar-dropdown"
          ref="calendarDropdown"
        >
          <div class="calendar-header">
            <button 
              class="month-nav" 
              @click="prevMonth"
            >
              &lt;
            </button>
            <div class="month-year-selector" @click="toggleMonthYearSelector">
              <span>{{ currentMonthName }} {{ currentYear }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="chevron-icon" :class="{ 'rotate': showMonthYearSelector }">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
              </svg>
            </div>
            <button 
              class="month-nav" 
              @click="nextMonth"
            >
              &gt;
            </button>
          </div>
          
          <!-- Month/Year Selector -->
          <div v-if="showMonthYearSelector" class="month-year-dropdown">
            <div class="selector-tabs">
              <button 
                :class="{ 'active': selectorView === 'month' }" 
                @click="selectorView = 'month'"
              >
                Month
              </button>
              <button 
                :class="{ 'active': selectorView === 'year' }" 
                @click="selectorView = 'year'"
              >
                Year
              </button>
            </div>
            
            <!-- Month Selection -->
            <div v-if="selectorView === 'month'" class="month-grid">
              <div 
                v-for="(month, index) in monthNames" 
                :key="month"
                class="month-item"
                :class="{ 'selected': currentMonth === index }"
                @click="selectMonth(index)"
              >
                {{ getMonthAbbreviation(month) }}
              </div>
            </div>
            
            <!-- Year Selection -->
            <div v-else class="year-grid">
              <button class="year-nav" @click="prevYearPage">&lt;</button>
              <div class="year-list">
                <div 
                  v-for="year in yearRange" 
                  :key="year"
                  class="year-item"
                  :class="{ 'selected': currentYear === year }"
                  @click="selectYear(year)"
                >
                  {{ year }}
                </div>
              </div>
              <button class="year-nav" @click="nextYearPage">&gt;</button>
            </div>
          </div>
          
          <div class="calendar-grid">
            <div class="weekday" v-for="day in weekdays" :key="day">{{ day }}</div>
            <div 
              v-for="{ date, current, today, selected } in calendarDays" 
              :key="date.getTime()"
              class="day"
              :class="{
                'current-month': current,
                'today': today,
                'selected': selected
              }"
              @click="selectDate(date)"
            >
              {{ date.getDate() }}
            </div>
          </div>
          
          <div class="calendar-actions">
            <button
              class="calendar-action"
              @click="clearDate"
              type="button"
            >
              Clear
            </button>
            <button
              class="calendar-action primary"
              @click="showCalendar = false"
              type="button"
            >
              Done
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <span 
      v-if="error" 
      class="error-msg"
    >
      {{ error }}
    </span>
    <span 
      v-else-if="helperText" 
      class="helper-text"
    >
      {{ helperText }}
    </span>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

interface CalendarDay {
  date: Date
  current: boolean
  today: boolean
  selected: boolean
}

interface Props {
  modelValue?: string
  id?: string
  label?: string
  required?: boolean
  disabled?: boolean
  error?: string
  helperText?: string
  placeholder?: string
  autocomplete?: string
  minDate?: Date | string | null
  maxDate?: Date | string | null
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  id: () => `date-${Math.random().toString(36).substr(2, 9)}`,
  label: 'Date',
  required: false,
  disabled: false,
  error: '',
  helperText: '',
  placeholder: 'DD.MM.YYYY',
  autocomplete: 'bday',
  minDate: null,
  maxDate: null
})

const emit = defineEmits<Emits>()

// Refs
const calendarDropdown = ref<HTMLElement | null>(null)
const focused = ref<boolean>(false)
const showCalendar = ref<boolean>(false)
const currentMonth = ref<number>(new Date().getMonth())
const currentYear = ref<number>(new Date().getFullYear())
const weekdays = ref<string[]>(['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'])
const selectedDate = ref<Date | null>(null)
const showMonthYearSelector = ref<boolean>(false)
const selectorView = ref<'month' | 'year'>('month')
const yearPageStart = ref<number>(new Date().getFullYear() - 6)
const monthNames = ref<string[]>([
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
])

// Computed
const displayValue = computed<string>(() => {
  if (!props.modelValue) return ''
  const date = new Date(props.modelValue)
  if (isNaN(date.getTime())) {
    // Try parsing YYYY-MM-DD format
    const [year, month, day] = props.modelValue.split('-')
    const parsedDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
    return formatDate(parsedDate)
  }
  return formatDate(date)
})

const currentMonthName = computed<string>(() => {
  return monthNames.value[currentMonth.value]
})

const yearRange = computed<number[]>(() => {
  // Generate a range of years for the year selector
  const years: number[] = []
  for (let i = 0; i < 12; i++) {
    years.push(yearPageStart.value + i)
  }
  return years
})

const calendarDays = computed<CalendarDay[]>(() => {
  const days: CalendarDay[] = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)

  // Get the day of the week for the first day (0 = Sunday, 1 = Monday, etc.)
  let firstDayOfWeek = firstDay.getDay()
  // Adjust for Monday as first day of week
  firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1

  // Add days from previous month
  const prevMonthLastDay = new Date(currentYear.value, currentMonth.value, 0).getDate()
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(currentYear.value, currentMonth.value - 1, prevMonthLastDay - i)
    days.push({
      date,
      current: false,
      today: isToday(date),
      selected: isSelected(date)
    })
  }

  // Add days from current month
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(currentYear.value, currentMonth.value, i)
    days.push({
      date,
      current: true,
      today: isToday(date),
      selected: isSelected(date)
    })
  }

  // Add days from next month
  const daysNeeded = 42 - days.length // 6 rows of 7 days
  for (let i = 1; i <= daysNeeded; i++) {
    const date = new Date(currentYear.value, currentMonth.value + 1, i)
    days.push({
      date,
      current: false,
      today: isToday(date),
      selected: isSelected(date)
    })
  }

  return days
})

const computedMinDate = computed<Date | null>(() => {
  if (!props.minDate) return null
  return typeof props.minDate === 'string' ? new Date(props.minDate) : props.minDate
})

const computedMaxDate = computed<Date | null>(() => {
  if (!props.maxDate) return null
  return typeof props.maxDate === 'string' ? new Date(props.maxDate) : props.maxDate
})

// Methods
function formatDate(date: Date): string {
  if (!date || isNaN(date.getTime())) return ''
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear()

  return `${day}.${month}.${year}`
}

function formatDateForModel(date: Date): string {
  if (!date || isNaN(date.getTime())) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function toggleCalendar(): void {
  if (props.disabled) return
  showCalendar.value = !showCalendar.value
}

function selectDate(date: Date): void {
  if (isDateDisabled(date)) return

  selectedDate.value = date
  emit('update:modelValue', formatDateForModel(date))
  showCalendar.value = false
}

function clearDate(): void {
  selectedDate.value = null
  emit('update:modelValue', '')
  showCalendar.value = false
}

function prevMonth(): void {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth(): void {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
  showMonthYearSelector.value = false
}

function toggleMonthYearSelector(): void {
  showMonthYearSelector.value = !showMonthYearSelector.value
}

function selectMonth(monthIndex: number): void {
  currentMonth.value = monthIndex
  // Just close the month/year selector, not the calendar
  showMonthYearSelector.value = false
}

function selectYear(year: number): void {
  currentYear.value = year
  // Just close the month/year selector, not the calendar
  showMonthYearSelector.value = false
}

function prevYearPage(): void {
  yearPageStart.value -= 12
}

function nextYearPage(): void {
  yearPageStart.value += 12
}

function getMonthAbbreviation(month: string): string {
  // Custom abbreviations for months
  const abbreviations: Record<string, string> = {
    'January': 'Jan',
    'February': 'Feb',
    'March': 'Mar',
    'April': 'Apr',
    'May': 'May',
    'June': 'Jun',
    'July': 'Jul',
    'August': 'Aug',
    'September': 'Sep',
    'October': 'Oct',
    'November': 'Nov',
    'December': 'Dec'
  }

  return abbreviations[month] || month.substring(0, 3)
}

function isToday(date: Date): boolean {
  const today = new Date()
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear()
}

function isSelected(date: Date): boolean {
  if (!selectedDate.value) return false

  return date.getDate() === selectedDate.value.getDate() &&
         date.getMonth() === selectedDate.value.getMonth() &&
         date.getFullYear() === selectedDate.value.getFullYear()
}

function isDateDisabled(date: Date): boolean {
  if (computedMinDate.value && date < computedMinDate.value) return true
  if (computedMaxDate.value && date > computedMaxDate.value) return true
  return false
}

function handleClickOutside(event: MouseEvent): void {
  const calendar = calendarDropdown.value
  const target = event.target as HTMLElement
  const rootEl = calendar?.parentElement?.parentElement

  if (!rootEl) return

  const input = rootEl.querySelector('input')
  const icon = rootEl.querySelector('.calendar-icon')

  if (showCalendar.value && calendar &&
      !calendar.contains(target) &&
      !input?.contains(target) &&
      !icon?.contains(target)) {
    showCalendar.value = false
  }
}

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    const date = new Date(newVal)
    if (!isNaN(date.getTime())) {
      selectedDate.value = date
      currentMonth.value = date.getMonth()
      currentYear.value = date.getFullYear()
    }
  } else {
    selectedDate.value = null
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside as EventListener)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside as EventListener)
})
</script>

<style lang="scss" scoped>
.hb-date-input {
  position: relative;
  width: 100%;
  
  label {
    display: block;
    margin-bottom: 0.25rem;
    color: #1f2937; /* gray-800 */
    font-weight: 500;
    font-size: 0.875rem;
    
    span {
      color: #ef4444; /* red-500 */
    }
  }
  
  .input-wrapper {
    position: relative;
    width: 100%;
    
    input {
      display: block;
      width: 100%;
      height: 2.75rem; /* ~44px */
      padding: 0 1rem;
      padding-right: 2.5rem;
      margin: 0;
      border: 1px solid #e5e7eb; /* gray-200 */
      border-radius: 0.5rem; /* rounded-lg */
      font-size: 0.875rem;
      line-height: 1;
      transition: all .2s ease;
      background-color: #ffffff;
      color: #1f2937; /* gray-800 */
      appearance: none;
      -webkit-appearance: none;
      text-align: inherit;
      font-weight: 400;
      font-family: inherit;
      cursor: pointer;
      
      &:focus {
        outline: none;
        border-color: #0ea5e9; /* primary-500 */
      }
      
      &:disabled {
        background-color: #f3f4f6; /* gray-100 */
        cursor: not-allowed;
      }
      
      &::placeholder {
        color: #9ca3af; /* gray-400 */
      }
    }
    
    .calendar-icon {
      position: absolute;
      right: 1rem;
      top: 50%;
      transform: translateY(-50%);
      width: 20px;
      height: 20px;
      color: #6b7280; /* gray-500 */
      cursor: pointer;
      transition: color 0.2s ease;
      
      &:hover {
        color: #0ea5e9; /* primary-500 */
      }
      
      svg {
        width: 100%;
        height: 100%;
      }
    }
    
    .calendar-dropdown {
      position: absolute;
      top: calc(100% + 5px);
      left: 0;
      z-index: 100;
      width: 300px;
      background: #ffffff;
      border: 1px solid #e5e7eb; /* gray-200 */
      border-radius: 0.5rem; /* rounded-lg */
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      
      .calendar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e5e7eb; /* gray-200 */
        font-weight: 500;
        
        .month-nav {
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: none;
          border: none;
          border-radius: 0.25rem;
          cursor: pointer;
          
          &:hover {
            background-color: #f3f4f6; /* gray-100 */
          }
        }
        
        .month-year-selector {
          display: flex;
          align-items: center;
          cursor: pointer;
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          
          &:hover {
            background-color: #f3f4f6; /* gray-100 */
          }
          
          .chevron-icon {
            width: 16px;
            height: 16px;
            margin-left: 0.25rem;
            transition: transform 0.2s ease;
            
            &.rotate {
              transform: rotate(180deg);
            }
          }
        }
      }
      
      .month-year-dropdown {
        padding: 0.25rem 0.5rem;
        border-bottom: 1px solid #e5e7eb; /* gray-200 */
        
        .selector-tabs {
          display: flex;
          margin-bottom: 0.25rem;
          
          button {
            flex: 1;
            padding: 0.25rem;
            background: none;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.75rem;
            
            &.active {
              border-bottom-color: #0ea5e9; /* primary-500 */
              color: #0ea5e9; /* primary-500 */
            }
          }
        }
        
        .month-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 0.25rem;
          
          .month-item {
            padding: 0.25rem;
            text-align: center;
            cursor: pointer;
            border-radius: 0.25rem;
            font-size: 0.7rem;
            
            &:hover {
              background-color: #f3f4f6; /* gray-100 */
            }
            
            &.selected {
              background-color: #0ea5e9; /* primary-500 */
              color: white;
            }
          }
        }
        
        .year-grid {
          display: flex;
          align-items: center;
          
          .year-nav {
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: none;
            border: none;
            cursor: pointer;
            flex-shrink: 0;
          }
          
          .year-list {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.5rem;
            flex-grow: 1;
            
            .year-item {
              padding: 0.25rem;
              text-align: center;
              cursor: pointer;
              border-radius: 0.25rem;
              font-size: 0.7rem;
              
              &:hover {
                background-color: #f3f4f6; /* gray-100 */
              }
              
              &.selected {
                background-color: #0ea5e9; /* primary-500 */
                color: white;
              }
            }
          }
        }
      }
      
      .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        padding: 0.5rem;
        
        .weekday {
          text-align: center;
          font-weight: 500;
          font-size: 0.75rem;
          color: #6b7280; /* gray-500 */
          padding: 0.5rem 0;
        }
        
        .day {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 36px;
          font-size: 0.875rem;
          cursor: pointer;
          border-radius: 0.25rem;
          
          &:hover {
            background-color: #f3f4f6; /* gray-100 */
          }
          
          &.current-month {
            color: #1f2937; /* gray-800 */
          }
          
          &:not(.current-month) {
            color: #9ca3af; /* gray-400 */
          }
          
          &.today {
            font-weight: 600;
          }
          
          &.selected {
            background-color: #0ea5e9; /* primary-500 */
            color: white;
          }
        }
      }
      
      .calendar-actions {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        border-top: 1px solid #e5e7eb; /* gray-200 */
        
        .calendar-action {
          padding: 0.375rem 0.75rem;
          border: none;
          background: none;
          color: #1f2937; /* gray-800 */
          cursor: pointer;
          font-size: 0.875rem;
          border-radius: 0.375rem; /* rounded-md */
          transition: all 0.2s ease;
          
          &:hover {
            background-color: #f3f4f6; /* gray-100 */
          }
          
          &.primary {
            background-color: #0ea5e9; /* primary-500 */
            color: white;
            
            &:hover {
              background-color: #0284c7; /* primary-600 */
            }
          }
        }
      }
    }
  }
  
  &.has-error {
    .input-wrapper input {
      border-color: #ef4444; /* red-500 */
    }
  }
  
  &.focused {
    .input-wrapper input {
      border-color: #0ea5e9; /* primary-500 */
    }
  }
  
  .error-msg {
    display: block;
    color: #ef4444; /* red-500 */
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  
  .helper-text {
    display: block;
    color: #6b7280; /* gray-500 */
    font-size: 0.75rem;
    margin-top: 0.25rem;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
