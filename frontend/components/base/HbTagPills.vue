<template>
  <div class="hb-tag-pills" :class="{ 'hb-tag-pills--inline': inline }">
    <div 
      v-for="(tag, index) in tags" 
      :key="index"
      class="hb-tag-pill"
      :class="[
        `hb-tag-pill--${size}`,
        `hb-tag-pill--${variant}`,
        { 'hb-tag-pill--removable': removable },
        { 'hb-tag-pill--rounded': rounded },
        { 'hb-tag-pill--solid': solid }
      ]"
    >
      <slot name="prefix" :tag="tag" v-if="$slots.prefix"></slot>
      
      <span class="hb-tag-pill__label">
        <slot name="tag" :tag="tag">
          {{ typeof tag === 'object' ? tag.label || tag.name || tag.value : tag }}
        </slot>
      </span>
      
      <button 
        v-if="removable" 
        class="hb-tag-pill__remove"
        @click.stop="handleRemove(index, tag)"
        type="button"
        aria-label="Remove tag"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5">
          <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
        </svg>
      </button>
    </div>
    
    <slot name="empty" v-if="!tags || tags.length === 0"></slot>
    
    <div v-if="addable" class="hb-tag-pill hb-tag-pill--add" :class="`hb-tag-pill--${size}`">
      <slot name="add-button">
        <button 
          @click="$emit('add')" 
          type="button"
          class="hb-tag-pill__add"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 mr-1">
            <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
          </svg>
          Add
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

interface Tag {
  label?: string
  name?: string
  value?: string
}

interface RemovePayload {
  index: number
  tag: Tag | string
}

interface Props {
  tags?: (Tag | string)[]
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'gray'
  solid?: boolean
  rounded?: boolean
  size?: 'sm' | 'md' | 'lg'
  removable?: boolean
  addable?: boolean
  inline?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  tags: () => [],
  variant: 'primary',
  solid: false,
  rounded: false,
  size: 'md',
  removable: false,
  addable: false,
  inline: true
})

const emit = defineEmits<{
  'remove': [payload: RemovePayload]
  'add': []
}>()

const handleRemove = (index: number, tag: Tag | string): void => {
  emit('remove', { index, tag })
}
</script>

<style scoped>
.hb-tag-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.hb-tag-pills--inline {
  display: inline-flex;
}

.hb-tag-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  font-family: var(--font-body);
  font-weight: var(--font-medium);
  white-space: nowrap;
  border-radius: var(--radius-full);
  transition: all 0.2s ease;
  user-select: none;
}

/* Sizes */
.hb-tag-pill--sm {
  font-size: var(--text-xs);
  padding: 0.125rem 0.5rem;
  line-height: 1.2;
}

.hb-tag-pill--md {
  font-size: var(--text-xs);
  padding: 0.25rem 0.625rem;
  line-height: 1.2;
}

.hb-tag-pill--lg {
  font-size: var(--text-sm);
  padding: 0.375rem 0.75rem;
  line-height: 1.2;
}

/* Removable */
.hb-tag-pill--removable {
  padding-right: 0.375rem;
}

.hb-tag-pill__remove {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.25rem;
  color: currentColor;
  opacity: 0.7;
  transition: opacity 0.2s ease;
  cursor: pointer;
}

.hb-tag-pill__remove:hover {
  opacity: 1;
}

/* Add button */
.hb-tag-pill--add {
  background-color: transparent;
  border: 1px dashed var(--gray-300);
  color: var(--gray-600);
  cursor: pointer;
}

.hb-tag-pill--add:hover {
  border-color: var(--gray-400);
  color: var(--gray-700);
  background-color: var(--gray-50);
}

.hb-tag-pill__add {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

/* Variants */
/* Primary */
.hb-tag-pill--primary {
  background-color: var(--primary-100);
  color: var(--primary-700);
}

.hb-tag-pill--primary.hb-tag-pill--solid {
  background-color: var(--primary-600);
  color: white;
}

/* Secondary */
.hb-tag-pill--secondary {
  background-color: var(--secondary-100);
  color: var(--secondary-700);
}

.hb-tag-pill--secondary.hb-tag-pill--solid {
  background-color: var(--secondary-600);
  color: white;
}

/* Success */
.hb-tag-pill--success {
  background-color: var(--success-100);
  color: var(--success-700);
}

.hb-tag-pill--success.hb-tag-pill--solid {
  background-color: var(--success-600);
  color: white;
}

/* Danger */
.hb-tag-pill--danger {
  background-color: var(--danger-100);
  color: var(--danger-700);
}

.hb-tag-pill--danger.hb-tag-pill--solid {
  background-color: var(--danger-600);
  color: white;
}

/* Warning */
.hb-tag-pill--warning {
  background-color: var(--warning-100);
  color: var(--warning-700);
}

.hb-tag-pill--warning.hb-tag-pill--solid {
  background-color: var(--warning-600);
  color: white;
}

/* Info */
.hb-tag-pill--info {
  background-color: var(--info-100);
  color: var(--info-700);
}

.hb-tag-pill--info.hb-tag-pill--solid {
  background-color: var(--info-600);
  color: white;
}

/* Gray */
.hb-tag-pill--gray {
  background-color: var(--gray-100);
  color: var(--gray-700);
}

.hb-tag-pill--gray.hb-tag-pill--solid {
  background-color: var(--gray-600);
  color: white;
}

/* Rounded variant */
.hb-tag-pill--rounded {
  border-radius: 0.375rem;
}
</style>
