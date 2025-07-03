# ChronoLog Mapping Module

This directory contains all the mapping functionality for the ChronoLog application, separated from the main app for better organization.

## File Structure

```
mapping/
├── __init__.py                     # Python package marker
├── README.md                       # This file
├── mapping_controller.py           # MVC Controller - handles business logic
├── mapping_model.py                # MVC Model - data operations
├── mapping_view.py                 # MVC View - UI components
├── test_mapping.py                 # Single-page mapping app
├── test_mapping_multipage.py       # Multi-page mapping app (main entry)
└── pages/                          # Streamlit multi-page structure
    ├── 1_📍_Submit_Range.py        # Range submission page
    └── 2_📋_My_Ranges.py           # Range viewing page
```

## Shared Dependencies

The mapping module depends on these shared components from the root directory:
- `auth.py` - Authentication functionality
- `supabase` library - Database client
- `.streamlit/secrets.toml` - Configuration

## Running the Application

### Multi-Page Version (Recommended)
```bash
cd mapping/
streamlit run test_mapping_multipage.py --server.port=8502
```

### Single-Page Version
```bash
cd mapping/
streamlit run test_mapping.py --server.port=8502
```

## Features

- **Range Submission**: Interactive map for selecting firing position and target
- **Calculations**: Automatic distance, azimuth, and elevation angle calculations
- **Address Lookup**: Reverse geocoding using OpenStreetMap Nominatim API
- **Data Persistence**: Range data stored in Supabase database
- **User Limits**: 15 ranges per user maximum
- **Range Viewing**: Table view of submitted ranges with filtering and sorting

## Architecture

This module follows the Model-View-Controller (MVC) pattern:

- **Model** (`mapping_model.py`): Database operations, calculations, API calls
- **View** (`mapping_view.py`): UI components, forms, maps, tables
- **Controller** (`mapping_controller.py`): Business logic, state management, user interactions

## Database Schema

The mapping module uses the `ranges_submissions` table:
- Range metadata (name, description)
- Geographic coordinates (start/end lat/lon, altitudes)
- Calculated measurements (distance, azimuth, elevation angle)
- Address information (GeoJSON format)
- User email and timestamps