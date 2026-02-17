#!/usr/bin/env python3
"""
Generate a static website to browse content files from subdirectories.
Creates:
- Individual HTML pages for each content file
- Main index.html with card-based browsing
"""

import os
import re
import json
import html
from pathlib import Path
from datetime import datetime

# Configuration
ROOT_DIR = Path(".")
OUTPUT_DIR = Path("website")
CONTENT_FILES = list(ROOT_DIR.glob("*/content"))


def detect_content_type(content_bytes):
    """Detect the type of content in the file."""
    # Check for image files
    if content_bytes.startswith(b"\xff\xd8\xff"):  # JPEG
        return "image", "jpeg"
    if content_bytes.startswith(b"\x89PNG"):  # PNG
        return "image", "png"
    if content_bytes.startswith(b"GIF8"):  # GIF
        return "image", "gif"
    if content_bytes.startswith(b"RIFF") and content_bytes[8:12] == b"WEBP":  # WebP
        return "image", "webp"

    # Try to decode as text
    try:
        content = content_bytes.decode("utf-8", errors="ignore")
    except:
        return "binary", "unknown"

    # Check for HTML
    if "<html" in content.lower() or "<!doctype html" in content.lower():
        return "html", "html"

    # Check for Markdown
    if (
        content.strip().startswith("#")
        or "## " in content[:500]
        or "**" in content[:500]
    ):
        return "markdown", "markdown"

    # Check for JavaScript/React
    if (
        "const " in content
        or "function " in content
        or "=>" in content
        or "import " in content
    ):
        if "React" in content or "Component" in content:
            return "code", "react"
        return "code", "javascript"

    # Check for Python
    if "def " in content or "import " in content or "class " in content:
        if "print(" in content or "def " in content:
            return "code", "python"

    # Check for CSS
    if "{" in content and (
        "color:" in content or "display:" in content or "margin:" in content
    ):
        return "code", "css"

    # Check for JSON
    if content.strip().startswith("{") or content.strip().startswith("["):
        try:
            json.loads(content)
            return "json", "json"
        except:
            pass

    # Check for XML
    if content.strip().startswith("<?xml"):
        return "xml", "xml"

    # Default to text
    return "text", "text"


def get_description(content_type, subtype, content_text, filename):
    """Generate a description of what the document contains."""
    descriptions = {
        ("image", "jpeg"): "JPEG Image",
        ("image", "png"): "PNG Image",
        ("image", "gif"): "GIF Image",
        ("image", "webp"): "WebP Image",
        ("html", "html"): "HTML Document",
        ("markdown", "markdown"): "Markdown Article",
        ("code", "react"): "React Component",
        ("code", "javascript"): "JavaScript Code",
        ("code", "python"): "Python Script",
        ("code", "css"): "CSS Stylesheet",
        ("json", "json"): "JSON Data",
        ("xml", "xml"): "XML Document",
        ("text", "text"): "Text Document",
        ("binary", "unknown"): "Binary File",
    }

    base_desc = descriptions.get((content_type, subtype), "Unknown Document")

    # Try to extract a better description from content
    if content_type == "markdown":
        # Extract title from first heading
        match = re.search(r"^#\s+(.+)$", content_text, re.MULTILINE)
        if match:
            return f"Article: {match.group(1)[:60]}"

    if content_type == "html":
        # Extract title from HTML
        match = re.search(r"<title[^>]*>([^<]+)</title>", content_text, re.IGNORECASE)
        if match:
            return f"HTML Page: {match.group(1)[:60]}"
        # Check for common HTML patterns
        if "form" in content_text.lower():
            return "HTML Form/Widget"
        if "canvas" in content_text.lower():
            return "HTML Canvas Visualization"

    if content_type == "code":
        if subtype == "react":
            # Try to find component name
            match = re.search(r"const\s+(\w+)\s*=", content_text)
            if match:
                return f"React: {match.group(1)} Component"
            return "React Component"
        elif subtype == "python":
            # Try to find main function or class
            match = re.search(r"def\s+(\w+)\s*\(", content_text)
            if match:
                return f"Python: {match.group(1)}() function"
            return "Python Script"

    return base_desc


