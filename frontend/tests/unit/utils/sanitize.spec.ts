import { describe, it, expect } from 'vitest'
import { sanitizeHtml, sanitizeSvg, containsDangerousHtml, sanitizeText } from '~/utils/sanitize'

describe('Sanitization Utility', () => {
  describe('sanitizeHtml', () => {
    it('should allow safe HTML tags', () => {
      const input = '<p>Hello <strong>world</strong></p>'
      const result = sanitizeHtml(input)
      expect(result).toBe('<p>Hello <strong>world</strong></p>')
    })

    it('should remove script tags', () => {
      const input = '<p>Hello</p><script>alert("XSS")</script>'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('<script>')
      expect(result).not.toContain('alert')
      expect(result).toContain('Hello')
    })

    it('should remove onclick handlers', () => {
      const input = '<p onclick="alert(\'XSS\')">Click me</p>'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('onclick')
      expect(result).toContain('Click me')
    })

    it('should remove javascript: URLs', () => {
      const input = '<a href="javascript:alert(\'XSS\')">Link</a>'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('javascript:')
      expect(result).toContain('Link')
    })

    it('should remove data attributes', () => {
      const input = '<div data-userid="123">Content</div>'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('data-userid')
      expect(result).toContain('Content')
    })

    it('should allow safe links with target and rel', () => {
      const input = '<a href="https://example.com" target="_blank" rel="noopener">Link</a>'
      const result = sanitizeHtml(input)
      expect(result).toContain('href="https://example.com"')
      expect(result).toContain('target="_blank"')
      expect(result).toContain('rel="noopener"')
    })

    it('should remove style tags', () => {
      const input = '<style>body { background: red; }</style><p>Text</p>'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('<style>')
      expect(result).not.toContain('background')
      expect(result).toContain('Text')
    })

    it('should remove iframe tags', () => {
      const input = '<p>Text</p><iframe src="evil.com"></iframe>'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('<iframe>')
      expect(result).not.toContain('evil.com')
      expect(result).toContain('Text')
    })

    it('should handle empty string', () => {
      expect(sanitizeHtml('')).toBe('')
    })

    it('should handle plain text', () => {
      const input = 'Just plain text'
      expect(sanitizeHtml(input)).toBe('Just plain text')
    })

    it('should preserve nested allowed tags', () => {
      const input = '<div><p>Paragraph with <strong>bold</strong> and <em>italic</em></p></div>'
      const result = sanitizeHtml(input)
      expect(result).toContain('<p>')
      expect(result).toContain('<strong>')
      expect(result).toContain('<em>')
    })

    it('should remove img tags with onerror', () => {
      const input = '<img src="x" onerror="alert(\'XSS\')">'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('onerror')
      expect(result).not.toContain('alert')
    })
  })

  describe('sanitizeSvg', () => {
    it('should allow safe SVG elements', () => {
      const input = '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40"/></svg>'
      const result = sanitizeSvg(input)
      expect(result).toContain('<svg')
      expect(result).toContain('<circle')
      expect(result).toContain('cx="50"')
    })

    it('should remove script tags from SVG', () => {
      const input = '<svg><script>alert("XSS")</script><circle cx="50" cy="50" r="40"/></svg>'
      const result = sanitizeSvg(input)
      expect(result).not.toContain('<script>')
      expect(result).not.toContain('alert')
      // Note: DOMPurify SVG profile is strict and may remove entire SVG if malicious content detected
      // This is expected security behavior
    })

    it('should remove event handlers from SVG', () => {
      const input = '<svg onclick="alert(\'XSS\')"><circle cx="50" cy="50" r="40"/></svg>'
      const result = sanitizeSvg(input)
      expect(result).not.toContain('onclick')
      expect(result).toContain('<circle')
    })

    it('should handle empty SVG', () => {
      expect(sanitizeSvg('')).toBe('')
    })

    it('should allow SVG paths', () => {
      const input = '<svg><path d="M10 10 L20 20" stroke="black"/></svg>'
      const result = sanitizeSvg(input)
      expect(result).toContain('<path')
      expect(result).toContain('d="M10 10 L20 20"')
    })

    it('should allow SVG with viewBox', () => {
      const input = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
      const result = sanitizeSvg(input)
      expect(result).toContain('viewBox="0 0 100 100"')
    })
  })

  describe('containsDangerousHtml', () => {
    it('should detect script tags', () => {
      const input = '<p>Text</p><script>alert("XSS")</script>'
      expect(containsDangerousHtml(input)).toBe(true)
    })

    it('should detect onerror handlers', () => {
      const input = '<img src="x" onerror="alert(\'XSS\')">'
      expect(containsDangerousHtml(input)).toBe(true)
    })

    it('should detect onclick handlers', () => {
      const input = '<div onclick="malicious()">Click</div>'
      expect(containsDangerousHtml(input)).toBe(true)
    })

    it('should detect javascript: URLs', () => {
      const input = '<a href="javascript:alert(\'XSS\')">Link</a>'
      expect(containsDangerousHtml(input)).toBe(true)
    })

    it('should detect data: URLs', () => {
      const input = '<a href="data:text/html,<script>alert(\'XSS\')</script>">Link</a>'
      expect(containsDangerousHtml(input)).toBe(true)
    })

    it('should return false for safe HTML', () => {
      const input = '<p>Safe <strong>text</strong></p>'
      expect(containsDangerousHtml(input)).toBe(false)
    })

    it('should return false for empty string', () => {
      expect(containsDangerousHtml('')).toBe(false)
    })

    it('should return false for plain text', () => {
      expect(containsDangerousHtml('Just plain text')).toBe(false)
    })

    it('should detect iframe tags', () => {
      const input = '<iframe src="evil.com"></iframe>'
      expect(containsDangerousHtml(input)).toBe(true)
    })

    it('should detect object tags', () => {
      const input = '<object data="evil.swf"></object>'
      expect(containsDangerousHtml(input)).toBe(true)
    })

    it('should detect embed tags', () => {
      const input = '<embed src="evil.swf">'
      expect(containsDangerousHtml(input)).toBe(true)
    })
  })

  describe('sanitizeText', () => {
    it('should strip all HTML tags', () => {
      const input = '<p>Hello <strong>world</strong></p>'
      const result = sanitizeText(input)
      expect(result).toBe('Hello world')
    })

    it('should remove script tags and content', () => {
      const input = 'Text<script>alert("XSS")</script>More text'
      const result = sanitizeText(input)
      expect(result).toBe('TextMore text')
    })

    it('should handle empty string', () => {
      expect(sanitizeText('')).toBe('')
    })

    it('should preserve plain text', () => {
      const input = 'Just plain text'
      expect(sanitizeText(input)).toBe('Just plain text')
    })

    it('should remove nested tags', () => {
      const input = '<div><p>Text with <span>nested <strong>tags</strong></span></p></div>'
      const result = sanitizeText(input)
      expect(result).toBe('Text with nested tags')
    })

    it('should handle malformed HTML', () => {
      const input = '<div>Unclosed tag'
      const result = sanitizeText(input)
      expect(result).toBe('Unclosed tag')
    })
  })

  describe('Real-world XSS attack vectors', () => {
    it('should block XSS via img onerror', () => {
      const input = '<img src=x onerror="alert(document.cookie)">'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('onerror')
      expect(result).not.toContain('document.cookie')
    })

    it('should block XSS via SVG onload', () => {
      const input = '<svg onload="alert(1)">'
      const result = sanitizeSvg(input)
      expect(result).not.toContain('onload')
      expect(result).not.toContain('alert')
    })

    it('should block XSS via body onload', () => {
      const input = '<body onload="alert(1)">Text</body>'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('onload')
      expect(result).not.toContain('alert')
    })

    it('should block XSS via base64 encoded script', () => {
      const input = '<img src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('data:')
      expect(result).not.toContain('base64')
    })

    it('should block XSS via style with expression', () => {
      const input = '<div style="background: url(javascript:alert(1))">Text</div>'
      const result = sanitizeHtml(input)
      expect(result).not.toContain('javascript:')
    })
  })
})
