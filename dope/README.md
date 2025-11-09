# DOPE Module

**Data On Previous Engagement** - The convergence point for all ballistic data in ChronoLog.

## Overview

The DOPE module aggregates data from chronograph, rifles, cartridges, bullets, weather, and ranges to create comprehensive ballistic profiles. It is the **most important module** in ChronoLog - all other modules exist to feed data into DOPE sessions.

## Quick Start

```python
from dope.api import DopeAPI

# Initialize API
api = DopeAPI(supabase_client)

# Get user's DOPE sessions
sessions = api.get_sessions_for_user(user_id)

# Create new DOPE session
session_data = {
    "session_name": "308 Win @ 100m",
    "chrono_session_id": "chrono-uuid",
    "cartridge_id": "cartridge-uuid",
    "rifle_id": "rifle-uuid",
    "range_submission_id": "range-uuid",
}
session = api.create_session(session_data, user_id)
```

## Architecture

The DOPE module follows a three-layer architecture:

1. **Service Layer** (`service.py`): Database operations, complex 6-table JOINs
2. **API Layer** (`api.py`): Public facade for external consumers
3. **Business Layer** (`create/business.py`): Workflow orchestration
4. **UI Layer** (`view/view_page.py`, `create/create_page.py`): Streamlit pages

**Critical pattern**: Business layer calls Service directly for own module, calls API for cross-module operations. Never call own module's API (circular dependency).

## Documentation

**Comprehensive documentation**: See [docs/modules/dope/README.md](../docs/modules/dope/README.md)

Key docs:
- [Architecture Layers](../docs/modules/dope/architecture-layers.md) - Three-layer pattern explained
- [API Reference](../docs/modules/dope/api-reference.md) - Complete API documentation
- [Models](../docs/modules/dope/models.md) - Data model specifications (60+ fields)
- [Examples](../docs/modules/dope/examples.md) - Usage patterns

## AI Development Instructions

All instructions for AI-based construction are defined in [README-AI.md](./README-AI.md)