def get_preview(content_text, content_type, max_length=150):
    """Generate a text preview for card display."""
    if content_type == "image":
        return "[Image Preview]"

    # Clean up the text
    text = content_text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    if len(text) > max_length:
        return text[:max_length] + "..."
    return text if text else "[No text preview available]"


def markdown_to_html(markdown_text):
    """Simple markdown to HTML converter."""
    html_content = html.escape(markdown_text)

    # Headers
    html_content = re.sub(r"#### (.+)", r"<h4>\1</h4>", html_content)
    html_content = re.sub(r"### (.+)", r"<h3>\1</h3>", html_content)
    html_content = re.sub(r"## (.+)", r"<h2>\1</h2>", html_content)
    html_content = re.sub(r"# (.+)", r"<h1>\1</h1>", html_content)

    # Bold and italic
    html_content = re.sub(
        r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", html_content
    )
    html_content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html_content)
    html_content = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html_content)

    # Line breaks and paragraphs
    html_content = html_content.replace("\n\n", "</p><p>")
    html_content = html_content.replace("\n", "<br>")

    return f"<p>{html_content}</p>"


def generate_individual_page(
    folder_name, content_bytes, content_type, subtype, description
):
    """Generate an individual HTML page for a content file."""
    page_path = OUTPUT_DIR / f"{folder_name}.html"

    if content_type == "image":
        # For images, embed them directly
        mime_type = f"image/{subtype}"
        import base64

        encoded = base64.b64encode(content_bytes).decode("utf-8")
        content_html = f'<img src="data:{mime_type};base64,{encoded}" alt="{description}" style="max-width: 100%; height: auto;">'
    elif content_type == "html":
        # For HTML, show it in an iframe
        content_text = content_bytes.decode("utf-8", errors="ignore")
        encoded_html = html.escape(content_text)
        content_html = f'''<div class="html-preview">
            <h3>HTML Source:</h3>
            <pre><code>{encoded_html[:5000]}{"..." if len(encoded_html) > 5000 else ""}</code></pre>
            <h3>HTML Preview:</h3>
            <iframe srcdoc="{html.escape(content_text)}" style="width: 100%; height: 600px; border: 1px solid #ddd;"></iframe>
        </div>'''
    elif content_type == "markdown":
        content_text = content_bytes.decode("utf-8", errors="ignore")
        content_html = markdown_to_html(content_text)
    elif content_type == "code":
        content_text = content_bytes.decode("utf-8", errors="ignore")
        encoded = html.escape(content_text)
        content_html = f'<pre><code class="language-{subtype}">{encoded}</code></pre>'
    elif content_type == "json":
        content_text = content_bytes.decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(content_text)
            formatted = json.dumps(parsed, indent=2)
            content_html = f'<pre><code class="language-json">{html.escape(formatted)}</code></pre>'
        except:
            content_html = f"<pre><code>{html.escape(content_text)}</code></pre>"
    else:
        content_text = content_bytes.decode("utf-8", errors="ignore")
        content_html = f"<pre>{html.escape(content_text)}</pre>"

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{folder_name} - Content Viewer</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/javascript.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/css.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/json.min.js"></script>
</head>
<body>
    <div class="container">
        <nav class="breadcrumb">
            <a href="index.html">← Back to All Content</a>
        </nav>
        
        <header class="content-header">
            <h1>{folder_name}</h1>
            <div class="meta">
                <span class="badge type-{content_type}">{content_type.upper()}</span>
                <span class="badge subtype-{subtype}">{subtype}</span>
                <span class="description">{description}</span>
            </div>
        </header>
        
        <main class="content-display">
            {content_html}
        </main>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('pre code').forEach((block) => {{
                hljs.highlightBlock(block);
            }});
        }});
    </script>
