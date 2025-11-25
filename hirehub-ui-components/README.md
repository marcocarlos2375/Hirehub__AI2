# HireHub UI Components

A comprehensive, production-ready Vue 3 component library with 50+ TypeScript-strict components. Originally built for the HireHub platform, these components are designed to be reusable across any Vue 3 application.

## ✨ Features

- **56 Production-Ready Components** - Form inputs, buttons, modals, tables, navigation, feedback, and more
- **TypeScript Strict Mode** - All components use `// @ts-strict` with full type safety
- **Composition API** - Modern Vue 3 patterns throughout
- **Customizable Design System** - CSS variables for easy theming
- **Zero Dependencies** - Most components have no external dependencies (except HbWysiwyg which requires TipTap)
- **Accessibility** - ARIA labels, keyboard navigation, focus management
- **Framework Flexible** - Easy to adapt from Nuxt to any Vue 3 setup

## 📦 Installation

```bash
npm install hirehub-ui-components
# or
yarn add hirehub-ui-components
# or
pnpm add hirehub-ui-components
```

### Required Peer Dependencies

```bash
npm install vue@^3.3.0
```

### Optional Dependencies

For **HbWysiwyg** (Rich Text Editor):
```bash
npm install @tiptap/vue-3 @tiptap/starter-kit @tiptap/extension-underline @tiptap/extension-placeholder
```

For **HbDatepicker** (Calendar):
```bash
npm install v-calendar@^3.1.2
```

## 🚀 Quick Start

### 1. Import CSS Variables (Required)

In your main entry file (`main.ts` or `main.js`):

```typescript
import 'hirehub-ui-components/assets/css/var.css'
import 'hirehub-ui-components/assets/css/main.css'
```

### 2. Use Components

```vue
<script setup lang="ts">
import { HbButton, HbInput, HbModal } from 'hirehub-ui-components'
import { ref } from 'vue'

const email = ref('')
const showModal = ref(false)
</script>

<template>
  <div>
    <HbInput
      v-model="email"
      label="Email"
      type="email"
      placeholder="Enter your email"
    />

    <HbButton @click="showModal = true">
      Open Modal
    </HbButton>

    <HbModal v-model="showModal" title="Welcome">
      <p>This is a modal component!</p>
    </HbModal>
  </div>
</template>
```

## 📚 Component Catalog

### Form Components

| Component | Description |
|-----------|-------------|
| **HbInput** | Text input with variants (text, email, password, url, textarea, birthdate) |
| **HbCheckbox** | Single checkbox with customizable styling |
| **HbRadio** | Radio button group |
| **HbToggle** | Toggle switch |
| **HbSelect** | Custom select dropdown with search |
| **HbRange** | Range slider input |
| **HbDatepicker** | Date picker with calendar |
| **HbDateInput** | Simple date input field |
| **HbDateMonthYear** | Month/Year picker |
| **HbSingleCheckbox** | Standalone checkbox |

### Button Components

| Component | Description |
|-----------|-------------|
| **HbButton** | Versatile button with multiple variants (primary, secondary, outline, ghost, danger, etc.) |

### Layout Components

| Component | Description |
|-----------|-------------|
| **HbCard** | Card container with optional header/footer |
| **HbModal** | Modal dialog with customizable sizes |
| **HbModalFullscreen** | Full-screen modal overlay |
| **HbSidebar** | Collapsible sidebar navigation |
| **HbCardSelect** | Selectable card with radio/checkbox |

### Navigation Components

| Component | Description |
|-----------|-------------|
| **HbBreadcrumbs** | Breadcrumb navigation trail |
| **HbPagination** | Pagination controls |
| **HbTabs** | Tab navigation |
| **HbStepper** | Step-by-step progress indicator |

### Feedback Components

| Component | Description |
|-----------|-------------|
| **HbSpinner** | Loading spinner in various sizes |
| **HbIconSpinner** | Animated icon spinner |
| **HbBadge** | Status badge with color variants |
| **HbProgressBar** | Linear progress bar |
| **HbSegmentedProgress** | Multi-segment progress indicator |
| **HbSemicircleProgress** | Semicircular progress chart |
| **HbNotification** | Toast notification |
| **HbTooltip** | Hover tooltip |
| **HbPulsingIcon** | Pulsing icon animation |

### Data Display Components

