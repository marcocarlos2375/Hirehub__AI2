<template>
  <div class="hb-profile-picture-wrapper">
    <div class="hb-profile-picture-container">
      <!-- Preview Display -->
      <div
        class="hb-profile-picture-preview"
        :class="[
          `size-${size}`,
          { 'hb-profile-picture-preview--clickable': editable }
        ]"
        :role="editable ? 'button' : undefined"
        :tabindex="editable ? 0 : undefined"
        :aria-label="editable ? (modelValue ? 'Change profile picture' : 'Upload profile picture') : undefined"
        @click="handlePreviewClick"
        @keydown.enter="handlePreviewClick"
        @keydown.space.prevent="handlePreviewClick"
      >
        <!-- Image Preview -->
        <div v-if="modelValue && !loading" class="hb-profile-picture-preview__image-container">
          <img
            :src="getImageUrl(modelValue)"
            :alt="alt"
            class="hb-profile-picture-preview__image"
            @error="onImageError"
          />
        </div>

        <!-- Placeholder (when no image) -->
        <div v-else-if="!loading" class="hb-profile-picture-preview__placeholder">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span class="text-sm text-gray-500 mt-2">No photo</span>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="hb-profile-picture-preview__loading">
          <HbSpinner size="md" color="primary" />
        </div>

        <!-- Edit Overlay -->
        <div v-if="editable && !loading" class="hb-profile-picture-preview__edit-overlay">
          <i class="ri-pencil-line"></i>
        </div>
      </div>

      <!-- Action Buttons -->
      <div v-if="editable" class="hb-profile-picture-actions">
        <HbButton
          variant="outline"
          size="sm"
          @click="openModal"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {{ modelValue ? 'Change Photo' : 'Upload Photo' }}
        </HbButton>

        <HbButton
          v-if="modelValue"
          variant="outline"
          size="sm"
          class="mt-2"
          @click="confirmRemove"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          Remove Photo
        </HbButton>
      </div>
    </div>

    <!-- Main Modal with Two Tabs -->
    <HbModal
      v-model="showModal"
      :title="getModalTitle"
      size="lg"
      appearance="dark"
      @close="closeModal"
    >
      <!-- Top-level Tab Navigation -->
      <div class="profile-picture-main-tabs">
        <button
          class="main-tab-btn"
          :class="{ 'active': mainTab === 'gallery' }"
          @click="mainTab = 'gallery'"
          type="button"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          My Pictures ({{ userPictures.length }}/{{ MAX_PICTURES }})
        </button>
        <button
          class="main-tab-btn"
          :class="{ 'active': mainTab === 'upload' }"
          @click="mainTab = 'upload'"
          type="button"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Upload New
        </button>
      </div>

      <!-- Tab Content -->
      <div class="profile-picture-tab-content">
        <!-- Gallery Tab -->
        <div v-if="mainTab === 'gallery'" class="gallery-tab">
          <p v-if="userPictures.length === 0" class="text-sm text-gray-400 text-center py-8">
            You haven't uploaded any profile pictures yet. Click "Upload New" to add your first picture.
          </p>

          <div v-else class="picture-grid" role="list" aria-label="Profile picture gallery">
            <div
              v-for="picture in userPictures"
              :key="picture.id"
              class="picture-card"
              :class="{ 'selected': selectedPictureId === picture.id }"
              role="listitem"
              tabindex="0"
              :aria-label="`${picture.name}${picture.isDefault ? ' (default)' : ''}${selectedPictureId === picture.id ? ' (selected)' : ''}`"
              @click="selectPicture(picture)"
              @keydown.enter="selectPicture(picture)"
              @keydown.space.prevent="selectPicture(picture)"
            >
              <div class="picture-card__image-container">
                <img
                  :src="getImageUrl(picture)"
                  :alt="picture.name"
                  class="picture-card__image"
                />

                <!-- Selected Overlay -->
                <div v-if="selectedPictureId === picture.id" class="picture-card__selected-overlay">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>

                <!-- Default Badge -->
                <div v-if="picture.isDefault" class="picture-card__default-badge">
                  Default
                </div>
              </div>

              <div class="picture-card__info">
                <span class="picture-card__name">{{ picture.name }}</span>

                <!-- Actions -->
                <div class="picture-card__actions">
                  <button
                    v-if="!picture.isDefault"
                    class="action-btn action-btn--default"
                    type="button"
                    :aria-label="`Set ${picture.name} as default`"
                    @click.stop="setAsDefault(picture.id)"
                    title="Set as default"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  </button>

                  <button
                    class="action-btn action-btn--delete"
                    type="button"
                    :aria-label="`Delete ${picture.name}`"
                    @click.stop="confirmDelete(picture.id)"
                    title="Delete"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 1 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upload Tab -->
        <div v-else-if="mainTab === 'upload'" class="upload-tab">
          <!-- API Error Message -->
          <div v-if="apiError" class="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-200 text-sm">
            {{ apiError }}
          </div>

          <!-- Step 1: Upload -->
          <div v-if="uploadStep === 1" class="upload-step">
            <p class="text-sm text-gray-300 mb-4">
              Upload a new profile picture. Supported formats: JPG, PNG, GIF, WebP. Maximum size: {{ MAX_FILE_SIZE_MB }}MB.
            </p>

            <p v-if="userPictures.length >= MAX_PICTURES" class="text-sm text-red-400 mb-4">
              ⚠️ You've reached the maximum limit of {{ MAX_PICTURES }} pictures. Please delete an existing picture before uploading a new one.
            </p>

            <!-- Upload dropzone -->
            <div
              class="hb-file-image__dropzone"
              :class="{
                'hb-file-image__dropzone--dragging': isDragging,
                'hb-file-image__dropzone--disabled': userPictures.length >= MAX_PICTURES
              }"
              role="button"
              tabindex="0"
              :aria-label="userPictures.length >= MAX_PICTURES ? 'Maximum pictures reached' : 'Upload profile picture - drag and drop or click to browse'"
              :aria-disabled="userPictures.length >= MAX_PICTURES"
              @dragover.prevent="onDragOver"
              @dragleave.prevent="onDragLeave"
              @drop.prevent="onDrop"
              @click="userPictures.length < MAX_PICTURES && fileInput?.click()"
              @keydown.enter="userPictures.length < MAX_PICTURES && fileInput?.click()"
              @keydown.space.prevent="userPictures.length < MAX_PICTURES && fileInput?.click()"
            >
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                class="hb-file-image__input"
                aria-label="Select image file"
                @change="onFileChange"
                :disabled="userPictures.length >= MAX_PICTURES"
              />

              <div class="hb-file-image__placeholder">
                <div class="hb-file-image__icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 64 64" fill-rule="evenodd">
                    <path fill="#ffffff" d="M15.017 22.248C6.501 23.67 0 31.081 0 40c0 9.934 8.066 18 18 18s18-8.066 18-18V29a2 2 0 0 0-4 0v11c0 7.727-6.273 14-14 14S4 47.727 4 40c0-7.443 5.82-13.538 13.154-13.975a2.002 2.002 0 0 0 1.876-2.132C19.01 23.598 19 23.3 19 23c0-7.175 5.825-13 13-13s13 5.825 13 13c0 .339-.013.675-.038 1.007a2.001 2.001 0 0 0 2.306 2.129A11 11 0 0 1 49 26c6.071 0 11 4.929 11 11s-4.929 11-11 11H38a2 2 0 0 0 0 4h11c8.279 0 15-6.721 15-15s-6.721-15-15-15h-.03C48.452 13.082 41.047 6 32 6c-9.13 0-16.589 7.213-16.983 16.248z"/>
                    <path fill="#009fdf" d="M32 30.968V40c0 7.727-6.27 14-14 14-1.1 0-2 .896-2 2s.9 2 2 2c9.93 0 18-8.066 18-18v-9.102l3.6 3.53c.79.773 2.06.76 2.83-.028s.76-2.055-.03-2.828l-5.53-5.427c-1.54-1.512-4.04-1.524-5.6-.028-2.06 1.983-5.66 5.441-5.66 5.441a2.002 2.002 0 0 0 2.78 2.884z"/>
                  </svg>
                </div>
                <div class="hb-file-image__text">
                  <span class="hb-file-image__primary-text">
                    {{ userPictures.length >= MAX_PICTURES ? 'Maximum pictures reached' : 'Drag and drop your image here' }}
                  </span>
                  <span v-if="userPictures.length < MAX_PICTURES" class="hb-file-image__secondary-text">or click to browse</span>
                </div>
              </div>
            </div>

            <!-- Picture name input -->
            <div v-if="newPictureFile" class="mt-4">
              <label class="block text-sm font-medium text-gray-300 mb-2">Picture Name</label>
              <input
                v-model="newPictureName"
                type="text"
                class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., Professional Headshot, Casual Photo"
              />
            </div>

            <p v-if="fileError" class="text-sm text-red-600 mt-2">{{ fileError }}</p>
          </div>

          <!-- Step 2: Edit with Cropper, Rotate & Filters -->
          <div v-else-if="uploadStep === 2 && newPicturePreview" class="edit-step">
            <!-- Preview with filter (hidden when in crop tab) -->
            <div v-if="editTab !== 'crop'" class="edit-preview-container">
              <img
                :src="rotatedImagePreview || newPicturePreview"
                alt="Picture preview"
                :style="{
                  filter: currentFilterStyle
                }"
                class="edit-preview-image"
              />
            </div>

            <!-- Edit Tabs -->
            <div class="edit-tabs">
              <button
                class="edit-tab-btn"
                :class="{ 'active': editTab === 'filters' }"
                @click="editTab = 'filters'"
                type="button"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
                Filters
              </button>
              <button
                class="edit-tab-btn"
                :class="{ 'active': editTab === 'crop' }"
                @click="editTab = 'crop'"
                type="button"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243 4.243 3 3 0 004.243-4.243zm0-5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z" />
                </svg>
                Crop
              </button>
            </div>

            <!-- Edit Tab Content -->
            <div class="edit-tab-content">
              <!-- Filters Tab -->
              <div v-if="editTab === 'filters'" class="filters-content">
                <div class="filter-grid" role="radiogroup" aria-label="Image filters">
                  <div
                    v-for="filter in filters"
                    :key="filter.value"
                    class="filter-option"
                    :class="{ 'active': selectedFilter === filter.value }"
                    role="radio"
                    tabindex="0"
                    :aria-checked="selectedFilter === filter.value"
                    :aria-label="`${filter.label} filter`"
                    @click="selectedFilter = filter.value"
                    @keydown.enter="selectedFilter = filter.value"
                    @keydown.space.prevent="selectedFilter = filter.value"
                  >
                    <div class="filter-preview">
                      <img
                        :src="newPicturePreview"
                        alt="Filter preview"
                        :style="{ filter: filter.class }"
                      />
                    </div>
                    <span class="filter-label">{{ filter.label }}</span>
                  </div>
                </div>
              </div>

              <!-- Crop Tab -->
              <div v-else-if="editTab === 'crop'" class="crop-content">
                <!-- Cropper -->
                <div class="cropper-container">
                  <Cropper
                    ref="cropperRef"
                    class="cropper"
                    :src="rotatedImagePreview || filteredPreview || newPicturePreview"
                    :stencil-props="{
                      aspectRatio: 1,
                      movable: true,
                      resizable: false
                    }"
                    :stencil-size="{
                      width: 300,
                      height: 300
                    }"
                    :default-size="{
                      width: 300,
                      height: 300
                    }"
                    :resize-image="{
                      adjustStencil: false
                    }"
                    :image-restriction="'stencil'"
                  />
                </div>

                <!-- Crop Instructions -->
                <div class="crop-instructions">
                  <p class="text-sm text-gray-300">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Use mouse wheel to zoom • Drag to reposition • Drag corners to resize
                  </p>
                </div>

                <!-- Zoom & Rotation Controls -->
                <div class="edit-controls">
                  <!-- Zoom Control -->
                  <div class="control-group">
                    <label class="control-label">Zoom</label>
                    <div class="zoom-control">
                      <span class="zoom-value">{{ cropZoomValue.toFixed(1) }}×</span>
                      <input
                        type="range"
                        class="slider"
                        min="0.5"
                        max="3"
                        step="0.1"
                        v-model.number="cropZoomValue"
                        @input="applyCropperZoom"
                        aria-label="Zoom level"
                      />
                      <HbButton
                        variant="dark-ghost"
                        size="sm"
                        @click="resetCropZoom"
                      >
                        Reset
                      </HbButton>
                    </div>
                  </div>

                  <!-- Rotation Control -->
                  <div class="control-group">
                    <label class="control-label">Rotate Image</label>
                    <div class="rotation-control">
                      <button
                        class="rotation-btn"
                        @click="rotateCropper(-90)"
                        type="button"
                        aria-label="Rotate 90 degrees counter-clockwise"
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
                        aria-label="Rotate 90 degrees clockwise"
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
                    Apply Crop
                  </HbButton>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end space-x-2">
          <!-- Gallery Tab Footer -->
          <template v-if="mainTab === 'gallery'">
            <HbButton
              variant="ghost"
              @click="closeModal"
              size="sm"
            >
              Cancel
            </HbButton>

            <HbButton
              variant="primary"
              @click="useSelectedPicture"
              size="sm"
              :disabled="!selectedPictureId"
            >
              Use Selected Picture
            </HbButton>
          </template>

          <!-- Upload Tab Footer -->
          <template v-else-if="mainTab === 'upload'">
            <HbButton
              v-if="uploadStep === 2"
              variant="ghost"
              @click="uploadStep = 1"
              size="sm"
            >
              Back
            </HbButton>

            <HbButton
              variant="ghost"
              @click="closeModal"
              size="sm"
            >
              Cancel
            </HbButton>

            <HbButton
              v-if="uploadStep === 1"
              variant="primary"
              @click="goToEditStep"
              size="sm"
              :disabled="!newPictureFile || !newPictureName"
            >
              Next
            </HbButton>

            <HbButton
              v-else
              variant="primary"
              @click="savePicture"
              size="sm"
              :disabled="saving"
            >
              {{ saving ? 'Saving...' : 'Save Picture' }}
            </HbButton>
          </template>
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
        Are you sure you want to delete this profile picture? This action cannot be undone.
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
            :disabled="deleting"
          >
            {{ deleting ? 'Deleting...' : 'Delete' }}
          </HbButton>
        </div>
      </template>
    </HbModal>

    <!-- Remove Photo Confirmation Modal -->
    <HbModal
      v-model="showRemoveModal"
      title="Remove Profile Picture"
      size="sm"
      appearance="dark"
      @close="showRemoveModal = false"
    >
      <p class="text-sm text-gray-300 mb-4">
        Are you sure you want to remove this profile picture from your cover letter/resume?
      </p>

      <template #footer>
        <div class="flex justify-end space-x-2">
          <HbButton
            variant="dark-ghost"
            @click="showRemoveModal = false"
            size="sm"
          >
            Cancel
          </HbButton>

          <HbButton
            variant="danger"
            @click="handleRemove"
            size="sm"
          >
            Remove
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
import { profilePictureApi } from '~/services/api';
import type { ProfilePicture } from '~/types/entities';

