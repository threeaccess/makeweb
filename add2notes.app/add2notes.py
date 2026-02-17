#!/usr/bin/env python3
"""Add to Notes: Register an HTML file in your notes index."""

from __future__ import annotations

import argparse
import html.parser
import json
import pathlib
import shutil
import sys
from datetime import datetime
from string import Template
from typing import Optional, List


TOOLS_DIR = pathlib.Path(__file__).parent.resolve()
THEMES_CONFIG_PATH = TOOLS_DIR / "themes.json"
SOURCE_STYLES_DIR = TOOLS_DIR / "styles"
INDEX_TEMPLATE_FILE = TOOLS_DIR / "index.html"
CONFIG_FILE = pathlib.Path.home() / ".add2notes_config.json"
DEFAULT_MAIN_PATH = pathlib.Path.home() / "notes"

# Runtime paths (initialized in main)
NOTES_DIR: pathlib.Path
REGISTRY_FILE: pathlib.Path
INDEX_FILE: pathlib.Path
STYLES_DIR: pathlib.Path
CSS_BASE_PATH: str


def configure_paths(main_path: pathlib.Path) -> None:
    """Configure runtime paths from the user-selected main path."""
    global NOTES_DIR, REGISTRY_FILE, INDEX_FILE, STYLES_DIR, CSS_BASE_PATH

    NOTES_DIR = main_path.expanduser().resolve()
    REGISTRY_FILE = NOTES_DIR / "notes.json"
    INDEX_FILE = NOTES_DIR / "index.html"
    STYLES_DIR = NOTES_DIR / "styles"
    CSS_BASE_PATH = STYLES_DIR.as_uri()


class TitleExtractor(html.parser.HTMLParser):
    """Extract the <title> content from an HTML file."""

    def __init__(self):
        super().__init__()
        self._in_title = False
        self.title: Optional[str] = None

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title = data.strip()


def extract_title(html_path: pathlib.Path) -> str:
    """Extract title from HTML file, falling back to filename."""
    content = html_path.read_text(encoding="utf-8")
    parser = TitleExtractor()
    parser.feed(content)
    return parser.title or html_path.stem


def prompt_main_path() -> pathlib.Path:
    """Prompt user for main notes path on first run."""
    if not sys.stdin.isatty():
        return DEFAULT_MAIN_PATH

    default_str = str(DEFAULT_MAIN_PATH)
    print("First run setup:")
    print("Set the main notes path used by add2notes.")

    while True:
        raw = input(f"Main path [{default_str}]: ").strip()
        chosen = pathlib.Path(raw).expanduser() if raw else DEFAULT_MAIN_PATH
        try:
            return chosen.resolve()
        except OSError as exc:
            print(f"Invalid path: {exc}", file=sys.stderr)


