import json
import os
import sys
import tempfile

from merge_pdfs import (
    read_json, 
    sanitize_file_name, 
    get_pdf_files_in_order, 
    merge_pdfs
)


def test_sanitize_file_name():
    """Test filename sanitization"""
    print("Testing sanitize_file_name...")
    
    test_cases = [
        ("Chapter 1: Introduction", "Chapter 1_ Introduction"),
        ("Test/File*Name?", "Test_File_Name_"),
        ("Normal File Name", "Normal File Name"),
        ("<script>alert('xss')</script>", "_script_alert('xss')__script_"),
    ]
    
    for input_name, expected in test_cases:
        result = sanitize_file_name(input_name)
        assert result == expected, f"Expected '{expected}', got '{result}' for input '{input_name}'"
    
    print("✅ sanitize_file_name test passed!")
    return True


def test_read_json():
    """Test JSON reading functionality"""
    print("\nTesting read_json...")
    
    test_data = {
        "totalCount": 2,
        "baseUrl": "https://example.com",
        "links": [
            {"url": "/test1", "title": "Test 1"},
            {"url": "/test2", "title": "Test 2"},
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    try:
        result = read_json(temp_file)
        assert result == test_data, "JSON data mismatch"
        
        # Test non-existent file
        result = read_json("/non/existent/file.json")
        assert result == {}, "Should return empty dict for non-existent file"
        
    finally:
        os.unlink(temp_file)
    
    print("✅ read_json test passed!")
    return True


def test_get_pdf_files_in_order():
    """Test PDF file discovery in order"""
    print("\nTesting get_pdf_files_in_order...")
    
    json_data = {
        "links": [
            {"url": "/chapter1", "title": "Chapter 1"},
            {"url": "/chapter2", "title": "Chapter 2"},
            {"url": "/chapter3", "title": "Chapter 3"},
        ]
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some test PDF files
        pdf_files = [
            os.path.join(temp_dir, "Chapter 1.pdf"),
            os.path.join(temp_dir, "Chapter 3.pdf"),
            # Note: Chapter 2.pdf is missing
        ]
        
        for pdf_file in pdf_files:
            with open(pdf_file, 'w') as f:
                f.write("fake pdf content")
        
        result = get_pdf_files_in_order(json_data, temp_dir)
        
        # Should find 2 files (Chapter 1 and Chapter 3)
        assert len(result) == 2, f"Expected 2 files, got {len(result)}"
        
        # Check that files are in correct order
        assert result[0]['title'] == "Chapter 1", "First file should be Chapter 1"
        assert result[1]['title'] == "Chapter 3", "Second file should be Chapter 3"
        
        # Check file paths
        assert result[0]['path'] == pdf_files[0], "First file path mismatch"
        assert result[1]['path'] == pdf_files[1], "Second file path mismatch"
    
    print("✅ get_pdf_files_in_order test passed!")
    return True


def test_merge_pdfs():
    """Test PDF merging functionality"""
    print("\nTesting merge_pdfs...")
    
    # Create mock PDF files
    pdf_files = [
        {"path": "/fake/path1.pdf", "title": "Test 1", "url": "/test1"},
        {"path": "/fake/path2.pdf", "title": "Test 2", "url": "/test2"},
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "merged.pdf")
        
        # Test with invalid PDF files (should fail gracefully)
        result = merge_pdfs(pdf_files, output_path)
        
        # Verify results - should succeed but with no processed files
        assert result['success'] == True, "Merge should succeed even with invalid files"
        assert result['processedCount'] == 0, "Should process 0 files"
        assert result['errorCount'] == 2, "Should have 2 errors"
        assert result['pageCount'] == 0, "Should have 0 pages"
    
    print("✅ merge_pdfs test passed!")
    return True


def test_integration():
    """Test full integration workflow"""
    print("\nTesting integration workflow...")
    
    # Create test data structure
    json_data = {
        "totalCount": 2,
        "baseUrl": "https://example.com",
        "links": [
            {"url": "/chapter1", "title": "Chapter 1"},
            {"url": "/chapter2", "title": "Chapter 2"},
        ]
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create JSON file
        json_file = os.path.join(temp_dir, "extracted_urls.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # Create PDF directory and files
        pdf_dir = os.path.join(temp_dir, "pdfs")
        os.makedirs(pdf_dir)
        
        pdf_files = [
            os.path.join(pdf_dir, "Chapter 1.pdf"),
            os.path.join(pdf_dir, "Chapter 2.pdf"),
        ]
        
        for pdf_file in pdf_files:
            with open(pdf_file, 'w') as f:
                f.write("fake pdf content")
        
        # Test the workflow
        data = read_json(json_file)
        assert data == json_data, "JSON reading failed"
        
        files = get_pdf_files_in_order(data, pdf_dir)
        assert len(files) == 2, "Should find 2 PDF files"
        
        # Test merge with invalid PDF files (should fail gracefully)
        output_path = os.path.join(temp_dir, "merged.pdf")
        result = merge_pdfs(files, output_path)
        
        # Should succeed but with no processed files due to invalid PDF content
        assert result['success'] == True, "Integration merge should succeed even with invalid files"
        assert result['processedCount'] == 0, "Should process 0 files"
        assert result['errorCount'] == 2, "Should have 2 errors"
    
    print("✅ Integration test passed!")
    return True


def main():
    """Run all tests"""
    print("Running merge_pdfs.py tests...\n")
    
    try:
        test_sanitize_file_name()
        test_read_json()
        test_get_pdf_files_in_order()
        test_merge_pdfs()
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