// Constants
const MAX_PICTURES = 6;
const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'] as const;
const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp'] as const;

type SizeVariant = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
type MainTab = 'gallery' | 'upload';
type EditTab = 'filters' | 'crop';
type FilterValue = 'none' | 'grayscale' | 'sepia' | 'vintage' | 'cool' | 'warm' | 'bright' | 'dramatic';

interface Props {
  modelValue?: string
  alt?: string
  editable?: boolean
  size?: SizeVariant
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  alt: 'Profile Picture',
  editable: true,
  size: 'lg'
});

// Use ProfilePicture type from entities, but keep Picture as alias for compatibility
type Picture = ProfilePicture;

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'picture-uploaded', picture: Picture): void
  (e: 'picture-deleted', id: number): void
}

const emit = defineEmits<Emits>();

// Runtime config
// NOTE: Replace useRuntimeConfig with your environment config
// For Vite: import.meta.env.VITE_API_URL
// For Vue 3: app.config.globalProperties.$config
// Also requires replacing profilePictureApi with your own API implementation
// @ts-expect-error - useRuntimeConfig is auto-imported by Nuxt
const config = useRuntimeConfig();
// Normalize backend URL - remove trailing slash and /api to get base URL
const backendUrl = (config.public.apiUrl as string).replace(/\/$/, '').replace('/api', '');

