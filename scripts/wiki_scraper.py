import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import json
import os

BASE_URL = "https://felixkratz.github.io/SketchyBar/"
PAGES = [
    "config/bar", "config/items", "config/events", "config/animations", "config/types", "config/querying", "config/reloading", "config/tricks", "config/popups", "config/components", "setup", "features"  # Expand as needed
]

OUTPUT_DIR = "/Users/krishiv/Desktop/Projects/config-assistant/data/docs/sketchybar_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_html(url):
    res = requests.get(url)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")


def extract_code_blocks(soup):
    code_blocks = []
    for block in soup.find_all("pre"):
        text = block.get_text(strip=True)
        if text:
            code_blocks.append({
                "type": "code",
                "content": text
            })
    return code_blocks


def extract_tables(soup):
    tables = []
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        rows = []
        for tr in table.find_all("tr")[1:]:
            row = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            rows.append(dict(zip(headers, row)))
        if rows:
            tables.append({
                "type": "table",
                "headers": headers,
                "rows": rows
            })
    return tables


def extract_text_sections(soup):
    content = []
    for el in soup.find_all(["h1", "h2", "h3", "p", "ul", "ol"]):
        if el.name.startswith("h"):
            content.append({
                "type": "header",
                "level": el.name,
                "content": el.get_text(strip=True)
            })
        elif el.name == "p":
            content.append({
                "type": "paragraph",
                "content": el.get_text(strip=True)
            })
        elif el.name in ["ul", "ol"]:
            items = [li.get_text(strip=True) for li in el.find_all("li")]
            content.append({
                "type": "list",
                "ordered": el.name == "ol",
                "items": items
            })
    return content


def scrape_page(slug):
    url = BASE_URL + slug
    soup = fetch_html(url)
    content = {
        "page": slug,
        "url": url,
        "sections": []
    }

    content["sections"].extend(extract_text_sections(soup))
    content["sections"].extend(extract_tables(soup))
    content["sections"].extend(extract_code_blocks(soup))


    with open(f"{OUTPUT_DIR}/{os.path.basename(slug)}.json", "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

    print(f"✅ Scraped {slug} → {len(content['sections'])} sections")


def main():
    for page in PAGES:
        try:
            scrape_page(page)
        except requests.exceptions.HTTPError:
            print("url not found")
            continue


if __name__ == "__main__":
    main()