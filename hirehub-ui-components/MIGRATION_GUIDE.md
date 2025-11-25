# Migration Guide: Using HireHub UI Components Outside of Nuxt

This guide helps you integrate HireHub UI Components into any Vue 3 application, whether you're using Vite, Vue CLI, or another build tool.

## Table of Contents

- [Quick Start](#quick-start)
- [Required Changes](#required-changes)
- [Component-Specific Migrations](#component-specific-migrations)
- [Environment Configuration](#environment-configuration)
- [CSS & Styling Setup](#css--styling-setup)
- [Font Setup](#font-setup)
- [TypeScript Configuration](#typescript-configuration)
- [Common Issues](#common-issues)

## Quick Start

### 1. Install the Package

```bash
npm install hirehub-ui-components
```

### 2. Install Peer Dependencies

```bash
npm install vue@^3.3.0
```

### 3. Optional Dependencies

For **HbWysiwyg** (Rich Text Editor):
```bash
npm install @tiptap/vue-3 @tiptap/starter-kit @tiptap/extension-underline @tiptap/extension-placeholder
```

For **HbDatepicker**:
```bash
npm install v-calendar@^3.1.2
```

### 4. Import CSS (Required)

In your `main.ts` or `main.js`:

```typescript
import { createApp } from 'vue'
import App from './App.vue'

// Import HireHub UI CSS (REQUIRED)
import 'hirehub-ui-components/assets/css/var.css'
import 'hirehub-ui-components/assets/css/main.css'

const app = createApp(App)
app.mount('#app')
```

## Required Changes

The following components require modifications when used outside of Nuxt:

| Component | Issue | Solution |
|-----------|-------|----------|
| HbButton | Uses `NuxtLink` | Replace with `RouterLink` or `<a>` |
| HbBreadcrumbs | Uses `NuxtLink` | Replace with `RouterLink` or `<a>` |
| HbAvatar | Uses `useRuntimeConfig()` | Replace with env variables |
| HbProfilePicture | Uses `useRuntimeConfig()` + API | Replace with env variables + custom API |
| HbWysiwyg | Uses `useRuntimeConfig()` | Replace with env variables |

## Component-Specific Migrations

### 1. HbButton - Replace NuxtLink

**Issue:** HbButton uses `<NuxtLink>` for internal navigation

**Solution Options:**

#### Option A: Use Vue Router (Recommended)

```typescript
// In your component that uses HbButton
import { RouterLink } from 'vue-router'

// No changes needed if using HbButton as external link or regular button
// For internal navigation, HbButton's `to` prop will work with RouterLink
```

#### Option B: Fork and Replace

If you need full control, you can copy `HbButton.vue` and replace:

```vue
<!-- Find this in HbButton.vue (line ~33) -->
<NuxtLink
  v-else-if="to && !href"
  :to="to"
  :class="buttonClasses"
>
  <!-- ... -->
</NuxtLink>

<!-- Replace with -->
<RouterLink
  v-else-if="to && !href"
  :to="to"
  :class="buttonClasses"
>
  <!-- ... -->
</RouterLink>
```

### 2. HbBreadcrumbs - Replace NuxtLink

**Issue:** Uses `<NuxtLink>` for breadcrumb links

**Solution:**

```vue
<!-- Find this in HbBreadcrumbs.vue (line ~12) -->
<NuxtLink
  v-if="item.url"
  :to="item.url"
  class="hb-breadcrumbs__link"
>
  <!-- ... -->
</NuxtLink>

<!-- Replace with -->
<RouterLink
  v-if="item.url"
  :to="item.url"
  class="hb-breadcrumbs__link"
>
  <!-- ... -->
</RouterLink>
```

### 3. HbAvatar - Replace useRuntimeConfig

**Issue:** Uses `useRuntimeConfig()` to get API base URL

**Location:** Line 413 in `HbAvatar.vue`

**Current Code:**
```typescript
const config = useRuntimeConfig();
const baseUrl = config.public.apiBaseUrl?.replace('/api', '') || 'http://localhost:8080';
```

**Solution for Vite:**
```typescript
// Replace with
const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8080';
```

**Solution for Vue CLI:**
```typescript
// Replace with
const baseUrl = process.env.VUE_APP_API_BASE_URL?.replace('/api', '') || 'http://localhost:8080';
```

**Environment Variable (.env):**
```bash
VITE_API_BASE_URL=http://localhost:8080
# or for Vue CLI
VUE_APP_API_BASE_URL=http://localhost:8080
```

### 4. HbProfilePicture - API Integration Required

**Issue:** Uses `useRuntimeConfig()` + backend API service

**Location:** Lines 626-631 in `HbProfilePicture.vue`

**Required Changes:**

#### Step 1: Replace useRuntimeConfig

```typescript
// Current code (line 626)
const config = useRuntimeConfig();
const backendUrl = (config.public.apiUrl as string).replace(/\/$/, '').replace('/api', '');

// Replace with Vite
const backendUrl = (import.meta.env.VITE_API_URL as string).replace(/\/$/, '').replace('/api', '');

// Or Vue CLI
const backendUrl = (process.env.VUE_APP_API_URL as string).replace(/\/$/, '').replace('/api', '');
```

#### Step 2: Implement API Service

Create a file `services/api.ts`:

```typescript
export const profilePictureApi = {
  /**
   * Upload profile picture
   * @param file - Image file to upload
   * @returns Promise with uploaded image data
   */
  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('profilePicture', file)

    const response = await fetch(`${import.meta.env.VITE_API_URL}/profile-picture`, {
      method: 'POST',
      body: formData,
      credentials: 'include', // Include cookies if needed
      headers: {
        // Add your auth headers if needed
        // 'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Upload failed')
    }

    return await response.json()
  },

  /**
   * Delete profile picture
   * @param id - Picture ID to delete
   * @returns Promise with delete result
   */
  delete: async (id: number) => {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/profile-picture/${id}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        // Add your auth headers if needed
      }
    })

    if (!response.ok) {
      throw new Error('Delete failed')
    }

    return await response.json()
  }
}
```

#### Step 3: Import and Use

In `HbProfilePicture.vue`, replace the import:

```typescript
// Current import (line ~600)
import { profilePictureApi } from '~/services/api'

// Replace with
import { profilePictureApi } from '@/services/api'
```

### 5. HbWysiwyg - Replace useRuntimeConfig

**Issue:** Uses `useRuntimeConfig()` for LanguageTool API URL

**Location:** Line 586 in `HbWysiwyg.vue`

**Current Code:**
```typescript
const config = useRuntimeConfig()
const apiUrl = config.public.languageToolApiUrl || 'https://api.languagetool.org/v2/check'
```

**Solution for Vite:**
```typescript
const apiUrl = import.meta.env.VITE_LANGUAGETOOL_API_URL || 'https://api.languagetool.org/v2/check'
```

**Environment Variable (.env):**
```bash
VITE_LANGUAGETOOL_API_URL=https://api.languagetool.org/v2/check
```

## Environment Configuration

### Vite Projects

Create `.env` file in your project root:

```bash
# API Base URL (for HbAvatar, HbProfilePicture)
VITE_API_BASE_URL=http://localhost:8080
VITE_API_URL=http://localhost:8080/api

# LanguageTool API (for HbWysiwyg spell checking)
VITE_LANGUAGETOOL_API_URL=https://api.languagetool.org/v2/check

# PDF Generator (if you need PDF export)
VITE_PDF_API_URL=http://localhost:5001
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_URL
```

### Vue CLI Projects

Create `.env` file:

```bash
VUE_APP_API_BASE_URL=http://localhost:8080
VUE_APP_API_URL=http://localhost:8080/api
VUE_APP_LANGUAGETOOL_API_URL=https://api.languagetool.org/v2/check
```

Access in code:
```typescript
const apiUrl = process.env.VUE_APP_API_URL
```

### TypeScript Support for Environment Variables

Create `env.d.ts` in your project root:

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_API_BASE_URL: string
  readonly VITE_LANGUAGETOOL_API_URL: string
  readonly VITE_PDF_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

## CSS & Styling Setup

### 1. Import Required CSS Files

In your `main.ts`:

```typescript
import 'hirehub-ui-components/assets/css/var.css'  // CSS variables (REQUIRED)
import 'hirehub-ui-components/assets/css/main.css' // Base styles
```

### 2. Customize CSS Variables (Optional)

Create your own CSS file to override variables:

```css
/* styles/theme.css */
:root {
  /* Override primary colors */
  --primary-500: #10b981; /* Change to your brand color */
  --primary-600: #059669;

  /* Override fonts */
  --font-heading: 'Your Heading Font', sans-serif;
  --font-body: 'Your Body Font', sans-serif;

  /* Override component sizes */
  --input-height: 48px;
  --button-border-radius: 12px;
}
```

Import after HireHub CSS:
```typescript
import 'hirehub-ui-components/assets/css/var.css'
import './styles/theme.css' // Your overrides
```

### 3. Sass/SCSS Setup (Optional)

If you want to use Sass features:

```bash
npm install -D sass
```

Components already use `<style lang="scss" scoped>` - no changes needed.

## Font Setup

### Option 1: Google Fonts CDN (Easiest)

Add to your `index.html` `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gabarito:wght@400;500;600;700&family=Outfit:wght@300;400;500;600;700&family=Wix+Madefor+Text:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Option 2: Self-Hosted Fonts

1. Download fonts from Google Fonts
2. Place in `public/fonts/`
3. Create CSS file:

```css
/* styles/fonts.css */
@font-face {
  font-family: 'Gabarito';
  src: url('/fonts/Gabarito-Regular.woff2') format('woff2');
  font-weight: 400;
  font-display: swap;
}

@font-face {
  font-family: 'Gabarito';
  src: url('/fonts/Gabarito-Bold.woff2') format('woff2');
  font-weight: 700;
  font-display: swap;
}

/* Repeat for Outfit and Wix Madefor Text */
```

Import in `main.ts`:
```typescript
import './styles/fonts.css'
```

## TypeScript Configuration

Update your `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "types": ["vite/client"],
    "paths": {
      "@/*": ["./src/*"],
      "hirehub-ui-components": ["./node_modules/hirehub-ui-components"],
      "hirehub-ui-components/*": ["./node_modules/hirehub-ui-components/*"]
    }
  },
  "include": [
    "src/**/*",
    "node_modules/hirehub-ui-components/types/**/*"
  ]
}
```

## Common Issues

### Issue 1: "Cannot find module 'hirehub-ui-components'"

**Solution:**
- Ensure package is installed: `npm install hirehub-ui-components`
- Check `tsconfig.json` paths configuration
- Restart your dev server

### Issue 2: CSS Variables Not Working

**Solution:**
- Ensure you imported `var.css` in `main.ts`
- Check that import comes before any component usage
- Clear browser cache

### Issue 3: Components Look Broken/Unstyled

**Solution:**
- Import both CSS files: `var.css` and `main.css`
- Check that fonts are loaded (inspect Network tab)
- Verify no CSS conflicts with your existing styles

### Issue 4: HbButton Navigation Not Working

**Solution:**
- Install Vue Router: `npm install vue-router`
- Replace `NuxtLink` with `RouterLink` in HbButton.vue
- Or use `href` prop for external links instead of `to`

### Issue 5: HbProfilePicture Upload Fails

**Solution:**
- Implement `profilePictureApi` service (see [Step 2](#step-2-implement-api-service))
- Check API endpoint URL in environment variables
- Verify CORS settings if API is on different domain
- Check authentication headers are included

### Issue 6: TypeScript Errors with Component Props

**Solution:**
```typescript
// Import types explicitly
import type { HbButtonProps } from 'hirehub-ui-components/types/components'

// Use in your component
const props = withDefaults(defineProps<HbButtonProps>(), {
  variant: 'primary'
})
```

### Issue 7: Icons Not Displaying (HbIcon)

**Solution:**
- Icons are in `assets/icons/` folder
- Available icons: check `hirehub-ui-components/assets/icons/` directory
- Usage: `<HbIcon name="check" />`
- Ensure icon name matches SVG filename (without .svg extension)

## Testing Your Setup

Create a test component to verify everything works:

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { HbButton, HbInput, HbModal, HbSpinner } from 'hirehub-ui-components'

const name = ref('')
const showModal = ref(false)
</script>

<template>
  <div style="padding: 2rem;">
    <h1>HireHub UI Components Test</h1>

    <!-- Test Input -->
    <HbInput
      v-model="name"
      label="Name"
      placeholder="Enter your name"
    />

    <!-- Test Button -->
    <HbButton @click="showModal = true">
      Open Modal
    </HbButton>

    <!-- Test Modal -->
    <HbModal v-model="showModal" title="Test Modal">
      <p>If you can see this, HireHub UI Components are working!</p>
      <template #footer>
        <HbButton @click="showModal = false">Close</HbButton>
      </template>
    </HbModal>

    <!-- Test Spinner -->
    <HbSpinner size="md" color="primary" />
  </div>
</template>
```

If this renders correctly with proper styling, your setup is complete!

## Need Help?

- Check the main [README.md](./README.md) for component examples
- Review [Component Type Definitions](./types/components.d.ts)
- Inspect [CSS Variables](./assets/css/var.css) for customization options
- Open an issue on GitHub if you encounter problems

## Summary Checklist

- [ ] Installed package: `npm install hirehub-ui-components`
- [ ] Installed peer dependencies (Vue 3, TipTap, v-calendar if needed)
- [ ] Imported CSS files in `main.ts`
- [ ] Set up fonts (Google CDN or self-hosted)
- [ ] Configured environment variables
- [ ] Replaced `NuxtLink` with `RouterLink` (if using HbButton/HbBreadcrumbs)
- [ ] Replaced `useRuntimeConfig()` with env variables (if using HbAvatar/HbProfilePicture/HbWysiwyg)
- [ ] Implemented API service (if using HbProfilePicture)
- [ ] Updated `tsconfig.json` for TypeScript support
- [ ] Tested with a sample component

You're all set! 🎉
