<template>
  <div class="hb-wysiwyg">
    <client-only>
      <div v-if="editor" class="hb-wysiwyg__container">
        <section class="hb-wysiwyg__toolbar">
          <button
            type="button"
            @click="editor.chain().focus().toggleBold().run()"
            :class="{ 'is-active': editor.isActive('bold') }"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <BoldIcon title="Bold" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().toggleItalic().run()"
            :class="{ 'is-active': editor.isActive('italic') }"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <ItalicIcon title="Italic" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().toggleUnderline().run()"
            :class="{ 'is-active': editor.isActive('underline') }"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <UnderlineIcon title="Underline" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
            :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <H1Icon title="H1" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
            :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <H2Icon title="H2" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().toggleBulletList().run()"
            :class="{ 'is-active': editor.isActive('bulletList') }"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <ListIcon title="Bullet List" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().toggleOrderedList().run()"
            :class="{ 'is-active': editor.isActive('orderedList') }"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <OrderedListIcon title="Ordered List" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().toggleBlockquote().run()"
            :class="{ 'is-active': editor.isActive('blockquote') }"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <BlockquoteIcon title="Blockquote" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().toggleCode().run()"
            :class="{ 'is-active': editor.isActive('code') }"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <CodeIcon title="Code" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().setHorizontalRule().run()"
            :disabled="disabled"
            class="hb-wysiwyg__button"
          >
            <HorizontalRuleIcon title="Horizontal Rule" />
          </button>
          <div class="hb-wysiwyg__divider"></div>
          <button
            type="button"
            @click="editor.chain().focus().undo().run()"
            :disabled="disabled || !editor.can().chain().focus().undo().run()"
            class="hb-wysiwyg__button"
          >
            <UndoIcon title="Undo" />
          </button>
          <button
            type="button"
            @click="editor.chain().focus().redo().run()"
            :disabled="disabled || !editor.can().chain().focus().redo().run()"
            class="hb-wysiwyg__button"
          >
            <RedoIcon title="Redo" />
          </button>
        </section>
        
        <div class="hb-wysiwyg__editor-wrapper">
          <EditorContent :editor="editor" />
          
          <!-- Floating Spell-Check Bubble (Grammarly-style) -->
          <div
            v-if="!disabled"
            class="hb-spellcheck-bubble"
            :class="{ 'has-errors': spellErrors.length > 0 }"
            @click.stop="checkSpelling"
            :title="isCheckingSpelling ? 'Checking...' : `Check spelling (${spellErrors.length} issues)`"
          >
            <LoadingIcon v-if="isCheckingSpelling" class="hb-spellcheck-spinner" />
            <SpellCheckIcon v-else />
            <span v-if="spellErrors.length > 0" class="error-badge">{{ spellErrors.length }}</span>
          </div>
        </div>

        <!-- Suggestions Menu -->
        <ul
          v-if="showSuggestions && currentSuggestions.length > 0"
          class="hb-suggestion-menu"
          :style="{ top: suggestionMenuPos.top + 'px', left: suggestionMenuPos.left + 'px' }"
          @click.stop
        >
          <li
            v-for="(suggestion, idx) in currentSuggestions"
            :key="idx"
            @click="applySuggestion(suggestion)"
          >
            {{ suggestion }}
          </li>
          <li class="ignore-option" @click="ignoreError">Ignore</li>
        </ul>
      </div>
      <template #fallback>
        <div class="hb-wysiwyg__placeholder">
          <textarea 
            :value="modelValue" 
            @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)" 
            :placeholder="placeholder"
            :disabled="disabled"
            class="hb-wysiwyg__textarea"
          ></textarea>
        </div>
      </template>
    </client-only>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent, Editor } from '@tiptap/vue-3'
import type { Transaction } from '@tiptap/pm/state'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'
import { SpellErrorMark } from './SpellErrorMark.js'

import BoldIcon from 'vue-material-design-icons/FormatBold.vue'
import ItalicIcon from 'vue-material-design-icons/FormatItalic.vue'
import UnderlineIcon from 'vue-material-design-icons/FormatUnderline.vue'
import H1Icon from 'vue-material-design-icons/FormatHeader1.vue'
import H2Icon from 'vue-material-design-icons/FormatHeader2.vue'
import ListIcon from 'vue-material-design-icons/FormatListBulleted.vue'
import OrderedListIcon from 'vue-material-design-icons/FormatListNumbered.vue'
import BlockquoteIcon from 'vue-material-design-icons/FormatQuoteClose.vue'
import CodeIcon from 'vue-material-design-icons/CodeTags.vue'
import HorizontalRuleIcon from 'vue-material-design-icons/Minus.vue'
import UndoIcon from 'vue-material-design-icons/Undo.vue'
import RedoIcon from 'vue-material-design-icons/Redo.vue'
import SpellCheckIcon from 'vue-material-design-icons/Spellcheck.vue'
import LoadingIcon from 'vue-material-design-icons/Loading.vue'

