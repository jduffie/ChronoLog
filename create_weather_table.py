#!/usr/bin/env python3

import os
from supabase import create_client

def create_weather_table():
    """Create the weather_measurements table in Supabase"""
    
    # Get service role key from environment
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not service_role_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY environment variable not set")
        return False
    
    # Supabase connection (using service role for admin operations)
    SUPABASE_URL = "https://kpvrhkqpwhcqnobpjjud.supabase.co"
    supabase = create_client(SUPABASE_URL, service_role_key)
    
    # Read the SQL file
    try:
        with open('create_weather_table.sql', 'r') as f:
            sql_content = f.read()
        
        # Execute the SQL
        print("Creating weather_measurements table...")
        result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
        
        print("✅ Weather table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating weather table: {e}")
        return False

if __name__ == "__main__":
    create_weather_table()