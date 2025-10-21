"""
Cartridges API - Public interface for the cartridges module.

This module provides a clean, type-safe API for accessing cartridge specifications
with a dual ownership model (global + user-owned). It implements the CartridgesAPIProtocol
and wraps the CartridgeService for internal operations.

Ownership Model:
- Global cartridges (owner_id = NULL): Admin-owned, visible to all, editable by admins only
- User-owned cartridges (owner_id = user_id): Visible only to owner, editable by owner only
"""

from typing import List, Optional

from .models import CartridgeModel
from .protocols import CartridgesAPIProtocol
from .service import CartridgeService


class CartridgesAPI:
    """
    Public API for the cartridges module with dual ownership model.

    This facade provides a clean, type-safe interface for accessing cartridge specifications.
    All methods are UI-agnostic and return strongly-typed CartridgeModel instances.

    Ownership:
    - Global cartridges: Admin-maintained, visible to all users
    - User-owned cartridges: Created by users, visible only to owner

    Example:
        >>> api = CartridgesAPI(supabase_client)
        >>> # Get all accessible cartridges
        >>> cartridges = api.get_all_cartridges(user_id)
        >>> # Filter by type
        >>> creedmoor = api.filter_cartridges(user_id, cartridge_type="6.5 Creedmoor")
    """

    def __init__(self, supabase_client):
        """
        Initialize the Cartridges API.

        Args:
            supabase_client: Supabase client instance for database operations
        """
        self._service = CartridgeService(supabase_client)
        self._supabase = supabase_client

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
            List[CartridgeModel]: All accessible cartridges with bullet details

        Raises:
            Exception: If database query fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> cartridges = api.get_all_cartridges(user_id)
            >>> for cart in cartridges:
            ...     print(f"{cart.display_name} - {cart.bullet_display}")
        """
        return self._service.get_cartridges_for_user(user_id)

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
            Optional[CartridgeModel]: Cartridge with bullet details if accessible

        Raises:
            Exception: If database query fails

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> cartridge = api.get_cartridge_by_id(cartridge_id, user_id)
            >>> if cartridge:
            ...     print(f"{cartridge.display_name}")
            ...     print(f"Bullet: {cartridge.bullet_display}")
        """
        return self._service.get_cartridge_by_id(cartridge_id, user_id)

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
        """
        if not cartridge_ids:
            return []

        try:
            response = (
                self._supabase.table("cartridges")
                .select(
                    """
                    *,
                    bullets!bullet_id (
                        manufacturer,
                        model,
                        weight_grains,
                        bullet_diameter_groove_mm,
                        bore_diameter_land_mm,
                        bullet_length_mm,
                        ballistic_coefficient_g1,
                        ballistic_coefficient_g7,
                        sectional_density,
                        min_req_twist_rate_in_per_rev,
                        pref_twist_rate_in_per_rev
                    )
                """
                )
                .in_("id", cartridge_ids)
                .or_(f"owner_id.eq.{user_id},owner_id.is.null")
                .execute()
            )

            if not response.data:
                return []

            # Flatten bullet data
            cartridges = []
            for record in response.data:
                if record.get("bullets"):
                    bullet_data = record["bullets"]
                    record["bullet_manufacturer"] = bullet_data.get("manufacturer")
                    record["bullet_model"] = bullet_data.get("model")
                    record["bullet_weight_grains"] = bullet_data.get("weight_grains")
                    record["bullet_diameter_groove_mm"] = bullet_data.get(
                        "bullet_diameter_groove_mm"
                    )
                    record["bore_diameter_land_mm"] = bullet_data.get(
                        "bore_diameter_land_mm"
                    )
                    record["bullet_length_mm"] = bullet_data.get("bullet_length_mm")
                    record["ballistic_coefficient_g1"] = bullet_data.get(
                        "ballistic_coefficient_g1"
                    )
                    record["ballistic_coefficient_g7"] = bullet_data.get(
                        "ballistic_coefficient_g7"
                    )
                    record["sectional_density"] = bullet_data.get("sectional_density")
                    record["min_req_twist_rate_in_per_rev"] = bullet_data.get(
                        "min_req_twist_rate_in_per_rev"
                    )
                    record["pref_twist_rate_in_per_rev"] = bullet_data.get(
                        "pref_twist_rate_in_per_rev"
                    )

                cartridges.append(CartridgeModel.from_supabase_record(record))

            return cartridges

        except Exception as e:
            raise Exception(f"Error fetching cartridges by IDs: {str(e)}")

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
            >>> # Get all Federal 6.5 Creedmoor
            >>> federal_creedmoor = api.filter_cartridges(
            ...     user_id,
            ...     make="Federal",
            ...     cartridge_type="6.5 Creedmoor"
            ... )
        """
        try:
            query = self._supabase.table("cartridges").select(
                """
                *,
                bullets!bullet_id (
                    manufacturer,
                    model,
                    weight_grains,
                    bullet_diameter_groove_mm,
                    bore_diameter_land_mm,
                    bullet_length_mm,
                    ballistic_coefficient_g1,
                    ballistic_coefficient_g7,
                    sectional_density,
                    min_req_twist_rate_in_per_rev,
                    pref_twist_rate_in_per_rev
                )
            """
            )

            # Apply filters
            if make:
                query = query.eq("make", make)
            if model:
                query = query.eq("model", model)
            if cartridge_type:
                query = query.eq("cartridge_type", cartridge_type)
            if bullet_id:
                query = query.eq("bullet_id", bullet_id)

            # Apply access control
            query = query.or_(f"owner_id.eq.{user_id},owner_id.is.null")

            response = query.execute()

            if not response.data:
                return []

            # Flatten bullet data
            cartridges = []
            for record in response.data:
                if record.get("bullets"):
                    bullet_data = record["bullets"]
                    record["bullet_manufacturer"] = bullet_data.get("manufacturer")
                    record["bullet_model"] = bullet_data.get("model")
                    record["bullet_weight_grains"] = bullet_data.get("weight_grains")
                    record["bullet_diameter_groove_mm"] = bullet_data.get(
                        "bullet_diameter_groove_mm"
                    )
                    record["bore_diameter_land_mm"] = bullet_data.get(
                        "bore_diameter_land_mm"
                    )
                    record["bullet_length_mm"] = bullet_data.get("bullet_length_mm")
                    record["ballistic_coefficient_g1"] = bullet_data.get(
                        "ballistic_coefficient_g1"
                    )
                    record["ballistic_coefficient_g7"] = bullet_data.get(
                        "ballistic_coefficient_g7"
                    )
                    record["sectional_density"] = bullet_data.get("sectional_density")
                    record["min_req_twist_rate_in_per_rev"] = bullet_data.get(
                        "min_req_twist_rate_in_per_rev"
                    )
                    record["pref_twist_rate_in_per_rev"] = bullet_data.get(
                        "pref_twist_rate_in_per_rev"
                    )

                cartridges.append(CartridgeModel.from_supabase_record(record))

            return cartridges

        except Exception as e:
            raise Exception(f"Error filtering cartridges: {str(e)}")

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
        return self._service.get_cartridge_types()

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
            ['Custom Load', 'Federal', 'Hornady', 'Winchester']
        """
        try:
            cartridges = self.get_all_cartridges(user_id)
            makes = list(set(c.make for c in cartridges if c.make))
            return sorted(makes)
        except Exception as e:
            raise Exception(f"Error getting unique makes: {str(e)}")

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
        try:
            cartridges = self.get_all_cartridges(user_id)
            models = list(set(c.model for c in cartridges if c.model))
            return sorted(models)
        except Exception as e:
            raise Exception(f"Error getting unique models: {str(e)}")

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

        Note:
            Sets owner_id = user_id automatically.
        """
        import uuid

        try:
            # Set owner_id to user_id
            insert_data = cartridge_data.copy()
            insert_data["owner_id"] = user_id
            insert_data["id"] = str(uuid.uuid4())

            response = self._supabase.table("cartridges").insert(insert_data).execute()

            if not response.data:
                raise Exception("Failed to create cartridge")

            # Fetch with bullet details
            return self.get_cartridge_by_id(response.data[0]["id"], user_id)

        except Exception as e:
            if "duplicate key value" in str(e):
                raise Exception("This cartridge already exists")
            raise Exception(f"Error creating cartridge: {str(e)}")

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
        """
        try:
            response = (
                self._supabase.table("cartridges")
                .update(cartridge_data)
                .eq("id", cartridge_id)
                .eq("owner_id", user_id)  # Only update if owned by user
                .execute()
            )

            if not response.data:
                raise Exception("Cartridge not found or not owned by user")

            # Fetch with bullet details
            return self.get_cartridge_by_id(cartridge_id, user_id)

        except Exception as e:
            raise Exception(f"Error updating cartridge: {str(e)}")

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
            Exception: If delete fails or cartridge is referenced

        Example:
            >>> api = CartridgesAPI(supabase_client)
            >>> deleted = api.delete_user_cartridge(cartridge_id, user_id)

        Note:
            Cannot delete if referenced by DOPE sessions (FK constraint).
        """
        try:
            response = (
                self._supabase.table("cartridges")
                .delete()
                .eq("id", cartridge_id)
                .eq("owner_id", user_id)  # Only delete if owned by user
                .execute()
            )

            return bool(response.data)

        except Exception as e:
            raise Exception(f"Error deleting cartridge: {str(e)}")

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
        """
        import uuid

        try:
            # Set owner_id to NULL
            insert_data = cartridge_data.copy()
            insert_data["owner_id"] = None
            insert_data["id"] = str(uuid.uuid4())

            response = self._supabase.table("cartridges").insert(insert_data).execute()

            if not response.data:
                raise Exception("Failed to create global cartridge")

            # Fetch with bullet details (admin can access all)
            cartridge_id = response.data[0]["id"]
            # Use a dummy user_id since global cartridges are accessible to all
            return self.get_cartridge_by_id(cartridge_id, "admin")

        except Exception as e:
            if "duplicate key value" in str(e):
                raise Exception("This cartridge already exists")
            raise Exception(f"Error creating global cartridge: {str(e)}")

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
        """
        try:
            response = (
                self._supabase.table("cartridges")
                .update(cartridge_data)
                .eq("id", cartridge_id)
                .is_("owner_id", "null")  # Only update if global
                .execute()
            )

            if not response.data:
                raise Exception("Global cartridge not found")

            # Fetch with bullet details
            return self.get_cartridge_by_id(cartridge_id, "admin")

        except Exception as e:
            raise Exception(f"Error updating global cartridge: {str(e)}")

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
        """
        try:
            response = (
                self._supabase.table("cartridges")
                .delete()
                .eq("id", cartridge_id)
                .is_("owner_id", "null")  # Only delete if global
                .execute()
            )

            return bool(response.data)

        except Exception as e:
            raise Exception(f"Error deleting global cartridge: {str(e)}")


# Type check: Verify CartridgesAPI implements CartridgesAPIProtocol
# This is a compile-time check, not a runtime check
def _type_check() -> None:
    """Type checker validates that CartridgesAPI implements CartridgesAPIProtocol."""
    api: CartridgesAPIProtocol = CartridgesAPI(None)  # type: ignore