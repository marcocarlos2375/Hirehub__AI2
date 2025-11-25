<template>
  <div class="hb-avatar-wrapper">
    <div class="hb-avatar-container" :class="{ 'with-actions': editable }">
      <div 
        class="hb-avatar" 
      :class="[
        `hb-avatar--${size}`, 
        `hb-avatar--rounded-${rounded}`,
        { 'hb-avatar--loading': loading },
        { 'hb-avatar--with-status': status },
        { 'hb-avatar--with-badge': badge },
        { 'hb-avatar--square': square },
        { 'hb-avatar--clickable': clickable || editable },
        { 'hb-avatar--editable': editable }
      ]"
      @click="handleClick"
    >
    <!-- Image Avatar -->
    <div v-if="src && !loading && !error" class="hb-avatar__image-container">
      <img 
        :src="avatarSrc" 
        :alt="alt" 
        class="hb-avatar__image" 
        @error="onImageError"
      />
    </div>
    
    <!-- Default Image Avatar (when defaultImage is provided) -->
    <div v-else-if="defaultImage && !loading && !error" class="hb-avatar__image-container">
      <img 
        :src="defaultAvatarUrl" 
        :alt="alt" 
        class="hb-avatar__image" 
        @error="onImageError"
      />
    </div>
    
    <!-- Initials Avatar (fallback when no image, no default image, or error) -->
    <div v-else-if="!loading && initials" class="hb-avatar__initials" :style="{ backgroundColor: bgColor }">
      {{ initials }}
    </div>
    
    <!-- Icon Avatar (fallback when no image, no default image, no initials, or error) -->
    <div v-else-if="!loading" class="hb-avatar__icon" :style="{ backgroundColor: bgColor }">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="hb-avatar__loading">
      <HbSpinner :size="spinnerSize" color="primary" />
    </div>
    
    <!-- Status Indicator -->
    <div 
      v-if="status && !loading" 
      class="hb-avatar__status" 
      :class="`hb-avatar__status--${status}`"
    ></div>
    
    <!-- Badge -->
    <div 
      v-if="badge && !loading" 
      class="hb-avatar__badge"
    >
      {{ typeof badge === 'boolean' ? '' : badge }}
    </div>
    
    <!-- Edit Overlay -->
    <div v-if="editable && !loading" class="hb-avatar__edit-overlay">
      <i class="ri-pencil-line"></i>
    </div>
  </div>
    
    <!-- Avatar Actions when editable -->
    <div v-if="editable" class="hb-avatar-actions">
      <HbButton
        variant="outline"
        size="sm"
        @click="openUploadModal"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        {{ src ? 'Upload Another Photo' : 'Upload Photo' }}
      </HbButton>
      
      <HbButton 
        v-if="src"
        variant="outline" 
        size="sm"
        class="mt-2"
        @click="confirmDelete"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
        {{ src ? 'Delete Photo' : 'Remove Photo' }}
      </HbButton>
    </div>
    </div>
  
    <!-- Change picture modal -->
  <HbModal 
    v-model="showChangeModal" 
    :title="modalStep === 1 ? 'Upload Profile Picture' : 'Edit Profile Picture'"
    size="lg"
    appearance="dark"
    @close="closeChangeModal"
  >
    <!-- Step 1: Upload -->
    <div v-if="modalStep === 1" class="avatar-upload-step">
      <p class="text-sm text-gray-300 mb-4">
        Upload a new profile picture. Supported formats: JPG, PNG, GIF. Maximum size: 5MB.
      </p>
      
      <!-- Upload dropzone (copied from HbFileImage) -->
      <div
        class="hb-file-image__dropzone"
        :class="{ 'hb-file-image__dropzone--dragging': isDragging }"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          class="hb-file-image__input"
          @change="onFileChange"
        />
        
        <div class="hb-file-image__placeholder">
          <div class="hb-file-image__icon">
            <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="48" height="48" x="0" y="0" viewBox="0 0 64 64" style="enable-background:new 0 0 512 512" xml:space="preserve" fill-rule="evenodd">
              <g>
                <path fill="#ffffff" d="M15.017 22.248C6.501 23.67 0 31.081 0 40c0 9.934 8.066 18 18 18s18-8.066 18-18V29a2 2 0 0 0-4 0v11c0 7.727-6.273 14-14 14S4 47.727 4 40c0-7.443 5.82-13.538 13.154-13.975a2.002 2.002 0 0 0 1.876-2.132C19.01 23.598 19 23.3 19 23c0-7.175 5.825-13 13-13s13 5.825 13 13c0 .339-.013.675-.038 1.007a2.001 2.001 0 0 0 2.306 2.129A11 11 0 0 1 49 26c6.071 0 11 4.929 11 11s-4.929 11-11 11H38a2 2 0 0 0 0 4h11c8.279 0 15-6.721 15-15s-6.721-15-15-15h-.03C48.452 13.082 41.047 6 32 6c-9.13 0-16.589 7.213-16.983 16.248z" opacity="1"/>
                <path fill="#009fdf" d="M32 30.968V40c0 7.727-6.27 14-14 14-1.1 0-2 .896-2 2s.9 2 2 2c9.93 0 18-8.066 18-18v-9.102l3.6 3.53c.79.773 2.06.76 2.83-.028s.76-2.055-.03-2.828l-5.53-5.427c-1.54-1.512-4.04-1.524-5.6-.028-2.06 1.983-5.66 5.441-5.66 5.441a2.002 2.002 0 0 0 2.78 2.884z" opacity="1"/>
              </g>
            </svg>
          </div>
          <div class="hb-file-image__text">
            <span class="hb-file-image__primary-text">Drag and drop your image here</span>
            <span class="hb-file-image__secondary-text">or click to browse</span>
          </div>
        </div>
      </div>
      
      <p v-if="fileError" class="text-sm text-red-600 mt-2">{{ fileError }}</p>
    </div>
    
    <!-- Step 2: Edit with Cropper, Rotate & Filters -->
    <div v-else-if="modalStep === 2 && newAvatarPreview" class="avatar-edit-step">
      <!-- Preview with filter (hidden when in crop tab) -->
      <div v-if="activeTab !== 'crop'" class="avatar-preview-container">
        <img 
          :src="newAvatarPreview" 
          alt="Avatar preview"
          :style="{ 
            filter: currentFilterStyle,
            transform: `scale(${zoomValue}) rotate(${currentRotation}deg)`
          }"
          class="avatar-preview-image"
        />
      </div>
      
      <!-- Tabs -->
      <div class="avatar-tabs">
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'filters' }"
          @click="activeTab = 'filters'"
          type="button"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
          Filters
        </button>
        <button 
          class="tab-btn" 
          :class="{ 'active': activeTab === 'crop' }"
          @click="activeTab = 'crop'"
          type="button"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243 4.243 3 3 0 004.243-4.243zm0-5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z" />
          </svg>
          Crop
        </button>
      </div>
      
      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Filters Tab -->
        <div v-if="activeTab === 'filters'" class="avatar-filters">
        <div class="filter-grid">
          <div
            v-for="filter in filters"
            :key="filter.value"
            class="filter-option"
            :class="{ 'active': selectedFilter === filter.value }"
            @click="selectedFilter = filter.value"
          >
            <div class="filter-preview">
              <img 
                :src="newAvatarPreview" 
                alt="Filter preview"
                :style="{ filter: filter.class }"
              />
            </div>
            <span class="filter-label">{{ filter.label }}</span>
          </div>
        </div>
        </div>
        
        <!-- Crop Tab -->
        <div v-else-if="activeTab === 'crop'" class="crop-tab">
          <!-- Cropper -->
          <div class="cropper-container" @wheel.prevent="handleCropperWheel">
            <Cropper
              ref="cropperRef"
              class="cropper"
              :src="filteredPreview || newAvatarPreview"
              :stencil-props="{
                aspectRatio: 1,
                movable: true,
                resizable: false,
                handlers: {},
                lines: {}
              }"
              :stencil-size="{
                width: 300,
                height: 300
              }"
              :image-restriction="'none'"
            />
          </div>
          
          <!-- Zoom & Rotation Controls for Cropper -->
          <div class="avatar-controls">
            <!-- Zoom Control -->
            <div class="control-group">
              <label class="control-label">Zoom</label>
              <div class="zoom-control">
                <span class="zoom-value">{{ cropZoomValue }}×</span>
                <input 
                  type="range" 
                  class="slider" 
                  min="0.5" 
                  max="3" 
                  step="0.1" 
                  v-model="cropZoomValue"
                  @input="applyCropperZoom"
                />
                <HbButton 
                  variant="dark-ghost" 
                  size="sm"
                  @click="resetCropZoom"
                >
                  <template #leading-icon>
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </template>
                  Reset
                </HbButton>
              </div>
            </div>
            
            <!-- Rotation Control -->
            <div class="control-group">
              <label class="control-label">Rotate</label>
              <div class="rotation-control">
                <button 
                  class="rotation-btn" 
                  @click="rotateCropper(-90)"
                  type="button"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                  </svg>
                </button>
                <span class="rotation-value">{{ currentRotation }}°</span>
                <button 
                  class="rotation-btn" 
                  @click="rotateCropper(90)"
                  type="button"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10H11a8 8 0 00-8 8v2m18-10l-6 6m6-6l-6-6" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Apply Crop Button -->
          <div class="apply-crop-section">
            <HbButton 
              variant="primary" 
              size="md"
              @click="applyCrop"
              class="w-full"
            >
              <template #leading-icon>
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </template>
              Apply Crop
            </HbButton>
          </div>
        </div>
        
      </div>
    </div>
    
    <template #footer>
      <div class="flex justify-end space-x-2">
        <HbButton 
          v-if="modalStep === 2"
          variant="ghost" 
          @click="modalStep = 1"
          size="sm"
        >
          Back
        </HbButton>
        
        <HbButton 
          variant="ghost" 
          @click="closeChangeModal"
          size="sm"
          class="px-4"
        >
          Cancel
        </HbButton>
        
        <HbButton 
          v-if="modalStep === 1"
          variant="primary" 
          @click="goToEditStep"
          class="px-4"
          size="sm"
          :disabled="!newAvatarFile"
        >
          Next
        </HbButton>
        
        <HbButton 
          v-else
          variant="primary" 
          @click="handleFileUpload"
          class="px-4"
          size="sm"
        >
          Save Picture
        </HbButton>
      </div>
    </template>
  </HbModal>
  
  <!-- Delete Confirmation Modal -->
  <HbModal
    v-model="showDeleteModal"
    title="Delete Profile Picture"
    size="sm"
    appearance="dark"
    @close="showDeleteModal = false"
  >
    <p class="text-sm text-gray-300 mb-4">
      Are you sure you want to delete your profile picture? This action cannot be undone.
    </p>
    
    <template #footer>
      <div class="flex justify-end space-x-2">
        <HbButton 
          variant="dark-ghost" 
          @click="showDeleteModal = false"
          size="sm"
        >
          Cancel
        </HbButton>
        
        <HbButton 
          variant="danger" 
          @click="handleDelete"
          size="sm"
        >
          Delete
        </HbButton>
      </div>
    </template>
  </HbModal>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';
