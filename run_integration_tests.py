#!/usr/bin/env python3
"""
Integration test runner for ChronoLog.

This script runs integration tests that may require real database connections
or external services. Use this for local development and staging environments.

Usage:
    python run_integration_tests.py                    # Run all integration tests
    python run_integration_tests.py --fast            # Skip slow integration tests  
    python run_integration_tests.py --database-only   # Only database integration tests
    python run_integration_tests.py --file-upload     # Only file upload tests
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def setup_environment():
    """Set up test environment variables"""
    # Set default test database credentials if not provided
    os.environ.setdefault('SUPABASE_URL', 'https://test.supabase.co')
    os.environ.setdefault('SUPABASE_KEY', 'test-key') 
    os.environ.setdefault('TESTING', 'true')
    
    # Create test secrets file if it doesn't exist
    test_secrets_dir = Path('.streamlit')
    test_secrets_dir.mkdir(exist_ok=True)
    
    test_secrets_file = test_secrets_dir / 'secrets.toml'
    if not test_secrets_file.exists():
        test_secrets_content = """
[supabase]
url = "https://test.supabase.co"
key = "test-key"
bucket = "test-bucket"

[auth0]
domain = "test.auth0.com" 
client_id = "test-client-id"
client_secret = "test-client-secret"
"""
        test_secrets_file.write_text(test_secrets_content.strip())
        print(f"Created test secrets file: {test_secrets_file}")


def run_pytest_command(markers=None, extra_args=None):
    """Run pytest with specified markers and arguments"""
    cmd = ['python', '-m', 'pytest']
    
    # Add marker filters
    if markers:
        for marker in markers:
            cmd.extend(['-m', marker])
    
    # Add test file
    cmd.append('test_integration.py')
    
    # Add extra arguments
    if extra_args:
        cmd.extend(extra_args)
    
    # Add verbose output
    cmd.extend(['-v', '--tb=short'])
    
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description='Run ChronoLog integration tests')
    parser.add_argument('--fast', action='store_true', 
                       help='Skip slow integration tests')
    parser.add_argument('--database-only', action='store_true',
                       help='Only run database integration tests')  
    parser.add_argument('--file-upload', action='store_true',
                       help='Only run file upload integration tests')
    parser.add_argument('--auth', action='store_true',
                       help='Only run authentication integration tests')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--coverage', action='store_true',
                       help='Run with coverage reporting')
    
    args = parser.parse_args()
    
    # Set up test environment
    setup_environment()
    
    # Determine which markers to use
    markers = ['integration']
    
    if args.fast:
        markers.append('not slow')
    
    if args.database_only:
        markers.append('database')
        
    if args.file_upload:
        markers.append('file_upload')
        
    if args.auth:
        markers.append('auth')
    
    # Extra pytest arguments
    extra_args = []
    
    if args.coverage:
        extra_args.extend([
            '--cov=.',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    
    if args.verbose:
        extra_args.append('-vv')
    
    # Run the tests
    result = run_pytest_command(markers, extra_args)
    
    if result.returncode == 0:
        print("\n✅ All integration tests passed!")
    else:
        print(f"\n❌ Integration tests failed with code {result.returncode}")
        
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())