import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from save_pages import read_json, ensure_dir, run_node_save


def test_read_json():
    """Test JSON reading functionality"""
    print("Testing read_json...")
    
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


def test_ensure_dir():
    """Test directory creation functionality"""
    print("\nTesting ensure_dir...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = os.path.join(temp_dir, "test", "nested", "directory")
        
        # Directory should not exist initially
        assert not os.path.exists(test_dir), "Directory should not exist initially"
        
        ensure_dir(test_dir)
        
        # Directory should exist after calling ensure_dir
        assert os.path.exists(test_dir), "Directory should exist after ensure_dir"
        assert os.path.isdir(test_dir), "Should be a directory"
        
        # Calling again should not cause errors
        ensure_dir(test_dir)
        assert os.path.exists(test_dir), "Directory should still exist after second call"
    
    print("✅ ensure_dir test passed!")
    return True


def test_run_node_save():
    """Test Node.js savepdf.js execution"""
    print("\nTesting run_node_save...")
    
    # Mock subprocess.run to avoid actually calling Node.js
    with patch('save_pages.subprocess.run') as mock_run:
        # Mock successful execution
        mock_run.return_value.returncode = 0
        
        result = run_node_save("https://example.com", "Test Page", "/tmp")
        
        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]  # First positional argument (the command list)
        
        assert "node" in call_args, "Command should include 'node'"
        assert "--url=https://example.com" in call_args, "Command should include URL"
        assert "--title=Test Page" in call_args, "Command should include title"
        assert "--outputDir=/tmp" in call_args, "Command should include output directory"
        
        assert result == 0, "Should return success code"
    
    print("✅ run_node_save test passed!")
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
        
        # Create output directory
        output_dir = os.path.join(temp_dir, "pdfs")
        
        # Test the workflow with mocked Node.js calls
        data = read_json(json_file)
        assert data == json_data, "JSON reading failed"
        
        ensure_dir(output_dir)
        assert os.path.exists(output_dir), "Output directory should exist"
        
        # Mock subprocess calls for each link
        with patch('save_pages.subprocess.run') as mock_run:
            # Mock successful execution for all calls
            mock_run.return_value.returncode = 0
            
            # Simulate the main workflow
            base_url = data.get("baseUrl", "")
            links = data.get("links", [])
            
            success, fail = 0, 0
            for link in links:
                full_url = base_url + link["url"]
                title = link["title"]
                code = run_node_save(full_url, title, output_dir)
                if code == 0:
                    success += 1
                else:
                    fail += 1
            
            # Verify results
            assert success == 2, f"Should have 2 successful saves, got {success}"
            assert fail == 0, f"Should have 0 failed saves, got {fail}"
            assert mock_run.call_count == 2, f"Should call subprocess 2 times, called {mock_run.call_count}"
    
    print("✅ Integration test passed!")
    return True


def main():
    """Run all tests"""
    print("Running save_pages.py tests...\n")
    
    try:
        test_read_json()
        test_ensure_dir()
        test_run_node_save()
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