import HbSpinner from './HbSpinner.vue';
import HbModal from './HbModal.vue';
import HbButton from './HbButton.vue';

// NOTE: Replace useRuntimeConfig with your environment config
// For Vite: import.meta.env.VITE_API_BASE_URL
// For Vue 3: app.config.globalProperties.$config
// @ts-expect-error - useRuntimeConfig is auto-imported in Nuxt
const config = useRuntimeConfig();

interface Props {
  src?: string
  defaultImage?: string
  alt?: string
  name?: string
  editable?: boolean
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl'
  status?: '' | 'online' | 'offline' | 'away' | 'busy'
  badge?: boolean | string | number
  color?: string
  square?: boolean
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full'
  gender?: '' | 'male' | 'female'
  loading?: boolean
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  src: '',
  defaultImage: 'https://ui-avatars.com/api/?background=random&color=fff',
  alt: 'Avatar',
  name: '',
  editable: false,
  size: 'md',
  status: '',
  badge: false,
  color: '',
  square: false,
  rounded: 'full',
  gender: '',
  loading: false,
  clickable: false
});

interface Emits {
  (e: 'click'): void
  (e: 'change', file: File): void
  (e: 'delete'): void
}

const emit = defineEmits<Emits>();

const error = ref<boolean>(false);
const showChangeModal = ref<boolean>(false);
const newAvatarFile = ref<File | null>(null);
const newAvatarPreview = ref<string>('');
const fileError = ref<string>('');
const isEditing = ref<boolean>(false);
const modalStep = ref<number>(1); // 1 = upload, 2 = edit
const selectedFilter = ref<string>('none');
const activeTab = ref<'filters' | 'crop'>('filters'); // 'filters' or 'crop'
const cropperRef = ref<typeof Cropper | null>(null);
const zoomValue = ref<number>(1);
const cropZoomValue = ref<number>(1); // Separate zoom for cropper
const baseCoordinates = ref<any>(null); // Store initial coordinates for zoom calculation
const currentRotation = ref<number>(0);
const isDragging = ref<boolean>(false);
const fileInput = ref<HTMLInputElement | null>(null);
const filteredPreview = ref<string>(''); // Preview with filter applied for cropper
const croppedImage = ref<string>(''); // Store the cropped result
const showDeleteModal = ref<boolean>(false); // Delete confirmation modal

