"""
Cartridges Module - Ammunition specifications catalog with dual ownership.

This module provides access to the ammunition cartridge specifications catalog
supporting both global (admin-owned) and user-owned cartridges.

Ownership Model:
- Global cartridges (owner_id=NULL): Admin-maintained, visible to all users
- User-owned cartridges (owner_id=user_id): Created by users, visible only to owner

Public API:
    CartridgesAPI: Main API facade for accessing cartridges
    CartridgeModel: Data model for cartridge specifications
    CartridgeTypeModel: Data model for cartridge types
    CartridgesAPIProtocol: Type protocol for the API contract

Example:
    >>> from cartridges import CartridgesAPI
    >>>
    >>> api = CartridgesAPI(supabase_client)
    >>> # Get all accessible cartridges (global + user-owned)
    >>> cartridges = api.get_all_cartridges(user_id)
    >>> # Filter by type
    >>> creedmoor = api.filter_cartridges(user_id, cartridge_type="6.5 Creedmoor")

For detailed documentation, see:
    - docs/modules/cartridges/README.md
    - docs/modules/cartridges/api-reference.md
    - docs/modules/cartridges/examples.md
"""

from .api import CartridgesAPI
from .models import CartridgeModel, CartridgeTypeModel
from .protocols import CartridgesAPIProtocol

# Public exports
__all__ = [
    "CartridgesAPI",
    "CartridgeModel",
    "CartridgeTypeModel",
    "CartridgesAPIProtocol",
]

# Module metadata
__version__ = "1.0.0"
__author__ = "ChronoLog Team"