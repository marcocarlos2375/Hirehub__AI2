<template>
  <nav class="hb-breadcrumbs" :class="[`hb-breadcrumbs--${size}`, { 'hb-breadcrumbs--truncate': truncate, 'hb-breadcrumbs--white': appearance === 'white' }]" aria-label="Breadcrumb">
    <ol class="hb-breadcrumbs__list">
      <li 
        v-for="(item, index) in items" 
        :key="index" 
        class="hb-breadcrumbs__item"
        :class="{ 'hb-breadcrumbs__item--active': index === items.length - 1 }"
      >
        <div class="hb-breadcrumbs__content">
          <!-- Render as link if item has URL, otherwise as span -->
          <!-- NOTE: Replace NuxtLink with your router component (RouterLink for vue-router, <a> for plain HTML) -->
          <NuxtLink
            v-if="item.url"
            :to="item.url"
            class="hb-breadcrumbs__link"
            :class="{ 'hb-breadcrumbs__link--active': index === items.length - 1 }"
          >
            <!-- Icon slot for each item -->
            <span v-if="item.icon || $slots[`icon-${index}`]" class="hb-breadcrumbs__icon">
              <slot :name="`icon-${index}`">
                <component :is="item.icon" v-if="item.icon" />
              </slot>
            </span>
            
            <!-- Item text -->
            <span class="hb-breadcrumbs__text">{{ item.text }}</span>
          </NuxtLink>
          
          <span 
            v-else
            class="hb-breadcrumbs__link"
            :class="{ 'hb-breadcrumbs__link--active': index === items.length - 1 }"
          >
            <!-- Icon slot for each item -->
            <span v-if="item.icon || $slots[`icon-${index}`]" class="hb-breadcrumbs__icon">
              <slot :name="`icon-${index}`">
                <component :is="item.icon" v-if="item.icon" />
              </slot>
            </span>
            
            <!-- Item text -->
            <span class="hb-breadcrumbs__text">{{ item.text }}</span>
          </span>
        </div>
        
        <!-- Separator between items -->
        <span v-if="index < items.length - 1" class="hb-breadcrumbs__separator" aria-hidden="true">
          <slot name="separator">/</slot>
        </span>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
// @ts-strict
import type { Component } from 'vue'

type BreadcrumbSize = 'sm' | 'md' | 'lg'
type BreadcrumbAppearance = 'default' | 'white'

interface BreadcrumbItem {
  text: string
  url?: string
  icon?: Component
}

interface Props {
  /**
   * Array of breadcrumb items
   * Each item should have:
   * - text: String (required) - The text to display
   * - url: String (optional) - The URL to navigate to when clicked
   * - icon: Component (optional) - Icon component to display before the text
   */
  items: BreadcrumbItem[]

  /**
   * Size variant of the breadcrumbs
   */
  size?: BreadcrumbSize

  /**
   * Whether to truncate long breadcrumb items
   */
  truncate?: boolean

  /**
   * Appearance variant of the breadcrumbs
   */
  appearance?: BreadcrumbAppearance
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  truncate: false,
  appearance: 'default'
});
</script>

<style lang="scss" scoped>
.hb-breadcrumbs {
  width: 100%;
  font-family: var(--font-heading);
  &__list {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    padding: 0;
    margin: 0;
    list-style: none;
  }
  
  &__item {
    display: flex;
    align-items: center;
    
    &:last-child {
      overflow-wrap: break-word;
      word-break: break-word;
    }
  }
  
  &__content {
    display: flex;
    align-items: center;
  }
  
  &__link {
    display: inline-flex;
    align-items: center;
    font-size: var(--text-sm);
    color: var(--gray-600);
    text-decoration: none;
    padding: var(--spacing-1) var(--spacing-2);
    border-radius: var(--radius-md);
    transition: all var(--transition-normal) var(--transition-ease);
    
    &:hover:not(&--active) {
      color: var(--primary-600);
      
    }
    
    &--active {
      color: var(--gray-900);
      font-weight: var(--font-medium);
      cursor: default;
    }
  }
  
  &__icon {
    display: inline-flex;
    margin-right: var(--spacing-1);
    
    svg {
      width: 1rem;
      height: 1rem;
    }
  }
  
  &__separator {
    display: flex;
    align-items: center;
    color: var(--gray-400);
    margin: 0 var(--spacing-1);
    
    &-icon {
      width: 1rem;
      height: 1rem;
    }
  }
  
  /* Size variants */
  &--sm {
    .hb-breadcrumbs__link {
      font-size: var(--text-xs);
      padding: var(--spacing-0-5) var(--spacing-1);
    }
    
    .hb-breadcrumbs__separator-icon,
    .hb-breadcrumbs__icon svg {
      width: 0.875rem;
      height: 0.875rem;
    }
  }
  
  &--lg {
    .hb-breadcrumbs__link {
      font-size: var(--text-base);
      padding: var(--spacing-1-5) var(--spacing-3);
    }
    
    .hb-breadcrumbs__separator-icon,
    .hb-breadcrumbs__icon svg {
      width: 1.25rem;
      height: 1.25rem;
    }
  }
  
  /* Truncate option */
  &--truncate {
    .hb-breadcrumbs__text {
      max-width: 200px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
  
  /* Appearance variants */
  &--white {
    .hb-breadcrumbs__link {
      color: rgba(255, 255, 255, 0.8);
      
      &:hover:not(&--active) {
        color: white;
        background-color: rgba(255, 255, 255, 0.1);
      }
      
      &--active {
        color: white;
        font-weight: var(--font-medium);
      }
    }
    
    .hb-breadcrumbs__separator {
      color: rgba(255, 255, 255, 0.6);
    }
  }
}
</style>
