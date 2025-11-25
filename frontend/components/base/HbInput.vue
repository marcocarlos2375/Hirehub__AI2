<template>
  <div
    class="hb-fieldset"
    :class="[
      { 'focused': focused },
      { 'not-empty': modelValue },
      { 'fieldset-error': error },
      type,
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
      <textarea
        v-if="type === 'textarea'"
        :id="id"
        :ref="id"
        :value="modelValue"
        :name="id"
        rows="6"
        :autofocus="autofocus"
        :autocomplete="autocomplete"
        :placeholder="placeholder"
        :disabled="disabled"
        @focus="onFocus"
        @blur="onBlur"
        @keyup.enter="($event.target as HTMLTextAreaElement).blur()"
        @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      />
  
      <div
        v-else-if="type === 'birthdate'"
        class="birthdate"
      >
        <input
          :id="`${id}-day`"
          :ref="`${id}-day`"
          v-model="birthdate.day"
          :name="`${id}-day`"
          type="number"
          :autocomplete="autocomplete"
          :autofocus="autofocus"
          :disabled="disabled"
          placeholder="01"
          min="1"
          max="31"
          digits="2"
          pattern="[0-1]*"
          @keyup.enter="focusNextInput('day')"
          @blur="onBlurBirthdate('day')"
        >
        <input
          :id="`${id}-month`"
          :ref="`${id}-month`"
          v-model="birthdate.month"
          :name="`${id}-month`"
          type="number"
          :autocomplete="autocomplete"
          :disabled="disabled"
          placeholder="01"
          min="1"
          max="12"
          pattern="[0-1]*"
          @keyup.enter="focusNextInput('month')"
          @blur="onBlurBirthdate('month')"
        >
        <input
          :id="`${id}-year`"
          :ref="`${id}-year`"
          v-model="birthdate.year"
          :name="`${id}-year`"
          type="number"
          :autocomplete="autocomplete"
          :disabled="disabled"
          :placeholder="String(new Date().getFullYear())"
          min="1900"
          :max="String(new Date().getFullYear())"
          @keyup.enter="($event.target as HTMLInputElement).blur()"
          @blur="onBlurBirthdate('year')"
        >
      </div>
  
      <input
        v-else
        :id="id"
        :ref="id"
        :value="modelValue"
        :name="id"
        :type="computedType"
        :autofocus="autofocus"
        :disabled="disabled"
        :autocomplete="autocomplete"
        :placeholder="placeholder"
        :pattern="pattern"
        @focus="onFocus"
        @blur="onBlur"
        @keyup.enter="($event.target as HTMLInputElement).blur()"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      >

      <div
        v-if="type === 'url'"
        class="protocol"
      >
        https://
      </div>
  
      <div
        v-if="type === 'password'"
        class="toggle-visibility"
        @click="showPassword = !showPassword"
      >
        <span v-if="!showPassword" key="show">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
          </svg>
        </span>
        <span v-else key="hide">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
          </svg>
        </span>
      </div>

      <!-- Slot for icons -->
      <div v-if="$slots.leadingIcon" class="leading-icon">
        <slot name="leadingIcon" />
      </div>
      
      <div v-if="$slots.trailingIcon" class="trailing-icon">
        <slot name="trailingIcon" />
      </div>
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
import { ref, computed } from 'vue'
import type { HbInputProps, HbInputEmits } from '~/types/components'

const props = withDefaults(defineProps<HbInputProps>(), {
  modelValue: '',
  id: () => `input-${Math.random().toString(36).substr(2, 9)}`,
  label: '',
  size: 'md',
  appearance: 'white',
  type: 'text',
  placeholder: '',
  required: false,
  disabled: false,
  error: '',
  helperText: '',
  autofocus: false,
  autocomplete: 'off',
  pattern: ''
})

const emit = defineEmits<HbInputEmits>()

// State
const focused = ref(false)
const showPassword = ref(false)
const birthdate = ref({
  day: '',
  month: '',
  year: ''
})

// Computed properties
const computedType = computed(() => {
  if (props.type === 'password') {
    return !showPassword.value ? 'password' : 'text'
  }
  return props.type
})

// Methods
const onFocus = () => {
  emit('focus')
  focused.value = true
}

const onBlur = () => {
  emit('blur')
  focused.value = false
}

const onBlurBirthdate = (inputEl: string) => {
  emit('blur')
  focused.value = false

  if (typeof inputEl === 'string' && birthdate.value[inputEl as keyof typeof birthdate.value]) {
    const el = document.getElementById(`${props.id}-${inputEl}`) as HTMLInputElement
    if (el) {
      const value = parseInt(birthdate.value[inputEl as keyof typeof birthdate.value] as string)
      const maxValue = parseInt(el.max)
      const minValue = parseInt(el.min)

      if (value >= maxValue) {
        birthdate.value[inputEl as keyof typeof birthdate.value] = String(maxValue)
      } else if (value <= minValue) {
        birthdate.value[inputEl as keyof typeof birthdate.value] = String(minValue)
      }
    }
  }
}

