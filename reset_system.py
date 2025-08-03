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
    print("⚠️  WARNING: This will COMPLETELY RESET the ChronoLog system!")
    print("This will:")
    print("  • DELETE ALL uploaded files from storage")
    print("  • DROP ALL database tables")
    print("  • RECREATE empty tables with the correct schema")
    print("\nThis action cannot be undone and will erase ALL data!")
    confirmation = input("\nType 'RESET EVERYTHING' to confirm: ")

    if confirmation != "RESET EVERYTHING":
        print("❌ Operation cancelled.")
        sys.exit(0)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("\n🗑️  Step 1: Deleting all uploaded files...")
    delete_all_files(supabase)

    print("\n🗃️  Step 2: Dropping existing tables...")
    drop_tables(supabase)

    print("\n🏗️  Step 3: Creating fresh tables...")
    create_tables(supabase)

    print("\n🎉 System reset complete! ChronoLog is ready for fresh data.")


def delete_all_files(supabase):
    deleted_count = 0

    def delete_files_recursive(path="", level=0):
        nonlocal deleted_count
        indent = "  " * level

        try:
            # List items in current path
            items = supabase.storage.from_(BUCKET_NAME).list(path)
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
        print(f"✅ File deletion complete! {deleted_count} files removed from storage.")

    except Exception as e:
        print(f"❌ Error during file deletion: {e}")


def drop_tables(supabase):
    tables_to_drop = ["measurements", "sessions", "locations"]

    for table in tables_to_drop:
        try:
            print(f"  🗑️  Dropping table: {table}")
            supabase.rpc("drop_table_if_exists", {"table_name": table}).execute()
            print(f"  ✅ Dropped table: {table}")
        except Exception as e:
            # Try direct SQL approach if RPC doesn't work
            try:
                sql = f"DROP TABLE IF EXISTS {table} CASCADE;"
                supabase.rpc("execute_sql", {"sql": sql}).execute()
                print(f"  ✅ Dropped table: {table}")
            except Exception as e2:
                print(f"  ⚠️  Could not drop table {table}: {e2}")


def create_tables(supabase):
    # Create sessions table
    sessions_sql = """
    CREATE TABLE sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_email TEXT NOT NULL,
        sheet_name TEXT NOT NULL,
        bullet_type TEXT NOT NULL,
        bullet_grain NUMERIC,
        session_timestamp TIMESTAMPTZ,
        uploaded_at TIMESTAMPTZ DEFAULT NOW(),
        file_path TEXT,
        location_id UUID REFERENCES locations(id),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    # Create measurements table
    measurements_sql = """
    CREATE TABLE measurements (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
        shot_number INTEGER,
        speed_fps NUMERIC,
        delta_avg_fps NUMERIC,
        ke_ft_lb NUMERIC,
        power_factor NUMERIC,
        time_local TEXT,
        clean_bore BOOLEAN,
        cold_bore BOOLEAN,
        shot_notes TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    # Create locations table
    locations_sql = """
    CREATE TABLE locations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_email TEXT NOT NULL,
        name TEXT NOT NULL,
        altitude NUMERIC,
        azimuth NUMERIC,
        latitude NUMERIC(10, 8),
        longitude NUMERIC(11, 8),
        google_maps_link TEXT,
        status TEXT DEFAULT 'ACTIVE',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    # Create indexes for better performance
    indexes_sql = [
        "CREATE INDEX idx_sessions_user_email ON sessions(user_email);",
        "CREATE INDEX idx_sessions_uploaded_at ON sessions(uploaded_at);",
        "CREATE INDEX idx_sessions_location_id ON sessions(location_id);",
        "CREATE INDEX idx_measurements_session_id ON measurements(session_id);",
        "CREATE INDEX idx_measurements_shot_number ON measurements(shot_number);",
        "CREATE INDEX idx_locations_user_email ON locations(user_email);",
        "CREATE INDEX idx_locations_name ON locations(name);",
        "CREATE INDEX idx_locations_status ON locations(status);",
    ]

    try:
        print("  🏗️  Creating sessions table...")
        supabase.rpc("execute_sql", {"sql": sessions_sql}).execute()
        print("  ✅ Created sessions table")

        print("  🏗️  Creating measurements table...")
        supabase.rpc("execute_sql", {"sql": measurements_sql}).execute()
        print("  ✅ Created measurements table")

        print("  🏗️  Creating locations table...")
        supabase.rpc("execute_sql", {"sql": locations_sql}).execute()
        print("  ✅ Created locations table")

        print("  🏗️  Creating indexes...")
        for idx_sql in indexes_sql:
            try:
                supabase.rpc("execute_sql", {"sql": idx_sql}).execute()
            except Exception as e:
                print(f"  ⚠️  Index creation warning: {e}")
        print("  ✅ Created database indexes")

    except Exception as e:
        print(f"  ❌ Error creating tables: {e}")
        print("  💡 You may need to create tables manually in Supabase SQL Editor:")
        print("\n--- Sessions Table ---")
        print(sessions_sql)
        print("\n--- Measurements Table ---")
        print(measurements_sql)
        print("\n--- Locations Table ---")
        print(locations_sql)
        print("\n--- Indexes ---")
        for idx_sql in indexes_sql:
            print(idx_sql)


if __name__ == "__main__":
    main()