| Component | Description |
|-----------|-------------|
| **HbTable** | Data table with sorting, selection, pagination |
| **HbTableActions** | Action buttons for table rows |

### Media Components

| Component | Description |
|-----------|-------------|
| **HbAvatar** | User avatar with fallback initials |
| **HbImg** | Image component with lazy loading |
| **HbVideo** | Video player with controls |
| **HbFile** | File upload/display component |
| **HbFileImage** | Image file upload with preview |
| **HbIcon** | SVG icon component (51 built-in icons) |
| **HbProfilePicture** | Profile picture with upload/crop (requires API) |

### Miscellaneous Components

| Component | Description |
|-----------|-------------|
| **HbColor** | Color input picker |
| **HbColorPicker** | Advanced color picker with palette |
| **HbColorPalette** | Preset color palette selector |
| **HbColorPaletteLocked** | Locked color palette |
| **HbSlider** | Image/content slider |
| **HbCounter** | Animated number counter |
| **HbPills** | Pill-shaped tag list |
| **HbTagPills** | Interactive tag pills with remove |
| **HbSnake** | Snake game component |
| **LanguageBar** | Language proficiency bar |

### Rich Content Components

| Component | Description | Dependencies |
|-----------|-------------|--------------|
| **HbWysiwyg** | Rich text WYSIWYG editor | Requires TipTap |
| **HbImageEditor** | Canvas-based image editor | No dependencies |

## 🎨 Theming & Customization

All components use CSS variables defined in `assets/css/var.css`. You can override these in your own CSS:

```css
:root {
  /* Primary Colors */
  --primary-50: #f0f9ff;
  --primary-500: #3b82f6;
  --primary-600: #2563eb;

  /* Typography */
  --font-heading: 'Gabarito', sans-serif;
  --font-body: 'Outfit', sans-serif;
  --font-text: 'Wix Madefor Text', sans-serif;

  /* Spacing */
  --spacing-1: 0.25rem;
  --spacing-4: 1rem;

  /* Component-specific */
  --input-height: 44px;
  --input-border-radius: 8px;
  --button-border-radius: 8px;
}
```

### Loading Fonts

Add to your HTML `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gabarito:wght@400;500;600;700&family=Outfit:wght@300;400;500;600;700&family=Wix+Madefor+Text:wght@400;500;600;700&display=swap" rel="stylesheet">
```

## 🔧 Migrating from Nuxt

If you're using these components outside of Nuxt, you'll need to make a few adjustments:

### 1. Replace NuxtLink (2 components affected)

**Components:** HbButton, HbBreadcrumbs

Replace `<NuxtLink>` with Vue Router's `<RouterLink>` or plain `<a>` tags:

```vue
<!-- Before (Nuxt) -->
<NuxtLink :to="/about">About</NuxtLink>

<!-- After (Vue Router) -->
<RouterLink :to="/about">About</RouterLink>

<!-- After (Plain HTML) -->
<a href="/about">About</a>
```

### 2. Replace useRuntimeConfig (3 components affected)

**Components:** HbAvatar, HbProfilePicture, HbWysiwyg

Replace Nuxt's `useRuntimeConfig()` with Vite environment variables:

```typescript
// Before (Nuxt)
const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl

// After (Vite)
const apiUrl = import.meta.env.VITE_API_URL
```

### 3. API Integration (HbProfilePicture)

**HbProfilePicture** requires an API for upload/delete. You'll need to implement:

```typescript
// Your API service
export const profilePictureApi = {
  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return await fetch('/api/profile-picture', { method: 'POST', body: formData })
  },
  delete: async (id: number) => {
    return await fetch(`/api/profile-picture/${id}`, { method: 'DELETE' })
  }
}
```

See `MIGRATION_GUIDE.md` for detailed migration steps.

## 📖 Component Examples

### HbButton Examples

