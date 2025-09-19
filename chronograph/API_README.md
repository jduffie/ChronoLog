# Chronograph API Documentation

## Overview

The Chronograph API provides comprehensive RESTful endpoints for managing chronograph sessions, measurements, and sources. This API follows modern design patterns with proper authentication, validation, and error handling.

### Key Features

- **Metric-only data storage** - All velocities stored in meters per second (m/s), energy in joules (J)
- **User isolation** - All operations are scoped to authenticated users
- **Comprehensive validation** - Input validation for ballistics safety and data integrity
- **Bulk operations** - Support for efficient bulk measurement uploads
- **Statistical analysis** - Built-in session statistics calculation
- **Pagination** - Efficient pagination for large datasets
- **Error handling** - Standardized error responses with detailed information

## Base URL

```
/api/v1/chronograph
```

## Authentication

All endpoints require authentication via JWT Bearer token:

```
Authorization: Bearer <jwt_token>
```

## Data Models

### Core Entities

#### ChronographSession
Represents a chronograph session containing metadata and statistics.

```json
{
  "id": "uuid",
  "user_id": "string",
  "tab_name": "string",
  "session_name": "string",
  "datetime_local": "2025-01-15T14:30:00Z",
  "uploaded_at": "2025-01-15T15:00:00Z",
  "file_path": "string",
  "chronograph_source_id": "uuid",
  "shot_count": 10,
  "avg_speed_mps": 762.5,
  "std_dev_mps": 8.2,
  "min_speed_mps": 751.3,
  "max_speed_mps": 775.1,
  "created_at": "2025-01-15T15:00:00Z"
}
```

#### ChronographMeasurement
Represents individual shot measurements.

```json
{
  "id": "uuid",
  "user_id": "string",
  "chrono_session_id": "uuid",
  "shot_number": 1,
  "speed_mps": 762.5,
  "datetime_local": "2025-01-15T14:30:15Z",
  "delta_avg_mps": -2.1,
  "ke_j": 3456.2,
  "power_factor_kgms": 0.0123,
  "clean_bore": true,
  "cold_bore": true,
  "shot_notes": "First shot of the day"
}
```

#### ChronographSource
Represents chronograph device information.

