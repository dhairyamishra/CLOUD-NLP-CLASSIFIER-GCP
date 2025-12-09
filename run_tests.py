#!/usr/bin/env python3
"""
Cross-platform script to run all Phase 3 tests.
Works on Windows, Linux, and Mac.
"""
import sys
import subprocess
from pathlib import Path

def print_header(message, color_code=36):
    """Print colored header (cyan by default)."""
    separator = "=" * 60
    print(f"\033[{color_code}m{separator}\033[0m")
    print(f"\033[{color_code}m{message}\033[0m")
    print(f"\033[{color_code}m{separator}\033[0m")

def print_success(message):
    """Print success message in green."""
    print(f"\033[32m{message}\033[0m")

def print_error(message):
    """Print error message in red."""
    print(f"\033[31m{message}\033[0m")

def print_warning(message):
    """Print warning message in yellow."""
    print(f"\033[33m{message}\033[0m")

def run_test(test_name, test_path):
    """Run a single test script."""
    print_warning(f"\nRunning Test: {test_name}...")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            check=False
        )
        
        if result.returncode == 0:
            print_success(f"✓ {test_name} passed")
            return True
        else:
            print_error(f"✗ {test_name} failed")
            return False
            
    except Exception as e:
        print_error(f"✗ Error running {test_name}: {str(e)}")
        return False

def main():
    """Main entry point."""
    print_header("Phase 3 Testing Suite")
    
    # Define tests
    tests = [
        ("Model Loading", Path("tests/test_model_loading.py")),
        ("Inference", Path("tests/test_inference.py")),
        ("Metrics Validation", Path("tests/test_metrics.py"))
    ]
    
    # Check if test files exist
    missing_tests = []
    for name, path in tests:
        if not path.exists():
            missing_tests.append(str(path))
    
    if missing_tests:
        print_error(f"\n❌ Missing test files: {', '.join(missing_tests)}")
        return 1
    
    # Run all tests
    results = []
    for test_name, test_path in tests:
        passed = run_test(test_name, test_path)
        results.append((test_name, passed))
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 60)
    print_header("Test Summary", 36)
    
    all_passed = True
    for test_name, passed in results:
        if passed:
            print_success(f"  ✓ {test_name}")
        else:
            print_error(f"  ✗ {test_name}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print_success("✓ ALL TESTS PASSED!")
        print_success("Phase 3 is working correctly!")
        print_success("=" * 60)
        print("\nNext steps:")
        print("  1. Review results in models/transformer/distilbert/")
        print("  2. Compare with baseline models")
        print("  3. Move to Phase 4: FastAPI server")
        return 0
    else:
        print_error("✗ SOME TESTS FAILED")
        print_error("Please check the output above for details")
        print_error("=" * 60)
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\n\n✗ Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
