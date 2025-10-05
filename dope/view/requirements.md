# DOPE View Requirements Specification

## Overview

The DOPE View module provides a comprehensive interface for users to view, filter, search, and manage their DOPE (Data On Previous Engagement) sessions. This module renders session data in a tabular format with advanced filtering capabilities and allows users to select sessions for detailed viewing and editing.

**IMPORTANT**: All requirements in this document must adhere to the global project requirements specified in CLAUDE.md. In case of conflicts, CLAUDE.md takes precedence.

## Functional Requirements

### 1. Session Data Display

#### 1.1 Complete Data Table Rendering
- **REQ-DV-001**: ✅ **RESOLVED** - Display all DOPE sessions for the authenticated user in a sortable data table
- **REQ-DV-002**: ✅ **RESOLVED** - Show default session table columns: Selector, Start Time, Session Name, Range Name, Rifle, Cartridge Type, Bullet, Bullet Weight (user preferred units)
  - **Additional Available Columns**: Distance, Weather Summary (Temperature, Humidity, Wind Speed), Session Notes (truncated for table display)
  - **Hidden from UI**: All UUID fields (ID, Chrono Session ID, Weather Source ID, Rifle ID), detailed technical specifications
- **REQ-DV-003**: ⚠️ **PARTIAL** - Support column visibility toggle (user can show/hide columns) - Basic implementation exists but needs refinement
- **REQ-DV-004**: ✅ **RESOLVED** - Support pagination when more than 50 sessions exist
- **REQ-DV-005**: ✅ **RESOLVED** - Display session count and total records information
- **REQ-DV-006**: ⚠️ **PARTIAL** - Column resizing and reordering capabilities - Limited by Streamlit dataframe widget

#### 1.2 Data Formatting and Global Application Standards
- **REQ-DV-007**: ✅ **RESOLVED** - Format dates in user-friendly format (e.g., "Mar 15, 2024 10:30 AM")
- **REQ-DV-008**: ✅ **RESOLVED** - Display numeric values without unit suffixes - units are provided in column headers
- **REQ-DV-009**: ✅ **RESOLVED** - Show distance, weight, temperature, humidity, and other measurements as numeric values only
- **REQ-DV-010**: ✅ **RESOLVED** - Format weather data with appropriate precision (no unit suffixes in values)
- **REQ-DV-011**: ✅ **RESOLVED** - ~~Use status badges with appropriate colors (Active: Green, Archived: Gray)~~ **[DEPRECATED]** - Status field removed from schema
- **REQ-DV-012**: ✅ **RESOLVED** - Handle null/empty values gracefully with placeholder text
- **REQ-DV-013**: ✅ **RESOLVED** - Include units in column headers based on user preferences (e.g., "Distance (m)" or "Distance (ft)", "Temperature (°C)" or "Temperature (°F)")
- **REQ-DV-139**: ✅ **RESOLVED** - **GLOBAL STANDARD**: Store all measurement data in metric units in database regardless of user interface preferences
- **REQ-DV-140**: ✅ **RESOLVED** - **GLOBAL STANDARD**: Convert values to user's preferred unit system for display only (Imperial/Metric toggle in user settings)
- **REQ-DV-141**: ✅ **RESOLVED** - **GLOBAL STANDARD**: Never expose UUID/ID fields in user interface - use meaningful names and references only
- **REQ-DV-142**: ✅ **RESOLVED** - **GLOBAL STANDARD**: All filtering, sorting, and export operations work on metric data internally, display in user preferred units
- **REQ-DV-143**: ✅ **RESOLVED** - **GLOBAL STANDARD**: Remove duplicate/archive functionality - sessions are either active or deleted

### 2. Comprehensive Filtering and Search

#### 2.1 Basic Filters
- **REQ-DV-144**: ✅ **RESOLVED** - Created At date range picker
- **REQ-DV-014**: ✅ **RESOLVED** - ~~Status filter dropdown (All, Active, Archived)~~ **[DEPRECATED]** - Status field removed from schema
- **REQ-DV-015**: ✅ **RESOLVED** - Rifle Name filter with autocomplete dropdown
- **REQ-DV-016**: ✅ **RESOLVED** - Range Name filter with autocomplete dropdown