// Available filters
const filters = [
  { value: 'none', label: 'Original', class: '' },
  { value: 'grayscale', label: 'B&W', class: 'grayscale(100%)' },
  { value: 'sepia', label: 'Sepia', class: 'sepia(100%)' },
  { value: 'vintage', label: 'Vintage', class: 'sepia(50%) contrast(1.2) brightness(0.9)' },
  { value: 'cool', label: 'Cool', class: 'hue-rotate(180deg) saturate(1.2)' },
  { value: 'warm', label: 'Warm', class: 'sepia(30%) saturate(1.4)' },
  { value: 'bright', label: 'Bright', class: 'brightness(1.2) contrast(1.1)' },
  { value: 'dramatic', label: 'Dramatic', class: 'contrast(1.5) saturate(0.8)' }
];

// Computed property for avatar source with backend URL
const avatarSrc = computed(() => {
  console.log('🖼️ avatarSrc - props.src:', props.src);
  
  if (!props.src) {
    console.log('🖼️ avatarSrc - No src provided, returning empty');
    return '';
  }
  
  // If it's already a full URL (http/https), return as is
  if (props.src.startsWith('http://') || props.src.startsWith('https://') || props.src.startsWith('data:')) {
    console.log('🖼️ avatarSrc - Full URL detected, returning as is:', props.src);
    return props.src;
  }
  
  // If it's a relative path from backend, prepend backend URL
  if (props.src.startsWith('/uploads/')) {
    const baseUrl = config.public.apiBaseUrl?.replace('/api', '') || 'http://localhost:8080';
    const fullUrl = `${baseUrl}${props.src}`;
    console.log('🖼️ avatarSrc - Backend path detected, returning:', fullUrl);
    return fullUrl;
  }
  
  return props.src;
});

// Computed property for initials
const initials = computed(() => {
  if (!props.name) return '';
  
  const parts = props.name.trim().split(' ');
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return parts[0].substring(0, 2).toUpperCase();
});

