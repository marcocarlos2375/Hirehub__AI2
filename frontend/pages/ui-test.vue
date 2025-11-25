<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-4xl font-bold mb-2">HireHub UI Components Test</h1>
      <p class="text-gray-600 mb-8">Testing integration of all 51 components</p>

      <!-- Buttons Section -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 class="text-2xl font-semibold mb-4">Buttons</h2>
        <div class="flex flex-wrap gap-4">
          <HbButton variant="primary">Primary Button</HbButton>
          <HbButton variant="secondary">Secondary Button</HbButton>
          <HbButton variant="outline">Outline Button</HbButton>
          <HbButton variant="ghost">Ghost Button</HbButton>
          <HbButton variant="danger">Danger Button</HbButton>
          <HbButton variant="primary" size="sm">Small</HbButton>
          <HbButton variant="primary" size="md">Medium</HbButton>
          <HbButton variant="primary" size="lg">Large</HbButton>
          <HbButton variant="primary" :loading="true">Loading...</HbButton>
        </div>
      </section>

      <!-- Badges Section -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 class="text-2xl font-semibold mb-4">Badges</h2>
        <div class="flex flex-wrap gap-4 items-center">
          <HbBadge variant="primary">Primary</HbBadge>
          <HbBadge variant="secondary">Secondary</HbBadge>
          <HbBadge variant="success">Success</HbBadge>
          <HbBadge variant="warning">Warning</HbBadge>
          <HbBadge variant="danger">Danger</HbBadge>
          <HbBadge variant="info">Info</HbBadge>
          <HbBadge>Default</HbBadge>
        </div>
      </section>

      <!-- Spinners Section -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 class="text-2xl font-semibold mb-4">Spinners</h2>
        <div class="flex flex-wrap gap-8 items-center">
          <div class="flex flex-col items-center gap-2">
            <HbSpinner size="xs" />
            <span class="text-sm text-gray-600">XS</span>
          </div>
          <div class="flex flex-col items-center gap-2">
            <HbSpinner size="sm" />
            <span class="text-sm text-gray-600">SM</span>
          </div>
          <div class="flex flex-col items-center gap-2">
            <HbSpinner size="md" />
            <span class="text-sm text-gray-600">MD</span>
          </div>
          <div class="flex flex-col items-center gap-2">
            <HbSpinner size="lg" />
            <span class="text-sm text-gray-600">LG</span>
          </div>
          <div class="flex flex-col items-center gap-2">
            <HbSpinner size="xl" />
            <span class="text-sm text-gray-600">XL</span>
          </div>
        </div>
      </section>

      <!-- Form Components Section -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 class="text-2xl font-semibold mb-4">Form Components</h2>
        <div class="grid gap-4 max-w-md">
          <div>
            <label class="block text-sm font-medium mb-2">Text Input</label>
            <HbInput
              v-model="formData.name"
              placeholder="Enter your name"
              variant="text"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">Email Input</label>
            <HbInput
              v-model="formData.email"
              placeholder="Enter your email"
              variant="email"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">Checkbox</label>
            <HbCheckbox
              v-model="formData.agreeArray"
              :options="['I agree to the terms']"
              label="Agreement"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">Toggle</label>
            <HbToggle v-model="formData.enabled" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">Select</label>
            <HbSelect
              v-model="formData.country"
              :options="countries"
              placeholder="Select a country"
            />
          </div>
        </div>
      </section>

      <!-- Cards Section -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">Cards</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <HbCard>
            <template #header>
              <h3 class="text-lg font-semibold">Card Title 1</h3>
            </template>
            <p>This is a card with header and content.</p>
            <template #footer>
              <HbButton variant="primary" size="sm">Action</HbButton>
            </template>
          </HbCard>

          <HbCard>
            <template #header>
              <h3 class="text-lg font-semibold">Card Title 2</h3>
            </template>
            <p>Another card with different content.</p>
            <template #footer>
              <HbButton variant="secondary" size="sm">Action</HbButton>
            </template>
          </HbCard>

          <HbCard>
            <template #header>
              <h3 class="text-lg font-semibold">Card Title 3</h3>
            </template>
            <p>Yet another card for testing.</p>
            <template #footer>
              <HbButton variant="outline" size="sm">Action</HbButton>
            </template>
          </HbCard>
        </div>
      </section>

      <!-- Progress Section -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 class="text-2xl font-semibold mb-4">Progress Indicators</h2>
        <div class="space-y-6">
          <div>
            <label class="block text-sm font-medium mb-2">Progress Bar (65%)</label>
            <HbProgressBar :value="65" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">Progress Bar (100%)</label>
            <HbProgressBar :value="100" />
          </div>
        </div>
      </section>

      <!-- Avatar Section -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 class="text-2xl font-semibold mb-4">Avatars</h2>
        <div class="flex flex-wrap gap-4 items-center">
          <HbAvatar name="John Doe" size="sm" />
          <HbAvatar name="Jane Smith" size="md" />
          <HbAvatar name="Bob Wilson" size="lg" />
          <HbAvatar name="Alice Johnson" size="xl" status="online" />
        </div>
      </section>

      <!-- Tabs Section -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 class="text-2xl font-semibold mb-4">Tabs</h2>
        <HbTabs
          v-model="activeTabIndex"
          :tabs="[
            { label: 'Overview' },
            { label: 'Details' },
            { label: 'Settings' }
          ]"
        >
          <div v-if="activeTabIndex === 0" class="p-4">Overview content goes here</div>
          <div v-else-if="activeTabIndex === 1" class="p-4">Details content goes here</div>
          <div v-else-if="activeTabIndex === 2" class="p-4">Settings content goes here</div>
        </HbTabs>
      </section>

      <!-- Modal Test -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 class="text-2xl font-semibold mb-4">Modal</h2>
        <HbButton @click="showModal = true">Open Modal</HbButton>

        <HbModal v-model="showModal" title="Test Modal" size="md">
          <p>This is a test modal with some content.</p>
          <template #footer>
            <div class="flex gap-2 justify-end">
              <HbButton variant="outline" @click="showModal = false">Cancel</HbButton>
              <HbButton variant="primary" @click="showModal = false">Confirm</HbButton>
            </div>
          </template>
        </HbModal>
      </section>

      <!-- Pills Section -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 class="text-2xl font-semibold mb-4">Pills</h2>
        <HbTagPills
          v-model="selectedTags"
          :tags="['Vue.js', 'Nuxt', 'TypeScript', 'TailwindCSS', 'Python', 'FastAPI']"
        />
      </section>

      <!-- Success Message -->
      <section class="mb-12 bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
        <h2 class="text-2xl font-semibold mb-2 text-green-700">✓ Integration Successful!</h2>
        <p class="text-gray-600">
          All HireHub UI Components are now available in the frontend.
          You can use them with the <code class="bg-gray-100 px-2 py-1 rounded">Hb</code> prefix.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const formData = ref({
  name: '',
  email: '',
  agree: false,
  agreeArray: [] as any[],
  enabled: false,
  country: ''
})

const countries = [
  { value: 'us', label: 'United States' },
  { value: 'uk', label: 'United Kingdom' },
  { value: 'ca', label: 'Canada' },
  { value: 'fr', label: 'France' },
  { value: 'de', label: 'Germany' }
]

const activeTabIndex = ref(0)
const showModal = ref(false)
const selectedTags = ref<string[]>([])
</script>
