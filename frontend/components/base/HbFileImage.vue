<template>
  <div class="hb-file-image" :class="{ 'has-error': error, 'is-disabled': disabled }">
    <div v-if="helperText && !error && !editMode" class="hb-file-image__helper">{{ helperText }}</div>
    
    <!-- Image Editor Mode -->
    <div v-if="editMode && hasPreview" class="hb-file-image__editor-container">
      <div class="hb-file-image__editor">
        <Cropper
          ref="cropperRef"
          class="hb-file-image__cropper"
          :src="previewUrl"
          :stencil-props="{
            aspectRatio: aspectRatio
          }"
          :default-size="defaultSize"
          :default-position="defaultPosition"
          @ready="onCropperReady"
          :min-width="50"
          :min-height="50"
          :image-restriction="imageRestriction"
        />
      </div>
      
      <!-- Zoom control -->
      <div class="hb-file-image__controls">
        <div class="hb-file-image__control-group">
          <div class="hb-file-image__control-label">Zoom</div>
          <div class="hb-file-image__zoom-controls">
            <span class="hb-file-image__zoom-value">{{ zoomValue }}×</span>
            <div class="hb-file-image__slider-container">
              <input 
                type="range" 
                class="hb-file-image__slider" 
                min="1" 
                max="3" 
                step="0.1" 
                v-model="zoomValue" 
                @input="onZoomChange"
              />
            </div>
          </div>
        </div>
        
        <!-- Rotation control -->
        <div class="hb-file-image__control-group">
          <div class="hb-file-image__control-label">Rotate</div>
          <div class="hb-file-image__rotation-controls">
            <button 
              class="hb-file-image__rotation-button" 
              @click="rotate(-90)"
              aria-label="Rotate left 90 degrees"
            >
              <i class="ri-anticlockwise-line"></i>
              <span>-90°</span>
            </button>
            
            <div class="hb-file-image__rotation-slider">
              <div 
                v-for="angle in rotationAngles" 
                :key="angle" 
                class="hb-file-image__rotation-tick"
                :class="{ 'active': Math.abs(currentRotation - angle) < 5 }"
                @click="setRotation(angle)"
              >
                <div class="hb-file-image__rotation-tick-line"></div>
                <div class="hb-file-image__rotation-tick-label">{{ angle }}°</div>
              </div>
            </div>
            
            <button 
              class="hb-file-image__rotation-button" 
              @click="rotate(90)"
              aria-label="Rotate right 90 degrees"
            >
              <i class="ri-clockwise-line"></i>
              <span>+90°</span>
            </button>
          </div>
        </div>
      </div>
      
      <div class="hb-file-image__editor-actions">
        <HbButton 
          variant="ghost" 
          size="sm"
          @click="cancelEdit"
        >
          Cancel
        </HbButton>
        <HbButton 
          variant="primary" 
          size="sm"
          @click="applyEdit"
        >
          Apply
        </HbButton>
      </div>
    </div>
    
    <!-- Preview image if available and not in edit mode -->
    <div v-else-if="hasPreview" class="hb-file-image__preview">
      <img :src="previewUrl" alt="Preview" class="hb-file-image__preview-img" />
      <div class="hb-file-image__preview-actions">
        <button 
          v-if="!disabled" 
          class="hb-file-image__edit-btn"
          @click.stop="startEdit"
          type="button"
          aria-label="Edit image"
        >
          <i class="ri-edit-2-line"></i>
        </button>
        <button 
          v-if="!disabled" 
          class="hb-file-image__remove-btn"
          @click.stop="removeFile"
          type="button"
          aria-label="Remove image"
        >
          <i class="ri-delete-bin-line"></i>
        </button>
      </div>
    </div>
    
    <!-- Upload area if no preview -->
    <div 
      v-else
      class="hb-file-image__dropzone"
      :class="{ 'hb-file-image__dropzone--dragging': isDragging }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="!disabled && fileInput?.click()"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        :disabled="disabled"
        class="hb-file-image__input"
        @change="onFileChange"
      />
      
      <div class="hb-file-image__placeholder">
        <div class="hb-file-image__icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
        </div>
        <div class="hb-file-image__text">
          <span class="hb-file-image__primary-text">{{ dragText }}</span>
          <span class="hb-file-image__secondary-text">{{ browseText }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="error" class="hb-file-image__error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, watch } from 'vue';
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';
import HbButton from './HbButton.vue';

interface Props {
  modelValue?: File | string | null
  previewUrl?: string
  label?: string
  required?: boolean
  disabled?: boolean
  accept?: string
  maxSize?: number
  dragText?: string
  browseText?: string
  error?: string
  helperText?: string
  aspectRatio?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  previewUrl: '',
  label: '',
  required: false,
  disabled: false,
  accept: 'image/*',
  maxSize: 5 * 1024 * 1024, // 5MB default
  dragText: 'Drag and drop your image here',
  browseText: 'or click to browse',
  error: '',
  helperText: '',
  aspectRatio: 1
});