// Helper function to get image URL (handles both base64 and file paths)
// Use the profile picture URL composable
const { getImageUrl: getProfilePictureUrl } = useProfilePictureUrl();

/**
 * Get image URL for display
 * Handles both ProfilePicture objects and string paths for backward compatibility
 */
function getImageUrl(value: string | Picture | null | undefined): string {
  if (!value) return '';

  // If it's a string (legacy or base64)
  if (typeof value === 'string') {
    // If it's already a data URL (base64), return as-is
    if (value.startsWith('data:')) return value;
    // If it's a file path, convert to full URL (legacy support)
    if (value.startsWith('/')) {
      const fullUrl = `${backendUrl}/api${value}`;  // Add /api prefix
      return fullUrl;
    }
    // If it's a MinIO object key (doesn't start with / or http), prepend /api/images/
    if (!value.startsWith('http')) {
      return `${backendUrl}/api/images/${value}`;
    }
    // Otherwise return as-is
    return value;
  }

  // If it's a ProfilePicture object, use the composable
  const url = getProfilePictureUrl(value, 'original');
  return url || '';
}

// State
const loading = ref<boolean>(false);
const error = ref<boolean>(false);
const apiError = ref<string>(''); // For displaying API errors to user
const showModal = ref<boolean>(false);
const mainTab = ref<MainTab>('gallery');
const uploadStep = ref<1 | 2>(1); // 1 = upload, 2 = edit
const editTab = ref<EditTab>('filters');
const fileInput = ref<HTMLInputElement | null>(null);

