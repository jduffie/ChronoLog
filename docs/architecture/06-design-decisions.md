# Design Decisions

## Hybrid Approach to Cross-Module Data Access

### The Problem

Modules need data from other modules. Two approaches:

1. **JOINs**: Fast (single query) but breaks modularity and type safety
2. **API calls**: Modular and type-safe but slower (N+1 queries)

### The Solution: Hybrid Approach

**Rule**: Different modules have different responsibilities, so different coupling rules.

#### Independent Modules (Chronograph, Rifles, Weather, Bullets, Cartridges)

These modules are **fully independent**:
- No JOINs to other module tables
- No direct imports of other module models (except via shared protocols)
- If they need related data, use batch loading APIs

**Example**: If chronograph needed to display bullet data (hypothetically):
```python
# chronograph uses bullets API, not JOINs
sessions = chronograph_service.get_sessions(user_id)
cartridge_ids = [s.cartridge_id for s in sessions]
cartridges = cartridges_api.get_cartridges_by_ids(cartridge_ids)  # Batch load
```

#### DOPE Module (Convergence Point)

DOPE is **explicitly allowed to couple** with source modules:
- DOPE performs JOINs for performance
- DOPE imports model classes from all source modules for type safety
- DOPE creates composite/joined models using typed imports

**Rationale**:
- DOPE's entire purpose is to aggregate data from sources
- Performance matters for DOPE queries (users query sessions frequently)
- By making coupling explicit and typed, we maintain type safety

---

## DOPE Typed Composite Models

### Import Pattern

DOPE module directly imports models from source modules:

```python
# dope/models.py

# Explicit imports from source modules
from bullets.models import BulletModel
from cartridges.models import CartridgeModel
from rifles.models import Rifle
from chronograph.chronograph_session_models import ChronographSession
from weather.models import WeatherMeasurement
from mapping.range_models import Range  # When mapping refactor complete

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
```

**Key point**: DOPE imports are **one-way**. Source modules never import from DOPE.

---

### Composite Model Structure

```python
@dataclass
class DopeSessionModel:
    """
    Composite model representing a DOPE session with all joined data.

    This model is constructed from database JOINs for performance,
    but uses typed model classes from source modules for type safety.
    """

    # DOPE-owned fields (from dope_sessions table)
    id: str
    user_id: str
    created_at: datetime
    session_date: datetime
    notes: Optional[str]
    range_distance_meters: float

    # Foreign key IDs (stored in dope_sessions table)
    cartridge_id: str
    rifle_id: str
    chronograph_session_id: str
    weather_measurement_id: Optional[str]
    range_id: Optional[str]

    # Joined data from other modules (typed!)
    # These are populated from JOIN results but use proper model classes
    cartridge: CartridgeModel  # From cartridges module
    bullet: BulletModel        # From bullets module (via cartridge join)
    rifle: Rifle               # From rifles module
    chronograph_session: ChronographSession  # From chronograph module
    weather: Optional[WeatherMeasurement]    # From weather module
    range: Optional[Range]     # From mapping module (future)

    # Computed/display fields
    @property
    def display_name(self) -> str:
        """User-friendly session identifier"""
        return f"{self.session_date.strftime('%Y-%m-%d')} - {self.cartridge.display_name}"

    @property
    def bullet_weight_display(self) -> str:
        """Bullet weight with units (imperial for display)"""
        return f"{self.bullet.weight_grains} gr"

    @classmethod
    def from_supabase_joined_record(cls, record: dict) -> 'DopeSessionModel':
        """
        Construct from a JOIN query result.

        The record contains flattened data from multiple tables.
        We use source module model classes to parse their portions.
        """
        # Parse bullet data using BulletModel
        bullet = BulletModel.from_supabase_record({
            'id': record['bullet_id'],
            'manufacturer': record['bullet_manufacturer'],
            'model': record['bullet_model'],
            'weight_grains': record['bullet_weight_grains'],
            'bc_g1': record['bullet_bc_g1'],
            # ... other bullet fields
        })

        # Parse cartridge data using CartridgeModel
        # CartridgeModel already contains the bullet we just created
        cartridge = CartridgeModel(
            id=record['cartridge_id'],
            make=record['cartridge_make'],
            model=record['cartridge_model'],
            cartridge_type=record['cartridge_type'],
            bullet=bullet,  # Nested typed model
            # ... other cartridge fields
        )

        # Parse rifle data using Rifle model
        rifle = Rifle.from_supabase_record({
            'id': record['rifle_id'],
            'user_id': record['rifle_user_id'],
            'name': record['rifle_name'],
            'barrel_length_inches': record['rifle_barrel_length_inches'],
            # ... other rifle fields
        })

        # Parse chronograph session using ChronographSession model
        chrono = ChronographSession.from_supabase_record({
            'id': record['chronograph_session_id'],
            'user_id': record['chrono_user_id'],
            'session_name': record['chrono_session_name'],
            # ... other chronograph fields
        })

        # Parse weather if present
        weather = None
        if record.get('weather_measurement_id'):
            weather = WeatherMeasurement.from_supabase_record({
                'id': record['weather_measurement_id'],
                'temp_c': record['weather_temp_c'],
                'humidity_pct': record['weather_humidity_pct'],
                # ... other weather fields
            })

        # Construct the composite model
        return cls(
            id=record['id'],
            user_id=record['user_id'],
            created_at=record['created_at'],
            session_date=record['session_date'],
            notes=record.get('notes'),
            range_distance_meters=record['range_distance_meters'],
            cartridge_id=record['cartridge_id'],
            rifle_id=record['rifle_id'],
            chronograph_session_id=record['chronograph_session_id'],
            weather_measurement_id=record.get('weather_measurement_id'),
            range_id=record.get('range_id'),
            cartridge=cartridge,
            bullet=bullet,
            rifle=rifle,
            chronograph_session=chrono,
            weather=weather,
            range=None,  # TODO: when mapping refactored
        )
```

