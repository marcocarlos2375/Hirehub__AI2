<template>
  <div class="hb-table-container" :class="{ 'hb-table--loading': loading }">
    <!-- Table -->
    <table class="hb-table" :class="tableClasses">
      <!-- Table Header -->
      <thead class="hb-table__header">
        <tr>
          <!-- Selection Column -->
          <th v-if="selectable" class="hb-table__th hb-table__th--checkbox">
            <div class="hb-table__th-content hb-table__checkbox-wrapper">
              <HbSingleCheckbox
                :modelValue="allSelected"
                @update:modelValue="toggleSelectAll"
                :indeterminate="someSelected && !allSelected"
              />
            </div>
          </th>
          
          <!-- Regular Columns -->
          <th 
            v-for="column in visibleColumns" 
            :key="column.key"
            class="hb-table__th"
            :class="[
              column.sortable ? 'hb-table__th--sortable' : '',
              sortBy === column.key ? `hb-table__th--sorted-${sortDirection}` : ''
            ]"
            @click="column.sortable && sort(column.key)"
          >
            <div class="hb-table__th-content">
              {{ column.label }}
              
              <!-- Sort Icon -->
              <span v-if="column.sortable" class="hb-table__sort-icon">
                <svg v-if="sortBy === column.key && sortDirection === 'asc'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                  <path fill-rule="evenodd" d="M10 5a.75.75 0 01.75.75v6.638l1.96-2.158a.75.75 0 111.08 1.04l-3.25 3.5a.75.75 0 01-1.08 0l-3.25-3.5a.75.75 0 111.08-1.04l1.96 2.158V5.75A.75.75 0 0110 5z" clip-rule="evenodd" />
                </svg>
                <svg v-else-if="sortBy === column.key && sortDirection === 'desc'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                  <path fill-rule="evenodd" d="M10 15a.75.75 0 01-.75-.75V7.612L7.29 9.77a.75.75 0 01-1.08-1.04l3.25-3.5a.75.75 0 011.08 0l3.25 3.5a.75.75 0 11-1.08 1.04l-1.96-2.158v6.638A.75.75 0 0110 15z" clip-rule="evenodd" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5 opacity-30">
                  <path fill-rule="evenodd" d="M10 3a.75.75 0 01.55.24l3.25 3.5a.75.75 0 11-1.1 1.02L10 4.852 7.3 7.76a.75.75 0 01-1.1-1.02l3.25-3.5A.75.75 0 0110 3zm-3.76 9.2a.75.75 0 011.06.04l2.7 2.908 2.7-2.908a.75.75 0 111.1 1.02l-3.25 3.5a.75.75 0 01-1.1 0l-3.25-3.5a.75.75 0 01.04-1.06z" clip-rule="evenodd" />
                </svg>
              </span>
            </div>
          </th>
          
          <!-- Actions Column -->
          <th v-if="hasActions" class="hb-table__th hb-table__th--actions">
            <div class="hb-table__th-content">
              Actions
            </div>
          </th>
        </tr>
      </thead>
      
      <!-- Table Body -->
      <tbody class="hb-table__body">
        <!-- Empty State -->
        <tr v-if="displayedData.length === 0 && !loading" class="hb-table__empty-row">
          <td :colspan="totalColumns" class="hb-table__empty-cell">
            <div class="hb-table__empty-content">
              <slot name="empty">
                <div class="hb-table__empty-message">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                  </svg>
                  <p>{{ emptyText }}</p>
                </div>
              </slot>
            </div>
          </td>
        </tr>
        
        <!-- Data Rows -->
        <tr 
          v-for="(item, index) in displayedData" 
          :key="rowKey ? item[rowKey] : index"
          class="hb-table__row"
          :class="{ 
            'hb-table__row--selected': isSelected(item),
            'hb-table__row--striped': striped && index % 2 === 1,
            'hb-table__row--clickable': rowClickable
          }"
          @click="rowClickable && onRowClick(item)"
        >
          <!-- Selection Cell -->
          <td v-if="selectable" class="hb-table__td hb-table__td--checkbox" @click.stop>
            <div class="hb-table__checkbox-wrapper">
              <HbSingleCheckbox
                :modelValue="isSelected(item)"
                @update:modelValue="() => toggleSelect(item)"
              />
            </div>
          </td>
          
          <!-- Data Cells -->
          <td 
            v-for="column in visibleColumns" 
            :key="column.key"
            class="hb-table__td"
            :class="column.cellClass"
          >
            <!-- Custom Cell Template -->
            <slot :name="`cell-${column.key}`" :item="item" :value="getValue(item, column.key)">
              {{ formatValue(getValue(item, column.key), column.format) }}
            </slot>
          </td>
          
          <!-- Actions Cell -->
          <td v-if="hasActions" class="hb-table__td hb-table__td--actions" @click.stop>
            <slot name="actions" :item="item" :index="index"></slot>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- Loading Overlay -->
    <div v-if="loading" class="hb-table__loading-overlay">
      <HbSpinner :size="'lg'" color="primary" />
    </div>
    
    <!-- Pagination -->
    <div v-if="pagination" class="hb-table__pagination">
      <HbPagination
        :currentPage="currentPageSync"
        :pageSize="pageSizeSync"
        :totalPages="totalPages"
        :showPageSizeSelector="showPageSizeSelector"
        :pageSizeOptions="pageSizeOptions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { computed, ref, watch, useSlots } from 'vue'
