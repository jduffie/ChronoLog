"""
Cartridges API Protocol - Type-safe contract definition.

This module defines the API contract for the cartridges module using Python's
Protocol class for compile-time type checking.

The cartridges catalog supports both:
- Global/admin-owned cartridges (owner_id is NULL) - read-only to users
- User-owned cartridges (owner_id is user_id) - full CRUD for owners

All users can read both global and their own cartridges.
Only admins can create/modify global cartridges.
Users can create/modify their own cartridges.
"""

from typing import List, Optional, Protocol

from .models import CartridgeModel


class CartridgesAPIProtocol(Protocol):
    """
    Protocol defining the public API contract for the cartridges module.

    This protocol ensures type safety and provides a clear contract for
    implementations. Any class implementing this protocol must provide
    all these methods with matching signatures.

    The API handles both global (admin-owned) and user-owned cartridges.
    """

    # -------------------------------------------------------------------------
    # Public Methods (All Users)
    # -------------------------------------------------------------------------

    def get_all_cartridges(self, user_id: str) -> List[CartridgeModel]:
        """
        Get all cartridges accessible to a user.

        Returns both global cartridges (owner_id is NULL) and cartridges
        owned by the user, with bullet details joined in.

        Args:
            user_id: User's ID for filtering user-owned cartridges

        Returns:
            List[CartridgeModel]: List of accessible cartridges with bullet details

        Raises:
            Exception: If database query fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> cartridges = api.get_all_cartridges(user_id)
            >>> len(cartridges)
            45  # Global + user-owned cartridges
        """
        ...

    def get_cartridge_by_id(
        self, cartridge_id: str, user_id: str
    ) -> Optional[CartridgeModel]:
        """
        Get a specific cartridge by ID with bullet details.

        Only returns the cartridge if it's either:
        - Global (owner_id is NULL), or
        - Owned by the user (owner_id equals user_id)

        Args:
            cartridge_id: UUID of the cartridge
            user_id: User's ID for access control

        Returns:
            Optional[CartridgeModel]: Cartridge with bullet details if found and accessible

        Raises:
            Exception: If database query fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> cartridge = api.get_cartridge_by_id(cartridge_id, user_id)
            >>> if cartridge:
            ...     print(f"{cartridge.display_name}")
            ...     print(f"Bullet: {cartridge.bullet_display}")
        """
        ...

    def get_cartridges_by_ids(
        self, cartridge_ids: List[str], user_id: str
    ) -> List[CartridgeModel]:
        """
        Get multiple cartridges by their IDs (batch operation).

        More efficient than calling get_cartridge_by_id() in a loop.
        Only returns cartridges that are accessible to the user.

        Args:
            cartridge_ids: List of cartridge UUIDs
            user_id: User's ID for access control

        Returns:
            List[CartridgeModel]: Found cartridges (may be fewer than requested)

        Raises:
            Exception: If database query fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> cartridge_ids = ["id1", "id2", "id3"]
            >>> cartridges = api.get_cartridges_by_ids(cartridge_ids, user_id)
            >>> len(cartridges)
            3
        """
        ...

    def filter_cartridges(
        self,
        user_id: str,
        make: Optional[str] = None,
        model: Optional[str] = None,
        cartridge_type: Optional[str] = None,
        bullet_id: Optional[str] = None,
    ) -> List[CartridgeModel]:
        """
        Filter cartridges by various criteria.

        Returns cartridges accessible to user (global + user-owned) that match filters.
        All filter parameters are optional. Multiple filters use AND logic.

        Args:
            user_id: User's ID for access control
            make: Filter by exact manufacturer name
            model: Filter by exact model name
            cartridge_type: Filter by exact cartridge type
            bullet_id: Filter by specific bullet ID

        Returns:
            List[CartridgeModel]: Filtered cartridges with bullet details

        Raises:
            Exception: If database query fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> # Get all Federal cartridges
            >>> federal = api.filter_cartridges(user_id, make="Federal")
            >>> # Get all 6.5 Creedmoor cartridges
            >>> creedmoor = api.filter_cartridges(
            ...     user_id, cartridge_type="6.5 Creedmoor"
            ... )
        """
        ...

    def get_cartridge_types(self) -> List[str]:
        """
        Get list of all available cartridge types.

        Returns values from the cartridge_types lookup table.
        Useful for populating UI dropdowns.

        Returns:
            List[str]: Sorted list of cartridge type names

        Raises:
            Exception: If database query fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> types = api.get_cartridge_types()
            >>> types
            ['6.5 Creedmoor', '6mm Creedmoor', '.308 Winchester', ...]
        """
        ...

    def get_unique_makes(self, user_id: str) -> List[str]:
        """
        Get list of unique cartridge manufacturers.

        Returns manufacturers from cartridges accessible to user.
        Useful for populating UI filters.

        Args:
            user_id: User's ID for filtering

        Returns:
            List[str]: Sorted list of unique manufacturer names

        Raises:
            Exception: If database query fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> makes = api.get_unique_makes(user_id)
            >>> makes
            ['Federal', 'Hornady', 'Nosler', 'Winchester']
        """
        ...

    def get_unique_models(self, user_id: str) -> List[str]:
        """
        Get list of unique cartridge model names.

        Returns models from cartridges accessible to user.
        Useful for populating UI filters.

        Args:
            user_id: User's ID for filtering

        Returns:
            List[str]: Sorted list of unique model names

        Raises:
            Exception: If database query fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> models = api.get_unique_models(user_id)
            >>> models
            ['Gold Medal', 'Match', 'Premium', 'Superformance']
        """
        ...

    # -------------------------------------------------------------------------
    # User Methods (User-Owned Cartridges)
    # -------------------------------------------------------------------------

    def create_user_cartridge(
        self, cartridge_data: dict, user_id: str
    ) -> CartridgeModel:
        """
        Create a new user-owned cartridge.

        Creates a cartridge owned by the user (owner_id = user_id).
        Regular users can only create their own cartridges.

        Args:
            cartridge_data: Dict with cartridge fields
            user_id: User's ID (will be set as owner_id)

        Returns:
            CartridgeModel: Created cartridge with generated ID

        Raises:
            Exception: If creation fails or validation fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> cartridge_data = {
            ...     "make": "Custom Load",
            ...     "model": "Match",
            ...     "bullet_id": bullet_id,
            ...     "cartridge_type": "6.5 Creedmoor",
            ... }
            >>> cartridge = api.create_user_cartridge(cartridge_data, user_id)
            >>> print(f"Created: {cartridge.display_name}")

        Note:
            User can only create cartridges for themselves.
            Sets owner_id = user_id automatically.
        """
        ...

    def update_user_cartridge(
        self, cartridge_id: str, cartridge_data: dict, user_id: str
    ) -> CartridgeModel:
        """
        Update a user-owned cartridge.

        Only allows updating cartridges owned by the user.
        Cannot update global (admin-owned) cartridges.

        Args:
            cartridge_id: UUID of cartridge to update
            cartridge_data: Dict with fields to update
            user_id: User's ID (for ownership verification)

        Returns:
            CartridgeModel: Updated cartridge

        Raises:
            Exception: If update fails or user doesn't own cartridge

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> update_data = {"model": "Updated Match"}
            >>> cartridge = api.update_user_cartridge(
            ...     cartridge_id, update_data, user_id
            ... )

        Note:
            User can only update their own cartridges.
            Cannot modify global cartridges.
        """
        ...

    def delete_user_cartridge(self, cartridge_id: str, user_id: str) -> bool:
        """
        Delete a user-owned cartridge.

        Only allows deleting cartridges owned by the user.
        Cannot delete global (admin-owned) cartridges.

        Args:
            cartridge_id: UUID of cartridge to delete
            user_id: User's ID (for ownership verification)

        Returns:
            bool: True if deleted, False if not found or not owned

        Raises:
            Exception: If delete fails or cartridge is referenced by DOPE sessions

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> deleted = api.delete_user_cartridge(cartridge_id, user_id)
            >>> if deleted:
            ...     print("Cartridge deleted")

        Note:
            User can only delete their own cartridges.
            Cannot delete if referenced by DOPE sessions (FK constraint).
        """
        ...

    # -------------------------------------------------------------------------
    # Admin Methods (Global Cartridges - Admin Only)
    # -------------------------------------------------------------------------

    def create_global_cartridge(self, cartridge_data: dict) -> CartridgeModel:
        """
        Create a new global cartridge (admin only).

        Creates a cartridge with owner_id = NULL, making it accessible
        to all users but editable only by admins.

        Args:
            cartridge_data: Dict with cartridge fields

        Returns:
            CartridgeModel: Created global cartridge

        Raises:
            Exception: If creation fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> cartridge_data = {
            ...     "make": "Federal",
            ...     "model": "Gold Medal",
            ...     "bullet_id": bullet_id,
            ...     "cartridge_type": "6.5 Creedmoor",
            ... }
            >>> cartridge = api.create_global_cartridge(cartridge_data)

        Note:
            Admin-only operation.
            Sets owner_id = NULL automatically.
            Should be protected by authentication/authorization.
        """
        ...

    def update_global_cartridge(
        self, cartridge_id: str, cartridge_data: dict
    ) -> CartridgeModel:
        """
        Update a global cartridge (admin only).

        Only allows updating global cartridges (owner_id is NULL).

        Args:
            cartridge_id: UUID of cartridge to update
            cartridge_data: Dict with fields to update

        Returns:
            CartridgeModel: Updated cartridge

        Raises:
            Exception: If update fails or cartridge is not global

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> update_data = {"model": "Gold Medal Match"}
            >>> cartridge = api.update_global_cartridge(
            ...     cartridge_id, update_data
            ... )

        Note:
            Admin-only operation.
            Only updates cartridges where owner_id is NULL.
            Should be protected by authentication/authorization.
        """
        ...

    def delete_global_cartridge(self, cartridge_id: str) -> bool:
        """
        Delete a global cartridge (admin only).

        Only allows deleting global cartridges (owner_id is NULL).

        Args:
            cartridge_id: UUID of cartridge to delete

        Returns:
            bool: True if deleted, False if not found

        Raises:
            Exception: If delete fails or cartridge is referenced

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> deleted = api.delete_global_cartridge(cartridge_id)

        Note:
            Admin-only operation.
            Cannot delete if referenced by DOPE sessions.
            Should be protected by authentication/authorization.
        """
        ...