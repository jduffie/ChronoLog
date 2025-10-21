# User Isolation and Security Model

## Overview

ChronoLog is a multi-tenant application where multiple users share the same database but must never access each other's private data. This document describes the security model that enforces user isolation.

## Core Principles

1. **Defense in depth**: Multiple layers enforce isolation
2. **Filter at query time**: Every query includes user_id filtering for user-owned data
3. **Auth0 user ID as source of truth**: Use `user["id"]` from Auth0, not email
4. **Admin data is global**: Bullets and cartridges are shared (read-only to users)
5. **User data is private**: Rifles, chronograph sessions, weather, DOPE sessions are isolated

---

## User Identification

### Auth0 Integration

ChronoLog uses Auth0 for authentication:

```python
# After successful OAuth flow
user = {
    "id": "auth0|507f1f77bcf86cd799439011",  # Unique, stable identifier
    "email": "user@example.com",             # Can change
    "name": "John Doe"
}
```

### Critical Rule: Use user["id"], NOT email

**Always**:
```python
# Correct
rifles = rifles_service.get_rifles_for_user(user["id"])
```

**Never**:
```python
# Wrong - email can change!
rifles = rifles_service.get_rifles_for_user(user["email"])
```

**Why**:
- `user["id"]` is immutable (Auth0 guarantees this)
- Email can change if user updates their account
- Email might be reused if account deleted and recreated

---

## Data Ownership Models

### Model 1: User-Owned Data (Private)

**Modules**: Chronograph, Rifles, Weather, DOPE

**Pattern**: Data has `user_id` column, all queries filter by it.

```python
# Database schema
CREATE TABLE rifles (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,  -- Auth0 user ID
    name TEXT NOT NULL,
    barrel_length_inches FLOAT,
    ...
);

CREATE INDEX idx_rifles_user_id ON rifles(user_id);
```

**Query pattern**:
```python
def get_rifles_for_user(self, user_id: str) -> List[Rifle]:
    response = self.supabase.from_('rifles') \
        .select('*') \
        .eq('user_id', user_id) \  # REQUIRED
        .execute()
    return [Rifle.from_supabase_record(r) for r in response.data]
```

**Enforcement**:
- Every SELECT: `WHERE user_id = ?`
- Every INSERT: `user_id` column set to current user
- Every UPDATE/DELETE: `WHERE user_id = ?`

---

### Model 2: Admin-Owned Data (Global, Read-Only to Users)

**Modules**: Bullets, Cartridges

**Pattern**: Data has NO `user_id` column. All users can read, only admin can write.

```python
# Database schema
CREATE TABLE bullets (
    id UUID PRIMARY KEY,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    weight_grains FLOAT NOT NULL,
    ...
    -- NO user_id column
);
```

**Query pattern**:
```python
def get_all_bullets(self) -> List[BulletModel]:
    response = self.supabase.from_('bullets') \
        .select('*') \
        .execute()  # No user_id filter - global catalog
    return [BulletModel.from_supabase_record(b) for b in response.data]
```

**Enforcement**:
- SELECT: No user_id filter (global read access)
- INSERT/UPDATE/DELETE: Admin-only (enforced via Supabase RLS or admin panel)

---

### Model 3: Mixed Ownership (Mapping/Ranges)

**Module**: Mapping (future refactoring)

**Pattern**: Some ranges are public, some are user-submitted and private.

```python
# Database schema (conceptual)
CREATE TABLE ranges (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    is_public BOOLEAN DEFAULT FALSE,
    submitted_by_user_id TEXT,  -- NULL for public ranges
    approved BOOLEAN DEFAULT FALSE
);
```

**Query pattern**:
```python
def get_ranges_for_user(self, user_id: str) -> List[Range]:
    # User sees: public ranges + their own submissions
    response = self.supabase.from_('ranges') \
        .select('*') \
        .or_(f'is_public.eq.true,submitted_by_user_id.eq.{user_id}') \
        .execute()
    return [Range.from_supabase_record(r) for r in response.data]
```

---

## Enforcement Layers

### Layer 1: Application Code (Primary)

Every service method enforces user isolation:

```python
class ChronographService:
    def get_sessions_for_user(self, user_id: str) -> List[ChronographSession]:
        """Get chronograph sessions for a specific user."""
        if not user_id:
            raise ValueError("user_id is required")

        response = self.supabase.from_('chronograph_sessions') \
            .select('*') \
            .eq('user_id', user_id) \  # User isolation
            .execute()

        return [ChronographSession.from_supabase_record(s) for s in response.data]

    def create_session(self, session_data: dict, user_id: str) -> ChronographSession:
        """Create a new chronograph session."""
        if not user_id:
            raise ValueError("user_id is required")

        # Force user_id to current user (can't be spoofed)
        session_data['user_id'] = user_id

        response = self.supabase.from_('chronograph_sessions') \
            .insert(session_data) \
            .execute()

        return ChronographSession.from_supabase_record(response.data[0])

    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session (only if user owns it)."""
        # User isolation on DELETE
        response = self.supabase.from_('chronograph_sessions') \
            .delete() \
            .eq('id', session_id) \
            .eq('user_id', user_id) \  # Can only delete own sessions
            .execute()

        return len(response.data) > 0
```

**Key pattern**: `user_id` is always a required parameter, never optional.

---

### Layer 2: Database Row-Level Security (RLS)

Supabase supports PostgreSQL Row-Level Security policies:

```sql
-- Example RLS policy for rifles table
ALTER TABLE rifles ENABLE ROW LEVEL SECURITY;

CREATE POLICY rifles_user_isolation ON rifles
    FOR ALL
    USING (user_id = auth.uid()::text);

-- Users can only see/modify their own rifles
```