import HbSpinner from './HbSpinner.vue'
import HbPagination from './HbPagination.vue'
import HbSingleCheckbox from './HbSingleCheckbox.vue'

interface Props {
  data: Record<string, any>[]
  columns: Column[]
  rowKey?: string
  striped?: boolean
  bordered?: boolean
  hoverable?: boolean
  compact?: boolean
  selectable?: boolean
  rowClickable?: boolean
  loading?: boolean
  sortable?: boolean
  defaultSortBy?: string
  defaultSortDirection?: 'asc' | 'desc'
  pagination?: boolean
  currentPage?: number
  pageSize?: number
  pageSizeOptions?: number[]
  showPageSizeSelector?: boolean
  totalItems?: number | null
  emptyText?: string
}

interface Column {
  key: string
  label: string
  sortable?: boolean
  hidden?: boolean
  cellClass?: string
  format?: string | ((value: any) => string)
}

interface Emits {
  (e: 'update:selectedItems', items: Record<string, any>[]): void
  (e: 'update:currentPage', page: number): void
  (e: 'update:pageSize', size: number): void
  (e: 'update:sortBy', key: string): void
  (e: 'update:sortDirection', direction: 'asc' | 'desc'): void
  (e: 'row-click', item: Record<string, any>): void
}

const props = withDefaults(defineProps<Props>(), {
  rowKey: 'id',
  striped: true,
  bordered: false,
  hoverable: true,
  compact: false,
  selectable: false,
  rowClickable: false,
  loading: false,
  sortable: true,
  defaultSortBy: '',
  defaultSortDirection: 'asc',
  pagination: false,
  currentPage: 1,
  pageSize: 10,
  pageSizeOptions: () => [10, 20, 50, 100],
  showPageSizeSelector: true,
  totalItems: null,
  emptyText: 'No data available'
})

const emit = defineEmits<Emits>()

// Selection
const selectedItems = ref<Record<string, any>[]>([])

const isSelected = (item: Record<string, any>): boolean => {
  if (!props.rowKey) return selectedItems.value.includes(item)
  return selectedItems.value.some((selected: Record<string, any>) => selected[props.rowKey!] === item[props.rowKey!])
}

const toggleSelect = (item: Record<string, any>): void => {
  if (isSelected(item)) {
    if (props.rowKey) {
      selectedItems.value = selectedItems.value.filter(
        (selected: Record<string, any>) => selected[props.rowKey!] !== item[props.rowKey!]
      )
    } else {
      selectedItems.value = selectedItems.value.filter((selected: Record<string, any>) => selected !== item)
    }
  } else {
    selectedItems.value = [...selectedItems.value, item]
  }

  emit('update:selectedItems', selectedItems.value)
}