def get_or_create_main_path() -> pathlib.Path:
    """Load configured main path, or initialize configuration."""
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            configured = config.get("main_path")
            if configured:
                return pathlib.Path(configured).expanduser().resolve()
        except (json.JSONDecodeError, OSError):
            print(f"Warning: Ignoring invalid config at {CONFIG_FILE}", file=sys.stderr)

    main_path = prompt_main_path()
    config_payload = {"main_path": str(main_path)}
    CONFIG_FILE.write_text(
        json.dumps(config_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Configured main path: {main_path}")
    print(f"Config saved to: {CONFIG_FILE}")
    return main_path


def load_registry() -> list[dict]:
    """Load the notes registry from JSON."""
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    return []


def save_registry(entries: list[dict]) -> None:
    """Save the notes registry to JSON."""
    REGISTRY_FILE.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_index_template() -> Template:
    """Load index HTML template from the project root."""
    if not INDEX_TEMPLATE_FILE.exists():
        raise RuntimeError(f"Template not found: {INDEX_TEMPLATE_FILE}")
    return Template(INDEX_TEMPLATE_FILE.read_text(encoding="utf-8"))


def validate_paths() -> bool:
    """Validate optional assets and print warnings when they are missing."""
    warnings = []

    if not STYLES_DIR.exists():
        warnings.append(f"Styles directory not found: {STYLES_DIR}")

    required_css = ["core.css", "index.css"]
    for css_file in required_css:
        css_path = STYLES_DIR / css_file
        if not css_path.exists():
            warnings.append(f"Optional CSS file not found: {css_path}")

    if warnings:
        print("Warning: Themed index assets are incomplete.", file=sys.stderr)
        for warning in warnings:
            print(f"  - {warning}", file=sys.stderr)
        print("Falling back to a minimal index page as needed.", file=sys.stderr)

    return True


def discover_themes() -> List[dict]:
    """Auto-discover all theme CSS files from styles directory."""
    themes = []
    
    if not STYLES_DIR.exists():
        return themes
    
    for css_file in sorted(STYLES_DIR.glob("theme-*.css")):
        theme_id = css_file.stem.replace("theme-", "")
        theme_name = theme_id.replace("-", " ").title()
        
        # Check if theme supports dark mode
        css_content = css_file.read_text(encoding="utf-8")
        supports_dark = "[data-color-scheme=\"dark\"]" in css_content
        
        themes.append({
            "id": theme_id,
            "name": theme_name,
            "css_url": f"{CSS_BASE_PATH}/theme-{theme_id}.css",
            "supports_dark": supports_dark
        })
    
    return themes


def load_themes_config() -> dict:
    """Load themes configuration and merge with discovered themes."""
    discovered = discover_themes()
    
    if THEMES_CONFIG_PATH.exists():
        config = json.loads(THEMES_CONFIG_PATH.read_text(encoding="utf-8"))
    else:
        config = {}
    
    # Merge discovered themes with config
    theme_lookup = {t["id"]: t for t in discovered}
    
    # Override with any custom config
    for theme_id, theme_config in config.get("themes", {}).items():
        if theme_id in theme_lookup:
            theme_lookup[theme_id]["name"] = theme_config.get("name", theme_lookup[theme_id]["name"])
    
    return {
        "default_theme": config.get("default_theme", "modern"),
        "themes": list(theme_lookup.values()),
        "css_base_path": CSS_BASE_PATH,
        "page_types": config.get("page_types", {
            "index": {
                "css_file": "index.css",
                "template": "index_template.html",
                "badge_default": "Knowledge Base",
                "subtitle_default": "Your personal collection of linked documents"
            },
            "content": {
                "css_file": "content.css",
                "template": "content_template.html",
                "badge_default": "Documentation",
                "subtitle_default": "Generated by Make Web"
            }
        })
    }


def generate_theme_css_links(themes: List[dict]) -> str:
    """Generate HTML link tags for all theme CSS files."""
    links = []
    for theme in themes:
        links.append(f'<link rel="stylesheet" href="{theme["css_url"]}">')
    return "\n  ".join(links)


def generate_theme_selector_options(themes: List[dict], default_theme: str) -> str:
    """Generate HTML option tags for theme selector dropdown."""
    options = []
    for theme in themes:
        selected = " selected" if theme["id"] == default_theme else ""
        options.append(f'<option value="{theme["id"]}"{selected}>{theme["name"]}</option>')
    
    return "\n            ".join(options)


def generate_stats_html(entries: list[dict]) -> str:
    """Generate stats bar HTML."""
    from datetime import datetime
    
    # Get the most recent date
    if entries:
        latest = max(entries, key=lambda e: e["added"])
        latest_date = latest["added"][:10]
        if latest_date == datetime.now().strftime("%Y-%m-%d"):
            last_updated = "Today"
        else:
            last_updated = latest_date
    else:
        last_updated = "Never"
    
    return f"""
    <div class="stat-item">
      <div class="stat-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-value">{len(entries)}</span>
        <span class="stat-label">Total Notes</span>
      </div>
    </div>
    
    <div class="stat-item">
      <div class="stat-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/>
          <line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-value">{last_updated}</span>
        <span class="stat-label">Last Updated</span>
      </div>
    </div>
    
    <div class="stat-item">
      <div class="stat-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-value">Private</span>
        <span class="stat-label">Access</span>
      </div>
    </div>
    """


def generate_table_rows(entries: list[dict]) -> str:
    """Generate table rows HTML."""
    if not entries:
        return '<tr><td colspan="3" class="empty-state"><div class="empty-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div><div class="empty-title">No notes yet</div><div class="empty-text">Add your first note to get started</div></td></tr>'
    
    rows = []
    for entry in sorted(entries, key=lambda e: e["added"], reverse=True):
        path = entry["path"]
        title = entry["title"]
        added = entry["added"][:10]  # Just the date part
        
        # Determine icon based on path
        if "tools" in path.lower():
            icon_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>'
        elif "notes" in path.lower():
            icon_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
        else:
            icon_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
        
        rows.append(f"""<tr>
    <td>
      <div class="note-title">
        <div class="note-icon">{icon_svg}</div>
        <a href="file://{path}" class="note-link">{title}</a>
      </div>
    </td>
    <td><code class="note-path">{path}</code></td>
    <td>
      <span class="note-date">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/>
          <line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
        {added}
      </span>
    </td>
  </tr>""")
    
    return "\n".join(rows)


def generate_index(entries: list[dict]) -> str:
    """Generate the index.html page using template."""
    # Load template and config
    template = load_index_template()
    config = load_themes_config()
    themes = config["themes"]
    default_theme = config["default_theme"]
    
    page_config = config.get("page_types", {}).get("index", {})
    badge = page_config.get("badge_default", "Knowledge Base")
    subtitle = page_config.get("subtitle_default", "Your personal collection of linked documents")
    
    # Generate content
    stats_html = generate_stats_html(entries)
    table_rows = generate_table_rows(entries)
    theme_css_links = generate_theme_css_links(themes)
    theme_selector_options = generate_theme_selector_options(themes, default_theme)
    
    # Current timestamp
    from datetime import datetime
    last_updated = f"Updated {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Template variables
    template_vars = {
        "title": "Notes Index",
        "default_theme": default_theme,
        "theme_selector_options": theme_selector_options,
        "theme_css_links": theme_css_links,
        "css_core": f"{CSS_BASE_PATH}/core.css",
        "css_page": f"{CSS_BASE_PATH}/index.css",
        "badge_text": badge,
        "subtitle": subtitle,
        "stats_html": stats_html,
        "table_header_html": "<tr><th>Title</th><th>Location</th><th>Added</th></tr>",
        "table_rows_html": table_rows,
        "last_updated": last_updated
    }
    
    return template.safe_substitute(template_vars)


def generate_fallback_index(entries: list[dict]) -> str:
    """Generate a minimal index page when template assets are unavailable."""
    rows = []
    for entry in sorted(entries, key=lambda e: e["added"], reverse=True):
        rows.append(
            f'<li><a href="file://{entry["path"]}">{entry["title"]}</a> '
            f'({entry["added"][:10]})</li>'
        )

    list_html = "\n".join(rows) if rows else "<li>No notes yet.</li>"
    return (
        "<!doctype html>\n"
        "<html><head><meta charset=\"utf-8\"><title>Notes Index</title></head>\n"
        "<body><h1>Notes Index</h1><ul>"
        f"{list_html}"
        "</ul></body></html>"
    )


def write_index(entries: list[dict]) -> None:
    """Write index file using template, or fallback if assets are missing."""
    try:
        content = generate_index(entries)
    except Exception as exc:
        print(f"Warning: Could not render themed index ({exc})", file=sys.stderr)
        content = generate_fallback_index(entries)
    INDEX_FILE.write_text(content, encoding="utf-8")


def initialize_workspace() -> None:
    """Create required runtime files on first run."""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    if SOURCE_STYLES_DIR.exists():
        styles_missing = not STYLES_DIR.exists()
        if styles_missing or not (STYLES_DIR / "core.css").exists() or not (STYLES_DIR / "index.css").exists():
            shutil.copytree(SOURCE_STYLES_DIR, STYLES_DIR, dirs_exist_ok=True)
            print(f"Initialized styles: {STYLES_DIR}")
    elif not STYLES_DIR.exists():
        print(
            f"Warning: Source styles directory not found: {SOURCE_STYLES_DIR}",
            file=sys.stderr,
        )

    if not REGISTRY_FILE.exists():
        save_registry([])

    if not INDEX_FILE.exists():
        entries = load_registry()
        write_index(entries)
        print(f"Initialized: {INDEX_FILE}")


def add_note(html_path: pathlib.Path, custom_title: Optional[str] = None) -> dict:
    """Add a note to the registry and regenerate the index."""
    # Resolve to absolute path
    abs_path = html_path.resolve()

    # Extract or use custom title
    title = custom_title or extract_title(abs_path)

    # Load existing entries
    entries = load_registry()

    # Check if already registered
    path_str = str(abs_path)
    for entry in entries:
        if entry["path"] == path_str:
            print(f"Note already registered: {title}", file=sys.stderr)
            print(f"  Path: {path_str}", file=sys.stderr)
            return entry

    # Add new entry
    new_entry = {
        "title": title,
        "path": path_str,
        "added": datetime.now().isoformat(),
    }
    entries.append(new_entry)

    # Save registry and regenerate index
    save_registry(entries)
    write_index(entries)

    return new_entry


def list_notes() -> None:
    """List all registered notes."""
    entries = load_registry()
    if not entries:
        print("No notes registered yet.")
        return

    print(f"{'Title':<40} {'Added':<12} Path")
    print("-" * 80)
    for entry in sorted(entries, key=lambda e: e["added"], reverse=True):
        title = entry["title"][:38] + ".." if len(entry["title"]) > 40 else entry["title"]
        added = entry["added"][:10]
        print(f"{title:<40} {added:<12} {entry['path']}")


def list_themes() -> None:
    """List available themes."""
    config = load_themes_config()
    default_theme = config.get("default_theme", "modern")
    
    print("Available themes:")
    for theme in config["themes"]:
        marker = " ✓" if theme["id"] == default_theme else ""
        print(f"  {theme['id']}{marker}: {theme['name']}")
    print(f"\nDefault theme: {default_theme}")


def remove_note(identifier: str) -> bool:
    """Remove a note by title or path."""
    entries = load_registry()
    original_count = len(entries)

    entries = [
        e for e in entries
        if identifier not in e["path"] and identifier.lower() not in e["title"].lower()
    ]

    if len(entries) == original_count:
        return False

    save_registry(entries)
    write_index(entries)
    return True


def main() -> int:
    configure_paths(get_or_create_main_path())
    initialize_workspace()

    parser = argparse.ArgumentParser(
        prog="add-to-notes",
        description="Register an HTML file in your notes index.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add an HTML file to notes")
    add_parser.add_argument("file", help="Path to the HTML file")
    add_parser.add_argument("-t", "--title", help="Custom title (default: extracted from HTML)")

    # List command
    subparsers.add_parser("list", help="List all registered notes")

    # Remove command
    rm_parser = subparsers.add_parser("remove", help="Remove a note by title or path")
    rm_parser.add_argument("identifier", help="Title or path substring to match")

    # Regenerate command
    subparsers.add_parser("regen", help="Regenerate index.html from registry")

    # Themes command
    subparsers.add_parser("themes", help="List available themes")

    # Rebuild command
    subparsers.add_parser("rebuild", help="Rebuild index with current settings")

    args = parser.parse_args()

    validate_paths()

    if args.command == "add" or args.command is None and hasattr(args, "file"):
        # Handle both "add-to-notes add file.html" and "add-to-notes file.html"
        file_arg = getattr(args, "file", None)
        if file_arg is None and len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            file_arg = sys.argv[1]

        if file_arg is None:
            parser.print_help()
            return 1

        html_path = pathlib.Path(file_arg)
        if not html_path.exists():
            print(f"File not found: {html_path}", file=sys.stderr)
            return 1

        title = getattr(args, "title", None)
        entry = add_note(html_path, title)
        print(f"Added: {entry['title']}")
        print(f"  Path: {entry['path']}")
        print(f"  Index: {INDEX_FILE}")
        return 0

    elif args.command == "list":
        list_notes()
        return 0

    elif args.command == "remove":
        if remove_note(args.identifier):
            print(f"Removed notes matching: {args.identifier}")
            return 0
        else:
            print(f"No notes found matching: {args.identifier}", file=sys.stderr)
            return 1

    elif args.command == "regen" or args.command == "rebuild":
        entries = load_registry()
        write_index(entries)
        print(f"Regenerated: {INDEX_FILE}")
        print(f"  {len(entries)} note{'s' if len(entries) != 1 else ''} indexed")
        return 0

    elif args.command == "themes":
        list_themes()
        return 0

    else:
        # No command given - try to treat first arg as a file
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            html_path = pathlib.Path(sys.argv[1])
            if html_path.exists():
                entry = add_note(html_path)
                print(f"Added: {entry['title']}")
                print(f"  Path: {entry['path']}")
                print(f"  Index: {INDEX_FILE}")
                return 0

        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