// AbortController for cancelling API requests
let fetchAbortController: AbortController | null = null;
let saveAbortController: AbortController | null = null;
let deleteAbortController: AbortController | null = null;

// Debounce timer for filter watcher
let filterDebounceTimer: ReturnType<typeof setTimeout> | null = null;

// User's uploaded pictures
const userPictures = ref<Picture[]>([]);
const selectedPictureId = ref<number | null>(null);

// Upload state
const newPictureFile = ref<File | null>(null);
const newPictureName = ref<string>('');
const newPicturePreview = ref<string>('');
const isDragging = ref<boolean>(false);
const fileError = ref<string>('');
const saving = ref<boolean>(false);

// Edit state
const selectedFilter = ref<FilterValue>('none');
const cropperRef = ref<InstanceType<typeof Cropper> | null>(null);
const cropZoomValue = ref<number>(1); // Desired zoom level from slider
const currentActualZoom = ref<number>(1); // Track actual zoom state of cropper
const currentRotation = ref<number>(0);
const filteredPreview = ref<string>('');
const croppedImage = ref<string>('');
const rotatedImagePreview = ref<string>(''); // For storing rotated image

// Delete state
const showDeleteModal = ref<boolean>(false);
const pictureToDelete = ref<number | null>(null);
const deleting = ref<boolean>(false);

// Remove state
const showRemoveModal = ref<boolean>(false);

interface Filter {
  value: FilterValue
  label: string
  class: string
}

// Available filters
const filters: Filter[] = [
  { value: 'none', label: 'Original', class: '' },
  { value: 'grayscale', label: 'B&W', class: 'grayscale(100%)' },
  { value: 'sepia', label: 'Sepia', class: 'sepia(100%)' },
  { value: 'vintage', label: 'Vintage', class: 'sepia(50%) contrast(1.2) brightness(0.9)' },
  { value: 'cool', label: 'Cool', class: 'hue-rotate(180deg) saturate(1.2)' },
  { value: 'warm', label: 'Warm', class: 'sepia(30%) saturate(1.4)' },
  { value: 'bright', label: 'Bright', class: 'brightness(1.2) contrast(1.1)' },
  { value: 'dramatic', label: 'Dramatic', class: 'contrast(1.5) saturate(0.8)' }
];

// Computed
const getModalTitle = computed<string>(() => {
  if (mainTab.value === 'gallery') {
    return 'My Profile Pictures';
  }
  if (uploadStep.value === 1) {
    return 'Upload Profile Picture';
  }
  return 'Edit Profile Picture';
});

const currentFilterStyle = computed<string>(() => {
  const filter = filters.find(f => f.value === selectedFilter.value);
  return filter ? filter.class : '';
});

// Methods
function handlePreviewClick(): void {
  if (props.editable) {
    openModal();
  }
}

function openModal(): void {
  showModal.value = true;
  fetchUserPictures();
}

function closeModal(): void {
  showModal.value = false;
  resetUploadState();
}