const focusNextInput = (current: string) => {
  if (current === 'day') {
    document.getElementById(`${props.id}-month`)?.focus()
  } else if (current === 'month') {
    document.getElementById(`${props.id}-year`)?.focus()
  }
}
</script>

<style lang="scss" scoped>
.hb-fieldset {
  position: relative;
  font-weight: normal;
  font-size: 14px;

  /* All inputs now have gray-100 background by default */

  .input-wrapper {
    position: relative;
  }
  
  /* Size variants */
  &.size-sm {
    label {
      font-size: var(--text-xs);
      padding-bottom: var(--spacing-1);
    }
    
    input, textarea {
      height: calc(var(--input-height) * 0.6) !important;
      font-size: var(--text-xs);
      padding: 0 var(--spacing-3);
      min-height: calc(var(--input-height) * 0.8);
    }
    
    .leading-icon, .trailing-icon {
      transform: scale(0.85) translateY(-50%);
      top: 45%;
    }
  }
  
  &.size-md {
    input, textarea {
      height: var(--input-height);
      min-height: var(--input-height);
    }
  }
  
  &.size-lg {
    label {
      font-size: var(--text-sm);
      padding-bottom: var(--spacing-2);
    }
    
    input, textarea {
      height: calc(var(--input-height) * 1.2);
      min-height: calc(var(--input-height) * 1.2);
      font-size: var(--text-base);
      padding: 0 var(--spacing-5);
    }
    
    .leading-icon, .trailing-icon {
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

  input[type=text],
  input[type=password],
  input[type=email],
  input[type=search],
  input[type=number],
  input[type=url],
  input[type=tel],
  textarea {
    display: block;
    width: 100%;
    padding: 0 var(--spacing-4);
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
    
    &:disabled {
      cursor: not-allowed;
      color: var(--gray-400);
    }
  }

  input[type=search] {
    padding-right: 2rem;
  }

  input:focus,
  textarea:focus {
    outline: none;
    border: 1px solid var(--primary-500) !important;
    box-shadow: none;
  }

  ::placeholder {
    color: var(--gray-400);
    font-size: var(--text-sm);
    font-weight: 400 !important;
   
  }

  ::-webkit-search-cancel-button {
    display: none;
  }
  
  /* Override browser autofill styles */
  input:-webkit-autofill,
  input:-webkit-autofill:hover, 
  input:-webkit-autofill:focus,
  input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 30px var(--gray-100) inset !important;
    transition: background-color 5000s ease-in-out 0s;
    background-color: var(--gray-100) !important;
  }
  
  /* Firefox autofill */
  input:autofill {
    background-color: var(--gray-100) !important;
  }

  textarea {
    resize: vertical;
    padding: var(--spacing-4);
    min-height: 150px;
    line-height: var(--leading-normal);
  }

  .toggle-visibility {
    position: absolute;
    right: 0;
    bottom: 0;
    height: var(--input-height);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 var(--spacing-4);
    cursor: pointer;
    color: var(--gray-500);

    &:hover {
      color: var(--primary-500);
    }
  }

  .leading-icon,
  .trailing-icon {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    color: var(--gray-500);
  }

  .leading-icon {
    left: var(--spacing-3);
  }

  .trailing-icon {
    right: var(--spacing-3);
  }

  .birthdate {
    display: flex;
    gap: var(--spacing-2);

    > *:nth-child(1),
    > *:nth-child(2) {
      flex: 0 0 90px;
    }

    > *:nth-child(3) {
      flex: 1;
    }
  }

  .error-msg {
    font-size: var(--text-sm);
    color: var(--danger-500);
    margin-top: var(--spacing-1);
  }

  &.url {
    input {
      padding-left: 90px;
    }

    .protocol {
      pointer-events: none;
      position: absolute;
      top: 1px;
      left: 1px;
      bottom: 1px;
      display: flex;
      align-items: center;
      padding: 0 var(--spacing-2) 0 var(--spacing-4);
      color: var(--gray-500);
      background-color: rgba(0,0,0,.05);
      border-radius: var(--radius-lg) 0 0 var(--radius-lg);
      border: 1px solid var(--white);
    }
  }

  legend {
    margin-top: var(--spacing-2);
    font-size: var(--text-xs);
    color: var(--gray-500);
  }

  &.focused {
    input, textarea {
      border-color: var(--primary-500) !important;
      border: 1px solid var(--primary-500) !important;
    }
  }

  &.fieldset-error {
    input, textarea {
      border-color: var(--danger-400);
    }

    ::placeholder {
      color: var(--danger-300);
    }
  }
  
  /* Appearance variants */
  &.appearance-white {
    input, textarea {
      background-color: var(--white) !important;
      border-color: var(--gray-200);
      color: var(--gray-800) !important;
    }
  }
  
  &.appearance-light {
    input, textarea {
      background-color: var(--gray-100) !important;
      border-color: var(--gray-100);
      color: var(--gray-800) !important;
    }
  }
  
  &.appearance-gray {
    input, textarea {
      background-color: var(--gray-100) !important;
      border-color: var(--gray-300);
      color: var(--gray-900) !important;
    }
    
    label {
      color: var(--gray-600) !important;
    }
  }
  
  &.appearance-dark {
    input, textarea {
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
</style>
