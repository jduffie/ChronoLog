# DOPE Module: Three-Layer Architecture

## Overview

The DOPE module follows ChronoLog's standard three-layer architecture pattern, with a fourth UI layer for Streamlit pages. This document explains the responsibilities, dependencies, and data flow between layers.

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: UI (Streamlit Pages)                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ view/view_page.py                                    │   │
│  │ create/create_page.py                                │   │
│  └──────────────────┬──────────────────────────────────┘   │
│                     │ imports API + Business               │
│                     │ NEVER imports Service                │
└─────────────────────┼──────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Business (Workflow Orchestration)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ create/business.py (DopeCreateBusiness)              │   │
│  │ view/business.py (future)                            │   │
│  └──────┬──────────────────────────────┬─────────────┘   │
│         │ OWN MODULE                   │ CROSS-MODULE     │
│         │ (direct to Service)          │ (via API)        │
└─────────┼──────────────────────────────┼──────────────────┘
          ▼                              ▼
┌──────────────────────┐    ┌────────────────────────────────┐
│  Layer 2: API        │    │  Other Module APIs             │
│  (PUBLIC FACADE)     │    │  - ChronographAPI              │
│  ┌────────────────┐  │    │  - CartridgesAPI               │
│  │ api.py         │  │    │  - RiflesAPI                   │
│  │ protocols.py   │  │    │  - WeatherAPI                  │
│  └───────┬────────┘  │    └────────────────────────────────┘
│          │ wraps     │
│          │ (thin)    │    ⚠️  Business NEVER calls own API
└──────────┼───────────┘    ⚠️  That creates circular dependency!
           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Service (Database Operations)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ service.py (DopeService)                             │   │
│  │ - Complex JOINs across 6 tables                      │   │
│  │ - Supabase queries                                   │   │
│  │ - Model transformations                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Critical Rule: Own Module vs. Cross-Module

### ✅ CORRECT: Business Layer Calls

```
DopeCreateBusiness
│
├─> DopeService.get_sessions_for_user()        ✅ OWN MODULE
├─> DopeService.create_session()               ✅ OWN MODULE
│
├─> ChronographAPI.get_all_sessions()          ✅ CROSS-MODULE
├─> CartridgesAPI.get_all_cartridges()         ✅ CROSS-MODULE
├─> RiflesAPI.get_all_rifles()                 ✅ CROSS-MODULE
└─> WeatherAPI.get_all_sources()               ✅ CROSS-MODULE
```

### ❌ WRONG: Circular Dependency

```
DopeCreateBusiness
│
└─> DopeAPI.get_sessions_for_user()            ❌ CIRCULAR!
      └─> DopeService.get_sessions_for_user()
            (Business → API → Service when Business could call Service directly)
```

**Why this is wrong:**
- Creates unnecessary indirection (Business → API → Service)
- Business and API both wrap Service (redundant)
- Breaks separation of concerns
- Makes dependency graph circular

## Layer 1: Service Layer

**File**: `dope/service.py`
**Class**: `DopeService`

### Responsibilities

1. **Database operations**: All Supabase queries happen here
2. **Complex JOINs**: Constructs denormalized sessions from 6 tables
3. **Data transformation**: Converts Supabase records to/from models
4. **Mock data**: Provides fallback mock data for development
5. **No cross-module dependencies**: Only imports models, not other module APIs

### Key Methods

```python
class DopeService:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]:
        """Complex 6-table JOIN to get denormalized sessions"""
        response = (
            self.supabase.table("dope_sessions")
            .select("""
                *,
                cartridges!cartridge_id (
                    make, model, cartridge_type,
                    bullets!bullet_id (...)
                ),
                rifles!rifle_id (...),
                ranges_submissions!range_submission_id (...),
                weather_source!weather_source_id (...),
                chrono_sessions!chrono_session_id (...)
            """)
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        sessions = []
        for record in response.data:
            session_data = self._flatten_joined_record(record)
            sessions.append(DopeSessionModel.from_supabase_record(session_data))
        return sessions
```

### Design Principles

- **Single responsibility**: Database access only
- **No business logic**: Filtering, validation, orchestration belong in Business layer
- **No cross-module calls**: Doesn't import ChronographAPI, CartridgesAPI, etc.
- **Type safety**: Returns strongly-typed models