async function fetchUserPictures(): Promise<void> {
  // Cancel any in-flight fetch request
  if (fetchAbortController) {
    fetchAbortController.abort();
  }
  fetchAbortController = new AbortController();

  loading.value = true;
  apiError.value = '';

  const { data, error } = await profilePictureApi.getAll();
  loading.value = false;

  if (error) {
    console.error('Failed to fetch pictures:', error);
    apiError.value = 'Failed to load pictures. Please try again.';
    return;
  }

  userPictures.value = data.pictures || [];
}

function selectPicture(picture: Picture): void {
  selectedPictureId.value = picture.id;
}

function useSelectedPicture(): void {
  const selected = userPictures.value.find(p => p.id === selectedPictureId.value);
  if (selected) {
    emit('update:modelValue', selected.proxyUrl || selected.filePath);
    closeModal();
  }
}

async function setAsDefault(pictureId: number): Promise<void> {
  apiError.value = '';
  const { error } = await profilePictureApi.setDefault(pictureId);

  if (error) {
    console.error('Failed to set default:', error);
    apiError.value = 'Failed to set default picture. Please try again.';
    return;
  }

  // Update local state
  userPictures.value = userPictures.value.map(p => ({
    ...p,
    isDefault: p.id === pictureId
  }));
}

function confirmDelete(pictureId: number): void {
  pictureToDelete.value = pictureId;
  showDeleteModal.value = true;
}

async function handleDelete(): Promise<void> {
  if (!pictureToDelete.value) return;

  // Find the picture BEFORE removing it from the array
  const deletedPicture = userPictures.value.find(p => p.id === pictureToDelete.value);

  deleting.value = true;
  const { error } = await profilePictureApi.delete(pictureToDelete.value);
  deleting.value = false;

  if (error) {
    console.error('Failed to delete picture:', error);
    apiError.value = 'Failed to delete picture. Please try again.';
    return;
  }

  // Remove from local state
  userPictures.value = userPictures.value.filter(p => p.id !== pictureToDelete.value);

  // Clear selection if deleted picture was selected
  if (selectedPictureId.value === pictureToDelete.value) {
    selectedPictureId.value = null;
  }

  // If the deleted picture is currently displayed, remove it
  if (deletedPicture && props.modelValue === deletedPicture.filePath) {
    emit('update:modelValue', '');
  }

  emit('picture-deleted', pictureToDelete.value);

  showDeleteModal.value = false;
  pictureToDelete.value = null;
}

function confirmRemove(): void {
  showRemoveModal.value = true;
}

function handleRemove(): void {
  emit('update:modelValue', '');
  showRemoveModal.value = false;
}

// Upload handlers
function onDragOver(event: DragEvent): void {
  if (userPictures.value.length >= MAX_PICTURES) return;
  isDragging.value = true;
}

function onDragLeave(): void {
  isDragging.value = false;
}

async function onDrop(event: DragEvent): Promise<void> {
  if (userPictures.value.length >= MAX_PICTURES) return;

  isDragging.value = false;
  const files = event.dataTransfer?.files;

  if (files && files.length > 0) {
    await validateAndProcessFile(files[0]);
  }
}

async function onFileChange(event: Event): Promise<void> {
  const files = (event.target as HTMLInputElement).files;

  if (files && files.length > 0) {
    await validateAndProcessFile(files[0]);
    (event.target as HTMLInputElement).value = '';
  }
}

/**
 * Verify that a file is actually a valid image by attempting to load it
 */
async function verifyImageContent(file: File): Promise<boolean> {
  return new Promise((resolve) => {
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(objectUrl);
      resolve(true);
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      resolve(false);
    };

    img.src = objectUrl;
  });
}

async function validateAndProcessFile(file: File | undefined): Promise<void> {
  fileError.value = '';

  if (!file) return;

  // Validate file type with whitelist
  const fileMimeType = file.type.toLowerCase();
  if (!ALLOWED_MIME_TYPES.includes(fileMimeType as typeof ALLOWED_MIME_TYPES[number])) {
    fileError.value = 'Invalid file type. Please upload JPG, PNG, GIF, or WebP images only.';
    return;
  }

  // Additional extension validation for extra security
  const fileName = file.name.toLowerCase();
  const hasValidExtension = ALLOWED_EXTENSIONS.some(ext => fileName.endsWith(ext));
  if (!hasValidExtension) {
    fileError.value = 'Invalid file extension. Please upload JPG, PNG, GIF, or WebP images only.';
    return;
  }

  // Validate file size using constant
  if (file.size > MAX_FILE_SIZE_BYTES) {
    fileError.value = `Image size exceeds ${MAX_FILE_SIZE_MB}MB limit`;
    return;
  }

  // Verify actual image content (prevents malicious files with fake MIME types)
  const isValidImage = await verifyImageContent(file);
  if (!isValidImage) {
    fileError.value = 'File appears to be corrupted or is not a valid image.';
    return;
  }

  newPictureFile.value = file;

  // Auto-generate name from filename
  if (!newPictureName.value) {
    const fileNameWithoutExt = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
    newPictureName.value = fileNameWithoutExt;
  }
}

function goToEditStep(): void {
  if (newPictureFile.value && newPictureName.value) {
    uploadStep.value = 2;
  }
}

