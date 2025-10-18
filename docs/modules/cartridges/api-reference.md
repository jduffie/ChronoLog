# Cartridges API Reference

Complete API documentation for the cartridges module with dual ownership model (global + user-owned).

---

## Initialization

```python
from cartridges import CartridgesAPI

api = CartridgesAPI(supabase_client)
```

---

## Public Methods (All Users)

### get_all_cartridges()

Get all cartridges accessible to a user (global + user-owned).

**Signature:**
```python
def get_all_cartridges(self, user_id: str) -> List[CartridgeModel]
```

**Parameters:**
- `user_id` (str): User's ID for filtering user-owned cartridges

**Returns:**
- `List[CartridgeModel]`: All accessible cartridges with bullet details joined

**Raises:**
- `Exception`: If database query fails

**Example:**
```python
cartridges = api.get_all_cartridges(user_id)
print(f"Found {len(cartridges)} cartridges")

for cartridge in cartridges:
    ownership = "Global" if cartridge.is_global else "Custom"
    print(f"{cartridge.display_name} [{ownership}]")
    print(f"  Bullet: {cartridge.bullet_display}")
```

---

### get_cartridge_by_id()

Get a specific cartridge by ID with bullet details.

**Signature:**
```python
def get_cartridge_by_id(
    self, cartridge_id: str, user_id: str
) -> Optional[CartridgeModel]
```

**Parameters:**
- `cartridge_id` (str): UUID of the cartridge
- `user_id` (str): User's ID for access control

**Returns:**
- `Optional[CartridgeModel]`: Cartridge if found and accessible, None otherwise

**Raises:**
- `Exception`: If database query fails

**Access Control:**
Returns cartridge only if:
- It's global (owner_id is NULL), OR
- It's owned by the user (owner_id equals user_id)

**Example:**
```python
cartridge = api.get_cartridge_by_id(cartridge_id, user_id)

if cartridge:
    print(f"Cartridge: {cartridge.display_name}")
    print(f"Bullet: {cartridge.bullet_display}")
    print(f"Type: {cartridge.cartridge_type}")
    print(f"BC (G7): {cartridge.ballistic_coefficient_g7}")
else:
    print("Cartridge not found or not accessible")
```

---

### get_cartridges_by_ids()

Get multiple cartridges by IDs (batch operation).

**Signature:**
```python
def get_cartridges_by_ids(
    self, cartridge_ids: List[str], user_id: str
) -> List[CartridgeModel]
```

**Parameters:**
- `cartridge_ids` (List[str]): List of cartridge UUIDs
- `user_id` (str): User's ID for access control

**Returns:**
- `List[CartridgeModel]`: Found cartridges (may be fewer than requested)

**Raises:**
- `Exception`: If database query fails

**Performance:**
More efficient than calling `get_cartridge_by_id()` in a loop.

**Example:**
```python
# Load cartridges for multiple DOPE sessions
session_cartridge_ids = ["id1", "id2", "id3"]
cartridges = api.get_cartridges_by_ids(session_cartridge_ids, user_id)

# Create lookup map
cartridges_by_id = {c.id: c for c in cartridges}

# Use with sessions
for session in sessions:
    cartridge = cartridges_by_id.get(session.cartridge_id)
    if cartridge:
        print(f"{session.name}: {cartridge.display_name}")
```

---

### filter_cartridges()

Filter cartridges by various criteria.

**Signature:**
```python
def filter_cartridges(
    self,
    user_id: str,
    make: Optional[str] = None,
    model: Optional[str] = None,
    cartridge_type: Optional[str] = None,
    bullet_id: Optional[str] = None,
) -> List[CartridgeModel]
```

**Parameters:**
- `user_id` (str): User's ID for access control
- `make` (Optional[str]): Filter by exact manufacturer name
- `model` (Optional[str]): Filter by exact model name
- `cartridge_type` (Optional[str]): Filter by exact cartridge type
- `bullet_id` (Optional[str]): Filter by specific bullet ID

**Returns:**
- `List[CartridgeModel]`: Filtered cartridges with bullet details

**Raises:**
- `Exception`: If database query fails

**Filter Logic:**
- All parameters are optional
- Multiple filters use AND logic
- Returns only accessible cartridges (global + user-owned)

**Example:**
```python
# Get all Federal cartridges
federal = api.filter_cartridges(user_id, make="Federal")

# Get all 6.5 Creedmoor cartridges
creedmoor = api.filter_cartridges(user_id, cartridge_type="6.5 Creedmoor")

# Get Federal 6.5 Creedmoor Gold Medal
specific = api.filter_cartridges(
    user_id,
    make="Federal",
    model="Gold Medal",
    cartridge_type="6.5 Creedmoor"
)
```

