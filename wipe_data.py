#!/usr/bin/env python3

import os
import sys
from supabase import create_client

SUPABASE_URL = "https://qnzioartedlrithdxszx.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = "uploads"


def main():
    if not SUPABASE_KEY:
        print("❌ Environment variable 'SUPABASE_SERVICE_ROLE_KEY' not set.")
        print("Set it with: export SUPABASE_SERVICE_ROLE_KEY=your_key")
        sys.exit(1)

    # Confirmation prompt
    print("⚠️  WARNING: This will DELETE ALL DATA from ChronoLog!")
    print("This will:")
    print("  • DELETE ALL measurements")
    print("  • DELETE ALL sessions")
    print("  • DELETE ALL draft location requests")
    print("  • DELETE ALL approved locations")
    print("  • DELETE ALL uploaded files from storage")
    print("\nThis action cannot be undone and will erase ALL data!")
    confirmation = input("\nType 'WIPE ALL DATA' to confirm: ")

    if confirmation != "WIPE ALL DATA":
        print("❌ Operation cancelled.")
        sys.exit(0)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("\n🗑️  Step 1: Deleting all measurements...")
    wipe_table(supabase, "measurements")

    print("\n🗑️  Step 2: Deleting all sessions...")
    wipe_table(supabase, "sessions")

    print("\n🗑️  Step 3: Deleting all draft location requests...")
    wipe_table(supabase, "locations_draft")

    print("\n🗑️  Step 4: Deleting all approved locations...")
    wipe_table(supabase, "locations")

    print("\n🗑️  Step 5: Deleting all uploaded files...")
    delete_all_files(supabase)

    print("\n🎉 Data wipe complete! All data has been removed from ChronoLog.")


def wipe_table(supabase, table_name):
    try:
        print(f"  🗑️  Deleting all records from {table_name}...")

        # First check how many records exist
        count_response = (
            supabase.table(table_name).select("id", count="exact").execute()
        )
        record_count = (
            count_response.count
            if hasattr(count_response, "count")
            else len(count_response.data)
        )

        if record_count == 0:
            print(f"  ✅ Table {table_name} is already empty")
            return

        print(f"  📊 Found {record_count} records in {table_name}")

        # Delete all records using truncate if available, otherwise delete all
        try:
            # Try truncate first (faster for large tables)
            sql = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
            supabase.rpc("execute_sql", {"sql": sql}).execute()
            print(f"  ✅ Truncated table {table_name} ({record_count} records removed)")
        except Exception as e:
            # Fall back to delete all if truncate fails
            print(f"  ⚠️  Truncate failed, trying delete all: {e}")

            # Delete in batches to avoid timeouts
            batch_size = 1000
            deleted_total = 0

            while True:
                # Get a batch of IDs
                batch_response = (
                    supabase.table(table_name).select("id").limit(batch_size).execute()
                )
                batch_data = batch_response.data

                if not batch_data:
                    break

                # Delete this batch
                ids_to_delete = [record["id"] for record in batch_data]
                for record_id in ids_to_delete:
                    supabase.table(table_name).delete().eq("id", record_id).execute()

                deleted_total += len(ids_to_delete)
                print(
                    f"  📝 Deleted {deleted_total}/{record_count} records from {table_name}"
                )

            print(
                f"  ✅ Deleted all records from {table_name} ({deleted_total} records removed)"
            )

    except Exception as e:
        print(f"  ❌ Error wiping table {table_name}: {e}")


def delete_all_files(supabase):
    deleted_count = 0

    def delete_files_recursive(path="", level=0):
        nonlocal deleted_count
        indent = "  " * (level + 1)

        try:
            # List items in current path
            items = supabase.storage.from_(BUCKET_NAME).list(path)

            if not items:
                print(f"{indent}No items found in '{path or 'root'}'")
                return

            print(f"{indent}Found {len(items)} items in '{path or 'root'}'")

            files_to_delete = []
            subdirectories = []

            for item in items:
                item_name = item.get("name")
                if not item_name:
                    continue

                # Build full path
                full_path = f"{path}/{item_name}" if path else item_name

                # Check if it's a file or directory
                if item.get("metadata") and item["metadata"].get("size") is not None:
                    # It's a file
                    files_to_delete.append(full_path)
                else:
                    # It's likely a directory, add to subdirectories list
                    subdirectories.append(full_path)

            # Delete files in current directory
            if files_to_delete:
                print(f"{indent}🗑️  Deleting {len(files_to_delete)} files...")
                try:
                    supabase.storage.from_(BUCKET_NAME).remove(files_to_delete)
                    deleted_count += len(files_to_delete)
                    for file_path in files_to_delete:
                        print(f"{indent}✅ Deleted: {file_path}")
                except Exception as e:
                    print(f"{indent}❌ Failed to delete files: {e}")

            # Recursively delete subdirectories
            for subdir in subdirectories:
                print(f"{indent}📁 Entering directory: {subdir}")
                delete_files_recursive(subdir, level + 1)

        except Exception as e:
            print(f"{indent}❌ Error listing path '{path}': {e}")

    try:
        delete_files_recursive()
        print(
            f"  ✅ File deletion complete! {deleted_count} files removed from storage."
        )

    except Exception as e:
        print(f"  ❌ Error during file deletion: {e}")


if __name__ == "__main__":
    main()