---

### Service Layer Usage

```python
# dope/service.py
from typing import List, Optional
from .models import DopeSessionModel

class DopeService:
    """
    DOPE service performs JOINs but returns typed composite models.
    """

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]:
        """
        Get all DOPE sessions for a user with all joined data.

        This performs a complex JOIN but returns fully typed models.
        """
        # Complex JOIN query (conceptual)
        query = self.supabase.from_('dope_sessions') \
            .select('''
                *,
                cartridges:cartridge_id (
                    *,
                    bullets:bullet_id (*)
                ),
                rifles:rifle_id (*),
                chronograph_sessions:chronograph_session_id (*),
                weather_measurements:weather_measurement_id (*)
            ''') \
            .eq('user_id', user_id)

        response = query.execute()

        # Convert to typed models
        return [
            DopeSessionModel.from_supabase_joined_record(record)
            for record in response.data
        ]

    def get_session_by_id(
        self,
        session_id: str,
        user_id: str
    ) -> Optional[DopeSessionModel]:
        """Get a single DOPE session with all joined data."""
        query = self.supabase.from_('dope_sessions') \
            .select('''
                *,
                cartridges:cartridge_id (
                    *,
                    bullets:bullet_id (*)
                ),
                rifles:rifle_id (*),
                chronograph_sessions:chronograph_session_id (*),
                weather_measurements:weather_measurement_id (*)
            ''') \
            .eq('id', session_id) \
            .eq('user_id', user_id) \
            .single()

        response = query.execute()

        if not response.data:
            return None

        return DopeSessionModel.from_supabase_joined_record(response.data)
```

---

### DOPE Measurement Model (Simpler)

```python
@dataclass
class DopeMeasurementModel:
    """
    Individual shot measurement within a DOPE session.

    Lighter model - doesn't need all the JOINs that session needs.
    """
    id: str
    dope_session_id: str
    shot_number: int
    velocity_mps: float

    # Usually measurements don't need joined data,
    # but if they did, same pattern applies

    @classmethod
    def from_supabase_record(cls, record: dict) -> 'DopeMeasurementModel':
        return cls(
            id=record['id'],
            dope_session_id=record['dope_session_id'],
            shot_number=record['shot_number'],
            velocity_mps=record['velocity_mps'],
        )
```

---

## Benefits of This Approach

### 1. Performance
- Single JOIN query for DOPE sessions (not N+1)
- Critical for user-facing DOPE queries

### 2. Type Safety
- IDE autocomplete works: `session.bullet.weight_grains`
- Type checker validates: can't access non-existent fields
- Refactoring safe: if BulletModel changes, DOPE code breaks at compile time

