# Rifles Module

**Version:** 1.0.0
**Status:** Production Ready

## Overview

The Rifles module provides a type-safe, protocol-based API for managing firearm specifications in ChronoLog. It stores detailed information about rifles including barrel characteristics, cartridge types, and equipment details.

### Key Features

- **User-Scoped Ownership**: All rifles belong to individual users
- **Type Safety**: Full Protocol-based type checking
- **Rich Metadata**: Barrel specifications, optics, trigger details
- **Flexible Filtering**: Filter by cartridge type, twist ratio
- **Display Helpers**: Formatted display methods for UI

## Architecture

```
RiflesAPI (Public Interface)
    ↓
RifleService (Database Operations)
    ↓
Supabase (rifles table)
```

### Ownership Model

Unlike the cartridges module which supports both global and user-owned entries, rifles are **user-scoped only**:

- Each rifle belongs to exactly one user
- No global/shared rifles
- Access control enforced at all layers
- User ID required for all operations

## Quick Start

### Installation

```python
from rifles import RiflesAPI

# Initialize with Supabase client
api = RiflesAPI(supabase_client)
```

### Basic Operations

```python
# Create a rifle
rifle_data = {
    "name": "Remington 700",
    "cartridge_type": "6.5 Creedmoor",
    "barrel_twist_ratio": "1:8",
    "barrel_length": "24 inches",
    "scope": "Vortex Viper PST 5-25x50"
}
rifle = api.create_rifle(rifle_data, user_id)

# Get all rifles for a user
rifles = api.get_all_rifles(user_id)

# Filter rifles
creedmoor_rifles = api.filter_rifles(
    user_id,
    cartridge_type="6.5 Creedmoor"
)

# Update a rifle
updates = {"barrel_length": "26 inches"}
updated_rifle = api.update_rifle(rifle.id, updates, user_id)

# Delete a rifle
if api.delete_rifle(rifle.id, user_id):
    print("Rifle deleted successfully")
```

## Data Model

### RifleModel

Represents a firearm with ballistics-relevant specifications.

**Required Fields:**
- `id` (str): Unique identifier (UUID)
- `user_id` (str): Owner's user ID
- `name` (str): User-defined rifle name
- `cartridge_type` (str): Cartridge caliber (e.g., "6.5 Creedmoor")

**Optional Fields:**
- `barrel_twist_ratio` (str): Rifling twist rate (e.g., "1:8")
- `barrel_length` (str): Barrel length with units (e.g., "24 inches")
- `sight_offset` (str): Height over bore measurement
- `trigger` (str): Trigger description/specs
- `scope` (str): Scope/optic description

**Timestamps:**
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

### Display Methods

RifleModel provides helpful display methods:

```python
rifle.display_name()      # "Remington 700 (6.5 Creedmoor)"
rifle.barrel_display()    # "24 inches - Twist: 1:8"
rifle.optics_display()    # "Scope: Vortex - Offset: 1.5 inches"
rifle.trigger_display()   # "Timney 2-stage 2.5lb"
```

## API Reference

### Read Operations

#### `get_all_rifles(user_id: str) -> List[RifleModel]`

Get all rifles for a user, ordered by creation date descending.

**Parameters:**
- `user_id` (str): The user's ID

**Returns:**
- `List[RifleModel]`: List of rifles owned by user
- Empty list if user has no rifles

**Example:**
```python
rifles = api.get_all_rifles("user-123")
for rifle in rifles:
    print(f"{rifle.name} - {rifle.cartridge_type}")
```

#### `get_rifle_by_id(rifle_id: str, user_id: str) -> Optional[RifleModel]`

Get a specific rifle by ID.

**Parameters:**
- `rifle_id` (str): The rifle's unique ID
- `user_id` (str): The user's ID (for access control)

**Returns:**
- `RifleModel` if found and owned by user
- `None` if not found or not owned

**Example:**
```python
rifle = api.get_rifle_by_id("rifle-123", "user-123")
if rifle:
    print(f"Found: {rifle.name}")
```

#### `get_rifle_by_name(user_id: str, name: str) -> Optional[RifleModel]`

Get a rifle by name.

**Note:** Returns first match if multiple rifles have the same name.

