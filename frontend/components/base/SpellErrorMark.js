import { Mark } from '@tiptap/core'

export const SpellErrorMark = Mark.create({
  name: 'spellError',

  addAttributes() {
    return {
      suggestions: {
        default: [],
        parseHTML: element => {
          const suggestionsAttr = element.getAttribute('data-suggestions')
          return suggestionsAttr ? JSON.parse(suggestionsAttr) : []
        },
        renderHTML: attributes => {
          return {
            'data-suggestions': JSON.stringify(attributes.suggestions || []),
          }
        },
      },
      errorText: {
        default: '',
        parseHTML: element => element.getAttribute('data-error-text'),
        renderHTML: attributes => {
          return {
            'data-error-text': attributes.errorText || '',
          }
        },
      },
      errorIndex: {
        default: null,
        parseHTML: element => element.getAttribute('data-error-index'),
        renderHTML: attributes => {
          return {
            'data-error-index': attributes.errorIndex,
          }
        },
      },
    }
  },

  parseHTML() {
    return [
      { 
        tag: 'span[data-spell-error]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'span',
      {
        ...HTMLAttributes,
        'data-spell-error': 'true',
        class: 'spell-error-highlight',
      },
      0,
    ]
  },

  addCommands() {
    return {
      addSpellError:
        (from, to, attrs) =>
        ({ tr, dispatch }) => {
          if (dispatch) {
            tr.addMark(from, to, this.type.create(attrs))
          }
          return true
        },
      removeAllSpellErrors:
        () =>
        ({ state, dispatch }) => {
          const { tr, doc, schema } = state
          const spellErrorMark = schema.marks.spellError
          if (!spellErrorMark) return false
          
          // Remove all spell error marks from the entire document
          tr.removeMark(0, doc.content.size, spellErrorMark)
          
          if (dispatch) dispatch(tr)
          return true
        },
    }
  },
})
