# ChronoLog Documentation

Welcome to the ChronoLog technical documentation. This documentation is designed to help developers, AI agents, and future contributors understand the system architecture and implementation patterns.

## Purpose

This documentation serves as:
1. **Architectural reference** for understanding system design
2. **Context for AI agents** working with the codebase
3. **Guide for adding new features** following established patterns
4. **Reference for modularization and API contracts**

## Quick Start

**New to ChronoLog?** Start here:

1. [DOPE System Overview](architecture/01-dope-system.md) - Understand what DOPE is and why it's central
2. [Data Sources](architecture/02-data-sources.md) - Learn about the 6 data source modules
3. [Common Patterns](integration/common-patterns.md) - See how to implement modules

**Want to add a feature?** Read:

1. [Common Patterns](integration/common-patterns.md) - Implementation templates
2. [Design Decisions](architecture/06-design-decisions.md) - Understand architectural choices
3. Relevant [Module Documentation](modules/) - Specific module details

---

## Documentation Structure

### Architecture Documents

Core architectural concepts and design decisions:

- **[01-dope-system.md](architecture/01-dope-system.md)**
  - What DOPE is and why it's the convergence point
  - DOPE vs chronograph distinction
  - Module responsibilities

- **[02-data-sources.md](architecture/02-data-sources.md)**
  - The 6 data source modules (chronograph, bullets, cartridges, rifles, weather, mapping)
  - Module independence and relationships
  - Data ownership models (user-owned vs admin-owned)

- **[03-data-flow.md](architecture/03-data-flow.md)**
  - How data moves through the system
  - Typical user workflows
  - Database-level joins and queries
  - Service layer communication

- **[04-user-isolation.md](architecture/04-user-isolation.md)**
  - Multi-tenant security model
  - User-owned vs admin-owned data patterns
  - Common security pitfalls and solutions

- **[05-metric-system.md](architecture/05-metric-system.md)**
  - Why metric internally, imperial at edges
  - Unit conversion patterns
  - Special cases (bullet weights in grains)

- **[06-design-decisions.md](architecture/06-design-decisions.md)**
  - Hybrid approach to cross-module data access
  - DOPE typed composite models
  - UI/Backend separation for framework flexibility

---

### Integration Guides

Practical implementation guidance:

- **[common-patterns.md](integration/common-patterns.md)**
  - Module structure template
  - Model class patterns (dataclasses)
  - Service layer patterns
  - Device adapters and UI formatters
  - Testing patterns

---

### Module Documentation

Detailed documentation for each module (to be completed in Phase 2):

- **[dope/](modules/dope/)** - DOPE aggregation and analytics
- **[chronograph/](modules/chronograph/)** - Velocity measurement import
- **[bullets/](modules/bullets/)** - Bullet specifications catalog
- **[cartridges/](modules/cartridges/)** - Cartridge configurations
- **[rifles/](modules/rifles/)** - Rifle profiles
- **[weather/](modules/weather/)** - Environmental measurements
- **[mapping/](modules/mapping/)** - Range locations (pending refactoring)

Each module will contain:
- `README.md` - Module overview
- `api-reference.md` - API contract documentation
- `models.md` - Data model specifications
- `examples.md` - Usage examples (pseudocode)

---

## Key Architectural Concepts

### DOPE as Convergence Point

DOPE (Data On Previous Engagement) is the central aggregation layer that brings together:
- Chronograph data (velocity measurements)
- Cartridges (with bullet specifications)
- Rifles (firearm configurations)
- Weather (environmental conditions)
- Ranges (location and distance)

**Why DOPE is special**: It's the ONLY module allowed to couple with other modules (via typed composite models). All other modules are fully independent.

See: [DOPE System](architecture/01-dope-system.md)

---

### Hybrid Data Access Pattern

ChronoLog uses different patterns for different module types:

**Independent Modules** (chronograph, rifles, weather, bullets, cartridges):
- No JOINs to other module tables
- Use batch loading APIs if cross-module data needed
- Fully independent and testable

**DOPE Module** (convergence point):
- Performs JOINs for performance
- Imports model classes from all source modules
- Creates typed composite models (DopeSessionModel)
- Explicit coupling is accepted here (it's DOPE's job)

