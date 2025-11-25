<template>
  <div class="hb-sidebar-wrapper">
    <!-- Backdrop for mobile - only visible when sidebar is open on mobile -->
    <div 
      v-if="isOpen && !persistent" 
      class="hb-sidebar-backdrop" 
      @click="closeSidebar"
    ></div>
    
    <!-- Sidebar container -->
    <aside 
      class="hb-sidebar"
      :class="[
        `hb-sidebar--${position}`,
        `hb-sidebar--${size}`,
        { 'hb-sidebar--open': isOpen },
        { 'hb-sidebar--persistent': persistent },
        { 'hb-sidebar--with-header': showHeader },
        { 'hb-sidebar--with-footer': $slots.footer }
      ]"
    >
      <!-- Header section -->
      <div v-if="showHeader" class="hb-sidebar__header">
        <div class="hb-sidebar__title">
          <slot name="title">
            <h3>{{ title }}</h3>
          </slot>
        </div>
        
        <button 
          v-if="!persistent" 
          class="hb-sidebar__close" 
          @click="closeSidebar"
          aria-label="Close sidebar"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
            <path fill-rule="evenodd" d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
      
      <!-- Main content section -->
      <div class="hb-sidebar__content">
        <slot></slot>
      </div>
      
      <!-- Footer section -->
      <div v-if="$slots.footer" class="hb-sidebar__footer">
        <slot name="footer"></slot>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

interface Props {
  modelValue?: boolean
  title?: string
  showHeader?: boolean
  position?: 'left' | 'right'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  persistent?: boolean
  closeOnClickOutside?: boolean
  closeOnEsc?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  title: '',
  showHeader: true,
  position: 'left',
  size: 'md',
  persistent: false,
  closeOnClickOutside: true,
  closeOnEsc: true
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// Internal state to track sidebar open/closed state
const isOpen = ref<boolean>(props.modelValue)

// Watch for changes to the modelValue prop
watch(() => props.modelValue, (newValue: boolean) => {
  isOpen.value = newValue

  // When sidebar opens, add a class to prevent scrolling on the body
  if (newValue && !props.persistent) {
    document.body.classList.add('hb-sidebar-open')
  } else {
    document.body.classList.remove('hb-sidebar-open')
  }
})

// Close the sidebar
const closeSidebar = (): void => {
  isOpen.value = false
  emit('update:modelValue', false)
}

// Handle escape key press
const handleEscKey = (event: KeyboardEvent): void => {
  if (props.closeOnEsc && event.key === 'Escape' && isOpen.value && !props.persistent) {
    closeSidebar()
  }
}

// Handle click outside
const handleClickOutside = (event: MouseEvent): void => {
  // If the sidebar is open, not persistent, and closeOnClickOutside is true
  if (isOpen.value && !props.persistent && props.closeOnClickOutside) {
    // Check if the click was outside the sidebar
    const sidebar = document.querySelector('.hb-sidebar')
    if (sidebar && !sidebar.contains(event.target as Node)) {
      closeSidebar()
    }
  }
}

// Set up event listeners
onMounted(() => {
  document.addEventListener('keydown', handleEscKey)

  // Apply initial body class if sidebar is open
  if (isOpen.value && !props.persistent) {
    document.body.classList.add('hb-sidebar-open')
  }
})

// Clean up event listeners
onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleEscKey)
  document.body.classList.remove('hb-sidebar-open')
})
</script>

<style lang="scss" scoped>
.hb-sidebar-wrapper {
  position: relative;
  height: 100%;
}

.hb-sidebar-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: var(--z-40);
  transition: opacity var(--transition-normal) var(--transition-ease);
}

.hb-sidebar {
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  bottom: 0;
  background-color: var(--white);
  z-index: var(--z-50);
  transition: transform var(--transition-normal) var(--transition-ease);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  
  // Position variants
  &--left {
    left: 0;
    transform: translateX(-100%);
  }
  
  &--right {
    right: 0;
    transform: translateX(100%);
  }
  
  // Size variants
  &--sm {
    width: 250px;
  }
  
  &--md {
    width: 320px;
  }
  
  &--lg {
    width: 400px;
  }
  
  &--xl {
    width: 480px;
  }
  
  // State variants
  &--open {
    transform: translateX(0);
  }
  
  &--persistent {
    position: relative;
    transform: translateX(0);
    box-shadow: none;
    border-right: 1px solid var(--gray-200);
    
    &.hb-sidebar--right {
      border-right: none;
      border-left: 1px solid var(--gray-200);
    }
  }
  
  // Header
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-4);
    border-bottom: 1px solid var(--gray-200);
    min-height: 64px;
  }
  
  &__title {
    font-weight: var(--font-medium);
    font-size: var(--text-lg);
    color: var(--gray-900);
  }
  
  &__close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--radius-full);
    color: var(--gray-500);
    background: transparent;
    border: none;
    cursor: pointer;
    transition: background-color var(--transition-normal) var(--transition-ease);
    
    &:hover {
      background-color: var(--gray-100);
      color: var(--gray-700);
    }
  }
  
  // Content
  &__content {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-4);
  }
  
  // Footer
  &__footer {
    padding: var(--spacing-4);
    border-top: 1px solid var(--gray-200);
  }
}

// Add responsive styles for mobile
@media (max-width: 768px) {
  .hb-sidebar {
    &--sm, &--md, &--lg, &--xl {
      width: 85%;
    }
  }
}

// Global styles (will be added to <style> block in the layout)
:global(.hb-sidebar-open) {
  overflow: hidden;
}
</style>
