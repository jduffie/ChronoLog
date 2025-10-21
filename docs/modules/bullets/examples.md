# Bullets Module Examples

## Overview

This document provides pseudocode examples showing common usage patterns for the bullets module API.

All examples assume you have initialized the API:

```python
from bullets import BulletsAPI

api = BulletsAPI(supabase_client)
```

---

## Reading Bullets

### Example 1: Get All Bullets

Retrieve the complete bullet catalog.

```python
# Get all bullets
bullets = api.get_all_bullets()

# Display count
print(f"Total bullets in catalog: {len(bullets)}")

# Iterate through bullets
for bullet in bullets:
    print(bullet.display_name)
    # Sierra MatchKing - 168.0gr - 7.62mm
    # Hornady ELD-M - 147.0gr - 6.5mm
    # ...
```

---

### Example 2: Get Specific Bullet

Retrieve a bullet by its ID.

```python
bullet_id = "123e4567-e89b-12d3-a456-426614174000"

bullet = api.get_bullet_by_id(bullet_id)

if bullet:
    print(f"Found: {bullet.display_name}")
    print(f"  Manufacturer: {bullet.manufacturer}")
    print(f"  Weight: {bullet.weight_grains}gr")
    print(f"  BC (G7): {bullet.ballistic_coefficient_g7}")
    print(f"  Caliber: {bullet.bore_diameter_land_mm}mm")
else:
    print("Bullet not found")
```

---

### Example 3: Batch Load Bullets

Load multiple bullets efficiently (for cartridge display).

```python
# You have cartridges with bullet IDs
cartridge_bullet_ids = [
    "id-1",
    "id-2",
    "id-3"
]

# Load all bullets in one query
bullets = api.get_bullets_by_ids(cartridge_bullet_ids)

# Create lookup map
bullets_by_id = {b.id: b for b in bullets}

# Use with cartridges
for cartridge in cartridges:
    bullet = bullets_by_id.get(cartridge.bullet_id)
    if bullet:
        print(f"{cartridge.name}: {bullet.display_name}")
```

---

## Filtering Bullets

### Example 4: Filter by Manufacturer

Get all bullets from a specific manufacturer.

```python
# Get all Sierra bullets
sierra_bullets = api.filter_bullets(manufacturer="Sierra")

print(f"Found {len(sierra_bullets)} Sierra bullets")

for bullet in sierra_bullets:
    print(f"  {bullet.model} - {bullet.weight_grains}gr")
```

---

### Example 5: Filter by Weight

Get all bullets of a specific weight.

```python
# Get all 168 grain bullets
heavy_bullets = api.filter_bullets(weight_grains=168)

print(f"Found {len(heavy_bullets)} 168gr bullets")

for bullet in heavy_bullets:
    print(f"  {bullet.manufacturer} {bullet.model}")
```

---

### Example 6: Filter by Caliber

Get all bullets for a specific caliber.

```python
# Get all .308 (7.62mm) bullets
caliber_308_bullets = api.filter_bullets(bore_diameter_mm=7.62)

print(f"Found {len(caliber_308_bullets)} .308 bullets")

for bullet in caliber_308_bullets:
    print(f"  {bullet.display_name}")
```

---

### Example 7: Combined Filters

Use multiple filters together.

```python
# Get Sierra 168gr .308 bullets
specific_bullets = api.filter_bullets(
    manufacturer="Sierra",
    bore_diameter_mm=7.62,
    weight_grains=168
)

print(f"Found {len(specific_bullets)} matching bullets")

for bullet in specific_bullets:
    print(f"  {bullet.model}")
    print(f"    BC (G7): {bullet.ballistic_coefficient_g7}")
    print(f"    SD: {bullet.sectional_density}")
```

---

## Populating UI Dropdowns

### Example 8: Manufacturer Dropdown

Get unique manufacturers for a dropdown.

```python
manufacturers = api.get_unique_manufacturers()

# Create dropdown options
for mfr in manufacturers:
    display_dropdown_option(mfr)

# Example output:
# [ ] Berger
# [ ] Hornady
# [ ] Nosler
# [ ] Sierra
```