#### 2.2 Cartridge Filters
- **REQ-DV-017**: ✅ **RESOLVED** - Cartridge Make filter with autocomplete
- **REQ-DV-018**: ❌ **MISSING** - Cartridge Model filter with autocomplete  
- **REQ-DV-019**: ✅ **RESOLVED** - Cartridge Type filter with autocomplete
- **REQ-DV-020**: ⚠️ **PARTIAL** - Combined cartridge search across all cartridge fields (global search works but dedicated combined filter missing)

#### 2.3 Bullet Filters (Display Units Based on User Preference)
- **REQ-DV-021**: ✅ **RESOLVED** - Bullet Make filter with autocomplete
- **REQ-DV-022**: ❌ **MISSING** - Bullet Model filter with autocomplete
- **REQ-DV-023**: ✅ **RESOLVED** - Bullet Weight filter with range slider (grains/grams based on user preference)
- **REQ-DV-024**: ⚠️ **PARTIAL** - Combined bullet search across all bullet fields (global search works but dedicated combined filter missing)

#### 2.4 Weather Filters (Display Units Based on User Preference)
- **REQ-DV-025**: ✅ **RESOLVED** - Temperature range filter (°C/°F based on user preference, min/max sliders)
- **REQ-DV-026**: ✅ **RESOLVED** - Humidity range filter (%, min/max sliders)
- **REQ-DV-027**: ❌ **MISSING** - Pressure range filter (hPa/inHg based on user preference, min/max sliders)
- **REQ-DV-028**: ✅ **RESOLVED** - Wind Speed range filter (m/s/mph based on user preference, min/max sliders)
- **REQ-DV-029**: ❌ **MISSING** - Wind Direction range filter (degrees, circular slider)
- **REQ-DV-030**: ✅ **RESOLVED** - ~~Weather Source Name filter with autocomplete~~ **[DEPRECATED]** - UUID field hidden from UI

#### 2.5 Range and Position Filters (Display Units Based on User Preference)
- **REQ-DV-031**: ✅ **RESOLVED** - Distance range filter (m/ft based on user preference, min/max sliders)
- **REQ-DV-032**: ❌ **MISSING** - Altitude range filter (m/ft based on user preference, min/max sliders)
- **REQ-DV-033**: ❌ **MISSING** - Geographic bounding box filter (lat/lon coordinates)
- **REQ-DV-034**: ❌ **MISSING** - Azimuth range filter (degrees, circular slider)
- **REQ-DV-035**: ❌ **MISSING** - Elevation angle range filter (degrees, min/max sliders)

#### 2.6 Advanced Search and Filtering
- **REQ-DV-036**: ✅ **RESOLVED** - Global search box that searches across all text fields:
  - Session name, notes
  - Rifle name
  - Cartridge make/model/type
  - Bullet make/model
  - Range name
  - Weather source name
- **REQ-DV-037**: ⚠️ **PARTIAL** - Real-time search results as user types (debounced) - Works but could be optimized
- **REQ-DV-038**: ✅ **RESOLVED** - Multiple filter combination with AND logic
- **REQ-DV-039**: ❌ **MISSING** - Save filter presets for quick reuse
- **REQ-DV-040**: ✅ **RESOLVED** - Clear all filters button
- **REQ-DV-041**: ⚠️ **PARTIAL** - Filter summary display showing active filters (basic implementation exists)

#### 2.7 Sorting
- **REQ-DV-042**: ✅ **RESOLVED** - Sort by any column (ascending/descending)
- **REQ-DV-043**: ⚠️ **PARTIAL** - Multi-column sorting support (limited by Streamlit dataframe capabilities)
- **REQ-DV-044**: ✅ **RESOLVED** - Default sort by created date (newest first)
- **REQ-DV-045**: ⚠️ **PARTIAL** - Visual indicators for current sort column and direction (basic implementation)

### 3. Session Selection and Actions

#### 3.1 Row Selection
- **REQ-DV-046**: ✅ **RESOLVED** - Allow single-click row selection with visual highlighting
- **REQ-DV-047**: ✅ **RESOLVED** - Show selected session details in expandable section
- **REQ-DV-048**: ❌ **MISSING** - Support keyboard navigation (arrow keys, Enter to select)
- **REQ-DV-049**: ❌ **MISSING** - Double-click row to open edit mode

#### 3.2 Bulk Operations
- **REQ-DV-050**: ✅ **RESOLVED** - Support multi-row selection with checkboxes
- **REQ-DV-051**: ✅ **RESOLVED** - Bulk actions dropdown for selected sessions:
  - Delete selected (with confirmation)
  - Export selected to CSV
