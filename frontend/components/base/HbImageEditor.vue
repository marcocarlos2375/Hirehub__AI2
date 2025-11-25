<template>
  <div class="hb-image-editor">
    <div class="hb-image-editor__container">
      <!-- Main cropper component -->
      <Cropper
        ref="cropperRef"
        class="hb-image-editor__cropper"
        :src="imageUrl"
        :stencil-props="{
          aspectRatio: aspectRatio
        }"
        :default-size="defaultSize"
        :default-position="defaultPosition"
        @ready="onReady"
        :min-width="50"
        :min-height="50"
        :image-restriction="imageRestriction"
      />
      
      <!-- Zoom control -->
      <div class="hb-image-editor__controls">
        <div class="hb-image-editor__control-group">
          <div class="hb-image-editor__control-label">{{ $t('Zoom') }}</div>
          <div class="hb-image-editor__zoom-controls">
            <span class="hb-image-editor__zoom-value">{{ zoomValue }}×</span>
            <div class="hb-image-editor__slider-container">
              <input 
                type="range" 
                class="hb-image-editor__slider" 
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
        <div class="hb-image-editor__control-group">
          <div class="hb-image-editor__control-label">{{ $t('Ausrichten') }}</div>
          <div class="hb-image-editor__rotation-controls">
            <button 
              class="hb-image-editor__rotation-button" 
              @click="rotate(-90)"
              aria-label="Rotate left 90 degrees"
            >
              <i class="ri-anticlockwise-line"></i>
              <span>-90°</span>
            </button>
            
            <div class="hb-image-editor__rotation-slider">
              <div 
                v-for="angle in rotationAngles" 
                :key="angle" 
                class="hb-image-editor__rotation-tick"
                :class="{ 'active': Math.abs(currentRotation - angle) < 5 }"
                @click="setRotation(angle)"
              >
                <div class="hb-image-editor__rotation-tick-line"></div>
                <div class="hb-image-editor__rotation-tick-label">{{ angle }}°</div>
              </div>
            </div>
            
            <button 
              class="hb-image-editor__rotation-button" 
              @click="rotate(90)"
              aria-label="Rotate right 90 degrees"
            >
              <i class="ri-clockwise-line"></i>
              <span>+90°</span>
            </button>
          </div>
        </div>
        
        <!-- Tab controls -->
        <div class="hb-image-editor__tabs">
          <button 
            class="hb-image-editor__tab-button"
            :class="{ 'active': activeTab === 'crop' }"
            @click="activeTab = 'crop'"
          >
            {{ $t('Zuschneiden & Drehen') }}
          </button>
          <button 
            class="hb-image-editor__tab-button"
            :class="{ 'active': activeTab === 'background' }"
            @click="activeTab = 'background'"
          >
            {{ $t('Hintergrund') }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Footer with action buttons -->
    <div class="hb-image-editor__footer">
      <HbButton 
        variant="ghost" 
        size="sm"
        @click="onCancel"
      >
        <template #leading-icon>
          <i class="ri-upload-line"></i>
        </template>
        {{ $t('Neu hochladen') }}
      </HbButton>
      
      <HbButton 
        variant="primary" 
        size="sm"
        @click="onSave"
      >
        {{ $t('Änderungen speichern') }}
      </HbButton>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, onMounted, watch } from 'vue';
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';
import HbButton from './HbButton.vue';

type ImageRestriction = 'stencil' | 'fit-area' | 'fill-area' | 'none';

interface Props {
  imageUrl: string
  aspectRatio?: number
  roundedResult?: boolean
  imageRestriction?: ImageRestriction
}

const props = withDefaults(defineProps<Props>(), {
  aspectRatio: 1,
  roundedResult: true,
  imageRestriction: 'stencil'
});

interface SavePayload {
  blob: Blob
  url: string
}

interface Emits {
  (e: 'save', payload: SavePayload): void
  (e: 'cancel'): void
  (e: 'update:imageUrl', url: string): void
}

const emit = defineEmits<Emits>();

