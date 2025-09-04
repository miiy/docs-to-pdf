import json
import os
import sys
import tempfile

from extract_urls import extract_urls_from_html, write_extracted_json


def test_extract_urls_from_html():
    """Test URL extraction from HTML content"""
    print("Testing extract_urls_from_html...")
    
    # Test HTML with various link formats
    test_html = """
    <html>
    <body>
        <h1>Test Page</h1>
        <a href="/chapter1">Chapter 1: Introduction</a>
        <a href="/chapter2">Chapter 2: <strong>Advanced</strong> Topics</a>
        <a href="https://external.com">External Link</a>
        <a href="/chapter3" title="Chapter 3">Chapter 3: <em>Conclusion</em></a>
        <a href="/empty"></a>
        <a href="/no-text">   </a>
        <p>Some text without links</p>
    </body>
    </html>
    """
    
    result = extract_urls_from_html(test_html)
    
    # Expected results
    expected = [
        {"url": "/chapter1", "title": "Chapter 1: Introduction"},
        {"url": "/chapter2", "title": "Chapter 2: Advanced Topics"},
        {"url": "https://external.com", "title": "External Link"},
        {"url": "/chapter3", "title": "Chapter 3: Conclusion"},
    ]
    
    print(f"Extracted {len(result)} links:")
    for i, link in enumerate(result):
        print(f"  {i+1}. {link['title']} -> {link['url']}")
    
    # Verify results
    assert len(result) == len(expected), f"Expected {len(expected)} links, got {len(result)}"
    
    for i, (actual, expected_item) in enumerate(zip(result, expected)):
        assert actual['url'] == expected_item['url'], f"Link {i+1} URL mismatch"
        assert actual['title'] == expected_item['title'], f"Link {i+1} title mismatch"
    
    print("✅ extract_urls_from_html test passed!")
    return True


def test_write_extracted_json():
    """Test JSON writing functionality"""
    print("\nTesting write_extracted_json...")
    
    test_links = [
        {"url": "/test1", "title": "Test 1"},
        {"url": "/test2", "title": "Test 2"},
    ]
    base_url = "https://example.com"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "test_output.json")
        
        write_extracted_json(test_links, base_url, output_path)
        
        # Verify file was created and contains correct data
        assert os.path.exists(output_path), "Output file was not created"
        
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data['totalCount'] == 2, "totalCount mismatch"
        assert data['baseUrl'] == base_url, "baseUrl mismatch"
        assert len(data['links']) == 2, "links count mismatch"
        assert data['links'] == test_links, "links content mismatch"
    
    print("✅ write_extracted_json test passed!")
    return True


def test_integration():
    """Test full integration with sample HTML file"""
    print("\nTesting integration with sample HTML file...")
    
    # Create a sample HTML file
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Example Book</title></head>
    <body>
        <h1>The Example Programming Language</h1>
        <nav>
            <a href="/foreword">Foreword</a>
            <a href="/introduction">Introduction</a>
            <a href="/getting-started">Getting Started</a>
            <a href="/guessing-game">Guessing Game Tutorial</a>
        </nav>
    </body>
    </html>
    """
    
    with tempfile.TemporaryDirectory() as temp_dir:
        html_file = os.path.join(temp_dir, "sample.html")
        json_file = os.path.join(temp_dir, "extracted_urls.json")
        
        # Write sample HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(sample_html)
        
        # Test the full workflow
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        links = extract_urls_from_html(html_content)
        write_extracted_json(links, "https://example.com/book", json_file)
        
        # Verify results
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data['totalCount'] == 4, f"Expected 4 links, got {data['totalCount']}"
        assert data['baseUrl'] == "https://example.com/book"
        
        expected_titles = ["Foreword", "Introduction", "Getting Started", "Guessing Game Tutorial"]
        actual_titles = [link['title'] for link in data['links']]
        
        for expected in expected_titles:
            assert expected in actual_titles, f"Missing expected title: {expected}"
    
    print("✅ Integration test passed!")
    return True


def main():
    """Run all tests"""
    print("Running extract_urls.py tests...\n")
    
    try:
        test_extract_urls_from_html()
        test_write_extracted_json()
        test_integration()
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