- **REQ-DV-052**: ⚠️ **PARTIAL** - Select all/none checkboxes in header (functionality exists but UI could be improved)

#### 3.3 Individual Actions
- **REQ-DV-053**: ✅ **RESOLVED** - Row-level action menu (three dots) with options:
  - View Details
  - Edit Session
  - Delete (with confirmation)
 
### 4. Session Details View

#### 4.1 Expandable Details Panel
- **REQ-DV-054**: ✅ **RESOLVED** - Show comprehensive session information when row is selected
- **REQ-DV-055**: ✅ **RESOLVED** - Organize details in logical sections with tabbed interface:
  - **Session Info**: Name, created date, notes with proper data source formatting (4-space indentation for sub-items) - read-only
  - **Range**: Location coordinates with Google Maps hyperlink, altitude, azimuth angle (not just "azimuth"), elevation angle (distance field removed) - read-only
  - **Rifle Configuration**: Name, barrel specs (no UUID display) - read-only
  - **Bullet Ballistics**: Physical measurements grouped (Length, Diameter Land/Groove), Ballistic coefficients grouped (BC G1/G7) - read-only
  - **Cartridge Specifications**: Complete cartridge data - read-only
  - **Weather Conditions**: All weather measurements with wind data grouped on right side, units following user preferences - read-only
  - **Shots**: Contains a shots table (read-only display) with single row selection capability. When a row is selected, shot details are rendered below the table with all fields editable
- **REQ-DV-056**: ✅ **RESOLVED** - Display related measurement data if available
- **REQ-DV-057**: ✅ **RESOLVED** - Show creation and modification timestamps
- **REQ-DV-145**: ✅ **RESOLVED** - Remove duplicate button functionality from session details
- **REQ-DV-146**: ✅ **RESOLVED** - Remove archive functionality text and controls

#### 4.2 Session Info Tab Specifications
- **REQ-DV-058**: Allow inline editing of session name and notes
- **REQ-DV-147**: Display data sources with proper visual hierarchy using 4-space indentation
- **REQ-DV-148**: Show actual chronograph source names instead of "Linked" status
- **REQ-DV-149**: Show actual weather source names or "Not-linked" instead of UUID
- **REQ-DV-150**: Remove emoji text (e.g., "🕐 Session Times:")
- **REQ-DV-151**: Replace all UUID displays with meaningful names and references
- **REQ-DV-166**: Display chronograph source name instead of "Linked" status - use chronograph session name when available, "Linked" when chrono_session_id exists but no name, "Not-linked" when no chronograph connection
- **REQ-DV-060**: Save/Cancel buttons for inline edits
- **REQ-DV-061**: Validate required fields before saving

### 5. Data Management

#### 5.1 Export Functionality
- **REQ-DV-062**: ✅ **RESOLVED** - Export filtered sessions to CSV format (all columns)
- **REQ-DV-063**: ✅ **RESOLVED** - Export selected sessions to CSV format
- **REQ-DV-064**: ✅ **RESOLVED** - Include all session data in exports with proper formatting
- **REQ-DV-065**: ✅ **RESOLVED** - Filename with timestamp (e.g., "dope_sessions_2024-03-15.csv")

#### 5.2 Import/Sync
- **REQ-DV-066**: ✅ **RESOLVED** - Refresh button to reload data from database
- **REQ-DV-067**: ⚠️ **PARTIAL** - Auto-refresh when returning to tab (cache management) - Basic cache clearing implemented
- **REQ-DV-068**: ⚠️ **PARTIAL** - Loading states during data operations - Basic implementation exists

### 6. User Experience

#### 6.1 Performance
- **REQ-DV-069**: ✅ **RESOLVED** - Load initial data within 3 seconds
- **REQ-DV-070**: ✅ **RESOLVED** - Filter operations complete within 500ms
- **REQ-DV-071**: ⚠️ **PARTIAL** - Smooth scrolling for large datasets (limited by Streamlit framework)
- **REQ-DV-072**: ❌ **MISSING** - Virtual scrolling for tables with >100 rows (Streamlit limitation)

#### 6.2 Responsive Design
- **REQ-DV-073**: ✅ **RESOLVED** - Responsive table design with horizontal scrolling
- **REQ-DV-074**: ⚠️ **PARTIAL** - Mobile-friendly filtering interface with collapsible sections
- **REQ-DV-075**: ⚠️ **PARTIAL** - Touch-friendly selection on mobile devices (limited by Streamlit)