## Layer 2: API Layer

**Files**: `dope/api.py`, `dope/protocols.py`
**Class**: `DopeAPI`
**Protocol**: `DopeAPIProtocol`

### Responsibilities

1. **Public facade**: External interface for UI and other modules
2. **Service wrapper**: Delegates to Service layer
3. **Type contract**: Implements `DopeAPIProtocol`
4. **Documentation**: Comprehensive docstrings for each method
5. **UI-agnostic**: No Streamlit dependencies

### Key Characteristics

```python
class DopeAPI:
    """
    Public API for the DOPE module.

    This facade provides a clean, type-safe interface for managing DOPE sessions.
    All methods are UI-agnostic and return strongly-typed model instances.
    """

    def __init__(self, supabase_client):
        # API wraps Service - thin delegation layer
        self._service = DopeService(supabase_client)

    def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]:
        """Get all DOPE sessions for a user with joined data."""
        # Direct delegation - API is a thin wrapper
        return self._service.get_sessions_for_user(user_id)

    def create_session(self, session_data: Dict[str, Any], user_id: str) -> DopeSessionModel:
        """Create a new DOPE session."""
        return self._service.create_session(session_data, user_id)
```

### Design Principles

- **Thin wrapper**: Delegates to Service without adding logic
- **Protocol compliance**: Implements `DopeAPIProtocol` for type checking
- **Stable interface**: API contract doesn't change when Service internals change
- **External consumers**: Used by UI, other modules, CLI tools, etc.

## Layer 3: Business Layer

**File**: `dope/create/business.py`
**Class**: `DopeCreateBusiness`

### Responsibilities

1. **Workflow orchestration**: Coordinates multiple steps in a workflow
2. **Cross-module integration**: Calls APIs from other modules
3. **Business logic**: Filtering, validation, data preparation
4. **Direct Service calls**: Calls own module's Service layer directly
5. **Workflow-specific**: Separate class per workflow (create, view, edit, etc.)

### Correct Pattern: Own Module vs. Cross-Module

```python
class DopeCreateBusiness:
    def __init__(self, supabase):
        # ✅ CORRECT: Call own module's Service directly (not DopeAPI!)
        self.dope_service = DopeService(supabase)

        # ✅ CORRECT: Call other modules' APIs
        self.chrono_api = ChronographAPI(supabase)
        self.cartridge_api = CartridgesAPI(supabase)
        self.rifle_api = RiflesAPI(supabase)
        self.weather_api = WeatherAPI(supabase)
        self.submission_model = SubmissionModel()  # Range data
        self.weather_associator = WeatherSessionAssociator(supabase)

    def get_unused_chrono_sessions(self, user_id: str) -> List[ChronographSession]:
        """Business logic: find chronograph sessions not yet in DOPE"""
        # ✅ Cross-module: use API
        all_chrono_sessions = self.chrono_api.get_all_sessions(user_id)

        # ✅ Own module: use Service (NOT self.dope_api!)
        all_dope_sessions = self.dope_service.get_sessions_for_user(user_id)

        # Business logic: filter out used sessions
        used_chrono_ids = {
            session.chrono_session_id
            for session in all_dope_sessions
            if session.chrono_session_id
        }

        return [
            session
            for session in all_chrono_sessions
            if session.id not in used_chrono_ids
        ]
```

### Anti-Pattern: Circular Dependency (FIXED)

**This was the bug in the original code - now fixed:**

```python
# ❌ WRONG: Business layer calling own module's API
class DopeCreateBusiness:
    def __init__(self, supabase):
        self.dope_api = DopeAPI(supabase)  # ❌ Circular dependency!

    def get_unused_chrono_sessions(self, user_id: str):
        # This creates: Business → API → Service
        # But Business should call Service directly!
        all_dope_sessions = self.dope_api.get_sessions_for_user(user_id)  # ❌ WRONG
```

**Why this is wrong**:
- Creates circular dependency: Business → API → Service (Business could call Service directly)
- Business and API both wrap Service - redundant layers
- Breaks separation of concerns
- Makes testing harder

