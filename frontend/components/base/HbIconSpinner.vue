<template>
  <div
    class="hb-icon-spinner"
    :class="[size, color]"
  >
    <div class="hb-icon-spinner__ring"></div>
    <div class="hb-icon-spinner__icon">
      <slot>
        <!-- Default lock icon if no icon is provided -->
        <svg v-if="icon === 'lock'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path fill-rule="evenodd" d="M12 1.5a5.25 5.25 0 00-5.25 5.25v3a3 3 0 00-3 3v6.75a3 3 0 003 3h10.5a3 3 0 003-3v-6.75a3 3 0 00-3-3v-3c0-2.9-2.35-5.25-5.25-5.25zm3.75 8.25v-3a3.75 3.75 0 10-7.5 0v3h7.5z" clip-rule="evenodd" />
        </svg>
        <svg v-else-if="icon === 'shield'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path fill-rule="evenodd" d="M12.516 2.17a.75.75 0 00-1.032 0 11.209 11.209 0 01-7.877 3.08.75.75 0 00-.722.515A12.74 12.74 0 002.25 9.75c0 5.942 4.064 10.933 9.563 12.348a.75.75 0 00.674 0c5.499-1.415 9.563-6.406 9.563-12.348 0-1.39-.223-2.73-.635-3.985a.75.75 0 00-.722-.516l-.143.001c-2.996 0-5.717-1.17-7.734-3.08zm3.094 8.016a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd" />
        </svg>
        <svg v-else-if="icon === 'check'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd" />
        </svg>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

interface Props {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl' | 'xxxl'
  color?: 'primary' | 'secondary' | 'white' | 'black' | 'danger'
  icon?: 'lock' | 'shield' | 'check' | 'custom'
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'primary',
  icon: 'lock'
})
</script>

<style lang="scss" scoped>
.hb-icon-spinner {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  
  &__ring {
    position: absolute;
    border: 3px rgba(var(--primary-500-rgb), 0.25) solid;
    border-top: 3px rgba(var(--primary-500-rgb), 1) solid;
    border-radius: 50%;
    animation: spinnerRotation 0.6s infinite linear;
    width: 100%;
    height: 100%;
  }
  
  &__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
    width: 50%;
    height: 50%;
    color: inherit;
    
    svg {
      width: 100%;
      height: 100%;
    }
  }

  // Colors
  &.primary {
    color: var(--primary-600);
    
    .hb-icon-spinner__ring {
      border: 3px rgba(var(--primary-500-rgb), 0.25) solid;
      border-top: 3px rgba(var(--primary-500-rgb), 1) solid;
    }
  }

  &.secondary {
    color: var(--secondary-600);
    
    .hb-icon-spinner__ring {
      border: 3px rgba(var(--secondary-500-rgb), 0.25) solid;
      border-top: 3px rgba(var(--secondary-500-rgb), 1) solid;
    }
  }

  &.danger {
    color: var(--danger-600);
    
    .hb-icon-spinner__ring {
      border: 3px rgba(var(--danger-500-rgb), 0.25) solid;
      border-top: 3px rgba(var(--danger-500-rgb), 1) solid;
    }
  }

  &.white {
    color: white;
    
    .hb-icon-spinner__ring {
      border: 3px rgba(255, 255, 255, 0.25) solid;
      border-top: 3px rgba(255, 255, 255, 1) solid;
    }
  }

  &.black {
    color: black;
    
    .hb-icon-spinner__ring {
      border: 3px rgba(0, 0, 0, 0.25) solid;
      border-top: 3px rgba(0, 0, 0, 1) solid;
    }
  }

  // Sizes
  &.xs {
    width: 24px;
    height: 24px;
    
    .hb-icon-spinner__ring {
      border-width: 2px;
    }
  }
  
  &.sm {
    width: 32px;
    height: 32px;
    
    .hb-icon-spinner__ring {
      border-width: 2px;
    }
  }

  &.md {
    width: 40px;
    height: 40px;
    
    .hb-icon-spinner__ring {
      border-width: 3px;
    }
  }

  &.lg {
    width: 56px;
    height: 56px;
    
    .hb-icon-spinner__ring {
      border-width: 3px;
    }
  }

  &.xl {
    width: 72px;
    height: 72px;
    
    .hb-icon-spinner__ring {
      border-width: 4px;
    }
  }

  &.xxl {
    width: 96px;
    height: 96px;
    
    .hb-icon-spinner__ring {
      border-width: 4px;
    }
  }

  &.xxxl {
    width: 128px;
    height: 128px;
    
    .hb-icon-spinner__ring {
      border-width: 5px;
    }
  }
}

@keyframes spinnerRotation {
  from { transform: rotate(0deg); }
  to { transform: rotate(359deg); }
}
</style>
