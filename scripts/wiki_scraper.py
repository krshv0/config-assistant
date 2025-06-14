from langchain_community.document_loaders import WebBaseLoader
from bs4 import SoupStrainer
from markdownify import markdownify as md
import os

# Save directory
path = "/Users/krishiv/Desktop/Projects/config-assistant/store/data/docs"
os.makedirs(path, exist_ok=True)

DOC_URLS = [
    "https://felixkratz.github.io/SketchyBar/features",
    "https://felixkratz.github.io/SketchyBar/setup",
    "https://felixkratz.github.io/SketchyBar/config/bar",
    "https://felixkratz.github.io/SketchyBar/config/items",
    "https://felixkratz.github.io/SketchyBar/config/popups",
    "https://felixkratz.github.io/SketchyBar/config/events",
    "https://felixkratz.github.io/SketchyBar/config/querying",
    "https://felixkratz.github.io/SketchyBar/config/animations",
    "https://felixkratz.github.io/SketchyBar/config/types",
    "https://felixkratz.github.io/SketchyBar/config/reloading",
    "https://felixkratz.github.io/SketchyBar/config/tricks",
]

# Load and save each page
for i, url in enumerate(DOC_URLS):
    try:
        loader = WebBaseLoader(
            web_paths=(url,),
            bs_kwargs=dict(parse_only=SoupStrainer(class_="docMainContainer_gTbr"))
        )
        docs = loader.load()
        if not docs:
            raise ValueError("No content found.")
        
        # Convert raw HTML to Markdown for better structure
        html = docs[0].metadata.get("raw_html", docs[0].page_content)
        content = md(html).strip()

        # Determine filename
        slug = url.rstrip("/").split("/")[-1] or "index"
        filename = os.path.join(path, f"{i:02d}_{slug}.md")

        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Saved: {filename}")

    except Exception as e:
        print(f"[!] Failed to scrape {url}: {e}")