```vue
<template>
  <!-- Variants -->
  <HbButton variant="primary">Primary</HbButton>
  <HbButton variant="secondary">Secondary</HbButton>
  <HbButton variant="outline">Outline</HbButton>
  <HbButton variant="ghost">Ghost</HbButton>
  <HbButton variant="danger">Danger</HbButton>

  <!-- Sizes -->
  <HbButton size="sm">Small</HbButton>
  <HbButton size="md">Medium</HbButton>
  <HbButton size="lg">Large</HbButton>

  <!-- With Icons -->
  <HbButton>
    <template #leading-icon>
      <HbIcon name="plus" />
    </template>
    Add Item
  </HbButton>

  <!-- Loading State -->
  <HbButton :loading="true">Processing...</HbButton>

  <!-- Navigation -->
  <HbButton to="/dashboard">Go to Dashboard</HbButton>
  <HbButton href="https://example.com" target="_blank">External Link</HbButton>
</template>
```

### HbInput Examples

```vue
<script setup lang="ts">
import { ref } from 'vue'

const name = ref('')
const email = ref('')
const password = ref('')
const bio = ref('')
</script>

<template>
  <!-- Text Input -->
  <HbInput
    v-model="name"
    label="Full Name"
    placeholder="John Doe"
    required
  />

  <!-- Email Input -->
  <HbInput
    v-model="email"
    type="email"
    label="Email Address"
    placeholder="john@example.com"
  />

  <!-- Password Input -->
  <HbInput
    v-model="password"
    type="password"
    label="Password"
    helperText="Must be at least 8 characters"
  />

  <!-- Textarea -->
  <HbInput
    v-model="bio"
    type="textarea"
    label="Biography"
    placeholder="Tell us about yourself..."
  />

  <!-- With Icons -->
  <HbInput v-model="search" placeholder="Search...">
    <template #leadingIcon>
      <HbIcon name="search" />
    </template>
  </HbInput>
</template>
```

### HbModal Examples

```vue
<script setup lang="ts">
import { ref } from 'vue'

const showModal = ref(false)
</script>

<template>
  <HbButton @click="showModal = true">Open Modal</HbButton>

  <HbModal
    v-model="showModal"
    title="Confirm Action"
    size="md"
  >
    <p>Are you sure you want to proceed?</p>

    <template #footer>
      <HbButton variant="outline" @click="showModal = false">
        Cancel
      </HbButton>
      <HbButton variant="danger" @click="handleConfirm">
        Confirm
      </HbButton>
    </template>
  </HbModal>
</template>
```

### HbTable Example

```vue
<script setup lang="ts">
import { ref } from 'vue'

const columns = [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'role', label: 'Role' },
  { key: 'actions', label: 'Actions' }
]

const data = ref([
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User' }
])
</script>

<template>
  <HbTable
    :columns="columns"
    :data="data"
    selectable
    :loading="false"
  >
    <template #cell-actions="{ row }">
      <HbTableActions
        :actions="[
          { label: 'Edit', icon: 'edit', onClick: () => handleEdit(row) },
          { label: 'Delete', icon: 'delete', onClick: () => handleDelete(row) }
        ]"
      />
    </template>
  </HbTable>
</template>
```

## 🏗️ Project Structure

```
hirehub-ui-components/
├── components/
│   └── base/               # All 56 components
│       ├── HbButton.vue
│       ├── HbInput.vue
│       ├── HbModal.vue
│       └── ...
├── types/
│   ├── components.d.ts     # Component prop/emit types
│   └── globals.d.ts        # Global type definitions
├── assets/
│   ├── css/
│   │   ├── var.css        # CSS variables (REQUIRED)
│   │   └── main.css       # Base styles
│   └── icons/             # 51 SVG icons
│       ├── check.svg
│       ├── close.svg
│       └── ...
├── package.json
├── README.md
└── MIGRATION_GUIDE.md
```

## 🔍 TypeScript Support

All components are written in TypeScript with strict mode enabled. Import types:

```typescript
import type { HbButtonProps, HbInputProps, HbModalProps } from 'hirehub-ui-components/types/components'
```

## 🤝 Contributing

This component library was extracted from the HireHub platform. Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🐛 Known Issues

1. **HbProfilePicture** requires backend API integration (see Migration Guide)
2. **NuxtLink** must be replaced with RouterLink or `<a>` for non-Nuxt projects
3. **useRuntimeConfig** must be replaced with environment variables (3 components affected)

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/hirehub-ui-components/issues)
- Documentation: See `MIGRATION_GUIDE.md` for detailed setup instructions

## 🙏 Acknowledgments

Built with ❤️ by the HireHub team
- Vue 3 & Composition API
- TipTap for rich text editing
- v-calendar for date picking
- CSS Variables for theming
