import argparse
import json
import os
from typing import List, Dict
from lxml import html


def extract_urls_from_html(html_content: str) -> List[Dict[str, str]]:
    """
    Extract href and title text from HTML anchor tags using lxml DOM parsing.

    The output items contain keys: url, title.
    """
    try:
        # Parse HTML with lxml
        doc = html.fromstring(html_content)
        
        matches: List[Dict[str, str]] = []
        
        # Find all anchor tags with href attributes
        for link in doc.xpath('//a[@href]'):
            href = link.get('href')
            if not href:
                continue
                
            # Extract text content, removing nested HTML tags
            title = link.text_content()
            title = ' '.join(title.split())  # Normalize whitespace
            
            if title.strip():
                matches.append({
                    "url": href,
                    "title": title.strip(),
                    "file_name": safe_title(title.strip()) + ".pdf"
                })
        
        return matches
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return []


def write_extracted_json(links: List[Dict[str, str]], base_url: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {
        "totalCount": len(links),
        "baseUrl": base_url,
        "links": links,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def safe_title(title: str) -> str:
    """Generate safe title from title"""
    # Remove or replace characters that are not safe for filenames
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
    return safe_title

def main() -> None:
    parser = argparse.ArgumentParser(description="Extract URLs and titles from an HTML file and write extracted_urls.json")
    parser.add_argument("--html", required=True, help="Path to input HTML file")
    parser.add_argument("--base-url", required=True, help="Base URL to prepend for relative links")
    parser.add_argument("--out", default="./data/extracted_urls.json", help="Output JSON path")
    args = parser.parse_args()

    with open(args.html, "r", encoding="utf-8") as f:
        html = f.read()

    links = extract_urls_from_html(html)

    # add index for duplicate title
    title_dict = {}
    for i in range(len(links)):
        link = links[i]
        key = link['file_name']
        if key in title_dict:
            title_dict[key] += 1
            file_name = links[i]['file_name'].rstrip('.pdf')
            links[i]['file_name'] = f"{file_name}_{title_dict[key]}.pdf"
            continue
        title_dict[key] = 1

    write_extracted_json(links, args.base_url, args.out)
    print(f"Extracted {len(links)} links -> {args.out}")


if __name__ == "__main__":
    main()