---

### Example 9: Caliber Dropdown

Get unique calibers for filtering.

```python
calibers = api.get_unique_bore_diameters()

# Create dropdown with display names
for caliber_mm in calibers:
    # Convert to common caliber names for display
    display_name = format_caliber(caliber_mm)
    display_dropdown_option(display_name, value=caliber_mm)

# Example output:
# [ ] .223 (5.56mm)
# [ ] 6.5mm
# [ ] .308 (7.62mm)
# [ ] 9mm
```

---

### Example 10: Weight Dropdown

Get unique weights for filtering.

```python
weights = api.get_unique_weights()

# Create dropdown
for weight in weights:
    display_dropdown_option(f"{weight} gr", value=weight)

# Example output:
# [ ] 55 gr
# [ ] 69 gr
# [ ] 77 gr
# [ ] 147 gr
# [ ] 168 gr
```

---

## Cascading Filters (UI Pattern)

### Example 11: Manufacturer → Caliber → Weight

Progressive filtering based on user selections.

```python
# Step 1: User selects manufacturer
selected_manufacturer = user_selects_manufacturer()

# Get calibers for that manufacturer
manufacturer_bullets = api.filter_bullets(manufacturer=selected_manufacturer)
available_calibers = unique([b.bore_diameter_land_mm for b in manufacturer_bullets])

# Step 2: User selects caliber
selected_caliber = user_selects_from(available_calibers)

# Get weights for that manufacturer + caliber
caliber_bullets = api.filter_bullets(
    manufacturer=selected_manufacturer,
    bore_diameter_mm=selected_caliber
)
available_weights = unique([b.weight_grains for b in caliber_bullets])

# Step 3: User selects weight
selected_weight = user_selects_from(available_weights)

# Get final filtered bullets
final_bullets = api.filter_bullets(
    manufacturer=selected_manufacturer,
    bore_diameter_mm=selected_caliber,
    weight_grains=selected_weight
)

# Display results
display_bullets(final_bullets)
```

---

## Integration with Other Modules

### Example 12: Loading Bullets for Cartridges

When displaying cartridges, you need bullet data.

```python
from cartridges import CartridgesAPI
from bullets import BulletsAPI

cartridges_api = CartridgesAPI(supabase_client)
bullets_api = BulletsAPI(supabase_client)

# Get all cartridges (already have bullet data via join)
cartridges = cartridges_api.get_all_cartridges()

# Each cartridge already has nested bullet
for cartridge in cartridges:
    # CartridgeModel has a nested BulletModel
    bullet = cartridge.bullet

    print(f"Cartridge: {cartridge.make} {cartridge.model}")
    print(f"  Bullet: {bullet.display_name}")
    print(f"  BC (G7): {bullet.ballistic_coefficient_g7}")
```

**Note**: Cartridges module already joins bullet data, so you usually don't need to call BulletsAPI separately. This example shows the data is available.

---

### Example 13: DOPE Session Bullet Access

Accessing bullet data in DOPE sessions.

```python
from dope import DopeAPI

dope_api = DopeAPI(supabase_client)

# Get DOPE session (has nested bullet via cartridge)
session = dope_api.get_session_by_id(session_id, user_id)

# Access bullet directly (flattened in DopeSessionModel)
bullet = session.bullet

print(f"DOPE Session: {session.display_name}")
print(f"  Bullet: {bullet.display_name}")
print(f"  BC (G7): {bullet.ballistic_coefficient_g7}")
print(f"  Weight: {bullet.weight_grains}gr")

# Also accessible via cartridge
same_bullet = session.cartridge.bullet
assert bullet.id == same_bullet.id
```

---

## Ballistic Calculations

### Example 14: Using BC for Trajectory

Use bullet data for ballistic calculations.

```python
bullet = api.get_bullet_by_id(bullet_id)

# Use G7 BC for modern boat-tail bullets
bc_g7 = bullet.ballistic_coefficient_g7

if bc_g7:
    # Pass to trajectory calculator
    trajectory = calculate_trajectory(
        bc=bc_g7,
        bc_type="G7",
        weight_grains=bullet.weight_grains,
        velocity_mps=initial_velocity
    )

    print(f"Drop at 1000m: {trajectory.drop_at_distance(1000)} meters")
else:
    # Fall back to G1 if G7 not available
    bc_g1 = bullet.ballistic_coefficient_g1
    # ... use G1
```