**Parameters:**
- `user_id` (str): The user's ID
- `name` (str): The rifle name to search for

**Returns:**
- `RifleModel` if found
- `None` if not found

**Example:**
```python
rifle = api.get_rifle_by_name("user-123", "Remington 700")
```

#### `filter_rifles(user_id: str, cartridge_type: Optional[str] = None, twist_ratio: Optional[str] = None) -> List[RifleModel]`

Get rifles filtered by criteria.

**Parameters:**
- `user_id` (str): The user's ID
- `cartridge_type` (str, optional): Filter by cartridge type (use "All" or None for all)
- `twist_ratio` (str, optional): Filter by twist ratio (use "All" or None for all)

**Returns:**
- `List[RifleModel]`: Matching rifles, ordered by creation date descending

**Example:**
```python
# All 6.5 Creedmoor rifles
rifles = api.filter_rifles("user-123", cartridge_type="6.5 Creedmoor")

# 6.5 Creedmoor with 1:8 twist
rifles = api.filter_rifles(
    "user-123",
    cartridge_type="6.5 Creedmoor",
    twist_ratio="1:8"
)
```

### Metadata Operations

#### `get_unique_cartridge_types(user_id: str) -> List[str]`

Get unique cartridge types from user's rifles.

**Use Case:** Populating filter dropdowns in UI

**Parameters:**
- `user_id` (str): The user's ID

**Returns:**
- `List[str]`: Sorted list of unique cartridge types

**Example:**
```python
types = api.get_unique_cartridge_types("user-123")
# ['6.5 Creedmoor', '308 Winchester', ...]
```

#### `get_unique_twist_ratios(user_id: str) -> List[str]`

Get unique barrel twist ratios from user's rifles.

**Use Case:** Populating filter dropdowns in UI

**Parameters:**
- `user_id` (str): The user's ID

**Returns:**
- `List[str]`: Sorted list of unique twist ratios

**Example:**
```python
ratios = api.get_unique_twist_ratios("user-123")
# ['1:7', '1:8', '1:9', ...]
```

### Write Operations

#### `create_rifle(rifle_data: dict, user_id: str) -> RifleModel`

Create a new rifle.

**Parameters:**
- `rifle_data` (dict): Rifle fields
  - `name` (str, required): Rifle name
  - `cartridge_type` (str, required): Cartridge type
  - `barrel_twist_ratio` (str, optional): e.g., "1:8"
  - `barrel_length` (str, optional): e.g., "24 inches"
  - `sight_offset` (str, optional): Height over bore
  - `trigger` (str, optional): Trigger description
  - `scope` (str, optional): Scope description
- `user_id` (str): Owner's user ID

**Returns:**
- `RifleModel`: Created rifle with generated ID

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
rifle = api.create_rifle(rifle_data, user_id)
```

#### `update_rifle(rifle_id: str, updates: dict, user_id: str) -> RifleModel`

Update an existing rifle.

**Parameters:**
- `rifle_id` (str): The rifle's unique ID
- `updates` (dict): Fields to update (only provided fields are updated)
- `user_id` (str): The user's ID (for access control)

**Returns:**
- `RifleModel`: Updated rifle

**Example:**
```python
updates = {
    "barrel_length": "26 inches",
    "scope": "Nightforce ATACR 7-35x56"
}
rifle = api.update_rifle("rifle-123", updates, user_id)
```

#### `delete_rifle(rifle_id: str, user_id: str) -> bool`

Delete a rifle.

**Parameters:**
- `rifle_id` (str): The rifle's unique ID
- `user_id` (str): The user's ID (for access control)

**Returns:**
- `True` if deleted successfully
- `False` if not found or not owned by user

**Example:**
```python
if api.delete_rifle("rifle-123", user_id):
    print("Rifle deleted")
else:
    print("Rifle not found")
```

## Common Use Cases

### Building a Rifle Selection UI

```python
# Get all unique cartridge types for dropdown
types = api.get_unique_cartridge_types(user_id)

# User selects a type, filter rifles
selected_type = "6.5 Creedmoor"
rifles = api.filter_rifles(user_id, cartridge_type=selected_type)

