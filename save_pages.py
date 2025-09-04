import argparse
import json
import os
import subprocess
import sys
import time
from typing import Dict

def read_json(file_path: str) -> Dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to read JSON file: {e}")
        return {}


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def run_node_save(url: str, file_name: str, output_dir: str, max_retries: int = 3, proxy: str = None, proxy_username: str = None, proxy_password: str = None, selector: str = None) -> int:
    """
    Run Node.js savepdf script with retry logic for connection failures.
    
    Args:
        url: URL to save as PDF
        file_name: filename for the PDF file
        output_dir: Output directory for PDF
        max_retries: Maximum number of retry attempts (default: 3)
        proxy: Proxy server URL (e.g., 'http://proxy.example.com:8080')
        proxy_username: Username for proxy authentication
        proxy_password: Password for proxy authentication
        selector: CSS selector for specific element to print (e.g., 'div.book')
    
    Returns:
        Return code: 0 for success, non-zero for failure after all retries
    """
    cmd = [
        "node",
        os.path.join(os.path.dirname(__file__), "savepdf", "savepdf.js"),
        f"--url={url}",
        f"--fileName={file_name}",
        f"--outputDir={output_dir}"
    ]
    
    # Add selector if provided
    if selector:
        cmd.append(f"--selector={selector}")
    
    # Add proxy arguments if provided
    if proxy:
        cmd.append(f"--proxy={proxy}")
    if proxy_username:
        cmd.append(f"--proxyUsername={proxy_username}")
    if proxy_password:
        cmd.append(f"--proxyPassword={proxy_password}")
    
    for attempt in range(max_retries + 1):
        print(f"visiting: {url}")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            if proc.stdout:
                print(f"stdout: {proc.stdout.strip()}")
            # Check if the PDF file was actually created
            pdf_path = os.path.join(output_dir, file_name)
            if os.path.exists(pdf_path):
                print(f"✅ saved: {file_name}")
                return 0
            else:
                # Node script returned 0 but file wasn't created
                print(f"❌ save failed {file_name}: PDF file was not created")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    return 1
        else:
            # Node script returned non-zero exit code
            error_msg = proc.stderr.strip() if proc.stderr else 'Unknown error'
            print(f"❌ save failed {file_name}: {error_msg}")
            
            # If this is not the last attempt, wait and retry
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                # Final attempt failed
                return proc.returncode
    
    return proc.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Use Node savepdf.js to save pages as PDFs based on extracted_urls.json")
    parser.add_argument("--json", default="./data/extracted_urls.json", help="Input JSON with links")
    parser.add_argument("--output-dir", default="./data/pdfs", help="Directory to store PDFs")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum number of retry attempts for failed saves (default: 3)")
    parser.add_argument("--selector", help="CSS selector for specific element to print (e.g., 'div.book')")
    parser.add_argument("--proxy", help="Proxy server URL (e.g., 'http://proxy.example.com:8080')")
    parser.add_argument("--proxy-username", help="Username for proxy authentication")
    parser.add_argument("--proxy-password", help="Password for proxy authentication")
    args = parser.parse_args()

    data = read_json(args.json)
    if not data:
        print("Cannot read JSON file, program exit")
        sys.exit(1)

    base_url = data.get("baseUrl", "")
    links = data.get("links", [])
    ensure_dir(args.output_dir)

    print(f"Will save {len(links)} pages as PDFs, output directory: {args.output_dir}")
    success, fail, skipped = 0, 0, 0
    for idx, link in enumerate(links, start=1):
        full_url = base_url.rstrip('/') + '/' + link["url"]
        title = link["title"]
        file_name = link["file_name"]
        pdf_path = os.path.join(args.output_dir, file_name)
        
        print(f"[{idx}/{len(links)}] Processing: {title}")
        
        # Check if PDF already exists
        if os.path.exists(pdf_path):
            print(f"⏭️  skipped: {file_name} (already exists)")
            skipped += 1
            continue
        
        code = run_node_save(full_url, file_name, args.output_dir, args.max_retries, args.proxy, args.proxy_username, args.proxy_password, args.selector)
        if code == 0:
            success += 1
        else:
            fail += 1

    print("\n=== Processing completed ===")
    print(f"Total: {len(links)} pages")
    print(f"Success: {success} pages")
    print(f"Skipped: {skipped} pages (already exist)")
    print(f"Failed: {fail} pages")


if __name__ == "__main__":
    main()


