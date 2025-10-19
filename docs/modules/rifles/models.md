# Rifles Models Reference

Complete reference for data models in the Rifles module.

## Table of Contents

- [RifleModel](#riflemodel)
- [Field Specifications](#field-specifications)
- [Methods](#methods)
- [Display Helpers](#display-helpers)
- [Type Conversions](#type-conversions)
- [Examples](#examples)

## RifleModel

```python
from rifles import RifleModel
from datetime import datetime
```

The `RifleModel` is a dataclass representing a firearm with ballistics-relevant specifications.

### Class Definition

```python
@dataclass
class RifleModel:
    """
    Domain model representing a rifle.

    Rifles are user-scoped entities storing firearm specifications.
    Each rifle is associated with a cartridge type and includes optional
    ballistics-relevant information like barrel twist rate and length.
    """
    # Required Fields
    id: str
    user_id: str
    name: str
    cartridge_type: str

    # Optional Fields
    barrel_twist_ratio: Optional[str] = None
    barrel_length: Optional[str] = None
    sight_offset: Optional[str] = None
    trigger: Optional[str] = None
    scope: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

## Field Specifications

### Required Fields

#### `id: str`

Unique identifier for the rifle (UUID format).

- **Type:** `str`
- **Format:** UUID v4 (e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
- **Generated:** Automatically by API on creation
- **Immutable:** Cannot be changed after creation

**Example:**
```python
rifle.id  # "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

---

#### `user_id: str`

Owner's user ID.

- **Type:** `str`
- **Format:** Auth0 user ID or UUID
- **Set:** Automatically by API on creation
- **Immutable:** Cannot be changed after creation
- **Purpose:** Enforces user-scoped ownership

**Example:**
```python
rifle.user_id  # "google-oauth2|111273793361054745867"
```

---

#### `name: str`

User-defined rifle name.

- **Type:** `str`
- **Constraints:**
  - Should be unique per user (not enforced at database level)
  - Recommended: Descriptive name
- **Examples:** "Remington 700", "Custom 6.5 PRC Build", "Bergara HMR"

**Example:**
```python
rifle.name  # "Remington 700"
```

---

#### `cartridge_type: str`

Cartridge caliber/type.

- **Type:** `str`
- **Format:** Standard cartridge naming (e.g., "6.5 Creedmoor", "308 Winchester")
- **Purpose:** Links rifle to compatible cartridges module entries
- **Note:** Must match cartridge_types table entries for FK integrity

**Examples:**
```python
rifle.cartridge_type  # "6.5 Creedmoor"
rifle.cartridge_type  # "308 Winchester"
rifle.cartridge_type  # "223 Remington"
```

### Optional Fields

#### `barrel_twist_ratio: Optional[str]`

Rifling twist rate.

- **Type:** `Optional[str]`
- **Format:** Ratio format (e.g., "1:8", "1:10")
- **Default:** `None`
- **Purpose:** Bullet stabilization information

**Common Values:**
- "1:7" - Fast twist (heavy bullets)
- "1:8" - Common for 6.5 Creedmoor
- "1:9" - Common for .223
- "1:10" - Slower twist (light bullets)
- "1:12" - Very slow twist

**Example:**
```python
rifle.barrel_twist_ratio  # "1:8"
rifle.barrel_twist_ratio  # None (if not specified)
```

---

#### `barrel_length: Optional[str]`

Barrel length with units.

- **Type:** `Optional[str]`
- **Format:** Number + units (e.g., "24 inches", "26 inches")
- **Default:** `None`
- **Purpose:** Affects velocity and ballistics

**Examples:**
```python
rifle.barrel_length  # "24 inches"
rifle.barrel_length  # "26 inches"
rifle.barrel_length  # "20 inches"
```

---

#### `sight_offset: Optional[str]`

Height over bore measurement.

- **Type:** `Optional[str]`
- **Format:** Number + units (e.g., "1.5 inches", "2.0 inches")
- **Default:** `None`
- **Purpose:** Ballistics calculator input

**Examples:**
```python
rifle.sight_offset  # "1.5 inches"
rifle.sight_offset  # "2.0 inches"
```

---

#### `trigger: Optional[str]`

Trigger description/specifications.

- **Type:** `Optional[str]`
- **Format:** Free-form text
- **Default:** `None`
- **Common Info:** Manufacturer, model, pull weight

**Examples:**
```python
rifle.trigger  # "Timney 2-stage 2.5lb"
rifle.trigger  # "TriggerTech Diamond 1.5lb"
rifle.trigger  # "Factory trigger"
```

---

#### `scope: Optional[str]`

Scope/optic description.

- **Type:** `Optional[str]`
- **Format:** Free-form text
- **Default:** `None`
- **Common Info:** Manufacturer, model, magnification

**Examples:**
```python
rifle.scope  # "Vortex Viper PST Gen II 5-25x50"
rifle.scope  # "Nightforce ATACR 7-35x56"
rifle.scope  # "Leopold Mark 5HD 5-25x56"
```

### Timestamp Fields

#### `created_at: Optional[datetime]`

Creation timestamp.

- **Type:** `Optional[datetime]`
- **Set:** Automatically by API on creation
- **Immutable:** Cannot be changed
- **Timezone:** UTC or local (depends on Supabase configuration)

**Example:**
```python
rifle.created_at  # datetime(2025, 1, 15, 10, 30, 0)
```

---

#### `updated_at: Optional[datetime]`

Last update timestamp.

- **Type:** `Optional[datetime]`
- **Set:** Automatically by API on creation and updates
- **Updated:** On every update operation

**Example:**
```python
rifle.updated_at  # datetime(2025, 1, 15, 11, 0, 0)
```

## Methods

### Class Methods

#### `from_supabase_record(record: dict) -> RifleModel`

Create a RifleModel from a Supabase database record.

**Parameters:**
- `record` (dict): Database record from Supabase query

**Returns:**
- `RifleModel`: New instance

**Example:**
```python
record = {
    "id": "rifle-123",
    "user_id": "user-123",
    "name": "Remington 700",
    "cartridge_type": "6.5 Creedmoor",
    "barrel_twist_ratio": "1:8",
    "barrel_length": "24 inches",
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:30:00"
}

rifle = RifleModel.from_supabase_record(record)
print(rifle.name)  # "Remington 700"
```

---

#### `from_supabase_records(records: List[dict]) -> List[RifleModel]`

Create a list of RifleModel objects from Supabase records.

**Parameters:**
- `records` (List[dict]): List of database records

**Returns:**
- `List[RifleModel]`: List of rifle instances

**Example:**
```python
records = [
    {"id": "1", "name": "Rifle 1", ...},
    {"id": "2", "name": "Rifle 2", ...},
]

rifles = RifleModel.from_supabase_records(records)
print(len(rifles))  # 2
```

### Instance Methods

#### `to_dict() -> dict`

Convert RifleModel to dictionary for database operations.

**Returns:**
- `dict`: Dictionary with all rifle fields

**Example:**
```python
rifle_dict = rifle.to_dict()
# {
#     "id": "rifle-123",
#     "user_id": "user-123",
#     "name": "Remington 700",
#     "cartridge_type": "6.5 Creedmoor",
#     "barrel_twist_ratio": "1:8",
#     ...
# }

# Use for direct database operations
supabase.table("rifles").insert(rifle_dict).execute()
```

## Display Helpers

RifleModel provides formatted display methods for UI rendering.

### `display_name() -> str`

Get a display-friendly name for the rifle.

**Format:** `"{name} ({cartridge_type})"`

**Returns:**
- `str`: Formatted display name

**Example:**
```python
rifle = RifleModel(
    id="1",
    user_id="user-1",
    name="Remington 700",
    cartridge_type="6.5 Creedmoor"
)

print(rifle.display_name())
# "Remington 700 (6.5 Creedmoor)"
```

---

### `barrel_display() -> str`

Get formatted barrel information.

**Format:** Combines barrel length and twist ratio with " - "

**Returns:**
- `str`: Formatted barrel info or "Not specified"

**Examples:**
```python
# Both length and twist
rifle.barrel_length = "24 inches"
rifle.barrel_twist_ratio = "1:8"
print(rifle.barrel_display())
# "24 inches - Twist: 1:8"

# Length only
rifle.barrel_length = "24 inches"
rifle.barrel_twist_ratio = None
print(rifle.barrel_display())
# "24 inches"

# Twist only
rifle.barrel_length = None
rifle.barrel_twist_ratio = "1:8"
print(rifle.barrel_display())
# "Twist: 1:8"

# Neither
rifle.barrel_length = None
rifle.barrel_twist_ratio = None
print(rifle.barrel_display())
# "Not specified"
```

---

### `optics_display() -> str`

Get formatted optics information.

**Format:** Combines scope and sight offset with " - "

**Returns:**
- `str`: Formatted optics info or "Not specified"

**Examples:**
```python
# Both scope and offset
rifle.scope = "Vortex Viper PST 5-25x50"
rifle.sight_offset = "1.5 inches"
print(rifle.optics_display())
# "Scope: Vortex Viper PST 5-25x50 - Offset: 1.5 inches"

# Scope only
rifle.scope = "Vortex Viper PST 5-25x50"
rifle.sight_offset = None
print(rifle.optics_display())
# "Scope: Vortex Viper PST 5-25x50"

# Offset only
rifle.scope = None
rifle.sight_offset = "1.5 inches"
print(rifle.optics_display())
# "Offset: 1.5 inches"

# Neither
rifle.scope = None
rifle.sight_offset = None
print(rifle.optics_display())
# "Not specified"
```

---

### `trigger_display() -> str`

Get formatted trigger information.

**Returns:**
- `str`: Trigger value or "Not specified"

**Examples:**
```python
rifle.trigger = "Timney 2-stage 2.5lb"
print(rifle.trigger_display())
# "Timney 2-stage 2.5lb"

rifle.trigger = None
print(rifle.trigger_display())
# "Not specified"
```

## Type Conversions

### Database to Model

Timestamps are automatically converted from ISO strings to datetime objects:

```python
# Database record
record = {
    "created_at": "2025-01-15T10:30:00+00:00",
    "updated_at": "2025-01-15T11:00:00+00:00",
    ...
}

# Converted to datetime
rifle = RifleModel.from_supabase_record(record)
rifle.created_at  # datetime object
rifle.updated_at  # datetime object
```

### Model to Database

The `to_dict()` method converts datetime objects back to ISO strings:

```python
rifle = RifleModel(
    id="1",
    user_id="user-1",
    name="Rifle",
    cartridge_type="6.5 Creedmoor",
    created_at=datetime.now()
)

rifle_dict = rifle.to_dict()
# created_at is ISO string: "2025-01-15T10:30:00"
```

## Examples

### Creating a Rifle Model

```python
from rifles import RifleModel
from datetime import datetime

# Manual creation (rare - usually use API)
rifle = RifleModel(
    id="rifle-123",
    user_id="user-123",
    name="Custom Build",
    cartridge_type="6.5 Creedmoor",
    barrel_twist_ratio="1:7.5",
    barrel_length="26 inches",
    sight_offset="1.75 inches",
    trigger="TriggerTech Diamond 1.5lb",
    scope="Nightforce ATACR 7-35x56",
    created_at=datetime.now(),
    updated_at=datetime.now()
)
```

### From Database Record

```python
# Typical usage - from API/database query
record = supabase.table("rifles").select("*").eq("id", rifle_id).single().execute()

rifle = RifleModel.from_supabase_record(record.data)
```

### Using Display Methods in UI

```python
# Display card
print(f"Rifle: {rifle.display_name()}")
print(f"Barrel: {rifle.barrel_display()}")
print(f"Trigger: {rifle.trigger_display()}")
print(f"Optics: {rifle.optics_display()}")

# Output:
# Rifle: Custom Build (6.5 Creedmoor)
# Barrel: 26 inches - Twist: 1:7.5
# Trigger: TriggerTech Diamond 1.5lb
# Optics: Scope: Nightforce ATACR 7-35x56 - Offset: 1.75 inches
```

### Converting to Dictionary

```python
# For database operations
rifle_dict = rifle.to_dict()

# Use in Supabase query
supabase.table("rifles").insert(rifle_dict).execute()

# Or for JSON serialization
import json
json_str = json.dumps(rifle_dict, default=str)
```

### Handling Optional Fields

```python
# Check before using
if rifle.barrel_length:
    print(f"Barrel: {rifle.barrel_length}")
else:
    print("Barrel length not specified")

# Or use display methods which handle None
print(rifle.barrel_display())  # Always returns a string
```

### Comparing Rifles

```python
# Compare by attributes
rifles = api.get_all_rifles(user_id)

# Group by cartridge type
from collections import defaultdict
by_type = defaultdict(list)
for rifle in rifles:
    by_type[rifle.cartridge_type].append(rifle)

# Find rifles with fastest twist
sorted_by_twist = sorted(
    [r for r in rifles if r.barrel_twist_ratio],
    key=lambda r: float(r.barrel_twist_ratio.split(':')[1])
)
```

## Validation

While the model itself doesn't enforce validation, consider these best practices:

### Required Field Validation

```python
# Ensure required fields are present
def validate_rifle_data(data: dict) -> bool:
    required = ["name", "cartridge_type"]
    return all(field in data for field in required)

if validate_rifle_data(rifle_data):
    rifle = api.create_rifle(rifle_data, user_id)
```

### Format Validation

```python
import re

def validate_twist_ratio(ratio: str) -> bool:
    """Validate twist ratio format (e.g., '1:8')"""
    pattern = r'^\d+:\d+(\.\d+)?$'
    return bool(re.match(pattern, ratio))

# Example usage
if rifle.barrel_twist_ratio:
    assert validate_twist_ratio(rifle.barrel_twist_ratio)
```

## See Also

- [API Reference](./api-reference.md) - Complete API documentation
- [Examples](./examples.md) - Practical usage examples
- [README](./README.md) - Module overview