// Register EditorContent as a component for use in template

interface Props {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  height?: string
  toolbarVariant?: 'light' | 'primary' | 'dark'
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

interface SpellError {
  offset: number
  length: number
  replacements: Array<{ value: string }>
  context?: {
    text: string
    offset: number
    length: number
  }
}

interface SuggestionMenuPosition {
  top: number
  left: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '',
  disabled: false,
  height: '12rem',
  toolbarVariant: 'light'
})

// Computed toolbar styles based on variant
const toolbarBgColor = computed(() => {
  const variants = {
    light: 'var(--gray-100)',
    primary: 'var(--primary-400)',
    dark: 'var(--primary-800)'
  }
  return variants[props.toolbarVariant] || variants.light
})

const toolbarIconColor = computed(() => {
  const variants = {
    light: 'var(--gray-600)',
    primary: 'white',
    dark: 'white'
  }
  return variants[props.toolbarVariant] || variants.light
})

const toolbarIconActiveColor = computed(() => {
  const variants = {
    light: 'var(--primary-600)',
    primary: 'var(--primary-900)',
    dark: 'var(--primary-300)'
  }
  return variants[props.toolbarVariant] || variants.light
})

const toolbarIconActiveBg = computed(() => {
  const variants = {
    light: 'var(--primary-50)',
    primary: 'rgba(255, 255, 255, 0.2)',
    dark: 'rgba(255, 255, 255, 0.15)'
  }
  return variants[props.toolbarVariant] || variants.light
})

const toolbarIconHoverBg = computed(() => {
  const variants = {
    light: 'var(--gray-200)',
    primary: 'rgba(255, 255, 255, 0.15)',
    dark: 'rgba(255, 255, 255, 0.1)'
  }
  return variants[props.toolbarVariant] || variants.light
})

const toolbarDividerColor = computed(() => {
  const variants = {
    light: 'var(--gray-300)',
    primary: 'rgba(255, 255, 255, 0.3)',
    dark: 'rgba(255, 255, 255, 0.2)'
  }
  return variants[props.toolbarVariant] || variants.light
})

const emit = defineEmits<Emits>()

// Spell check state
const isCheckingSpelling = ref<boolean>(false)
const showSpellErrors = ref<boolean>(false)
const spellErrors = ref<SpellError[]>([])
const showSuggestions = ref<boolean>(false)
const currentSuggestions = ref<string[]>([])
const currentErrorIndex = ref<number | null>(null)
const suggestionMenuPos = ref<SuggestionMenuPosition>({ top: 0, left: 0 })
const lastWordCount = ref<number>(0)
const selectedErrorSpan = ref<HTMLElement | null>(null)
const selectedErrorPos = ref<{ errorText?: string }>({ errorText: undefined })
const isApplyingSuggestion = ref<boolean>(false) // Flag to prevent clearing during suggestion application

// Plugin key for spell-check decorations
const spellCheckPluginKey = new PluginKey('spellCheck')

/**
 * Spell-Check Extension using TipTap/ProseMirror Decorations
 * 
 * This creates a proper TipTap extension with decoration support
 */
const SpellCheckExtension = {
  name: 'spellCheck',
  
  addProseMirrorPlugins() {
    console.log('🏗️ Creating spell-check plugin via TipTap extension')
    
    return [
      new Plugin({
        key: spellCheckPluginKey,
        
        state: {
          init() {
            console.log('🔌 Spell-check plugin state initialized')
            return DecorationSet.empty
          },
          
          apply(tr, oldSet) {
            console.log('⚙️ Plugin apply() called, docChanged:', tr.docChanged)
            
            // Check if we have new spell errors to apply
            const meta = tr.getMeta(spellCheckPluginKey)
            if (meta && meta.decorations !== undefined) {
              console.log('🎨 New decorations from meta:', meta.decorations.find().length)
              return meta.decorations
            }
            
            // Map decorations to new document positions
            const mapped = oldSet.map(tr.mapping, tr.doc)
            console.log('🗺️ Remapped decorations:', mapped.find().length)
            return mapped
          }
        },
        
        props: {
          decorations(state) {
            console.log('📐 Plugin decorations() prop called')
            const pluginState = spellCheckPluginKey.getState(state)
            const decos = pluginState.find()
            console.log('📐 Returning decorations:', decos.length)
            
            if (decos.length > 0) {
              console.log('📐 Sample decoration:', decos[0])
            }
            
            return pluginState
          }
        }
      })
    ]
  }
}