#### 6.3 Error Handling
- **REQ-DV-076**: ✅ **RESOLVED** - Graceful handling of database connection errors
- **REQ-DV-077**: ✅ **RESOLVED** - User-friendly error messages
- **REQ-DV-078**: ❌ **MISSING** - Retry mechanism for failed operations
- **REQ-DV-079**: ❌ **MISSING** - Offline state handling

### 7. Integration Requirements

#### 7.1 Navigation
- **REQ-DV-080**: ✅ **RESOLVED** - "Create New Session" button linking to DOPE Create page
- **REQ-DV-081**: ❌ **MISSING** - "Analytics" button linking to DOPE Analytics page
- **REQ-DV-082**: ❌ **MISSING** - Breadcrumb navigation showing current location

#### 7.2 Data Dependencies
- **REQ-DV-083**: ✅ **RESOLVED** - Integration with DopeService for all database operations
- **REQ-DV-084**: ✅ **RESOLVED** - Consistent with DopeSessionModel data structure
- **REQ-DV-085**: ⚠️ **PARTIAL** - Real-time updates when sessions are modified in other tabs (basic refresh functionality)

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

### Default Columns (Always Visible)
- Selector, Start Time, Session Name, Range Name, Rifle, Cartridge Type, Bullet, Bullet Weight

### Additional Columns (Toggleable)
- Distance, Weather Summary
- Temperature, Humidity, Wind Speed
- Session Notes

### Advanced View (Optional)
- All detailed ballistic coefficients
- Precise coordinates and angles
- Technical specifications

## Bonus Features Implemented

### 9. Enhanced Shot Data Management

#### 9.1 Shot Measurements Table
- **REQ-DV-097**: ✅ **RESOLVED** - Provide editable table for individual shot measurements within session details
- **REQ-DV-098**: ✅ **RESOLVED** - Support real-time editing of shot data with automatic database persistence
- **REQ-DV-099**: ✅ **RESOLVED** - Display limited default columns: row selector, Shot #, Time, Velocity, Distance, Elevation Offset, Windage Offset, Notes
- **REQ-DV-100**: ✅ **RESOLVED** - Optional columns are : Wind Speed 1, Wind Speed 2, Wind Direction, Temp, Pressure, Humidity, Elevation Angle Deg, Azimuth Angle Deg, Cold Bore, Clean Bore, KE, Power Factor
- **REQ-DV-099b**: ⚠️ **PARTIAL** - When user selects the row, all fields for that row should appear beneath the table and be editable except shot number and timestamp (Select Mode tab exists but detail editing incomplete)
- **REQ-DV-101**: ❌ **MISSING** - Provide dropdown selection for clean bore and cold bore flags
- **REQ-DV-104**: ⚠️ **PARTIAL** - Show clear visual indicators for editable vs read-only fields

#### 9.2 Unit-Aware Data Entry and Display
- **REQ-DV-105**: ✅ **RESOLVED** - Respect user's preferred unit system (Imperial/Metric) for data display in shots table
- **REQ-DV-106**: ⚠️ **PARTIAL** - Automatically convert user input from display units to metric units for database storage (display conversion works, input conversion needs implementation)
- **REQ-DV-107**: ✅ **RESOLVED** - Support bidirectional unit conversion for velocity (fps ↔ m/s), energy (ft·lb ↔ J), temperature (°F ↔ °C), pressure (inHg ↔ hPa)
- **REQ-DV-108**: ✅ **RESOLVED** - Handle power factor conversion between grain·ft/s and kg·m/s systems
- **REQ-DV-109**: ✅ **RESOLVED** - Display column headers with appropriate units based on user preferences
- **REQ-DV-110**: ✅ **RESOLVED** - Store all data internally in metric units while presenting user-friendly units in interface

#### 9.3 User-Preferred Units in Filters
- **REQ-DV-111**: Apply user's unit system preference to all filter sliders and inputs
- **REQ-DV-112**: Convert temperature filter ranges between Celsius and Fahrenheit based on user preference
- **REQ-DV-113**: Convert wind speed filter ranges between m/s and mph based on user preference
- **REQ-DV-114**: Maintain metric storage for filter values while presenting preferred units in UI
- **REQ-DV-115**: Ensure filter persistence works correctly across unit system changes