**The fix** (already applied to `dope/create/business.py`):
```python
# ✅ CORRECT: Business layer calling own module's Service
class DopeCreateBusiness:
    def __init__(self, supabase):
        self.dope_service = DopeService(supabase)  # ✅ Direct to Service

    def get_unused_chrono_sessions(self, user_id: str):
        # Own module: call Service directly
        all_dope_sessions = self.dope_service.get_sessions_for_user(user_id)  # ✅ CORRECT
```

### Cross-Module Orchestration Example

```python
def prepare_session_data(
    self,
    chrono_session,    # From ChronographAPI
    rifle,             # From RiflesAPI
    cartridge,         # From CartridgesAPI
    range_data,        # From SubmissionModel
    weather_data,      # From WeatherAPI
    session_details,   # From UI
    time_window,       # From WeatherSessionAssociator
) -> DopeSessionModel:
    """
    Business logic: Prepare session data for creation.

    This orchestrates data from 5+ modules into a single DOPE session.
    """
    # Validation logic
    if not chrono_session or not chrono_session.id:
        raise ValueError("Chronograph session is required")

    # Data extraction and transformation
    rifle_id = rifle.id if hasattr(rifle, "id") else rifle.get("id")
    cartridge_id = cartridge.id if hasattr(cartridge, "id") else cartridge.get("id")

    # Prepare denormalized session data
    return {
        "session_name": session_details.get("session_name") or f"Session {datetime.now():%Y-%m-%d %H:%M}",
        "chrono_session_id": chrono_session.id,
        "rifle_id": rifle_id,
        "cartridge_id": cartridge_id,
        "range_submission_id": range_data["id"] if range_data else None,
        "weather_source_id": weather_data.id if weather_data else None,
        "start_time": time_window[0].isoformat(),
        "end_time": time_window[1].isoformat(),
        "notes": session_details.get("notes"),
    }
```

### Design Principles

- **Orchestration layer**: Coordinates multiple services and APIs
- **Own module → Service**: Direct call avoids circular dependency
- **Cross-module → API**: Uses public interface of other modules
- **Workflow-specific**: `DopeCreateBusiness`, `DopeViewBusiness`, etc.
- **Stateless**: Doesn't maintain state between method calls

## Layer 4: UI Layer

**Files**: `dope/view/view_page.py`, `dope/create/create_page.py`
**Framework**: Streamlit

### Responsibilities

1. **User interface**: Streamlit widgets, layout, session state
2. **Display formatting**: Unit conversions, number formatting
3. **User input handling**: Form validation, button clicks
4. **Minimal logic**: Delegates to Business or API layer

### Key Pattern

```python
from dope.api import DopeAPI
from dope.create.business import DopeCreateBusiness

def render_create_page(user):
    """Streamlit page for creating DOPE sessions"""
    # Initialize dependencies
    api = DopeAPI(st.session_state.supabase)
    business = DopeCreateBusiness(st.session_state.supabase)

    # Get dropdown options from business layer
    unused_sessions = business.get_unused_chrono_sessions(user["id"])
    rifles = business.get_rifles_for_user(user["id"])
    cartridges = business.get_cartridges_for_user(user["id"])

    # Streamlit UI
    st.selectbox("Chronograph Session", options=unused_sessions)
    st.selectbox("Rifle", options=rifles)
    st.selectbox("Cartridge", options=cartridges)

    if st.button("Create Session"):
        # Prepare data
        session_data = {...}

        # Delegate to business layer
        new_session = business.create_dope_session(session_data, user["id"])

        st.success(f"Created session: {new_session.display_name}")
```

### Design Principles

- **UI-specific code only**: Streamlit, widgets, layout
- **Uses API + Business**: Never imports Service directly
- **Thin layer**: Minimal logic - delegates to Business/API
- **Display edge**: Unit conversions happen here (metric → imperial)

## Data Flow Examples

### Example 1: Creating a DOPE Session

```
User (UI Layer)
  └─> render_create_page()
        └─> DopeCreateBusiness.create_dope_session()
              ├─> ChronographAPI.get_session()          [cross-module → API]
              ├─> CartridgesAPI.get_cartridge()         [cross-module → API]
              ├─> RiflesAPI.get_rifle()                 [cross-module → API]
              ├─> WeatherAPI.get_source()               [cross-module → API]
              ├─> WeatherSessionAssociator.associate()  [cross-module]
              └─> DopeService.create_session()          [own module → Service DIRECTLY]
                    ├─> Validate foreign keys
                    ├─> Get chronograph time window
                    ├─> Calculate velocity statistics
                    ├─> INSERT into dope_sessions
                    ├─> Copy chrono measurements to dope_measurements
                    └─> DopeService.get_session_by_id()
                          └─> Complex 6-table JOIN
                          └─> Return DopeSessionModel with denormalized data
```