interface Emits {
  (e: 'update:modelValue', value: File | null): void
  (e: 'error', message: string): void
  (e: 'remove'): void
  (e: 'edit', editing: boolean): void
}

const emit = defineEmits<Emits>();

const fileInput = ref<HTMLInputElement | null>(null);
const cropperRef = ref<InstanceType<typeof Cropper> | null>(null);
const isDragging = ref<boolean>(false);
const internalError = ref<string>('');
const editMode = ref<boolean>(false);
const zoomValue = ref<number>(1);
const currentRotation = ref<number>(0);
const isReady = ref<boolean>(false);
const defaultSize = ref<{ width: string; height: string }>({ width: '80%', height: '80%' });
const defaultPosition = ref<{ left: string; top: string }>({ left: '50%', top: '50%' });
const imageRestriction = ref<'stencil' | 'fit-area' | 'fill-area' | 'none'>('stencil');

// Rotation angle options
const rotationAngles: number[] = [-30, -15, 0, 15, 30];

// Combine external and internal errors
const errorMessage = computed<string>(() => props.error || internalError.value);

// Generate preview URL from File object if needed
const previewFromFile = ref<string>('');

// Check if we have a preview to show
const hasPreview = computed<boolean>(() => {
  return !!props.previewUrl || (props.modelValue instanceof File && !!previewFromFile.value);
});

// Watch for file changes to generate preview
watch(() => props.modelValue, (newFile) => {
  if (newFile instanceof File) {
    const reader = new FileReader();
    reader.onload = (e: ProgressEvent<FileReader>) => {
      previewFromFile.value = e.target?.result as string;
    };
    reader.readAsDataURL(newFile);
  } else {
    previewFromFile.value = '';
  }
}, { immediate: true });

// Display preview URL - either from prop or from file
const previewUrl = computed<string>(() => {
  return props.previewUrl || previewFromFile.value;
});

function onDragOver(event: DragEvent): void {
  isDragging.value = true;
}

function onDragLeave(): void {
  isDragging.value = false;
}

function onDrop(event: DragEvent): void {
  isDragging.value = false;

  const files = event.dataTransfer?.files;
  if (files && files.length > 0) {
    validateAndProcessFile(files[0]);
  }
}

function onFileChange(event: Event): void {
  if (props.disabled) return;

  const files = (event.target as HTMLInputElement).files;
  if (files && files.length > 0) {
    validateAndProcessFile(files[0]);
  }
}

