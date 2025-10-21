# Cartridges Models

Data models for the cartridges module with dual ownership support.

---

## CartridgeModel

Primary data model for cartridge specifications with embedded bullet data.

### Class Definition

```python
@dataclass
class CartridgeModel:
    """Entity representing a cartridge specification with bullet details"""
```

---

### Core Fields

#### id
- **Type**: `Optional[str]`
- **Description**: UUID primary key, auto-generated
- **Example**: `"123e4567-e89b-12d3-a456-426614174000"`

#### owner_id
- **Type**: `Optional[str]`
- **Description**: User ID of owner (NULL for global/admin cartridges)
- **Values**:
  - `None` (NULL): Global cartridge, visible to all users
  - User ID string: User-owned cartridge, visible only to owner
- **Example**: `"google-oauth2|111273793361054745867"` or `None`

#### make
- **Type**: `str`
- **Required**: Yes (NOT NULL in database)
- **Description**: Manufacturer name
- **Examples**: `"Federal"`, `"Hornady"`, `"Custom Load"`

#### model
- **Type**: `str`
- **Required**: Yes (NOT NULL in database)
- **Description**: Model name or designation
- **Examples**: `"Gold Medal"`, `"Match"`, `"Superformance"`

#### bullet_id
- **Type**: `Optional[str]`
- **Required**: Yes (NOT NULL in database)
- **Description**: Foreign key to bullets table
- **Example**: `"456e7890-e89b-12d3-a456-426614174111"`

#### cartridge_type
- **Type**: `str`
- **Required**: Yes (NOT NULL in database)
- **Description**: Cartridge type designation from lookup table
- **Examples**: `"6.5 Creedmoor"`, `".308 Winchester"`, `"6mm Creedmoor"`

---

### Optional Fields

#### data_source_name
- **Type**: `Optional[str]`
- **Description**: Name of data source (catalog, manufacturer, etc.)
- **Example**: `"Federal Catalog 2024"`

#### data_source_link
- **Type**: `Optional[str]`
- **Description**: URL to source documentation
- **Example**: `"https://federal.com/products/gold-medal"`

#### cartridge_key
- **Type**: `Optional[str]`
- **Description**: Generated natural key for deduplication
- **Example**: `"federal-gold-medal-65creedmoor"`

#### created_at
- **Type**: `Optional[datetime]`
- **Description**: Timestamp when cartridge was created
- **Auto-generated**: Yes

#### updated_at
- **Type**: `Optional[datetime]`
- **Description**: Timestamp of last update
- **Auto-updated**: Yes

---

### Embedded Bullet Fields

These fields are populated via JOIN with the bullets table and provide nested bullet data without requiring a separate API call.

#### bullet_manufacturer
- **Type**: `Optional[str]`
- **Description**: Bullet manufacturer name (from bullets table)
- **Example**: `"Hornady"`

#### bullet_model
- **Type**: `Optional[str]`
- **Description**: Bullet model name (from bullets table)
- **Example**: `"ELD Match"`

#### bullet_weight_grains
- **Type**: `Optional[float]`
- **Description**: Bullet weight in grains
- **Example**: `147.0`

#### bullet_diameter_groove_mm
- **Type**: `Optional[float]`
- **Description**: Bullet diameter at groove in millimeters
- **Example**: `6.71`

#### bore_diameter_land_mm
- **Type**: `Optional[float]`
- **Description**: Bore diameter at land in millimeters (defines caliber)
- **Example**: `6.5`

#### bullet_length_mm
- **Type**: `Optional[float]`
- **Description**: Bullet length in millimeters
- **Example**: `33.3`

#### ballistic_coefficient_g1
- **Type**: `Optional[float]`
- **Description**: Ballistic coefficient using G1 standard
- **Example**: `0.697`

#### ballistic_coefficient_g7
- **Type**: `Optional[float]`
- **Description**: Ballistic coefficient using G7 standard (preferred for modern bullets)
- **Example**: `0.351`

#### sectional_density
- **Type**: `Optional[float]`
- **Description**: Sectional density of bullet
- **Example**: `0.301`

