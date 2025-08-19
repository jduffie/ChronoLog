#!/usr/bin/env python3
"""
Script to generate table schema markdown files from Supabase database.
This script connects to Supabase and retrieves detailed schema information
for specified tables, then generates comprehensive markdown documentation.
"""

import os
import sys
from typing import Dict, List, Any
from supabase import create_client

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Supabase configuration
SUPABASE_URL = "https://qnzioartedlrithdxszx.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def check_environment():
    """Check if required environment variables are set."""
    if not SUPABASE_KEY:
        print("❌ Environment variable 'SUPABASE_SERVICE_ROLE_KEY' not set.")
        print("Please set the Supabase service role key using:")
        print("export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here")
        sys.exit(1)

def create_supabase_client():
    """Create and return Supabase client."""
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        sys.exit(1)

def get_table_schema(supabase, table_name: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive table schema information from Supabase.
    
    Args:
        supabase: Supabase client instance
        table_name: Name of the table to analyze
        
    Returns:
        Dictionary containing table schema information
    """
    print(f"❌ Schema introspection not available - Supabase client cannot query system catalogs")
    print(f"Please use the Supabase MCP server or dashboard to view schema information")
    return None

def generate_create_table_sql(table_name: str, schema_info: Dict[str, Any]) -> str:
    """Generate CREATE TABLE SQL statement from schema information."""
    if not schema_info or not schema_info.get('columns'):
        return ""
    
    sql_parts = [f"CREATE TABLE {table_name} ("]
    
    primary_keys = [pk['column_name'] for pk in schema_info.get('primary_keys', [])]
    
    for col in schema_info['columns']:
        col_name = col['column_name']
        data_type = col['data_type'].upper()
        
        # Handle specific PostgreSQL types
        if data_type == 'CHARACTER VARYING':
            data_type = 'TEXT'
        elif data_type == 'TIMESTAMP WITH TIME ZONE':
            data_type = 'TIMESTAMPTZ'
        elif data_type == 'DOUBLE PRECISION':
            data_type = 'REAL'
            
        col_def = f"    {col_name} {data_type}"
        
        # Add primary key constraint
        if col_name in primary_keys:
            col_def += " PRIMARY KEY"
            
        # Add NOT NULL constraint
        if col['is_nullable'] == 'NO':
            col_def += " NOT NULL"
            
        # Add default value
        if col['column_default']:
            default_val = col['column_default']
            # Clean up default values
            if 'gen_random_uuid()' in default_val:
                col_def += " DEFAULT gen_random_uuid()"
            elif 'now()' in default_val.lower():
                col_def += " DEFAULT NOW()"
            elif default_val != 'NULL':
                col_def += f" DEFAULT {default_val}"
                
        sql_parts.append(col_def + ",")
    
    # Remove last comma and close table definition
    if sql_parts[-1].endswith(','):
        sql_parts[-1] = sql_parts[-1][:-1]
    sql_parts.append(");")
    
    return "\n".join(sql_parts)

def generate_indexes_sql(table_name: str, schema_info: Dict[str, Any]) -> str:
    """Generate recommended indexes based on table structure."""
    indexes = []
    
    if table_name == 'dope_sessions':
        indexes = [
            f"CREATE INDEX idx_{table_name}_user_id ON {table_name}(user_id);",
            f"CREATE INDEX idx_{table_name}_chrono_session_id ON {table_name}(chrono_session_id);",
            f"CREATE INDEX idx_{table_name}_range_submission_id ON {table_name}(range_submission_id);",
            f"CREATE INDEX idx_{table_name}_created_at ON {table_name}(created_at DESC);"
        ]
    
    return "\n".join(indexes)

def generate_markdown_content(table_name: str, schema_info: Dict[str, Any]) -> str:
    """Generate complete markdown documentation for the table."""
    
    create_sql = generate_create_table_sql(table_name, schema_info)
    indexes_sql = generate_indexes_sql(table_name, schema_info)
    
    # Generate column description table
    if schema_info and schema_info.get('columns'):
        columns = schema_info['columns']
    else:
        print(f"❌ Could not retrieve schema information for table '{table_name}'")
        return ""
    
    # Column descriptions for dope_sessions
    column_descriptions = {
        'id': 'Primary key, auto-generated unique identifier',
        'user_id': 'Auth0 user identifier for data isolation',
        'session_name': 'Descriptive name for the DOPE session',
        'chrono_session_id': 'Foreign key to chrono_sessions table',
        'range_submission_id': 'Foreign key to ranges_submissions table',
        'weather_source_id': 'Foreign key to weather_source table',
        'rifle_id': 'Foreign key to rifles table',
        'cartridge_type': "Type of cartridge ('factory' or 'custom')",
        'cartridge_spec_id': 'Reference to cartridge specification',
        'cartridge_lot_number': 'Cartridge lot identifier',
        'range_name': 'Name of the shooting range',
        'distance_m': 'Target distance in meters',
        'notes': 'Session notes and observations',
        'status': 'Session status',
        'created_at': 'Record creation timestamp',
        'updated_at': 'Last modification timestamp'
    }
    
    markdown_content = f"""# {table_name} Table Schema

## CREATE TABLE Statement

```sql
{create_sql}
```

## Recommended Indexes

```sql
{indexes_sql}
```

## Table Description

| Column Name | Data Type | Nullable | Default | Description |
|-------------|-----------|----------|---------|-------------|"""

    for col in columns:
        col_name = col['column_name']
        data_type = col['data_type'].upper()
        nullable = "YES" if col['is_nullable'] == 'YES' else "NO"
        default = col['column_default'] if col['column_default'] else "-"
        description = column_descriptions.get(col_name, "")
        
        markdown_content += f"\n| **{col_name}** | {data_type} | {nullable} | {default} | {description} |"

    # Add foreign key relationships section
    if table_name == 'dope_sessions':
        markdown_content += """

## Foreign Key Relationships

The table has the following foreign key relationships:

- **chrono_sessions(id)** - Links to chronograph session data for velocity measurements
- **ranges_submissions(id)** - Links to shooting range information and location data
- **weather_source(id)** - Links to weather measurement devices (optional)
- **rifles(id)** - Links to rifle configuration data including barrel specifications

## Purpose and Context

The `dope_sessions` table stores "Data On Previous Engagement" sessions, which are used for ballistic analysis and tracking shooting performance across different conditions. This table serves as the metadata container for DOPE sessions, connecting:

- Chronograph data (velocity measurements)
- Range information (distance, location, environmental factors)
- Weather conditions
- Rifle configurations
- Cartridge specifications

Each DOPE session represents a shooting event where ballistic performance is recorded and analyzed for future reference and trajectory calculations.

## Key Features

1. **User Isolation**: The `user_id` field ensures data is properly isolated per user
2. **Timestamps**: Both creation and update timestamps are automatically tracked
3. **Optional Relationships**: Many foreign key fields are nullable to accommodate varying data availability
4. **Comprehensive Context**: Links multiple aspects of shooting data for complete ballistic analysis
5. **Flexible Cartridge Tracking**: Supports both factory and custom cartridge specifications"""

    return markdown_content

def main():
    """Main function to generate table schema markdown."""
    if len(sys.argv) != 2:
        print("Usage: python generate_table_schema.py <table_name>")
        print("Example: python generate_table_schema.py dope_sessions")
        sys.exit(1)
    
    table_name = sys.argv[1]
    
    print(f"🔍 Generating schema documentation for table: {table_name}")
    
    # Check environment and create client
    check_environment()
    supabase = create_supabase_client()
    
    # Get table schema
    print(f"📊 Retrieving schema information...")
    schema_info = get_table_schema(supabase, table_name)
    
    if schema_info is None:
        print(f"❌ Could not retrieve schema for table '{table_name}'")
        sys.exit(1)
    
    # Generate markdown content
    print(f"📝 Generating markdown documentation...")
    markdown_content = generate_markdown_content(table_name, schema_info)
    
    # Write to file using relative path
    output_file = f"./{table_name}_table_schema.md"
    with open(output_file, 'w') as f:
        f.write(markdown_content)
    
    print(f"✅ Schema documentation generated: {output_file}")

if __name__ == "__main__":
    main()