// Generate default avatar URL with name
const defaultAvatarUrl = computed(() => {
  if (!props.defaultImage) return '';
  
  // If the default image is set to 'illustration' and we have a name,
  // generate a personalized illustration based on the user's name and gender
  if (props.defaultImage === 'illustration' && props.name) {
    // Create a clean seed from the name (remove spaces, lowercase)
    const seed = props.name.replace(/\s+/g, '').toLowerCase();
    
    // Base URL with common parameters
    let avatarUrl = `https://api.dicebear.com/7.x/personas/svg?seed=${encodeURIComponent(seed)}&backgroundColor=0ea5e9,0284c7,0369a1,5bd692,49ab75&radius=10&skinColor=f2d3b1&age=young`;
    
    // Add gender-specific parameters if gender is provided
    if (props.gender === 'male') {
      avatarUrl += '&gender=male&hairProbability=100&beardProbability=30';
    } else if (props.gender === 'female') {
      avatarUrl += '&gender=female&hairProbability=100&accessoriesProbability=40&wrinkles=0&wrinklesProbability=0';
    }
    
    return avatarUrl;
  }
  
  // If the default image contains 'unsplash' and we have a name,
  // we can generate a unique image based on the name
  if (props.defaultImage.includes('unsplash.com') && props.name) {
    // Use a set of modern illustrations for avatars with radius=10 for rounded-lg style
    // Using project's primary and secondary color palette
    const profileImages = [
      'https://api.dicebear.com/7.x/personas/svg?seed=avatar1&backgroundColor=0ea5e9,0284c7,0369a1,5bd692,49ab75&radius=10',
      'https://api.dicebear.com/7.x/personas/svg?seed=avatar2&backgroundColor=0ea5e9,0284c7,0369a1,5bd692,49ab75&radius=10',
      'https://api.dicebear.com/7.x/personas/svg?seed=avatar3&backgroundColor=0ea5e9,0284c7,0369a1,5bd692,49ab75&radius=10',
      'https://api.dicebear.com/7.x/personas/svg?seed=avatar4&backgroundColor=0ea5e9,0284c7,0369a1,5bd692,49ab75&radius=10',
      'https://api.dicebear.com/7.x/personas/svg?seed=avatar5&backgroundColor=0ea5e9,0284c7,0369a1,5bd692,49ab75&radius=10',
      'https://api.dicebear.com/7.x/personas/svg?seed=avatar6&backgroundColor=0ea5e9,0284c7,0369a1,5bd692,49ab75&radius=10'
    ];
    
    // Generate a consistent index based on the name
    const nameHash = props.name.split('').reduce((acc, char) => {
      return char.charCodeAt(0) + ((acc << 5) - acc);
    }, 0);
    
    // Use the hash to select an image
    return profileImages[Math.abs(nameHash) % profileImages.length];
  }
  
  // If using ui-avatars.com service and name is provided
  if (props.defaultImage.includes('ui-avatars.com') && props.name) {
    // Encode the name for URL
    const encodedName = encodeURIComponent(props.name);
    return `${props.defaultImage}&name=${encodedName}`;
  }
  
  return props.defaultImage;
});

// Determine background color based on name or provided color
const bgColor = computed(() => {
  if (props.color) return props.color;
  
  // If no color is provided, generate one based on the name
  if (props.name) {
    const colors = [
      'var(--primary-500)',
      'var(--secondary-500)',
      'var(--success-500)',
      'var(--danger-500)',
      'var(--warning-500)',
      '#6366f1', // Indigo
      '#8b5cf6', // Violet
      '#ec4899', // Pink
      '#f97316', // Orange
      '#14b8a6', // Teal
    ];
    
    // Simple hash function to get consistent color for the same name
    const hash = props.name.split('').reduce((acc, char) => {
      return char.charCodeAt(0) + ((acc << 5) - acc);
    }, 0);
    
    return colors[Math.abs(hash) % colors.length];
  }
  
  // Default color
  return 'var(--gray-500)';
});

// Determine spinner size based on avatar size
const spinnerSize = computed((): 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl' | 'xxxl' => {
  const sizeMap: Record<string, 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl' | 'xxxl'> = {
    xs: 'xs',
    sm: 'xs',
    md: 'sm',
    lg: 'md',
    xl: 'lg',
    '2xl': 'lg',
    '3xl': 'xl',
    '4xl': 'xl'
  };

  return sizeMap[props.size] || 'sm';
});

// Get current filter style
const currentFilterStyle = computed(() => {
  const filter = filters.find(f => f.value === selectedFilter.value);
  return filter ? filter.class : '';
});

// Handle image error
function onImageError() {
  error.value = true;
}

// Handle click on avatar
function handleClick() {
  if (props.clickable) {
    emit('click');
  } else if (props.editable) {
    showChangeModal.value = true;
  }
}

// Open upload modal
function openUploadModal() {
  showChangeModal.value = true;
}