const editor = useEditor({
  content: props.modelValue,
  editable: !props.disabled,
  onUpdate: ({ editor, transaction }: { editor: Editor; transaction: Transaction }) => {
    const html = editor.getHTML()
    console.log('HbWysiwyg update:', html?.substring(0, 50) || '(empty)')

    emit('update:modelValue', html)

    // Clear highlights if user types new content (but not when applying suggestions)
    if (transaction.docChanged && !isApplyingSuggestion.value) {
      // User made a manual change, clear spell errors
      if (spellErrors.value.length > 0) {
        console.log('🧹 User typed - clearing all spell errors')
        spellErrors.value = []
        persistentErrors.value = []
        // Clear highlights using TipTap command
        // @ts-expect-error - removeAllSpellErrors is a custom command from SpellErrorMark extension
        editor.chain().focus().removeAllSpellErrors().run()
      }
    }
  },
  extensions: [
    StarterKit,
    Underline,
    SpellErrorMark,
    Placeholder.configure({
      placeholder: props.placeholder,
    }),
  ],
  editorProps: {
    attributes: {
      class: 'hb-wysiwyg__editor',
    },
    handleDOMEvents: {
      click: (view: any, event: Event) => {
        handleEditorClick(view, event)
        return false
      }
    }
  }
})

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.getHTML() !== newValue) {
    editor.value.commands.setContent(newValue || '', false)
  }
})

// Watch for disabled changes
watch(() => props.disabled, (newDisabled) => {
  if (editor.value) {
    editor.value.setEditable(!newDisabled)
  }
})

// Watch for placeholder changes
watch(() => props.placeholder, (newPlaceholder) => {
  if (editor.value) {
    const placeholderExt = editor.value.extensionManager.extensions.find(
      ext => ext.name === 'placeholder'
    )
    if (placeholderExt) {
      placeholderExt.options.placeholder = newPlaceholder
    }
  }
})

// Helper: Convert text offset to ProseMirror position
// Build a complete mapping between text offsets and ProseMirror positions
const textOffsetToPos = (doc: any, offset: number): number | null => {
  // Build a map: text offset -> prosemirror position
  const offsetMap = []
  let textOffset = 0
  let isFirstBlock = true
  
  doc.descendants((node, pos) => {
    if (node.isBlock) {
      // Add newline separator between blocks (matching textBetween '\n' separator)
      if (!isFirstBlock) {
        // The newline doesn't exist in ProseMirror, so we map it to the start of the next block
        offsetMap.push({ offset: textOffset, pos: pos + 1 })
        textOffset += 1
      }
      isFirstBlock = false
    } else if (node.isText) {
      // Map each character in the text node
      for (let i = 0; i < node.text.length; i++) {
        offsetMap.push({ offset: textOffset, pos: pos + i })
        textOffset += 1
      }
    }
  })
  
  // Find the position for this offset
  const mapping = offsetMap.find(m => m.offset === offset)
  const result = mapping ? mapping.pos : null
  
  // Log the mapping for debugging (only for the first call)
  if (offset <= 320 && offset >= 300) {
    console.log(`  📍 Text offset ${offset} → ProseMirror pos ${result}`)
    // Show nearby mappings
    const nearby = offsetMap.filter(m => m.offset >= offset - 2 && m.offset <= offset + 2)
    console.log(`    Nearby mappings:`, nearby)
  }
  
  if (!result && result !== 0) {
    console.warn(`  ⚠️ Could not find position for offset ${offset}`)
  }
  
  return result
}

// Store errors for persistent highlighting
const persistentErrors = ref<SpellError[]>([])

