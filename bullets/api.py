"""
Bullets API - Public interface for the bullets module.

This module provides a clean, type-safe API for accessing bullet specifications.
It implements the BulletsAPIProtocol and wraps the BulletsService for internal operations.

The bullets catalog is admin-maintained and globally accessible to all users.
"""

from typing import List, Optional
from .models import BulletModel
from .service import BulletsService
from .protocols import BulletsAPIProtocol


class BulletsAPI:
    """
    Public API for the bullets module.

    This facade provides a clean, type-safe interface for accessing bullet specifications.
    All methods are UI-agnostic and return strongly-typed BulletModel instances.

    The bullets catalog is admin-maintained (read-only for regular users).
    All users can read the catalog; only admins can create/update/delete.

    Example:
        >>> api = BulletsAPI(supabase_client)
        >>> bullets = api.get_all_bullets()
        >>> sierra_168 = api.filter_bullets(manufacturer="Sierra", weight_grains=168)
    """

    def __init__(self, supabase_client):
        """
        Initialize the Bullets API.

        Args:
            supabase_client: Supabase client instance for database operations
        """
        self._service = BulletsService(supabase_client)
        self._supabase = supabase_client

    # -------------------------------------------------------------------------
    # Public Methods (All Users)
    # -------------------------------------------------------------------------

    def get_all_bullets(self) -> List[BulletModel]:
        """
        Get all bullets from the global catalog.

        Returns all bullets in the database, ordered by manufacturer, model, and weight.
        No user filtering - this is a global catalog accessible to all users.

        Returns:
            List[BulletModel]: List of all bullets (empty list if none found)

        Raises:
            Exception: If database query fails

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> bullets = api.get_all_bullets()
            >>> len(bullets)
            150
            >>> bullets[0].manufacturer
            'Sierra'
        """
        return self._service.get_all_bullets()

    def get_bullet_by_id(self, bullet_id: str) -> Optional[BulletModel]:
        """
        Get a specific bullet by its ID.

        Args:
            bullet_id: UUID of the bullet to retrieve

        Returns:
            Optional[BulletModel]: Bullet if found, None if not found

        Raises:
            Exception: If database query fails

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> bullet = api.get_bullet_by_id("123e4567-e89b-12d3-a456-426614174000")
            >>> bullet.manufacturer
            'Sierra'
            >>> bullet.model
            'MatchKing'
        """
        return self._service.get_bullet_by_id(bullet_id)

    def get_bullets_by_ids(self, bullet_ids: List[str]) -> List[BulletModel]:
        """
        Get multiple bullets by their IDs (batch operation).

        Useful for loading bullets for multiple cartridges efficiently.
        More efficient than calling get_bullet_by_id() in a loop.

        Args:
            bullet_ids: List of bullet UUIDs to retrieve

        Returns:
            List[BulletModel]: List of found bullets (may be fewer than requested)

        Raises:
            Exception: If database query fails

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> bullet_ids = ["id1", "id2", "id3"]
            >>> bullets = api.get_bullets_by_ids(bullet_ids)
            >>> len(bullets)
            3
        """
        if not bullet_ids:
            return []

        try:
            response = (
                self._supabase.table("bullets")
                .select("*")
                .in_("id", bullet_ids)
                .execute()
            )

            if not response.data:
                return []

            return BulletModel.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching bullets by IDs: {str(e)}")

    def filter_bullets(
        self,
        manufacturer: Optional[str] = None,
        bore_diameter_mm: Optional[float] = None,
        weight_grains: Optional[int] = None,
    ) -> List[BulletModel]:
        """
        Filter bullets by various criteria.

        All filter parameters are optional. If none provided, returns all bullets.
        Multiple filters are combined with AND logic.

        Args:
            manufacturer: Filter by exact manufacturer name (case-sensitive)
            bore_diameter_mm: Filter by exact bore diameter in millimeters
            weight_grains: Filter by exact weight in grains

        Returns:
            List[BulletModel]: Filtered bullets (empty list if no matches)

        Raises:
            Exception: If database query fails

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> # Get all Sierra 168gr bullets
            >>> bullets = api.filter_bullets(manufacturer="Sierra", weight_grains=168)
            >>> all(b.manufacturer == "Sierra" and b.weight_grains == 168 for b in bullets)
            True
        """
        return self._service.filter_bullets(
            manufacturer=manufacturer,
            bore_diameter_mm=bore_diameter_mm,
            weight_grains=weight_grains,
        )

    def get_unique_manufacturers(self) -> List[str]:
        """
        Get list of unique bullet manufacturers.

        Useful for populating UI dropdowns and filters.
        Results are sorted alphabetically.

        Returns:
            List[str]: Sorted list of unique manufacturer names

        Raises:
            Exception: If database query fails

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> manufacturers = api.get_unique_manufacturers()
            >>> manufacturers
            ['Berger', 'Hornady', 'Nosler', 'Sierra']
        """
        return self._service.get_unique_manufacturers()

    def get_unique_bore_diameters(self) -> List[float]:
        """
        Get list of unique bore diameters.

        Useful for populating UI dropdowns and filters.
        Returns bore diameters in millimeters, sorted numerically.

        Returns:
            List[float]: Sorted list of unique bore diameters in mm

        Raises:
            Exception: If database query fails

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> diameters = api.get_unique_bore_diameters()
            >>> diameters
            [5.56, 6.5, 7.62, 9.0]
        """
        return self._service.get_unique_bore_diameters()

    def get_unique_weights(self) -> List[int]:
        """
        Get list of unique bullet weights.

        Useful for populating UI dropdowns and filters.
        Returns weights in grains (ballistics standard), sorted numerically.

        Returns:
            List[int]: Sorted list of unique bullet weights in grains

        Raises:
            Exception: If database query fails

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> weights = api.get_unique_weights()
            >>> weights
            [55, 69, 77, 147, 168, 175, 180]
        """
        return self._service.get_unique_weights()

    # -------------------------------------------------------------------------
    # Admin Methods (Admin Only)
    # -------------------------------------------------------------------------

    def create_bullet(self, bullet_data: dict) -> BulletModel:
        """
        Create a new bullet entry (admin only).

        This method should only be called by admin users.
        Regular API implementations may not expose this method.

        Args:
            bullet_data: Dict with bullet fields (metric units)

        Returns:
            BulletModel: Created bullet with generated ID

        Raises:
            Exception: If creation fails or duplicate exists

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> bullet_data = {
            ...     "manufacturer": "Sierra",
            ...     "model": "MatchKing",
            ...     "weight_grains": 168,
            ...     "bullet_diameter_groove_mm": 7.82,
            ...     "bore_diameter_land_mm": 7.62,
            ...     "ballistic_coefficient_g7": 0.243,
            ... }
            >>> bullet = api.create_bullet(bullet_data)
            >>> print(f"Created bullet with ID: {bullet.id}")

        Note:
            Admin-only operation. Should be protected by authentication/authorization.
        """
        return self._service.create_bullet(bullet_data)

    def update_bullet(self, bullet_id: str, bullet_data: dict) -> BulletModel:
        """
        Update an existing bullet entry (admin only).

        This method should only be called by admin users.
        Regular API implementations may not expose this method.

        Args:
            bullet_id: UUID of bullet to update
            bullet_data: Dict with fields to update (metric units)

        Returns:
            BulletModel: Updated bullet

        Raises:
            Exception: If update fails or bullet not found

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> update_data = {
            ...     "ballistic_coefficient_g7": 0.245,  # Updated BC
            ... }
            >>> bullet = api.update_bullet(bullet_id, update_data)
            >>> print(f"Updated BC to: {bullet.ballistic_coefficient_g7}")

        Note:
            Admin-only operation. Should be protected by authentication/authorization.
        """
        return self._service.update_bullet(bullet_id, bullet_data)

    def delete_bullet(self, bullet_id: str) -> bool:
        """
        Delete a bullet entry (admin only).

        This method should only be called by admin users.
        Regular API implementations may not expose this method.

        Args:
            bullet_id: UUID of bullet to delete

        Returns:
            bool: True if deleted, False if not found

        Raises:
            Exception: If delete fails or bullet is referenced by cartridges

        Example:
            >>> api = BulletsAPI(supabase_client)
            >>> deleted = api.delete_bullet(bullet_id)
            >>> if deleted:
            ...     print("Bullet deleted successfully")
            >>> else:
            ...     print("Bullet not found")

        Note:
            Admin-only operation. Should be protected by authentication/authorization.
            Cannot delete bullets that are referenced by cartridges (FK constraint).
        """
        return self._service.delete_bullet(bullet_id)


# Type check: Verify BulletsAPI implements BulletsAPIProtocol
# This is a compile-time check, not a runtime check
def _type_check() -> None:
    """Type checker validates that BulletsAPI implements BulletsAPIProtocol."""
    api: BulletsAPIProtocol = BulletsAPI(None)  # type: ignore