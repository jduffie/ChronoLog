#!/usr/bin/env python3

import os
import sys
import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://qnzioartedlrithdxszx.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def generate_google_maps_link(latitude, longitude):
    """Generate a Google Maps link for the given coordinates."""
    if pd.isna(latitude) or pd.isna(longitude):
        return None
    return f"https://maps.google.com/?q={latitude},{longitude}"

def import_locations_to_database(user_email="admin@chronolog.com"):
    """Import processed locations from CSV into the database."""
    
    if not SUPABASE_KEY:
        print("❌ Environment variable 'SUPABASE_SERVICE_ROLE_KEY' not set.")
        print("Set it with: export SUPABASE_SERVICE_ROLE_KEY=your_key")
        sys.exit(1)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Read the processed CSV file
    print("📄 Reading locations_processed.csv...")
    try:
        df = pd.read_csv('locations_processed.csv')
    except FileNotFoundError:
        print("❌ locations_processed.csv not found. Run process_locations.py first.")
        sys.exit(1)
    
    print(f"Found {len(df)} locations to import")
    
    imported_count = 0
    
    for _, row in df.iterrows():
        location_name = row['Location']
        altitude = row['Alt (ft)'] if pd.notna(row['Alt (ft)']) else None
        azimuth = row['Azimuth '] if pd.notna(row['Azimuth ']) else None  # Note the space in column name
        latitude = row['Latitude'] if pd.notna(row['Latitude']) else None
        longitude = row['Longitude'] if pd.notna(row['Longitude']) else None
        
        # Generate Google Maps link
        google_maps_link = generate_google_maps_link(latitude, longitude)
        
        # Prepare data for insertion
        location_data = {
            "user_email": user_email,
            "name": location_name,
            "altitude": altitude,
            "azimuth": azimuth,
            "latitude": latitude,
            "longitude": longitude,
            "google_maps_link": google_maps_link
        }
        
        try:
            print(f"📍 Inserting: {location_name}")
            supabase.table("locations").insert(location_data).execute()
            imported_count += 1
            print(f"✅ Imported: {location_name}")
            if google_maps_link:
                print(f"   📍 Maps: {google_maps_link}")
        except Exception as e:
            print(f"❌ Failed to import {location_name}: {e}")
    
    print(f"\n🎉 Import complete! {imported_count}/{len(df)} locations imported successfully.")

if __name__ == "__main__":
    import_locations_to_database()