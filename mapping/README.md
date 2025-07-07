# ChronoLog Mapping Module

This directory contains all the mapping functionality for the ChronoLog application, organized using specialized MVC components.

## File Structure

```
mapping/
├── __init__.py                     # Python package marker
├── README.md                       # This file
├── session_state_manager.py       # Page-specific session state management
├── navigate_map.py                 # Simple interactive map viewer
├── range_models.py                 # Data models for ranges and measurements
│
├── # MVC Components by Function
├── nominate_controller.py          # Range nomination controller
├── nominate_model.py               # Range nomination model  
├── nominate_view.py                # Range nomination view
├── public_ranges_controller.py     # Public ranges controller
├── public_ranges_model.py          # Public ranges model
├── public_ranges_view.py           # Public ranges view
├── submission_controller.py        # User submissions controller
├── submission_model.py             # User submissions model
├── submission_view.py              # User submissions view
├── admin_controller.py             # Admin review controller
├── admin_model.py                  # Admin review model
├── admin_view.py                   # Admin review view
│
└── pages/                          # Streamlit multi-page structure
    ├── 1_🏠_Home.py                # Landing page
    └── 2_🌍_Ranges.py              # Public ranges page
```

## Shared Dependencies

The mapping module depends on these shared components from the root directory:
- `auth.py` - Authentication functionality
- `supabase` library - Database client
- `.streamlit/secrets.toml` - Configuration

## Running the Application


### Single-Page Version
```bash
cd mapping/
streamlit run Range_Library.py --server.port=8502
```

## Features

### **Range Nomination** (nominate_*)
- Interactive map for selecting firing position and target
- Address and lat/lon search controls for map navigation
- Automatic distance, azimuth, and elevation angle calculations
- Address lookup using OpenStreetMap Nominatim API
- User limit: 40 ranges per user maximum

### **Public Ranges** (public_ranges_*)
- View approved ranges available to all users
- Admin controls for managing public ranges
- Interactive map display of ranges
- Detailed range information tables

### **User Submissions** (submission_*)
- Manage user's submitted ranges
- View submission status and review feedback
- Delete unwanted submissions
- Map visualization of selected ranges

### **Admin Review** (admin_*)
- Review pending range submissions
- Approve or deny submissions with feedback
- Bulk actions for multiple submissions
- Statistics and submission tracking

## Architecture

This module follows a **specialized MVC pattern** with dedicated components for each feature:

### **Models**
- **NominateModel**: Range nomination logic, calculations, database operations
- **PublicRangesModel**: Public ranges data retrieval and management
- **SubmissionModel**: User submission management and CRUD operations
- **AdminModel**: Admin review workflow and approval/denial logic

### **Views**
- **NominateView**: Range nomination UI components and forms
- **PublicRangesView**: Public ranges display tables and maps
- **SubmissionView**: User submission management interface
- **AdminView**: Admin review interface and bulk action controls

### **Controllers**
- **NominateController**: Orchestrates range nomination workflow
- **PublicRangesController**: Manages public ranges display and admin actions
- **SubmissionController**: Handles user submission management
- **AdminController**: Coordinates admin review processes

### **Session State Management**
- **SessionStateManager**: Prevents state conflicts between pages
- Page-specific state isolation with automatic cleanup
- Global state preservation for authentication

## Database Schema

### **ranges_submissions** table (user submissions)
- Range metadata (name, description, user_email)
- Geographic coordinates (start/end lat/lon, altitudes)
- Calculated measurements (distance, azimuth, elevation angle)
- Address information (GeoJSON format)
- Review status and admin feedback
- Timestamps

### **ranges** table (approved public ranges)
- Same structure as submissions
- Only approved ranges visible to all users