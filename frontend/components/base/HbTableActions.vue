<template>
  <div
    class="hb-table-actions"
    :class="{ 'hb-table-actions--loading': loading }"
  >
    <div class="hb-table-actions__row hb-table-actions__search-bar">
      <div class="hb-table-actions__search">
        <HbInput
          v-model="searchQuery"
          :placeholder="searchPlaceholder"
          type="text"
          size="lg"
          @keydown.enter="$emit('search')"
        />
        <Transition
          name="fade"
          mode="out-in"
        >
          <div
            v-if="!loading"
            class="hb-table-actions__icons"
          >
          </div>
          <HbSpinner
            v-else
            size="sm"
            class="hb-table-actions__spinner"
          />
        </Transition>
      </div>

      <div
        v-if="pageSizeEnabled"
        class="hb-table-actions__show-entries"
      >
        <HbSelect
          v-model="perPageDisplay"
          :options="pageSizeOptions"
          size="lg"
          :placeholder="'Page Size'"
        />
      </div>

     

      <slot
        v-if="$slots.actions"
        name="actions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, watch, nextTick } from 'vue'
import HbInput from './HbInput.vue'
import HbSelect from './HbSelect.vue'
import HbSpinner from './HbSpinner.vue'
import HbIcon from './HbIcon.vue'

interface Props {
  entityData?: Record<string, any>[]
  total?: number
  currentPage?: number
  searchPlaceholder?: string
  initialSearchQuery?: string
  perPage?: number
  pageSizeEnabled?: boolean
  filters?: Record<string, any>
  filterOptions?: Record<string, Array<Record<string, string | number>>>
  loading?: boolean
}

interface Emits {
  (e: 'search'): void
  (e: 'searchInput', value: string): void
  (e: 'clearSearch'): void
  (e: 'perPageInput', value: number): void
  (e: 'filterChange', filters: Record<string, any>): void
}

const props = withDefaults(defineProps<Props>(), {
  entityData: () => [],
  total: 0,
  currentPage: 0,
  searchPlaceholder: 'Search...',
  initialSearchQuery: '',
  perPage: 5,
  pageSizeEnabled: true,
  filters: () => ({}),
  filterOptions: () => ({}),
  loading: false
})

const emit = defineEmits<Emits>()

const searchQuery = ref<string>(props.initialSearchQuery)
const perPageDisplay = ref<number>(props.perPage)
const filterLocal = ref<Record<string, any>>({ ...props.filters })

const pageSizeOptions = computed<Array<Record<string, string | number>>>(() => {
  return [
    { label: '5', value: 5 },
    { label: '10', value: 10 },
    { label: '25', value: 25 },
    { label: '50', value: 50 },
    { label: '100', value: 100 }
  ]
})

// Watch searchQuery
watch(searchQuery, (newVal: string) => {
  emit('searchInput', newVal)
})

// Watch initialSearchQuery
watch(() => props.initialSearchQuery, (newVal: string) => {
  searchQuery.value = newVal
}, { immediate: true })

// Watch perPageDisplay
watch(perPageDisplay, (newVal: number) => {
  emit('perPageInput', newVal)
})

// Watch filterLocal
watch(filterLocal, (newVal: Record<string, any>) => {
  emit('filterChange', newVal)
}, { deep: true })

// Watch filters prop
watch(() => props.filters, (newVal: Record<string, any>) => {
  filterLocal.value = { ...newVal }
}, { deep: true })

// Methods
const clearSearch = (): void => {
  searchQuery.value = ''
  nextTick(() => {
    emit('clearSearch')
  })
}

const getFilterOptions = (key: string): Array<Record<string, string | number>> => {
  if (props.filterOptions[key]) {
    return props.filterOptions[key]
  }

  // Default status options
  return [
    { label: 'Active', value: 'active' },
    { label: 'Inactive', value: 'inactive' },
    { label: 'Draft', value: 'draft' }
  ]
}

const getFilterPlaceholder = (key: string): string => {
  return key.charAt(0).toUpperCase() + key.slice(1)
}
</script>

<style lang="scss" scoped>
.hb-table-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;

  &__row {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
    
    @media (max-width: 768px) {
      flex-direction: column;
      align-items: stretch;
      gap: 0.75rem;
    }
  }

  &__search {
    position: relative;
    flex: 1 1 auto;
    min-width: 200px;
    
    @media (max-width: 768px) {
      width: 100%;
      min-width: 100%;
    }
  }

  &__icons {
    position: absolute;
    right: 0.75rem;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  &__search-icon {
    cursor: pointer;
    color: var(--gray-400);
    width: 1rem;
    height: 1rem;
    transition: color 0.2s ease;

    &--has-value {
      color: var(--primary-500);
    }

    &:hover {
      color: var(--primary-600);
    }
  }

  &__delete-icon {
    cursor: pointer;
    color: var(--red-400);
    width: 1rem;
    height: 1rem;
    transition: color 0.2s ease;

    &:hover {
      color: var(--red-500);
    }
  }

  &__spinner {
    position: absolute;
    top: 50%;
    right: 0.75rem;
    transform: translateY(-50%);
  }

  &__show-entries {
    min-width: 100px;

    @media (max-width: 768px) {
      min-width: auto;
      width: 100%;
    }
  }

  &--loading {
    opacity: 0.6;
    pointer-events: none;
  }
}

// Fade transitions
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
