# ChronoLog Application - Specifications and Requirements Document

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Functional Requirements](#functional-requirements)
4. [Non-Functional Requirements](#non-functional-requirements)
5. [Data Requirements](#data-requirements)
6. [User Requirements](#user-requirements)
7. [Integration Requirements](#integration-requirements)
8. [Security Requirements](#security-requirements)
9. [File Processing Requirements](#file-processing-requirements)
10. [Testing and Quality Assurance](#testing-and-quality-assurance)
11. [Deployment and Environment Setup](#deployment-and-environment-setup)
12. [Performance Requirements](#performance-requirements)

## System Overview

### Application Purpose
ChronoLog is a comprehensive ballistics data management application designed to automate DOPE (Data On Previous Engagements) construction from multiple data sources. The system integrates chronograph data, weather measurements, range information, and equipment specifications to provide precision shooters with automated ballistic analysis and record keeping.

### Key Features
- **Automated Data Integration**: Merges chronograph data, weather conditions, and range information
- **Equipment Tracking**: Manages rifles, bullets, factory cartridges, and custom ammunition loads
- **DOPE Session Management**: Creates comprehensive shooting session records
- **Multi-Source Data Processing**: Supports Garmin Xero chronographs and Kestrel weather meters
- **Range Management**: GPS-based range library with distance and elevation calculations
- **User Management**: Multi-tenant system with role-based access control

### Technology Stack
- **Frontend**: Streamlit 1.46.0 (Python web framework)
- **Backend**: Supabase (PostgreSQL database + Storage + Auth)
- **Authentication**: Auth0 with Google OAuth integration
- **Data Processing**: Pandas 2.3.0, OpenPyXL 3.1.5
- **Visualization**: Plotly, Matplotlib, Folium
- **Testing**: Pytest 8.4.1 with coverage and HTML reporting

## Architecture

### System Architecture
The ChronoLog application follows a multi-tier architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  Streamlit Web Interface + Auth0 Authentication             │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                        │
│  Service Classes + Business Logic + File Processing         │
├─────────────────────────────────────────────────────────────┤
│                      Data Layer                             │
│  Supabase (PostgreSQL) + Storage + External APIs            │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### Core Components
- **ChronoLog.py**: Main application entry point that delegates to landing page
- **auth.py**: Authentication management with Auth0 Google OAuth
- **pages/**: Modular page components for different application features
- **Service Layer**: Domain-specific services (chronograph, weather, dope, etc.)
- **Model Layer**: Data entities and Supabase integration
- **Utility Layer**: File processing, validation, and shared functionality

#### Page Structure
- **Home (1_🏠_Home.py)**: Landing page with application overview
- **DOPE (2_📊_DOPE.py)**: DOPE session creation and management
- **Chronograph (3_⏱️_Chronograph.py)**: Garmin Xero data import and viewing
- **Weather (4_🌤️_Weather.py)**: Kestrel meter data import and sources
- **Ranges (5_🌍_Ranges.py)**: GPS-based range management
- **Rifles (6_📏_Rifles.py)**: Rifle configuration management
- **Factory Cartridges (7_🏭_Factory_Cartridges.py)**: Commercial ammunition tracking
- **Custom Cartridges (8_🎯_Custom_Cartridges.py)**: Custom load development
- **Bullets (9_📦_Bullets.py)**: Bullet specifications and ballistic data
- **Admin (10_👑_Admin.py)**: Administrative functions

### Service Layer Pattern
All database operations are abstracted through service classes:
- **ChronographService**: Manages chronograph sessions and measurements
- **WeatherService**: Handles weather sources and measurements
- **UserService**: User profile and authentication management
- **RangeService**: Range submission and management

## Functional Requirements

### FR1: User Authentication and Profile Management
- **FR1.1**: Users must authenticate via Auth0 Google OAuth
- **FR1.2**: System must support user profile creation and management
- **FR1.3**: Users must complete profile setup (username, location, unit system)
- **FR1.4**: System must validate username uniqueness and format constraints
- **FR1.5**: Admin users must have elevated privileges for system management

### FR2: Chronograph Data Management
- **FR2.1**: System must import Garmin Xero Excel files (.xlsx format)
- **FR2.2**: System must parse bullet metadata from first row (type, grain weight)
- **FR2.3**: System must extract shot measurements (speed, energy, power factor)
- **FR2.4**: System must calculate session statistics (avg, std dev, min/max velocity)
- **FR2.5**: System must support session filtering and search capabilities
- **FR2.6**: System must prevent duplicate session imports

### FR3: Weather Data Management
- **FR3.1**: System must import Kestrel weather meter CSV files
- **FR3.2**: System must track weather source devices and configurations
- **FR3.3**: System must capture environmental conditions (temperature, humidity, pressure, wind)
- **FR3.4**: System must support multiple weather measurement formats
- **FR3.5**: System must provide weather data visualization and analysis

### FR4: Range Management
- **FR4.1**: System must support GPS coordinate-based range definitions
- **FR4.2**: System must calculate distance and elevation angles between positions
- **FR4.3**: System must provide range submission workflow for new ranges
- **FR4.4**: System must support admin approval process for range submissions
- **FR4.5**: System must integrate with mapping services for visualization

### FR5: Equipment Management
- **FR5.1**: System must manage rifle configurations (barrel, trigger, scope)
- **FR5.2**: System must maintain bullet database with ballistic coefficients
- **FR5.3**: System must track factory cartridge specifications
- **FR5.4**: System must support custom cartridge load development
- **FR5.5**: System must link cartridges to bullet specifications

### FR6: DOPE Session Management
- **FR6.1**: System must create comprehensive DOPE sessions from multiple data sources
- **FR6.2**: System must link chronograph, weather, range, and equipment data
- **FR6.3**: System must support manual ballistic adjustment entry
- **FR6.4**: System must provide session editing and annotation capabilities
- **FR6.5**: System must generate exportable DOPE records

### FR7: File Management
- **FR7.1**: System must provide secure file upload to cloud storage
- **FR7.2**: System must organize files by user and data type
- **FR7.3**: System must prevent file name conflicts and duplicates
- **FR7.4**: System must support file deletion and management
- **FR7.5**: System must track file metadata and upload timestamps

### FR8: Data Visualization and Reporting
- **FR8.1**: System must provide chronograph data visualization
- **FR8.2**: System must display weather condition trends
- **FR8.3**: System must show ballistic performance analysis
- **FR8.4**: System must support data export capabilities
- **FR8.5**: System must provide session comparison tools

## Non-Functional Requirements

### NFR1: Performance Requirements
- **NFR1.1**: Page load times must not exceed 3 seconds under normal load
- **NFR1.2**: File uploads must process within 30 seconds for typical Excel files
- **NFR1.3**: Database queries must return results within 2 seconds
- **NFR1.4**: System must support concurrent users without performance degradation

### NFR2: Reliability Requirements
- **NFR2.1**: System must maintain 99.5% uptime during business hours
- **NFR2.2**: Data integrity must be maintained through transaction consistency
- **NFR2.3**: System must handle file upload failures gracefully
- **NFR2.4**: Error messages must be user-friendly and actionable

### NFR3: Scalability Requirements
- **NFR3.1**: System must support up to 1000 concurrent users
- **NFR3.2**: Database must handle up to 1 million measurement records
- **NFR3.3**: File storage must accommodate up to 100GB per user
- **NFR3.4**: System architecture must support horizontal scaling

### NFR4: Usability Requirements
- **NFR4.1**: Interface must be intuitive for users with basic computer skills
- **NFR4.2**: System must provide contextual help and tooltips
- **NFR4.3**: Error handling must guide users toward resolution
- **NFR4.4**: Mobile responsiveness must support tablet usage

### NFR5: Maintainability Requirements
- **NFR5.1**: Code must maintain modular architecture with clear separation of concerns
- **NFR5.2**: All modules must have comprehensive unit test coverage
- **NFR5.3**: Database schema changes must be versioned and documented
- **NFR5.4**: System must support automated deployment processes

## Data Requirements

### Database Schema

#### Core Tables

**users**
```sql
- id (text, PK): Auth0 user identifier
- email (text, NOT NULL): User email address
- name (text, NOT NULL): User display name
- username (text, NOT NULL): Unique username (3-30 chars, alphanumeric)
- state (text, NOT NULL): User's state/province
- country (text, NOT NULL): User's country
- unit_system (text, NOT NULL): 'Imperial' or 'Metric'
- profile_complete (boolean): Profile completion status
- picture (text): Profile image URL
- roles (text[], DEFAULT ['user']): User roles (user, admin)
- created_at (timestamptz): Account creation timestamp
- updated_at (timestamptz): Last profile update
```

**chrono_sessions**
```sql
- id (uuid, PK): Session identifier
- user_id (text, NOT NULL): Auth0 user identifier
- tab_name (text, NOT NULL): UI tab identifier
- bullet_type (text, NOT NULL): Bullet type/model
- bullet_grain (numeric): Bullet weight in grains
- datetime_local (timestamptz, NOT NULL): Session timestamp
- uploaded_at (timestamptz): File upload timestamp
- file_path (text): Original file path
- shot_count (integer): Number of shots in session
- avg_speed_fps (numeric): Average velocity
- std_dev_fps (numeric): Standard deviation
- min_speed_fps (numeric): Minimum velocity
- max_speed_fps (numeric): Maximum velocity
- created_at (timestamptz): Record creation
```

**chrono_measurements**
```sql
- id (uuid, PK): Measurement identifier
- user_id (text, NOT NULL): Auth0 user identifier
- chrono_session_id (uuid, FK): Parent session
- shot_number (integer, NOT NULL): Shot sequence number
- speed_fps (numeric, NOT NULL): Velocity in feet per second
- delta_avg_fps (numeric): Deviation from average
- ke_ft_lb (numeric): Kinetic energy in foot-pounds
- power_factor (numeric): Power factor calculation
- datetime_local (timestamptz): Shot timestamp
- clean_bore (boolean): Clean bore indicator
- cold_bore (boolean): Cold bore indicator
- shot_notes (text): Shot-specific notes
```

**dope_sessions**
```sql
- id (uuid, PK): DOPE session identifier
- user_id (text, NOT NULL): Auth0 user identifier
- session_name (text): Descriptive session name
- chrono_session_id (uuid, FK): Linked chronograph session
- range_submission_id (uuid, FK): Associated range
- weather_source_id (uuid, FK): Weather data source
- rifle_id (uuid, FK): Rifle configuration
- cartridge_type (text): 'factory' or 'custom'
- cartridge_spec_id (uuid): Reference to cartridge spec
- cartridge_lot_number (text): Lot identifier
- range_name (text): Range name
- distance_m (real): Target distance in meters
- notes (text): Session notes
- status (text): Session status
- created_at (timestamptz): Session creation
- updated_at (timestamptz): Last modification
```

#### Supporting Tables

**weather_source** - Weather measurement devices
**weather_measurements** - Environmental condition records
**rifles** - User rifle configurations
**bullets** - Bullet specifications and ballistic data
**factory_cartridge_specs** - Commercial cartridge specifications
**custom_cartridge_specs** - User-defined custom loads
**ranges** - Approved public shooting ranges
**ranges_submissions** - User-submitted range data

### Data Integrity Requirements
- **DR1**: All user data must be isolated by user_id/email
- **DR2**: Foreign key relationships must be enforced
- **DR3**: Required fields must be validated before insertion
- **DR4**: Timestamps must use consistent timezone handling
- **DR5**: Numeric data must be validated for reasonable ranges

### Data Retention Requirements
- **DR6**: User data must be retained indefinitely unless user requests deletion
- **DR7**: File uploads must be backed up with point-in-time recovery
- **DR8**: Session data must maintain referential integrity
- **DR9**: Deleted records must be soft-deleted for audit trail

## User Requirements

### User Roles and Permissions

#### Standard User
- Create and manage personal shooting data
- Upload chronograph and weather files
- Create DOPE sessions
- Manage equipment configurations
- Submit new range requests
- View and edit own data only

#### Admin User
- All standard user capabilities
- Review and approve range submissions
- Manage factory cartridge database
- View system-wide statistics
- Manage user accounts
- Access administrative functions

### User Experience Requirements
- **UX1**: Single sign-on through Google OAuth
- **UX2**: Progressive disclosure of advanced features
- **UX3**: Consistent navigation and page structure
- **UX4**: Real-time feedback for user actions
- **UX5**: Graceful handling of error conditions

### Accessibility Requirements
- **A1**: Interface must support keyboard navigation
- **A2**: Color schemes must meet WCAG contrast requirements
- **A3**: Screen reader compatibility for key functions
- **A4**: Responsive design for tablet and desktop usage

## Integration Requirements

### Auth0 Integration
- **I1**: Google OAuth 2.0 authentication flow
- **I2**: User profile synchronization
- **I3**: Session management and token refresh
- **I4**: Secure redirect URI handling
- **I5**: Support for local development and production environments

### Supabase Integration
- **I6**: PostgreSQL database connectivity
- **I7**: Real-time subscriptions for data updates
- **I8**: File storage with access control
- **I9**: Row-level security policies
- **I10**: Automated backup and recovery

### External Service Integration
- **I11**: Geolocation services for range mapping
- **I12**: File format validation and parsing
- **I13**: Email notifications for admin workflows
- **I14**: Error monitoring and logging services

## Security Requirements

### Authentication and Authorization
- **S1**: All users must authenticate through Auth0
- **S2**: Session tokens must expire and refresh automatically
- **S3**: User data access must be restricted by ownership
- **S4**: Admin functions must require elevated privileges
- **S5**: API keys and secrets must be stored securely

### Data Protection
- **S6**: All data transmission must use HTTPS/TLS
- **S7**: Database connections must be encrypted
- **S8**: File uploads must be validated for type and content
- **S9**: User input must be sanitized against injection attacks
- **S10**: Sensitive data must not be logged in plain text

### Privacy Requirements
- **S11**: User data must be isolated between accounts
- **S12**: File storage must implement access controls
- **S13**: User data deletion must be complete and irreversible
- **S14**: Data processing must comply with privacy regulations

## File Processing Requirements

### Garmin Xero Excel Processing
- **FP1**: Support for .xlsx format files
- **FP2**: Parse bullet metadata from first row (type, grain weight)
- **FP3**: Extract measurement data starting from row 2
- **FP4**: Handle optional fields (Clean Bore, Cold Bore, Shot Notes)
- **FP5**: Extract session timestamps from sheet metadata
- **FP6**: Calculate session statistics (average, std dev, range)
- **FP7**: Validate measurement data for reasonable values

### Kestrel Weather CSV Processing
- **FP8**: Support for standard Kestrel CSV export format
- **FP9**: Parse environmental measurements (temp, humidity, pressure, wind)
- **FP10**: Extract device information and serial numbers
- **FP11**: Handle timestamp conversion and timezone issues
- **FP12**: Process location and GPS coordinate data
- **FP13**: Validate weather data for realistic ranges

### File Validation Requirements
- **FP14**: Verify file format before processing
- **FP15**: Check file size limits (prevent DoS attacks)
- **FP16**: Validate file content structure
- **FP17**: Handle malformed or corrupted files gracefully
- **FP18**: Provide detailed error messages for invalid files

## Testing and Quality Assurance

### Unit Testing Requirements
- **T1**: All service classes must have comprehensive unit tests
- **T2**: Model classes must test data validation and conversion
- **T3**: File processing functions must test various input formats
- **T4**: Database operations must use mocked Supabase clients
- **T5**: Test coverage must exceed 80% for core functionality

### Integration Testing Requirements
- **T6**: End-to-end testing of file upload and processing workflows
- **T7**: Authentication flow testing with mocked Auth0 responses
- **T8**: Database integration testing with test data
- **T9**: Cross-page navigation and state management testing
- **T10**: File storage integration testing

### Testing Framework
- **Testing Tool**: Pytest 8.4.1 with pytest-mock and pytest-cov
- **Test Organization**: Modular tests in respective feature directories
- **Test Execution**: Automated via `run_all_tests.py` and `run_integration_tests.py`
- **Coverage Reporting**: HTML coverage reports with pytest-html
- **Commit Requirements**: All tests must pass before code commits

### Quality Gates
- **QG1**: No commits allowed with failing tests
- **QG2**: Code formatting enforced with Black 25.1.0
- **QG3**: Import organization enforced with isort 6.0.1
- **QG4**: Pre-commit hooks for quality checks
- **QG5**: Continuous integration for automated testing

## Deployment and Environment Setup

### Development Environment
```bash
# Virtual environment setup
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Environment variables
export SUPABASE_SERVICE_ROLE_KEY=your_key_here

# Application startup
streamlit run ChronoLog.py
```

### Testing Environment
```bash
# Unit tests
python run_all_tests.py

# Integration tests  
python run_integration_tests.py

# Supabase connectivity verification
python verify_supabase.py
```

### Production Environment
- **Cloud Platform**: Streamlit Cloud or equivalent
- **Database**: Supabase hosted PostgreSQL
- **Authentication**: Auth0 production tenant
- **File Storage**: Supabase Storage with CDN
- **Monitoring**: Application and database performance monitoring

### Configuration Management
- **Environment Variables**: Sensitive credentials via environment variables
- **Secrets Management**: Streamlit secrets.toml for configuration
- **Version Control**: Git-based deployment with automated pipelines
- **Database Migrations**: Versioned schema changes through Supabase migrations

### Backup and Recovery
- **Database Backups**: Automated daily backups with point-in-time recovery
- **File Storage Backups**: Redundant storage with geographic distribution
- **Disaster Recovery**: RTO of 4 hours, RPO of 1 hour
- **Testing**: Regular backup restoration testing

## Performance Requirements

### Response Time Requirements
- **P1**: Page initial load: < 3 seconds
- **P2**: File upload processing: < 30 seconds for typical files
- **P3**: Database queries: < 2 seconds
- **P4**: Authentication flow: < 5 seconds
- **P5**: Data visualization rendering: < 5 seconds

### Throughput Requirements
- **P6**: Support 100 concurrent file uploads
- **P7**: Handle 1000 concurrent page views
- **P8**: Process 10,000 measurement records per minute
- **P9**: Support 50 simultaneous DOPE session creations

### Resource Utilization
- **P10**: Memory usage: < 2GB per application instance
- **P11**: CPU utilization: < 80% under normal load
- **P12**: Database connections: < 100 concurrent connections
- **P13**: File storage: 99.9% availability with sub-second access times

### Scalability Targets
- **P14**: Linear performance scaling with horizontal instances
- **P15**: Database read replicas for query distribution
- **P16**: CDN integration for static asset delivery
- **P17**: Caching strategy for frequently accessed data

---

**Document Version**: 1.0  
**Last Updated**: 2025-08-18  
**Author**: System Analysis of ChronoLog Codebase  
**Status**: Complete and ready for implementation reference