```json
{
  "id": "uuid",
  "user_id": "string",
  "name": "My Garmin Xero C1",
  "source_type": "chronograph",
  "device_name": "Garmin Xero C1",
  "make": "Garmin",
  "model": "Xero C1",
  "serial_number": "123456789",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

## API Endpoints

### Sessions

#### List Sessions
```http
GET /api/v1/chronograph/sessions
```

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `size` (int, default: 20, max: 100) - Items per page
- `bullet_type` (string, optional) - Filter by bullet type
- `start_date` (datetime, optional) - Start date filter
- `end_date` (datetime, optional) - End date filter
- `chronograph_source_id` (uuid, optional) - Filter by source device

**Response:**
```json
{
  "items": [/* array of ChronographSession objects */],
  "total": 50,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

#### Create Session
```http
POST /api/v1/chronograph/sessions
```

**Request Body:**
```json
{
  "tab_name": "Session_01",
  "session_name": "308 Winchester Load Development",
  "datetime_local": "2025-01-15T14:30:00",
  "file_path": "uploads/session_01.xlsx",
  "chronograph_source_id": "uuid"
}
```

**Response:** `201 Created` with ChronographSession object

#### Get Session
```http
GET /api/v1/chronograph/sessions/{session_id}
```

**Response:** ChronographSession object

#### Get Session Statistics
```http
GET /api/v1/chronograph/sessions/{session_id}/statistics
```

**Response:**
```json
{
  "session_id": "uuid",
  "shot_count": 10,
  "avg_speed_mps": 762.5,
  "std_dev_mps": 8.2,
  "min_speed_mps": 751.3,
  "max_speed_mps": 775.1,
  "extreme_spread_mps": 23.8,
  "coefficient_of_variation": 1.08
}
```

### Measurements

#### List Measurements for Session
```http
GET /api/v1/chronograph/sessions/{session_id}/measurements
```

**Response:** Array of ChronographMeasurement objects

#### Create Measurement
```http
POST /api/v1/chronograph/measurements
```

**Request Body:**
```json
{
  "chrono_session_id": "uuid",
  "shot_number": 1,
  "speed_mps": 762.5,
  "datetime_local": "2025-01-15T14:30:15",
  "delta_avg_mps": -2.1,
  "ke_j": 3456.2,
  "power_factor_kgms": 0.0123,
  "clean_bore": true,
  "cold_bore": true,
  "shot_notes": "First shot of the day"
}
```

**Response:** `201 Created` with ChronographMeasurement object

#### Bulk Create Measurements
```http
POST /api/v1/chronograph/measurements/bulk
```

**Request Body:**
```json
{
  "measurements": [
    {
      "chrono_session_id": "uuid",
      "shot_number": 1,
      "speed_mps": 762.5,
      "datetime_local": "2025-01-15T14:30:15"
    },
    {
      "chrono_session_id": "uuid",
      "shot_number": 2,
      "speed_mps": 765.1,
      "datetime_local": "2025-01-15T14:30:45"
    }
  ]
}
```

**Response:** `201 Created` with array of ChronographMeasurement objects

### Sources

#### List Sources
```http
GET /api/v1/chronograph/sources
```

**Response:** Array of ChronographSource objects

#### Create Source
```http
POST /api/v1/chronograph/sources
```

**Request Body:**
```json
{
  "name": "My Garmin Xero C1",
  "source_type": "chronograph",
  "device_name": "Garmin Xero C1",
  "make": "Garmin",
  "model": "Xero C1",
  "serial_number": "123456789"
}
```

**Response:** `201 Created` with ChronographSource object

#### Get Source
```http
GET /api/v1/chronograph/sources/{source_id}
```

**Response:** ChronographSource object

#### Update Source
```http
PUT /api/v1/chronograph/sources/{source_id}
```

**Request Body:** Same as Create Source

**Response:** Updated ChronographSource object

#### Delete Source
```http
DELETE /api/v1/chronograph/sources/{source_id}
```

**Response:** `204 No Content`

### Utility Endpoints

#### Get Bullet Types
```http
GET /api/v1/chronograph/bullet-types
```

**Response:** Array of unique bullet type strings

## Validation Rules

### Velocity Validation
- Must be greater than 0 m/s
- Must be between 50-2000 m/s for chronograph range
- Cannot be negative

### Shot Number Validation
- Must be >= 1
- Must be unique within a session
- Sequential numbering recommended

### Date Validation
- Session dates cannot be before year 2000
- Session dates cannot be more than 1 day in the future
- Measurement dates should be within session timeframe

### String Validation
- Names limited to 100 characters
- Notes limited to 500 characters
- Input sanitization applied to prevent injection

## Error Handling

### Standard Error Response
```json
{
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": {
    "field": "speed_mps",
    "issue": "Value must be greater than 0"
  }
}
```

### HTTP Status Codes

- **200 OK** - Successful GET/PUT operations
- **201 Created** - Successful POST operations
- **204 No Content** - Successful DELETE operations
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Access denied to resource
- **404 Not Found** - Resource does not exist
- **409 Conflict** - Resource already exists or constraint violation
- **422 Unprocessable Entity** - Validation errors
- **500 Internal Server Error** - Server errors

### Common Error Types

- **ValidationError** - Input validation failures
- **AuthorizationException** - Access control violations
- **ResourceNotFoundException** - Missing resources
- **ConflictException** - Duplicate resources or constraints
- **DatabaseException** - Database operation failures

## Rate Limiting

Rate limiting is applied per user:
- **100 requests per minute** for read operations
- **50 requests per minute** for write operations
- **10 requests per minute** for bulk operations

## Performance Considerations

### Pagination
- Use appropriate page sizes (default: 20, max: 100)
- Large datasets should use pagination
- Total count provided for UI pagination controls

### Bulk Operations
- Bulk measurement creation supports up to 1000 measurements
- Use bulk endpoints for importing large datasets
- Statistics automatically recalculated after bulk operations

### Caching
- Session statistics cached for 5 minutes
- Source lists cached for 10 minutes
- Use ETags for conditional requests where supported

## Security

### Data Isolation
- All operations scoped to authenticated user
- Cross-user access prevented at API level
- User ID validation on all resource access

### Input Sanitization
- All string inputs sanitized
- SQL injection prevention
- XSS protection on text fields

### Audit Logging
- All API operations logged with user context
- Performance metrics tracked
- Error rates monitored

## SDKs and Integration

### JavaScript/TypeScript
```typescript
import { ChronographAPI } from '@chronolog/api-client';

const api = new ChronographAPI({
  baseURL: 'https://api.chronolog.com',
  bearerToken: 'your-jwt-token'
});

// List sessions
const sessions = await api.sessions.list({
  page: 1,
  size: 20,
  bullet_type: '308 Winchester'
});

// Create measurement
const measurement = await api.measurements.create({
  chrono_session_id: 'session-uuid',
  shot_number: 1,
  speed_mps: 762.5,
  datetime_local: new Date()
});
```

### Python
```python
from chronolog_api import ChronographAPI

api = ChronographAPI(
    base_url='https://api.chronolog.com',
    bearer_token='your-jwt-token'
)

# List sessions
sessions = api.sessions.list(
    page=1,
    size=20,
    bullet_type='308 Winchester'
)

# Create measurement
measurement = api.measurements.create({
    'chrono_session_id': 'session-uuid',
    'shot_number': 1,
    'speed_mps': 762.5,
    'datetime_local': datetime.now()
})
```

## Changelog

### v1.0.0 (2025-01-15)
- Initial API release
- Session, measurement, and source management
- Bulk operations support
- Comprehensive validation and error handling
- Statistical analysis endpoints

## Support

For API support and questions:
- Documentation: [https://docs.chronolog.com/api](https://docs.chronolog.com/api)
- Issues: [https://github.com/chronolog/api/issues](https://github.com/chronolog/api/issues)
- Email: api-support@chronolog.com