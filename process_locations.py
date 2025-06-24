#!/usr/bin/env python3

import pandas as pd
import re

def split_latlon(latlon_str):
    """
    Split a LatLon string like "36.222285°N 78.051825°W" into separate lat/lon values.
    Returns (latitude, longitude) as decimal degrees.
    """
    if pd.isna(latlon_str) or not isinstance(latlon_str, str) or latlon_str.strip() == "":
        return None, None
    
    # Remove any extra whitespace
    latlon_str = latlon_str.strip()
    
    # Pattern to match: decimal°N/S decimal°E/W
    pattern = r'([0-9.]+)°([NS])\s+([0-9.]+)°([EW])'
    match = re.match(pattern, latlon_str)
    
    if not match:
        print(f"Warning: Could not parse LatLon: {latlon_str}")
        return None, None
    
    lat_val, lat_dir, lon_val, lon_dir = match.groups()
    
    # Convert to decimal degrees
    latitude = float(lat_val)
    longitude = float(lon_val)
    
    # Apply direction (S and W are negative)
    if lat_dir == 'S':
        latitude = -latitude
    if lon_dir == 'W':
        longitude = -longitude
    
    return latitude, longitude

def process_locations_csv():
    """Process the locations.csv file and split LatLon into separate columns."""
    
    # Read the CSV file
    print("📄 Reading locations.csv...")
    df = pd.read_csv('locations.csv')
    
    print(f"Found {len(df)} rows in the file")
    print("\nColumns:", list(df.columns))
    
    # Show first few rows
    print("\nFirst few rows:")
    print(df.head())
    
    # Split the LatLon column
    print("\n🔄 Processing LatLon column...")
    df[['Latitude', 'Longitude']] = df['LatLon'].apply(
        lambda x: pd.Series(split_latlon(x))
    )
    
    # Show the results
    print("\n✅ Results after splitting LatLon:")
    print(df[['Location', 'LatLon', 'Latitude', 'Longitude']].head())
    
    # Remove rows that are completely empty or have no location name
    df_clean = df.dropna(subset=['Location']).copy()
    df_clean = df_clean[df_clean['Location'].str.strip() != '']
    
    print(f"\n🧹 After cleaning: {len(df_clean)} valid locations")
    
    # Save the processed file
    output_file = 'locations_processed.csv'
    df_clean.to_csv(output_file, index=False)
    print(f"💾 Saved processed data to: {output_file}")
    
    # Show final summary
    print("\n📊 Summary of processed locations:")
    for _, row in df_clean.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            print(f"  • {row['Location']}: {row['Latitude']:.6f}, {row['Longitude']:.6f}")
        else:
            print(f"  • {row['Location']}: No coordinates")
    
    return df_clean

if __name__ == "__main__":
    processed_df = process_locations_csv()
    print(f"\n🎉 Processing complete! {len(processed_df)} locations processed.")