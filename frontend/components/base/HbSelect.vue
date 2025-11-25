<template>
  <div
    class="hb-select"
    :class="[
      { 'is--expanded': expanded },
      `size-${size}`,
      `appearance-${appearance}`
    ]"
  >
    <label
      v-if="label"
      @click="expanded ? collapse() : expand()"
    >{{ label }}<span v-if="required">*</span></label>
    <div class="hb-select__inner">
      <div
        ref="selectWrapper"
        class="hb-select__selection items-center"
        tabindex="0"
        @click="expanded ? collapse() : expand()"
        @keydown.tab="collapse"
        @keydown.esc="collapse"
      >
        <div class="select-content">
          <div
            class="hb-select__selection-text"
            :class="selectionTextClasses"
          >
            <template v-if="expanded && searchable && filter">
              {{ filter }}
            </template>
            <template v-else-if="singleSelection">
              {{ singleSelection }}
            </template>
            <template v-else>
              {{ placeholder }}
            </template>
          </div>
        </div>

        <div
          v-if="clearable && singleSelection"
          class="clear-indicator"
          @click.stop="clearSelection"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
          </svg>
        </div>

        <div class="select-indicator">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>

      <Teleport to="body">
        <transition name="fade">
          <ul
            v-if="expanded"
            ref="resultsList"
            class="hb-select__result-list"
            :class="`appearance-${appearance}`"
          >
            <li
              v-for="(item, idx) in filteredResults"
              :key="typeof item === 'object' && item !== null ? (item as Record<string, unknown>).value as PropertyKey : idx"
              :class="[
                {
                  'selected': isSelected(item),
                  'highlighted': idx < highlightedRows
                },
                'hb-select-option--' + idx
              ]"
              @click="setValue(item)"
            >
              <slot
                :option="item"
                name="resultItem"
              >
                <div class="option-content">
                  <div class="option-label">{{ typeof item === 'object' ? item[optionLabel] : item }}</div>
                  <div v-if="typeof item === 'object' && item.description" class="option-description">{{ item.description }}</div>
                </div>
              </slot>
            </li>
            <li
              v-if="!filteredResults.length"
              class="no-result"
            >
              No results found
            </li>
          </ul>
        </transition>
      </Teleport>
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
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

type OptionValue = string | number | Record<string, unknown>

interface Props {
  modelValue?: OptionValue | null
  options: OptionValue[]
  id?: string
  autocomplete?: string
  label?: string
  optionLabel?: string
  reduce?: ((option: OptionValue) => unknown) | null
  placeholder?: string
  dropDownWidth?: string
  clearable?: boolean
  searchable?: boolean
  highlightedRows?: number
  required?: boolean
  error?: string
  helperText?: string
  defaultValue?: OptionValue | null
  size?: 'sm' | 'md' | 'lg'
  appearance?: 'dark' | 'gray' | 'light' | 'white'
}

interface Emits {
  (e: 'update:modelValue', value: OptionValue | null): void
  (e: 'onClear'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  id: '',
  autocomplete: 'off',
  label: '',
  optionLabel: 'label',
  reduce: null,
  placeholder: 'Select an option',
  dropDownWidth: '',
  clearable: false,
  searchable: false,
  highlightedRows: 0,
  required: false,
  error: '',
  helperText: '',
  defaultValue: null,
  size: 'md',
  appearance: 'white'
})

const emit = defineEmits<Emits>()

// Refs
const selectWrapper = ref<HTMLElement | null>(null)
const resultsList = ref<HTMLElement | null>(null)
const expanded = ref<boolean>(false)
const itemRecentlySelected = ref<boolean>(false)
const filter = ref<string>('')

// Computed
const selectionTextClasses = computed(() => ({
  'is--placeholder': !singleSelection.value
}))

const singleSelection = computed<string>(() => {
  let selected: OptionValue | undefined

  if (props.reduce) {
    if (props.modelValue) {
      for (const option of props.options) {
        const key = getKeyByValue(option as Record<string, unknown>, props.modelValue)
        if (key) {
          const found = props.options.find(o => (o as Record<string, unknown>)[key] === props.modelValue)
          return found ? (found as Record<string, unknown>)[props.optionLabel] as string : ''
        }
      }
    } else {
      return ''
    }
  }

  // when model.value is object without reduce
  if (typeof props.modelValue === 'object' && props.modelValue !== null && !props.reduce) {
    selected = props.options.find(option => isEqual(option, props.modelValue))
    // dirty hack to prevent errors on item-removal
    return selected && (selected as Record<string, unknown>)[props.optionLabel]
      ? (selected as Record<string, unknown>)[props.optionLabel] as string
      : ''
  }

  // when model.value is string
  // First try to find an exact match
  selected = props.options.find(option => option === props.modelValue)

  // If no exact match is found, try to match by value property
  if (!selected && typeof props.options[0] === 'object' && props.options[0] !== null) {
    selected = props.options.find(option => (option as Record<string, unknown>).value === props.modelValue)
    if (selected) {
      return (selected as Record<string, unknown>)[props.optionLabel] as string
    }
  }

  return selected as string ?? ''
})