// Apply spell-check highlights using TipTap Mark commands
const applySpellCheckDecorations = (errors: SpellError[]): SpellError[] => {
  if (!editor.value) {
    console.warn('⚠️ Editor not ready')
    return []
  }
  
  persistentErrors.value = errors
  
  // Clear all previous spell error marks
  // @ts-expect-error - removeAllSpellErrors is a custom command from SpellErrorMark extension
  editor.value.chain().focus().removeAllSpellErrors().run()
  
  if (!errors.length) {
    console.log('🧹 Cleared spell-check highlights')
    return []
  }
  
  console.log(`📍 Applying highlights for ${errors.length} errors using TipTap Marks...`)
  
  const { state } = editor.value
  const doc = state.doc
  const fullText = doc.textBetween(0, doc.content.size, '\n', ' ')
  console.log(`📄 Document text: "${fullText.substring(0, 150)}..."`)
  
  // Apply each error as a TipTap Mark and track successful applications
  const successfulErrors: SpellError[] = []

  errors.forEach((error: SpellError, index: number) => {
    const { offset, length, replacements } = error
    const suggestions = replacements.map(r => r.value).slice(0, 5)
    const errorText = fullText.substring(offset, offset + length)
    
    // Convert text offset to ProseMirror position
    const from = textOffsetToPos(doc, offset)
    const to = textOffsetToPos(doc, offset + length)
    
    if (from === null || to === null || from === undefined || to === undefined) {
      console.warn(`  ✗ Error ${index}: Could not find positions for "${errorText}"`)
      return
    }
    
    // Verify the text at these positions
    const textAtPos = doc.textBetween(from, to, ' ')
    
    if (textAtPos !== errorText) {
      console.warn(`  ✗ Error ${index}: MISMATCH! Expected "${errorText}", got "${textAtPos}" (offset ${offset}-${offset+length} → pos ${from}-${to})`)
      return
    }
    
    // Apply the spell error mark using TipTap command
    // @ts-expect-error - addSpellError is a custom command from SpellErrorMark extension
    editor.value.commands.addSpellError(from, to, {
      suggestions,
      errorText,
      errorIndex: successfulErrors.length // Use new index
    })
    
    // Store the successfully applied error
    successfulErrors.push(error)
    
    console.log(`  ✓ Error ${successfulErrors.length - 1}: Marked "${errorText}" at pos ${from}-${to}`)
  })
  
  // Update persistentErrors with only the successfully applied errors
  persistentErrors.value = successfulErrors
  
  // Verify marks were applied
  setTimeout(() => {
    const highlightedElements = document.querySelectorAll('.spell-error-highlight')
    console.log(`🔍 DOM check: Found ${highlightedElements.length} highlighted elements`)
    if (highlightedElements.length > 0) {
      console.log('✅ Marks persisted successfully!')
    } else {
      console.warn('⚠️ No marks found in DOM')
    }
  }, 100)
  
  // Return the successful errors
  return successfulErrors
}

// Spell check function (Grammarly-style with formatting preservation)
const checkSpelling = async (): Promise<void> => {
  if (!editor.value || isCheckingSpelling.value) return
  
  isCheckingSpelling.value = true
  
  // COMPLETE RESET: Clear all previous state
  closeSuggestions()
  spellErrors.value = []
  persistentErrors.value = []
  showSpellErrors.value = false
  
  console.log('🔄 Starting fresh spell check...')
  
  try {
    // Use textBetween to match what applySpellCheckDecorations uses
    const doc = editor.value.state.doc
    const text = doc.textBetween(0, doc.content.size, '\n', ' ')
    
    console.log('📝 Text being checked:', text.substring(0, 100) + '...')
    console.log('📏 Text length:', text.length)
    
    if (!text.trim()) {
      isCheckingSpelling.value = false
      return
    }
    
    // Call LanguageTool API
    // NOTE: Replace useRuntimeConfig with your environment config
    // For Vite: import.meta.env.VITE_LANGUAGETOOL_API_URL
    // @ts-expect-error - useRuntimeConfig is auto-imported by Nuxt
    const config = useRuntimeConfig()
    const apiUrl = config.public.languageToolApiUrl || 'https://api.languagetool.org/v2/check'
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        text: text,
        language: 'en-US',
      }),
    })
    
    if (!response.ok) {
      throw new Error('Spell check failed')
    }
    
    const data: { matches: SpellError[] } = await response.json()
    const allMatches: SpellError[] = data.matches || []
    
    // Apply decorations and get successfully applied errors
    if (allMatches.length > 0) {
      const successfulErrors = applySpellCheckDecorations(allMatches)
      spellErrors.value = successfulErrors // Only store successfully applied errors
      console.log(`✓ Found ${allMatches.length} issues, successfully marked ${successfulErrors.length}`)
    } else {
      applySpellCheckDecorations([]) // Clear decorations
      spellErrors.value = []
      console.log('✓ No spelling or grammar errors found!')
    }
    
    showSpellErrors.value = true
  } catch (error) {
    console.error('Spell check error:', error)
  } finally {
    isCheckingSpelling.value = false
  }
}