// Handle file upload - Apply all transformations (crop, filter, rotation, zoom)
async function handleFileUpload() {
  if (!newAvatarFile.value) return;
  
  try {
    let finalCanvas;
    
    // If cropper exists, get the cropped result
    if (cropperRef.value) {
      const { canvas } = cropperRef.value.getResult();
      finalCanvas = canvas;
    } else {
      // Create canvas from original image
      finalCanvas = document.createElement('canvas');
      const img = new Image();
      img.src = newAvatarPreview.value;
      await new Promise((resolve) => {
        img.onload = resolve;
      });
      finalCanvas.width = img.width;
      finalCanvas.height = img.height;
      const ctx = finalCanvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
    }
    
    // Apply filter and transformations
    if (finalCanvas) {
      const ctx = finalCanvas.getContext('2d');
      
      // Apply CSS filter
      if (selectedFilter.value !== 'none') {
        const filter = filters.find(f => f.value === selectedFilter.value);
        if (filter && filter.class) {
          ctx.filter = filter.class;
        }
      }
      
      // Apply rotation and zoom if needed (from positioning tab)
      if (currentRotation.value !== 0 || zoomValue.value !== 1) {
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        
        // Calculate new dimensions for rotation
        const radians = (currentRotation.value * Math.PI) / 180;
        const cos = Math.abs(Math.cos(radians));
        const sin = Math.abs(Math.sin(radians));
        const newWidth = finalCanvas.width * cos + finalCanvas.height * sin;
        const newHeight = finalCanvas.width * sin + finalCanvas.height * cos;
        
        tempCanvas.width = newWidth * zoomValue.value;
        tempCanvas.height = newHeight * zoomValue.value;
        
        tempCtx.translate(tempCanvas.width / 2, tempCanvas.height / 2);
        tempCtx.rotate(radians);
        tempCtx.scale(zoomValue.value, zoomValue.value);
        tempCtx.drawImage(finalCanvas, -finalCanvas.width / 2, -finalCanvas.height / 2);
        
        finalCanvas = tempCanvas;
      }
      
      // Convert to blob and save
      finalCanvas.toBlob((blob) => {
        const fileName = newAvatarFile.value.name || 'avatar.jpg';
        const editedFile = new File([blob], fileName, { type: 'image/jpeg' });
        emit('change', editedFile);
        showChangeModal.value = false;
        resetFileState();
      }, 'image/jpeg', 0.9);
    }
  } catch (error) {
    console.error('Error processing image:', error);
    // Fallback to original file
    emit('change', newAvatarFile.value);
    showChangeModal.value = false;
    resetFileState();
  }
}

function onDragOver(event) {
  console.log('🔵 onDragOver');
  isDragging.value = true;
}

function onDragLeave() {
  console.log('🔵 onDragLeave');
  isDragging.value = false;
}

function onDrop(event) {
  console.log('📥 onDrop called', event);
  isDragging.value = false;
  
  const files = event.dataTransfer.files;
  console.log('📥 Dropped files:', files);
  if (files.length > 0) {
    validateAndProcessFile(files[0]);
  }
}

function onFileChange(event) {
  console.log('🔵 onFileChange called', event);
  const files = event.target.files;
  console.log('🔵 Selected files:', files);
  if (files.length > 0) {
    validateAndProcessFile(files[0]);
    // Reset so selecting the same file triggers again
    event.target.value = '';
  }
}

function validateAndProcessFile(file) {
  console.log('🔍 Validating file:', file);
  fileError.value = '';
  
  if (!file) {
    console.log('❌ No file provided');
    return;
  }
  
  // Validate file type
  if (!file.type.startsWith('image/')) {
    console.log('❌ Invalid file type:', file.type);
    fileError.value = 'Please select a valid image file';
    return;
  }
  
  // Validate file size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    console.log('❌ File too large:', file.size);
    fileError.value = 'Image size exceeds 5MB limit';
    return;
  }
  
  console.log('✅ File validated, setting newAvatarFile');
  newAvatarFile.value = file;
  console.log('✅ newAvatarFile set:', newAvatarFile.value);
}

function handleFileError(errorMsg) {
  fileError.value = errorMsg;
}

function goToEditStep() {
  if (newAvatarFile.value) {
    modalStep.value = 2;
  }
}

function rotateCropper(angle) {
  if (cropperRef.value) {
    cropperRef.value.rotate(angle);
    currentRotation.value = (currentRotation.value + angle) % 360;
  }
}

function applyCropperZoom() {
  if (cropperRef.value) {
    // Use the cropper's zoom method - it zooms the image, not the stencil
    cropperRef.value.zoom(cropZoomValue.value);
  }
}

function handleCropperWheel(event) {
  if (cropperRef.value) {
    // Determine zoom direction
    const delta = event.deltaY > 0 ? -0.1 : 0.1;
    const newZoom = Math.max(0.5, Math.min(3, cropZoomValue.value + delta));
    
    // Update zoom value and apply
    cropZoomValue.value = parseFloat(newZoom.toFixed(1));
    cropperRef.value.zoom(cropZoomValue.value);
  }
}

function resetCropZoom() {
  cropZoomValue.value = 1;
  baseCoordinates.value = null;
  if (cropperRef.value) {
    // Reset to default view
    cropperRef.value.reset();
  }
}

function applyCrop() {
  if (cropperRef.value) {
    const { canvas } = cropperRef.value.getResult();
    
    if (canvas) {
      // Convert cropped canvas to blob URL
      canvas.toBlob((blob) => {
        if (croppedImage.value) {
          URL.revokeObjectURL(croppedImage.value);
        }
        croppedImage.value = URL.createObjectURL(blob);
        
        // Update the preview to use cropped image
        if (newAvatarPreview.value && newAvatarPreview.value !== croppedImage.value) {
          URL.revokeObjectURL(newAvatarPreview.value);
        }
        newAvatarPreview.value = croppedImage.value;
        
        // Clear filtered preview so it regenerates with cropped image
        if (filteredPreview.value) {
          URL.revokeObjectURL(filteredPreview.value);
          filteredPreview.value = '';
        }
        
        // Switch to filters tab to show result
        activeTab.value = 'filters';
      }, 'image/jpeg', 0.95);
    }
  }
}