const filteredResults = computed<OptionValue[]>(() => {
  if (!props.options || !Array.isArray(props.options)) return []
  if (!filter.value) return props.options

  const filtered = props.options.filter(e => {
    if (!e) return false
    if (typeof e === 'object' && e !== null) {
      const label = (e as Record<string, unknown>)[props.optionLabel]
      return label && typeof label === 'string' ? label.toLowerCase().includes(filter.value.toLowerCase()) : false
    } else if (typeof e === 'number') {
      return e.toString().includes(filter.value)
    } else if (typeof e === 'string') {
      return e.toLowerCase().includes(filter.value.toLowerCase())
    }
    return false
  })
  return filtered
})

// Methods
function isEqual(obj1: unknown, obj2: unknown): boolean {
  // Simple deep comparison for objects
  if (obj1 === obj2) return true

  if (typeof obj1 !== 'object' || obj1 === null ||
      typeof obj2 !== 'object' || obj2 === null) {
    return false
  }

  const keys1 = Object.keys(obj1 as Record<string, unknown>)
  const keys2 = Object.keys(obj2 as Record<string, unknown>)

  if (keys1.length !== keys2.length) return false

  for (const key of keys1) {
    if (!keys2.includes(key)) return false

    const val1 = (obj1 as Record<string, unknown>)[key]
    const val2 = (obj2 as Record<string, unknown>)[key]

    if (typeof val1 === 'object' && typeof val2 === 'object') {
      if (!isEqual(val1, val2)) return false
    } else if (val1 !== val2) {
      return false
    }
  }

  return true
}

function toggleExpand(): void {
  if (!expanded.value) {
    expand()
  } else {
    collapse()
  }
}

function expand(): void {
  if (expanded.value) {
    return
  }

  expanded.value = true
  document.addEventListener('click', listenToClickOutside)

  nextTick(() => {
    nextTick(() => {
      handleDropdownPositioning()
      window.addEventListener('resize', handleDropdownPositioning)
      window.addEventListener('scroll', handleDropdownPositioning)
    })
  })
}

function handleDropdownPositioning(): void {
  const wrapper = selectWrapper.value
  const dropdown = resultsList.value

  if (!wrapper || !dropdown) return

  const offsetTop = wrapper.getBoundingClientRect().top + dropdown.getBoundingClientRect().height + 60

  dropdown.style.left = (wrapper.getBoundingClientRect().left - 1) + 'px'
  dropdown.style.width = props.dropDownWidth ? props.dropDownWidth : (wrapper.getBoundingClientRect().width + 2) + 'px'

  if (offsetTop > window.innerHeight) {
    dropdown.style.top = ((wrapper.getBoundingClientRect().top + window.scrollY) - dropdown.getBoundingClientRect().height - 10) + 'px'
  } else {
    dropdown.style.top = (wrapper.getBoundingClientRect().top + window.scrollY + wrapper.getBoundingClientRect().height + 10) + 'px'
  }
}

function collapse(): void {
  document.removeEventListener('click', listenToClickOutside)
  window.removeEventListener('resize', handleDropdownPositioning)
  window.removeEventListener('scroll', handleDropdownPositioning)
  expanded.value = false
  itemRecentlySelected.value = false
}

function listenToClickOutside(event: Event): void {
  const mouseEvent = event as MouseEvent & { path?: EventTarget[] }
  let path = mouseEvent.path
  if (typeof path === 'undefined') {
    path = computePath(event)
  }

  const wrapperEl = selectWrapper.value
  if (wrapperEl && !path.find((element) => element === wrapperEl.parentElement)) {
    collapse()
  }
}

function computePath(event: Event): EventTarget[] {
  const path: EventTarget[] = []
  let target = event.target as HTMLElement | null

  while (target) {
    path.push(target)
    target = target.parentElement
  }

  return path
}

function getKeyByValue(object: Record<string, unknown>, value: unknown): string | undefined {
  for (const prop in object) {
    if (Object.values(object).includes(value as never)) {
      if (object[prop] === value) return prop
    }
  }
  return undefined
}

function isSelected(item: OptionValue): boolean {
  // Handle both object and string values
  if (typeof item === 'object' && item !== null) {
    if (typeof props.modelValue === 'object' && props.modelValue !== null) {
      return (item as Record<string, unknown>).value === (props.modelValue as Record<string, unknown>).value
    }
    return (item as Record<string, unknown>).value === props.modelValue
  }
  return item === props.modelValue
}

