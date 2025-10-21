# Cartridges Module

## Overview

The **cartridges module** provides access to the ammunition cartridge specifications catalog with a dual ownership model:

- **Global cartridges** (admin-owned, owner_id=NULL): Pre-populated by admins, read-only for all users
- **User-owned cartridges** (owner_id=user_id): Custom loads created and managed by individual users

Each cartridge links to a bullet from the bullets module and includes manufacturer, model, and cartridge type information.

**Module Type**: Hybrid (Admin-Owned + User-Owned)
**Dependencies**: bullets (for bullet specifications)
**Database Tables**: `cartridges`, `cartridge_types`
**Primary Use**: Storing and retrieving ammunition specifications for DOPE sessions

---

## Key Concepts

### Dual Ownership Model

Unlike the bullets module (admin-only), cartridges supports TWO ownership modes:

1. **Global Cartridges** (owner_id = NULL):
   - Created by admins
   - Visible to ALL users
   - Read-only for regular users
   - Factory/commercial loads

2. **User-Owned Cartridges** (owner_id = user_id):
   - Created by users for their own use
   - Visible ONLY to the owner
   - Full CRUD by owner
   - Custom/handloads

### Data Integration

Cartridges integrate bullet data through database JOINs:
- CartridgeModel includes nested bullet fields
- Service layer performs JOIN with bullets table
- API returns typed CartridgeModel with bullet data embedded

This follows the **typed composite model** pattern from `docs/architecture/06-design-decisions.md`.

---

## Module Structure

```
cartridges/
├── __init__.py           # Public API exports
├── api.py                # CartridgesAPI facade (public interface)
├── protocols.py          # CartridgesAPIProtocol (type contract)
├── models.py             # CartridgeModel, CartridgeTypeModel
├── service.py            # CartridgeService (internal DB operations)
├── test_cartridges_api.py        # Unit tests
└── test_cartridges_integration.py # Integration tests
```

---

## Public API

### Importing

```python
from cartridges import CartridgesAPI, CartridgeModel, CartridgesAPIProtocol

# Initialize
api = CartridgesAPI(supabase_client)
```

### Core Operations

**Reading Cartridges** (all users):
```python
# Get all accessible cartridges (global + user-owned)
cartridges = api.get_all_cartridges(user_id)

# Get specific cartridge
cartridge = api.get_cartridge_by_id(cartridge_id, user_id)

# Filter cartridges
federal = api.filter_cartridges(user_id, make="Federal")
creedmoor = api.filter_cartridges(user_id, cartridge_type="6.5 Creedmoor")
```

**User-Owned Operations**:
```python
# Create custom cartridge
cartridge_data = {
    "make": "Custom Load",
    "model": "Match",
    "bullet_id": bullet_id,
    "cartridge_type": "6.5 Creedmoor",
}
cartridge = api.create_user_cartridge(cartridge_data, user_id)

# Update own cartridge
api.update_user_cartridge(cartridge_id, {"model": "Updated"}, user_id)

# Delete own cartridge
api.delete_user_cartridge(cartridge_id, user_id)
```

**Admin Operations** (global cartridges):
```python
# Create global cartridge (admin only)
cartridge = api.create_global_cartridge(cartridge_data)

# Update global cartridge (admin only)
api.update_global_cartridge(cartridge_id, update_data)

# Delete global cartridge (admin only)
api.delete_global_cartridge(cartridge_id)
```

---

## Integration with Other Modules

### Bullets Module

Every cartridge references a bullet:

```python
cartridge = api.get_cartridge_by_id(cartridge_id, user_id)

# Bullet data is embedded in CartridgeModel
print(f"Cartridge: {cartridge.display_name}")
print(f"Bullet: {cartridge.bullet_display}")
print(f"BC (G7): {cartridge.ballistic_coefficient_g7}")
print(f"Weight: {cartridge.bullet_weight_grains}gr")
```

The service layer performs the JOIN automatically - no separate API call needed.

### DOPE Module

DOPE sessions reference cartridges:

```python
# DOPE session has nested cartridge
session = dope_api.get_session_by_id(session_id, user_id)

# Cartridge data is embedded
cartridge = session.cartridge
print(f"Using: {cartridge.display_name}")
print(f"Bullet: {cartridge.bullet_display}")
```

See `docs/architecture/06-design-decisions.md` for the typed composite model pattern.

---

## Data Model

### CartridgeModel

Primary data model for cartridge specifications.

**Core Fields**:
- `id` (str): UUID
- `owner_id` (Optional[str]): NULL for global, user_id for user-owned
- `make` (str): Manufacturer name (e.g., "Federal")
- `model` (str): Model name (e.g., "Gold Medal")
- `bullet_id` (str): Foreign key to bullets table
- `cartridge_type` (str): Cartridge type (e.g., "6.5 Creedmoor")