</body>
</html>"""

    page_path.write_text(html_template, encoding="utf-8")
    return page_path.name


def generate_index_page(items):
    """Generate the main index page with cards."""
    cards_html = []

    for item in items:
        folder_name = item["folder"]
        content_type = item["type"]
        subtype = item["subtype"]
        description = item["description"]
        preview = item["preview"]

        type_class = f"type-{content_type}"

        card = f'''<article class="card {type_class}" data-type="{content_type}" data-subtype="{subtype}">
            <a href="{folder_name}.html" class="card-link">
                <div class="card-header">
                    <span class="card-id">{folder_name[:8]}...</span>
                    <span class="card-type">{content_type.upper()}</span>
                </div>
                <div class="card-body">
                    <h3 class="card-title">{html.escape(description[:80])}</h3>
                    <p class="card-preview">{html.escape(preview[:120])}</p>
                </div>
                <div class="card-footer">
                    <span class="badge">{subtype}</span>
                    <span class="view-link">View →</span>
                </div>
            </a>
        </article>'''

        cards_html.append(card)

    cards_joined = "\n".join(cards_html)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Browser - {len(items)} Items</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header class="site-header">
            <h1>📁 Content Browser</h1>
            <p class="subtitle">Browse {len(items)} content files from subdirectories</p>
        </header>
        
        <section class="filters">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search by description..." autocomplete="off">
            </div>
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">All ({len(items)})</button>
                <button class="filter-btn" data-filter="markdown">Articles ({sum(1 for i in items if i["type"] == "markdown")})</button>
                <button class="filter-btn" data-filter="html">HTML ({sum(1 for i in items if i["type"] == "html")})</button>
                <button class="filter-btn" data-filter="code">Code ({sum(1 for i in items if i["type"] == "code")})</button>
                <button class="filter-btn" data-filter="image">Images ({sum(1 for i in items if i["type"] == "image")})</button>
                <button class="filter-btn" data-filter="text">Text ({sum(1 for i in items if i["type"] == "text")})</button>
            </div>
        </section>
        
        <main class="card-grid">
            {cards_joined}
        </main>
        
        <footer class="site-footer">
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </footer>
    </div>
    
    <script>
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const cards = document.querySelectorAll('.card');
        
        searchInput.addEventListener('input', function(e) {{
            const query = e.target.value.toLowerCase();
            cards.forEach(card => {{
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const preview = card.querySelector('.card-preview').textContent.toLowerCase();
                if (title.includes(query) || preview.includes(query)) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }});
        
        // Filter functionality
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {{
            btn.addEventListener('click', function() {{
                filterBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                cards.forEach(card => {{
                    if (filter === 'all' || card.getAttribute('data-type') === filter) {{
                        card.style.display = '';
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>"""

    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(html_template, encoding="utf-8")