function setValue(item: OptionValue | null): void {
  itemRecentlySelected.value = true

  // Emit the value property if it's an object, otherwise emit the item itself
  if (typeof item === 'object' && item !== null && (item as Record<string, unknown>).value !== undefined) {
    emit('update:modelValue', (item as Record<string, unknown>).value as OptionValue)
  } else {
    emit('update:modelValue', item)
  }

  collapse()
}

function clearSelection(): void {
  setValue(null)
  emit('onClear')
}

function handleKeystrokes(event: KeyboardEvent): void {
  const validKey = event.key.length === 1 || event.key === 'Backspace'
  if (validKey) {
    if (event.key === 'Backspace') {
      filter.value = filter.value.slice(0, -1)
    } else {
      filter.value += event.key
    }
  }
}

// Watchers
watch(expanded, (newValue) => {
  if (newValue) {
    if (!props.searchable) return
    filter.value = ''
    window.addEventListener('keydown', handleKeystrokes)
  } else {
    window.removeEventListener('keydown', handleKeystrokes)
  }
})

// Lifecycle
onMounted(() => {
  // Only set a default value if modelValue is truly empty/null/undefined
  // and a defaultValue is explicitly provided
  if ((props.modelValue === null || props.modelValue === undefined || props.modelValue === '') &&
      props.defaultValue !== null && props.defaultValue !== undefined) {
    emit('update:modelValue', props.defaultValue)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeystrokes)
})
</script>

