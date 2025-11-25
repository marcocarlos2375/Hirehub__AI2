<template>
  <div class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div class="flex min-h-full items-center justify-center p-4">
      <!-- Modal Container -->
      <div class="relative bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden" @click.stop>
        <!-- Header -->
        <div class="bg-gradient-to-r from-purple-600 to-indigo-600 px-8 py-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                <svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Job Search Queries
              </h2>
              <p class="text-purple-100 text-sm mt-1">{{ querySets.length }} domains × 10 queries each = {{ querySets.length * 10 }} total</p>
            </div>
            <HbButton
              @click="$emit('close')"
              variant="link"
              size="sm"
              class="text-white hover:bg-white/20"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </HbButton>
          </div>
        </div>

        <!-- Domain Selector -->
        <div class="bg-gray-50 px-8 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex-1 mr-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Select Domain</label>
              <HbSelect
                v-model="selectedDomainIndex"
                :options="domainOptions"
              />
            </div>
            <div class="flex gap-2">
              <HbButton
                @click="copyAllForCurrentDomain"
                variant="outline"
                size="sm"
              >
                <template #leading-icon>
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </template>
                Copy All (10)
              </HbButton>
              <HbButton
                @click="downloadAllQueries"
                variant="primary"
                size="sm"
              >
                <template #leading-icon>
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </template>
                Download All
              </HbButton>
            </div>
          </div>
        </div>

        <!-- Queries List -->
        <div class="px-8 py-6 overflow-y-auto max-h-[calc(90vh-280px)]">
          <div v-if="selectedQuerySet" class="space-y-4">
            <!-- Domain Info -->
            <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
              <div class="flex items-start justify-between">
                <div>
                  <h3 class="font-semibold text-indigo-900">{{ selectedQuerySet.domainName }}</h3>
                  <div class="flex gap-4 mt-2 text-sm">
                    <span class="text-indigo-700">
                      <strong>Role:</strong> {{ selectedQuerySet.technicalRole }}
                    </span>
                    <span class="text-indigo-700">
                      <strong>Industry:</strong> {{ selectedQuerySet.industry }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Query Cards -->
            <div v-for="query in selectedQuerySet.queries" :key="query.id" class="bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
              <div class="p-5">
                <div class="flex items-start justify-between mb-3">
                  <div class="flex items-center gap-3">
                    <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-purple-100 text-purple-700 font-semibold text-sm">
                      {{ query.id }}
                    </span>
                    <div>
                      <h4 class="font-medium text-gray-900">{{ query.description }}</h4>
                    </div>
                  </div>
                  <HbButton
                    @click="copyQuery(query.query)"
                    variant="secondary"
                    size="sm"
                  >
                    <template #leading-icon>
                      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </template>
                    Copy
                  </HbButton>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 font-mono text-sm text-gray-800 break-all">
                  {{ query.query }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Copy Success Toast -->
        <transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 translate-y-2"
        >
          <div
            v-if="copySuccess"
            class="absolute bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span class="font-medium">Copied to clipboard!</span>
          </div>
        </transition>
      </div>
    </div>

    <!-- Background Overlay -->
    <div class="fixed inset-0 bg-black/50 -z-10" @click="$emit('close')"></div>
  </div>
</template>

<script setup lang="ts">
import type { DomainMatch } from '~/composables/features/useDomainFinder'
import type { QuerySet } from '~/utils/queryGenerator'

interface Props {
  domains: DomainMatch[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const {
  generateQueries,
  copyToClipboard,
  copyAllQueriesForDomain,
  downloadQueriesAsFile,
  copySuccess
} = useJobSearchQueryGenerator()

// Generate queries on mount
const querySets = ref<QuerySet[]>([])
const selectedDomainIndex = ref(0)

onMounted(() => {
  querySets.value = generateQueries(props.domains)
})

const selectedQuerySet = computed(() => {
  return querySets.value[selectedDomainIndex.value]
})

// Domain options for HbSelect
const domainOptions = computed(() => {
  return querySets.value.map((querySet, index) => ({
    value: index,
    label: querySet.domainName
  }))
})

const copyQuery = async (query: string) => {
  await copyToClipboard(query)
}

const copyAllForCurrentDomain = async () => {
  if (selectedQuerySet.value) {
    await copyAllQueriesForDomain(selectedQuerySet.value)
  }
}

const downloadAllQueries = () => {
  downloadQueriesAsFile(querySets.value)
}
</script>