async function savePicture(): Promise<void> {
  if (!newPictureFile.value || !newPictureName.value) return;

  saving.value = true;

  try {
    let sourceCanvas: HTMLCanvasElement;

    // Get cropped result if cropper exists
    if (cropperRef.value) {
      const { canvas } = cropperRef.value.getResult();
      sourceCanvas = canvas;
    } else {
      // Create canvas from original image
      sourceCanvas = document.createElement('canvas');
      const img = new Image();
      img.src = newPicturePreview.value;
      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = () => reject(new Error('Failed to load image'));
      });
      sourceCanvas.width = img.width;
      sourceCanvas.height = img.height;
      const ctx = sourceCanvas.getContext('2d');
      if (!ctx) {
        throw new Error('Failed to get canvas 2D context');
      }
      ctx.drawImage(img, 0, 0);
    }

    let finalCanvas = sourceCanvas;

    // Apply filter if selected (must create new canvas and apply filter BEFORE drawing)
    if (selectedFilter.value !== 'none') {
      const filter = filters.find(f => f.value === selectedFilter.value);
      if (filter && filter.class) {
        // Create new canvas for filtered result
        const filteredCanvas = document.createElement('canvas');
        filteredCanvas.width = sourceCanvas.width;
        filteredCanvas.height = sourceCanvas.height;
        const ctx = filteredCanvas.getContext('2d');

        if (!ctx) {
          throw new Error('Failed to get canvas 2D context for filtering');
        }

        // Set filter BEFORE drawing
        ctx.filter = filter.class;

        // Draw source canvas with filter applied
        ctx.drawImage(sourceCanvas, 0, 0);

        // Use filtered canvas as final result
        finalCanvas = filteredCanvas;

        console.log(`Applied filter: ${filter.label} (${filter.class})`);
      }
    }

    // Convert to base64 data URL
    const imageData = finalCanvas.toDataURL('image/jpeg', 0.9);

    // Save to backend
    const { data, error } = await profilePictureApi.create({
      name: newPictureName.value,
      imageData: imageData,
      isDefault: userPictures.value.length === 0
    });

    saving.value = false;

    if (error) {
      fileError.value = error;
      return;
    }

    // Add to local state
    userPictures.value.push(data.picture);

    // Auto-select the new picture
    emit('update:modelValue', data.picture.proxyUrl || data.picture.filePath);
    emit('picture-uploaded', data.picture);

    // Show notification if duplicate was detected
    if (data.isDuplicate) {
      console.info('Duplicate image detected - existing file reused to save storage space');
    }

    closeModal();
  } catch (error) {
    saving.value = false;
    console.error('Error saving picture:', error);
    fileError.value = 'Failed to save picture';
  }
}

// Cropper methods
/**
 * Apply zoom to the cropper using native zoom method with relative factor calculation
 * This scales only the image, keeping the grid fixed
 * Note: zoom() is a RELATIVE method (multiplier), not absolute
 */
function applyCropperZoom(): void {
  if (!cropperRef.value) return;

  // Calculate the relative zoom factor needed to reach the desired zoom level
  // zoom() expects a multiplier from current state, not an absolute value
  const relativeFactor = cropZoomValue.value / currentActualZoom.value;

  // Apply the relative zoom
  cropperRef.value.zoom(relativeFactor);

  // Update tracked zoom level to keep in sync
  currentActualZoom.value = cropZoomValue.value;
}

function resetCropZoom(): void {
  // Calculate relative factor to get back to 1.0
  const relativeFactor = 1.0 / currentActualZoom.value;

  if (cropperRef.value) {
    cropperRef.value.zoom(relativeFactor);
  }

  // Reset both zoom values to 1
  cropZoomValue.value = 1;
  currentActualZoom.value = 1;
}

async function rotateCropper(angle: number): Promise<void> {
  currentRotation.value = (currentRotation.value + angle) % 360;

  // Rotate the source image using canvas
  const sourceImage = filteredPreview.value || newPicturePreview.value;
  if (!sourceImage) return;

  try {
    const img = new Image();
    img.src = sourceImage;

    await new Promise<void>((resolve, reject) => {
      img.onload = () => resolve();
      img.onerror = () => reject(new Error('Failed to load image'));
    });

    const canvas = document.createElement('canvas');

    // Swap width/height for 90 or 270 degree rotations
    if (currentRotation.value === 90 || currentRotation.value === 270) {
      canvas.width = img.height;
      canvas.height = img.width;
    } else {
      canvas.width = img.width;
      canvas.height = img.height;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      throw new Error('Failed to get canvas 2D context');
    }

    // Move to center, rotate, then draw image
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate((currentRotation.value * Math.PI) / 180);
    ctx.drawImage(img, -img.width / 2, -img.height / 2);

    // Convert to blob and update preview
    canvas.toBlob((blob) => {
      if (!blob) return;

      // Revoke old rotated preview
      if (rotatedImagePreview.value && rotatedImagePreview.value.startsWith('blob:')) {
        URL.revokeObjectURL(rotatedImagePreview.value);
      }

      rotatedImagePreview.value = URL.createObjectURL(blob);

      // Update the cropper source - force re-render
      if (cropperRef.value) {
        cropperRef.value.refresh();
        // Reset zoom tracking after refresh (refresh resets zoom state)
        currentActualZoom.value = 1;
      }
    }, 'image/jpeg', 0.95);
  } catch (err) {
    console.error('Failed to rotate image:', err);
  }
}

