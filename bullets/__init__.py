"""
Bullets Module - Global bullet specifications catalog.

This module provides access to the bullet specifications catalog.
The catalog is admin-maintained and globally accessible to all users.

Public API:
    BulletsAPI: Main API facade for accessing bullets
    BulletModel: Data model for bullet specifications
    BulletsAPIProtocol: Type protocol for the API contract

Example:
    >>> from bullets import BulletsAPI
    >>>
    >>> api = BulletsAPI(supabase_client)
    >>> bullets = api.get_all_bullets()
    >>> sierra_bullets = api.filter_bullets(manufacturer="Sierra")

For detailed documentation, see:
    - docs/modules/bullets/README.md
    - docs/modules/bullets/api-reference.md
    - docs/modules/bullets/examples.md
"""

from .api import BulletsAPI
from .models import BulletModel
from .protocols import BulletsAPIProtocol

# Public exports
__all__ = [
    "BulletsAPI",
    "BulletModel",
    "BulletsAPIProtocol",
]

# Module metadata
__version__ = "1.0.0"
__author__ = "ChronoLog Team"
