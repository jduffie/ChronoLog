    # CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Testing Supabase Configuration

If using 1Password CLI:
```bash
# Retrieve Supabase service role key from 1Password
export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --fields "service role secret")

source venv/bin/activate
python verify_supabase.py
```

### Running the Application
```bash
# Run the main Streamlit app
streamlit run ChronoLog.py
```

### Testing Commands

**IMPORTANT**: All tests must pass before committing code.

#### Unit Tests (Always run before commit)
```bash
# Run all unit tests
source venv/bin/activate
python run_all_tests.py

# Run specific module unit tests
python -m pytest chronograph/test_chronograph.py -v
python -m pytest bullets/test_bullets.py -v
python -m pytest cartridges/test_cartridges.py -v
python -m pytest rifles/test_rifles.py -v
python -m pytest weather/test_weather.py -v
python -m pytest dope/test_dope_modules.py -v

# Run with coverage (excludes integration tests)
pytest -m "not integration" --cov=. --cov-report=html --cov-report=term-missing
```

#### Integration Tests (Two modes: Mock and Real)

Integration tests implement a **hybrid mock/real pattern**:
- **Mock Mode** (CI/default): Tests skip actual database operations, use mocked Supabase client
- **Real Mode** (local with credentials): Full end-to-end testing with real Supabase database

```bash
# Mock Mode - Tests will skip with message "Skipping integration test in mock mode"
python run_integration_tests.py

# Real Mode - Requires SUPABASE_SERVICE_ROLE_KEY environment variable
export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --fields "service role secret")
python run_integration_tests.py

# Run specific integration test files (real mode)
pytest chronograph/test_garmin_import_integration.py -v
pytest chronograph/test_chronograph_integration.py -v
pytest bullets/test_bullets_integration.py -v

# Run all integration tests with marker
pytest -m integration -v
```

**Note**: GitHub Actions uses `pytest -m "not integration"` to completely exclude integration tests from CI runs.

### Code Quality Commands

```bash
# Format imports (required before commit)
isort .

# Format code with Black
black .

# Run linting
flake8 . --exclude venv

# Type checking
mypy . --ignore-missing-imports --exclude venv/

# Security scanning
bandit -r . --exclude venv/
```

### Pre-Commit Checklist

Before committing:
1. Run `isort .` to sort imports
2. Run `python run_all_tests.py` - all tests must pass
3. Check for unused imports
4. Verify test coverage is above 70%
5. Test the specific features you modified

## Architecture Overview

### Application Structure

ChronoLog is a multi-user ballistics data management application with the following core modules:

- **chronograph**: Velocity measurement data from devices (Garmin Xero)
- **bullets**: Projectile specifications (manufacturer, model, weight, BC)
- **cartridges**: Ammunition specifications linking bullets with cartridge types
- **rifles**: Firearm configurations (make, model, caliber, barrel specs)
- **weather**: Environmental conditions (temperature, humidity, pressure, wind)
- **dope**: Data On Previous Engagement - convergence point aggregating all source modules
- **mapping**: Range locations and shooting positions
- **users**: User profiles and preferences

### Authentication

- Auth0 for Google OAuth authentication
- User session in Streamlit session state
- All database operations filtered by `user["id"]` for data isolation

### Data Storage

- **Supabase PostgreSQL**: All structured data (sessions, measurements, specifications)
- **Supabase Storage**: Original uploaded files (Excel, CSV, JSON) organized by user email
- **Local migrations**: Database schema managed in `supabase/migrations/`


## Key Development Patterns

### Three-Layer Architecture

Each module follows a consistent three-layer pattern:

1. **Service Layer** (`service.py`): Database operations
   ```python
   from bullets.service import BulletsService
   service = BulletsService(supabase_client)
   bullets = service.get_all_bullets()
   ```

2. **API Layer** (`api.py`): Public interface for cross-module access
   ```python
   from bullets.api import BulletsAPI
   api = BulletsAPI(supabase_client)
   bullets = api.get_all_bullets()  # Returns List[BulletModel]
   ```

3. **UI Layer** (`*_tab.py`, `*_page.py`): Streamlit-specific code
   - Keep UI code isolated for potential framework migration
   - UI imports from API layer, never from service layer directly

### Model Classes

All entities use dataclasses with Supabase conversion:

```python
from dataclasses import dataclass

@dataclass
class BulletModel:
    id: str
    manufacturer: str
    model: str
    weight_grains: float
    
    @classmethod
    def from_supabase_record(cls, record: dict):
        return cls(
            id=record["id"],
            manufacturer=record["manufacturer"],
            ...
        )
```

### Protocol Definitions

Each module defines protocols in `protocols.py` for type safety:

