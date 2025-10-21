# Metric System Philosophy

## Overview

ChronoLog uses the metric system internally for all data storage and calculations. Imperial units are only used at the edges (import/export and UI display) based on user preferences.

## Core Principle

**All interior processing and storage is based on the metric system. Only swap at the edge when importing files that use imperial or in the UI if the user preferences require it.**

## Why Metric Internally?

1. **Consistency**: Single system of units throughout backend
2. **Simplicity**: No conversion bugs in business logic
3. **International**: Metric is the scientific standard
4. **Precision**: Avoids accumulated rounding errors from repeated conversions

---

## The Edge Conversion Pattern

```
IMPERIAL (Edge)  →  METRIC (Internal)  →  IMPERIAL (Edge, if needed)
    ↓                      ↓                       ↓
  Import              Models/Services          Display
  Device Files        Database                 UI (user preference)
```

### Left Edge: Import (Imperial → Metric)

When data enters the system in imperial units, convert immediately:

```python
# garmin/garmin_import.py (device adapter)
def import_garmin_excel(file_path: str) -> ChronographSession:
    """Import Garmin data (in fps) and convert to metric (m/s)"""
    df = pd.read_excel(file_path)

    # Garmin provides velocity in fps (feet per second)
    fps_values = df['Velocity (fps)'].tolist()

    # Convert to metric BEFORE creating models
    mps_values = [fps * 0.3048 for fps in fps_values]  # fps → m/s

    # Store metric values
    measurements = [
        ChronographMeasurement(velocity_mps=v) for v in mps_values
    ]

    return ChronographSession(measurements=measurements)
```

**Key point**: Conversion happens in the **device adapter**, not in models or services.

---

### Center: Internal (Always Metric)

Models, services, and database always use metric:

```python
# chronograph/models.py
@dataclass
class ChronographMeasurement:
    """Measurement model - always metric internally."""
    id: str
    velocity_mps: float  # meters per second (NOT fps!)
    energy_joules: float  # joules (NOT foot-pounds!)

    def calculate_kinetic_energy(self, bullet_mass_grams: float) -> float:
        """Calculate kinetic energy. All inputs/outputs are metric."""
        mass_kg = bullet_mass_grams / 1000
        return 0.5 * mass_kg * (self.velocity_mps ** 2)  # Returns joules
```

**Database schema**:
```sql
CREATE TABLE chronograph_measurements (
    id UUID PRIMARY KEY,
    velocity_mps FLOAT NOT NULL,  -- meters per second
    energy_joules FLOAT,           -- joules
    ...
);
```

**No imperial columns in database!**

---

### Right Edge: Display (Metric → Imperial, if user preference)

UI layer converts to imperial only if user prefers it:

```python
# chronograph/view_tab.py (UI layer)
import streamlit as st

def display_chronograph_measurement(measurement: ChronographMeasurement, user_prefs: dict):
    """Display measurement with unit conversion based on user preference."""

    if user_prefs.get('units') == 'imperial':
        # Convert for display only
        velocity_fps = measurement.velocity_mps / 0.3048
        st.write(f"Velocity: {velocity_fps:.1f} fps")
    else:
        # Display metric as-is
        st.write(f"Velocity: {measurement.velocity_mps:.1f} m/s")
```

**Key point**: Conversion happens in **UI formatters**, not in models.

---

## Unit Conversion Reference

### Velocity
```python
# Imperial → Metric
meters_per_second = feet_per_second * 0.3048

# Metric → Imperial
feet_per_second = meters_per_second / 0.3048
```

### Temperature
```python
# Imperial → Metric
celsius = (fahrenheit - 32) * 5/9

# Metric → Imperial
fahrenheit = (celsius * 9/5) + 32
```

### Pressure
```python
# Imperial → Metric
hectopascals = inches_of_mercury * 33.8639

# Metric → Imperial
inches_of_mercury = hectopascals / 33.8639
```

