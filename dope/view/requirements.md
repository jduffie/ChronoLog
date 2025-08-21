# DOPE View Requirements Specification

## Overview

The DOPE View module provides a comprehensive interface for users to view, filter, search, and manage their DOPE (Data On Previous Engagement) sessions. This module renders session data in a tabular format with advanced filtering capabilities and allows users to select sessions for detailed viewing and editing.

## Functional Requirements

### 1. Session Data Display

#### 1.1 Complete Data Table Rendering
- **REQ-DV-001**: Display all DOPE sessions for the authenticated user in a sortable data table
- **REQ-DV-002**: Show ALL session information in columns based on DopeSessionModel:
  - **Core Fields**: ID, Session Name, Created At, Status
  - **Foreign Keys**: Chrono Session ID, Range Submission ID, Weather Source ID, Rifle ID
  - **Range Data**: Range Name, Distance (m)
  - **Rifle Info**: Rifle Name, Barrel Length (cm), Barrel Twist (in/rev)
  - **Cartridge Info**: Cartridge Make, Cartridge Model, Cartridge Type, Lot Number
  - **Bullet Info**: Bullet Make, Bullet Model, Bullet Weight, Length (mm), BC G1, BC G7, Sectional Density, Diameter Groove (mm), Bore Diameter Land (mm)
  - **Weather Data**: Weather Source Name, Temperature (°C), Humidity (%), Pressure (inHg), Wind Speed 1 (km/h), Wind Speed 2 (km/h), Wind Direction (°)
  - **Position Data**: Start Lat, Start Lon, Start Altitude (m), Azimuth (°), Elevation Angle (°)
  - **Notes**: Session Notes
- **REQ-DV-003**: Support column visibility toggle (user can show/hide columns)
- **REQ-DV-004**: Support pagination when more than 50 sessions exist
- **REQ-DV-005**: Display session count and total records information
- **REQ-DV-006**: Column resizing and reordering capabilities

#### 1.2 Data Formatting
- **REQ-DV-007**: Format dates in user-friendly format (e.g., "Mar 15, 2024 10:30 AM")
- **REQ-DV-008**: Display bullet information with proper units (e.g., "175gr", "0.875 mm")
- **REQ-DV-009**: Show distance with unit suffix (e.g., "100.0m")
- **REQ-DV-010**: Format weather data with appropriate units and precision
- **REQ-DV-011**: Use status badges with appropriate colors (Active: Green, Archived: Gray)
- **REQ-DV-012**: Handle null/empty values gracefully with placeholder text

### 2. Comprehensive Filtering and Search

#### 2.1 Basic Filters
- **REQ-DV-013**: Created At date range picker
- **REQ-DV-014**: Status filter dropdown (All, Active, Archived)
- **REQ-DV-015**: Rifle Name filter with autocomplete dropdown
- **REQ-DV-016**: Range Name filter with autocomplete dropdown

#### 2.2 Cartridge Filters
- **REQ-DV-017**: Cartridge Make filter with autocomplete
- **REQ-DV-018**: Cartridge Model filter with autocomplete  
- **REQ-DV-019**: Cartridge Type filter with autocomplete
- **REQ-DV-020**: Combined cartridge search across all cartridge fields

#### 2.3 Bullet Filters
- **REQ-DV-021**: Bullet Make filter with autocomplete
- **REQ-DV-022**: Bullet Model filter with autocomplete
- **REQ-DV-023**: Bullet Weight filter with range slider (min/max grains)
- **REQ-DV-024**: Combined bullet search across all bullet fields

#### 2.4 Weather Filters
- **REQ-DV-025**: Temperature range filter (°C, min/max sliders)
- **REQ-DV-026**: Humidity range filter (%, min/max sliders)
- **REQ-DV-027**: Pressure range filter (inHg, min/max sliders)
- **REQ-DV-028**: Wind Speed range filter (km/h, min/max sliders)
- **REQ-DV-029**: Wind Direction range filter (degrees, circular slider)
- **REQ-DV-030**: Weather Source Name filter with autocomplete

#### 2.5 Range and Position Filters
- **REQ-DV-031**: Distance range filter (meters, min/max sliders)
- **REQ-DV-032**: Altitude range filter (meters, min/max sliders)
- **REQ-DV-033**: Geographic bounding box filter (lat/lon coordinates)
- **REQ-DV-034**: Azimuth range filter (degrees, circular slider)
- **REQ-DV-035**: Elevation angle range filter (degrees, min/max sliders)

#### 2.6 Advanced Search and Filtering
- **REQ-DV-036**: Global search box that searches across all text fields:
  - Session name, notes
  - Rifle name
  - Cartridge make/model/type
  - Bullet make/model
  - Range name
  - Weather source name
- **REQ-DV-037**: Real-time search results as user types (debounced)
- **REQ-DV-038**: Multiple filter combination with AND logic
- **REQ-DV-039**: Save filter presets for quick reuse
- **REQ-DV-040**: Clear all filters button
- **REQ-DV-041**: Filter summary display showing active filters

#### 2.7 Sorting
- **REQ-DV-042**: Sort by any column (ascending/descending)
- **REQ-DV-043**: Multi-column sorting support
- **REQ-DV-044**: Default sort by created date (newest first)
- **REQ-DV-045**: Visual indicators for current sort column and direction

### 3. Session Selection and Actions