**Benefits**:
- Defense in depth (even if app code fails, DB blocks)
- Works across all queries (including raw SQL)
- Prevents privilege escalation

**Note**: Implementation of RLS is optional but recommended for production.

---

### Layer 3: API Layer Validation (Future)

With the new API layer, validation happens at the contract boundary:

```python
# In API protocol
class ChronographAPIProtocol(Protocol):
    def get_sessions(self, user_id: str) -> List[ChronographSession]:
        """Get sessions for user. user_id must not be empty."""
        ...
```

API implementation validates:
```python
class ChronographAPI:
    def get_sessions(self, user_id: str) -> List[ChronographSession]:
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required and cannot be empty")

        return self._service.get_sessions_for_user(user_id)
```

---

## User Isolation in JOINs

### User-Owned JOINs

When joining user-owned tables, filter on both:

```sql
-- DOPE sessions with chronograph sessions
SELECT ds.*, cs.*
FROM dope_sessions ds
JOIN chronograph_sessions cs ON ds.chronograph_session_id = cs.id
WHERE ds.user_id = :user_id
  AND cs.user_id = :user_id  -- Redundant but safe
```

Even though `dope_sessions.chronograph_session_id` FK ensures the chronograph session exists, explicitly filtering `cs.user_id` ensures:
- No leaked data if FK is compromised
- Clear intent in query
- Defense in depth

---

### Mixed Ownership JOINs (DOPE)

DOPE joins user-owned and admin-owned tables:

```sql
-- DOPE session with cartridge (admin) and rifle (user)
SELECT ds.*, c.*, r.*
FROM dope_sessions ds
JOIN cartridges c ON ds.cartridge_id = c.id
  -- No user_id filter on cartridges (admin-owned, global)
JOIN rifles r ON ds.rifle_id = r.id
  AND r.user_id = :user_id  -- User isolation for user-owned data
WHERE ds.user_id = :user_id  -- Primary user isolation
```

**Pattern**:
- User-owned tables: Filter by `user_id`
- Admin-owned tables: No filter (global access)
- Always filter the primary table (`dope_sessions.user_id`)

---

## Common Security Pitfalls and Mitigations

### Pitfall 1: Using email instead of user ID

**Bad**:
```python
def get_rifles(self, email: str):
    # Email can change! Data leak!
    return self.supabase.from_('rifles').eq('user_id', email).execute()
```

**Good**:
```python
def get_rifles(self, user_id: str):
    # user_id is immutable
    return self.supabase.from_('rifles').eq('user_id', user_id).execute()
```

---

### Pitfall 2: Forgetting user_id filter

**Bad**:
```python
def get_session_by_name(self, name: str):
    # BUG: No user_id filter - returns ANY user's session with this name!
    return self.supabase.from_('chronograph_sessions') \
        .eq('session_name', name) \
        .execute()
```

**Good**:
```python
def get_session_by_name(self, name: str, user_id: str):
    # Safe: Filters by both name AND user_id
    return self.supabase.from_('chronograph_sessions') \
        .eq('session_name', name) \
        .eq('user_id', user_id) \
        .execute()
```

---

### Pitfall 3: Trusting client-provided user_id

**Bad**:
```python
# In API endpoint
def create_session(session_data: dict):
    # BUG: Client could spoof user_id in session_data!
    return service.create_session(session_data)
```

**Good**:
```python
# In API endpoint
def create_session(session_data: dict, authenticated_user: dict):
    # Force user_id from auth token, ignore client input
    user_id = authenticated_user["id"]
    return service.create_session(session_data, user_id)
```

---

### Pitfall 4: Incomplete DELETE/UPDATE filters

**Bad**:
```python
def delete_session(self, session_id: str):
    # BUG: Can delete ANY user's session!
    self.supabase.from_('sessions').delete().eq('id', session_id).execute()
```

**Good**:
```python
def delete_session(self, session_id: str, user_id: str):
    # Safe: Can only delete own sessions
    self.supabase.from_('sessions').delete() \
        .eq('id', session_id) \
        .eq('user_id', user_id) \
        .execute()
```

---

## Testing User Isolation

### Unit Tests

Mock Supabase and verify user_id is passed:

```python
def test_get_sessions_filters_by_user():
    mock_supabase = Mock()
    service = ChronographService(mock_supabase)

    service.get_sessions_for_user("user123")

    # Verify user_id filter was applied
    mock_supabase.from_().select().eq.assert_called_with('user_id', 'user123')
```

### Integration Tests

Create test data for multiple users, verify isolation:

```python
def test_user_isolation_integration():
    # Create session for user1
    user1_session = service.create_session(data, user_id="user1")

    # Try to fetch as user2
    user2_sessions = service.get_sessions_for_user("user2")

    # Verify user2 cannot see user1's session
    assert user1_session.id not in [s.id for s in user2_sessions]
```

---

## Summary

**User-Owned Data**:
- Has `user_id` column
- All queries filter by `user_id`
- User can only access their own data

**Admin-Owned Data**:
- No `user_id` column
- All users can read
- Only admin can write

**Enforcement**:
1. Application code (required `user_id` parameters)
2. Database RLS policies (optional but recommended)
3. API layer validation (future)

**Critical Rules**:
- Always use `user["id"]`, never email
- Always require `user_id` parameter (never optional)
- Always filter user-owned queries by `user_id`
- Never trust client-provided `user_id`

---

## Next Steps

- [Metric System](05-metric-system.md) - Unit handling
- [Design Decisions](06-design-decisions.md) - Architectural choices
- [Common Patterns](../integration/common-patterns.md) - Implementation examples