const toggleSelectAll = (): void => {
  if (allSelected.value) {
    selectedItems.value = []
  } else {
    selectedItems.value = [...displayedData.value]
  }

  emit('update:selectedItems', selectedItems.value)
}

const someSelected = computed<boolean>(() => {
  return selectedItems.value.length > 0 && selectedItems.value.length < displayedData.value.length
})

const allSelected = computed<boolean>(() => {
  return displayedData.value.length > 0 && selectedItems.value.length === displayedData.value.length
})

// Sorting
const sortBy = ref<string>(props.defaultSortBy)
const sortDirection = ref<'asc' | 'desc'>(props.defaultSortDirection)

const sort = (key: string): void => {
  if (sortBy.value === key) {
    // Toggle direction if already sorting by this column
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    // New sort column
    sortBy.value = key;
    sortDirection.value = 'asc';
  }
  
  emit('update:sortBy', sortBy.value);
  emit('update:sortDirection', sortDirection.value);
};

// Pagination
const currentPageSync = computed<number>({
  get: () => props.currentPage,
  set: (value: number) => emit('update:currentPage', value)
})

const pageSizeSync = computed<number>({
  get: () => props.pageSize,
  set: (value: number) => emit('update:pageSize', value)
})

const totalPages = computed<number>(() => {
  const total = props.totalItems !== null ? props.totalItems : props.data.length
  return Math.ceil(total / props.pageSize)
})

// Data processing
const sortedData = computed<Record<string, any>[]>(() => {
  if (!sortBy.value) return props.data

  return [...props.data].sort((a: Record<string, any>, b: Record<string, any>) => {
    const aValue = getValue(a, sortBy.value)
    const bValue = getValue(b, sortBy.value)

    if (aValue === bValue) return 0

    const direction = sortDirection.value === 'asc' ? 1 : -1

    if (aValue === null || aValue === undefined) return 1 * direction
    if (bValue === null || bValue === undefined) return -1 * direction

    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return aValue.localeCompare(bValue) * direction
    }

    return (aValue < bValue ? -1 : 1) * direction
  })
})

const displayedData = computed<Record<string, any>[]>(() => {
  if (!props.pagination || props.totalItems !== null) {
    // If external pagination is used (totalItems is provided), don't slice the data
    return sortedData.value
  }

  const start = (currentPageSync.value - 1) * pageSizeSync.value
  const end = start + pageSizeSync.value

  return sortedData.value.slice(start, end)
})

// Columns
const visibleColumns = computed<Column[]>(() => {
  return props.columns.filter((column: Column) => !column.hidden)
})

// Get access to slots
const slots = useSlots()

const hasActions = computed<boolean>(() => {
  return !!slots.actions
})

const totalColumns = computed<number>(() => {
  let count = visibleColumns.value.length
  if (props.selectable) count++
  if (hasActions.value) count++
  return count
})

const tableClasses = computed<Record<string, boolean>>(() => {
  return {
    'hb-table--bordered': props.bordered,
    'hb-table--hoverable': props.hoverable,
    'hb-table--compact': props.compact,
  }
})

// Utilities
const getValue = (item: Record<string, any>, key: string): any => {
  if (!key.includes('.')) return item[key]

  // Handle nested properties (e.g., 'user.name')
  return key.split('.').reduce((obj: any, path: string) => {
    return obj && obj[path] !== undefined ? obj[path] : null
  }, item)
}

const formatValue = (value: any, format: string | ((value: any) => string) | undefined): string => {
  if (value === null || value === undefined) return ''

  if (!format) return value

  if (typeof format === 'function') {
    return format(value)
  }

  switch (format) {
    case 'date':
      return new Date(value).toLocaleDateString()
    case 'datetime':
      return new Date(value).toLocaleString()
    case 'currency':
      return typeof value === 'number'
        ? value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
        : value
    case 'percent':
      return typeof value === 'number'
        ? `${(value * 100).toFixed(2)}%`
        : value
    default:
      return value
  }
}

const onRowClick = (item: Record<string, any>): void => {
  emit('row-click', item)
}