```python
from typing import Protocol, List

class BulletsAPIProtocol(Protocol):
    def get_all_bullets(self) -> List[BulletModel]: ...
    def filter_bullets(self, **filters) -> List[BulletModel]: ...
```

### Cross-Module APIs

Modules export clean APIs for cross-module access:
- `chronograph/api.py` - ChronographAPI
- `bullets/api.py` - BulletsAPI  
- `cartridges/api.py` - CartridgesAPI
- `rifles/api.py` - RiflesAPI
- `weather/api.py` - WeatherAPI
- `dope/api.py` - DopeAPI (aggregates all source modules)

### User Data Isolation

**CRITICAL**: All database queries must filter by `user["id"]`:

```python
# Correct
results = service.get_sessions_for_user(user["id"])

# Wrong - exposes all users' data
results = supabase.table("sessions").select("*").execute()
```

### Unit System

- **Internal storage**: Metric only (meters, kilograms, Celsius)
- **UI display**: Convert based on user preferences
- **File imports**: Convert from imperial at import time
- **Models**: Always metric, never imperial
- **Column headers**: Include units (e.g., "Velocity (m/s)"), not in cell values

### Testing Structure

```
module/
  ├── test_<module>.py              # Unit tests (mocked dependencies)
  ├── test_<module>_integration.py  # Integration tests (hybrid mock/real)
  ├── test_<module>_api.py         # API layer tests
  └── test_<module>_ui_integration.py  # UI integration tests
```

Test markers in `pytest.ini`:
- `@pytest.mark.unit` - Unit tests with mocks
- `@pytest.mark.integration` - Integration tests (hybrid mock/real pattern)
- `@pytest.mark.structural` - Structural validation tests
- `@pytest.mark.database` - Database integration tests

### Integration Test Design Pattern

All `*_integration.py` files implement a **hybrid mock/real pattern** that allows tests to run in two modes:

**Pattern Implementation:**
```python
import os
from unittest.mock import Mock
from supabase import create_client

class BaseModuleIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        cls.supabase_url = os.getenv("SUPABASE_URL", "https://qnzioartedlrithdxszx.supabase.co")
        cls.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")
        cls.test_user_id = "google-oauth2|111273793361054745867"

        # Create Supabase client (or mock for CI)
        if cls.supabase_key == "test-key":
            # Mock client for CI/testing without credentials
            cls.supabase = Mock()
            cls.mock_mode = True
        else:
            # Real client for local integration testing
            cls.supabase = create_client(cls.supabase_url, cls.supabase_key)
            cls.mock_mode = False

    def test_something(self):
        """Test that requires real database"""
        if self.mock_mode:
            self.skipTest("Skipping integration test in mock mode")

        # Test with real database...
        # Perform cleanup in tearDown()
```

**Why This Pattern:**
1. **CI Compatibility**: Tests don't fail in CI - they skip gracefully when credentials unavailable
2. **Local Validation**: Developers can run full end-to-end tests with real Supabase
3. **Consistent Structure**: All integration tests follow the same pattern across modules
4. **Safe Testing**: Mock mode prevents accidental database operations during development

**Examples:**
- `chronograph/test_chronograph_integration.py` - Chronograph session and measurement operations
- `chronograph/test_garmin_import_integration.py` - Garmin Excel file import validation
- `bullets/test_bullets_integration.py` - Bullet management operations



## Database Migrations

Migrations are stored in `supabase/migrations/` and managed via Supabase CLI:

```bash
# Create new migration
supabase migration new <migration_name>

# Apply migrations locally
supabase db reset

# Push to remote
supabase db push
```

## Module Import Pattern

All modules add root directory to path for imports:

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):
- Tests on Python 3.9, 3.10, 3.11
- Runs structural tests (`test_all_pages.py`)
- Runs modular tests (`run_all_tests.py`)
- Generates coverage reports (must be >70%)
- Runs linting (flake8, isort)
- Runs security scanning (bandit)

## Important Development Rules

- Always use `user["id"]` for authorization, never `user["email"]`
- Run `isort .` before every commit
- Check for unused imports before committing
- All interior processing uses metric system
- Column headers include units, not cell values
- Each Streamlit page has its own private session state
- Prefer IntelliJ MCP tools for file searching when available
- Never create documentation files unless explicitly requested

### Chronograph Module - Duplicate File Handling

The chronograph module implements two-tier duplicate detection:

1. **File Storage**: When re-uploading same filename, user must check confirmation box to proceed
   - Implementation: `chronograph/garmin_ui.py` lines 27-54
2. **Session Level**: Sessions identified by `(user_id, tab_name, datetime_local)` - duplicates skipped
   - Implementation: `chronograph/garmin_import.py` lines 52-61
3. **Re-upload behavior**: Replaces file in storage, skips duplicate sessions, imports new/modified data only

See `docs/modules/chronograph/README.md` for detailed documentation and example scenarios.