---

### Example 15: Twist Rate Compatibility

Check if a bullet is suitable for a rifle's barrel twist.

```python
bullet = api.get_bullet_by_id(bullet_id)
rifle_twist_rate = 10.0  # 1:10 twist

# Check minimum required twist
if bullet.min_req_twist_rate_in_per_rev:
    if rifle_twist_rate <= bullet.min_req_twist_rate_in_per_rev:
        print("✓ Bullet is stable in this barrel")
    else:
        print("✗ Bullet may not stabilize")
        print(f"  Requires 1:{bullet.min_req_twist_rate_in_per_rev} or faster")
        print(f"  Rifle has 1:{rifle_twist_rate}")

# Check preferred twist
if bullet.pref_twist_rate_in_per_rev:
    if rifle_twist_rate <= bullet.pref_twist_rate_in_per_rev:
        print("✓ Using preferred twist rate")
    else:
        print("Consider faster twist for optimal accuracy")
```

---

## Display Formatting

### Example 16: Format for Table Display

Format bullet data for display in a table.

```python
bullets = api.filter_bullets(manufacturer="Sierra")

# Create table rows
table_rows = []
for bullet in bullets:
    row = {
        'Model': bullet.model,
        'Weight (gr)': bullet.weight_grains,
        'Caliber (mm)': bullet.bore_diameter_land_mm,
        'BC (G7)': bullet.ballistic_coefficient_g7 or "N/A",
        'SD': bullet.sectional_density or "N/A",
    }
    table_rows.append(row)

# Display in UI
display_table(table_rows)
```

---

### Example 17: Imperial Unit Conversion (Display Only)

Convert metric to imperial for display (if user prefers).

```python
bullet = api.get_bullet_by_id(bullet_id)

# Bullet stores metric internally
caliber_mm = bullet.bore_diameter_land_mm  # 7.62

# Convert for display if user prefers imperial
user_prefers_imperial = get_user_preference()

if user_prefers_imperial:
    caliber_inches = caliber_mm / 25.4  # 0.300
    display_text = f".{int(caliber_inches * 1000)} ({caliber_mm}mm)"
    # Display: ".300 (7.62mm)"
else:
    display_text = f"{caliber_mm}mm"
    # Display: "7.62mm"

print(f"Caliber: {display_text}")
```

---

## Error Handling

### Example 18: Handle Not Found

Handle cases where bullet doesn't exist.

```python
bullet_id = user_provided_bullet_id()

bullet = api.get_bullet_by_id(bullet_id)

if not bullet:
    display_error("Bullet not found. It may have been deleted.")
    return

# Continue with bullet data
process_bullet(bullet)
```

---

### Example 19: Handle Database Errors

Handle database connection issues.

```python
try:
    bullets = api.get_all_bullets()
    display_bullets(bullets)

except Exception as e:
    log_error(f"Failed to load bullets: {e}")
    display_error("Unable to load bullet catalog. Please try again.")
```

---

## Admin Operations (Admin Only)

### Example 20: Create New Bullet

Add a new bullet to the catalog (admin only).

```python
# Admin only - not exposed in regular user API

bullet_data = {
    "user_id": admin_user_id,
    "manufacturer": "Sierra",
    "model": "MatchKing",
    "weight_grains": 168,
    "bullet_diameter_groove_mm": 7.82,
    "bore_diameter_land_mm": 7.62,
    "ballistic_coefficient_g7": 0.243,
    "sectional_density": 0.253,
    "data_source_name": "Sierra Bullets",
}

bullet = api.create_bullet(bullet_data)

print(f"Created: {bullet.display_name}")
print(f"  ID: {bullet.id}")
```

---

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Models](models.md) - Data model specifications
- [Module README](README.md) - Overview and integration

---

**Examples Version**: 1.0
**Last Updated**: 2025-10-18