#### 3.1 Row Selection
- **REQ-DV-046**: Allow single-click row selection with visual highlighting
- **REQ-DV-047**: Show selected session details in expandable section
- **REQ-DV-048**: Support keyboard navigation (arrow keys, Enter to select)
- **REQ-DV-049**: Double-click row to open edit mode

#### 3.2 Bulk Operations
- **REQ-DV-050**: Support multi-row selection with checkboxes
- **REQ-DV-051**: Bulk actions dropdown for selected sessions:
  - Archive selected
  - Delete selected (with confirmation)
  - Export selected to CSV
- **REQ-DV-052**: Select all/none checkboxes in header

#### 3.3 Individual Actions
- **REQ-DV-053**: Row-level action menu (three dots) with options:
  - View Details
  - Edit Session
  - Duplicate Session
  - Archive/Unarchive
  - Delete (with confirmation)

### 4. Session Details View

#### 4.1 Expandable Details Panel
- **REQ-DV-054**: Show comprehensive session information when row is selected
- **REQ-DV-055**: Organize details in logical sections:
  - **Session Info**: Name, status, created date, notes
  - **Rifle Configuration**: Name, barrel specs
  - **Cartridge Specifications**: Complete cartridge data
  - **Bullet Ballistics**: Complete bullet data with all coefficients
  - **Weather Conditions**: All weather measurements
  - **Range Information**: Location data and coordinates
- **REQ-DV-056**: Display related measurement data if available
- **REQ-DV-057**: Show creation and modification timestamps

#### 4.2 Quick Edit Mode
- **REQ-DV-058**: Allow inline editing of session name and notes
- **REQ-DV-059**: Status toggle button (Active ↔ Archived)
- **REQ-DV-060**: Save/Cancel buttons for inline edits
- **REQ-DV-061**: Validate required fields before saving

### 5. Data Management

#### 5.1 Export Functionality
- **REQ-DV-062**: Export filtered sessions to CSV format (all columns)
- **REQ-DV-063**: Export selected sessions to CSV format
- **REQ-DV-064**: Include all session data in exports with proper formatting
- **REQ-DV-065**: Filename with timestamp (e.g., "dope_sessions_2024-03-15.csv")

#### 5.2 Import/Sync
- **REQ-DV-066**: Refresh button to reload data from database
- **REQ-DV-067**: Auto-refresh when returning to tab (cache management)
- **REQ-DV-068**: Loading states during data operations

### 6. User Experience

#### 6.1 Performance
- **REQ-DV-069**: Load initial data within 3 seconds
- **REQ-DV-070**: Filter operations complete within 500ms
- **REQ-DV-071**: Smooth scrolling for large datasets
- **REQ-DV-072**: Virtual scrolling for tables with >100 rows

#### 6.2 Responsive Design
- **REQ-DV-073**: Responsive table design with horizontal scrolling
- **REQ-DV-074**: Mobile-friendly filtering interface with collapsible sections
- **REQ-DV-075**: Touch-friendly selection on mobile devices

#### 6.3 Error Handling
- **REQ-DV-076**: Graceful handling of database connection errors
- **REQ-DV-077**: User-friendly error messages
- **REQ-DV-078**: Retry mechanism for failed operations
- **REQ-DV-079**: Offline state handling

### 7. Integration Requirements

#### 7.1 Navigation
- **REQ-DV-080**: "Create New Session" button linking to DOPE Create page
- **REQ-DV-081**: "Analytics" button linking to DOPE Analytics page
- **REQ-DV-082**: Breadcrumb navigation showing current location

#### 7.2 Data Dependencies
- **REQ-DV-083**: Integration with DopeService for all database operations
- **REQ-DV-084**: Consistent with DopeSessionModel data structure
- **REQ-DV-085**: Real-time updates when sessions are modified in other tabs

## Technical Requirements

### 8. Implementation Specifications

#### 8.1 Framework Integration
- **REQ-DV-086**: Built using Streamlit components and widgets
- **REQ-DV-087**: Use st.dataframe with column configuration for main table
- **REQ-DV-088**: Implement filtering using organized sidebar sections
- **REQ-DV-089**: Session state management for selected items and filters

#### 8.2 Service Integration
- **REQ-DV-090**: Use DopeService for all data operations
- **REQ-DV-091**: Handle service exceptions gracefully
- **REQ-DV-092**: Cache frequently accessed data appropriately

#### 8.3 Security
- **REQ-DV-093**: User authentication required before accessing any data
- **REQ-DV-094**: User data isolation (only show user's own sessions)
- **REQ-DV-095**: Input validation for all filter parameters
- **REQ-DV-096**: CSRF protection for state-modifying operations

## Success Criteria

1. **Usability**: Users can easily find and manage their DOPE sessions with comprehensive filtering
2. **Performance**: Page loads and operations are responsive even with large datasets
3. **Reliability**: Data operations are consistent and error-free
4. **Completeness**: All session data is accessible and filterable
5. **Maintainability**: Code follows established patterns and is well-documented

## Data Column Priorities

### High Priority (Always Visible)
- Session Name, Created At, Status
- Cartridge Type, Bullet Make/Model/Weight
- Distance, Range Name

### Medium Priority (Toggleable)
- Rifle Name, Weather Summary
- Temperature, Humidity, Wind Speed

### Low Priority (Advanced View)
- All detailed ballistic coefficients
- Precise coordinates and angles
- Technical specifications