### 3. Explicit Coupling
- DOPE's imports make coupling visible
- Easy to see which modules DOPE depends on
- Source modules remain independent (no reverse dependencies)

### 4. Testable
```python
# In tests, can create composite models with proper types
def test_dope_session_display():
    bullet = BulletModel(manufacturer="Sierra", model="MatchKing", weight_grains=168, ...)
    cartridge = CartridgeModel(make="Federal", model="GMM", bullet=bullet, ...)
    rifle = Rifle(name="Bergara HMR", ...)

    session = DopeSessionModel(
        cartridge=cartridge,
        bullet=bullet,
        rifle=rifle,
        ...
    )

    assert session.display_name == "2025-10-18 - Federal GMM"
```

### 5. Maintainable
- If BulletModel adds a field, DopeSessionModel automatically has access
- Changes in source modules propagate via types
- No duplication of field definitions

---

## Trade-offs

### What We Gain
- DOPE performance (single query)
- Full type safety
- Clear separation: DOPE couples, others don't

### What We Accept
- DOPE has import dependencies on all source modules
- DOPE tests require source module models
- If source module models change, DOPE may need updates

### Why It's Worth It
DOPE's entire purpose is aggregation. Coupling is its job. By making it:
- **Explicit** (via imports)
- **Typed** (using real model classes)
- **Unidirectional** (sources don't know about DOPE)

We get the best of both worlds: performance + type safety.

---

## Alternative Considered: DTOs

We could create separate Data Transfer Objects:
```python
@dataclass
class DopeSessionDTO:
    bullet_manufacturer: str  # Flattened, untyped
    bullet_model: str
    # ... loses type safety
```

**Rejected because**:
- Loses type safety (no BulletModel methods/properties)
- Duplicates field definitions
- Harder to maintain
- Less discoverable for AI agents

By using actual model classes, we maintain the full power of the type system.

---

## Summary: Cross-Module Data Access

**Independent modules**: Stay independent, use batch APIs if needed
**DOPE module**: Performs JOINs, imports source models, creates typed composites
**Result**: Performance where it matters, modularity everywhere else, type safety throughout

---

# UI/Backend Separation

## The Requirement

**Goal**: Be able to migrate from Streamlit to a different frontend framework (Vue, React, etc.) without rewriting backend logic.

**Implication**: The backend (models, services, business logic, APIs) must have ZERO dependencies on Streamlit.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│  UI Layer (Streamlit-specific)          │  ← Can be replaced
│  - Pages (*_tab.py, view/*.py)          │
│  - Session state management             │
│  - Streamlit widgets                    │
│  - Display formatters (st.dataframe)    │
└─────────────────────────────────────────┘
              ↓ calls ↓
┌─────────────────────────────────────────┐
│  API Layer (UI-agnostic)                │  ← Stable contract
│  - Protocol classes (type contracts)    │
│  - Facade classes (BulletsAPI, etc.)    │
│  - Module exports (__init__.py)         │
└─────────────────────────────────────────┘
              ↓ calls ↓
┌─────────────────────────────────────────┐
│  Service Layer (UI-agnostic)            │  ← Backend logic
│  - Service classes (BulletsService)     │
│  - Business logic                       │
│  - Database operations                  │
└─────────────────────────────────────────┘
              ↓ uses ↓
┌─────────────────────────────────────────┐
│  Model Layer (UI-agnostic)              │  ← Domain entities
│  - Dataclasses (BulletModel, Rifle)     │
│  - Domain logic                         │
│  - Type definitions                     │
└─────────────────────────────────────────┘
              ↓ queries ↓
┌─────────────────────────────────────────┐
│  Data Layer (UI-agnostic)               │  ← Persistence
│  - Supabase client                      │
│  - Database schema                      │
└─────────────────────────────────────────┘
```

## Strict Rules

### Rule 1: Backend NEVER Imports Streamlit

**Backend** = Models, Services, APIs, Business Logic

**NEVER do this**:
```python
# BAD - in bullets/service.py
import streamlit as st

class BulletsService:
    def get_bullets(self):
        if 'bullets' not in st.session_state:  # WRONG!
            st.session_state.bullets = self.fetch_bullets()
```

**Why**:
- Creates hard dependency on Streamlit
- Can't swap UI framework without rewriting backend
- Can't reuse backend in CLI, API server, or other contexts

---

### Rule 2: UI Calls APIs, Not Services Directly

**GOOD** (after API layer is built):
```python
# streamlit_page.py
from bullets import BulletsAPI

def display_bullets_page(user_id: str):
    bullets_api = BulletsAPI(supabase_client)
    bullets = bullets_api.get_bullets()  # Clean API call

    # Streamlit-specific display
    st.dataframe(bullets)
```

**ACCEPTABLE** (current state, before API layer):
```python
# streamlit_page.py
from bullets.service import BulletsService

def display_bullets_page(user_id: str):
    service = BulletsService(supabase_client)
    bullets = service.get_all_bullets()  # Direct service call

    # Streamlit-specific display
    st.dataframe(bullets)
```

**BAD** (tight coupling):
```python
# streamlit_page.py
from bullets.service import BulletsService

def display_bullets_page():
    # Service reads from st.session_state - WRONG!
    service = BulletsService()
    bullets = service.get_bullets_from_session_state()
```

---

### Rule 3: Session State is UI-Only

**Session state** (st.session_state) belongs ONLY in UI layer.

**GOOD**:
```python
# bullets/view_tab.py (UI layer)
import streamlit as st
from bullets import BulletsAPI

def render_bullets_tab(user_id: str):
    # UI manages session state
    if 'bullets_filter' not in st.session_state:
        st.session_state.bullets_filter = None

    filter_value = st.text_input("Filter", value=st.session_state.bullets_filter)

    # Call backend with explicit parameters (not from session state)
    api = BulletsAPI(supabase_client)
    bullets = api.get_bullets(filter=filter_value)

    st.dataframe([b.to_dict() for b in bullets])
```

**BAD**:
```python
# bullets/service.py (backend layer)
import streamlit as st  # WRONG!

class BulletsService:
    def get_bullets(self):
        # Backend reading session state - WRONG!
        filter_value = st.session_state.get('bullets_filter')
        return self.supabase.from_('bullets').eq('model', filter_value).execute()
```

---

### Rule 4: Models Return Plain Data, UI Formats

**Models should NOT format for display**.

**GOOD**:
```python
# bullets/models.py (backend)
@dataclass
class BulletModel:
    weight_grains: float
    bc_g1: float

    def to_dict(self) -> dict:
        """Return plain dict for serialization."""
        return {
            'weight_grains': self.weight_grains,
            'bc_g1': self.bc_g1,
        }
```

```python
# bullets/ui_formatters.py (UI layer)
def format_bullet_for_display(bullet: BulletModel) -> dict:
    """Format bullet for Streamlit display."""
    return {
        'Weight': f"{bullet.weight_grains} gr",
        'BC (G1)': f"{bullet.bc_g1:.3f}",
    }
```

**BAD**:
```python
# bullets/models.py (backend)
@dataclass
class BulletModel:
    weight_grains: float

    def to_streamlit_dict(self) -> dict:  # WRONG!
        """Streamlit-specific formatting in model - WRONG!"""
        return {'Weight': f"{self.weight_grains} gr"}
```

---

### Rule 5: Business Logic is UI-Agnostic

Business logic should work with any UI (or no UI).

**GOOD**:
```python
# chronograph/business_logic.py (backend)
class SessionStatisticsCalculator:
    @staticmethod
    def calculate_statistics(velocities: List[float]) -> dict:
        """Calculate statistics from velocity list."""
        return {
            'mean': statistics.mean(velocities),
            'stdev': statistics.stdev(velocities),
            'extreme_spread': max(velocities) - min(velocities),
        }
```

```python
# chronograph/view_tab.py (UI)
def display_session_stats(session: ChronographSession):
    stats = SessionStatisticsCalculator.calculate_statistics(
        [m.velocity_mps for m in session.measurements]
    )

    # Streamlit-specific display
    st.metric("Mean Velocity", f"{stats['mean']:.2f} m/s")
    st.metric("SD", f"{stats['stdev']:.2f} m/s")
```

**BAD**:
```python
# chronograph/business_logic.py (backend)
import streamlit as st  # WRONG!

class SessionStatisticsCalculator:
    @staticmethod
    def display_statistics(velocities: List[float]):  # WRONG!
        """Business logic mixed with UI - WRONG!"""
        mean = statistics.mean(velocities)
        st.metric("Mean Velocity", f"{mean:.2f} m/s")  # WRONG!
```

---

## File Organization

### Backend (UI-agnostic)

```
bullets/
├── models.py           # Domain entities (NO streamlit)
├── service.py          # Business logic (NO streamlit)
├── protocols.py        # API contracts (NO streamlit)
├── api.py              # API facade (NO streamlit)
├── __init__.py         # Module exports (NO streamlit)
└── business_logic.py   # Pure functions (NO streamlit)
```

### UI Layer (Streamlit-specific)

```
bullets/
├── view_tab.py         # Streamlit UI (CAN import streamlit)
├── create_tab.py       # Streamlit UI (CAN import streamlit)
└── ui_formatters.py    # Display helpers (CAN import streamlit)
```

OR (alternative structure):
```
bullets/ui/
├── view.py
├── create.py
└── formatters.py
```

**Rule**: UI files can import from backend. Backend NEVER imports from UI.

---

## Migration Path to Vue/React

When migrating to a new UI:

### Step 1: Keep Backend (No Changes)
```
bullets/
├── models.py          # Keep as-is ✓
├── service.py         # Keep as-is ✓
├── protocols.py       # Keep as-is ✓
├── api.py             # Keep as-is ✓
└── __init__.py        # Keep as-is ✓
```

### Step 2: Replace UI Layer
```
bullets/
├── view_tab.py        # DELETE (Streamlit-specific)
├── create_tab.py      # DELETE (Streamlit-specific)
└── ui_formatters.py   # DELETE (Streamlit-specific)
```

### Step 3: Create New UI
```
frontend/vue/bullets/
├── BulletsListView.vue      # New Vue component
├── BulletCreateView.vue     # New Vue component
└── bulletFormatters.js      # New Vue formatters
```

### Step 4: Call Same APIs
```javascript
// Vue component
import { BulletsAPI } from '@/api/bullets'

export default {
  async created() {
    const api = new BulletsAPI(supabaseClient)
    this.bullets = await api.getBullets()  // Same API!
  }
}
```

**Result**: Backend logic untouched, only UI rewritten.

---

## Benefits

### 1. Framework Flexibility
- Swap Streamlit for Vue/React/Svelte without backend changes
- Run backend in different contexts (CLI, REST API, batch jobs)

### 2. Testability
- Test backend without Streamlit
- Mock UI components in backend tests
- Unit test business logic independently

### 3. Parallel Development
- Frontend team works on UI
- Backend team works on services
- Clear contract (API layer) between them

### 4. Reusability
- Backend can power multiple UIs simultaneously
- Same code for web app, mobile app, API server

---

## Enforcement

### Code Review Checklist

When reviewing backend code (models, services, APIs):
- [ ] No `import streamlit` statements
- [ ] No `st.session_state` access
- [ ] No Streamlit widgets (st.button, st.selectbox, etc.)
- [ ] No Streamlit display calls (st.write, st.dataframe, etc.)
- [ ] Functions take explicit parameters (not from session state)
- [ ] Returns plain Python types (not Streamlit components)

### Testing

Backend tests should run WITHOUT Streamlit installed:
```bash
# Should work even if streamlit not in environment
python -m pytest bullets/test_service.py
python -m pytest bullets/test_models.py
python -m pytest bullets/test_api.py
```

If backend test fails without Streamlit, you have a dependency problem.

---

## Current State vs Future State

### Current State (Before API Layer)
- Some UI code directly calls services ✓ (acceptable temporarily)
- Some `*_tab.py` files mix UI and logic ✗ (needs refactoring)
- Most models/services are UI-agnostic ✓ (good!)

### Future State (After API Layer)
- All UI calls APIs (not services directly) ✓
- All `*_tab.py` files are thin UI wrappers ✓
- All backend code 100% UI-agnostic ✓

---

## Summary: UI/Backend Separation

**Backend (UI-agnostic)**:
- Models, Services, APIs, Business Logic
- NEVER imports Streamlit
- Works with any UI framework

**UI Layer (Streamlit-specific)**:
- `*_tab.py`, `view/*.py`, `ui_formatters.py`
- CAN import Streamlit
- Thin wrapper around API calls

**Migration Path**:
- Keep backend untouched
- Delete Streamlit UI files
- Write new UI in Vue/React
- Call same backend APIs

**Result**: Future-proof architecture that supports framework flexibility