---

### get_cartridge_types()

Get list of all available cartridge types from lookup table.

**Signature:**
```python
def get_cartridge_types(self) -> List[str]
```

**Returns:**
- `List[str]`: Sorted list of cartridge type names

**Raises:**
- `Exception`: If database query fails

**Use Case:**
Populate UI dropdowns for cartridge type selection.

**Example:**
```python
types = api.get_cartridge_types()

for cart_type in types:
    display_dropdown_option(cart_type)

# Example output:
# .223 Remington
# .308 Winchester
# 6.5 Creedmoor
# 6mm Creedmoor
```

---

### get_unique_makes()

Get list of unique cartridge manufacturers.

**Signature:**
```python
def get_unique_makes(self, user_id: str) -> List[str]
```

**Parameters:**
- `user_id` (str): User's ID for filtering

**Returns:**
- `List[str]`: Sorted list of unique manufacturer names

**Raises:**
- `Exception`: If database query fails

**Example:**
```python
makes = api.get_unique_makes(user_id)

for make in makes:
    display_filter_option(make)

# Example output:
# Custom Load
# Federal
# Hornady
# Winchester
```

---

### get_unique_models()

Get list of unique cartridge model names.

**Signature:**
```python
def get_unique_models(self, user_id: str) -> List[str]
```

**Parameters:**
- `user_id` (str): User's ID for filtering

**Returns:**
- `List[str]`: Sorted list of unique model names

**Raises:**
- `Exception`: If database query fails

**Example:**
```python
models = api.get_unique_models(user_id)

for model in models:
    display_filter_option(model)

# Example output:
# Gold Medal
# Match
# Premium
# Superformance
```

---

## User Methods (User-Owned Cartridges)

### create_user_cartridge()

Create a new user-owned cartridge.

**Signature:**
```python
def create_user_cartridge(
    self, cartridge_data: dict, user_id: str
) -> CartridgeModel
```

**Parameters:**
- `cartridge_data` (dict): Cartridge fields
  - `make` (str, required): Manufacturer name
  - `model` (str, required): Model name
  - `bullet_id` (str, required): UUID of bullet
  - `cartridge_type` (str, required): Cartridge type
  - `data_source_name` (str, optional): Source name
  - `data_source_link` (str, optional): Source URL
- `user_id` (str): User's ID (will be set as owner_id)

**Returns:**
- `CartridgeModel`: Created cartridge with generated ID

**Raises:**
- `Exception`: If creation fails or validation fails

**Ownership:**
Automatically sets `owner_id = user_id`, making this a user-owned cartridge visible only to the creator.

**Example:**
```python
cartridge_data = {
    "make": "Custom Load",
    "model": "Match",
    "bullet_id": bullet_id,
    "cartridge_type": "6.5 Creedmoor",
    "data_source_name": "My handload data",
}

cartridge = api.create_user_cartridge(cartridge_data, user_id)

print(f"Created: {cartridge.display_name}")
print(f"ID: {cartridge.id}")
print(f"Owner: {cartridge.owner_id}")  # Will equal user_id
```

---

### update_user_cartridge()

Update a user-owned cartridge.

**Signature:**
```python
def update_user_cartridge(
    self, cartridge_id: str, cartridge_data: dict, user_id: str
) -> CartridgeModel
```

**Parameters:**
- `cartridge_id` (str): UUID of cartridge to update
- `cartridge_data` (dict): Fields to update (same as create)
- `user_id` (str): User's ID (for ownership verification)

**Returns:**
- `CartridgeModel`: Updated cartridge

**Raises:**
- `Exception`: If update fails or user doesn't own cartridge

**Access Control:**
Only allows updating cartridges where `owner_id = user_id`.
Cannot update global cartridges.

**Example:**
```python
update_data = {
    "model": "Updated Match Load",
    "data_source_name": "Updated data",
}

cartridge = api.update_user_cartridge(cartridge_id, update_data, user_id)

print(f"Updated: {cartridge.display_name}")
```

---

### delete_user_cartridge()

Delete a user-owned cartridge.

**Signature:**
```python
def delete_user_cartridge(self, cartridge_id: str, user_id: str) -> bool
```

**Parameters:**
- `cartridge_id` (str): UUID of cartridge to delete
- `user_id` (str): User's ID (for ownership verification)