// Editor click handler for spell-error overlay highlights
const handleEditorClick = (view: any, event: Event): boolean | void => {
  const target = event.target as HTMLElement
  
  // Check if clicked on a spell-error highlight overlay
  if (target && target.classList && target.classList.contains('spell-error-highlight')) {
    event.stopPropagation()
    event.preventDefault()
    
    try {
      const suggestionsAttr = target.getAttribute('data-suggestions')
      const suggestions = suggestionsAttr ? JSON.parse(suggestionsAttr) : []
      const errorIndex = parseInt(target.getAttribute('data-error-index'))
      const errorText = target.getAttribute('data-error-text')
      
      if (suggestions.length === 0) return
      
      currentSuggestions.value = suggestions
      currentErrorIndex.value = errorIndex
      
      // Store reference to the clicked highlight and error text
      selectedErrorSpan.value = target
      selectedErrorPos.value = { errorText }
      
      // Position the menu near the clicked word
      const rect = target.getBoundingClientRect()
      const containerRect = document.querySelector('.hb-wysiwyg')?.getBoundingClientRect()
      
      if (containerRect) {
        let top = rect.bottom - containerRect.top + 5
        let left = rect.left - containerRect.left
        
        // Ensure menu doesn't go beyond container bounds
        const menuWidth = 250
        const menuHeight = 200
        
        if (left + menuWidth > containerRect.width) {
          left = containerRect.width - menuWidth - 10
        }
        if (left < 0) left = 10
        
        if (top + menuHeight > containerRect.height) {
          top = rect.top - containerRect.top - menuHeight - 5
        }
        
        suggestionMenuPos.value = { top, left }
        showSuggestions.value = true
      }
    } catch (error) {
      console.error('Error parsing suggestions:', error)
    }
  } else if (!target.closest('.hb-suggestion-menu')) {
    closeSuggestions()
  }
  
  return false // Prevent default
}

// Document-level click handler (fallback)
const handleDocumentClick = (event: MouseEvent): void => {
  const target = event.target as HTMLElement
  
  if (!target.closest('.hb-wysiwyg') && !target.closest('.hb-suggestion-menu')) {
    closeSuggestions()
  }
}

// Apply selected suggestion
const applySuggestion = (suggestion: string): void => {
  if (!selectedErrorSpan.value || !selectedErrorPos.value?.errorText) return
  
  // Set flag to prevent onUpdate from clearing errors
  isApplyingSuggestion.value = true
  
  try {
    const errorText = selectedErrorPos.value.errorText
    
    if (!editor.value) return
    
    const { state, view } = editor.value
    const { doc, tr } = state
    
    // Find the position of the error mark in the document
    let errorPos = null
    let errorFrom = null
    let errorTo = null
    
    doc.descendants((node, pos) => {
      if (errorPos) return false // Already found
      
      if (node.isText) {
        // Check if this text node has the spellError mark
        const spellErrorMark = node.marks.find(mark => mark.type.name === 'spellError')
        
        if (spellErrorMark && spellErrorMark.attrs.errorText === errorText) {
          errorFrom = pos
          errorTo = pos + node.nodeSize
          errorPos = { from: errorFrom, to: errorTo }
          return false
        }
      }
    })
    
    if (errorPos) {
      console.log(`✏️ Replacing "${errorText}" with "${suggestion}" at pos ${errorPos.from}-${errorPos.to}`)
      
      // First remove the spellError mark from the range
      const { tr } = editor.value.state
      const spellErrorMarkType = editor.value.schema.marks.spellError
      tr.removeMark(errorPos.from, errorPos.to, spellErrorMarkType)
      editor.value.view.dispatch(tr)
      
      // Then replace the text (without the mark)
      editor.value.chain()
        .focus()
        .setTextSelection({ from: errorPos.from, to: errorPos.to })
        .insertContent(suggestion)
        .run()
      
      // Remove this error from the list by matching the error text
      // LanguageTool errors have a 'context' object with the matched text
      const errorIndexInArray = spellErrors.value.findIndex(err => {
        // Extract the error text from the context
        const contextText = err.context?.text
        if (contextText) {
          const contextOffset = err.context.offset
          const contextLength = err.context.length
          const extractedError = contextText.substring(contextOffset, contextOffset + contextLength)
          return extractedError === errorText
        }
        return false
      })
      
      if (errorIndexInArray !== -1) {
        spellErrors.value.splice(errorIndexInArray, 1)
        persistentErrors.value = [...spellErrors.value]
        console.log(`✓ Removed error for "${errorText}", ${spellErrors.value.length} errors remaining`)
      } else {
        console.warn(`⚠️ Could not find error in array for "${errorText}"`)
      }
    } else {
      console.warn(`⚠️ Could not find error mark for "${errorText}"`)
    }
  } catch (error) {
    console.error('Error applying suggestion:', error)
  } finally {
    // Reset flag after a short delay to ensure update has processed
    setTimeout(() => {
      isApplyingSuggestion.value = false
    }, 100)
  }
  
  closeSuggestions()
}

