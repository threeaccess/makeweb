# Content Browser Website Generator

**A Python tool that transforms scattered content files into a beautiful, browsable static website.**

---

## Overview

This tool automatically analyzes content files distributed across multiple subdirectories and generates a complete static website with a modern, card-based interface. It intelligently detects content types (Markdown articles, HTML pages, code files, images, and text documents) and creates optimized viewing pages for each.

**Perfect for:** Documentation libraries, asset collections, content archives, and knowledge bases stored in folder hierarchies.

---

## What It Does

### 1. Content Discovery
Scans all subdirectories for files named `content` and identifies what type of data each contains.

### 2. Smart Type Detection
Analyzes file contents to automatically categorize:
- **Images** (JPEG, PNG, GIF, WebP) - Detected via magic bytes
- **Markdown Articles** - With headers and formatting
- **HTML Documents** - Web pages and widgets
- **Code Files** - React components, JavaScript, Python, CSS
- **Structured Data** - JSON and XML
- **Plain Text** - Simple text documents

### 3. Description Generation
Extracts meaningful descriptions from content:
- Article titles from Markdown headers
- Page titles from HTML `<title>` tags
- Component/function names from code
- Image format details

### 4. Website Generation
Creates a complete static website with:
- **Main Index Page** - Browse all content with cards
- **Individual Pages** - Dedicated view for each file
- **Search & Filter** - Find content quickly
- **Syntax Highlighting** - For code files
- **Responsive Design** - Works on all devices

---

## Installation

### Prerequisites
- Python 3.6 or higher
- Content files organized in subdirectories (each containing a `content` file)

### Setup
1. Download or clone the tool:
```bash
# If you have the script
cp generate_website.py /path/to/your/content/

# Or create it manually and paste the code
```

2. Ensure your directory structure looks like this:
```
your-content-folder/
├── subdirectory-1/
│   └── content          # Your content file
├── subdirectory-2/
│   └── content          # Another content file
├── subdirectory-3/
│   └── content
└── generate_website.py  # This tool
```

---

## How to Use

### Basic Usage

1. **Navigate to your content directory:**
```bash
cd /path/to/your/content/folder
```

2. **Run the generator:**
```bash
python3 generate_website.py
```

3. **Open the website:**
```bash
# On macOS
open website/index.html

# On Linux
xdg-open website/index.html

# On Windows
start website/index.html
```

Or simply double-click `website/index.html` in your file manager.

### What Gets Generated

After running, you'll have:
```
website/
├── index.html              # Main browsing page
├── styles.css              # All styling
├── 002861c6-846a-...html   # Individual content pages
├── 007990bd-881e-...html
├── 01b6ae2b-8f41-...html
└── ... (260 total pages)
```

---

## Features

### Card-Based Browsing
View all your content as beautiful cards showing:
- Content type (color-coded badge)
- Extracted title/description
- Text preview (first 120 characters)
- File subtype (e.g., "react", "jpeg", "markdown")

### Search
Type in the search box to filter content by:
- Title/description
- Preview text
- Real-time results as you type

### Filter by Type
Click filter buttons to show only:
- **All** - Everything (default)
- **Articles** - Markdown documents
- **HTML** - Web pages and widgets
- **Code** - React, JS, Python, CSS files
- **Images** - JPEG, PNG, GIF, WebP
- **Text** - Plain text documents

### Individual Content Pages
Each content file gets its own page with:
- Breadcrumb navigation (back to index)
- Type badges and description
- Optimized display:
  - **Images:** Embedded and responsive
  - **Markdown:** Formatted HTML
  - **HTML:** Source code + preview iframe
  - **Code:** Syntax-highlighted with line numbers
  - **JSON:** Prettified and formatted

### Responsive Design
- Works on desktop, tablet, and mobile
- Adaptive grid layout (1-4 columns based on screen size)
- Touch-friendly interface

---

## Use Cases

### 1. Documentation Library
**Scenario:** You have 100+ markdown guides stored in folders.

**Solution:** Run the generator to create a browsable knowledge base with search and filtering.

**Benefits:**
- No server required - share via file system or static hosting
- Instant search across all docs
- Mobile-friendly for on-the-go reference

### 2. Design Asset Collection
**Scenario:** Hundreds of image assets with preview files scattered in project folders.

**Solution:** Generate a visual catalog with image previews and metadata.

**Benefits:**
- See all images at a glance
- Filter by image type (JPEG, PNG, etc.)
- Click to view full-size with embedded base64 encoding

### 3. Code Snippet Repository
**Scenario:** Archive of useful code snippets organized by project.

**Solution:** Create a code library with syntax highlighting and component detection.

**Benefits:**
- Syntax highlighting for readability
- Extracted function/component names
- Filter by language (React, Python, CSS)

### 4. HTML Widget Gallery
**Scenario:** Collection of HTML components, forms, and widgets.

**Solution:** Generate a component gallery with both source and preview.

**Benefits:**
- See rendered output in iframe
- View source code side-by-side
- Quick navigation between components

### 5. Content Archive
**Scenario:** Mixed content types (articles, images, data files) from various sources.