See: [Design Decisions - Hybrid Approach](architecture/06-design-decisions.md#hybrid-approach-to-cross-module-data-access)

---

### UI/Backend Separation

ChronoLog is designed for future frontend framework flexibility:

**Backend** (UI-agnostic):
- Models, Services, APIs, Business Logic
- NEVER imports Streamlit
- Works with any UI framework

**UI Layer** (Streamlit-specific):
- `*_tab.py`, `view/*.py`, `ui_formatters.py`
- CAN import Streamlit
- Thin wrapper around API calls

**Migration path**: Keep backend untouched, swap out Streamlit for Vue/React.

See: [Design Decisions - UI/Backend Separation](architecture/06-design-decisions.md#ui-backend-separation)

---

### Data Ownership Models

ChronoLog has two data ownership patterns:

**User-Owned (Private)**:
- Chronograph sessions, rifles, weather, DOPE sessions
- Has `user_id` column, queries filter by it
- Each user sees only their own data

**Admin-Owned (Global, Read-Only)**:
- Bullets, cartridges
- No `user_id` column
- All users can read, only admin can write

See: [User Isolation](architecture/04-user-isolation.md)

---

### Metric System Internally

All internal storage and calculations use metric units:
- Velocity: m/s (not fps)
- Temperature: °C (not °F)
- Pressure: hPa (not inHg)
- Distance: meters (not yards)

Imperial units only at edges:
- **Import**: Device adapters convert imperial → metric
- **Display**: UI formatters convert metric → imperial (if user prefers)

**Exception**: Bullet weights stored as grams but always displayed in grains (ballistics standard).

See: [Metric System](architecture/05-metric-system.md)

---

## Development Workflow

### Adding a New Data Source Module

1. **Read architectural docs**:
   - [Data Sources](architecture/02-data-sources.md)
   - [Common Patterns](integration/common-patterns.md)
   - [Design Decisions](architecture/06-design-decisions.md)

2. **Create module structure**:
   ```
   new_module/
   ├── models.py           # Dataclass with from_supabase_record()
   ├── service.py          # Service with user_id filtering
   ├── protocols.py        # API contract (Phase 2)
   ├── api.py              # API facade (Phase 3)
   └── test_new_module.py  # Unit tests
   ```

3. **Follow patterns**:
   - Models store metric units
   - Services enforce user isolation (if user-owned)
   - No Streamlit imports in backend

4. **Integrate with DOPE** (if needed):
   - DOPE can import your models
   - Add foreign key in dope_sessions table
   - Update DopeSessionModel to include your data

---

### Adding a New Feature to Existing Module

1. **Understand current structure**:
   - Read module documentation in `docs/modules/[module]/`
   - Review existing code in module

2. **Maintain patterns**:
   - Add fields to models (metric units)
   - Add methods to service (user_id filtering)
   - Add tests

3. **Update documentation**:
   - Update module `api-reference.md`
   - Update `models.md` if data model changed
   - Add examples to `examples.md`

---

## Testing

All backend code must be testable without Streamlit:

```bash
# Backend tests should work without Streamlit installed
python -m pytest bullets/test_bullets.py
python -m pytest chronograph/test_chronograph.py
```

See: [Common Patterns - Testing](integration/common-patterns.md#pattern-8-testing)

---

## API Development Roadmap

This documentation supports the modularization effort:

**Phase 1** (✓ Complete): Foundation documentation
- Architecture docs
- Design decisions
- Common patterns

**Phase 2** (Next): API Contracts
- Define Python Protocol classes for each module
- Write API documentation

**Phase 3**: Implementation
- Implement API facades
- Migrate UI to use APIs

**Phase 4**: Validation
- Extract reference docs from code
- Validate with AI agents

---

## For AI Agents

If you're an AI agent working with this codebase:

1. **Start with DOPE**: Read [01-dope-system.md](architecture/01-dope-system.md) to understand the convergence point

2. **Understand data sources**: Read [02-data-sources.md](architecture/02-data-sources.md) to see what modules exist

3. **Follow patterns**: Read [common-patterns.md](integration/common-patterns.md) for implementation templates

4. **Respect boundaries**:
   - Independent modules stay independent (no JOINs)
   - DOPE can couple (it's the aggregator)
   - Backend never imports Streamlit
   - Always use metric units internally
   - Always filter by user_id for user-owned data

5. **Type safety**: Use proper model classes, not raw dicts. Import models from source modules when needed (DOPE can do this).

---

## Contributing

When adding documentation:

1. **Architecture docs**: Describe "why" and high-level concepts
2. **Module docs**: Describe "what" and API contracts
3. **Integration docs**: Describe "how" with practical examples
4. **Examples**: Use pseudocode, not actual implementation (unless showing pattern)

---

## Questions?

For questions about:
- **Architecture**: Read design decisions and data flow docs
- **Implementation**: Read common patterns
- **Specific module**: Read module documentation
- **Security**: Read user isolation doc
- **Units**: Read metric system doc

---

## Document Status

- **Architecture**: ✓ Complete
- **Integration**: ✓ Complete
- **Module Docs**: ⏳ Planned for Phase 2
- **API Contracts**: ⏳ Planned for Phase 2

Last updated: 2025-10-18