function applyCrop(): void {
  if (cropperRef.value) {
    const { canvas } = cropperRef.value.getResult();

    if (canvas) {
      canvas.toBlob((blob) => {
        if (!blob) return;
        if (croppedImage.value) {
          URL.revokeObjectURL(croppedImage.value);
        }
        croppedImage.value = URL.createObjectURL(blob);

        // Update preview
        if (newPicturePreview.value && newPicturePreview.value !== croppedImage.value) {
          URL.revokeObjectURL(newPicturePreview.value);
        }
        newPicturePreview.value = croppedImage.value;

        // Clear filtered preview
        if (filteredPreview.value) {
          URL.revokeObjectURL(filteredPreview.value);
          filteredPreview.value = '';
        }

        // Switch to filters tab
        editTab.value = 'filters';
      }, 'image/jpeg', 0.95);
    }
  }
}

function resetUploadState(): void {
  // Clean up blob URLs
  if (newPicturePreview.value && newPicturePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(newPicturePreview.value);
  }
  if (filteredPreview.value && filteredPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(filteredPreview.value);
  }
  if (croppedImage.value && croppedImage.value.startsWith('blob:')) {
    URL.revokeObjectURL(croppedImage.value);
  }
  if (rotatedImagePreview.value && rotatedImagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(rotatedImagePreview.value);
  }

  // Reset state
  newPictureFile.value = null;
  newPictureName.value = '';
  newPicturePreview.value = '';
  filteredPreview.value = '';
  croppedImage.value = '';
  rotatedImagePreview.value = '';
  fileError.value = '';
  uploadStep.value = 1;
  selectedFilter.value = 'none';
  editTab.value = 'filters';
  cropZoomValue.value = 1;
  currentActualZoom.value = 1;
  currentRotation.value = 0;
  mainTab.value = 'gallery';
}

function onImageError(): void {
  error.value = true;
}

// Watchers
watch(newPictureFile, (file, oldFile) => {
  // Revoke old blob URL to prevent memory leak
  if (newPicturePreview.value && newPicturePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(newPicturePreview.value);
  }

  if (file && file instanceof File) {
    newPicturePreview.value = URL.createObjectURL(file);
  } else {
    newPicturePreview.value = '';
  }
});

watch(selectedFilter, (newFilter) => {
  // Clear existing timer to debounce rapid filter changes
  if (filterDebounceTimer) {
    clearTimeout(filterDebounceTimer);
  }

  // Debounce filter application to prevent excessive blob creation
  filterDebounceTimer = setTimeout(async () => {
    if (!newPicturePreview.value) return;

    const filter = filters.find(f => f.value === newFilter);
    if (!filter) return;

    try {
      // Create canvas to apply filter
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = newPicturePreview.value;

      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = () => reject(new Error('Failed to load image'));
      });

      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        throw new Error('Failed to get canvas 2D context');
      }

      if (filter.class) {
        ctx.filter = filter.class;
      }
      ctx.drawImage(img, 0, 0);

      canvas.toBlob((blob) => {
        if (!blob) return;

        // Revoke old blob URL before creating new one
        if (filteredPreview.value && filteredPreview.value.startsWith('blob:')) {
          URL.revokeObjectURL(filteredPreview.value);
        }

        filteredPreview.value = URL.createObjectURL(blob);
      }, 'image/jpeg', 0.95);
    } catch (err) {
      console.error('Failed to apply filter:', err);
      // Clear filtered preview on error
      if (filteredPreview.value && filteredPreview.value.startsWith('blob:')) {
        URL.revokeObjectURL(filteredPreview.value);
      }
      filteredPreview.value = '';
    }
  }, 150); // 150ms debounce delay
});

// Lifecycle
// Note: Pictures are fetched lazily when modal opens (in openModal function)
// This prevents unnecessary API calls and error messages on page load

onBeforeUnmount(() => {
  // Cancel any in-flight API requests
  if (fetchAbortController) {
    fetchAbortController.abort();
    fetchAbortController = null;
  }
  if (saveAbortController) {
    saveAbortController.abort();
    saveAbortController = null;
  }
  if (deleteAbortController) {
    deleteAbortController.abort();
    deleteAbortController = null;
  }

  // Clear debounce timer
  if (filterDebounceTimer) {
    clearTimeout(filterDebounceTimer);
    filterDebounceTimer = null;
  }

  // Clean up blob URLs
  if (newPicturePreview.value && newPicturePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(newPicturePreview.value);
  }
  if (filteredPreview.value && filteredPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(filteredPreview.value);
  }
  if (croppedImage.value && croppedImage.value.startsWith('blob:')) {
    URL.revokeObjectURL(croppedImage.value);
  }
  if (rotatedImagePreview.value && rotatedImagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(rotatedImagePreview.value);
  }
});
</script>

<style scoped lang="scss">
.hb-profile-picture-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.hb-profile-picture-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.hb-profile-picture-preview {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background-color: var(--gray-100);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Size variants */
.hb-profile-picture-container {
  &:has(.hb-profile-picture-preview) {
    .hb-profile-picture-preview {
      &.size-xs {
        width: 64px;
        height: 64px;
      }

      &.size-sm {
        width: 80px;
        height: 80px;
      }

      &.size-md {
        width: 96px;
        height: 96px;
      }

      &.size-lg {
        width: 128px;
        height: 128px;
      }

      &.size-xl {
        width: 160px;
        height: 160px;
      }
    }
  }
}

.hb-profile-picture-preview--clickable {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.hb-profile-picture-preview--clickable:hover {
  transform: scale(1.05);
}

.hb-profile-picture-preview--clickable:hover .hb-profile-picture-preview__edit-overlay {
  opacity: 1;
}

.hb-profile-picture-preview__image-container {
  width: 100%;
  height: 100%;
}

.hb-profile-picture-preview__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hb-profile-picture-preview__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--gray-400);
}

