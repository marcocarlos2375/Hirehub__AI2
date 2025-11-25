/**
 * HTML and SVG Sanitization Utilities
 *
 * This module provides functions to sanitize HTML and SVG content
 * to prevent XSS (Cross-Site Scripting) attacks.
 *
 * IMPORTANT: Always use these functions when rendering user-generated
 * content or API responses with v-html.
 */

import DOMPurify from 'isomorphic-dompurify'

/**
 * Sanitize HTML content to prevent XSS attacks.
 *
 * Allows common HTML tags used in resumes, cover letters, and rich text content
 * while stripping dangerous elements like scripts, event handlers, and inline styles.
 *
 * @param html - The HTML string to sanitize
 * @returns Sanitized HTML string safe for rendering with v-html
 *
 * @example
 * ```typescript
 * // In a Vue component
 * import { sanitizeHtml } from '~/utils/sanitize'
 *
 * const apiContent = '<p>Hello <script>alert("XSS")</script></p>'
 * const safe = sanitizeHtml(apiContent) // Returns: '<p>Hello </p>'
 * ```
 */
export function sanitizeHtml(html: string): string {
  if (!html) return ''

  return DOMPurify.sanitize(html, {
    // Allow common text formatting and structural tags
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'b', 'i',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li',
      'a', 'span', 'div',
      'blockquote', 'pre', 'code'
    ],

    // Allow safe attributes only
    ALLOWED_ATTR: [
      'href',      // Links
      'target',    // Link targets (_blank)
      'rel',       // Link relationships (noopener, noreferrer)
      'class'      // CSS classes for styling
    ],

    // Do not allow data-* attributes (potential attack vector)
    ALLOW_DATA_ATTR: false,

    // Return empty string for invalid/malicious input
    RETURN_DOM: false,
    RETURN_DOM_FRAGMENT: false,

    // Additional security settings
    SAFE_FOR_TEMPLATES: true,
    WHOLE_DOCUMENT: false,
    FORCE_BODY: false,

    // Keep text content from blocked tags (just remove the tags)
    KEEP_CONTENT: true
  })
}

/**
 * Sanitize SVG content (stricter than HTML).
 *
 * Used for rendering icon SVGs from dynamic sources.
 * Uses DOMPurify's SVG profile with additional restrictions.
 *
 * @param svg - The SVG string to sanitize
 * @returns Sanitized SVG string safe for rendering
 *
 * @example
 * ```typescript
 * import { sanitizeSvg } from '~/utils/sanitize'
 *
 * const iconSvg = '<svg><circle cx="10" cy="10" r="5"/></svg>'
 * const safe = sanitizeSvg(iconSvg)
 * ```
 */
export function sanitizeSvg(svg: string): string {
  if (!svg) return ''

  return DOMPurify.sanitize(svg, {
    // Use DOMPurify's built-in SVG profile
    USE_PROFILES: {
      svg: true,
      svgFilters: true
    },

    // Additional SVG-specific restrictions
    ADD_TAGS: [],  // Don't allow any additional tags beyond SVG spec
    ADD_ATTR: [],  // Don't allow any additional attributes

    // Security settings
    SAFE_FOR_TEMPLATES: true,
    RETURN_DOM: false,
    RETURN_DOM_FRAGMENT: false
  })
}

/**
 * Check if a string contains potentially dangerous HTML.
 *
 * This is a helper function to detect if sanitization changed the content,
 * which indicates potentially malicious input.
 *
 * @param html - The HTML string to check
 * @returns True if the HTML contains dangerous content
 *
 * @example
 * ```typescript
 * const userInput = '<p onclick="alert()">Click</p>'
 * if (containsDangerousHtml(userInput)) {
 *   console.warn('User attempted to inject malicious code')
 * }
 * ```
 */
export function containsDangerousHtml(html: string): boolean {
  if (!html) return false

  const sanitized = sanitizeHtml(html)

  // If sanitization changed the content length significantly,
  // it likely contained dangerous elements
  const originalLength = html.length
  const sanitizedLength = sanitized.length

  // Allow for minor whitespace differences (10% threshold)
  const threshold = originalLength * 0.1

  return Math.abs(originalLength - sanitizedLength) > threshold
}

/**
 * Sanitize text content (strips all HTML tags).
 *
 * Use this when you want to display user input as plain text
 * without any HTML formatting.
 *
 * @param text - The text to sanitize
 * @returns Plain text with all HTML tags removed
 *
 * @example
 * ```typescript
 * const input = '<p>Hello <strong>World</strong></p>'
 * const plain = sanitizeText(input) // Returns: 'Hello World'
 * ```
 */
export function sanitizeText(text: string): string {
  if (!text) return ''

  // First sanitize with KEEP_CONTENT to extract text
  const sanitized = DOMPurify.sanitize(text, {
    ALLOWED_TAGS: [],  // Remove all tags
    ALLOWED_ATTR: [],  // Remove all attributes
    KEEP_CONTENT: true // Keep text content
  })

  // DOMPurify with ALLOWED_TAGS: [] in some cases still leaves tags
  // So we do a second pass with a regex to strip any remaining tags
  return sanitized.replace(/<[^>]*>/g, '')
}
