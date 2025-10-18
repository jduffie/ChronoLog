# Cartridges Module Examples

Practical usage examples for the cartridges module with dual ownership model.

All examples assume:
```python
from cartridges import CartridgesAPI

api = CartridgesAPI(supabase_client)
user_id = current_user["id"]
```

---

## Reading Cartridges (All Users)

### Example 1: Get All Accessible Cartridges

```python
# Get both global and user-owned cartridges
cartridges = api.get_all_cartridges(user_id)

print(f"Total accessible cartridges: {len(cartridges)}")

for cartridge in cartridges:
    ownership = "Global" if cartridge.is_global else "Custom"
    print(f"[{ownership}] {cartridge.display_name}")
    print(f"  Bullet: {cartridge.bullet_display}")
```

### Example 2: Get Specific Cartridge with Bullet Details

```python
cartridge = api.get_cartridge_by_id(cartridge_id, user_id)

if cartridge:
    print(f"Cartridge: {cartridge.display_name}")
    print(f"Bullet: {cartridge.bullet_display}")
    print(f"Type: {cartridge.cartridge_type}")
    print(f"Ballistics: {cartridge.ballistic_data_summary}")
    print(f"Twist: {cartridge.twist_rate_recommendation}")
    print(f"Ownership: {'Global' if cartridge.is_global else 'Custom'}")
else:
    print("Cartridge not found or not accessible")
```

### Example 3: Filter by Manufacturer

```python
# Get all Federal cartridges
federal = api.filter_cartridges(user_id, make="Federal")

print(f"Found {len(federal)} Federal cartridges")
for cart in federal:
    print(f"  {cart.model} - {cart.bullet_display}")
```

### Example 4: Filter by Cartridge Type

```python
# Get all 6.5 Creedmoor cartridges
creedmoor = api.filter_cartridges(user_id, cartridge_type="6.5 Creedmoor")

print(f"Available 6.5 Creedmoor loads:")
for cart in creedmoor:
    ownership = "🌐" if cart.is_global else "👤"
    print(f"{ownership} {cart.make} {cart.model}")
```

### Example 5: Batch Load Cartridges

```python
# Load cartridges for multiple DOPE sessions
session_cart_ids = ["id1", "id2", "id3"]
cartridges = api.get_cartridges_by_ids(session_cart_ids, user_id)

# Create lookup map
carts_by_id = {c.id: c for c in cartridges}

# Use with sessions
for session in sessions:
    cart = carts_by_id.get(session.cartridge_id)
    if cart:
        print(f"{session.name}: {cart.display_name}")
```

---

## UI Integration

### Example 6: Populate Cartridge Selector

```python
cartridges = api.get_all_cartridges(user_id)

for cart in cartridges:
    # Visual indicators for ownership
    badge = "🌐 Global" if cart.is_global else "👤 Custom"
    label = f"{cart.display_name} [{badge}]"
    sublabel = f"  {cart.bullet_display}"

    dropdown_option(label, sublabel, value=cart.id)
```

### Example 7: Cascading Filters

```python
# Step 1: Select cartridge type
types = api.get_cartridge_types()
selected_type = user_selects(types)

# Step 2: Filter by manufacturer for that type
filtered = api.filter_cartridges(user_id, cartridge_type=selected_type)
makes = unique([c.make for c in filtered])
selected_make = user_selects(makes)

# Step 3: Show filtered cartridges
final = api.filter_cartridges(
    user_id,
    cartridge_type=selected_type,
    make=selected_make
)

display_cartridges(final)
```

---

## User-Owned Cartridges

### Example 8: Create Custom Cartridge

```python
# User creates their own handload
cartridge_data = {
    "make": "Custom Load",
    "model": "Match Load 1",
    "bullet_id": bullet_id,  # From bullets module
    "cartridge_type": "6.5 Creedmoor",
    "data_source_name": "My load development notes",
}

cartridge = api.create_user_cartridge(cartridge_data, user_id)

print(f"Created: {cartridge.display_name}")
print(f"ID: {cartridge.id}")
print(f"Owner: {cartridge.owner_id}")  # Equals user_id
print(f"Visible only to you: {cartridge.is_user_owned}")  # True
```

### Example 9: Update Custom Cartridge

```python
# User updates their own cartridge
update_data = {
    "model": "Match Load 1 - Updated",
    "data_source_name": "Load dev - final specs",
}

cartridge = api.update_user_cartridge(cartridge_id, update_data, user_id)
print(f"Updated: {cartridge.display_name}")
```

### Example 10: Delete Custom Cartridge

```python
# User deletes their own cartridge
# Note: Cannot delete if referenced by DOPE sessions

deleted = api.delete_user_cartridge(cartridge_id, user_id)

if deleted:
    print("Cartridge deleted successfully")
else:
    print("Not found or not owned by you")
```

### Example 11: Check Ownership Before Edit

