# Common Implementation Patterns

## Overview

This document describes the common patterns used across all ChronoLog modules. Following these patterns ensures consistency, maintainability, and type safety.

## Module Structure

Every data source module follows this standard structure:

```
module_name/
├── models.py               # Domain entities (dataclasses)
├── service.py              # Business logic and database operations
├── protocols.py            # API contracts (Python Protocol classes) - FUTURE
├── api.py                  # API facade - FUTURE
├── __init__.py             # Module exports - FUTURE
├── view_tab.py             # Streamlit UI (OPTIONAL, can be multiple)
├── create_tab.py           # Streamlit UI (OPTIONAL)
├── ui_formatters.py        # Display helpers (OPTIONAL)
├── business_logic.py       # Pure functions (OPTIONAL)
├── device_adapters.py      # Import adapters (OPTIONAL, e.g., Garmin, Kestrel)
└── test_module_name.py     # Unit tests
```

---

## Pattern 1: Model Classes (Dataclasses)

All domain entities use Python dataclasses with specific patterns.

### Basic Model Structure

```python
# module_name/models.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class EntityModel:
    """
    Domain entity for [description].

    All fields use metric units internally.
    """
    # Required fields
    id: str
    user_id: str  # For user-owned entities (omit for admin-owned)
    created_at: datetime

    # Domain-specific fields (all metric!)
    name: str
    value_metric: float  # e.g., velocity_mps, temp_c, distance_meters

    # Optional fields
    notes: Optional[str] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> 'EntityModel':
        """
        Construct model from Supabase database record.

        Args:
            record: Dictionary from Supabase query result

        Returns:
            EntityModel instance with typed fields
        """
        return cls(
            id=record['id'],
            user_id=record.get('user_id'),  # Optional for admin-owned
            created_at=record['created_at'],
            name=record['name'],
            value_metric=record['value_metric'],
            notes=record.get('notes'),
        )

    @classmethod
    def from_supabase_records(cls, records: list[dict]) -> list['EntityModel']:
        """Batch convert Supabase records to models."""
        return [cls.from_supabase_record(r) for r in records]

    def to_dict(self) -> dict:
        """
        Convert model to dictionary for database operations.

        Returns plain dict with metric values (no formatting).
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'name': self.name,
            'value_metric': self.value_metric,
            'notes': self.notes,
        }

    @property
    def display_name(self) -> str:
        """User-friendly display name."""
        return f"{self.name} ({self.id[:8]})"
```

### Key Patterns

1. **Use `@dataclass` decorator**: Automatic `__init__`, `__repr__`, `__eq__`
2. **Type everything**: Every field has a type hint
3. **Metric units**: All numeric fields are metric (velocity_mps, temp_c, etc.)
4. **from_supabase_record()**: Class method to construct from DB record
5. **from_supabase_records()**: Batch conversion helper
6. **to_dict()**: Convert to plain dict (for inserts/updates)
7. **display properties**: Computed fields for UI (but UI-agnostic!)

---

## Pattern 2: Service Layer

Service classes encapsulate business logic and database operations.

### Basic Service Structure