**Solution:** Unified browser with automatic type detection.

**Benefits:**
- No manual categorization needed
- Consistent interface for all content types
- Search across everything

### 6. Project Portfolio
**Scenario:** Showcase work samples stored in separate folders.

**Solution:** Create a portfolio website with project previews.

**Benefits:**
- Professional card-based layout
- Automatic descriptions from content
- Easy to share (just a folder of HTML files)

---

## Advanced Usage

### Customizing the Output

**Change the output directory:**
Edit line 14 in `generate_website.py`:
```python
OUTPUT_DIR = Path("my-website")  # Change from "website"
```

**Modify card preview length:**
Edit line 115:
```python
def get_preview(content_text, content_type, max_length=200):  # Change from 150
```

**Adjust color scheme:**
Edit the CSS variables in `generate_styles()` function (around line 270):
```python
css = '''/* Content Browser Styles */

:root {
    --primary-color: #2563eb;  # Change to your brand color
    --background-color: #f8fafc;  # Change background
    ...
}
```

### Regenerating

To update the website after adding/modifying content files:

```bash
# Re-run the generator (overwrites existing website folder)
python3 generate_website.py

# Old website is replaced with updated version
```

### Hosting Online

Since the output is static HTML, you can host it anywhere:

**GitHub Pages:**
1. Push `website/` folder to a repository
2. Enable GitHub Pages in settings
3. Access at `https://username.github.io/repo-name/`

**Netlify:**
1. Drag and drop the `website/` folder to Netlify
2. Instant deployment with CDN

**Any Web Server:**
```bash
# Python simple server
cd website && python3 -m http.server 8000

# Node.js
npx serve website

# PHP
php -S localhost:8000 -t website
```

---

## Troubleshooting

### "No content files found"
- Ensure subdirectories contain files named exactly `content` (no extension)
- Check you're running from the parent directory
- Verify file permissions with `ls -la */content`

### Images not displaying
- Images are embedded as base64 - check file isn't corrupted
- Verify image format is supported (JPEG, PNG, GIF, WebP)

### Special characters not rendering
- Tool uses UTF-8 encoding with error handling
- Some binary files may not display correctly (this is expected)

### Website looks unstyled
- Ensure `styles.css` is in the same folder as `index.html`
- Check browser console for 404 errors
- Try refreshing with Ctrl+Shift+R (hard reload)

---

## Technical Details

### Content Type Detection
The tool uses a multi-layer approach:

1. **Magic Bytes Check** (for binary files)
   - JPEG: `\xff\xd8\xff`
   - PNG: `\x89PNG`
   - GIF: `GIF8`
   - WebP: `RIFF...WEBP`

2. **Pattern Matching** (for text files)
   - HTML: `<html` or `<!DOCTYPE html`
   - Markdown: Starts with `#` or contains `##` / `**`
   - React: Contains `React` and `const` / `=>`
   - Python: Contains `def ` or `import ` patterns

3. **Validation** (for structured data)
   - JSON: Attempt `json.loads()`
   - XML: Check for `<?xml` declaration

### Performance
- Processes ~260 files in ~10 seconds
- Generates ~300KB-3MB HTML files (depending on image sizes)
- No runtime dependencies (all processing done upfront)

### Browser Compatibility
- Chrome/Edge 80+
- Firefox 75+
- Safari 13+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## File Reference

### Input
- `*/content` - Content files in subdirectories (required)

### Output
- `website/index.html` - Main browsing interface
- `website/styles.css` - All CSS styling
- `website/{uuid}.html` - Individual content pages

### Generator Script
- `generate_website.py` - Python script (22KB)

---

## Example Output

### Index Page
```
📁 Content Browser
Browse 260 content files from subdirectories

[Search box...]
[All (260)] [Articles (36)] [HTML (46)] [Code (17)] [Images (149)] [Text (10)]

┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ 002861c6...     HTML    │ 007990bd...     CODE    │ 01b6ae2b...  MARKDOWN   │
│ HTML Page: FOR 610      │ CSS Stylesheet          │ Article: The Importance │
│ Training Video Player   │ :root { /* Colors */    │ of Core Values...       │
│ html         View →     │ css          View →     │ markdown     View →     │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

### Individual Page (Markdown)
```
← Back to All Content

01b6ae2b-8f41-4662-8b17-809a17bb173e
[MARKDOWN] [markdown] Article: The Importance of Core Values and How to Create Your Own List

# The Importance of Core Values and How to Create Your Own List

In a world full of choices, distractions, and competing priorities...

## Why Core Values Matter
- **Better Decision-Making**: Core values provide a framework...
```

---

## Contributing

To extend the tool:

1. **Add new content types:** Edit `detect_content_type()` function
2. **Customize descriptions:** Modify `get_description()` function
3. **Change styling:** Update `generate_styles()` function
4. **Add new filters:** Update `generate_index_page()` function

---

## License

This tool is provided as-is for content management purposes. Feel free to modify and distribute.

---

**Questions or Issues?**
- Check the troubleshooting section above
- Review the PRD.md for detailed requirements
- Examine the Python script comments for implementation details

---

**Happy Browsing! 🎉**