function resetFileState() {
  // Clean up blob URLs before resetting
  if (newAvatarPreview.value && newAvatarPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(newAvatarPreview.value);
  }
  if (filteredPreview.value && filteredPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(filteredPreview.value);
  }
  if (croppedImage.value && croppedImage.value.startsWith('blob:')) {
    URL.revokeObjectURL(croppedImage.value);
  }

  // Reset state
  newAvatarFile.value = null;
  newAvatarPreview.value = '';
  filteredPreview.value = '';
  croppedImage.value = '';
  fileError.value = '';
  isEditing.value = false;
  modalStep.value = 1;
  selectedFilter.value = 'none';
  activeTab.value = 'filters';
  cropZoomValue.value = 1;
  baseCoordinates.value = null;
  currentRotation.value = 0;
  zoomValue.value = 1;
}

function closeChangeModal() {
  showChangeModal.value = false;
  resetFileState();
}

function confirmDelete() {
  // Show delete confirmation modal
  showDeleteModal.value = true;
}

function handleDelete() {
  // Emit delete event for parent component to handle
  emit('delete');
  showDeleteModal.value = false;
}

// Prevent default drag behavior on document when modal is open (but not inside dropzone)
let cleanupDragListeners = null;

watch(showChangeModal, (isOpen) => {
  // Clean up previous listeners if any
  if (cleanupDragListeners) {
    cleanupDragListeners();
    cleanupDragListeners = null;
  }
  
  if (isOpen) {
    // Only prevent default outside the dropzone
    const preventDefaults = (e) => {
      if (!e.target.closest('.hb-file-image__dropzone')) {
        e.preventDefault();
        e.stopPropagation();
      }
    };
    
    document.addEventListener('dragover', preventDefaults);
    document.addEventListener('drop', preventDefaults);
    
    // Store cleanup function
    cleanupDragListeners = () => {
      document.removeEventListener('dragover', preventDefaults);
      document.removeEventListener('drop', preventDefaults);
    };
  }
});

// Watch for file changes and create preview URL
watch(newAvatarFile, (file) => {
  console.log('👁️ Watcher triggered, file:', file);
  console.log('👁️ Current modalStep:', modalStep.value);
  console.log('👁️ Current newAvatarPreview:', newAvatarPreview.value);
  
  if (file && file instanceof File) {
    console.log('✅ File is valid, creating preview URL');
    // Create preview URL from the file
    newAvatarPreview.value = URL.createObjectURL(file);
    console.log('✅ Preview URL created:', newAvatarPreview.value);
    
    // Automatically go to edit step when file is uploaded
    if (modalStep.value === 1) {
      console.log('🔄 Transitioning to step 2 in 300ms...');
      setTimeout(() => {
        console.log('🔄 About to transition - modalStep:', modalStep.value, 'preview:', newAvatarPreview.value);
        modalStep.value = 2;
        console.log('✅ Transitioned to step 2 - modalStep:', modalStep.value);
      }, 300);
    }
  } else if (!file) {
    console.log('🗑️ File removed, cleaning up preview');
    // Clean up preview URL when file is removed
    if (newAvatarPreview.value) {
      URL.revokeObjectURL(newAvatarPreview.value);
      newAvatarPreview.value = '';
    }
  }
});

// Watch modalStep changes
watch(modalStep, (newStep, oldStep) => {
  console.log(`📊 modalStep changed from ${oldStep} to ${newStep}`);
  console.log('📊 newAvatarPreview:', newAvatarPreview.value);
  console.log('📊 newAvatarFile:', newAvatarFile.value);
});

// Watch for filter changes and apply to preview
watch(selectedFilter, async (newFilter) => {
  if (!newAvatarPreview.value) return;
  
  const filter = filters.find(f => f.value === newFilter);
  if (!filter) return;
  
  // Create canvas to apply filter
  const img = new Image();
  img.crossOrigin = 'anonymous';
  img.src = newAvatarPreview.value;
  
  await new Promise((resolve) => {
    img.onload = resolve;
  });
  
  const canvas = document.createElement('canvas');
  canvas.width = img.width;
  canvas.height = img.height;
  const ctx = canvas.getContext('2d');
  
  // Apply filter
  if (filter.class) {
    ctx.filter = filter.class;
  }
  ctx.drawImage(img, 0, 0);
  
  // Convert to blob URL
  canvas.toBlob((blob) => {
    if (filteredPreview.value) {
      URL.revokeObjectURL(filteredPreview.value);
    }
    filteredPreview.value = URL.createObjectURL(blob);
  }, 'image/jpeg', 0.95);
});

// Mounted lifecycle hook
onMounted(() => {
  console.log('🚀 HbAvatar component mounted');
  console.log('🚀 Props:', {
    src: props.src,
    name: props.name,
    editable: props.editable,
    size: props.size
  });
  console.log('🚀 Initial state:', {
    modalStep: modalStep.value,
    showChangeModal: showChangeModal.value,
    newAvatarFile: newAvatarFile.value,
    newAvatarPreview: newAvatarPreview.value,
    isDragging: isDragging.value,
    selectedFilter: selectedFilter.value
  });
  console.log('🚀 fileInput ref:', fileInput.value);
});