**Returns:**
- `bool`: True if deleted, False if not found or not owned

**Raises:**
- `Exception`: If delete fails or cartridge is referenced by DOPE sessions

**Access Control:**
Only allows deleting cartridges where `owner_id = user_id`.
Cannot delete global cartridges.

**Foreign Key Constraint:**
Cannot delete if cartridge is referenced by any DOPE sessions.

**Example:**
```python
deleted = api.delete_user_cartridge(cartridge_id, user_id)

if deleted:
    print("Cartridge deleted successfully")
else:
    print("Cartridge not found or not owned by user")
```

---

## Admin Methods (Global Cartridges)

### create_global_cartridge()

Create a new global cartridge (admin only).

**Signature:**
```python
def create_global_cartridge(self, cartridge_data: dict) -> CartridgeModel
```

**Parameters:**
- `cartridge_data` (dict): Same fields as create_user_cartridge

**Returns:**
- `CartridgeModel`: Created global cartridge

**Raises:**
- `Exception`: If creation fails

**Ownership:**
Automatically sets `owner_id = NULL`, making this visible to all users but editable only by admins.

**Authorization:**
Should be protected by authentication/authorization layer. Only admin users should be able to call this.

**Example:**
```python
# Admin only
cartridge_data = {
    "make": "Federal",
    "model": "Gold Medal",
    "bullet_id": bullet_id,
    "cartridge_type": "6.5 Creedmoor",
    "data_source_name": "Federal Catalog",
    "data_source_link": "https://federal.com",
}

cartridge = api.create_global_cartridge(cartridge_data)

print(f"Created global: {cartridge.display_name}")
print(f"Accessible to all users: {cartridge.is_global}")  # True
```

---

### update_global_cartridge()

Update a global cartridge (admin only).

**Signature:**
```python
def update_global_cartridge(
    self, cartridge_id: str, cartridge_data: dict
) -> CartridgeModel
```

**Parameters:**
- `cartridge_id` (str): UUID of cartridge to update
- `cartridge_data` (dict): Fields to update

**Returns:**
- `CartridgeModel`: Updated cartridge

**Raises:**
- `Exception`: If update fails or cartridge is not global

**Access Control:**
Only updates cartridges where `owner_id IS NULL`.

**Authorization:**
Should be protected by authentication/authorization layer.

**Example:**
```python
# Admin only
update_data = {
    "model": "Gold Medal Match",
    "data_source_link": "https://federal.com/updated",
}

cartridge = api.update_global_cartridge(cartridge_id, update_data)

print(f"Updated global: {cartridge.display_name}")
```

---

### delete_global_cartridge()

Delete a global cartridge (admin only).

**Signature:**
```python
def delete_global_cartridge(self, cartridge_id: str) -> bool
```

**Parameters:**
- `cartridge_id` (str): UUID of cartridge to delete

**Returns:**
- `bool`: True if deleted, False if not found

**Raises:**
- `Exception`: If delete fails or cartridge is referenced

**Access Control:**
Only deletes cartridges where `owner_id IS NULL`.

**Foreign Key Constraint:**
Cannot delete if cartridge is referenced by any DOPE sessions.

**Authorization:**
Should be protected by authentication/authorization layer.

**Example:**
```python
# Admin only
deleted = api.delete_global_cartridge(cartridge_id)

if deleted:
    print("Global cartridge deleted")
else:
    print("Cartridge not found")
```

---

## Type Safety

The API implements `CartridgesAPIProtocol` for compile-time type checking:

```python
from cartridges import CartridgesAPI, CartridgesAPIProtocol

# Type checker verifies API implements protocol
api: CartridgesAPIProtocol = CartridgesAPI(supabase_client)

# IDE provides autocomplete for all protocol methods
cartridges = api.get_all_cartridges(user_id)  # Type: List[CartridgeModel]
```

---

## Error Handling

All methods raise exceptions with descriptive messages:

```python
try:
    cartridge = api.get_cartridge_by_id(cartridge_id, user_id)
except Exception as e:
    log_error(f"Failed to fetch cartridge: {e}")
    display_error("Unable to load cartridge data")
```

Common errors:
- Database connection failures
- Access denied (user doesn't own cartridge)
- Foreign key violations (cartridge referenced by DOPE sessions)
- Invalid data (missing required fields)

---

## Next Steps

- [Models Documentation](models.md) - CartridgeModel specification
- [Examples](examples.md) - 20+ practical usage examples
- [Module README](README.md) - Overview and integration

---

**API Version**: 1.0
**Last Updated**: 2025-10-18