# Bullets Models Documentation

## Overview

The bullets module uses a single dataclass model: `BulletModel`. This model represents complete bullet specifications with ballistic data.

All field values are stored in **metric units** internally, following ChronoLog's metric system philosophy.

## BulletModel

Dataclass representing a bullet with complete ballistic specifications.

**Location**: `bullets/models.py`

### Class Definition

```python
@dataclass
class BulletModel:
    """Entity representing a bullet specification"""
    # ... fields ...
```

---

## Fields

### Identity Fields

#### id
- **Type**: `str`
- **Required**: Yes
- **Description**: UUID of the bullet
- **Example**: `"123e4567-e89b-12d3-a456-426614174000"`
- **Notes**: Auto-generated on creation

#### user_id
- **Type**: `str`
- **Required**: Yes
- **Description**: User ID of admin who created the bullet
- **Example**: `"auth0|507f1f77bcf86cd799439011"`
- **Notes**: For admin tracking only; does not affect access (bullets are global)

---

### Core Specification Fields

#### manufacturer
- **Type**: `str`
- **Required**: Yes
- **Description**: Bullet manufacturer name
- **Example**: `"Sierra"`, `"Hornady"`, `"Berger"`
- **Notes**: Case-sensitive, used for filtering

#### model
- **Type**: `str`
- **Required**: Yes
- **Description**: Bullet model/product name
- **Example**: `"MatchKing"`, `"ELD-M"`, `"Hybrid Target"`
- **Notes**: Combined with manufacturer for display

#### weight_grains
- **Type**: `float`
- **Required**: Yes
- **Unit**: Grains (gr)
- **Description**: Bullet weight
- **Example**: `168.0`, `175.0`, `180.0`
- **Notes**: **Exception to metric rule** - stored and displayed in grains (ballistics standard)

---

### Physical Dimension Fields

#### bullet_diameter_groove_mm
- **Type**: `float`
- **Required**: Yes
- **Unit**: Millimeters (mm)
- **Description**: Bullet diameter at the groove (widest part)
- **Example**: `7.82` (for .308/7.62mm bullets)
- **Notes**: Metric internally, may display as inches in UI

#### bore_diameter_land_mm
- **Type**: `float`
- **Required**: Yes
- **Unit**: Millimeters (mm)
- **Description**: Bore diameter at the land (narrowest part) - **defines the caliber**
- **Example**: `7.62` (for .308/7.62mm bullets)
- **Notes**: Used for caliber identification, filtering, and display name

#### bullet_length_mm
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Millimeters (mm)
- **Description**: Overall bullet length
- **Example**: `31.0`, `35.5`
- **Notes**: Affects stability and seating depth

---

### Ballistic Coefficient Fields

#### ballistic_coefficient_g1
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Dimensionless
- **Description**: Ballistic coefficient using G1 drag model
- **Example**: `0.462`, `0.505`
- **Notes**: Traditional BC model, less accurate for modern boat-tail bullets

#### ballistic_coefficient_g7
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Dimensionless
- **Description**: Ballistic coefficient using G7 drag model
- **Example**: `0.243`, `0.268`
- **Notes**: **Preferred for modern bullets** - more accurate for boat-tail designs

---

### Derived Fields

#### sectional_density
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Dimensionless
- **Description**: Weight-to-diameter ratio (indicator of penetration)
- **Example**: `0.253` (168gr .308)
- **Calculation**: `weight / (diameter^2 * 7000)`
- **Notes**: Higher SD = better penetration

---

### Barrel Twist Fields

#### min_req_twist_rate_in_per_rev
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Inches per revolution
- **Description**: Minimum twist rate required for stabilization
- **Example**: `10.0` (1:10 twist)
- **Notes**: **Imperial units** - twist rates are always expressed in inches

#### pref_twist_rate_in_per_rev
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Inches per revolution
- **Description**: Preferred/optimal twist rate
- **Example**: `8.0` (1:8 twist)
- **Notes**: May differ from minimum for optimal accuracy

---

### Metadata Fields

#### data_source_name
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Source of the bullet data
- **Example**: `"Sierra Bullets"`, `"Hornady Manual 11th Edition"`
- **Notes**: For reference and verification

#### data_source_url
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: URL to data source
- **Example**: `"https://www.sierrabullets.com/168gr-matchking"`
- **Notes**: For verification and updates

---

## Class Methods

### from_supabase_record()

Create a `BulletModel` from a Supabase database record.

**Signature**:
```python
@classmethod
def from_supabase_record(cls, record: dict) -> BulletModel
```

**Parameters**:
- `record` (dict): Dictionary from Supabase query result

**Returns**:
- `BulletModel`: Fully typed bullet instance

**Example**:
```python
record = {
    "id": "123",
    "user_id": "admin",
    "manufacturer": "Sierra",
    "model": "MatchKing",
    "weight_grains": 168,
    ...
}

bullet = BulletModel.from_supabase_record(record)
```

---

### from_supabase_records()

Batch convert multiple Supabase records to `BulletModel` instances.

**Signature**:
```python
@classmethod
def from_supabase_records(cls, records: List[dict]) -> List[BulletModel]
```

