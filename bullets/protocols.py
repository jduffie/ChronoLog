"""
Protocol definitions for the Bullets API.

This module defines the type contract for the bullets module API.
All implementations of the bullets API must conform to this protocol.
"""

from typing import List, Optional, Protocol

from .models import BulletModel


class BulletsAPIProtocol(Protocol):
    """
    Protocol defining the public API for the bullets module.

    The bullets module manages the global bullet specifications catalog.
    This is an admin-maintained, read-only catalog for all users.

    Access model:
    - All users can read (get_all, get_by_id, filter, get_unique_*)
    - Only admin can write (create, update, delete)

    All bullet data is stored in metric units internally.
    """

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
        ...

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
        ...

    def get_bullets_by_ids(self, bullet_ids: List[str]) -> List[BulletModel]:
        """
        Get multiple bullets by their IDs (batch operation).

        Useful for loading bullets for multiple cartridges efficiently.

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
        ...

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
        ...

    def get_unique_manufacturers(self) -> List[str]:
        """
        Get list of unique bullet manufacturers.

        Useful for populating UI dropdowns and filters.

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
        ...

    def get_unique_bore_diameters(self) -> List[float]:
        """
        Get list of unique bore diameters.

        Useful for populating UI dropdowns and filters.
        Returns bore diameters in millimeters, sorted.

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
        ...

    def get_unique_weights(self) -> List[int]:
        """
        Get list of unique bullet weights.

        Useful for populating UI dropdowns and filters.
        Returns weights in grains (ballistics standard), sorted.

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
        ...

    # Admin-only methods (not exposed in regular user API)
    # These would be in a separate AdminBulletsAPIProtocol or admin panel

    def create_bullet(self, bullet_data: dict) -> BulletModel:
        """
        Create a new bullet entry (admin only).

        Args:
            bullet_data: Dict with bullet fields (metric units)

        Returns:
            BulletModel: Created bullet with generated ID

        Raises:
            Exception: If creation fails or duplicate exists

        Note:
            This method should only be called by admin users.
            Regular API implementations may not expose this method.
        """
        ...

    def update_bullet(self, bullet_id: str, bullet_data: dict) -> BulletModel:
        """
        Update an existing bullet entry (admin only).

        Args:
            bullet_id: UUID of bullet to update
            bullet_data: Dict with fields to update (metric units)

        Returns:
            BulletModel: Updated bullet

        Raises:
            Exception: If update fails or bullet not found

        Note:
            This method should only be called by admin users.
            Regular API implementations may not expose this method.
        """
        ...

    def delete_bullet(self, bullet_id: str) -> bool:
        """
        Delete a bullet entry (admin only).

        Args:
            bullet_id: UUID of bullet to delete

        Returns:
            bool: True if deleted, False if not found

        Raises:
            Exception: If delete fails

        Note:
            This method should only be called by admin users.
            Regular API implementations may not expose this method.
        """
        ...