# Display rifles
for rifle in rifles:
    print(f"{rifle.display_name()}")
    print(f"  Barrel: {rifle.barrel_display()}")
    print(f"  Optics: {rifle.optics_display()}")
```

### Rifle Profile Page

```python
# Get rifle details
rifle = api.get_rifle_by_id(rifle_id, user_id)

if rifle:
    print(f"Name: {rifle.name}")
    print(f"Caliber: {rifle.cartridge_type}")
    print(f"Barrel: {rifle.barrel_display()}")
    print(f"Trigger: {rifle.trigger_display()}")
    print(f"Optics: {rifle.optics_display()}")
    print(f"Created: {rifle.created_at}")
```

### Quick Rifle Lookup by Name

```python
# User types "Remington"
rifle = api.get_rifle_by_name(user_id, "Remington 700")

if rifle:
    # Found exact match
    load_rifle_profile(rifle)
else:
    # No exact match, show filtered list
    all_rifles = api.get_all_rifles(user_id)
    matches = [r for r in all_rifles if "Remington" in r.name]
```

## Integration with Other Modules

### With Cartridges Module

Rifles store a `cartridge_type` field that can be used to find compatible cartridges:

```python
from rifles import RiflesAPI
from cartridges import CartridgesAPI

rifles_api = RiflesAPI(supabase)
cartridges_api = CartridgesAPI(supabase)

# Get rifle
rifle = rifles_api.get_rifle_by_id(rifle_id, user_id)

# Find compatible cartridges
cartridges = cartridges_api.filter_cartridges(
    user_id,
    cartridge_type=rifle.cartridge_type
)

print(f"Compatible cartridges for {rifle.name}:")
for cartridge in cartridges:
    print(f"  - {cartridge.display_name}")
```

### With Chronograph Module

Rifles can be associated with chronograph sessions via their cartridge type:

```python
# Get rifle's cartridge type
rifle = rifles_api.get_rifle_by_id(rifle_id, user_id)

# Create chronograph session with this rifle's specs
session_data = {
    "rifle_name": rifle.name,
    "cartridge_type": rifle.cartridge_type,
    "barrel_length": rifle.barrel_length,
    # ... other session fields
}
```

## Error Handling

```python
try:
    # Create rifle
    rifle = api.create_rifle(rifle_data, user_id)
except Exception as e:
    print(f"Error creating rifle: {e}")

try:
    # Update rifle
    rifle = api.update_rifle(rifle_id, updates, user_id)
except Exception as e:
    # Rifle not found or not owned by user
    print(f"Error updating rifle: {e}")
```

## Best Practices

### 1. Use Display Methods for UI

```python
# Good - uses display method
print(rifle.display_name())  # "Remington 700 (6.5 Creedmoor)"

# Avoid - manual formatting
print(f"{rifle.name} ({rifle.cartridge_type})")
```

### 2. Handle Optional Fields

```python
# Good - check for None
if rifle.barrel_length:
    print(f"Barrel: {rifle.barrel_length}")

# Or use display methods which handle None
print(rifle.barrel_display())  # "Not specified" if None
```

### 3. Use Filters for Performance

```python
# Good - filter at database level
rifles = api.filter_rifles(user_id, cartridge_type="6.5 Creedmoor")

# Avoid - filter in Python
all_rifles = api.get_all_rifles(user_id)
rifles = [r for r in all_rifles if r.cartridge_type == "6.5 Creedmoor"]
```

### 4. Verify Ownership

```python
# Good - user_id enforced in API
rifle = api.get_rifle_by_id(rifle_id, user_id)

# The API automatically ensures the rifle belongs to user_id
if rifle:
    # Safe to use rifle data
    pass
```

## Testing

See test files for comprehensive examples:
- `rifles/test_rifles_api.py` - Unit tests with mocked database
- `rifles/test_rifles_integration.py` - Integration tests with real Supabase

## Further Documentation

- [API Reference](./api-reference.md) - Complete API documentation
- [Models Reference](./models.md) - Data model details
- [Examples](./examples.md) - Practical usage examples

## Support

For issues or questions:
- Check the [examples](./examples.md) for common patterns
- Review the [API reference](./api-reference.md) for method signatures
- See test files for additional usage examples