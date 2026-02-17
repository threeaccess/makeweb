# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of personal Python-based tools for converting Markdown to styled HTML and managing a local notes index. There is no build system, package manager, or test suite — these are standalone Python scripts.

## Tools

### make_web.py (root + convert/make_web.py)
Converts Markdown files to themed HTML pages with table of contents, light/dark mode, and multiple theme support.

```bash
python make_web.py input.md                          # Output: input.html
python make_web.py input.md -o output.html           # Custom output path
python make_web.py input.md --standalone              # Self-contained HTML (CSS inlined)
python make_web.py input.md --badge "Guide" --subtitle "My subtitle"
python make_web.py input.md --no-toc                 # Disable table of contents
```

**Dependency:** `pip install markdown` (the `markdown` library with extensions: extra, tables, fenced_code, sane_lists, toc, codehilite).

### add2notes.app/add2notes.py
Maintains a JSON registry (`notes.json`) of HTML documents and generates a styled index page (`index.html`) in a configurable notes directory (default: `~/notes/`).

```bash
python add2notes.py add document.html        # Register an HTML file
python add2notes.py add doc.html -t "Title"  # With custom title
python add2notes.py list                     # List all registered notes
python add2notes.py remove "search term"     # Remove by title/path substring
python add2notes.py regen                    # Regenerate index.html
python add2notes.py themes                   # List available themes
```

**No external dependencies** (standard library only). Config stored at `~/.add2notes_config.json`.

### ContentManager/generate_website.py
Static site generator that scans subdirectories for `content` files, auto-detects types (markdown, HTML, code, images, JSON, etc.), and produces a card-based browsable website in a `website/` output directory.

```bash
cd ContentManager && python generate_website.py
```

**No external dependencies.** Uses a built-in simple Markdown converter (not the `markdown` library).

## Architecture

### Theme System (v3.0 — Client-Side)
All themes are loaded on every page. Switching happens via `data-theme-name` and `data-color-scheme` HTML attributes with CSS attribute selectors and JavaScript. User preferences persist in `localStorage`.

**Three-layer CSS architecture:**
1. **core.css** — Variables, reset, utilities, responsive breakpoints
2. **Page type CSS** — `index.css` (index pages) or `content.css` (content pages)
3. **theme-*.css** — Color schemes scoped with `[data-theme-name="xxx"]`

Themes are auto-discovered by globbing `theme-*.css` in the styles directory. Adding a new theme requires only dropping a CSS file — no config or script changes needed.

### Key Path Conventions
- **Styles directory:** `~/notes/styles/` (CSS files live here at runtime, copied from `add2notes.app/styles/` on first run)
- **Templates directory:** `~/tools/templates/` (HTML templates using Python `string.Template` with `$variable` placeholders)
- **Notes directory:** Configurable via `~/.add2notes_config.json`, defaults to `~/notes/`
- CSS is referenced via `file://` URIs (local-only use)

### Shared Patterns
- Both `make_web.py` and `add2notes.py` share identical `discover_themes()` and `load_themes_config()` functions (not factored into a shared module)
- HTML templates use Python's `string.Template` (`$variable` / `${variable}` syntax), NOT Jinja2
- Standalone mode in make_web.py uses f-strings with `{{` / `}}` for literal braces in embedded JavaScript
- Title extraction: make_web.py reads the first `# heading` from Markdown; add2notes.py parses the `<title>` tag from HTML

### Typical Workflow
1. Write Markdown → 2. `make_web.py` converts to HTML → 3. `add2notes.py add` registers in index → 4. Open `~/notes/index.html` in browser
