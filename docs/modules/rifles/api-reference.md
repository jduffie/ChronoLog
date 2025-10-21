# Rifles API Reference

Complete API documentation for the Rifles module.

## Table of Contents

- [RiflesAPI Class](#riflesapi-class)
- [Read Operations](#read-operations)
- [Metadata Operations](#metadata-operations)
- [Write Operations](#write-operations)
- [Type Protocol](#type-protocol)
- [Error Handling](#error-handling)

## RiflesAPI Class

```python
from rifles import RiflesAPI

api = RiflesAPI(supabase_client)
```

### Constructor

```python
def __init__(self, supabase_client) -> None
```

Initialize the Rifles API.

**Parameters:**
- `supabase_client`: Authenticated Supabase client instance

**Example:**
```python
from supabase import create_client

supabase = create_client(url, key)
api = RiflesAPI(supabase)
```

## Read Operations

### get_all_rifles

```python
def get_all_rifles(self, user_id: str) -> List[RifleModel]
```

Get all rifles for a user, ordered by creation date descending.

**Parameters:**
- `user_id` (str): The user's ID

**Returns:**
- `List[RifleModel]`: List of rifles owned by user
- Empty list if user has no rifles

**Raises:**
- `Exception`: If database operation fails

**Example:**
```python
rifles = api.get_all_rifles("user-123")
print(f"Found {len(rifles)} rifles")

for rifle in rifles:
    print(f"- {rifle.display_name()}")
```

**SQL Query:**
```sql
SELECT * FROM rifles
WHERE user_id = 'user-123'
ORDER BY created_at DESC
```

---

### get_rifle_by_id

```python
def get_rifle_by_id(
    self,
    rifle_id: str,
    user_id: str
) -> Optional[RifleModel]
```

Get a specific rifle by ID.

**Parameters:**
- `rifle_id` (str): The rifle's unique ID
- `user_id` (str): The user's ID (for access control)

**Returns:**
- `RifleModel`: Rifle if found and owned by user
- `None`: If not found or not owned by user

**Raises:**
- `Exception`: If database operation fails

**Example:**
```python
rifle = api.get_rifle_by_id("rifle-123", "user-123")

if rifle:
    print(f"Found: {rifle.name}")
    print(f"  Caliber: {rifle.cartridge_type}")
    print(f"  Barrel: {rifle.barrel_display()}")
else:
    print("Rifle not found")
```

**SQL Query:**
```sql
SELECT * FROM rifles
WHERE id = 'rifle-123'
  AND user_id = 'user-123'
LIMIT 1
```

---

### get_rifle_by_name

```python
def get_rifle_by_name(
    self,
    user_id: str,
    name: str
) -> Optional[RifleModel]
```

Get a rifle by name.

**Note:** Returns first match if multiple rifles have the same name.

**Parameters:**
- `user_id` (str): The user's ID
- `name` (str): The rifle name to search for (exact match)

**Returns:**
- `RifleModel`: Rifle if found
- `None`: If not found

**Raises:**
- `Exception`: If database operation fails (not raised for "not found")

**Example:**
```python
# Exact name match
rifle = api.get_rifle_by_name("user-123", "Remington 700")

if rifle:
    print(f"Found rifle ID: {rifle.id}")
else:
    print("No rifle with that name")
```

**SQL Query:**
```sql
SELECT * FROM rifles
WHERE user_id = 'user-123'
  AND name = 'Remington 700'
LIMIT 1
```

---

### filter_rifles

```python
def filter_rifles(
    self,
    user_id: str,
    cartridge_type: Optional[str] = None,
    twist_ratio: Optional[str] = None
) -> List[RifleModel]
```

Get rifles filtered by criteria.

**Parameters:**
- `user_id` (str): The user's ID
- `cartridge_type` (str, optional): Filter by cartridge type
  - Use `"All"` or `None` to include all types
- `twist_ratio` (str, optional): Filter by barrel twist ratio
  - Use `"All"` or `None` to include all ratios

**Returns:**
- `List[RifleModel]`: Matching rifles, ordered by creation date descending
- Empty list if no matches

**Raises:**
- `Exception`: If database operation fails

**Examples:**
```python
# All rifles (no filter)
all_rifles = api.filter_rifles("user-123")

# Filter by cartridge type only
creedmoor = api.filter_rifles(
    "user-123",
    cartridge_type="6.5 Creedmoor"
)

# Filter by both cartridge type and twist ratio
specific = api.filter_rifles(
    "user-123",
    cartridge_type="6.5 Creedmoor",
    twist_ratio="1:8"
)

# Using "All" (same as None)
all_rifles = api.filter_rifles(
    "user-123",
    cartridge_type="All",
    twist_ratio="All"
)
```

**SQL Queries:**
```sql
-- No filters
SELECT * FROM rifles
WHERE user_id = 'user-123'
ORDER BY created_at DESC

-- With cartridge type filter
SELECT * FROM rifles
WHERE user_id = 'user-123'
  AND cartridge_type = '6.5 Creedmoor'
ORDER BY created_at DESC

-- With both filters
SELECT * FROM rifles
WHERE user_id = 'user-123'
  AND cartridge_type = '6.5 Creedmoor'
  AND barrel_twist_ratio = '1:8'
ORDER BY created_at DESC
```

## Metadata Operations

### get_unique_cartridge_types

```python
def get_unique_cartridge_types(self, user_id: str) -> List[str]
```

Get unique cartridge types from user's rifles.

**Use Case:** Populating filter dropdowns in UI

**Parameters:**
- `user_id` (str): The user's ID

**Returns:**
- `List[str]`: Sorted list of unique cartridge type strings
- Empty list if user has no rifles

**Raises:**
- `Exception`: If database operation fails

**Example:**
```python
types = api.get_unique_cartridge_types("user-123")
print("Available calibers:")
for t in types:
    print(f"  - {t}")

# Example output:
# Available calibers:
#   - 223 Remington
#   - 6.5 Creedmoor
#   - 308 Winchester
```

**SQL Query:**
```sql
SELECT DISTINCT cartridge_type FROM rifles
WHERE user_id = 'user-123'
  AND cartridge_type IS NOT NULL
ORDER BY cartridge_type
```

---

### get_unique_twist_ratios

```python
def get_unique_twist_ratios(self, user_id: str) -> List[str]
```

Get unique barrel twist ratios from user's rifles.

**Use Case:** Populating filter dropdowns in UI

**Parameters:**
- `user_id` (str): The user's ID

**Returns:**
- `List[str]`: Sorted list of unique twist ratio strings
- Empty list if user has no rifles

**Raises:**
- `Exception`: If database operation fails

**Example:**
```python
ratios = api.get_unique_twist_ratios("user-123")
print("Available twist ratios:")
for r in ratios:
    print(f"  - {r}")

# Example output:
# Available twist ratios:
#   - 1:7
#   - 1:8
#   - 1:9
```

**SQL Query:**
```sql
SELECT DISTINCT barrel_twist_ratio FROM rifles
WHERE user_id = 'user-123'
  AND barrel_twist_ratio IS NOT NULL
ORDER BY barrel_twist_ratio
```

## Write Operations

### create_rifle

```python
def create_rifle(
    self,
    rifle_data: dict,
    user_id: str
) -> RifleModel
```

Create a new rifle.

Automatically generates UUID, sets timestamps, and enforces user ownership.

**Parameters:**
- `rifle_data` (dict): Rifle fields
  - `name` (str, **required**): Rifle name
  - `cartridge_type` (str, **required**): Cartridge type
  - `barrel_twist_ratio` (str, optional): e.g., "1:8"
  - `barrel_length` (str, optional): e.g., "24 inches"
  - `sight_offset` (str, optional): Height over bore
  - `trigger` (str, optional): Trigger description
  - `scope` (str, optional): Scope description
- `user_id` (str): Owner's user ID

**Returns:**
- `RifleModel`: Created rifle with generated ID and timestamps

**Raises:**
- `Exception`: If creation fails or required fields missing

**Example:**
```python
rifle_data = {
    "name": "Bergara B-14 HMR",
    "cartridge_type": "6.5 Creedmoor",
    "barrel_twist_ratio": "1:8",
    "barrel_length": "24 inches",
    "trigger": "Bergara Performance Trigger",
    "scope": "Vortex Viper PST Gen II 5-25x50"
}

rifle = api.create_rifle(rifle_data, "user-123")
print(f"Created rifle: {rifle.id}")
print(f"  Name: {rifle.name}")
print(f"  Created: {rifle.created_at}")
```

**Generated Fields:**
- `id`: UUID (e.g., "a1b2c3d4-...")
- `user_id`: Set from parameter
- `created_at`: Current timestamp
- `updated_at`: Current timestamp

**SQL Operation:**
```sql
INSERT INTO rifles (
    id, user_id, name, cartridge_type,
    barrel_twist_ratio, barrel_length, sight_offset,
    trigger, scope, created_at, updated_at
) VALUES (
    'a1b2c3d4-...', 'user-123', 'Bergara B-14 HMR',
    '6.5 Creedmoor', '1:8', '24 inches', NULL,
    'Bergara Performance Trigger',
    'Vortex Viper PST Gen II 5-25x50',
    '2025-01-15T10:30:00', '2025-01-15T10:30:00'
)
RETURNING *
```

---

### update_rifle

```python
def update_rifle(
    self,
    rifle_id: str,
    updates: dict,
    user_id: str
) -> RifleModel
```

Update an existing rifle.

Automatically updates `updated_at` timestamp. Only provided fields are updated.

**Parameters:**
- `rifle_id` (str): The rifle's unique ID
- `updates` (dict): Fields to update (only provided fields are updated)
  - Any RifleModel field except `id`, `user_id`, `created_at`
- `user_id` (str): The user's ID (for access control)

**Returns:**
- `RifleModel`: Updated rifle

**Raises:**
- `Exception`: If update fails or rifle not found/not owned by user

**Examples:**
```python
# Update single field
updates = {"barrel_length": "26 inches"}
rifle = api.update_rifle("rifle-123", updates, "user-123")

# Update multiple fields
updates = {
    "barrel_length": "26 inches",
    "scope": "Nightforce ATACR 7-35x56",
    "trigger": "TriggerTech Diamond 1.5lb"
}
rifle = api.update_rifle("rifle-123", updates, "user-123")
print(f"Updated: {rifle.updated_at}")

# Clear optional field (set to None)
updates = {"scope": None}
rifle = api.update_rifle("rifle-123", updates, "user-123")
```

**SQL Operation:**
```sql
UPDATE rifles
SET barrel_length = '26 inches',
    updated_at = '2025-01-15T11:00:00'
WHERE id = 'rifle-123'
  AND user_id = 'user-123'
RETURNING *
```

---

### delete_rifle

```python
def delete_rifle(
    self,
    rifle_id: str,
    user_id: str
) -> bool
```

Delete a rifle.

**Parameters:**
- `rifle_id` (str): The rifle's unique ID
- `user_id` (str): The user's ID (for access control)

**Returns:**
- `True`: If deleted successfully
- `False`: If rifle not found or not owned by user

**Raises:**
- `Exception`: If database operation fails

**Example:**
```python
# Delete rifle
success = api.delete_rifle("rifle-123", "user-123")

if success:
    print("Rifle deleted successfully")
else:
    print("Rifle not found or not owned by user")

# Verify deletion
rifle = api.get_rifle_by_id("rifle-123", "user-123")
assert rifle is None  # Rifle is gone
```

**SQL Operation:**
```sql
DELETE FROM rifles
WHERE id = 'rifle-123'
  AND user_id = 'user-123'
RETURNING *
```

## Type Protocol

### RiflesAPIProtocol

```python
from rifles import RiflesAPIProtocol
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    api: RiflesAPIProtocol = RiflesAPI(supabase)
```

The `RiflesAPIProtocol` defines the complete API contract using Python's Protocol class for structural typing. This enables:

- **Static Type Checking**: mypy/pyright verify implementations
- **IDE Support**: Auto-completion and inline documentation
- **Contract Verification**: Ensures API compliance

**Protocol Definition:**
```python
class RiflesAPIProtocol(Protocol):
    # Read Operations
    def get_all_rifles(self, user_id: str) -> List[RifleModel]: ...
    def get_rifle_by_id(
        self, rifle_id: str, user_id: str
    ) -> Optional[RifleModel]: ...
    def get_rifle_by_name(
        self, user_id: str, name: str
    ) -> Optional[RifleModel]: ...
    def filter_rifles(
        self,
        user_id: str,
        cartridge_type: Optional[str] = None,
        twist_ratio: Optional[str] = None
    ) -> List[RifleModel]: ...

    # Metadata Operations
    def get_unique_cartridge_types(self, user_id: str) -> List[str]: ...
    def get_unique_twist_ratios(self, user_id: str) -> List[str]: ...

    # Write Operations
    def create_rifle(
        self, rifle_data: dict, user_id: str
    ) -> RifleModel: ...
    def update_rifle(
        self, rifle_id: str, updates: dict, user_id: str
    ) -> RifleModel: ...
    def delete_rifle(self, rifle_id: str, user_id: str) -> bool: ...
```

## Error Handling

### Common Errors

#### Rifle Not Found

```python
try:
    rifle = api.get_rifle_by_id("invalid-id", user_id)
    # rifle will be None, no exception raised
    if not rifle:
        print("Rifle not found")
except Exception as e:
    # Only database errors raise exceptions
    print(f"Database error: {e}")
```

#### Access Control Violation

```python
# User tries to access another user's rifle
rifle = api.get_rifle_by_id("rifle-123", "wrong-user-id")
# Returns None (rifle exists but belongs to different user)
```

#### Missing Required Fields

```python
try:
    rifle_data = {
        "barrel_length": "24 inches"
        # Missing required: name, cartridge_type
    }
    rifle = api.create_rifle(rifle_data, user_id)
except Exception as e:
    print(f"Creation failed: {e}")
    # Error will indicate missing required fields
```

#### Update Non-Existent Rifle

```python
try:
    updates = {"barrel_length": "26 inches"}
    rifle = api.update_rifle("invalid-id", updates, user_id)
except Exception as e:
    print(f"Update failed: {e}")
    # Error: Rifle not found or not owned by user
```

### Best Practices

```python
# 1. Always check for None on get operations
rifle = api.get_rifle_by_id(rifle_id, user_id)
if rifle:
    # Safe to use rifle
    process_rifle(rifle)
else:
    # Handle not found
    log_error(f"Rifle {rifle_id} not found")

# 2. Use try-except for write operations
try:
    rifle = api.create_rifle(rifle_data, user_id)
    log_success(f"Created rifle {rifle.id}")
except Exception as e:
    log_error(f"Failed to create rifle: {e}")

# 3. Verify deletion success
if api.delete_rifle(rifle_id, user_id):
    log_success(f"Deleted rifle {rifle_id}")
else:
    log_warning(f"Rifle {rifle_id} not found")
```

## Performance Considerations

### Efficient Filtering

```python
# Good - filter at database level
rifles = api.filter_rifles(user_id, cartridge_type="6.5 Creedmoor")

# Bad - load all then filter in Python
all_rifles = api.get_all_rifles(user_id)
rifles = [r for r in all_rifles if r.cartridge_type == "6.5 Creedmoor"]
```

### Batch Operations

```python
# If you need multiple rifles by ID, consider using filter
rifle_ids = ["rifle-1", "rifle-2", "rifle-3"]

# Current approach (multiple queries)
rifles = [
    api.get_rifle_by_id(rid, user_id)
    for rid in rifle_ids
]

# Note: Batch get operation not yet implemented
# Future: api.get_rifles_by_ids(rifle_ids, user_id)
```

### Caching Metadata

```python
# Cache unique values for dropdowns
cartridge_types = api.get_unique_cartridge_types(user_id)
twist_ratios = api.get_unique_twist_ratios(user_id)

# Reuse cached values instead of fetching repeatedly
# Update cache when rifles are added/modified
```

## See Also

- [Models Reference](./models.md) - RifleModel details
- [Examples](./examples.md) - Practical usage examples
- [README](./README.md) - Module overview