// Reset selected items when data changes
watch(() => props.data, () => {
  selectedItems.value = [];
});
</script>

<style>
.hb-table-container {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.hb-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: var(--text-sm);
}

/* Header Styles */
.hb-table__header {
  background-color: var(--gray-50);
}

.hb-table__th {
  padding: var(--spacing-3) var(--spacing-4);
  text-align: left;
  font-weight: var(--font-medium);
  color: var(--gray-700);
  border-bottom: 1px solid var(--gray-200);
  white-space: nowrap;
}

.hb-table__th-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

/* Sortable Header */
.hb-table__th--sortable {
  cursor: pointer;
}

.hb-table__th--sortable:hover {
  background-color: var(--gray-100);
}

.hb-table__th--sorted-asc,
.hb-table__th--sorted-desc {
  background-color: var(--gray-100);
  color: var(--primary-600);
}

.hb-table__sort-icon {
  display: inline-flex;
  align-items: center;
}

/* Cell Styles */
.hb-table__td {
  padding: var(--spacing-3) var(--spacing-4);
  border-bottom: 1px solid var(--gray-200);
  color: var(--gray-700);
}

/* Row Styles */
.hb-table__row--striped {
  background-color: var(--gray-50);
}

.hb-table__row--selected {
  background-color: var(--primary-50);
}

.hb-table__row--clickable {
  cursor: pointer;
}

.hb-table__row--clickable:hover {
  background-color: var(--gray-100);
}

/* Hoverable Table */
.hb-table--hoverable .hb-table__row:hover {
  background-color: var(--gray-50);
}

.hb-table--hoverable .hb-table__row--selected:hover {
  background-color: var(--primary-100);
}

/* Checkbox Column */
.hb-table__th--checkbox,
.hb-table__td--checkbox {
  width: 1%;
  padding-right: var(--spacing-2);
}

/* HbSingleCheckbox styling in table context */
.hb-table__th--checkbox,
.hb-table__td--checkbox {
  vertical-align: middle;
  padding-left: var(--spacing-4);
}

.hb-table__checkbox-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.hb-table__th--checkbox :deep(.hb-checkbox-option),
.hb-table__td--checkbox :deep(.hb-checkbox-option) {
  padding: 0;
  margin-bottom: 0;
  justify-content: center;
}

.hb-table__th--checkbox :deep(.hb-single-checkbox),
.hb-table__td--checkbox :deep(.hb-single-checkbox) {
  margin-bottom: 0;
  display: flex;
  justify-content: center;
}

.hb-table__th--checkbox :deep(.hb-checkbox-content),
.hb-table__td--checkbox :deep(.hb-checkbox-content) {
  display: none; /* Hide label area in table context */
}

.hb-table__th--checkbox :deep(.checkbox-square),
.hb-table__td--checkbox :deep(.checkbox-square) {
  width: 1rem;
  height: 1rem;
}

/* Actions Column */
.hb-table__th--actions,
.hb-table__td--actions {
  width: 1%;
  white-space: nowrap;
  text-align: right;
}

/* Empty State */
.hb-table__empty-row {
  height: 200px;
}

.hb-table__empty-cell {
  text-align: center;
  padding: var(--spacing-8);
}

.hb-table__empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hb-table__empty-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
  color: var(--gray-500);
}

.hb-table__empty-message svg {
  width: 2.5rem;
  height: 2.5rem;
  color: var(--gray-400);
}

/* Loading State */
.hb-table--loading {
  opacity: 0.7;
  pointer-events: none;
}

.hb-table__loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.7);
  z-index: 1;
}

/* Pagination */
.hb-table__pagination {
  margin-top: var(--spacing-4);
  display: flex;
  justify-content: flex-end;
}

/* Variants */
.hb-table--bordered {
  border: 1px solid var(--gray-200);
}

.hb-table--bordered .hb-table__th,
.hb-table--bordered .hb-table__td {
  border: 1px solid var(--gray-200);
}

.hb-table--compact .hb-table__th,
.hb-table--compact .hb-table__td {
  padding: var(--spacing-2) var(--spacing-3);
}
</style>