<style lang="scss" scoped>
.hb-select {
  position: relative;
  width: 100%;
  font-weight: normal;
  font-size: 14px;
  
  label {
    display: flex;
    align-items: center;
    font-weight: var(--font-medium);
    font-size: var(--text-xs);
    padding-bottom: var(--spacing-2);
    color: var(--gray-500);
    cursor: pointer;
    
    span {
      color: var(--danger-500);
      margin-left: var(--spacing-1);
    }
  }

  .hb-select__inner {
    height: var(--input-height);
    user-select: none;
    position: relative;
    overflow: hidden;
    border: 1px solid var(--gray-200);
    border-radius: var(--input-border-radius);
    transition: all 0.3s ease;
    background: var(--white);
    color: var(--gray-800);
  }
  
  /* Size variants */
  &.size-sm {
    label {
      font-size: var(--text-xs);
      padding-bottom: var(--spacing-1);
    }
    
    .hb-select__inner {
      height: calc(var(--input-height) * 0.6);
      min-height: calc(var(--input-height) * 0.8);
    }
    
    .hb-select__selection {
      padding: 0 0.75rem;
      font-size: var(--text-xs);
    }
    
    .select-indicator {
      width: 16px;
      height: 16px;
    }
    
    .clear-indicator {
      width: 14px;
      height: 14px;
    }
  }
  
  &.size-md {
    .hb-select__inner {
      height: var(--input-height);
    }
  }
  
  &.size-lg {
    label {
      font-size: var(--text-sm);
      padding-bottom: var(--spacing-2);
    }
    
    .hb-select__inner {
      height: calc(var(--input-height) * 1.2);
    }
    
    .hb-select__selection {
      padding: 0 1.25rem;
      font-size: var(--text-sm);
      font-family: var(--font-heading);
      font-weight: 400 !important;
      color: var(--gray-700);
    }
    
    .select-indicator {
      width: 24px;
      height: 24px;
    }
  }

  .hb-select__selection {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
    height: 100%;
    padding: 0 1rem;
    outline: none;
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    cursor: pointer;
    overflow: hidden;

    &:focus-visible {
      outline: 1px solid var(--primary-500);
      box-shadow: 0 0 0 6px white;
      position: relative;
      z-index: 1;
    }

    .select-indicator {
      transition: transform 0.3s ease;
      width: 20px;
      height: 20px;
      color: var(--gray-500);
      
      svg {
        width: 100%;
        height: 100%;
      }
    }
  }

  .hb-select__selection-text {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    &.is--placeholder {
      color: var(--gray-400);
    }
  }

  .select-content {
    flex: 1;
    display: flex;
    flex-direction: row;
    gap: 0.5rem;
    align-items: center;
    overflow: hidden;
  }

  .clear-indicator {
    width: 16px;
    height: 16px;
    color: var(--danger-500);
    cursor: pointer;
    flex-shrink: 0;
    
    svg {
      width: 100%;
      height: 100%;
    }

    &:hover {
      color: var(--danger-600);
      transition: color 0.3s ease;
    }
  }

  &.is--expanded {
    .hb-select__inner {
      border-color: var(--primary-500);
      box-shadow: none;
    }

    .hb-select__selection {
      .select-indicator {
        transform: rotate(180deg);
      }
    }
  }
  
  .error-msg {
    display: block;
    color: var(--danger-600);
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  
  .helper-text {
    display: block;
    color: var(--gray-500);
    font-size: 0.75rem;
    margin-top: 0.25rem;
  }
  
  /* Appearance variants */
  &.appearance-white {
    .hb-select__inner {
      background-color: var(--white) !important;
      border-color: var(--gray-200);
      color: var(--gray-800) !important;
    }
  }
  
  &.appearance-light {
    .hb-select__inner {
      background-color: var(--gray-100) !important;
      border-color: var(--gray-100);
      color: var(--gray-800) !important;
    }
    
    .hb-select__selection-text.is--placeholder {
      color: var(--gray-400);
    }
  }
  
  &.appearance-gray {
    .hb-select__inner {
      background-color: var(--gray-100) !important;
      border-color: var(--gray-300);
      color: var(--gray-900) !important;
    }
    
    label {
      color: var(--gray-600) !important;
    }
  }
  
  &.appearance-dark {
    .hb-select__inner {
      background-color: var(--primary-900) !important;
      border-color: var(--primary-800);
      color: var(--white) !important;
    }
    
    label {
      color: var(--gray-300) !important;
    }
    
    .hb-select__selection-text.is--placeholder {
      color: var(--gray-500) !important;
    }
    
    .select-indicator,
    .clear-indicator {
      color: var(--gray-400);
    }
    
    &.is--expanded {
      .hb-select__inner {
        border-color: var(--primary-400);
      }
    }
  }
}

.hb-select__result-list {
  position: absolute;
  z-index: 9999;
  margin: 0;
  padding: 0;
  list-style: none;
  background-color: var(--white);
  border: 1px solid var(--primary-200);
  border-radius: var(--input-border-radius);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  font-family: var(--font-body);
  font-weight: normal;
  font-size: 14px;
  overflow: hidden;
  overflow-y: auto;
  max-height: 240px;
  
  /* Dark appearance for dropdown */
  &.appearance-dark {
    background-color: var(--primary-950);
    border-color: var(--primary-800);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
  }
  
  /* Custom Scrollbar Styling */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--gray-100);
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--gray-300);
    transition: background 0.2s ease;
    
    &:hover {
      background: var(--gray-400);
    }
  }
  
  /* Firefox Scrollbar */
  scrollbar-width: thin;
  scrollbar-color: var(--gray-300) var(--gray-100);
  
  /* Dark scrollbar */
  &.appearance-dark {
    &::-webkit-scrollbar-track {
      background: var(--primary-1000);
    }
    
    &::-webkit-scrollbar-thumb {
      background: var(--primary-700);
      
      &:hover {
        background: var(--primary-600);
      }
    }
    
    scrollbar-color: var(--primary-700) var(--primary-1000);
  }
  
  li {
    padding: 12px 1rem 10px 1rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
    border-bottom: 1px solid rgba(0, 0, 0, 0.03);
    
    .option-content {
      display: flex;
      flex-direction: column;
      
      .option-label {
        font-size: 14px;
        color: var(--gray-800);
      }
      
      .option-description {
        font-size: 0.75rem;
        color: var(--gray-500);
        margin-top: 0.25rem;
      }
    }
    
    &.selected {
      color: var(--primary-600);
      font-weight: 500;
      background-color: var(--primary-50);
      
      .option-description {
        color: var(--primary-700);
      }
    }
    
    &.highlighted {
      background-color: var(--primary-50);
      font-weight: 500;
    }
    
    &.no-result {
      color: var(--gray-500);
      font-style: italic;
      cursor: default;
      text-align: center;
      
      &:hover {
        background-color: transparent;
      }
    }
    
    @media (hover: hover) {
      &:hover:not(.no-result) {
        background-color: var(--primary-100);
        color: var(--gray-900);
      }
    }
  }
  
  /* Dark theme list items */
  &.appearance-dark li {
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    
    .option-content {
      .option-label {
        color: var(--gray-200);
      }
      
      .option-description {
        color: var(--gray-400);
      }
    }
    
    &.selected {
      color: var(--primary-300);
      background-color: var(--primary-800);
      
      .option-content .option-label {
        color: var(--primary-200);
      }
      
      .option-description {
        color: var(--primary-300);
      }
    }
    
    &.highlighted {
      background-color: var(--primary-800);
    }
    
    &.no-result {
      color: var(--gray-400);
    }
    
    @media (hover: hover) {
      &:hover:not(.no-result) {
        background-color: var(--primary-850);
        color: var(--primary-200);
        
        .option-content .option-label {
          color: var(--primary-100);
        }
      }
    }
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
