# Notes Theme System - Documentation

## Overview
Complete documentation for the centralized, client-side theme management system.

**Version:** 3.0  
**Last Updated:** 2026-02-01  
**Status:** Production Ready

---

## 🎨 Client-Side Theme Architecture (v3.0)

### Major Change: Client-Side Theme Switching

**Before (Server-Side):**
- Theme hardcoded into HTML at generation time
- Required running scripts to change themes
- One theme per page, baked in

**After (Client-Side):**
- All themes loaded with every page
- Users switch themes instantly via dropdown
- No page regeneration needed
- Auto-discovery of new themes

---

## How It Works

### 1. **All Themes Loaded**
Every HTML page loads CSS for ALL themes:
```html
<link rel="stylesheet" href=".../theme-modern.css">
<link rel="stylesheet" href=".../theme-minimal.css">
<link rel="stylesheet" href=".../theme-modal.css">
<link rel="stylesheet" href=".../theme-print.css">
```

### 2. **Theme Scoping with data-theme-name**
Each theme uses CSS attribute selectors:
```css
[data-theme-name="modern"] {
  --accent-primary: #6366f1;
  /* theme variables */
}

[data-theme-name="modern"][data-color-scheme="dark"] {
  /* dark mode overrides */
}
```

### 3. **JavaScript Switching**
```javascript
// Theme selector changes data-theme-name
html.setAttribute('data-theme-name', 'modal');

// Light/dark toggle changes data-color-scheme
html.setAttribute('data-color-scheme', 'dark');
```

### 4. **Persistence**
- `localStorage['theme-name']` - Stores selected theme
- `localStorage['color-scheme']` - Stores light/dark preference
- Both saved independently

---

## File Structure

```
~/notes/styles/
├── core.css                    # Foundation layer (variables, reset, utilities)
├── index.css                   # Index page specific styles
├── content.css                 # Content page specific styles
├── theme-modern.css            # Modern theme (indigo/violet/pink)
├── theme-minimal.css           # Minimal theme (clean, simple)
├── theme-modal.css             # Modal theme (dark, sleek, blue)
└── theme-print.css             # Print theme (no shadows, high contrast)

~/tools/templates/
├── index_template.html         # Index page template
└── content_template.html       # Content page template

~/tools/
├── make_web.py                 # Markdown to HTML converter
├── add2notes.py                # Notes registry manager
├── update-pages                # Wrapper for migration tool
└── themes.json                 # Theme metadata (optional overrides)
```

---

## Adding a New Theme

### Step 1: Create Theme CSS File
Create `~/notes/styles/theme-yourname.css`:

```css
/* ============================================
   THEME-YOURNAME.CSS
   Description of your theme
   ============================================ */

/* Light Mode */
[data-theme-name="yourname"] {
  --accent-primary: #your-color;
  --accent-secondary: #your-color-2;
  --gradient-header: linear-gradient(...);
  --shadow-glow: ...;
  /* Add your custom variables */
}

/* Dark Mode */
[data-theme-name="yourname"][data-color-scheme="dark"] {
  /* Dark mode overrides */
}

/* Component Styles */
[data-theme-name="yourname"] .header-badge {
  /* Your styles */
}

/* IMPORTANT: Always specify text color when using light backgrounds! */
[data-theme-name="yourname"] pre,
[data-theme-name="yourname"] code {
  color: var(--text-primary); /* Ensures contrast */
}
```

### Step 2: Reload Page
No scripts needed! The theme automatically appears in the selector.

---

## Theme Selector UI

### Location
In the header card, next to the light/dark toggle:
```html
<select id="theme-selector">
  <option value="modern">Modern Indigo</option>
  <option value="minimal">Minimal Clean</option>
  <option value="modal">Modal</option>
  <option value="print">Print Optimized</option>
  <!-- New themes appear here automatically -->
</select>
```

### Usage
1. **Select theme** from dropdown → Instant switch
2. **Toggle light/dark** with sun/moon buttons
3. **Both preferences saved** automatically

---

## Available Themes

### Modern (Default)
- **Colors:** Indigo, violet, pink gradients
- **Style:** Colorful, contemporary, eye-catching
- **Best for:** General use, showing off

### Minimal
- **Colors:** Clean blue accent, neutral grays
- **Style:** No gradients, simple, professional
- **Best for:** Reading, documentation, focus

### Modal
- **Colors:** Deep dark backgrounds, bright blue highlights
- **Style:** Dark, sleek, modern aesthetic
- **Best for:** Dark mode lovers, modern UI fans

### Print
- **Colors:** Black/white, maximum contrast
- **Style:** No shadows, compact spacing
- **Best for:** Printing, accessibility

---

## Important CSS Rules

### 1. **Code Block Contrast Rule**
When overriding `pre` or `code` backgrounds to use light colors, **MUST** specify text color:

```css
/* ❌ BAD - invisible text in some modes */
[data-theme-name="your-theme"] pre {
  background: var(--bg-secondary);
}

/* ✅ GOOD - proper contrast */
[data-theme-name="your-theme"] pre {
  background: var(--bg-secondary);
  color: var(--text-primary); /* Ensures contrast */
}
```

**Why:** `var(--text-primary)` automatically provides:
- Light mode: Dark text on light background
- Dark mode: Light text on dark background

### 2. **Theme Scoping Required**
All theme CSS must be scoped to `[data-theme-name="xxx"]`:

```css
/* ❌ BAD - affects all themes */
.header-badge {
  background: purple;
}

/* ✅ GOOD - only affects your theme */
[data-theme-name="yourname"] .header-badge {
  background: purple;
}
```

### 3. **Dark Mode Support**
Always provide dark mode variant:

```css
[data-theme-name="yourname"] {
  /* Light mode colors */
}

[data-theme-name="yourname"][data-color-scheme="dark"] {
  /* Dark mode colors */
}
```

---

## CSS Architecture

### Three-Layer System

**Layer 1: Core (core.css)**
- CSS custom properties (variables)
- CSS reset and base styles
- Utility classes
- Theme switching JavaScript
- Responsive breakpoints

**Layer 2: Page Type (index.css / content.css)**
- Page-specific layouts
- Component variations
- Index table styling
- Content TOC styling

**Layer 3: Theme (theme-*.css)**
- Color schemes
- Visual personality
- Theme-specific effects

### Variable Categories

```css
/* Colors */
--bg-primary, --bg-secondary, --bg-tertiary
--surface, --surface-elevated, --surface-hover
--text-primary, --text-secondary, --text-tertiary, --text-muted
--accent-primary, --accent-secondary, --accent-tertiary, --accent-hover
--border-light, --border-medium, --border-strong

/* Typography */
--font-sans, --font-mono

/* Effects */
--shadow-sm, --shadow-md, --shadow-lg, --shadow-xl, --shadow-glow
--radius-sm, --radius-md, --radius-lg, --radius-xl
--transition-fast, --transition-base, --transition-slow
```

---

## Python Script Changes

### make_web.py
- Auto-discovers themes from `~/notes/styles/`
- Loads all theme CSS files in generated HTML
- Generates theme selector dropdown
- Passes theme list to templates

### add2notes.py
- Same auto-discovery as make_web.py
- Regenerates index with all themes available
- No more `set-theme` command (not needed!)

### Auto-Discovery Function
```python
def discover_themes() -> List[dict]:
    """Scan styles directory for theme-*.css files."""
    themes = []
    for css_file in sorted(STYLES_DIR.glob("theme-*.css")):
        theme_id = css_file.stem.replace("theme-", "")
        themes.append({
            "id": theme_id,
            "name": theme_id.replace("-", " ").title(),
            "css_url": f"file:///Users/amirakbari/notes/styles/{css_file.name}",
            "supports_dark": "[data-color-scheme=\"dark\"]" in css_content
        })
    return themes
```

---

## Browser Compatibility

**Target Browsers:**
- Safari 14+ (macOS default)
- Chrome 90+
- Firefox 88+

**Features Used:**
- CSS Custom Properties (widely supported)
- CSS Grid (widely supported)
- Flexbox (universal)
- CSS Animations (universal)
- File URLs (local use only)

---

## Troubleshooting

### Theme not appearing in selector?
1. Check file is named `theme-yourname.css`
2. Verify it's in `~/notes/styles/`
3. Reload the page

### Colors not changing?
1. Check browser dev tools for CSS errors
2. Verify `[data-theme-name="xxx"]` scoping is correct
3. Check that both light and dark modes are defined

### Text invisible in code blocks?
1. Add `color: var(--text-primary)` to pre and code elements
2. See "Code Block Contrast Rule" above

---

## Future Enhancements

### Potential Features
- **More themes:** Just drop in CSS files
- **Custom theme builder:** UI to create themes
- **Theme sharing:** Export/import theme CSS
- **Live preview:** See theme changes in real-time

---

## Version History

### v3.0 - Client-Side Theme System (2026-02-01)
- Complete shift to client-side theme switching
- Auto-discovery of themes
- Theme selector dropdown in UI
- Modal theme added (blue variant)
- Fixed code block contrast issues

### v2.1 - Design Consistency (2026-02-01)
- Applied consistent theme to all pages
- Added content page template with TOC
- Migrated all existing pages

### v2.0 - Major Redesign (2026-02-01)
- Complete visual overhaul
- Added theme toggle with persistence
- Implemented gradient text and animations
- Added width toggle feature

### v1.0 - Initial Redesign (2026-02-01)
- Basic modern styling
- Color palette refinement
- Typography updates

---

## Summary

**The theme system is now completely client-side and user-controlled!**

- ✅ No scripts needed to change themes
- ✅ Instant switching without page reload
- ✅ Auto-discovery of new themes
- ✅ Persistent user preferences
- ✅ Proper contrast in all modes
- ✅ Easy to extend with new themes

**To add a theme:** Create CSS file → Done! 🎨