def generate_styles():
    """Generate CSS stylesheet."""
    css = """/* Content Browser Styles */

:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --background-color: #f8fafc;
    --card-background: #ffffff;
    --text-color: #1e293b;
    --border-color: #e2e8f0;
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.15);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: var(--background-color);
    color: var(--text-color);
    line-height: 1.6;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

/* Header */
.site-header {
    text-align: center;
    margin-bottom: 2rem;
    padding: 2rem 0;
}

.site-header h1 {
    font-size: 2.5rem;
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.subtitle {
    color: var(--secondary-color);
    font-size: 1.1rem;
}

/* Filters */
.filters {
    margin-bottom: 2rem;
}

.search-box {
    margin-bottom: 1rem;
}

.search-box input {
    width: 100%;
    max-width: 500px;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border: 2px solid var(--border-color);
    border-radius: 8px;
    outline: none;
    transition: border-color 0.2s;
}

.search-box input:focus {
    border-color: var(--primary-color);
}

.filter-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.filter-btn {
    padding: 0.5rem 1rem;
    border: 1px solid var(--border-color);
    background: white;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
}

.filter-btn:hover {
    background: var(--background-color);
}

.filter-btn.active {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

/* Card Grid */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
}

/* Cards */
.card {
    background: var(--card-background);
    border-radius: 12px;
    box-shadow: var(--shadow);
    transition: all 0.2s ease;
    overflow: hidden;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}

.card-link {
    display: block;
    text-decoration: none;
    color: inherit;
    padding: 1.25rem;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.card-id {
    font-family: monospace;
    font-size: 0.85rem;
    color: var(--secondary-color);
}

.card-type {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    background: #e0e7ff;
    color: #4338ca;
}

.type-image .card-type {
    background: #fce7f3;
    color: #be185d;
}

.type-html .card-type {
    background: #fed7aa;
    color: #c2410c;
}

.type-code .card-type {
    background: #d1fae5;
    color: #047857;
}

.type-markdown .card-type {
    background: #e0e7ff;
    color: #4338ca;
}

.type-text .card-type {
    background: #f3f4f6;
    color: #374151;
}

.card-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--text-color);
    line-height: 1.4;
}

.card-preview {
    font-size: 0.9rem;
    color: var(--secondary-color);
    line-height: 1.5;
    margin-bottom: 1rem;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border-color);
}

.badge {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
    background: var(--background-color);
    border-radius: 4px;
    color: var(--secondary-color);
}

.view-link {
    font-size: 0.9rem;
    color: var(--primary-color);
    font-weight: 500;
}

/* Footer */
.site-footer {
    text-align: center;
    margin-top: 3rem;
    padding: 2rem 0;
    color: var(--secondary-color);
    font-size: 0.9rem;
}

/* Individual Page Styles */
.breadcrumb {
    margin-bottom: 1.5rem;
}

.breadcrumb a {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
}

.breadcrumb a:hover {
    text-decoration: underline;
}

.content-header {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
}

.content-header h1 {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
    word-break: break-all;
}

.meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
}

.meta .badge {
    font-size: 0.85rem;
    padding: 0.35rem 0.75rem;
    background: #e0e7ff;
    color: #4338ca;
    border-radius: 20px;
}

.meta .description {
    color: var(--secondary-color);
    font-size: 0.9rem;
}

.content-display {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: var(--shadow);
    overflow-x: auto;
}

.content-display pre {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 0.9rem;
    line-height: 1.5;
}

.content-display code {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.content-display h1, .content-display h2, .content-display h3 {
    margin: 1.5rem 0 0.75rem;
}

.content-display p {
    margin-bottom: 1rem;
}

.content-display img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
}

.html-preview {
    margin-top: 1rem;
}

.html-preview h3 {
    margin: 1rem 0 0.5rem;
    font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    .site-header h1 {
        font-size: 1.75rem;
    }
    
    .card-grid {
        grid-template-columns: 1fr;
    }
    
    .filter-buttons {
        justify-content: center;
    }
    
    .content-display {
        padding: 1rem;
    }
}
"""

    styles_path = OUTPUT_DIR / "styles.css"
    styles_path.write_text(css, encoding="utf-8")


def main():
    """Main function to generate the website."""
    print(f"Found {len(CONTENT_FILES)} content files")

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    items = []

    for content_file in CONTENT_FILES:
        folder_name = content_file.parent.name

        try:
            content_bytes = content_file.read_bytes()
            content_type, subtype = detect_content_type(content_bytes)

            if content_type == "image":
                content_text = ""
            else:
                content_text = content_bytes.decode("utf-8", errors="ignore")

            description = get_description(
                content_type, subtype, content_text, folder_name
            )
            preview = get_preview(content_text, content_type)

            # Generate individual page
            page_name = generate_individual_page(
                folder_name, content_bytes, content_type, subtype, description
            )

            items.append(
                {
                    "folder": folder_name,
                    "type": content_type,
                    "subtype": subtype,
                    "description": description,
                    "preview": preview,
                    "page": page_name,
                }
            )

            print(f"✓ Generated: {folder_name} ({content_type}/{subtype})")

        except Exception as e:
            print(f"✗ Error processing {folder_name}: {e}")

    # Sort items by folder name
    items.sort(key=lambda x: x["folder"])

    # Generate index page
    generate_index_page(items)
    print(f"\n✓ Generated index.html with {len(items)} items")

    # Generate styles
    generate_styles()
    print("✓ Generated styles.css")

    print(f"\n✅ Website generated in: {OUTPUT_DIR.absolute()}")
    print(f"Open {OUTPUT_DIR}/index.html in your browser to view")


if __name__ == "__main__":
    main()
