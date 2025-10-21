# Bullets API Reference

## Overview

The Bullets API provides type-safe access to the bullet specifications catalog. This API follows the `BulletsAPIProtocol` defined in `bullets/protocols.py`.

All API methods are UI-agnostic and return strongly-typed `BulletModel` instances.

## API Contract

```python
from bullets.protocols import BulletsAPIProtocol
from bullets.models import BulletModel
```

The `BulletsAPIProtocol` defines the complete API contract that all implementations must follow.

---

## Public Methods (All Users)

These methods are available to all users for reading the global bullet catalog.

### get_all_bullets()

Get all bullets from the global catalog.

**Signature**:
```python
def get_all_bullets(self) -> List[BulletModel]
```

**Parameters**: None

**Returns**:
- `List[BulletModel]`: List of all bullets, ordered by manufacturer, model, and weight
- Empty list if no bullets found

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = BulletsAPI(supabase_client)
bullets = api.get_all_bullets()

for bullet in bullets:
    print(f"{bullet.manufacturer} {bullet.model} - {bullet.weight_grains}gr")
```

**Notes**:
- No user filtering - this is a global catalog
- Results are ordered for consistent display
- Returns all fields for each bullet

---

### get_bullet_by_id()

Get a specific bullet by its UUID.

**Signature**:
```python
def get_bullet_by_id(self, bullet_id: str) -> Optional[BulletModel]
```

**Parameters**:
- `bullet_id` (str): UUID of the bullet to retrieve

**Returns**:
- `BulletModel`: Bullet if found
- `None`: If bullet not found

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = BulletsAPI(supabase_client)
bullet = api.get_bullet_by_id("123e4567-e89b-12d3-a456-426614174000")

if bullet:
    print(f"Found: {bullet.display_name}")
    print(f"BC (G7): {bullet.ballistic_coefficient_g7}")
else:
    print("Bullet not found")
```

**Notes**:
- Returns `None` rather than raising exception if not found
- No user_id required (global catalog)

---

### get_bullets_by_ids()

Get multiple bullets by their UUIDs in a single batch operation.

**Signature**:
```python
def get_bullets_by_ids(self, bullet_ids: List[str]) -> List[BulletModel]
```

**Parameters**:
- `bullet_ids` (List[str]): List of bullet UUIDs to retrieve

**Returns**:
- `List[BulletModel]`: List of found bullets
- May be fewer bullets than IDs provided (if some not found)

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = BulletsAPI(supabase_client)

# Load bullets for multiple cartridges efficiently
bullet_ids = ["id1", "id2", "id3"]
bullets = api.get_bullets_by_ids(bullet_ids)

# Map bullets by ID for quick lookup
bullets_by_id = {b.id: b for b in bullets}
```

**Notes**:
- More efficient than calling `get_bullet_by_id()` in a loop
- Useful for loading bullets for multiple cartridges
- Silently skips IDs that don't exist (no error)

---

### filter_bullets()

Filter bullets by manufacturer, bore diameter, and/or weight.

**Signature**:
```python
def filter_bullets(
    self,
    manufacturer: Optional[str] = None,
    bore_diameter_mm: Optional[float] = None,
    weight_grains: Optional[int] = None,
) -> List[BulletModel]
```

**Parameters**:
- `manufacturer` (Optional[str]): Exact manufacturer name (case-sensitive)
- `bore_diameter_mm` (Optional[float]): Exact bore diameter in millimeters
- `weight_grains` (Optional[int]): Exact weight in grains

**Returns**:
- `List[BulletModel]`: Filtered bullets (empty list if no matches)

**Raises**:
- `Exception`: If database query fails

**Examples**:
```python
api = BulletsAPI(supabase_client)

# Get all Sierra bullets
sierra_bullets = api.filter_bullets(manufacturer="Sierra")

# Get all 168 grain bullets
heavy_bullets = api.filter_bullets(weight_grains=168)

# Get Sierra 168gr bullets (multiple filters)
specific = api.filter_bullets(
    manufacturer="Sierra",
    weight_grains=168
)

# Get all bullets (no filters)
all_bullets = api.filter_bullets()
```

**Notes**:
- All parameters are optional
- Multiple filters are combined with AND logic
- Returns empty list if no matches (not an error)
- Filters are exact matches (not fuzzy search)

---

### get_unique_manufacturers()

Get list of all unique bullet manufacturers in the catalog.

**Signature**:
```python
def get_unique_manufacturers(self) -> List[str]
```

**Parameters**: None

**Returns**:
- `List[str]`: Sorted list of unique manufacturer names

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = BulletsAPI(supabase_client)
manufacturers = api.get_unique_manufacturers()

# Use in UI dropdown
for mfr in manufacturers:
    print(f"Option: {mfr}")

# Result: ['Berger', 'Hornady', 'Nosler', 'Sierra']
```

**Notes**:
- Useful for populating UI dropdowns and filters
- Results are sorted alphabetically
- Includes only manufacturers that have bullets in catalog

---

### get_unique_bore_diameters()

Get list of all unique bore diameters in the catalog.

**Signature**:
```python
def get_unique_bore_diameters(self) -> List[float]
```

**Parameters**: None

**Returns**:
- `List[float]`: Sorted list of unique bore diameters in millimeters

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = BulletsAPI(supabase_client)
diameters = api.get_unique_bore_diameters()

# Use in UI dropdown
for diameter in diameters:
    print(f"Caliber: {diameter}mm")