### Example 2: Viewing DOPE Sessions

```
User (UI Layer)
  └─> render_view_page()
        └─> DopeAPI.get_sessions_for_user()
              └─> DopeService.get_sessions_for_user()
                    ├─> SELECT with 6-table JOIN
                    │   ├─> dope_sessions
                    │   ├─> cartridges (+ bullets nested)
                    │   ├─> rifles
                    │   ├─> chrono_sessions
                    │   ├─> weather_source
                    │   └─> ranges_submissions
                    ├─> _flatten_joined_record() for each row
                    └─> Return List[DopeSessionModel]
```

### Example 3: Filtering Sessions (Business Logic)

```
User (UI Layer)
  └─> render_view_page() with filters
        └─> DopeAPI.filter_sessions(user_id, filters)
              └─> DopeService.filter_sessions(user_id, filters)
                    ├─> _get_sessions_with_db_filters() [DB-level filtering]
                    │     └─> WHERE clauses for cartridge_type, date range, etc.
                    └─> DopeSessionFilter.apply_all_filters() [in-memory filtering]
                          ├─> Filter by bullet make/model
                          ├─> Filter by temperature range
                          ├─> Filter by wind conditions
                          └─> Return filtered List[DopeSessionModel]
```

## Why This Pattern?

### 1. Separation of Concerns

Each layer has a **single, clear responsibility**:
- **Service**: Database access
- **API**: Public interface
- **Business**: Workflow orchestration
- **UI**: User interaction

### 2. Testability

Each layer can be tested independently:
```python
# Test Service with mock Supabase
service = DopeService(mock_supabase)

# Test API with mock Service
api = DopeAPI(mock_supabase)

# Test Business with mock APIs and mock Service
business = DopeCreateBusiness(mock_supabase)
business.chrono_api = mock_chrono_api
business.dope_service = mock_dope_service  # Mock own Service

# Test UI with mock Business
def test_render_create_page():
    with patch('dope.create.business.DopeCreateBusiness') as mock_business:
        render_create_page(user)
        mock_business.create_dope_session.assert_called_once()
```

### 3. Flexibility

UI can change (Streamlit → React → CLI) without affecting Service/API:
```
Streamlit UI  ─┐
React UI      ─┼─> DopeAPI ─> DopeService
CLI Tool      ─┘
```

### 4. Type Safety

Protocol definitions ensure API contract compliance:
```python
# Protocol defines contract
class DopeAPIProtocol(Protocol):
    def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]: ...

# Implementation must match
class DopeAPI:
    def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]:
        return self._service.get_sessions_for_user(user_id)

# Type checker validates at compile time
api: DopeAPIProtocol = DopeAPI(supabase)  # ✅ Type-safe
```

### 5. Cross-Module Orchestration Without Tight Coupling

Business layer enables complex workflows:
```python
# DOPE Business layer orchestrates multiple modules
class DopeCreateBusiness:
    def create_dope_session(...):
        # Get data from 5+ modules via their APIs
        chrono = self.chrono_api.get_session(...)
        rifle = self.rifle_api.get_rifle(...)
        cartridge = self.cartridge_api.get_cartridge(...)
        weather = self.weather_api.get_source(...)
        range_data = self.submission_model.get_range(...)

        # Prepare combined data
        session_data = self.prepare_session_data(
            chrono, rifle, cartridge, weather, range_data
        )

        # Create in own database via Service (not API!)
        return self.dope_service.create_session(session_data, user_id)
```

## Common Pitfalls

### ❌ Pitfall 1: Business Calling Own Module's API (THE BUG WE FIXED)

```python
# WRONG - This was the original bug
class DopeCreateBusiness:
    def __init__(self, supabase):
        self.dope_api = DopeAPI(supabase)  # ❌ Circular dependency!

    def get_unused_chrono_sessions(self, user_id):
        all_dope = self.dope_api.get_sessions_for_user(user_id)  # ❌ WRONG
```