**Embedded Bullet Fields** (from JOIN):
- `bullet_manufacturer`, `bullet_model`, `bullet_weight_grains`
- `ballistic_coefficient_g1`, `ballistic_coefficient_g7`
- `sectional_density`, `bore_diameter_land_mm`
- And more...

**Properties**:
- `display_name`: "Federal Gold Medal (6.5 Creedmoor)"
- `bullet_display`: "Hornady ELD Match 147gr"
- `is_global`: True if owner_id is NULL
- `is_user_owned`: True if owner_id is set
- `ballistic_data_summary`: "G1 BC: 0.697, G7 BC: 0.351, SD: 0.301"
- `twist_rate_recommendation`: "Min: 1:8\", Pref: 1:7.5\""

See [models.md](models.md) for complete specification.

---

## Ownership and Access Control

### Access Rules

| Operation | Global Cartridge | User-Owned Cartridge |
|-----------|------------------|---------------------|
| Read | All users | Owner only |
| Create | Admin only | Any user (for self) |
| Update | Admin only | Owner only |
| Delete | Admin only | Owner only |

### Implementation

The API automatically enforces access control:

```python
# get_all_cartridges returns global + user-owned
cartridges = api.get_all_cartridges(user_id)
# Returns: WHERE owner_id IS NULL OR owner_id = user_id

# get_cartridge_by_id verifies access
cartridge = api.get_cartridge_by_id(cartridge_id, user_id)
# Returns: WHERE id = cartridge_id AND (owner_id IS NULL OR owner_id = user_id)

# create_user_cartridge sets owner
cartridge = api.create_user_cartridge(data, user_id)
# Sets: owner_id = user_id

# create_global_cartridge sets NULL
cartridge = api.create_global_cartridge(data)  # Admin only
# Sets: owner_id = NULL
```

---

## UI Integration Patterns

### Cartridge Selector

Populate dropdown with accessible cartridges:

```python
cartridges = api.get_all_cartridges(user_id)

for cartridge in cartridges:
    display_label = f"{cartridge.display_name} - {cartridge.bullet_display}"
    ownership_badge = "🌐 Global" if cartridge.is_global else "👤 Custom"

    dropdown_option(
        label=f"{display_label} [{ownership_badge}]",
        value=cartridge.id
    )
```

### Filter UI

Cascading filters:

```python
# Step 1: Select cartridge type
types = api.get_cartridge_types()
selected_type = user_selects_from(types)

# Step 2: Filter by manufacturer
filtered = api.filter_cartridges(user_id, cartridge_type=selected_type)
makes = list(set(c.make for c in filtered))
selected_make = user_selects_from(makes)

# Step 3: Filter by model
final = api.filter_cartridges(
    user_id,
    cartridge_type=selected_type,
    make=selected_make
)
display_cartridges(final)
```

---

## Testing

### Unit Tests

Test API compliance and functionality with mocked dependencies:

```bash
python -m pytest cartridges/test_cartridges_api.py -v
```

### Integration Tests

Test against real Supabase database:

```bash
export SUPABASE_SERVICE_ROLE_KEY=your-key
python -m pytest cartridges/test_cartridges_integration.py -v -m integration
```

---

## Best Practices

1. **Always pass user_id**: All read operations require user_id for access control
2. **Use batch operations**: `get_cartridges_by_ids()` for loading multiple cartridges
3. **Check ownership**: Use `is_global` property to determine if user can edit
4. **Embedded bullet data**: No need to separately fetch bullets - already joined
5. **Filter before creating**: Check if cartridge exists before creating duplicate
6. **User-owned for custom loads**: Global for factory/commercial loads

---

## Common Patterns

See [examples.md](examples.md) for 20+ practical usage examples covering:
- Reading and filtering cartridges
- Creating user-owned cartridges
- Admin global cartridge management
- UI integration patterns
- Error handling

---

## API Reference

See [api-reference.md](api-reference.md) for complete API documentation with:
- All 13 public methods
- Parameter specifications
- Return types
- Error handling
- Usage examples

---

## Related Documentation

- [Architecture: Data Sources](../../architecture/02-data-sources.md) - Cartridges as data source
- [Architecture: Design Decisions](../../architecture/06-design-decisions.md) - Typed composite models
- [Integration: Common Patterns](../../integration/common-patterns.md) - Implementation patterns
- [Bullets Module](../bullets/README.md) - Related bullet specifications

---

**Module Version**: 1.0
**Last Updated**: 2025-10-18