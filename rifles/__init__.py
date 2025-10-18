"""
Rifles Module - Firearm specifications catalog.

This module provides access to user's rifle specifications, including
barrel characteristics, cartridge types, and equipment details.

Ownership Model:
- All rifles are user-scoped (each rifle belongs to a single user)
- No global/shared rifles

Public API:
    RiflesAPI: Main API facade for accessing rifles
    RifleModel: Data model for rifle specifications
    RiflesAPIProtocol: Type protocol for the API contract

Example:
    >>> from rifles import RiflesAPI
    >>>
    >>> api = RiflesAPI(supabase_client)
    >>> # Get all rifles for a user
    >>> rifles = api.get_all_rifles(user_id)
    >>> # Filter by cartridge type
    >>> creedmoor_rifles = api.filter_rifles(
    ...     user_id,
    ...     cartridge_type="6.5 Creedmoor"
    ... )

For detailed documentation, see:
    - docs/modules/rifles/README.md
    - docs/modules/rifles/api-reference.md
    - docs/modules/rifles/examples.md
"""

from .api import RiflesAPI
from .models import RifleModel
from .protocols import RiflesAPIProtocol

# Public exports
__all__ = [
    "RiflesAPI",
    "RifleModel",
    "RiflesAPIProtocol",
]

# Module metadata
__version__ = "1.0.0"
__author__ = "ChronoLog Team"