### Weight (Bullets)
```python
# Grains are standard in ballistics, but grams for physics
# Grains → Grams
grams = grains * 0.06479891

# Grams → Grains
grains = grams / 0.06479891

# Note: Bullet weights are commonly displayed in grains even in metric countries
# Store in database as grams, convert to grains for display
```

### Distance
```python
# Inches → Millimeters
millimeters = inches * 25.4

# Millimeters → Inches
inches = millimeters / 25.4

# Yards → Meters
meters = yards * 0.9144

# Meters → Yards
yards = meters / 0.9144
```

### Wind Speed
```python
# MPH → m/s
meters_per_second = miles_per_hour * 0.44704

# m/s → MPH
miles_per_hour = meters_per_second / 0.44704
```

---

## Special Case: Bullet Weights

Bullet weights are a special case because **grains** are the universal standard in ballistics, even in metric countries.

### Storage: Grams (Metric)
```python
# bullets/models.py
@dataclass
class BulletModel:
    weight_grams: float  # Stored as grams (metric)

    @property
    def weight_grains(self) -> float:
        """Display weight in grains (ballistics standard)."""
        return self.weight_grams / 0.06479891
```

### Import: Convert grains to grams
```python
# bullets/import.py
def import_bullet_data(manufacturer_data: dict) -> BulletModel:
    """Import bullet data, converting grains to grams."""
    weight_gr = manufacturer_data['weight_grains']  # From manufacturer
    weight_g = weight_gr * 0.06479891  # Convert to grams for storage

    return BulletModel(weight_grams=weight_g)
```

### Display: Show in grains
```python
# bullets/view_tab.py
def display_bullet(bullet: BulletModel):
    """Display bullet with weight in grains (standard)."""
    st.write(f"Weight: {bullet.weight_grains:.1f} gr")  # Show grains
```

**Rationale**: Grains are the ballistics standard worldwide. Store metric internally, but always display in grains.

---

## Column Headers Must Include Units

When displaying data, units must be in column headers, NOT in cell values.

**GOOD**:
```python
# UI display
df = pd.DataFrame([
    {'Velocity (m/s)': 850.5, 'Energy (J)': 2450},
    {'Velocity (m/s)': 848.2, 'Energy (J)': 2438},
])
st.dataframe(df)
```

**BAD**:
```python
# Wrong - units in cell values
df = pd.DataFrame([
    {'Velocity': '850.5 m/s', 'Energy': '2450 J'},  # WRONG!
    {'Velocity': '848.2 m/s', 'Energy': '2438 J'},  # WRONG!
])
```

**Why**:
- Keeps data as numbers (can sort, filter, calculate)
- Clearer presentation
- Easier to change units dynamically
- Prevents parsing issues

---

## Rules for Models and Services

### Rule 1: Models Never Store Imperial

**GOOD**:
```python
@dataclass
class WeatherMeasurement:
    temp_c: float  # Celsius
    pressure_hpa: float  # Hectopascals
    wind_mps: float  # Meters per second
```

**BAD**:
```python
@dataclass
class WeatherMeasurement:
    temp_f: float  # WRONG - imperial in model!
    pressure_inhg: float  # WRONG!
```

---

### Rule 2: Services Never Handle Conversions

**GOOD**:
```python
# weather/service.py
class WeatherService:
    def create_measurement(self, data: dict, user_id: str) -> WeatherMeasurement:
        """Create weather measurement. Data must already be in metric."""
        # Assumes data is already metric
        return WeatherMeasurement(
            temp_c=data['temp_c'],  # Already Celsius
            pressure_hpa=data['pressure_hpa'],  # Already hPa
        )
```

**BAD**:
```python
# weather/service.py
class WeatherService:
    def create_measurement(self, data: dict, user_id: str) -> WeatherMeasurement:
        """WRONG - service should not handle conversions!"""
        # Converting in service - WRONG!
        temp_c = (data['temp_f'] - 32) * 5/9  # WRONG!
        return WeatherMeasurement(temp_c=temp_c)
```

