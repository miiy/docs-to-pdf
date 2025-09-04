import json
import os
import sys
import argparse
from pypdf import PdfReader, PdfWriter

def read_json_file(file_path):
    """Read JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to read JSON file: {e}")
        return None

def get_pdf_files_in_order(json_data, pdf_dir):
    """ Get PDF files in order from JSON data """
    pdf_files = []
    
    if not os.path.exists(pdf_dir):
        print(f"❌ PDF directory does not exist: {pdf_dir}")
        return []
    
    for link in json_data['links']:
        file_name = link['file_name']
        pdf_path = os.path.join(pdf_dir, file_name)
        
        if os.path.exists(pdf_path):
            pdf_files.append({
                'path': pdf_path,
                'title': link['title'],
                'url': link['url']
            })
        else:
            print(f"⚠️  PDF file does not exist: {file_name}")
    
    return pdf_files

def merge_pdfs_with_bookmarks(pdf_files, output_path):
    """ Merge PDF files and add bookmarks """
    try:
        print("Starting to merge PDF files and add bookmarks...\n")
        
        # create pdf writer
        writer = PdfWriter()
        
        processed_count = 0
        error_count = 0
        bookmarks = []
        current_page = 0
        
        for i, pdf_file in enumerate(pdf_files):
            try:
                print(f"[{i+1}/{len(pdf_files)}] Processing: {pdf_file['title']}")
                
                # read pdf file
                reader = PdfReader(pdf_file['path'])
                page_count = len(reader.pages)
                
                # add pages to writer
                for page in reader.pages:
                    writer.add_page(page)
                
                # record bookmark information
                if page_count > 0:
                    bookmarks.append({
                        'title': pdf_file['title'],
                        'page': current_page,
                        'page_count': page_count
                    })
                    current_page += page_count
                
                processed_count += 1
                print(f"✅ Added: {pdf_file['title']} ({page_count} pages)")
                
            except Exception as e:
                print(f"❌ Processing failed {pdf_file['title']}: {e}")
                error_count += 1
        
        # add bookmarks
        print("\nAdding bookmarks...")
        try:
            for bookmark in bookmarks:
                try:
                    # add bookmark to pdf
                    writer.add_outline_item(
                        title=bookmark['title'],
                        page_number=bookmark['page']
                    )
                    print(f"📖 Adding bookmark: {bookmark['title']} -> {bookmark['page'] + 1} page")
                except Exception as e:
                    print(f"⚠️  Adding bookmark failed {bookmark['title']}: {e}")
        except Exception as e:
            print(f"⚠️  Creating bookmarks failed: {e}")
            print("📝 Note: PDF has been merged but bookmarks have not been added")
        
        # save merged pdf
        print("\nSaving merged PDF file...")
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # get file size
        file_size = os.path.getsize(output_path)
        
        return {
            'success': True,
            'output_path': output_path,
            'file_size': file_size,
            'page_count': current_page,
            'processed_count': processed_count,
            'error_count': error_count,
            'bookmarks_count': len(bookmarks),
            'bookmarks': bookmarks
        }
        
    except Exception as e:
        print(f"❌ Merging PDF failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Merge PDF files and add bookmarks')
    parser.add_argument('--json', default='./data/extracted_urls.json', help='JSON file path')
    parser.add_argument('--pdf-dir', default='./data/pdfs', help='PDF directory path')
    parser.add_argument('--output', default='./data/merged.pdf', help='Output PDF file path')
    
    args = parser.parse_args()
    
    print("Starting to merge PDF files and add bookmarks...\n")
    
    # read json data
    json_data = read_json_file(args.json)
    if not json_data:
        print("Cannot read JSON file, program exit")
        return 1
    
    print(f"Found {json_data['totalCount']} links")
    print(f"Base URL: {json_data['baseUrl']}\n")
    
    # get pdf files list
    pdf_files = get_pdf_files_in_order(json_data, args.pdf_dir)
    
    if not pdf_files:
        print("No PDF files found")
        return 1
    
    print(f"Found {len(pdf_files)} PDF files\n")
    
    # merge pdfs
    result = merge_pdfs_with_bookmarks(pdf_files, args.output)
    
    if result['success']:
        print("\n✅ PDF merge task completed!")
        print(result)
        return 0
    else:
        print("\n❌ PDF merge task failed!")
        print(result)
        return 1

if __name__ == "__main__":
    sys.exit(main())
