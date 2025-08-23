#!/usr/bin/env python3
"""
Script to upload bullet data from CSV files to the bullets table.
"""

import os
import sys
from pathlib import Path

import pandas as pd

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from supabase import create_client


def upload_bullets_from_csv():
    """Upload bullet data from all CSV files in bullets/datasets/65mm"""

    # Get Supabase credentials from environment or secrets
    try:
        # Try to use Streamlit secrets if available
        if hasattr(st, "secrets"):
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
        else:
            # Fallback to environment variables
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not url or not key:
            print("Error: Supabase credentials not found")
            return False

    except Exception as e:
        print(f"Error getting Supabase credentials: {e}")
        return False

    # Create Supabase client
    supabase = create_client(url, key)

    # Path to CSV directory
    csv_dir = Path(__file__).parent / "bullets" / "datasets" / "65mm"

    if not csv_dir.exists():
        print(f"Error: Directory {csv_dir} does not exist")
        return False

    # Get all CSV files
    csv_files = list(csv_dir.glob("*.csv"))

    if not csv_files:
        print(f"Error: No CSV files found in {csv_dir}")
        return False

    print(f"Found {len(csv_files)} CSV files to process")

    total_inserted = 0
    total_skipped = 0

    for csv_file in sorted(csv_files):
        print(f"\nProcessing: {csv_file.name}")

        try:
            # Read CSV file
            df = pd.read_csv(csv_file)

            print(f"  - Found {len(df)} rows")

            # Convert DataFrame to list of dictionaries for Supabase
            records = df.to_dict("records")

            # Process each record to handle NaN values and add UUID
            processed_records = []
            for record in records:
                # Replace NaN with None for proper JSON/database handling
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None

                # Add UUID for the id field since the table requires it
                import uuid

                record["id"] = str(uuid.uuid4())

                processed_records.append(record)

            # Insert records in batches to avoid overwhelming the API
            batch_size = 50
            file_inserted = 0
            file_skipped = 0

            for i in range(0, len(processed_records), batch_size):
                batch = processed_records[i : i + batch_size]

                try:
                    # Insert batch
                    response = supabase.table("bullets").insert(batch).execute()

                    if response.data:
                        inserted_count = len(response.data)
                        file_inserted += inserted_count
                        print(
                            f"  - Inserted batch {i//batch_size + 1}: {inserted_count} records"
                        )
                    else:
                        print(
                            f"  - Warning: Batch {i//batch_size + 1} returned no data"
                        )
                        file_skipped += len(batch)

                except Exception as batch_error:
                    print(
                        f"  - Error inserting batch {i//batch_size + 1}: {batch_error}"
                    )

                    # Try inserting records individually to identify problematic ones
                    for record in batch:
                        try:
                            response = (
                                supabase.table("bullets").insert([record]).execute()
                            )
                            if response.data:
                                file_inserted += 1
                            else:
                                file_skipped += 1
                        except Exception as record_error:
                            print(f"    - Skipping record due to error: {record_error}")
                            file_skipped += 1

            print(f"  - Completed: {file_inserted} inserted, {file_skipped} skipped")
            total_inserted += file_inserted
            total_skipped += file_skipped

        except Exception as e:
            print(f"  - Error processing {csv_file.name}: {e}")
            continue

    print(f"\n=== UPLOAD SUMMARY ===")
    print(f"Total files processed: {len(csv_files)}")
    print(f"Total records inserted: {total_inserted}")
    print(f"Total records skipped: {total_skipped}")

    return True


if __name__ == "__main__":
    success = upload_bullets_from_csv()
    sys.exit(0 if success else 1)