**Parameters**:
- `records` (List[dict]): List of dictionaries from Supabase

**Returns**:
- `List[BulletModel]`: List of typed bullet instances

**Example**:
```python
records = [record1, record2, record3]
bullets = BulletModel.from_supabase_records(records)
```

---

### to_dict()

Convert `BulletModel` to dictionary for database operations.

**Signature**:
```python
def to_dict(self) -> dict
```

**Returns**:
- `dict`: Dictionary with all fields (excludes `id` for inserts)

**Example**:
```python
bullet = BulletModel(...)
bullet_dict = bullet.to_dict()

# Use for database insert/update
response = supabase.table('bullets').insert(bullet_dict).execute()
```

---

## Properties

### display_name

Get a user-friendly display name for the bullet.

**Signature**:
```python
@property
def display_name(self) -> str
```

**Returns**:
- `str`: Formatted display name

**Format**: `"{manufacturer} {model} - {weight}gr - {caliber}mm"`

Where `{caliber}` is `bore_diameter_land_mm` (the caliber-defining diameter).

**Example**:
```python
bullet = BulletModel(
    manufacturer="Sierra",
    model="MatchKing",
    weight_grains=168,
    bore_diameter_land_mm=7.62,  # Caliber (.308)
    bullet_diameter_groove_mm=7.82
)

print(bullet.display_name)
# Output: "Sierra MatchKing - 168.0gr - 7.62mm"
```

**Note**: Uses `bore_diameter_land_mm` (not `bullet_diameter_groove_mm`) because bore diameter defines the caliber.

---

## Unit Conventions

### Metric (Internal Storage)

**Always metric**:
- Diameters: millimeters
- Length: millimeters
- All calculations in metric

### Special Cases

**Grains (weight)**:
- Stored as grains (not grams)
- Ballistics standard worldwide
- Exception to metric rule

**Inches (twist rate)**:
- Barrel twist always in inches per revolution
- Industry standard (1:10, 1:8, etc.)
- Not converted to metric

### Display Conversion

UI may convert for display based on user preference:
- Diameters: mm ↔ inches
- Length: mm ↔ inches
- Weight: always grains (no conversion)
- Twist rate: always inches (no conversion)

---

## Field Validation

### Required Field Constraints

```python
# These must always be provided
id: str  # Non-empty UUID
user_id: str  # Non-empty Auth0 ID
manufacturer: str  # Non-empty
model: str  # Non-empty
weight_grains: float  # > 0
bullet_diameter_groove_mm: float  # > 0
bore_diameter_land_mm: float  # > 0 (defines caliber)
```

### Optional Field Defaults

```python
# These default to None if not provided
bullet_length_mm: Optional[float] = None
ballistic_coefficient_g1: Optional[float] = None
ballistic_coefficient_g7: Optional[float] = None
sectional_density: Optional[float] = None
min_req_twist_rate_in_per_rev: Optional[float] = None
pref_twist_rate_in_per_rev: Optional[float] = None
data_source_name: Optional[str] = None
data_source_url: Optional[str] = None
```

---

## Usage Example

### Complete Bullet Creation

```python
from bullets.models import BulletModel

# Create bullet instance
bullet = BulletModel(
    id="123e4567-e89b-12d3-a456-426614174000",
    user_id="auth0|admin_user",
    manufacturer="Sierra",
    model="MatchKing",
    weight_grains=168.0,
    bullet_diameter_groove_mm=7.82,
    bore_diameter_land_mm=7.62,  # Defines .308 caliber
    bullet_length_mm=31.0,
    ballistic_coefficient_g1=0.462,
    ballistic_coefficient_g7=0.243,
    sectional_density=0.253,
    min_req_twist_rate_in_per_rev=10.0,
    pref_twist_rate_in_per_rev=8.0,
    data_source_name="Sierra Bullets",
    data_source_url="https://www.sierrabullets.com"
)

# Access fields
print(bullet.display_name)
# "Sierra MatchKing - 168.0gr - 7.62mm"

print(f"BC (G7): {bullet.ballistic_coefficient_g7}")
# "BC (G7): 0.243"

print(f"Caliber: {bullet.bore_diameter_land_mm}mm")
# "Caliber: 7.62mm"

# Convert to dict for database
bullet_dict = bullet.to_dict()
```

---

## Integration with Other Models

### CartridgeModel

Cartridges reference bullets via foreign key:

```python
@dataclass
class CartridgeModel:
    bullet_id: str  # FK to bullets table
    bullet: BulletModel  # Joined bullet data
```

When querying cartridges, bullet data is automatically joined.

### DopeSessionModel

DOPE sessions include bullet data via cartridge:

```python
@dataclass
class DopeSessionModel:
    cartridge: CartridgeModel  # Has nested bullet
    bullet: BulletModel  # Direct reference (same as cartridge.bullet)
```

DOPE composite models flatten the relationship for easier access.

---

## Next Steps

- [API Reference](api-reference.md) - Methods for working with bullets
- [Examples](examples.md) - Common usage patterns
- [Module README](README.md) - Overview and integration

---

**Model Version**: 1.0
**Location**: `bullets/models.py`
**Database Table**: `bullets`