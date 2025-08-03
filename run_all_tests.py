#!/usr/bin/env python3
"""
Comprehensive test runner for ChronoLog application.
Runs all modular tests from their respective subdirectories.
"""

import unittest
import sys
import os

# Add the root directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def discover_and_run_tests():
    """Discover and run all tests in the project"""
    
    # Test directories to scan
    test_dirs = [
        'chronograph',
        'weather', 
        'dope',
        'ammo',
        'rifles',
        'mapping',
        '.'  # Root directory for general tests
    ]
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load tests from each directory
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            try:
                # Look for test files in the directory
                discovered_tests = loader.discover(test_dir, pattern='test_*.py')
                suite.addTest(discovered_tests)
                print(f"✓ Loaded tests from {test_dir}")
            except Exception as e:
                print(f"⚠ Warning: Could not load tests from {test_dir}: {e}")
    
    return suite

def run_specific_module_tests():
    """Run tests for specific modules"""
    
    test_modules = [
        'chronograph.test_chronograph',
        'weather.test_weather',
        'dope.test_dope',
        'ammo.test_ammo', 
        'rifles.test_rifles',
        'mapping.test_mapping',
        'test_all_pages'
    ]
    
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    for module_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            tests = loader.loadTestsFromModule(module)
            suite.addTest(tests)
            print(f"✓ Loaded tests from {module_name}")
        except ImportError as e:
            print(f"⚠ Could not import {module_name}: {e}")
        except Exception as e:
            print(f"⚠ Error loading tests from {module_name}: {e}")
    
    return suite

def main():
    """Main test runner"""
    print("=" * 60)
    print("ChronoLog Application Test Suite")
    print("=" * 60)
    
    # Try to run modular tests first
    print("\n📦 Loading modular tests...")
    try:
        suite = run_specific_module_tests()
        if suite.countTestCases() > 0:
            print(f"\n🧪 Running {suite.countTestCases()} tests...")
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            # Print summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print(f"Tests run: {result.testsRun}")
            print(f"Failures: {len(result.failures)}")
            print(f"Errors: {len(result.errors)}")
            print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
            
            if result.failures:
                print(f"\n❌ {len(result.failures)} test(s) failed")
                for test, traceback in result.failures:
                    print(f"  - {test}")
            
            if result.errors:
                print(f"\n🚨 {len(result.errors)} test(s) had errors")
                for test, traceback in result.errors:
                    print(f"  - {test}")
            
            if not result.failures and not result.errors:
                print("\n✅ All tests passed!")
            
            return len(result.failures) + len(result.errors)
        else:
            print("⚠ No tests found using modular approach")
    except Exception as e:
        print(f"❌ Error running modular tests: {e}")
    
    # Fallback to discovery
    print("\n🔍 Falling back to test discovery...")
    try:
        suite = discover_and_run_tests()
        if suite.countTestCases() > 0:
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            return len(result.failures) + len(result.errors)
        else:
            print("⚠ No tests found using discovery")
            return 1
    except Exception as e:
        print(f"❌ Error running discovery tests: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)