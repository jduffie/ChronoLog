# Mapping Module

## Status: Pending Refactoring

The mapping module is currently under architectural review and is pending refactoring to align with the standard module patterns used in other ChronoLog modules.

## Current State

The mapping module currently provides:
- Range catalog (public and user-submitted ranges)
- Geographic coordinates and location data
- Range submission and approval workflows
- Distance and location information

## Pending Work

The mapping module will be refactored in a future phase to follow the standard modularization pattern:

**Planned deliverables:**
- `models.py` - Clean model classes for range entities
- `service.py` - Service layer with user isolation
- `protocols.py` - API contract (Python Protocol classes)
- `api.py` - API facade for accessing range data
- Complete documentation (api-reference.md, models.md, examples.md)

## Current Usage

For now, DOPE and other modules interact with the mapping module through its existing interface. The current structure includes:

- `Range_Library.py` - Range library functionality
- `range_models.py` - Range model definitions
- `session_state_manager.py` - Session state management
- Multiple subdirectories for different workflows (admin, submission, nominate, public_ranges)

## Integration

DOPE sessions reference ranges via `range_submission_id` foreign key to the `ranges_submissions` table.

## Future Documentation

Once the refactoring is complete, this directory will contain:
- README.md (overview)
- api-reference.md (API contract documentation)
- models.md (data model specifications)
- examples.md (usage examples)

## Related Documentation

- [Data Sources Overview](../../architecture/02-data-sources.md#6-mapping-module)
- [Design Decisions](../../architecture/06-design-decisions.md)

---

**Last Updated:** 2025-10-19
**Status:** Pending Refactoring (Phase 2+)