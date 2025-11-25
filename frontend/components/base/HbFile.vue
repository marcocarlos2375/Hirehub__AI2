<template>
  <div class="hb-file" :class="{ 'has-error': error, 'is-disabled': disabled }">
    <div v-if="label" class="hb-file__label">
      {{ label }}<span v-if="required" class="required">*</span>
    </div>
    
    <div v-if="helperText && !error" class="hb-file__helper hb-file__helper--top">{{ helperText }}</div>
    
    <div 
      class="hb-file__dropzone"
      :class="{ 'hb-file__dropzone--dragging': isDragging, 'hb-file__dropzone--has-file': hasFile }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="!disabled && $refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        :multiple="multiple"
        :disabled="disabled"
        class="hb-file__input"
        @change="onFileChange"
      />
      
      <div v-if="!hasFile" class="hb-file__placeholder">
        <div class="hb-file__icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="12" y1="18" x2="12" y2="12"></line>
            <line x1="9" y1="15" x2="15" y2="15"></line>
          </svg>
        </div>
        <div class="hb-file__text">
          <span class="hb-file__primary-text">{{ dragText }}</span>
          <span class="hb-file__secondary-text">{{ browseText }}</span>
        </div>
      </div>
      
      <div v-else class="hb-file__file-info">
        <div class="hb-file__file-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
        </div>
        <div class="hb-file__file-details">
          <div class="hb-file__file-name">{{ fileName }}</div>
          <div class="hb-file__file-size">{{ fileSize }}</div>
        </div>
        <button 
          v-if="!disabled" 
          class="hb-file__remove-btn"
          @click.stop="removeFile"
          type="button"
          aria-label="Remove file"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
    
    <div v-if="error" class="hb-file__error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed } from 'vue';

interface Props {
  modelValue?: File | File[] | null
  label?: string
  required?: boolean
  disabled?: boolean
  accept?: string
  multiple?: boolean
  dragText?: string
  browseText?: string
  error?: string
  helperText?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  label: '',
  required: false,
  disabled: false,
  accept: '.pdf,.doc,.docx,.txt',
  multiple: false,
  dragText: 'Drag and drop your file here',
  browseText: 'or click to browse',
  error: '',
  helperText: ''
});

interface Emits {
  (e: 'update:modelValue', value: File | File[] | null): void
}

const emit = defineEmits<Emits>();

// Type the component refs
declare const $refs: {
  fileInput: HTMLInputElement
};

const fileInput = ref<HTMLInputElement | null>(null);
const isDragging = ref<boolean>(false);

const hasFile = computed<boolean>(() => {
  return props.modelValue !== null;
});

const fileName = computed<string>(() => {
  if (!props.modelValue) return '';
  return (props.modelValue as File).name;
});

const fileSize = computed<string>(() => {
  if (!props.modelValue) return '';

  const bytes = (props.modelValue as File).size;
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
});

function onDragOver(event: DragEvent): void {
  if (props.disabled) return;
  isDragging.value = true;
}

function onDragLeave(): void {
  isDragging.value = false;
}

function onDrop(event: DragEvent): void {
  if (props.disabled) return;
  isDragging.value = false;

  const files = event.dataTransfer?.files;
  if (files && files.length > 0) {
    handleFiles(files);
  }
}

function onFileChange(event: Event): void {
  if (props.disabled) return;

  const files = (event.target as HTMLInputElement).files;
  if (files && files.length > 0) {
    handleFiles(files);
  }
}

function handleFiles(files: FileList): void {
  if (props.multiple) {
    emit('update:modelValue', Array.from(files));
  } else {
    emit('update:modelValue', files[0]);
  }

  // Reset the input to allow selecting the same file again
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

function removeFile(event: MouseEvent): void {
  event.stopPropagation();
  emit('update:modelValue', null);
}
</script>

<style lang="scss" scoped>
.hb-file {
  width: 100%;
  margin-bottom: var(--spacing-4);
  
  &__label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: var(--font-medium);
    font-size: var(--text-sm);
    margin-bottom: var(--spacing-2);
    
    .required {
      color: var(--danger-500);
      margin-left: var(--spacing-0-5);
    }
  }
  
  &__helper {
    margin-top: var(--spacing-1);
    font-size: var(--text-xs);
    color: var(--gray-500);
    
    &--top {
      margin-top: var(--spacing-1);
      margin-bottom: var(--spacing-2);
    }
  }
  
  &__dropzone {
    border: 2px dashed var(--gray-300);
    border-radius: var(--radius-md);
    padding: var(--spacing-6);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: var(--gray-50);
    cursor: pointer;
    transition: all var(--transition-normal) var(--transition-ease);
    
    &:hover {
      border-color: var(--primary-400);
      background-color: var(--primary-50);
    }
    
    &--dragging {
      border-color: var(--primary-500);
      background-color: var(--primary-50);
    }
    
    &--has-file {
      border-style: solid;
      border-color: var(--primary-200);
      background-color: var(--primary-50);
    }
  }
  
  &__input {
    display: none;
  }
  
  &__placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  &__icon {
    color: var(--primary-500);
    margin-bottom: var(--spacing-3);
  }
  
  &__text {
    display: flex;
    flex-direction: column;
  }
  
  &__primary-text {
    font-weight: var(--font-medium);
    color: var(--gray-700);
    margin-bottom: var(--spacing-1);
  }
  
  &__secondary-text {
    color: var(--primary-500);
    font-size: var(--text-sm);
  }
  
  &__file-info {
    display: flex;
    align-items: center;
    width: 100%;
    padding: var(--spacing-2);
  }
  
  &__file-icon {
    color: var(--primary-500);
    margin-right: var(--spacing-3);
    flex-shrink: 0;
  }
  
  &__file-details {
    flex: 1;
    min-width: 0;
  }
  
  &__file-name {
    font-weight: var(--font-medium);
    color: var(--gray-700);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  &__file-size {
    font-size: var(--text-sm);
    color: var(--gray-500);
  }
  
  &__remove-btn {
    background: none;
    border: none;
    color: var(--gray-500);
    cursor: pointer;
    padding: var(--spacing-1);
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: var(--spacing-2);
    transition: all var(--transition-fast) var(--transition-ease);
    
    &:hover {
      color: var(--danger-500);
      background-color: var(--danger-50);
    }
  }
  
  &__error {
    margin-top: var(--spacing-2);
    font-size: var(--text-xs);
    color: var(--danger-500);
  }
  
  &.has-error {
    .hb-file__dropzone {
      border-color: var(--danger-400);
      background-color: var(--danger-50);
    }
  }
  
  &.is-disabled {
    opacity: 0.6;
    
    .hb-file__dropzone {
      cursor: not-allowed;
      background-color: var(--gray-100);
      border-color: var(--gray-300);
      
      &:hover {
        border-color: var(--gray-300);
        background-color: var(--gray-100);
      }
    }
  }
}
</style>