**Fix**: Call Service directly (already applied)
```python
# CORRECT - The fix
class DopeCreateBusiness:
    def __init__(self, supabase):
        self.dope_service = DopeService(supabase)  # ✅ Direct to Service

    def get_unused_chrono_sessions(self, user_id):
        all_dope = self.dope_service.get_sessions_for_user(user_id)  # ✅ CORRECT
```

### ❌ Pitfall 2: UI Calling Service Directly

```python
# WRONG
from dope.service import DopeService

def render_view_page(user):
    service = DopeService(st.session_state.supabase)  # ❌
    sessions = service.get_sessions_for_user(user["id"])
```

**Fix**: Use API layer
```python
# CORRECT
from dope.api import DopeAPI

def render_view_page(user):
    api = DopeAPI(st.session_state.supabase)  # ✅
    sessions = api.get_sessions_for_user(user["id"])
```

### ❌ Pitfall 3: Service Calling Cross-Module APIs

```python
# WRONG
from chronograph.api import ChronographAPI

class DopeService:
    def __init__(self, supabase):
        self.supabase = supabase
        self.chrono_api = ChronographAPI(supabase)  # ❌ Service shouldn't call APIs
```

**Fix**: Move cross-module logic to Business layer
```python
# CORRECT
class DopeService:
    def __init__(self, supabase):
        self.supabase = supabase  # Only database access

class DopeCreateBusiness:
    def __init__(self, supabase):
        self.dope_service = DopeService(supabase)
        self.chrono_api = ChronographAPI(supabase)  # ✅ Business orchestrates
```

### ❌ Pitfall 4: Business Logic in API Layer

```python
# WRONG
class DopeAPI:
    def get_unused_chrono_sessions(self, user_id):
        all_chrono = ChronographAPI(self.supabase).get_all_sessions(user_id)  # ❌
        all_dope = self._service.get_sessions_for_user(user_id)

        # Business logic doesn't belong in API layer!
        used_ids = {s.chrono_session_id for s in all_dope if s.chrono_session_id}
        return [s for s in all_chrono if s.id not in used_ids]
```

**Fix**: Move to Business layer
```python
# CORRECT
class DopeAPI:
    # API layer just delegates to Service
    def get_sessions_for_user(self, user_id):
        return self._service.get_sessions_for_user(user_id)

class DopeCreateBusiness:
    # Business logic lives here
    def get_unused_chrono_sessions(self, user_id):
        all_chrono = self.chrono_api.get_all_sessions(user_id)
        all_dope = self.dope_service.get_sessions_for_user(user_id)  # Service, not API!
        used_ids = {s.chrono_session_id for s in all_dope if s.chrono_session_id}
        return [s for s in all_chrono if s.id not in used_ids]
```

## Summary

### Quick Reference

| Layer | Purpose | Calls | Called By | Files |
|-------|---------|-------|-----------|-------|
| **Service** | Database operations | Supabase only | API, Business (own module) | `service.py` |
| **API** | Public facade | Service (own module) | UI, Business (cross-module), Other modules | `api.py`, `protocols.py` |
| **Business** | Workflow orchestration | Service (own), API (cross-module) | UI | `create/business.py` |
| **UI** | User interface | API, Business | User | `view/view_page.py`, `create/create_page.py` |

### Key Rules

1. ✅ **Business → Service** (own module): Direct calls - avoids circular dependency
2. ✅ **Business → API** (cross-module): Use public interface
3. ✅ **UI → API + Business**: Public interfaces only
4. ❌ **Business → own API**: Creates circular dependency (THIS WAS THE BUG)
5. ❌ **UI → Service**: Breaks encapsulation
6. ❌ **Service → other APIs**: Tight coupling

### Benefits

- **Testable**: Each layer mocks its dependencies
- **Flexible**: Change UI framework without affecting Service
- **Type-safe**: Protocol definitions ensure contract compliance
- **Maintainable**: Clear separation of concerns
- **Scalable**: Easy to add new workflows (new Business class)
- **No circular dependencies**: Business calls Service directly for own module

---

**Related Documentation**:
- [DOPE Module Overview](README.md)
- [API Reference](api-reference.md)
- [Models](models.md)