#### 9.4 Weather Data Integration
- **REQ-DV-116**: Automatically populate weather data in DOPE measurements from linked chronograph sessions
- **REQ-DV-117**: Implement timestamp-based weather lookup within ±30 minutes of shot time
- **REQ-DV-118**: Backfill existing DOPE measurements with weather data where chronograph data is available
- **REQ-DV-119**: Display weather conditions (temperature, pressure, humidity) alongside shot data
- **REQ-DV-120**: Handle missing weather data gracefully with appropriate null value handling

#### 9.5 Enhanced Data Validation and Error Handling
- **REQ-DV-121**: Validate numeric inputs with appropriate ranges and precision
- **REQ-DV-122**: Provide clear error messages for invalid data entry
- **REQ-DV-123**: Handle unit conversion errors gracefully with fallback values
- **REQ-DV-124**: Implement optimistic UI updates with rollback on database save failure
- **REQ-DV-125**: Show loading states during save operations
- **REQ-DV-126**: Display success confirmation messages when changes are saved

#### 9.6 Individual Session Data Export
- **REQ-DV-127**: Export individual session shot data to CSV format
- **REQ-DV-128**: Include all shot measurements with proper unit formatting in exports
- **REQ-DV-129**: Generate timestamped filenames for shot data exports
- **REQ-DV-130**: Preserve user's preferred units in exported data format

#### 9.7 Range Tab Specifications
- **REQ-DV-152**: Display "Azimuth Angle:" label instead of just "Azimuth:"
- **REQ-DV-153**: Remove distance field from Range tab display
- **REQ-DV-154**: Include latitude/longitude coordinates with Google Maps hyperlink
- **REQ-DV-155**: Display altitude in user's preferred units (meters/feet)
- **REQ-DV-156**: Show both azimuth and elevation angles with proper formatting

#### 9.8 Weather Tab Specifications
- **REQ-DV-157**: Ensure all units align with user preferences (metric/imperial)
- **REQ-DV-158**: Group wind measurements together on the right side of the display
- **REQ-DV-159**: Display weather source name instead of UUID
- **REQ-DV-160**: Include Wind Speed 2 field in schema, model, and UI

#### 9.9 Shot Details Interface
- **REQ-DV-163**: When row is selected, display detailed shot information beneath table in organized layout:
  - Basic Info - Shot number (read-only), time (read-only), distance (editable)
  - Adjustments & Environment - elevation offset, windage offset, environmental conditions
  - Ballistic Data - Velocity, KE, Power Factor with proper unit conversion
- **REQ-DV-164**: Maintain column chooser functionality for customizable table display
- **REQ-DV-165**: All displayed values must respect user's preferred unit system


### 10. Advanced Field Standardization

#### 10.1 Database-Model Alignment
- **REQ-DV-131**: Ensure field names are consistent between database schema and model classes
- **REQ-DV-132**: Use standardized field naming (distance_m, elevation_adjustment, windage_adjustment)
- **REQ-DV-133**: Remove unit suffixes from field names to maintain unit-agnostic data storage
- **REQ-DV-134**: Implement proper field mapping between display names and database columns

#### 10.2 Unit-Agnostic Data Storage
- **REQ-DV-135**: Store all measurement data in metric units regardless of user interface preferences
- **REQ-DV-136**: Separate data storage from presentation layer for unit handling
- **REQ-DV-137**: Maintain data integrity across different unit system preferences
- **REQ-DV-138**: Ensure consistent data types and precision for all numeric fields

## Updated Success Criteria

1. **Usability**: Users can easily find, view, and edit their DOPE sessions with comprehensive filtering, tabbed organization, and dual-mode shot editing
2. **Performance**: Page loads and operations are responsive even with large datasets, including real-time editing operations
3. **Reliability**: Data operations are consistent and error-free, with proper unit conversion and validation
4. **Completeness**: All session data is accessible, filterable, and editable with full weather integration and proper data source referencing
5. **Maintainability**: Code follows established patterns, is well-documented, and maintains unit-agnostic architecture with consistent UI organization
6. **User Experience**: Interface adapts to user preferences for units while maintaining data consistency, provides clear visual hierarchy, and eliminates technical UUID exposure
7. **Data Integrity**: All UUID references are replaced with meaningful names, proper grouping of related data, and consistent formatting across all tabs