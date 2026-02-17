# Add to Notes

A companion tool to `make-web` that maintains a central index of all your HTML documents, regardless of where they're stored on your filesystem.

## Overview

When you convert Markdown files to HTML using `make-web`, those HTML files can end up scattered across different directories. **Add to Notes** solves this by maintaining a JSON registry that tracks all your documents and generates a styled index page with links to each one.

**Key concept:** Documents stay where they are—only their metadata (title, path, date) is stored in the registry. The index page links to files using `file://` URLs.

## Files Created

### In `~/tools/`

| File | Purpose |
|------|---------|
| `add2notes.py` | Main Python script containing all logic |
| `add2notes` | Bash wrapper for easy command-line use |

### In `~/notes/`

| File | Purpose |
|------|---------|
| `notes.json` | JSON registry storing title, absolute path, and timestamp for each document |
| `index.html` | Auto-generated index page with a table of all registered documents |

## Installation

The tool is already installed in `~/tools/`. To use it from anywhere, either:

1. **Use the full path:**
   ```bash
   ~/tools/add2notes add document.html
   ```

2. **Add to PATH** (add to `~/.zshrc` or `~/.bashrc`):
   ```bash
   export PATH="$HOME/tools:$PATH"
   ```

## Usage

### Add a document

```bash
# Basic usage - title extracted from HTML <title> tag
add2notes add /path/to/document.html

# With custom title
add2notes add /path/to/document.html -t "My Custom Title"

# Shorthand (no subcommand needed)
add2notes /path/to/document.html
```

### List all documents

```bash
add2notes list
```

Output:
```
Title                                    Added        Path
--------------------------------------------------------------------------------
My Document Title                        2026-02-01   /Users/you/docs/file.html
Another Note                             2026-01-15   /Users/you/work/note.html
```

### Remove a document

```bash
# Remove by title (case-insensitive, partial match)
add2notes remove "My Document"

# Remove by path (partial match)
add2notes remove "/old/path/"
```

### Regenerate index

If you manually edit `notes.json`, regenerate the index:

```bash
add2notes regen
```

## Typical Workflow

```bash
# 1. Write your notes in Markdown
vim ~/Documents/project-notes.md

# 2. Convert to HTML
~/tools/make-web ~/Documents/project-notes.md

# 3. Register in your notes index
~/tools/add2notes ~/Documents/project-notes.html

# 4. View your notes index
open ~/notes/index.html
```

## Data Format

### notes.json

```json
[
  {
    "title": "Document Title",
    "path": "/absolute/path/to/document.html",
    "added": "2026-02-01T13:06:59.585070"
  }
]
```

You can manually edit this file if needed. After editing, run `add2notes regen` to update the index.

## How It Works

1. **Adding a document:**
   - Resolves the file path to an absolute path
   - Parses the HTML to extract the `<title>` tag (or uses filename as fallback)
   - Checks if already registered (prevents duplicates)
   - Appends entry to `notes.json`
   - Regenerates `index.html`

2. **Index generation:**
   - Reads all entries from `notes.json`
   - Sorts by date (newest first)
   - Generates HTML table with `file://` links
   - Uses the same visual styling as `make-web` output

3. **Title extraction:**
   - Uses Python's `html.parser` to find the `<title>` tag
   - Falls back to filename (without extension) if no title found

## Styling

The generated `index.html` matches the visual style of `make-web`:
- Light/dark mode support (respects system preference)
- Serif typography for readability
- Clean table layout with hover states
- Document count shown at bottom

## Limitations

- **Local files only:** Uses `file://` URLs, so links only work on the same machine
- **No file validation:** Doesn't check if linked files still exist (use `list` to audit)
- **Manual cleanup:** If you delete/move an HTML file, you must manually remove it from the registry

## Tips

- **Organize by keeping HTML near source:** Store your `.html` next to the `.md` source file, then register both locations in notes
- **Use descriptive titles:** The `-t` flag lets you override auto-detected titles for better organization
- **Audit periodically:** Run `add2notes list` occasionally to check for broken paths
- **Bookmark the index:** Add `~/notes/index.html` to your browser bookmarks for quick access

## Dependencies

- Python 3.6+ (uses f-strings, pathlib, typing)
- No external packages required (uses only standard library)

## Related Tools

| Tool | Purpose |
|------|---------|
| `make-web` | Convert Markdown to styled HTML |
| `add2notes` | Register HTML in central index |