```python
cartridge = api.get_cartridge_by_id(cartridge_id, user_id)

if cartridge.is_global:
    print("This is a factory load - cannot edit")
    show_readonly_view(cartridge)
elif cartridge.is_user_owned:
    print("This is your custom load - can edit")
    show_edit_form(cartridge)
```

---

## Admin Operations (Global Cartridges)

### Example 12: Create Global Cartridge

```python
# Admin creates factory load visible to all users
if is_admin(user):
    cartridge_data = {
        "make": "Federal",
        "model": "Gold Medal",
        "bullet_id": bullet_id,
        "cartridge_type": "6.5 Creedmoor",
        "data_source_name": "Federal Catalog 2024",
        "data_source_link": "https://federal.com",
    }

    cartridge = api.create_global_cartridge(cartridge_data)

    print(f"Created global: {cartridge.display_name}")
    print(f"Accessible to all: {cartridge.is_global}")  # True
    print(f"Owner: {cartridge.owner_id}")  # None
```

### Example 13: Update Global Cartridge

```python
# Admin updates factory load
if is_admin(user):
    update_data = {
        "model": "Gold Medal Match",
        "data_source_link": "https://federal.com/updated",
    }

    cartridge = api.update_global_cartridge(cartridge_id, update_data)
    print(f"Updated global: {cartridge.display_name}")
```

---

## Integration with Other Modules

### Example 14: Creating DOPE Session with Cartridge

```python
from dope import DopeAPI

dope_api = DopeAPI(supabase_client)

# Select cartridge for DOPE session
cartridges = api.get_all_cartridges(user_id)
selected_cartridge = user_selects(cartridges)

# Create DOPE session
session_data = {
    "cartridge_id": selected_cartridge.id,
    "rifle_id": rifle_id,
    # ... other fields
}

session = dope_api.create_session(session_data, user_id)

# Session now has nested cartridge data
print(f"Session using: {session.cartridge.display_name}")
print(f"With bullet: {session.cartridge.bullet_display}")
```

### Example 15: Displaying Cartridge in DOPE View

```python
# DOPE session has nested cartridge with bullet data
session = dope_api.get_session_by_id(session_id, user_id)

print(f"Cartridge: {session.cartridge.display_name}")
print(f"Bullet: {session.cartridge.bullet_display}")
print(f"BC (G7): {session.cartridge.ballistic_coefficient_g7}")
print(f"Weight: {session.cartridge.bullet_weight_grains}gr")
print(f"Ballistics: {session.cartridge.ballistic_data_summary}")
```

---

## Error Handling

### Example 16: Handle Access Denied

```python
try:
    cartridge = api.get_cartridge_by_id(cartridge_id, user_id)
    if not cartridge:
        print("Cartridge not found or not accessible")
except Exception as e:
    log_error(f"Failed to fetch cartridge: {e}")
    display_error("Unable to load cartridge")
```

### Example 17: Handle Delete With Foreign Key

```python
try:
    deleted = api.delete_user_cartridge(cartridge_id, user_id)
    if deleted:
        print("Cartridge deleted")
    else:
        print("Not found or not owned")
except Exception as e:
    if "foreign key" in str(e).lower():
        print("Cannot delete - cartridge is used in DOPE sessions")
    else:
        print(f"Delete failed: {e}")
```

---

## Common Patterns

### Example 18: Separate Global and Custom in UI

```python
cartridges = api.get_all_cartridges(user_id)

# Separate by ownership
global_carts = [c for c in cartridges if c.is_global]
custom_carts = [c for c in cartridges if c.is_user_owned]

# Display in sections
print("=== Factory Loads ===")
for cart in global_carts:
    print(f"  {cart.display_name}")

print("\n=== My Custom Loads ===")
for cart in custom_carts:
    print(f"  {cart.display_name}")
```

### Example 19: Check Before Creating Duplicate

```python
# Check if cartridge already exists
existing = api.filter_cartridges(
    user_id,
    make=make,
    model=model,
    cartridge_type=cartridge_type,
    bullet_id=bullet_id
)

if existing:
    print("Similar cartridge already exists:")
    for cart in existing:
        ownership = "Global" if cart.is_global else "Custom"
        print(f"  [{ownership}] {cart.display_name}")

    if not user_confirms("Create anyway?"):
        return

# Create new cartridge
cartridge = api.create_user_cartridge(cartridge_data, user_id)
```

### Example 20: Display with Edit Permissions

```python
cartridge = api.get_cartridge_by_id(cartridge_id, user_id)

# Show cartridge details
display_cartridge_info(cartridge)

# Show edit button only if allowed
if cartridge.is_user_owned:
    # User owns this - can edit
    show_edit_button(cartridge)
elif cartridge.is_global and is_admin(user):
    # Admin can edit global
    show_admin_edit_button(cartridge)
else:
    # Read-only
    show_readonly_indicator()
```

---

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Models](models.md) - Data model specifications
- [Module README](README.md) - Overview and integration

---

**Examples Version**: 1.0
**Last Updated**: 2025-10-18