# Type Safety Guide

This document provides guidelines for maintaining type safety across the HireHub frontend application using TypeScript.

## Table of Contents

- [Philosophy](#philosophy)
- [Type Definitions](#type-definitions)
- [Eliminating `any` Types](#eliminating-any-types)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)
- [Type Checking](#type-checking)
- [Troubleshooting](#troubleshooting)

---

## Philosophy

**Core Principle**: TypeScript is only valuable when used strictly. `any` types defeat the purpose.

### Why Type Safety Matters

1. **Catch Errors Early**: Type errors caught at compile-time, not runtime
2. **Better IDE Support**: Autocomplete, inline documentation, refactoring
3. **Self-Documenting**: Types serve as inline documentation
4. **Safer Refactoring**: Compiler catches breaking changes
5. **Team Collaboration**: Clear contracts between components

### Our Type Safety Goals

- ✅ Zero `any` types in production code
- ✅ Comprehensive type definitions for all API responses
- ✅ Type-safe store management (Pinia)
- ✅ Type-safe composables
- ✅ Strict TypeScript configuration

---

## Type Definitions

### Centralized API Types (`types/api-responses.ts`)

All API response types are centralized in a single file for consistency and reusability.

**Why Centralized?**
- Single source of truth
- Easy to update when API changes
- Prevents duplicate definitions
- Better IDE autocomplete

**Available Types** (15+ interfaces):

#### Core Data Structures

```typescript
import type {
  ParsedCV,
  ParsedJobDescription,
  GapInfo,
  QuestionData,
  CompatibilityScoreResult,
  AnswerEvaluationResponse,
  SubmitAnswersResponse,
  ResumeRewriteResponse,
  CoverLetterResponse,
  DomainFinderResponse,
  JobSearchQueriesResponse,
  AudioTranscriptionResponse,
  ApiErrorResponse
} from '~/types/api-responses'
```

#### Example: ParsedCV

```typescript
interface ParsedCV {
  personal_info: {
    first_name: string
    last_name: string
    email: string
    phone?: string
    location?: string
    job_title?: string
    social_links?: {
      linkedin?: string
      github?: string
      portfolio?: string
      twitter?: string
    }
  }
  work_experience: Array<{
    job_title: string
    company: string
    location: string
    start_date: string
    end_date?: string
    responsibilities: string[]
    achievements?: string[]
    technologies?: string[]
  }>
  education: Array<{
    degree: string
    field_of_study?: string
    institution: string
    graduation_date: string
    gpa?: string
    honors?: string[]
  }>
  skills: Array<{
    skill: string
    proficiency?: string
    years_of_experience?: number
    category?: string
  }>
  // ... more fields
}
```

### Adaptive Questions Types (`types/adaptive-questions.ts`)

Specialized types for the adaptive questions workflow:

```typescript
import type {
  ExperienceLevel,
  DeepDivePrompt,
  LearningResource,
  TimelineStep,
  StartWorkflowResponse,
  SubmitInputsResponse,
  RefineAnswerResponse,
  LearningPlanItem,
  AdaptiveQuestionState
} from '~/types/adaptive-questions'
```

### Component Types (`types/components.d.ts`)

HireHub UI component prop types for auto-completion:

```typescript
import type {
  HbButtonProps,
  HbModalProps,
  HbInputProps,
  // ... 51 component types
} from '~/types/components'
```

### Global Types (`types/globals.d.ts`)

Nuxt/Vue-specific global types:

```typescript
// Nuxt app extensions
declare module '#app' {
  interface NuxtApp {
    $t: (key: string, params?: Record<string, string | number>) => string
    $toast: {
      show(message: string, type?: 'success' | 'error', duration?: number): void
    }
  }
}
```

---

## Eliminating `any` Types

### Before: Unsafe Code

```typescript
// ❌ BAD - Lost all type safety
const startAdaptiveQuestion = async (
  questionId: string,
  questionText: string,
  questionData: any,  // ❌ What fields does this have?
  gapInfo: any,       // ❌ Unknown structure
  userId: string,
  parsedCV: any,      // ❌ Could be anything
  parsedJD: any,      // ❌ No IDE help
  experienceLevel: ExperienceLevel,
  language: string = 'english'
): Promise<any> => {  // ❌ What does this return?
  // Implementation
}
```

### After: Type-Safe Code

```typescript
// ✅ GOOD - Full type safety
import type { QuestionData, GapInfo, ParsedCV, ParsedJobDescription } from '~/types/api-responses'
import type { ExperienceLevel, StartWorkflowResponse } from '~/types/adaptive-questions'

const startAdaptiveQuestion = async (
  questionId: string,
  questionText: string,
  questionData: QuestionData,  // ✅ Known structure
  gapInfo: GapInfo,             // ✅ Documented fields
  userId: string,
  parsedCV: ParsedCV,           // ✅ Complete type
  parsedJD: ParsedJobDescription, // ✅ IDE autocomplete
  experienceLevel: ExperienceLevel,
  language: string = 'english'
): Promise<StartWorkflowResponse> => { // ✅ Known return type
  // Implementation
}
```

### Fixed Files

We eliminated **9 critical `any` types**:

1. **useAdaptiveQuestions.ts** (7 fixed)
   - `questionData: any` → `questionData: QuestionData`
   - `gapInfo: any` → `gapInfo: GapInfo`
   - `parsedCV: any` → `parsedCV: ParsedCV`
   - `parsedJD: any` → `parsedJD: ParsedJobDescription`
   - `refinementData: Record<string, any>` → `Record<string, string | number | boolean>`
   - `gap: any` → `gap: GapInfo`
   - Return type: `Promise<any>` → `Promise<StartWorkflowResponse>`

2. **useQuestionsStore.ts** (2 fixed)
   - `updated_cv: any` → `updated_cv: ParsedCV`
   - `currentAdaptiveQuestion: any | null` → `QuestionData | null`

---

## Best Practices

### 1. Use Type Imports

Always import types explicitly:

```typescript
// ✅ GOOD - Clear intent
import type { ParsedCV } from '~/types/api-responses'
import { ref } from 'vue'

const cv = ref<ParsedCV | null>(null)

// ❌ BAD - Mixing types and values
import { ParsedCV } from '~/types/api-responses'  // Might bundle unnecessary code
```

### 2. Define Props with Types

```typescript
// ✅ GOOD - Type-safe props
interface Props {
  question: QuestionData
  gap: GapInfo
  required?: boolean
}

const props = defineProps<Props>()

// ❌ BAD - Untyped props
const props = defineProps({
  question: Object,  // Lost all type information
  gap: Object,
  required: Boolean
})
```

### 3. Use Discriminated Unions

For states with different shapes:

```typescript
// ✅ GOOD - Type-safe state machine
type RequestState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: ParsedCV }
  | { status: 'error'; error: string }

const state = ref<RequestState>({ status: 'idle' })

// TypeScript knows data exists here
if (state.value.status === 'success') {
  console.log(state.value.data.personal_info.email) // ✅ Safe
}
```

### 4. Generic Functions

Make functions reusable with generics:

```typescript
// ✅ GOOD - Generic API caller
async function fetchApi<T>(url: string): Promise<T> {
  const response = await $fetch<T>(url, {
    method: 'POST',
    baseURL: config.public.apiBase
  })
  return response
}

// Usage with automatic type inference
const cv = await fetchApi<ParsedCV>('/api/parse-cv')
// cv is typed as ParsedCV ✅
```

### 5. Avoid Type Assertions

Type assertions bypass type checking:

```typescript
// ❌ BAD - Lying to TypeScript
const data = apiResponse as ParsedCV  // Could be wrong!

// ✅ GOOD - Runtime validation
function isParsedCV(data: unknown): data is ParsedCV {
  return (
    typeof data === 'object' &&
    data !== null &&
    'personal_info' in data &&
    'work_experience' in data
  )
}

if (isParsedCV(apiResponse)) {
  // Now TypeScript knows it's a ParsedCV
  console.log(apiResponse.personal_info.email)
}
```

### 6. Strict Null Checks

Always handle null/undefined:

```typescript
// ❌ BAD - Could crash
function getEmail(cv: ParsedCV) {
  return cv.personal_info.email.toLowerCase()  // Crashes if email is null
}

// ✅ GOOD - Safe handling
function getEmail(cv: ParsedCV): string | null {
  return cv.personal_info.email?.toLowerCase() ?? null
}
```

---

## Common Patterns

### Pattern 1: Optional Chaining

```typescript
// ✅ Safe property access
const linkedIn = cv.value?.personal_info?.social_links?.linkedin

// Equivalent to:
const linkedIn = cv.value
  ? cv.value.personal_info
    ? cv.value.personal_info.social_links
      ? cv.value.personal_info.social_links.linkedin
      : undefined
    : undefined
  : undefined
```

### Pattern 2: Nullish Coalescing

```typescript
// ✅ Provide defaults
const name = cv.personal_info.first_name ?? 'Anonymous'

// Only uses default if null/undefined (not for '', 0, false)
```

### Pattern 3: Type Guards

```typescript
// ✅ Narrow types at runtime
function isSuccessResponse(
  response: SuccessResponse | ErrorResponse
): response is SuccessResponse {
  return 'data' in response
}

if (isSuccessResponse(response)) {
  // TypeScript knows response has 'data' property
  console.log(response.data)
}
```

### Pattern 4: Mapped Types

```typescript
// ✅ Transform existing types
type Nullable<T> = {
  [P in keyof T]: T[P] | null
}

type NullableCV = Nullable<ParsedCV>
// All fields are now T | null
```

### Pattern 5: Utility Types

```typescript
// Pick - Select subset of properties
type PersonalInfo = Pick<ParsedCV, 'personal_info'>

// Omit - Exclude properties
type CVWithoutSkills = Omit<ParsedCV, 'skills'>

// Partial - Make all properties optional
type PartialCV = Partial<ParsedCV>

// Required - Make all properties required
type RequiredCV = Required<ParsedCV>

// Record - Create object type
type UserPreferences = Record<string, boolean>
```

---

## Type Checking

### Running Type Checks

```bash
# Quick type check
npx nuxi typecheck

# Use our script
./typecheck.sh

# Watch mode (for development)
npx nuxi typecheck --watch
```

### VSCode Integration

Our `.vscode/settings.json` enables:
- ✅ Real-time type checking
- ✅ Inlay hints (parameter names, types)
- ✅ Auto-imports
- ✅ Organize imports on save

### Pre-commit Hook (Recommended)

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running type check..."
npx nuxi typecheck

if [ $? -ne 0 ]; then
  echo "❌ Type check failed. Commit aborted."
  exit 1
fi

echo "✅ Type check passed"
```

---

## Troubleshooting

### Issue 1: "Property does not exist on type"

**Problem**:
```typescript
const cv: ParsedCV = apiResponse
console.log(cv.wrong_field)  // ❌ Error
```

**Solution**: Check the type definition or use optional chaining
```typescript
console.log(cv.personal_info.email)  // ✅ Correct field
```

### Issue 2: "Type 'null' is not assignable to type"

**Problem**:
```typescript
const name: string = cv.personal_info.phone  // ❌ phone is optional
```

**Solution**: Handle null/undefined
```typescript
const name: string | null = cv.personal_info.phone  // ✅
const name: string = cv.personal_info.phone ?? 'N/A'  // ✅
```

### Issue 3: "Argument of type 'any' is not assignable"

**Problem**:
```typescript
function process(data: ParsedCV) { }

const response = await $fetch('/api/parse-cv')  // Returns any
process(response)  // ❌ Error with strict mode
```

**Solution**: Type the fetch call
```typescript
const response = await $fetch<ParsedCV>('/api/parse-cv')
process(response)  // ✅ Now typed
```

### Issue 4: "Object is possibly 'null' or 'undefined'"

**Problem**:
```typescript
const store = useQuestionsStore()
const answer = store.getAnswerById('q1')
console.log(answer.answer_text)  // ❌ answer might be undefined
```

**Solution**: Check before accessing
```typescript
const answer = store.getAnswerById('q1')
if (answer) {
  console.log(answer.answer_text)  // ✅ Safe
}
// Or use optional chaining
console.log(answer?.answer_text)  // ✅ Safe
```

### Issue 5: "Type instantiation is excessively deep"

**Problem**: Circular type references or overly complex types

**Solution**: Simplify types or use `interface` instead of `type`
```typescript
// ❌ Can cause issues
type DeepType = {
  nested: DeepType
}

// ✅ Better
interface DeepType {
  nested?: DeepType
}
```

---

## TypeScript Configuration

Our `tsconfig.json` uses strict settings:

```json
{
  "compilerOptions": {
    "strict": true,                    // Enable all strict checks
    "noImplicitAny": true,            // Error on implied 'any'
    "strictNullChecks": true,         // Strict null checking
    "strictFunctionTypes": true,      // Strict function types
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,

    // Additional checks
    "noUnusedLocals": true,           // Error on unused variables
    "noUnusedParameters": true,       // Error on unused parameters
    "noImplicitReturns": true,        // All code paths return
    "noFallthroughCasesInSwitch": true
  }
}
```

---

## Migration Checklist

When adding new features or refactoring:

- [ ] Import types from centralized definitions (`types/api-responses.ts`)
- [ ] No `any` types (use `unknown` if type is truly unknown)
- [ ] Props defined with TypeScript interface, not runtime validation
- [ ] Composable return types explicitly defined
- [ ] Store actions have proper parameter and return types
- [ ] API calls typed with `$fetch<T>`
- [ ] Handle null/undefined with optional chaining or nullish coalescing
- [ ] Run `npx nuxi typecheck` before committing
- [ ] Update type definitions if API changes

---

## Resources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Vue 3 + TypeScript Guide](https://vuejs.org/guide/typescript/overview.html)
- [Nuxt TypeScript Guide](https://nuxt.com/docs/guide/concepts/typescript)
- [Pinia TypeScript Support](https://pinia.vuejs.org/core-concepts/#typescript)

---

## Type Safety Metrics

### Current Status

- ✅ **0 `any` types** in production code (down from 9)
- ✅ **15+ centralized type definitions** for API responses
- ✅ **100% type coverage** in composables and stores
- ✅ **Strict TypeScript configuration** enabled
- ✅ **VSCode integration** configured
- ✅ **Type checking script** available

### Before & After

**Before** (Technical Debt):
- 9 `any` types in critical code paths
- No centralized type definitions
- Scattered type definitions across files
- Poor IDE support

**After** (Type Safe):
- Zero `any` types
- Centralized `types/api-responses.ts`
- Consistent type usage
- Excellent IDE support with autocomplete

---

**Last Updated**: 2024-11-25
**Version**: 1.0.0
