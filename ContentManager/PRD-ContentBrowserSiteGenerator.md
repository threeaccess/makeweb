# Product Requirements Document (PRD)
## Content Browser Website Generator

**Version:** 1.0  
**Date:** February 6, 2026  
**Status:** Complete

---

## 1. Executive Summary

This document outlines the requirements for a Python-based static website generator that creates a browsable interface for content files distributed across multiple subdirectories. The tool analyzes content files, detects their types, and generates a complete static website with card-based navigation and individual content pages.

---

## 2. Purpose and Scope

### 2.1 Purpose
Create a user-friendly web interface to browse and view content files from a directory structure where each subdirectory contains a `content` file.

### 2.2 Scope
- Process 260+ subdirectories containing content files
- Automatically detect content types (Markdown, HTML, Code, Images, Text)
- Generate individual HTML pages for each content file
- Create a searchable, filterable index page
- Support embedded images and syntax-highlighted code

---

## 3. Functional Requirements

### 3.1 Content Discovery (FR-001)
**Requirement:** The system must scan all subdirectories and identify `content` files.

**Acceptance Criteria:**
- Recursively search for files named exactly `content`
- Support up to 300 subdirectories
- Handle missing or unreadable files gracefully

### 3.2 Content Type Detection (FR-002)
**Requirement:** Automatically detect and classify content types without relying on file extensions.

**Content Types to Support:**
- **Images:** JPEG, PNG, GIF, WebP (binary detection via magic bytes)
- **HTML:** Documents with `<html>` or `<!DOCTYPE html>` tags
- **Markdown:** Documents with `#` headers, `##` subheaders, or `**` bold markers
- **Code - React:** JavaScript files containing React components (`React`, `Component`, JSX patterns)
- **Code - JavaScript:** Standard JS files with `const`, `function`, or arrow functions
- **Code - Python:** Files with `def`, `import`, or `class` statements
- **Code - CSS:** Stylesheets with CSS properties (`color:`, `display:`, `margin:`)
- **JSON:** Valid JSON structure
- **XML:** Documents starting with `<?xml`
- **Text:** Plain text documents
- **Binary:** Unknown binary formats

**Discovery Through Iteration:**
- Initial implementation only checked file extensions
- **Iteration 1:** Added magic byte detection for images (JPEG: `\xff\xd8\xff`, PNG: `\x89PNG`, GIF: `GIF8`, WebP: `RIFF...WEBP`)
- **Iteration 2:** Added pattern matching for code types (React components, Python functions, CSS properties)
- **Iteration 3:** Added JSON/XML validation for structured data

### 3.3 Content Description Generation (FR-003)
**Requirement:** Generate human-readable descriptions for each content file.

**Description Rules:**
- **Markdown:** Extract title from first `# Heading` (e.g., "Article: The Importance of Core Values...")
- **HTML:** Extract from `<title>` tag or infer from content (e.g., "HTML Page: Grok API Key Validator")
- **React Code:** Extract component name from `const ComponentName =` pattern
- **Python Code:** Extract main function name from `def function_name(` pattern
- **Images:** Display format type ("JPEG Image", "PNG Image", etc.)
- **Other Types:** Display generic type description

**Discovery Through Iteration:**
- **Iteration 1:** Started with generic type descriptions only
- **Iteration 2:** Added content parsing to extract actual titles and names
- **Iteration 3:** Improved regex patterns to handle edge cases (truncation at 60 chars, fallback to generic)

### 3.4 Preview Generation (FR-004)
**Requirement:** Generate text previews for card display (max 150 characters).

**Acceptance Criteria:**
- Strip newlines and normalize whitespace
- Truncate with "..." suffix if over limit
- Handle empty content gracefully
- Images show "[Image Preview]" placeholder

### 3.5 Individual Page Generation (FR-005)
**Requirement:** Create a dedicated HTML page for each content file.

**Page Requirements:**
- Consistent layout with breadcrumb navigation
- Content-type-appropriate rendering:
  - **Images:** Base64-encoded embedded `<img>` tags
  - **HTML:** Source code view + iframe preview
  - **Markdown:** Converted to HTML (headers, bold, italic, paragraphs)
  - **Code:** Syntax-highlighted `<pre><code>` blocks
  - **JSON:** Prettified and formatted
  - **Text/Other:** Preformatted text
- Meta information display (type badges, description)
- Back navigation to index

**Discovery Through Iteration:**
- **Iteration 1:** Basic text-only display
- **Iteration 2:** Added base64 encoding for images to avoid external dependencies
- **Iteration 3:** Added dual-view for HTML (source + preview)
- **Iteration 4:** Integrated highlight.js for syntax highlighting

### 3.6 Index Page Generation (FR-006)
**Requirement:** Create main browsing interface with card-based layout.

**Requirements:**
- Grid layout responsive (1 column mobile, 2-4 columns desktop)
- Cards display:
  - Folder ID (truncated)
  - Content type badge (color-coded)
  - Description/title
  - Text preview (120 chars)
  - Subtype badge
  - "View →" link
- Show total count: "Browse 260 content files"

### 3.7 Search Functionality (FR-007)
**Requirement:** Real-time search across all content.

**Acceptance Criteria:**
- Search input field at top of page
- Real-time filtering as user types
- Search across both titles and preview text
- Case-insensitive matching
- No page reload required (JavaScript)

