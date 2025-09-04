# docs-to-pdf

covert online docs to pdf with bookmarks.

## Features

- Extract links from an HTML file to `data/extracted_urls.json`
- Select specific element to print
- Save all pages as PDFs using Node's puppeteer via Python wrapper
- Merge PDFs with bookmarks (keeps order from `extracted_urls.json` and adds outline)

## TODO

- Remove specific element

## Setup

1) Install Node deps (for puppeteer used in savepdf.js):

```bash
cd savepdf
npm install
```

2) Setup Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

- Extract links from an HTML file to `data/extracted_urls.json`:

```bash
python extract_urls.py --html path/to/index.html --base-url https://example.com --out ./data/extracted_urls.json
```

- Save all pages as PDFs using Node's puppeteer via Python wrapper:

```bash
python save_pages.py --json ./data/extracted_urls.json --output-dir ./data/pdfs
```

- Merge PDFs with bookmarks (keeps order from `extracted_urls.json` and adds outline):

```bash
python merge_pdfs.py \
  --json ./data/extracted_urls.json \
  --pdf-dir ./data/pdfs \
  --output ./data/example.pdf
```