#### min_req_twist_rate_in_per_rev
- **Type**: `Optional[float]`
- **Description**: Minimum required barrel twist rate (inches per revolution)
- **Example**: `8.0` (means 1:8" twist)

#### pref_twist_rate_in_per_rev
- **Type**: `Optional[float]`
- **Description**: Preferred barrel twist rate for optimal accuracy
- **Example**: `7.5` (means 1:7.5" twist)

---

### Properties

#### display_name
- **Type**: `str`
- **Description**: Human-readable cartridge name
- **Format**: `"{make} {model} ({cartridge_type})"`
- **Example**: `"Federal Gold Medal (6.5 Creedmoor)"`

```python
cartridge = api.get_cartridge_by_id(cartridge_id, user_id)
print(cartridge.display_name)
# Output: "Federal Gold Medal (6.5 Creedmoor)"
```

#### bullet_display
- **Type**: `str`
- **Description**: Human-readable bullet description
- **Format**: `"{bullet_manufacturer} {bullet_model} {bullet_weight_grains}gr"`
- **Example**: `"Hornady ELD Match 147gr"`
- **Fallback**: `"Unknown Bullet"` if bullet data missing

```python
print(cartridge.bullet_display)
# Output: "Hornady ELD Match 147gr"
```

#### is_global
- **Type**: `bool`
- **Description**: Check if cartridge is global (admin-owned)
- **Returns**: `True` if `owner_id is None`, else `False`

```python
if cartridge.is_global:
    print("This is a factory load available to all users")
```

#### is_user_owned
- **Type**: `bool`
- **Description**: Check if cartridge is user-owned
- **Returns**: `True` if `owner_id is not None`, else `False`

```python
if cartridge.is_user_owned:
    print("This is a custom handload")
```

#### ballistic_data_summary
- **Type**: `str`
- **Description**: Formatted summary of ballistic data
- **Format**: Comma-separated list of available ballistic coefficients and sectional density
- **Example**: `"G1 BC: 0.697, G7 BC: 0.351, SD: 0.301"`
- **Fallback**: `"No ballistic data"` if no data available

```python
print(cartridge.ballistic_data_summary)
# Output: "G1 BC: 0.697, G7 BC: 0.351, SD: 0.301"
```

#### twist_rate_recommendation
- **Type**: `str`
- **Description**: Formatted twist rate recommendations
- **Formats**:
  - Both available: `'Min: 1:{min}", Pref: 1:{pref}"'`
  - Min only: `'Min: 1:{min}"'`
  - Pref only: `'Pref: 1:{pref}"'`
  - Neither: `"No twist rate data"`
- **Example**: `'Min: 1:8", Pref: 1:7.5"'`

```python
print(cartridge.twist_rate_recommendation)
# Output: 'Min: 1:8", Pref: 1:7.5"'
```

---

### Methods

#### from_supabase_record()
- **Type**: Class method
- **Parameters**: `record: dict` - Database record
- **Returns**: `CartridgeModel`
- **Description**: Create CartridgeModel instance from Supabase record

```python
record = {...}  # Database record
cartridge = CartridgeModel.from_supabase_record(record)
```

#### from_supabase_records()
- **Type**: Class method
- **Parameters**: `records: List[dict]` - List of database records
- **Returns**: `List[CartridgeModel]`
- **Description**: Create list of CartridgeModel instances

```python
records = [...]  # Database records
cartridges = CartridgeModel.from_supabase_records(records)
```

#### to_dict()
- **Type**: Instance method
- **Returns**: `dict`
- **Description**: Convert to dictionary for database operations
- **Excludes**: `id`, timestamp fields, embedded bullet data

```python
cartridge_dict = cartridge.to_dict()
# Returns: {"owner_id": ..., "make": ..., "model": ..., ...}
```

#### is_complete()
- **Type**: Instance method
- **Returns**: `bool`
- **Description**: Check if all mandatory fields are filled
- **Mandatory**: `make`, `model`, `bullet_id`, `cartridge_type`

```python
if cartridge.is_complete():
    print("All required fields filled")
else:
    missing = cartridge.get_missing_mandatory_fields()
    print(f"Missing fields: {missing}")
```

#### get_missing_mandatory_fields()
- **Type**: Instance method
- **Returns**: `List[str]`
- **Description**: Get list of missing mandatory field names
- **Returns**: Empty list if complete

```python
missing = cartridge.get_missing_mandatory_fields()
if missing:
    print(f"Please fill: {', '.join(missing)}")
# Output: "Please fill: Make, Bullet Id"
```

---

## CartridgeTypeModel

Data model for cartridge types from the lookup table.

### Class Definition

```python
@dataclass
class CartridgeTypeModel:
    """Entity representing a cartridge type from lookup table"""
```

### Fields

#### name
- **Type**: `str`
- **Description**: Cartridge type name (primary key)
- **Examples**: `"6.5 Creedmoor"`, `".308 Winchester"`, `"6mm Creedmoor"`

### Properties

#### display_name
- **Type**: `str`
- **Description**: Human-readable cartridge type name
- **Returns**: `name` if set, else `"Unknown Type"`

```python
cart_type = CartridgeTypeModel(name="6.5 Creedmoor")
print(cart_type.display_name)
# Output: "6.5 Creedmoor"
```

### Methods

#### from_supabase_record()
```python
@classmethod
def from_supabase_record(cls, record: dict) -> CartridgeTypeModel
```

#### from_supabase_records()
```python
@classmethod
def from_supabase_records(cls, records: List[dict]) -> List[CartridgeTypeModel]
```

#### to_dict()
```python
def to_dict(self) -> dict
```

---

## Usage Examples

### Creating a CartridgeModel

```python
# From database record (with embedded bullet data)
record = {
    "id": "cart-123",
    "owner_id": None,  # Global cartridge
    "make": "Federal",
    "model": "Gold Medal",
    "bullet_id": "bullet-456",
    "cartridge_type": "6.5 Creedmoor",
    # Embedded bullet data from JOIN
    "bullet_manufacturer": "Hornady",
    "bullet_model": "ELD Match",
    "bullet_weight_grains": 147.0,
    "ballistic_coefficient_g7": 0.351,
    # ...
}

cartridge = CartridgeModel.from_supabase_record(record)
```

### Accessing Nested Bullet Data

```python
# No separate bullet API call needed - data is embedded
print(f"Cartridge: {cartridge.display_name}")
print(f"Bullet: {cartridge.bullet_display}")
print(f"BC (G7): {cartridge.ballistic_coefficient_g7}")
print(f"Weight: {cartridge.bullet_weight_grains}gr")
print(f"Caliber: {cartridge.bore_diameter_land_mm}mm")
```

### Checking Ownership

```python
if cartridge.is_global:
    print("Factory load - visible to all users")
    print("Read-only for regular users")
elif cartridge.is_user_owned:
    print(f"Custom load - owned by user {cartridge.owner_id}")
    print("Owner can edit/delete")
```

### Validation

```python
# Check if cartridge is complete
if not cartridge.is_complete():
    missing = cartridge.get_missing_mandatory_fields()
    print(f"Cannot save - missing: {', '.join(missing)}")
else:
    # Save to database
    save_cartridge(cartridge)
```

### Display in UI

```python
# Format for dropdown/list
for cartridge in cartridges:
    ownership_badge = "🌐" if cartridge.is_global else "👤"
    label = f"{ownership_badge} {cartridge.display_name}"
    sublabel = f"  {cartridge.bullet_display}"

    display_option(label, sublabel, value=cartridge.id)

# Output:
# 🌐 Federal Gold Medal (6.5 Creedmoor)
#   Hornady ELD Match 147gr
# 👤 Custom Load Match (6.5 Creedmoor)
#   Sierra MatchKing 140gr
```

---

## Typed Composite Pattern

CartridgeModel demonstrates the **typed composite model** pattern from `docs/architecture/06-design-decisions.md`:

1. **Performance**: Database JOIN brings in bullet data
2. **Type Safety**: Bullet fields are typed (not opaque dict)
3. **Convenience**: No separate API call for bullet details
4. **Modularity**: Still depends on bullets module for types

---

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Examples](examples.md) - Practical usage examples
- [Module README](README.md) - Overview and integration

---

**Models Version**: 1.0
**Last Updated**: 2025-10-18