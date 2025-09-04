#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from pathlib import Path

from supabase import create_client

SUPABASE_URL = "https://qnzioartedlrithdxszx.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = "uploads"


def main():
    if not SUPABASE_KEY:
        print("❌ Environment variable 'SUPABASE_SERVICE_ROLE_KEY' not set.")
        print("Set it with: export SUPABASE_SERVICE_ROLE_KEY=your_key")
        sys.exit(1)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Create downloads directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_dir = Path(f"downloads_{timestamp}")
    download_dir.mkdir(exist_ok=True)

    def download_files_recursive(path="", level=0):
        nonlocal downloaded_count
        indent = "  " * level

        try:
            # List items in current path
            items = supabase.storage.from_(BUCKET_NAME).list(path)
            print(f"{indent}Found {len(items)} items in '{path or 'root'}'")

            for item in items:
                item_name = item.get("name")
                if not item_name:
                    continue

                # Build full path
                full_path = f"{path}/{item_name}" if path else item_name

                # Check if it's a file or directory
                if item.get("metadata") and item["metadata"].get(
                        "size") is not None:
                    # It's a file
                    print(f"{indent}📄 Downloading file: {full_path}")

                    try:
                        # Download file
                        file_data = supabase.storage.from_(
                            BUCKET_NAME).download(full_path)

                        # Create local directory structure
                        local_file_path = download_dir / full_path
                        local_file_path.parent.mkdir(
                            parents=True, exist_ok=True)

                        # Write file
                        with open(local_file_path, "wb") as f:
                            f.write(file_data)

                        downloaded_count += 1
                        print(f"{indent}✅ Downloaded: {local_file_path}")

                    except Exception as e:
                        print(f"{indent}❌ Failed to download {full_path}: {e}")
                else:
                    # It's likely a directory, recurse into it
                    print(f"{indent}📁 Entering directory: {full_path}")
                    download_files_recursive(full_path, level + 1)

        except Exception as e:
            print(f"{indent}❌ Error listing path '{path}': {e}")

    try:
        downloaded_count = 0
        download_files_recursive()
        print(
            f"\n🎉 Download complete! {downloaded_count} files saved to '{download_dir}'"
        )

    except Exception as e:
        print(f"❌ Error listing files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