// Ignore error (removes highlight without changing text)
const ignoreError = (): void => {
  if (currentErrorIndex.value === null || !selectedErrorPos.value?.errorText) return
  
  // Set flag to prevent onUpdate from clearing errors
  isApplyingSuggestion.value = true
  
  try {
    const errorText = selectedErrorPos.value.errorText
    
    if (!editor.value) return
    
    const { state } = editor.value
    const { doc } = state
    
    // Find the position of the error mark in the document
    let errorFrom = null
    let errorTo = null
    
    doc.descendants((node, pos) => {
      if (errorFrom !== null) return false // Already found
      
      if (node.isText) {
        // Check if this text node has the spellError mark
        const spellErrorMark = node.marks.find(mark => mark.type.name === 'spellError')
        
        if (spellErrorMark && spellErrorMark.attrs.errorText === errorText) {
          errorFrom = pos
          errorTo = pos + node.nodeSize
          return false
        }
      }
    })
    
    if (errorFrom !== null && errorTo !== null) {
      console.log(`🚫 Ignoring error "${errorText}" at pos ${errorFrom}-${errorTo}`)
      
      // Remove the mark from this range using TipTap transaction
      const { tr } = editor.value.state
      const spellErrorMarkType = editor.value.schema.marks.spellError
      
      tr.removeMark(errorFrom, errorTo, spellErrorMarkType)
      editor.value.view.dispatch(tr)
      
      // Remove from error list by matching the error text
      const errorIndexInArray = spellErrors.value.findIndex(err => {
        const contextText = err.context?.text
        if (contextText) {
          const contextOffset = err.context.offset
          const contextLength = err.context.length
          const extractedError = contextText.substring(contextOffset, contextOffset + contextLength)
          return extractedError === errorText
        }
        return false
      })
      
      if (errorIndexInArray !== -1) {
        spellErrors.value.splice(errorIndexInArray, 1)
        persistentErrors.value = [...spellErrors.value]
        console.log(`✓ Ignored error "${errorText}", ${spellErrors.value.length} errors remaining`)
      } else {
        console.warn(`⚠️ Could not find error in array for "${errorText}"`)
      }
    } else {
      console.warn(`⚠️ Could not find error mark for "${errorText}"`)
    }
    
    // Focus editor
    if (editor.value) {
      editor.value.commands.focus()
    }
  } catch (error) {
    console.error('Error ignoring error:', error)
  } finally {
    // Reset flag after a short delay
    setTimeout(() => {
      isApplyingSuggestion.value = false
    }, 100)
  }
  
  closeSuggestions()
}

// Close suggestions menu
const closeSuggestions = (): void => {
  showSuggestions.value = false
  currentSuggestions.value = []
  currentErrorIndex.value = null
  selectedErrorSpan.value = null
}

// Auto-check after certain word count
watch(() => editor.value?.getText(), (text) => {
  if (!text) return
  
  const wordCount = text.trim().split(/\s+/).filter(w => w.length > 0).length
  
  // Check every 50 words
  if (wordCount > 0 && wordCount % 50 === 0 && wordCount !== lastWordCount.value) {
    lastWordCount.value = wordCount
    checkSpelling()
  }
})