# Result: [5.56, 6.5, 7.62, 9.0]
```

**Notes**:
- Values are in millimeters (metric)
- Results are sorted numerically
- UI may convert to inches for display

---

### get_unique_weights()

Get list of all unique bullet weights in the catalog.

**Signature**:
```python
def get_unique_weights(self) -> List[int]
```

**Parameters**: None

**Returns**:
- `List[int]`: Sorted list of unique bullet weights in grains

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = BulletsAPI(supabase_client)
weights = api.get_unique_weights()

# Use in UI dropdown
for weight in weights:
    print(f"{weight} gr")

# Result: [55, 69, 77, 147, 168, 175, 180]
```

**Notes**:
- Values are in grains (ballistics standard)
- Results are sorted numerically
- Includes only weights that exist in catalog

---

## Admin Methods (Admin Only)

These methods are for administrative use only and should not be exposed in the regular user API.

### create_bullet()

Create a new bullet entry in the catalog.

**Signature**:
```python
def create_bullet(self, bullet_data: dict) -> BulletModel
```

**Parameters**:
- `bullet_data` (dict): Dictionary with bullet fields (all metric units)

**Required fields**:
- `manufacturer` (str)
- `model` (str)
- `weight_grains` (float)
- `bullet_diameter_groove_mm` (float)
- `bore_diameter_land_mm` (float)

**Optional fields**:
- `bullet_length_mm` (float)
- `ballistic_coefficient_g1` (float)
- `ballistic_coefficient_g7` (float)
- `sectional_density` (float)
- `min_req_twist_rate_in_per_rev` (float)
- `pref_twist_rate_in_per_rev` (float)
- `data_source_name` (str)
- `data_source_url` (str)

**Returns**:
- `BulletModel`: Created bullet with generated UUID

**Raises**:
- `Exception`: If creation fails
- `Exception`: If duplicate bullet exists

**Example**:
```python
api = BulletsAPI(supabase_client)

bullet_data = {
    "manufacturer": "Sierra",
    "model": "MatchKing",
    "weight_grains": 168,
    "bullet_diameter_groove_mm": 7.82,
    "bore_diameter_land_mm": 7.62,
    "ballistic_coefficient_g7": 0.243,
}

bullet = api.create_bullet(bullet_data)
print(f"Created bullet with ID: {bullet.id}")
```

**Notes**:
- UUID is generated automatically
- Admin-only operation
- Validates for duplicate entries

---

### update_bullet()

Update an existing bullet entry.

**Signature**:
```python
def update_bullet(self, bullet_id: str, bullet_data: dict) -> BulletModel
```

**Parameters**:
- `bullet_id` (str): UUID of bullet to update
- `bullet_data` (dict): Dictionary with fields to update (metric units)

**Returns**:
- `BulletModel`: Updated bullet

**Raises**:
- `Exception`: If update fails
- `Exception`: If bullet not found

**Example**:
```python
api = BulletsAPI(supabase_client)

update_data = {
    "ballistic_coefficient_g7": 0.245,  # Updated BC
}

bullet = api.update_bullet(bullet_id, update_data)
print(f"Updated BC to: {bullet.ballistic_coefficient_g7}")
```

**Notes**:
- Admin-only operation
- Can update any field except `id`
- Partial updates supported

---

### delete_bullet()

Delete a bullet from the catalog.

**Signature**:
```python
def delete_bullet(self, bullet_id: str) -> bool
```

**Parameters**:
- `bullet_id` (str): UUID of bullet to delete

**Returns**:
- `bool`: True if deleted, False if not found

**Raises**:
- `Exception`: If delete fails
- `Exception`: If bullet is referenced by cartridges (FK constraint)

**Example**:
```python
api = BulletsAPI(supabase_client)

deleted = api.delete_bullet(bullet_id)
if deleted:
    print("Bullet deleted successfully")
else:
    print("Bullet not found")
```

**Notes**:
- Admin-only operation
- Cannot delete if referenced by cartridges
- No undo - deletion is permanent

---

## Type Safety

All API methods use type hints for compile-time checking:

```python
# IDE autocomplete works
api = BulletsAPI(supabase_client)
bullet = api.get_bullet_by_id("some-id")

if bullet:
    # Type checker knows bullet is BulletModel
    weight = bullet.weight_grains  # ✓ Valid
    bc = bullet.ballistic_coefficient_g7  # ✓ Valid
    invalid = bullet.nonexistent_field  # ✗ Type error

# Return types are enforced
bullets: List[BulletModel] = api.get_all_bullets()  # ✓ Correct type
bullets: List[dict] = api.get_all_bullets()  # ✗ Type error
```

---

## Error Handling

All API methods follow consistent error handling:

**Returns None** (not found, no error):
- `get_bullet_by_id()` returns `None` if bullet not found

**Returns empty list** (no matches, no error):
- `filter_bullets()` returns `[]` if no matches
- `get_all_bullets()` returns `[]` if catalog empty

**Raises Exception** (actual errors):
- Database connection failures
- Invalid parameters
- Constraint violations (duplicate, FK violations)

**Example**:
```python
api = BulletsAPI(supabase_client)

# Handle not found gracefully
bullet = api.get_bullet_by_id("nonexistent-id")
if not bullet:
    print("Bullet not found")  # Not an error

# Handle actual errors
try:
    bullets = api.get_all_bullets()
except Exception as e:
    print(f"Database error: {e}")  # Actual error
```

---

## Next Steps

- [Models Documentation](models.md) - Detailed field specifications
- [Examples](examples.md) - Common usage patterns
- [Module README](README.md) - Overview and integration

---

**API Version**: 1.0
**Protocol**: `bullets.protocols.BulletsAPIProtocol`
**Implementation**: `bullets.api.BulletsAPI` (Phase 3)