```python
# module_name/service.py
from typing import List, Optional
from .models import EntityModel

class EntityService:
    """
    Service for [entity] business logic and database operations.

    All methods are UI-agnostic and use metric units.
    """

    def __init__(self, supabase_client):
        """
        Initialize service with Supabase client.

        Args:
            supabase_client: Supabase client instance
        """
        self.supabase = supabase_client

    def get_entities_for_user(self, user_id: str) -> List[EntityModel]:
        """
        Get all entities for a user.

        Args:
            user_id: Auth0 user ID (NOT email)

        Returns:
            List of EntityModel instances (empty if none found)
        """
        if not user_id:
            raise ValueError("user_id is required")

        response = self.supabase.from_('entities') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True) \
            .execute()

        return EntityModel.from_supabase_records(response.data)

    def get_entity_by_id(self, entity_id: str, user_id: str) -> Optional[EntityModel]:
        """
        Get a specific entity by ID.

        Args:
            entity_id: Entity UUID
            user_id: Auth0 user ID (for security check)

        Returns:
            EntityModel if found and owned by user, None otherwise
        """
        if not user_id:
            raise ValueError("user_id is required")

        response = self.supabase.from_('entities') \
            .select('*') \
            .eq('id', entity_id) \
            .eq('user_id', user_id) \  # Security: user must own it
            .single() \
            .execute()

        if not response.data:
            return None

        return EntityModel.from_supabase_record(response.data)

    def create_entity(self, entity_data: dict, user_id: str) -> EntityModel:
        """
        Create a new entity.

        Args:
            entity_data: Dict with entity fields (must be metric!)
            user_id: Auth0 user ID (will be set on entity)

        Returns:
            Created EntityModel instance
        """
        if not user_id:
            raise ValueError("user_id is required")

        # Force user_id (can't be spoofed)
        entity_data['user_id'] = user_id

        response = self.supabase.from_('entities') \
            .insert(entity_data) \
            .execute()

        return EntityModel.from_supabase_record(response.data[0])

    def update_entity(
        self,
        entity_id: str,
        entity_data: dict,
        user_id: str
    ) -> Optional[EntityModel]:
        """
        Update an existing entity.

        Args:
            entity_id: Entity UUID to update
            entity_data: Dict with fields to update (metric values)
            user_id: Auth0 user ID (security check)

        Returns:
            Updated EntityModel if successful, None if not found/not owned
        """
        if not user_id:
            raise ValueError("user_id is required")

        # Remove user_id from updates (can't change owner)
        entity_data.pop('user_id', None)

        response = self.supabase.from_('entities') \
            .update(entity_data) \
            .eq('id', entity_id) \
            .eq('user_id', user_id) \  # Security: can only update own entities
            .execute()

        if not response.data:
            return None

        return EntityModel.from_supabase_record(response.data[0])

    def delete_entity(self, entity_id: str, user_id: str) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: Entity UUID to delete
            user_id: Auth0 user ID (security check)

        Returns:
            True if deleted, False if not found/not owned
        """
        if not user_id:
            raise ValueError("user_id is required")

        response = self.supabase.from_('entities') \
            .delete() \
            .eq('id', entity_id) \
            .eq('user_id', user_id) \  # Security: can only delete own entities
            .execute()

        return len(response.data) > 0
```

### Key Patterns

1. **Constructor takes Supabase client**: Dependency injection
2. **user_id always required**: Never optional, validated at start of method
3. **Filter by user_id**: Every query for user-owned data
4. **Force user_id on create**: Prevent spoofing
5. **Security on update/delete**: Can only modify own entities
6. **Return typed models**: Never return raw dicts
7. **No Streamlit imports**: Services are UI-agnostic

---

## Pattern 3: Admin-Owned Services (Bullets, Cartridges)

Admin-owned entities follow a slightly different pattern (no user_id filtering).

```python
# bullets/service.py
class BulletsService:
    """Service for bullets catalog (admin-owned, read-only to users)."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_all_bullets(self) -> List[BulletModel]:
        """
        Get all bullets (global catalog).

        No user_id filter - bullets are shared across all users.
        """
        response = self.supabase.from_('bullets') \
            .select('*') \
            .order('manufacturer', 'model') \
            .execute()

        return BulletModel.from_supabase_records(response.data)

    def get_bullet_by_id(self, bullet_id: str) -> Optional[BulletModel]:
        """Get a specific bullet (no user_id needed - global catalog)."""
        response = self.supabase.from_('bullets') \
            .select('*') \
            .eq('id', bullet_id) \
            .single() \
            .execute()

        if not response.data:
            return None

        return BulletModel.from_supabase_record(response.data)

    # create_bullet, update_bullet, delete_bullet would be admin-only
    # Not exposed in regular API (only in admin panel)
```