// Delegated click handler for spell-error highlight overlays
const handleEditorWrapperClick = (event: MouseEvent): void => {
  const target = event.target as HTMLElement
  
  if (target && target.classList && target.classList.contains('spell-error-highlight')) {
    handleEditorClick(null, event)
  }
}

// Register event listeners on mount
onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  
  // Add delegated listener for spell-error spans
  const editorWrapper = document.querySelector('.hb-wysiwyg__editor-wrapper')
  if (editorWrapper) {
    editorWrapper.addEventListener('click', handleEditorWrapperClick)
  }
})

onBeforeUnmount(() => {
  // Remove document click handler
  document.removeEventListener('click', handleDocumentClick)
  
  // Remove delegated listener
  const editorWrapper = document.querySelector('.hb-wysiwyg__editor-wrapper')
  if (editorWrapper) {
    editorWrapper.removeEventListener('click', handleEditorWrapperClick)
  }
  
  if (editor.value) {
    editor.value.destroy()
  }
})
</script>

<style>
/* IMPORTANT: Global styles for spell-error inline highlights */
/* These MUST be global (not scoped) to work correctly */

/* Target mark elements created by TipTap */
mark.spell-error-highlight,
.spell-error-highlight {
  /* Red wavy underline with 1px thickness */
  text-decoration-line: underline !important;
  text-decoration-style: wavy !important;
  text-decoration-color: #ef4444 !important;
  text-decoration-thickness: 1px !important;
  text-underline-offset: 3px !important;
  text-decoration-skip-ink: none !important;
  
  /* Styling */
  background: transparent !important;
  cursor: pointer !important;
  transition: background-color 0.15s ease !important;
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
  font: inherit !important;
  color: inherit !important;
}

mark.spell-error-highlight:hover,
.spell-error-highlight:hover {
  background-color: rgba(239, 68, 68, 0.1) !important;
  border-radius: 2px !important;
}

/* Fallback for browsers without wavy underline support */
@supports not (text-decoration-style: wavy) {
  mark.spell-error-highlight,
  .spell-error-highlight {
    border-bottom: 1px solid #ef4444 !important;
    text-decoration-line: none !important;
  }
}
</style>

<style scoped>
.hb-wysiwyg {
  position: relative;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-xl);
  background: white;
  font-family: var(--font-body);
  overflow: visible;
}

.hb-wysiwyg__container {
  position: relative;
  overflow: visible;
}

.hb-wysiwyg__editor-wrapper {
  position: relative !important;
  overflow: visible !important;
}

.hb-wysiwyg__toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.25rem;
  background: v-bind(toolbarBgColor);
  border-bottom: 1px solid var(--gray-200);
  padding: 0 var(--spacing-4);
  height: var(--input-height);
  min-height: var(--input-height);
  border-top-left-radius: var(--radius-xl);
  border-top-right-radius: var(--radius-xl);
}

