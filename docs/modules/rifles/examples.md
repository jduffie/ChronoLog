# Rifles Module Examples

Practical examples for common use cases with the Rifles module.

## Table of Contents

- [Basic Operations](#basic-operations)
- [UI Integration](#ui-integration)
- [Cross-Module Integration](#cross-module-integration)
- [Advanced Patterns](#advanced-patterns)
- [Real-World Scenarios](#real-world-scenarios)

## Basic Operations

### Creating Your First Rifle

```python
from rifles import RiflesAPI

# Initialize API
api = RiflesAPI(supabase_client)
user_id = "user-123"

# Create a rifle with minimal info
rifle_data = {
    "name": "Remington 700",
    "cartridge_type": "6.5 Creedmoor"
}
rifle = api.create_rifle(rifle_data, user_id)
print(f"Created rifle: {rifle.id}")
```

### Creating a Detailed Rifle Profile

```python
# Create with full specifications
rifle_data = {
    "name": "Bergara B-14 HMR",
    "cartridge_type": "6.5 Creedmoor",
    "barrel_twist_ratio": "1:8",
    "barrel_length": "24 inches",
    "sight_offset": "1.5 inches",
    "trigger": "Bergara Performance Trigger 2.5lb",
    "scope": "Vortex Viper PST Gen II 5-25x50 FFP EBR-2C"
}
rifle = api.create_rifle(rifle_data, user_id)

# Display full details
print(f"Rifle: {rifle.display_name()}")
print(f"Barrel: {rifle.barrel_display()}")
print(f"Trigger: {rifle.trigger_display()}")
print(f"Optics: {rifle.optics_display()}")
```

### Getting All Rifles

```python
# Get all rifles for a user
rifles = api.get_all_rifles(user_id)

if rifles:
    print(f"Found {len(rifles)} rifles:")
    for rifle in rifles:
        print(f"  - {rifle.display_name()}")
else:
    print("No rifles found")
```

### Finding a Specific Rifle

```python
# By ID
rifle = api.get_rifle_by_id("rifle-123", user_id)

if rifle:
    print(f"Found: {rifle.name}")
else:
    print("Rifle not found")

# By name
rifle = api.get_rifle_by_name(user_id, "Remington 700")

if rifle:
    print(f"Found rifle ID: {rifle.id}")
else:
    print("No rifle with that name")
```

### Updating a Rifle

```python
# Update single field
updates = {"barrel_length": "26 inches"}
rifle = api.update_rifle(rifle.id, updates, user_id)
print(f"Updated barrel length: {rifle.barrel_length}")

# Update multiple fields
updates = {
    "scope": "Nightforce ATACR 7-35x56",
    "trigger": "TriggerTech Diamond 1.5lb",
    "sight_offset": "1.75 inches"
}
rifle = api.update_rifle(rifle.id, updates, user_id)
print("Updated rifle configuration")
```

### Deleting a Rifle

```python
# Delete rifle
if api.delete_rifle(rifle.id, user_id):
    print("Rifle deleted successfully")
else:
    print("Rifle not found or already deleted")

# Verify deletion
rifle = api.get_rifle_by_id(rifle.id, user_id)
assert rifle is None  # Rifle is gone
```

## UI Integration

### Rifle Selection Dropdown

```python
import streamlit as st

# Get all rifles
rifles = api.get_all_rifles(user_id)

# Create dropdown options
rifle_options = {r.display_name(): r.id for r in rifles}

# Streamlit dropdown
selected_name = st.selectbox(
    "Select Rifle",
    options=list(rifle_options.keys())
)

# Get selected rifle ID
selected_id = rifle_options[selected_name]
rifle = api.get_rifle_by_id(selected_id, user_id)
```

### Filtered Rifle List with Dropdowns

```python
import streamlit as st

# Get filter options
cartridge_types = ["All"] + api.get_unique_cartridge_types(user_id)
twist_ratios = ["All"] + api.get_unique_twist_ratios(user_id)

# Filter dropdowns
selected_type = st.selectbox("Cartridge Type", cartridge_types)
selected_twist = st.selectbox("Twist Ratio", twist_ratios)

# Apply filters
filtered_rifles = api.filter_rifles(
    user_id,
    cartridge_type=selected_type if selected_type != "All" else None,
    twist_ratio=selected_twist if selected_twist != "All" else None
)

# Display results
st.write(f"Found {len(filtered_rifles)} rifles")
for rifle in filtered_rifles:
    st.write(f"- {rifle.display_name()}")
```

### Rifle Profile Card

```python
import streamlit as st

def display_rifle_card(rifle):
    """Display a rifle profile card"""
    st.subheader(rifle.display_name())

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Barrel Specifications**")
        st.write(rifle.barrel_display())

        st.write("**Trigger**")
        st.write(rifle.trigger_display())

    with col2:
        st.write("**Optics**")
        st.write(rifle.optics_display())

        st.write("**Created**")
        st.write(rifle.created_at.strftime("%Y-%m-%d %H:%M") if rifle.created_at else "Unknown")

# Usage
rifle = api.get_rifle_by_id(rifle_id, user_id)
if rifle:
    display_rifle_card(rifle)
```

### Create Rifle Form

```python
import streamlit as st

st.subheader("Add New Rifle")

# Form fields
name = st.text_input("Rifle Name*", placeholder="e.g., Remington 700")

# Get cartridge types for dropdown
cartridge_types = api.get_unique_cartridge_types(user_id)
cartridge_type = st.selectbox(
    "Cartridge Type*",
    options=cartridge_types
)

# Optional fields
barrel_length = st.text_input(
    "Barrel Length",
    placeholder="e.g., 24 inches"
)
barrel_twist = st.text_input(
    "Barrel Twist Ratio",
    placeholder="e.g., 1:8"
)
scope = st.text_input(
    "Scope",
    placeholder="e.g., Vortex Viper PST 5-25x50"
)
trigger = st.text_input(
    "Trigger",
    placeholder="e.g., Timney 2-stage 2.5lb"
)
sight_offset = st.text_input(
    "Sight Offset",
    placeholder="e.g., 1.5 inches"
)

# Submit button
if st.button("Create Rifle"):
    if not name or not cartridge_type:
        st.error("Name and Cartridge Type are required")
    else:
        rifle_data = {"name": name, "cartridge_type": cartridge_type}

        # Add optional fields if provided
        if barrel_length:
            rifle_data["barrel_length"] = barrel_length
        if barrel_twist:
            rifle_data["barrel_twist_ratio"] = barrel_twist
        if scope:
            rifle_data["scope"] = scope
        if trigger:
            rifle_data["trigger"] = trigger
        if sight_offset:
            rifle_data["sight_offset"] = sight_offset

        try:
            rifle = api.create_rifle(rifle_data, user_id)
            st.success(f"Created rifle: {rifle.display_name()}")
        except Exception as e:
            st.error(f"Error creating rifle: {e}")
```

## Cross-Module Integration

### With Cartridges Module

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

print(f"\nCompatible cartridges for {rifle.name}:")
for cartridge in cartridges:
    print(f"  {cartridge.display_name}")
    print(f"    Bullet: {cartridge.bullet_manufacturer} {cartridge.bullet_model}")
    print(f"    Weight: {cartridge.bullet_weight_grains}gr")
```

### With Bullets Module

```python
from rifles import RiflesAPI
from bullets import BulletsAPI

rifles_api = RiflesAPI(supabase)
bullets_api = BulletsAPI(supabase)

# Get rifle
rifle = rifles_api.get_rifle_by_id(rifle_id, user_id)

# Find compatible bullets based on barrel twist
all_bullets = bullets_api.get_all_bullets(user_id)

compatible_bullets = [
    b for b in all_bullets
    if b.cartridge_type == rifle.cartridge_type
]

# Further filter by twist rate if available
if rifle.barrel_twist_ratio:
    twist_rate = float(rifle.barrel_twist_ratio.split(':')[1])

    # Filter by recommended twist rate
    optimal_bullets = [
        b for b in compatible_bullets
        if b.pref_twist_rate_in_per_rev and
           abs(b.pref_twist_rate_in_per_rev - twist_rate) < 1
    ]

    print(f"Optimal bullets for {rifle.barrel_twist_ratio} twist:")
    for bullet in optimal_bullets:
        print(f"  {bullet.manufacturer} {bullet.model} ({bullet.weight_grains}gr)")
```

### Rifle Selection for Chronograph Session

```python
from rifles import RiflesAPI

# User selects rifle for new chronograph session
rifles = rifles_api.get_all_rifles(user_id)

# Display rifle options
print("Select rifle for session:")
for i, rifle in enumerate(rifles, 1):
    print(f"{i}. {rifle.display_name()}")
    print(f"   Barrel: {rifle.barrel_display()}")

# User selects rifle
rifle_choice = int(input("Enter number: ")) - 1
selected_rifle = rifles[rifle_choice]

# Create chronograph session with rifle data
session_data = {
    "rifle_name": selected_rifle.name,
    "rifle_id": selected_rifle.id,
    "cartridge_type": selected_rifle.cartridge_type,
    "barrel_length": selected_rifle.barrel_length,
    "barrel_twist": selected_rifle.barrel_twist_ratio,
    # ... other chronograph session fields
}
```

## Advanced Patterns

### Bulk Rifle Import

```python
import csv

# Load rifles from CSV
def import_rifles_from_csv(csv_path, user_id):
    """Import rifles from CSV file"""
    rifles = []

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rifle_data = {
                "name": row["name"],
                "cartridge_type": row["cartridge_type"],
            }

            # Add optional fields if present
            if row.get("barrel_length"):
                rifle_data["barrel_length"] = row["barrel_length"]
            if row.get("barrel_twist_ratio"):
                rifle_data["barrel_twist_ratio"] = row["barrel_twist_ratio"]
            if row.get("scope"):
                rifle_data["scope"] = row["scope"]
            if row.get("trigger"):
                rifle_data["trigger"] = row["trigger"]

            try:
                rifle = api.create_rifle(rifle_data, user_id)
                rifles.append(rifle)
                print(f"Imported: {rifle.display_name()}")
            except Exception as e:
                print(f"Error importing {row['name']}: {e}")

    return rifles

# Usage
imported_rifles = import_rifles_from_csv("rifles.csv", user_id)
print(f"\nImported {len(imported_rifles)} rifles")
```

### Rifle Comparison Tool

```python
def compare_rifles(rifle_ids, user_id):
    """Compare multiple rifles side-by-side"""
    rifles = [api.get_rifle_by_id(rid, user_id) for rid in rifle_ids]
    rifles = [r for r in rifles if r]  # Filter out None

    if len(rifles) < 2:
        print("Need at least 2 rifles to compare")
        return

    print("\nRifle Comparison:")
    print("-" * 80)

    # Header
    print(f"{'Attribute':<20}", end="")
    for rifle in rifles:
        print(f"{rifle.name[:15]:<20}", end="")
    print()
    print("-" * 80)

    # Compare attributes
    attrs = [
        ("Cartridge Type", "cartridge_type"),
        ("Barrel Length", "barrel_length"),
        ("Twist Ratio", "barrel_twist_ratio"),
        ("Scope", "scope"),
        ("Trigger", "trigger"),
    ]

    for label, attr in attrs:
        print(f"{label:<20}", end="")
        for rifle in rifles:
            value = getattr(rifle, attr) or "N/A"
            print(f"{str(value)[:15]:<20}", end="")
        print()

# Usage
compare_rifles(["rifle-1", "rifle-2", "rifle-3"], user_id)
```

### Smart Rifle Recommendations

```python
def recommend_rifle_for_cartridge(cartridge_type, user_id):
    """Recommend rifles compatible with a cartridge"""
    # Get all rifles
    all_rifles = api.get_all_rifles(user_id)

    # Filter by cartridge type
    compatible = [
        r for r in all_rifles
        if r.cartridge_type == cartridge_type
    ]

    if not compatible:
        print(f"No rifles found for {cartridge_type}")
        print("\nAvailable calibers:")
        types = api.get_unique_cartridge_types(user_id)
        for t in types:
            print(f"  - {t}")
        return None

    # Sort by completeness (more specs = better)
    def completeness_score(rifle):
        optional_fields = [
            rifle.barrel_length,
            rifle.barrel_twist_ratio,
            rifle.scope,
            rifle.trigger,
            rifle.sight_offset
        ]
        return sum(1 for f in optional_fields if f)

    compatible.sort(key=completeness_score, reverse=True)

    print(f"\nRecommended rifles for {cartridge_type}:")
    for rifle in compatible[:3]:  # Top 3
        score = completeness_score(rifle)
        print(f"\n{rifle.display_name()} (Profile {score}/5):")
        print(f"  Barrel: {rifle.barrel_display()}")
        print(f"  Optics: {rifle.optics_display()}")

    return compatible[0]

# Usage
best_rifle = recommend_rifle_for_cartridge("6.5 Creedmoor", user_id)
```

## Real-World Scenarios

### Scenario 1: New Shooter Setup

```python
# New shooter adds their first rifle
print("Welcome! Let's add your rifle to ChronoLog.\n")

# Simple questionnaire
name = input("What's the rifle name/model? ")
caliber = input("What caliber? (e.g., 6.5 Creedmoor) ")
barrel_length = input("Barrel length? (e.g., 24 inches, or press Enter to skip) ")

# Create rifle
rifle_data = {
    "name": name,
    "cartridge_type": caliber
}

if barrel_length:
    rifle_data["barrel_length"] = barrel_length

rifle = api.create_rifle(rifle_data, user_id)
print(f"\n✓ Added {rifle.display_name()}")
print("You can add more details later in your rifle profile.")
```

### Scenario 2: Competition Shooter Tracking

```python
# Competition shooter tracks multiple identical rifles
# with different configurations

base_rifle = "Bergara B-14 HMR"

configurations = [
    {
        "name": f"{base_rifle} - Match",
        "cartridge_type": "6.5 Creedmoor",
        "scope": "Vortex Viper PST Gen II 5-25x50",
        "trigger": "TriggerTech Diamond 1.5lb"
    },
    {
        "name": f"{base_rifle} - Practice",
        "cartridge_type": "6.5 Creedmoor",
        "scope": "Vortex Diamondback 4-12x40",
        "trigger": "Factory trigger"
    }
]

for config in configurations:
    rifle = api.create_rifle(config, user_id)
    print(f"Created: {rifle.display_name()}")
```

### Scenario 3: Rifle Upgrade Tracking

```python
# Track upgrades to a rifle over time
rifle = api.get_rifle_by_name(user_id, "Remington 700")

# Upgrade trigger
print(f"Current trigger: {rifle.trigger_display()}")
updates = {"trigger": "TriggerTech Diamond 1.5lb"}
rifle = api.update_rifle(rifle.id, updates, user_id)
print(f"Upgraded trigger: {rifle.trigger_display()}")

# Upgrade scope
updates = {"scope": "Nightforce ATACR 7-35x56"}
rifle = api.update_rifle(rifle.id, updates, user_id)
print(f"Upgraded scope: {rifle.optics_display()}")

# Check last update time
print(f"Last updated: {rifle.updated_at}")
```

### Scenario 4: Multi-Caliber Collection Management

```python
# Organize rifles by caliber
rifles = api.get_all_rifles(user_id)

# Group by cartridge type
from collections import defaultdict
by_caliber = defaultdict(list)

for rifle in rifles:
    by_caliber[rifle.cartridge_type].append(rifle)

# Display collection
print("Rifle Collection by Caliber:")
print("=" * 50)

for caliber in sorted(by_caliber.keys()):
    rifles_in_caliber = by_caliber[caliber]
    print(f"\n{caliber} ({len(rifles_in_caliber)} rifles):")

    for rifle in rifles_in_caliber:
        print(f"  • {rifle.name}")
        print(f"    Barrel: {rifle.barrel_display()}")
```

## Error Handling Examples

### Handling Creation Errors

```python
def safe_create_rifle(rifle_data, user_id):
    """Create rifle with error handling"""
    try:
        rifle = api.create_rifle(rifle_data, user_id)
        print(f"✓ Created: {rifle.display_name()}")
        return rifle
    except Exception as e:
        print(f"✗ Error creating rifle: {e}")
        return None

# Usage
rifle_data = {"name": "Test Rifle", "cartridge_type": "6.5 Creedmoor"}
rifle = safe_create_rifle(rifle_data, user_id)
```

### Handling Not Found

```python
def get_rifle_or_prompt(rifle_id, user_id):
    """Get rifle or prompt to create if not found"""
    rifle = api.get_rifle_by_id(rifle_id, user_id)

    if not rifle:
        print(f"Rifle {rifle_id} not found.")
        create = input("Would you like to create a new rifle? (y/n) ")

        if create.lower() == 'y':
            # Prompt for rifle details
            name = input("Rifle name: ")
            caliber = input("Caliber: ")
            rifle_data = {"name": name, "cartridge_type": caliber}
            rifle = api.create_rifle(rifle_data, user_id)

    return rifle
```

## See Also

- [README](./README.md) - Module overview
- [API Reference](./api-reference.md) - Complete API documentation
- [Models Reference](./models.md) - Data model details