.hb-profile-picture-preview__loading {
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

.hb-profile-picture-preview__edit-overlay {
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
  transition: opacity 0.2s ease;
  font-size: 2rem;
  color: white;
}

.hb-profile-picture-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Main Tabs */
.profile-picture-main-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--gray-600);
}

.main-tab-btn {
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

.main-tab-btn:hover {
  color: var(--gray-200);
  background-color: var(--gray-700);
}

.main-tab-btn.active {
  color: var(--primary-400);
  border-bottom-color: var(--primary-400);
}

.profile-picture-tab-content {
  margin-top: 1rem;
}

/* Gallery Tab */
.gallery-tab {
  min-height: 300px;
}

.picture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.picture-card {
  border: 2px solid var(--gray-600);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: var(--gray-700);
}

.picture-card:hover {
  border-color: var(--primary-400);
  transform: translateY(-2px);
}

.picture-card.selected {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2);
}

.picture-card__image-container {
  position: relative;
  width: 100%;
  height: 150px;
  overflow: hidden;
}

.picture-card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.picture-card__selected-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(14, 165, 233, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.picture-card__default-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background-color: var(--primary-500);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

.picture-card__info {
  padding: 0.75rem;
}

.picture-card__name {
  display: block;
  color: var(--gray-200);
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.picture-card__actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem;
  background-color: var(--gray-600);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--gray-300);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: var(--gray-500);
}

.action-btn--default:hover {
  color: var(--warning-400);
}

.action-btn--delete:hover {
  color: var(--danger-400);
}

/* Upload Tab */
.upload-tab {
  min-height: 300px;
}

.upload-step,
.edit-step {
  padding: 1rem 0;
}

/* Dropzone (copied from HbAvatar) */
.hb-file-image__dropzone {
  border: 2px dashed var(--primary-500);
  border-radius: var(--radius-md);
  padding: var(--spacing-6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 200px;
}

.hb-file-image__dropzone:hover {
  border-color: var(--primary-400);
  background-color: rgba(14, 165, 233, 0.05);
}

.hb-file-image__dropzone--dragging {
  border-color: var(--primary-500);
  background-color: rgba(14, 165, 233, 0.1);
}

.hb-file-image__dropzone--disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: var(--gray-500);
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
  margin-bottom: 1rem;
}

.hb-file-image__text {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hb-file-image__primary-text {
  font-weight: 500;
  color: var(--gray-300);
  margin-bottom: 0.5rem;
}

.hb-file-image__secondary-text {
  color: var(--primary-500);
  font-size: 0.875rem;
}

/* Edit Step */
.edit-step {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.edit-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--gray-900);
  border-radius: var(--radius-lg);
  padding: 2rem;
  min-height: 300px;
}

.edit-preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: var(--radius-lg);
  object-fit: contain;
  transition: filter 0.3s ease, transform 0.3s ease;
}

/* Edit Tabs */
.edit-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--gray-600);
}

.edit-tab-btn {
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

.edit-tab-btn:hover {
  color: var(--gray-200);
  background-color: var(--gray-700);
}

.edit-tab-btn.active {
  color: var(--primary-400);
  border-bottom-color: var(--primary-400);
}

.edit-tab-content {
  margin-top: 1rem;
}

/* Filters Content */
.filters-content {
  margin-top: 1rem;
}

.filter-grid {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.filter-option {
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  padding: 0.5rem;
  transition: all 0.2s ease;
  text-align: center;
  flex-shrink: 0;
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
  background-color: var(--gray-800);
}

.filter-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.filter-label {
  font-size: 0.75rem;
  color: var(--gray-300);
  font-weight: 500;
  display: block;
}

.filter-option.active .filter-label {
  color: var(--primary-400);
}

/* Crop Content */
.crop-content {
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

/* Cropper styling */
:deep(.vue-advanced-cropper__background),
:deep(.vue-advanced-cropper__foreground) {
  background-color: var(--gray-900);
}

/* Grid lines for crop guides */
:deep(.vue-line) {
  border-color: rgba(255, 255, 255, 0.4);
  border-style: solid;
}

:deep(.vue-line--horizontal) {
  border-top-width: 1px;
}

:deep(.vue-line--vertical) {
  border-left-width: 1px;
}

/* Corner handles for resizing */
:deep(.vue-handler) {
  background: var(--primary-500);
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
}

:deep(.vue-handler:hover) {
  background: var(--primary-400);
  transform: scale(1.2);
}

/* Stencil border */
:deep(.vue-simple-handler-wrapper__draggable) {
  border: 2px solid var(--primary-500);
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
}

/* Controls */
.edit-controls {
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

.apply-crop-section {
  margin-top: 0.5rem;
}

/* Crop instructions */
.crop-instructions {
  padding: 0.75rem 1rem;
  background-color: var(--gray-800);
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
  border-left: 3px solid var(--primary-500);
}

.crop-instructions p {
  margin: 0;
  display: flex;
  align-items: center;
}
</style>