.hb-wysiwyg__button {
  padding: 0.375rem;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: v-bind(toolbarIconColor);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.hb-wysiwyg__button:hover:not(:disabled) {
  background-color: v-bind(toolbarIconHoverBg);
}

.hb-wysiwyg__button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.hb-wysiwyg__button.is-active {
  background-color: v-bind(toolbarIconActiveBg);
  color: v-bind(toolbarIconActiveColor);
}

.hb-wysiwyg__divider {
  width: 1px;
  height: 24px;
  background: v-bind(toolbarDividerColor);
  margin: 0 0.25rem;
}

/* Floating Spell-Check Bubble (Grammarly-style) */
.hb-spellcheck-bubble {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: var(--primary-500);
  color: white;
  border-radius: 10px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 100;
}

.hb-spellcheck-bubble:hover {
  transform: scale(1.1);
}

.hb-spellcheck-bubble.has-errors {
  background: var(--danger-500);
  animation: pulse 2s infinite;
}

.hb-spellcheck-bubble :deep(svg) {
  width: 20px;
  height: 20px;
}

.hb-spellcheck-spinner {
  animation: spin 1s linear infinite;
}

.error-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: white;
  color: var(--danger-500);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  border: 2px solid var(--danger-500);
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

/* Suggestions Menu */
.hb-suggestion-menu {
  position: absolute;
  background: white;
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  list-style: none;
  padding: 0.25rem 0;
  margin: 0;
  min-width: 160px;
  max-width: 250px;
}

.hb-suggestion-menu li {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  white-space: nowrap;
  font-size: var(--text-sm);
  color: var(--gray-800);
  transition: background-color 0.15s ease;
}

.hb-suggestion-menu li:hover {
  background: var(--primary-50);
  color: var(--primary-600);
}

.hb-suggestion-menu li.ignore-option {
  border-top: 1px solid var(--gray-200);
  color: var(--gray-600);
  font-style: italic;
}

.hb-suggestion-menu li.ignore-option:hover {
  background: var(--gray-100);
  color: var(--gray-800);
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor) {
  min-height: 120px;
  height: v-bind(height);
  max-height: v-bind(height);
  overflow-y: auto;
  padding: 0.75rem 1rem;
  padding-bottom: 3rem;
  font-size: var(--text-sm);
  color: var(--gray-600);
  font-weight: 400;
  outline: none;
  font-family: var(--font-heading);
  border-bottom-left-radius: var(--radius-xl);
  border-bottom-right-radius: var(--radius-xl);
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor p) {
  margin: 0.5rem 0;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor p:first-child) {
  margin-top: 0;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor p:last-child) {
  margin-bottom: 0;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor ul),
.hb-wysiwyg :deep(.hb-wysiwyg__editor ol) {
  padding-left: 1.5rem;
  margin: 0.5rem 0;
  list-style-position: outside; /* Fixed: outside keeps text aligned next to bullet */
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor ul) {
  list-style-type: disc;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor ol) {
  list-style-type: decimal;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor li) {
  margin: 0.25rem 0;
  display: list-item;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor h1) {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 1rem 0 0.5rem;
  line-height: 1.2;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor h2) {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0.875rem 0 0.5rem;
  line-height: 1.3;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor blockquote) {
  border-left: 3px solid var(--gray-300);
  padding-left: 1rem;
  margin: 0.5rem 0;
  color: var(--gray-600);
  font-style: italic;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor code) {
  background: var(--gray-100);
  border-radius: var(--radius-sm);
  padding: 0.125rem 0.375rem;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  color: var(--gray-800);
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor hr) {
  border: none;
  border-top: 2px solid var(--gray-200);
  margin: 1rem 0;
}

.hb-wysiwyg :deep(.hb-wysiwyg__editor p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: var(--gray-400);
  pointer-events: none;
  height: 0;
}

.hb-wysiwyg__textarea {
  width: 100%;
  min-height: 120px;
  padding: 0.75rem 1rem;
  font-size: var(--text-sm);
  color: var(--gray-800);
  border: none;
  outline: none;
  resize: vertical;
  font-family: var(--font-heading) !important;
}

.hb-wysiwyg__placeholder {
  border-radius: var(--radius-md);
  background: white;
  min-height: 125px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .hb-wysiwyg__toolbar {
    padding: 0 var(--spacing-2);
    height: auto;
    min-height: auto;
    flex-wrap: wrap;
    gap: 0.125rem;
  }

  .hb-wysiwyg__button {
    padding: 0.25rem;
  }

  .hb-wysiwyg__button :deep(svg) {
    width: 18px;
    height: 18px;
  }

  .hb-wysiwyg__divider {
    height: 20px;
  }

  .hb-wysiwyg :deep(.hb-wysiwyg__editor) {
    padding: 0.5rem 0.75rem;
    padding-bottom: 2.5rem;
    font-size: 0.875rem;
  }

  .hb-spellcheck-bubble {
    bottom: 8px;
    right: 8px;
    width: 36px;
    height: 36px;
  }

  .hb-spellcheck-bubble :deep(svg) {
    width: 18px;
    height: 18px;
  }

  .error-badge {
    width: 18px;
    height: 18px;
    font-size: 10px;
  }
}

@media (max-width: 480px) {
  .hb-wysiwyg__toolbar {
    gap: 0.0625rem;
  }

  .hb-wysiwyg__button {
    padding: 0.1875rem;
  }

  .hb-wysiwyg__button :deep(svg) {
    width: 16px;
    height: 16px;
  }

  .hb-wysiwyg :deep(.hb-wysiwyg__editor) {
    padding: 0.5rem;
    padding-bottom: 2rem;
    font-size: 0.813rem;
  }

  .hb-spellcheck-bubble {
    width: 32px;
    height: 32px;
  }

  .hb-suggestion-menu {
    min-width: 140px;
    max-width: 200px;
  }

  .hb-suggestion-menu li {
    padding: 0.375rem 0.5rem;
    font-size: 0.813rem;
  }
}
</style>