function validateAndProcessFile(file: File): void {
  internalError.value = '';

  // Check if it's an image
  if (!file.type.startsWith('image/')) {
    internalError.value = 'Please select a valid image file';
    emit('error', internalError.value);
    return;
  }

  // Check file size
  if (file.size > props.maxSize) {
    const maxSizeMB = props.maxSize / (1024 * 1024);
    internalError.value = `Image size exceeds ${maxSizeMB}MB limit`;
    emit('error', internalError.value);
    return;
  }

  // Valid file, update model
  emit('update:modelValue', file);

  // Reset the input to allow selecting the same file again
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

function removeFile(event: MouseEvent): void {
  event.stopPropagation();
  emit('update:modelValue', null);
  emit('remove');
  previewFromFile.value = '';
  editMode.value = false;

  // Reset the input
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

// Image Editor Functions
function startEdit(): void {
  editMode.value = true;
  emit('edit', true);
}

function cancelEdit(): void {
  editMode.value = false;
  // Reset zoom and rotation
  zoomValue.value = 1;
  currentRotation.value = 0;
  emit('edit', false);
}

function onCropperReady(): void {
  isReady.value = true;
}

// Handle zoom change
function onZoomChange(): void {
  if (cropperRef.value && isReady.value) {
    const zoom = parseFloat(String(zoomValue.value));
    cropperRef.value.zoom(zoom);
  }
}

// Handle rotation
function rotate(angle: number): void {
  if (cropperRef.value && isReady.value) {
    currentRotation.value = (currentRotation.value + angle) % 360;
    cropperRef.value.rotate(angle);
  }
}

// Set specific rotation
function setRotation(angle: number): void {
  if (cropperRef.value && isReady.value) {
    const diff = angle - currentRotation.value;
    currentRotation.value = angle;
    cropperRef.value.rotate(diff);
  }
}

// Apply the edits
function applyEdit(): void {
  if (cropperRef.value && isReady.value) {
    const { canvas } = cropperRef.value.getResult();

    if (canvas) {
      // Convert to blob with desired format and quality
      canvas.toBlob((blob) => {
        if (!blob) return;
        const fileName = props.modelValue instanceof File ? props.modelValue.name : 'edited-image.jpg';
        const editedFile = new File([blob], fileName, { type: 'image/jpeg' });

        // Update the model value with the edited file
        emit('update:modelValue', editedFile);

        // Exit edit mode
        editMode.value = false;
        emit('edit', false);
      }, 'image/jpeg', 0.9);
    }
  }
}
</script>

<style lang="scss" scoped>
.hb-file-image {
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
    margin-bottom: var(--spacing-2);
    font-size: var(--text-xs);
    color: var(--gray-500);
  }
  
  &__dropzone {
    border: 1px dashed var(--primary-500);
    border-radius: var(--radius-md);
    padding: var(--spacing-6);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: transparent;
    cursor: pointer;
    transition: all var(--transition-normal) var(--transition-ease);
    
    &:hover {
      border-color: var(--primary-400);
      background-color: transparent;
    }
    
    &--dragging {
      border-color: var(--primary-500);
      background-color: transparent;
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
    
    svg {
      background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }
  
  &__text {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  &__primary-text {
    font-weight: var(--font-medium);
    color: var(--gray-400);
    font-family: var(--font-gabarito);
    margin-bottom: var(--spacing-1);
  }
  
  &__secondary-text {
    color: var(--primary-500);
    font-size: var(--text-sm);
  }
  
  &__preview {
    position: relative;
    display: flex;
    justify-content: center;
    margin-bottom: var(--spacing-2);
    border-radius: var(--radius-md);
    overflow: hidden;
  }
  
  &__preview-img {
    max-width: 100%;
    max-height: 300px;
    object-fit: contain;
  }
  
  &__preview-actions {
    position: absolute;
    top: var(--spacing-2);
    right: var(--spacing-2);
    display: flex;
    gap: var(--spacing-2);
  }
  
  &__edit-btn,
  &__remove-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: white;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-fast) var(--transition-ease);
    
    i {
      font-size: 16px;
    }
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
  }
  
  &__edit-btn {
    color: var(--primary-500);
    
    &:hover {
      background-color: var(--primary-50);
    }
    
    i {
      background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }
  
  &__remove-btn {
    color: var(--danger-500);
    
    &:hover {
      background-color: var(--danger-50);
    }
  }
  
  &__error {
    margin-top: var(--spacing-2);
    font-size: var(--text-xs);
    color: var(--danger-500);
  }
  
  /* Image Editor Styles */
  &__editor-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    background-color: var(--gray-900);
    color: white;
    border-radius: var(--radius-md);
    overflow: hidden;
  }
  
  &__editor {
    position: relative;
    height: 400px;
    width: 100%;
    background-color: var(--gray-900);
  }
  
  &__cropper {
    width: 100%;
    height: 100%;
    
    :deep(.vue-advanced-cropper__image) {
      max-height: 400px;
    }
    
    :deep(.vue-advanced-cropper__stretcher) {
      max-height: 400px;
    }
    
    :deep(.vue-advanced-cropper__stencil-grid) {
      border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    :deep(.vue-advanced-cropper__stencil-handler) {
      background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
      width: 10px;
      height: 10px;
    }
    
    :deep(.vue-advanced-cropper__stencil-handler--west-north),
    :deep(.vue-advanced-cropper__stencil-handler--east-north),
    :deep(.vue-advanced-cropper__stencil-handler--west-south),
    :deep(.vue-advanced-cropper__stencil-handler--east-south) {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
    
    :deep(.vue-advanced-cropper__stencil-handler--west),
    :deep(.vue-advanced-cropper__stencil-handler--east) {
      height: 20px;
      width: 10px;
      border-radius: 10px;
    }
    
    :deep(.vue-advanced-cropper__stencil-handler--north),
    :deep(.vue-advanced-cropper__stencil-handler--south) {
      width: 20px;
      height: 10px;
      border-radius: 10px;
    }
    
    :deep(.vue-advanced-cropper__stencil-grid-line) {
      background-color: rgba(255, 255, 255, 0.3);
    }
  }
  
  &__controls {
    padding: var(--spacing-4);
    background-color: var(--gray-800);
  }
  
  &__control-group {
    margin-bottom: var(--spacing-4);
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  &__control-label {
    font-size: var(--text-sm);
    margin-bottom: var(--spacing-2);
    color: var(--gray-300);
  }
  
  &__zoom-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-4);
  }
  
  &__zoom-value {
    min-width: 2rem;
    font-size: var(--text-sm);
    font-weight: 500;
    color: white;
  }
  
  &__slider-container {
    flex: 1;
  }
  
  &__slider {
    width: 100%;
    height: 4px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
    appearance: none;
    outline: none;
    
    &::-webkit-slider-thumb {
      appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
      cursor: pointer;
    }
    
    &::-moz-range-thumb {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
      border: none;
      cursor: pointer;
    }
  }
  
  &__rotation-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-4);
  }
  
  &__rotation-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: none;
    border: none;
    color: white;
    font-size: var(--text-xs);
    cursor: pointer;
    padding: var(--spacing-2);
    
    i {
      font-size: var(--text-xl);
      margin-bottom: var(--spacing-1);
      background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    &:hover {
      color: var(--primary-300);
    }
  }
  
  &__rotation-slider {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 40px;
    position: relative;
    
    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 0;
      right: 0;
      height: 2px;
      background-color: rgba(255, 255, 255, 0.2);
      transform: translateY(-50%);
    }
  }
  
  &__rotation-tick {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    z-index: 1;
    
    &.active {
      .hb-file-image__rotation-tick-line {
        background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
        height: 12px;
      }
      
      .hb-file-image__rotation-tick-label {
        background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }
    }
  }
  
  &__rotation-tick-line {
    width: 2px;
    height: 8px;
    background-color: rgba(255, 255, 255, 0.5);
    margin-bottom: var(--spacing-1);
    transition: all 0.2s ease;
  }
  
  &__rotation-tick-label {
    font-size: var(--text-xs);
    color: rgba(255, 255, 255, 0.7);
    transition: all 0.2s ease;
  }
  
  &__editor-actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-2);
    padding: var(--spacing-3);
    background-color: var(--gray-800);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  &.has-error {
    .hb-file-image__dropzone {
      border-color: var(--danger-400);
      background-color: transparent;
    }
  }
  
  &.is-disabled {
    opacity: 0.6;
    
    .hb-file-image__dropzone {
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
