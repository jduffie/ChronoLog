# Bullets Module

## Overview

The bullets module manages the global catalog of bullet specifications. This is an **admin-maintained, read-only catalog** accessible to all users.

Bullets are referenced by cartridges, which are in turn referenced by DOPE sessions. The bullets module provides ballistic data (BC, sectional density, etc.) needed for trajectory calculations.

## Purpose

- Maintain centralized catalog of bullet specifications
- Provide ballistic coefficients (G1, G7) for trajectory calculations
- Track physical specifications (weight, diameter, length)
- Support filtering and searching for bullet selection

## Data Ownership

**Admin-Owned (Global)**:
- All bullets are maintained by administrators
- All users can read the bullet catalog
- Users cannot create, update, or delete bullets
- No user_id filtering on read operations

## Key Entities

### BulletModel

Represents a specific bullet with complete ballistic specifications.

**Key fields**:
- `manufacturer`: Bullet manufacturer (e.g., "Sierra", "Hornady")
- `model`: Bullet model name (e.g., "MatchKing", "ELD-M")
- `weight_grains`: Bullet weight in grains (ballistics standard)
- `ballistic_coefficient_g1`: BC using G1 drag model
- `ballistic_coefficient_g7`: BC using G7 drag model (more accurate for modern bullets)
- `bullet_diameter_groove_mm`: Bullet diameter (groove) in millimeters
- `bore_diameter_land_mm`: Bore diameter (land) in millimeters
- `sectional_density`: Weight-to-diameter ratio (penetration indicator)

All measurements are stored in **metric units** internally.

## Module Structure

```
bullets/
├── models.py           # BulletModel dataclass
├── service.py          # BulletsService (database operations)
├── protocols.py        # BulletsAPIProtocol (type contract)
├── api.py              # BulletsAPI facade (Phase 3)
├── __init__.py         # Module exports (Phase 3)
├── view_tab.py         # Streamlit UI for viewing bullets
├── create_tab.py       # Streamlit UI for creating bullets (admin only)
└── test_bullets.py     # Unit tests
```

## API

See [API Reference](api-reference.md) for detailed API documentation.

**Public methods** (all users):
- `get_all_bullets()` - Get complete bullet catalog
- `get_bullet_by_id(bullet_id)` - Get specific bullet
- `get_bullets_by_ids(bullet_ids)` - Batch load bullets
- `filter_bullets(manufacturer, bore_diameter_mm, weight_grains)` - Filter bullets
- `get_unique_manufacturers()` - Get list of manufacturers
- `get_unique_bore_diameters()` - Get list of bore diameters
- `get_unique_weights()` - Get list of weights

**Admin methods** (admin only):
- `create_bullet(bullet_data)` - Add new bullet to catalog
- `update_bullet(bullet_id, bullet_data)` - Update bullet specification
- `delete_bullet(bullet_id)` - Remove bullet from catalog

## Usage

### Reading Bullets (All Users)

```python
from bullets import BulletsAPI

# Initialize API
api = BulletsAPI(supabase_client)

# Get all bullets
all_bullets = api.get_all_bullets()

# Get specific bullet
bullet = api.get_bullet_by_id(bullet_id)

# Filter bullets
sierra_168gr = api.filter_bullets(
    manufacturer="Sierra",
    weight_grains=168
)

# Get dropdown options
manufacturers = api.get_unique_manufacturers()
weights = api.get_unique_weights()
```

### Integration with Other Modules

**Cartridges Module**:
- Cartridges reference bullets via `bullet_id` foreign key
- When querying cartridges, bullet data is joined automatically
- `CartridgeModel` contains nested `BulletModel`

**DOPE Module**:
- DOPE sessions reference cartridges (which contain bullets)
- `DopeSessionModel` has nested `bullet` field (via cartridge join)
- Bullet specs used for ballistic calculations

## Data Model

See [Models Documentation](models.md) for complete field specifications.

**Metric Units**:
- Diameters: millimeters
- Length: millimeters
- Weight: stored as grams internally, displayed as grains

**Display Units**:
- Weight: Always shown in grains (ballistics standard)
- Diameters: Can show in mm or inches based on user preference

## Testing

```bash
# Run bullets unit tests
python -m pytest bullets/test_bullets.py

# Test specific function
python -m pytest bullets/test_bullets.py::test_get_all_bullets
```

## Examples

See [Examples](examples.md) for common usage patterns and pseudocode.

## Next Steps

- [API Reference](api-reference.md) - Detailed API documentation
- [Models](models.md) - Data model specifications
- [Examples](examples.md) - Usage examples

---

**Module Type**: Data Source (Admin-Owned)
**Dependencies**: None (fully independent)
**Used By**: Cartridges, DOPE
**Status**: Stable