**Why**: Conversion logic belongs in device adapters (import) or UI formatters (display), not services.

---

### Rule 3: Device Adapters Handle Import Conversions

**GOOD**:
```python
# weather/kestrel/kestrel_adapter.py
class KestrelAdapter:
    """Adapter for Kestrel weather meters (outputs imperial)."""

    def parse_kestrel_csv(self, csv_path: str) -> List[WeatherMeasurement]:
        """Parse Kestrel CSV and convert to metric."""
        df = pd.read_csv(csv_path)

        measurements = []
        for _, row in df.iterrows():
            # Kestrel outputs imperial - convert to metric
            temp_f = row['Temperature (F)']
            temp_c = (temp_f - 32) * 5/9  # Convert to Celsius

            pressure_inhg = row['Pressure (inHg)']
            pressure_hpa = pressure_inhg * 33.8639  # Convert to hPa

            measurements.append(WeatherMeasurement(
                temp_c=temp_c,  # Stored as metric
                pressure_hpa=pressure_hpa
            ))

        return measurements
```

**Location**: `weather/kestrel/kestrel_adapter.py` (device-specific adapter)

---

### Rule 4: UI Formatters Handle Display Conversions

**GOOD**:
```python
# weather/ui_formatters.py
def format_temperature(temp_c: float, user_prefs: dict) -> str:
    """Format temperature based on user preference."""
    if user_prefs.get('units') == 'imperial':
        temp_f = (temp_c * 9/5) + 32
        return f"{temp_f:.1f} °F"
    else:
        return f"{temp_c:.1f} °C"
```

**Location**: `weather/ui_formatters.py` (UI layer)

---

## Testing Unit Conversions

### Test Adapters (Import)

```python
def test_kestrel_adapter_converts_to_metric():
    """Verify Kestrel adapter converts imperial to metric."""
    adapter = KestrelAdapter()

    # Kestrel file has imperial units
    measurements = adapter.parse_kestrel_csv('test_data_imperial.csv')

    # Verify stored as metric
    assert measurements[0].temp_c == pytest.approx(21.1, abs=0.1)  # 70°F → ~21.1°C
    assert measurements[0].pressure_hpa == pytest.approx(1013, abs=1)  # 29.92 inHg → ~1013 hPa
```

### Test Formatters (Display)

```python
def test_ui_formatter_converts_to_imperial():
    """Verify UI formatter converts metric to imperial for display."""
    measurement = WeatherMeasurement(temp_c=21.1, pressure_hpa=1013)

    user_prefs = {'units': 'imperial'}
    formatted = format_temperature(measurement.temp_c, user_prefs)

    assert formatted == "70.0 °F"  # 21.1°C → 70°F
```

### Test Models (Always Metric)

```python
def test_models_store_metric():
    """Verify models always store metric units."""
    measurement = WeatherMeasurement(temp_c=21.1, pressure_hpa=1013)

    # Models always metric
    assert measurement.temp_c == 21.1
    assert measurement.pressure_hpa == 1013

    # No imperial fields
    assert not hasattr(measurement, 'temp_f')
    assert not hasattr(measurement, 'pressure_inhg')
```

---

## Summary

**Metric Internally**:
- All models store metric
- All services use metric
- All database columns are metric
- All calculations are metric

**Imperial at Edges**:
- Device adapters convert imperial → metric on import
- UI formatters convert metric → imperial on display (if user prefers)

**Special Cases**:
- Bullet weights: Store as grams, display as grains (ballistics standard)

**Rules**:
- Models NEVER store imperial
- Services NEVER handle conversions
- Adapters handle import conversions
- Formatters handle display conversions
- Column headers include units
- Cell values are numbers (no units)

**Result**: Clean, consistent backend with flexible display options.

---

## Next Steps

- [Design Decisions](06-design-decisions.md) - Architectural choices
- [Common Patterns](../integration/common-patterns.md) - Implementation examples
- [Data Flow](03-data-flow.md) - How units flow through the system