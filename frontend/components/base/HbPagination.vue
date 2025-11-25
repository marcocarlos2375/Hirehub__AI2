<template>
  <nav class="hb-pagination" :class="[`hb-pagination--${size}`]" aria-label="Pagination">
    <ul class="hb-pagination__list">
      <!-- Previous Button -->
      <li class="hb-pagination__item">
        <button
          class="hb-pagination__button hb-pagination__button--nav"
          :class="{ 'hb-pagination__button--disabled': currentPage <= 1 }"
          :disabled="currentPage <= 1"
          @click="updatePage(currentPage - 1)"
          aria-label="Previous page"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="hb-pagination__icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
      </li>

      <!-- First Page (always visible) -->
      <li v-if="showFirstLastButtons && currentPage > 3" class="hb-pagination__item">
        <button
          class="hb-pagination__button"
          :class="{ 'hb-pagination__button--active': currentPage === 1 }"
          @click="updatePage(1)"
        >
          1
        </button>
      </li>

      <!-- Ellipsis (if needed) -->
      <li v-if="showFirstLastButtons && currentPage > 4" class="hb-pagination__item">
        <span class="hb-pagination__ellipsis">...</span>
      </li>

      <!-- Page Numbers -->
      <li
        v-for="page in visiblePageNumbers"
        :key="page"
        class="hb-pagination__item"
      >
        <button
          class="hb-pagination__button"
          :class="{ 'hb-pagination__button--active': currentPage === page }"
          @click="updatePage(page)"
        >
          {{ page }}
        </button>
      </li>

      <!-- Ellipsis (if needed) -->
      <li v-if="showFirstLastButtons && currentPage < totalPages - 3" class="hb-pagination__item">
        <span class="hb-pagination__ellipsis">...</span>
      </li>

      <!-- Last Page (always visible) -->
      <li v-if="showFirstLastButtons && currentPage < totalPages - 2" class="hb-pagination__item">
        <button
          class="hb-pagination__button"
          :class="{ 'hb-pagination__button--active': currentPage === totalPages }"
          @click="updatePage(totalPages)"
        >
          {{ totalPages }}
        </button>
      </li>

      <!-- Next Button -->
      <li class="hb-pagination__item">
        <button
          class="hb-pagination__button hb-pagination__button--nav"
          :class="{ 'hb-pagination__button--disabled': currentPage >= totalPages }"
          :disabled="currentPage >= totalPages"
          @click="updatePage(currentPage + 1)"
          aria-label="Next page"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="hb-pagination__icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
      </li>
    </ul>
    
    <!-- Page Size Selector -->
    <div v-if="showPageSizeSelector" class="hb-pagination__size-selector">
      <span class="hb-pagination__size-label">Per page:</span>
      <HbSelect
        v-model="pageSizeValue"
        :options="pageSizeOptionsFormatted"
        placeholder="Select size"
        :clearable="false"
        optionLabel="label"
      />
    </div>
  </nav>
</template>

<script setup lang="ts">
// @ts-strict
import { computed } from 'vue'
import HbSelect from './HbSelect.vue'

interface PageSizeOption extends Record<string, unknown> {
  label: string
  value: number
  disabled?: boolean
}

interface Props {
  currentPage?: number
  totalPages?: number
  size?: 'sm' | 'md' | 'lg'
  maxVisiblePages?: number
  showFirstLastButtons?: boolean
  showPageSizeSelector?: boolean
  pageSize?: number
  pageSizeOptions?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  currentPage: 1,
  totalPages: 1,
  size: 'md',
  maxVisiblePages: 5,
  showFirstLastButtons: true,
  showPageSizeSelector: false,
  pageSize: 10,
  pageSizeOptions: () => [10, 20, 50, 100]
})

const emit = defineEmits<{
  'update:currentPage': [page: number]
  'update:pageSize': [size: number]
}>()

const updatePage = (page: number): void => {
  if (page < 1 || page > props.totalPages) return
  emit('update:currentPage', page)
}

const pageSizeOptionsFormatted = computed<PageSizeOption[]>(() => {
  return props.pageSizeOptions.map(size => ({
    label: size.toString(),
    value: size
  }))
})

const pageSizeValue = computed<PageSizeOption>({
  get: () => {
    const option = pageSizeOptionsFormatted.value.find(opt => opt.value === props.pageSize)
    return option || pageSizeOptionsFormatted.value[0]
  },
  set: (newValue: PageSizeOption) => {
    if (newValue && newValue.value) {
      emit('update:pageSize', parseInt(newValue.value.toString(), 10))
    }
  }
})

const visiblePageNumbers = computed<number[]>(() => {
  const halfVisiblePages = Math.floor(props.maxVisiblePages / 2)
  let startPage = Math.max(props.currentPage - halfVisiblePages, 1)
  let endPage = Math.min(startPage + props.maxVisiblePages - 1, props.totalPages)

  if (endPage - startPage + 1 < props.maxVisiblePages) {
    startPage = Math.max(endPage - props.maxVisiblePages + 1, 1)
  }

  const pages: number[] = []
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return pages
})
</script>

<style>
.hb-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.hb-pagination__list {
  display: flex;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
  gap: var(--spacing-1);
}

.hb-pagination__item {
  display: inline-flex;
}

.hb-pagination__button {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--gray-200);
  background-color: white;
  color: var(--gray-700);
  font-weight: var(--font-medium);
  border-radius: var(--radius-md);
  font-family: var(--font-heading);
  cursor: pointer;
  transition: all var(--transition-duration) var(--transition-ease);
}

.hb-pagination__button:hover:not(.hb-pagination__button--disabled):not(.hb-pagination__button--active) {
  background-color: var(--gray-50);
  border-color: var(--gray-300);
}

.hb-pagination__button--active {
  background-color: var(--primary-500);
  border-color: var(--primary-500);
  color: white;
}

.hb-pagination__button--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hb-pagination__button--nav {
  display: flex;
  align-items: center;
  justify-content: center;
}

.hb-pagination__icon {
  width: 1.25rem;
  height: 1.25rem;
}

.hb-pagination__ellipsis {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gray-500);
  padding: 0 var(--spacing-2);
}

/* Size Variants */
.hb-pagination--sm .hb-pagination__button {
  min-width: 2rem;
  height: 2rem;
  font-size: var(--text-sm);
}

.hb-pagination--sm .hb-pagination__icon {
  width: 1rem;
  height: 1rem;
}

.hb-pagination--md .hb-pagination__button {
  min-width: 2.5rem;
  height: 2.5rem;
  font-size: var(--text-base);
}

.hb-pagination--lg .hb-pagination__button {
  min-width: 3rem;
  height: 3rem;
  font-size: var(--text-lg);
}

.hb-pagination--lg .hb-pagination__icon {
  width: 1.5rem;
  height: 1.5rem;
}

/* Page Size Selector */
.hb-pagination__size-selector {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.hb-pagination__size-label {
  font-size: var(--text-sm);
  color: var(--gray-600);
}

/* HbSelect styling in pagination context */
.hb-pagination__size-selector :deep(.hb-select) {
  width: 80px;
}

.hb-pagination__size-selector :deep(.hb-select__selection) {
  min-height: 2.5rem;
  padding: var(--spacing-1) var(--spacing-2);
}

.hb-pagination--sm .hb-pagination__size-selector :deep(.hb-select__selection) {
  min-height: 2rem;
}

.hb-pagination--lg .hb-pagination__size-selector :deep(.hb-select__selection) {
  min-height: 3rem;
}
</style>