### 3.8 Filter Functionality (FR-008)
**Requirement:** Filter content by type.

**Filter Categories:**
- All (default)
- Articles (Markdown)
- HTML
- Code (all code types)
- Images
- Text

**Acceptance Criteria:**
- Button-based interface
- Show count in each button (e.g., "Articles (36)")
- Active state highlighting
- Instant filtering via JavaScript

---

## 4. Non-Functional Requirements

### 4.1 Performance (NFR-001)
- Generate 260 pages in under 30 seconds
- Index page load time < 2 seconds
- Individual pages < 500KB (images embedded as base64)

### 4.2 Usability (NFR-002)
- No server required (static files only)
- Works in modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design (mobile-friendly)
- No external dependencies except CDN resources (highlight.js)

### 4.3 Maintainability (NFR-003)
- Single Python script for generation
- Clean separation of concerns (detection, generation, styling)
- Well-commented code
- Modular functions for easy extension

### 4.4 Robustness (NFR-004)
- Handle encoding errors gracefully (UTF-8 with fallback)
- Skip corrupted files with error logging
- Continue processing if individual file fails
- Support binary and text content

---

## 5. Technical Requirements

### 5.1 Technology Stack
- **Language:** Python 3.6+
- **Output:** Static HTML/CSS/JS
- **Libraries:** Standard library only (no pip dependencies)
  - `os`, `re`, `json`, `html`, `pathlib`, `base64`, `datetime`
- **Frontend:** Vanilla JavaScript, CSS3
- **External CDN:** highlight.js for syntax highlighting

### 5.2 File Structure
```
website/
├── index.html              # Main browsing interface
├── styles.css              # All styling
├── {uuid}.html            # Individual content pages (260 files)
```

### 5.3 Content Processing Pipeline
1. **Discovery:** Find all `*/content` files
2. **Detection:** Analyze bytes/content to determine type
3. **Metadata Extraction:** Generate description and preview
4. **Page Generation:** Create individual HTML files
5. **Index Generation:** Create main page with all metadata
6. **Style Generation:** Create CSS file

---

## 6. UI/UX Requirements

### 6.1 Visual Design
- Clean, modern interface
- Color-coded content types:
  - Markdown: Blue (`#e0e7ff` / `#4338ca`)
  - HTML: Orange (`#fed7aa` / `#c2410c`)
  - Code: Green (`#d1fae5` / `#047857`)
  - Images: Pink (`#fce7f3` / `#be185d`)
  - Text: Gray (`#f3f4f6` / `#374151`)

### 6.2 Layout Specifications
- **Container:** Max-width 1400px, centered
- **Card Grid:** CSS Grid with `auto-fill` and `minmax(320px, 1fr)`
- **Card Structure:**
  - Header: ID (left) + Type badge (right)
  - Body: Title + Preview text
  - Footer: Subtype badge + View link
- **Spacing:** 1.5rem gap between cards, 1.25rem padding inside

### 6.3 Typography
- **Font Stack:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto...`
- **Hierarchy:**
  - Site title: 2.5rem (desktop), 1.75rem (mobile)
  - Card title: 1rem, font-weight 600
  - Body text: 0.9rem
  - Badges: 0.75rem uppercase

---

## 7. Iteration History

### Iteration 1: Basic Implementation
- Simple file extension-based type detection
- Generic descriptions only
- Text-only content display
- Basic HTML structure

### Iteration 2: Content Analysis
- Added magic byte detection for images
- Pattern matching for code types
- Content parsing to extract titles
- Improved descriptions

### Iteration 3: Enhanced Rendering
- Base64 image embedding
- Markdown to HTML conversion
- HTML source + preview dual view
- Syntax highlighting integration

### Iteration 4: UI Polish
- Color-coded type badges
- Responsive grid improvements
- Better typography
- Search and filter JavaScript

---

## 8. Success Metrics

- ✅ Process all 260 content files without errors
- ✅ Generate website in < 30 seconds
- ✅ All content types correctly identified
- ✅ Images display correctly
- ✅ Code has syntax highlighting
- ✅ Search and filter work in real-time
- ✅ Website works offline (static files)
- ✅ Mobile-responsive design

---

## 9. Future Enhancements (Out of Scope)

- Pagination for large collections (>1000 items)
- Full-text search indexing
- Content editing capabilities
- Multi-language support
- Dark mode toggle
- Export to PDF
- Content tagging/categorization

---

## 10. Appendix

### A. Content Type Detection Algorithm
```python
def detect_content_type(content_bytes):
    # Check magic bytes for images
    if content_bytes.startswith(b'\xff\xd8\xff'): return ("image", "jpeg")
    if content_bytes.startswith(b'\x89PNG'): return ("image", "png")
    
    # Decode as text
    content = content_bytes.decode('utf-8', errors='ignore')
    
    # Pattern matching for other types
    if '<html' in content.lower(): return ("html", "html")
    if content.strip().startswith('#'): return ("markdown", "markdown")
    if 'const ' in content and 'React' in content: return ("code", "react")
    # ... etc
```

### B. Markdown Conversion Rules
- `# Heading` → `<h1>Heading</h1>`
- `## Heading` → `<h2>Heading</h2>`
- `**bold**` → `<strong>bold</strong>`
- `*italic*` → `<em>italic</em>`
- `\n\n` → `</p><p>`

---

**End of Document**