const cropperRef = ref<InstanceType<typeof Cropper> | null>(null);
const zoomValue = ref<number>(1);
const currentRotation = ref<number>(0);
const activeTab = ref<'crop' | 'background'>('crop');
const isReady = ref<boolean>(false);
const defaultSize = ref<{ width: string; height: string }>({ width: '80%', height: '80%' });
const defaultPosition = ref<{ left: string; top: string }>({ left: '50%', top: '50%' });

// Rotation angle options
const rotationAngles: number[] = [-30, -15, 0, 15, 30];

// Handle zoom change
const onZoomChange = (): void => {
  if (cropperRef.value && isReady.value) {
    const cropper = cropperRef.value.getResult();
    const zoom = parseFloat(String(zoomValue.value));

    cropperRef.value.zoom(zoom);
  }
};

// Handle rotation
const rotate = (angle: number): void => {
  if (cropperRef.value && isReady.value) {
    currentRotation.value = (currentRotation.value + angle) % 360;
    cropperRef.value.rotate(angle);
  }
};

// Set specific rotation
const setRotation = (angle: number): void => {
  if (cropperRef.value && isReady.value) {
    const diff = angle - currentRotation.value;
    currentRotation.value = angle;
    cropperRef.value.rotate(diff);
  }
};

// Cropper ready event
const onReady = (): void => {
  isReady.value = true;
};

// Save the cropped image
const onSave = (): void => {
  if (cropperRef.value) {
    const { canvas } = cropperRef.value.getResult();

    if (canvas) {
      // Convert to blob with desired format and quality
      canvas.toBlob((blob) => {
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        emit('save', { blob, url });
        emit('update:imageUrl', url);
      }, 'image/jpeg', 0.9);
    }
  }
};

// Cancel editing
const onCancel = (): void => {
  emit('cancel');
};

// Reset editor when image changes
watch(() => props.imageUrl, () => {
  zoomValue.value = 1;
  currentRotation.value = 0;

  // Reset cropper when it's ready
  if (isReady.value && cropperRef.value) {
    cropperRef.value.reset();
  }
}, { immediate: true });
</script>

<style lang="scss" scoped>
.hb-image-editor {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background-color: #141824;
  color: #fff;
  
  &__container {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    padding: 1rem;
  }
  
  &__cropper {
    flex: 1;
    min-height: 0;
    margin-bottom: 1.5rem;
    
    :deep(.vue-advanced-cropper__image) {
      max-height: 70vh;
    }
    
    :deep(.vue-advanced-cropper__stretcher) {
      max-height: 70vh;
    }
    
    :deep(.vue-advanced-cropper__stencil-grid) {
      border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    :deep(.vue-advanced-cropper__stencil-handler) {
      background-color: var(--primary-500);
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
    margin-top: 1rem;
  }
  
  &__control-group {
    margin-bottom: 1.5rem;
  }
  
  &__control-label {
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
    color: #9ca3af;
  }
  
  &__zoom-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  &__zoom-value {
    min-width: 2rem;
    font-size: 0.875rem;
    font-weight: 500;
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
    gap: 1rem;
  }
  
  &__rotation-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: none;
    border: none;
    color: #fff;
    font-size: 0.75rem;
    cursor: pointer;
    padding: 0.5rem;
    
    i {
      font-size: 1.25rem;
      margin-bottom: 0.25rem;
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
      .hb-image-editor__rotation-tick-line {
        background-color: var(--primary-500);
        height: 12px;
      }
      
      .hb-image-editor__rotation-tick-label {
        color: var(--primary-500);
      }
    }
  }
  
  &__rotation-tick-line {
    width: 2px;
    height: 8px;
    background-color: rgba(255, 255, 255, 0.5);
    margin-bottom: 4px;
    transition: all 0.2s ease;
  }
  
  &__rotation-tick-label {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.7);
    transition: all 0.2s ease;
  }
  
  &__tabs {
    display: flex;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-top: 1rem;
  }
  
  &__tab-button {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.875rem;
    padding: 0.75rem 1rem;
    cursor: pointer;
    position: relative;
    transition: all 0.2s ease;
    
    &.active {
      color: #fff;
      
      &::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
      }
    }
    
    &:hover:not(.active) {
      color: #fff;
    }
  }
  
  &__footer {
    display: flex;
    justify-content: space-between;
    padding: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
}
</style>