// Cleanup lifecycle hook - prevent memory leaks
onBeforeUnmount(() => {
  // Clean up all blob URLs
  if (newAvatarPreview.value && newAvatarPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(newAvatarPreview.value);
  }
  if (filteredPreview.value && filteredPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(filteredPreview.value);
  }
  if (croppedImage.value && croppedImage.value.startsWith('blob:')) {
    URL.revokeObjectURL(croppedImage.value);
  }

  // Clean up drag listeners if any
  if (cleanupDragListeners) {
    cleanupDragListeners();
  }
});
</script>

<style scoped lang="scss">
.hb-avatar-container {
  display: flex;
  align-items: center;
}

.hb-avatar-container.with-actions {
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.hb-avatar-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0;
  margin-top: 3px;
}

.hb-avatar-action-btn {
  width: 100%;
  margin-bottom: -2px;
}

.hb-avatar-action-btn :deep(.hb-button) {
  padding: 2px 8px;
}

.change-picture-modal {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.upload-section {
  margin-bottom: var(--spacing-4);
}

.image-preview {
  position: relative;
  margin-top: var(--spacing-4);
  display: flex;
  justify-content: center;
}

.preview-img {
  max-width: 100%;
  max-height: 300px;
  border-radius: var(--radius-md);
 
}

.remove-preview-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  border-radius: 50%;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
 
}

.change-pic-button {
  background: linear-gradient(to right, var(--primary-500), var(--secondary-500)) !important;
  border: 2px solid var(--primary-500) !important;
}

.delete-pic-button {
  color: var(--danger-500) !important;
  border: 2px solid var(--danger-500) !important;
}

.hb-avatar-actions .hb-button:hover {
  transform: translateY(-1px);

}

.hb-avatar {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: var(--gray-200);
  color: white;
  font-weight: var(--font-medium);
  flex-shrink: 0;
}

/* Border radius variants */
.hb-avatar--rounded-none {
  border-radius: 0;
}

.hb-avatar--rounded-sm {
  border-radius: var(--radius-sm);
}

.hb-avatar--rounded-md {
  border-radius: var(--radius-md);
}

.hb-avatar--rounded-lg {
  border-radius: var(--radius-lg);
}

.hb-avatar--rounded-xl {
  border-radius: var(--radius-xl);
}

.hb-avatar--rounded-full {
  border-radius: 9999px;
}

/* For backward compatibility */
.hb-avatar--square {
  border-radius: var(--radius-md);
}

.hb-avatar--clickable {
  cursor: pointer;
  transition: transform var(--transition-duration) var(--transition-ease);
}

.hb-avatar--clickable:hover {
  transform: scale(1.05);
}

.hb-avatar--editable {
  cursor: pointer;
}

.hb-avatar--editable:hover .hb-avatar__edit-overlay {
  opacity: 1;
}

.hb-avatar__edit-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-duration) var(--transition-ease);
}

.hb-avatar__edit-icon {
  width: 40%;
  height: 40%;
  stroke: white;
  stroke-width: 2;
}

.hb-avatar__image-container {
  width: 100%;
  height: 100%;
}

.hb-avatar__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hb-avatar__initials {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-transform: uppercase;
}

.hb-avatar__icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hb-avatar__icon svg {
  width: 60%;
  height: 60%;
  stroke: white;
}

.hb-avatar__loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--gray-200);
}

.hb-avatar__status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 25%;
  height: 25%;
  border-radius: 50%;
  border: 2px solid white;
}

.hb-avatar__status--online {
  background-color: var(--success-500);
}

.hb-avatar__status--offline {
  background-color: var(--gray-400);
}

.hb-avatar__status--away {
  background-color: var(--warning-500);
}

.hb-avatar__status--busy {
  background-color: var(--danger-500);
}

.hb-avatar__badge {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  background-color: var(--danger-500);
  color: white;
  font-size: var(--text-xs);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--spacing-1);
  border: 2px solid white;
  transform: translate(25%, -25%);
}

/* Size variants */
.hb-avatar--xs {
  width: 24px;
  height: 24px;
  font-size: var(--text-xs);
}

.hb-avatar--xs .hb-avatar__status {
  width: 8px;
  height: 8px;
  border-width: 1px;
}

.hb-avatar--xs .hb-avatar__badge {
  min-width: 16px;
  height: 16px;
  font-size: 10px;
  border-width: 1px;
}

.hb-avatar--sm {
  width: 32px;
  height: 32px;
  font-size: var(--text-xs);
}

.hb-avatar--sm .hb-avatar__status {
  width: 10px;
  height: 10px;
  border-width: 1px;
}

.hb-avatar--sm .hb-avatar__badge {
  min-width: 18px;
  height: 18px;
  font-size: 10px;
  border-width: 1px;
}

.hb-avatar--md {
  width: 40px;
  height: 40px;
  font-size: var(--text-sm);
}

.hb-avatar--lg {
  width: 48px;
  height: 48px;
  font-size: var(--text-base);
}

.hb-avatar--xl {
  width: 64px;
  height: 64px;
  font-size: var(--text-lg);
}

.hb-avatar--2xl {
  width: 80px;
  height: 80px;
  font-size: var(--text-xl);
}

