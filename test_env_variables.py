#!/usr/bin/env python3
"""
Test script to verify environment variables are set correctly.
Usage: python test_env_variables.py
"""

import os
import sys


def test_env_variables():
    """Test that all required environment variables are set."""

    required_vars = [
        "AUTH0_DOMAIN",
        "AUTH0_CLIENT_ID",
        "AUTH0_CLIENT_SECRET",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
    ]

    optional_vars = [
        "AUTH0_REDIRECT_URI",
        "AUTH0_MAPPING_REDIRECT_URI",
        "SUPABASE_KEY",
        "SUPABASE_BUCKET",
    ]

    print("🔍 Checking environment variables...")
    print("=" * 50)

    missing_required = []

    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "SECRET" in var or "KEY" in var:
                display_value = f"***{value[-4:] if len(value) > 4 else '***'}"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_required.append(var)

    print("\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if "SECRET" in var or "KEY" in var:
                display_value = f"***{value[-4:] if len(value) > 4 else '***'}"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"⚠️  {var}: NOT SET (optional)")

    print("=" * 50)

    if missing_required:
        print(f"❌ Missing {len(missing_required)} required environment variables:")
        for var in missing_required:
            print(f"   - {var}")
        print("\n💡 To set environment variables from 1Password:")
        print("   eval $(op signin)")
        print("   source ./export_env_from_1password.sh")
        return False
    else:
        print("✅ All required environment variables are set!")
        print("\n🚀 You can now run:")
        print("   streamlit run ChronoLog.py")
        return True


if __name__ == "__main__":
    success = test_env_variables()
    sys.exit(0 if success else 1)
