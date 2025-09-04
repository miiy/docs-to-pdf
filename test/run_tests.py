import subprocess
import sys
from pathlib import Path


def run_test(test_file):
    """Run a single test file"""
    print(f"\n{'='*50}")
    print(f"Running {test_file}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False


def main():
    """Run all tests"""
    test_dir = Path(__file__).parent
    test_files = [
        "test_extract_urls.py",
        "test_merge_pdfs.py", 
        "test_save_pages.py"
    ]
    
    print("Running Python implementation tests...")
    
    all_passed = True
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            success = run_test(str(test_path))
            if not success:
                all_passed = False
        else:
            print(f"Test file not found: {test_file}")
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 All tests passed! Python implementations are working correctly.")
    else:
        print("❌ Some tests failed. Please check the output above.")
    print(f"{'='*50}")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