.hb-avatar--3xl {
  width: 96px;
  height: 96px;
  font-size: var(--text-2xl);
}

.hb-avatar--4xl {
  width: 128px;
  height: 128px;
  font-size: var(--text-3xl);
}

/* Avatar Group Styles */
.hb-avatar__group {
  display: flex;
}

.hb-avatar__group .hb-avatar {
  margin-left: -8px;
  border: 2px solid white;
}

.hb-avatar__group .hb-avatar:first-child {
  margin-left: 0;
}

/* Responsive styles */
@media (min-width: 640px) {
  .hb-avatar-container.with-actions {
    flex-direction: row;
    align-items: center;
    gap: 1rem;
  }
  
  .hb-avatar-actions {
    margin-top: 0;
  }
}

/* Avatar Upload Step Styles */
.avatar-upload-step {
  padding: 1rem 0;
}

/* HbFileImage styles (copied) */
.hb-file-image__dropzone {
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
  min-height: 200px;
}

.hb-file-image__dropzone:hover {
  border-color: var(--primary-400);
  background-color: transparent;
}

.hb-file-image__dropzone--dragging {
  border-color: var(--primary-500);
  background-color: transparent;
}

.hb-file-image__input {
  display: none;
}

.hb-file-image__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.hb-file-image__icon {
  color: var(--primary-500);
  margin-bottom: var(--spacing-3);
}

.hb-file-image__icon svg {
  background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hb-file-image__text {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hb-file-image__primary-text {
  font-weight: var(--font-medium);
  color: var(--gray-400);
  font-family: var(--font-gabarito);
  margin-bottom: var(--spacing-1);
}

.hb-file-image__secondary-text {
  color: var(--primary-500);
  font-size: var(--text-sm);
}

/* Avatar Edit Step Styles */
.avatar-edit-step {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.avatar-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--gray-50);
  border-radius: var(--radius-lg);
  padding: 2rem;
  min-height: 300px;
}

.avatar-preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: var(--radius-lg);
  object-fit: contain;
  transition: filter 0.3s ease, transform 0.3s ease;
}

/* Tabs */
.avatar-tabs {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.5rem;
  border-bottom: 1px solid var(--gray-600);
}

.tab-btn {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--gray-400);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: -1px;
}

.tab-btn:hover {
  color: var(--gray-200);
  background-color: var(--gray-700);
}

.tab-btn.active {
  color: var(--primary-400);
  border-bottom-color: var(--primary-400);
}

.tab-content {
  margin-top: 1rem;
}

/* Crop Tab */
.crop-tab {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.apply-crop-section {
  margin-top: 0.5rem;
}

/* Positioning Tab */
.positioning-tab {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cropper-container {
  background-color: var(--gray-900);
  border-radius: var(--radius-md);
  overflow: hidden;
  height: 400px;
}

.cropper {
  width: 100%;
  height: 100%;
}

/* Cropper custom styling */
:deep(.vue-advanced-cropper__background),
:deep(.vue-advanced-cropper__foreground) {
  background-color: var(--gray-900);
}

:deep(.vue-advanced-cropper__stretcher) {
  max-height: 400px;
}

:deep(.vue-advanced-cropper__image) {
  max-height: 400px;
}

:deep(.vue-advanced-cropper__boundaries) {
  background-color: var(--gray-900);
}

:deep(.vue-line-wrapper) {
  border-color: rgba(255, 255, 255, 0.3);
}

:deep(.vue-handler) {
  background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

/* Zoom & Rotation Controls */
.avatar-controls {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background-color: var(--gray-700);
  border-radius: var(--radius-md);
}

.control-group {
  flex: 1;
}

.control-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--gray-300);
  margin-bottom: 0.5rem;
}

.zoom-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.zoom-value {
  min-width: 2.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--gray-200);
}

.slider {
  flex: 1;
  height: 4px;
  background: var(--gray-600);
  border-radius: 2px;
  appearance: none;
  outline: none;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
  border: none;
  cursor: pointer;
}

.rotation-control {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: center;
}

.rotation-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: var(--gray-600);
  border: none;
  border-radius: var(--radius-md);
  color: var(--gray-300);
  cursor: pointer;
  transition: all 0.2s ease;
}

.rotation-btn svg {
  width: 18px;
  height: 18px;
}

.rotation-btn:hover {
  background-color: var(--gray-500);
  color: var(--primary-400);
}

.rotation-value {
  min-width: 2.5rem;
  text-align: center;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--gray-200);
}

.avatar-filters {
  margin-top: 1rem;
}

.filter-grid {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    height: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--gray-100);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--primary-400);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: var(--primary-500);
  }
}

.filter-option {
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  padding: 0.5rem;
  transition: all 0.2s ease;
  text-align: center;
  flex-shrink: 0;
  width: auto;
  background-color: var(--gray-700);
}

.filter-option:hover {
  border-color: var(--primary-400);
  background-color: var(--gray-600);
}

.filter-option.active {
  border-color: var(--primary-500);
  background-color: var(--gray-600);
}

.filter-preview {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 0.5rem;
  background-color: var(--gray-100);
}

.filter-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.filter-label {
  font-size: 0.75rem;
  color: var(--gray-300);
  font-weight: var(--font-medium);
  display: block;
}

.filter-option.active .filter-label {
  color: var(--primary-400);
}
</style>