**Key difference**: No `user_id` parameter, no user filtering.

---

## Pattern 4: Device Adapters (Import)

Device adapters handle file imports and convert to metric.

```python
# module_name/device_adapters.py
from typing import List
import pandas as pd
from .models import EntityModel

class DeviceAdapter:
    """Adapter for [DeviceName] device files."""

    @staticmethod
    def parse_device_file(file_path: str) -> List[EntityModel]:
        """
        Parse device file and convert to metric models.

        Args:
            file_path: Path to device export file

        Returns:
            List of EntityModel instances (metric units)

        Raises:
            ValueError: If file format is invalid
        """
        try:
            df = pd.read_csv(file_path)  # or read_excel, etc.
        except Exception as e:
            raise ValueError(f"Invalid file format: {e}")

        # Validate required columns
        required_cols = ['timestamp', 'value_imperial']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Missing required columns: {required_cols}")

        entities = []
        for _, row in df.iterrows():
            # Convert imperial to metric HERE
            value_imperial = row['value_imperial']
            value_metric = value_imperial * CONVERSION_FACTOR

            entities.append(EntityModel(
                id=generate_id(),  # or from file if available
                user_id=None,  # Set later by service
                created_at=row['timestamp'],
                value_metric=value_metric,  # METRIC!
            ))

        return entities
```

**Key patterns**:
1. **Static methods**: Adapters are often stateless
2. **Validate file format**: Check for required columns
3. **Convert to metric**: All conversions happen in adapter
4. **Return typed models**: Never return raw dicts
5. **Error handling**: Clear error messages for invalid files

---

## Pattern 5: UI Formatters (Display)

UI formatters convert metric to imperial for display.

```python
# module_name/ui_formatters.py
from .models import EntityModel

def format_value_for_display(value_metric: float, user_prefs: dict) -> str:
    """
    Format metric value for display based on user preference.

    Args:
        value_metric: Value in metric units
        user_prefs: User preferences dict with 'units' key

    Returns:
        Formatted string with units
    """
    if user_prefs.get('units') == 'imperial':
        value_imperial = value_metric / CONVERSION_FACTOR
        return f"{value_imperial:.2f} imperial_unit"
    else:
        return f"{value_metric:.2f} metric_unit"

def format_entity_for_dataframe(entity: EntityModel, user_prefs: dict) -> dict:
    """
    Format entity for Streamlit dataframe display.

    Args:
        entity: EntityModel instance
        user_prefs: User preferences

    Returns:
        Dict with formatted values for display
    """
    return {
        'Name': entity.name,
        'Value': format_value_for_display(entity.value_metric, user_prefs),
        'Created': entity.created_at.strftime('%Y-%m-%d %H:%M'),
    }
```

**Key patterns**:
1. **Takes user_prefs**: Unit preference from user settings
2. **Returns formatted strings**: With units included
3. **UI-specific**: Can import streamlit if needed
4. **Separate from models**: Models stay UI-agnostic

---

## Pattern 6: User Isolation (Security)

Every service method for user-owned data must enforce user isolation.

### CORRECT: Always Filter by user_id

```python
def get_entities_for_user(self, user_id: str) -> List[EntityModel]:
    """CORRECT: Filters by user_id."""
    if not user_id:
        raise ValueError("user_id is required")

    return self.supabase.from_('entities') \
        .select('*') \
        .eq('user_id', user_id) \  # ← REQUIRED!
        .execute()
```

### WRONG: Missing user_id Filter

```python
def get_all_entities(self) -> List[EntityModel]:
    """WRONG: Returns all users' entities!"""
    # Missing user_id filter - security vulnerability!
    return self.supabase.from_('entities').select('*').execute()
```

### CORRECT: Force user_id on Create

```python
def create_entity(self, data: dict, user_id: str) -> EntityModel:
    """CORRECT: Forces user_id from auth token."""
    if not user_id:
        raise ValueError("user_id is required")

    # Force user_id (ignore client input)
    data['user_id'] = user_id  # ← REQUIRED!

    return self.supabase.from_('entities').insert(data).execute()
```

---

## Pattern 7: Error Handling

Consistent error handling across services.

```python
def get_entity_by_id(self, entity_id: str, user_id: str) -> Optional[EntityModel]:
    """
    Get entity with proper error handling.

    Returns None if not found (not owned by user) rather than raising.
    Raises ValueError for invalid inputs.
    """
    # Validate inputs
    if not entity_id:
        raise ValueError("entity_id is required")
    if not user_id:
        raise ValueError("user_id is required")

    try:
        response = self.supabase.from_('entities') \
            .select('*') \
            .eq('id', entity_id) \
            .eq('user_id', user_id) \
            .single() \
            .execute()

        if not response.data:
            return None  # Not found or not owned

        return EntityModel.from_supabase_record(response.data)

    except Exception as e:
        # Log the error (future: proper logging)
        print(f"Error fetching entity {entity_id}: {e}")
        return None  # Fail gracefully
```

**Patterns**:
1. **Validate inputs**: Raise ValueError for invalid params
2. **Return None for not found**: Don't raise exceptions
3. **Try/except for DB errors**: Fail gracefully
4. **Log errors**: For debugging (future: structured logging)

---

## Pattern 8: Testing

Unit tests follow consistent patterns.

```python
# module_name/test_module_name.py
import pytest
from unittest.mock import Mock, MagicMock
from .service import EntityService
from .models import EntityModel

@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    return Mock()

@pytest.fixture
def entity_service(mock_supabase):
    """Entity service with mocked Supabase."""
    return EntityService(mock_supabase)

def test_get_entities_filters_by_user(entity_service, mock_supabase):
    """Verify get_entities_for_user filters by user_id."""
    # Setup mock
    mock_supabase.from_().select().eq().order().execute.return_value = \
        MagicMock(data=[{'id': '1', 'user_id': 'user123', 'name': 'Test'}])

    # Call service
    entities = entity_service.get_entities_for_user('user123')

    # Verify user_id filter was applied
    mock_supabase.from_().select().eq.assert_called_with('user_id', 'user123')

    # Verify returned typed models
    assert len(entities) == 1
    assert isinstance(entities[0], EntityModel)

def test_create_entity_forces_user_id(entity_service, mock_supabase):
    """Verify create_entity forces user_id from auth token."""
    # Setup mock
    mock_supabase.from_().insert().execute.return_value = \
        MagicMock(data=[{'id': '1', 'user_id': 'user123', 'name': 'Test'}])

    # Call service with data that might have spoofed user_id
    entity_data = {'name': 'Test', 'user_id': 'attacker'}
    entity = entity_service.create_entity(entity_data, user_id='user123')

    # Verify user_id was forced to authenticated user
    called_data = mock_supabase.from_().insert.call_args[0][0]
    assert called_data['user_id'] == 'user123'  # Not 'attacker'!
```

**Patterns**:
1. **pytest fixtures**: For reusable mocks
2. **Mock Supabase**: Test without database
3. **Verify filters**: Ensure user_id filtering
4. **Verify security**: Force user_id, can't spoof
5. **Test return types**: Ensure typed models returned

---

## Summary

**Every Module Should**:
- Use dataclasses for models
- Implement from_supabase_record() and to_dict()
- Store metric units internally
- Filter by user_id for user-owned data
- Force user_id on create operations
- Never import streamlit in backend code
- Return typed models (not dicts)
- Include unit tests

**Next Steps**:
- [Design Decisions](../architecture/06-design-decisions.md) - Why we chose these patterns
- [User Isolation](../architecture/04-user-isolation.md) - Security details
- [Metric System](../architecture/05-metric-system.md) - Unit handling