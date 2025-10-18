"""
Rifles Module API Facade

This module provides the public API facade for rifle operations.
It wraps the service layer with a clean, type-safe interface defined
by RiflesAPIProtocol.

Architecture:
    RiflesAPI (this file) -> RifleService -> Supabase

The API facade handles:
    - ID generation for new rifles
    - Timestamp management
    - Type conversions
    - Access control enforcement
    - Clean error messages

Example:
    >>> from rifles import RiflesAPI
    >>>
    >>> api = RiflesAPI(supabase_client)
    >>> rifles = api.get_all_rifles(user_id)
    >>> for rifle in rifles:
    ...     print(f"{rifle.name} - {rifle.cartridge_type}")
"""

import uuid
from datetime import datetime
from typing import List, Optional

from .models import RifleModel
from .protocols import RiflesAPIProtocol
from .service import RifleService


class RiflesAPI:
    """
    Main API facade for rifle operations.

    Implements RiflesAPIProtocol to ensure type safety and API contract compliance.
    All rifle operations are user-scoped - each rifle belongs to a single user.

    Attributes:
        _supabase: Supabase client instance
        _service: RifleService instance for database operations

    Example:
        >>> api = RiflesAPI(supabase_client)
        >>>
        >>> # Create a rifle
        >>> rifle_data = {
        ...     "name": "Remington 700",
        ...     "cartridge_type": "6.5 Creedmoor",
        ...     "barrel_twist_ratio": "1:8"
        ... }
        >>> rifle = api.create_rifle(rifle_data, user_id)
        >>>
        >>> # Get all rifles
        >>> rifles = api.get_all_rifles(user_id)
        >>>
        >>> # Update a rifle
        >>> updates = {"barrel_length": "26 inches"}
        >>> updated_rifle = api.update_rifle(rifle.id, updates, user_id)
        >>>
        >>> # Delete a rifle
        >>> if api.delete_rifle(rifle.id, user_id):
        ...     print("Rifle deleted successfully")
    """

    def __init__(self, supabase_client):
        """
        Initialize the Rifles API.

        Args:
            supabase_client: Authenticated Supabase client instance
        """
        self._supabase = supabase_client
        self._service = RifleService(supabase_client)

    # Read Operations

    def get_all_rifles(self, user_id: str) -> List[RifleModel]:
        """
        Get all rifles for a user, ordered by creation date descending.

        Args:
            user_id: The user's ID

        Returns:
            List of RifleModel objects owned by the user
            Returns empty list if user has no rifles

        Raises:
            Exception: If database operation fails

        Example:
            >>> rifles = api.get_all_rifles("user-123")
            >>> for rifle in rifles:
            ...     print(f"{rifle.name} - {rifle.cartridge_type}")
        """
        return self._service.get_rifles_for_user(user_id)

    def get_rifle_by_id(
        self, rifle_id: str, user_id: str
    ) -> Optional[RifleModel]:
        """
        Get a specific rifle by ID.

        Args:
            rifle_id: The rifle's unique ID
            user_id: The user's ID (for access control)

        Returns:
            RifleModel if found and owned by user, None otherwise

        Raises:
            Exception: If database operation fails

        Example:
            >>> rifle = api.get_rifle_by_id("rifle-123", "user-123")
            >>> if rifle:
            ...     print(f"Found: {rifle.name}")
        """
        return self._service.get_rifle_by_id(rifle_id, user_id)

    def get_rifle_by_name(
        self, user_id: str, name: str
    ) -> Optional[RifleModel]:
        """
        Get a rifle by name.

        Note: Names should be unique per user but this is not enforced at
        the database level. Returns the first match found.

        Args:
            user_id: The user's ID
            name: The rifle name to search for

        Returns:
            RifleModel if found, None otherwise

        Raises:
            Exception: If database operation fails

        Example:
            >>> rifle = api.get_rifle_by_name("user-123", "Remington 700")
            >>> if rifle:
            ...     print(f"Found rifle with ID: {rifle.id}")
        """
        return self._service.get_rifle_by_name(user_id, name)

    def filter_rifles(
        self,
        user_id: str,
        cartridge_type: Optional[str] = None,
        twist_ratio: Optional[str] = None,
    ) -> List[RifleModel]:
        """
        Get rifles filtered by criteria.

        Args:
            user_id: The user's ID
            cartridge_type: Filter by cartridge type (optional)
                          Use "All" or None to include all types
            twist_ratio: Filter by barrel twist ratio (optional)
                        Use "All" or None to include all ratios

        Returns:
            List of RifleModel objects matching filters
            Ordered by creation date descending
            Returns empty list if no matches

        Raises:
            Exception: If database operation fails

        Example:
            >>> # Get all 6.5 Creedmoor rifles
            >>> rifles = api.filter_rifles(
            ...     "user-123",
            ...     cartridge_type="6.5 Creedmoor"
            ... )
            >>>
            >>> # Get rifles with specific twist and caliber
            >>> rifles = api.filter_rifles(
            ...     "user-123",
            ...     cartridge_type="6.5 Creedmoor",
            ...     twist_ratio="1:8"
            ... )
        """
        return self._service.get_rifles_filtered(
            user_id, cartridge_type, twist_ratio
        )

    # Metadata Operations

    def get_unique_cartridge_types(self, user_id: str) -> List[str]:
        """
        Get unique cartridge types from user's rifles.

        Useful for populating filter dropdowns in UI.

        Args:
            user_id: The user's ID

        Returns:
            Sorted list of unique cartridge type strings
            Returns empty list if user has no rifles

        Raises:
            Exception: If database operation fails

        Example:
            >>> types = api.get_unique_cartridge_types("user-123")
            >>> print(types)  # ['6.5 Creedmoor', '308 Winchester', ...]
        """
        return self._service.get_unique_cartridge_types(user_id)

    def get_unique_twist_ratios(self, user_id: str) -> List[str]:
        """
        Get unique barrel twist ratios from user's rifles.

        Useful for populating filter dropdowns in UI.

        Args:
            user_id: The user's ID

        Returns:
            Sorted list of unique twist ratio strings
            Returns empty list if user has no rifles

        Raises:
            Exception: If database operation fails

        Example:
            >>> ratios = api.get_unique_twist_ratios("user-123")
            >>> print(ratios)  # ['1:7', '1:8', '1:9', ...]
        """
        return self._service.get_unique_twist_ratios(user_id)

    # Write Operations

    def create_rifle(self, rifle_data: dict, user_id: str) -> RifleModel:
        """
        Create a new rifle.

        Generates UUID, sets timestamps, and enforces user ownership.

        Args:
            rifle_data: Dictionary containing rifle fields:
                - name: str (required) - Rifle name
                - cartridge_type: str (required) - Cartridge type
                - barrel_twist_ratio: str (optional) - e.g., "1:8"
                - barrel_length: str (optional) - e.g., "24 inches"
                - sight_offset: str (optional) - Height over bore
                - trigger: str (optional) - Trigger description
                - scope: str (optional) - Scope description
            user_id: The user's ID (will be set as owner)

        Returns:
            Created RifleModel with generated ID and timestamps

        Raises:
            Exception: If creation fails or required fields missing

        Example:
            >>> rifle_data = {
            ...     "name": "Remington 700",
            ...     "cartridge_type": "6.5 Creedmoor",
            ...     "barrel_twist_ratio": "1:8",
            ...     "barrel_length": "24 inches"
            ... }
            >>> rifle = api.create_rifle(rifle_data, "user-123")
            >>> print(f"Created rifle: {rifle.id}")
        """
        try:
            # Generate ID and set metadata
            insert_data = rifle_data.copy()
            insert_data["id"] = str(uuid.uuid4())
            insert_data["user_id"] = user_id
            insert_data["created_at"] = datetime.now().isoformat()
            insert_data["updated_at"] = datetime.now().isoformat()

            # Insert the rifle
            response = (
                self._supabase.table("rifles")
                .insert(insert_data)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to create rifle - no data returned")

            # Return the created rifle as a model
            return RifleModel.from_supabase_record(response.data[0])

        except Exception as e:
            raise Exception(f"Error creating rifle: {str(e)}")

    def update_rifle(
        self, rifle_id: str, updates: dict, user_id: str
    ) -> RifleModel:
        """
        Update an existing rifle.

        Updates timestamp automatically. Only provided fields are updated.

        Args:
            rifle_id: The rifle's unique ID
            updates: Dictionary containing fields to update
                    Only provided fields will be updated
            user_id: The user's ID (for access control)

        Returns:
            Updated RifleModel

        Raises:
            Exception: If update fails or rifle not found/not owned by user

        Example:
            >>> updates = {"barrel_length": "26 inches"}
            >>> rifle = api.update_rifle("rifle-123", updates, "user-123")
            >>> print(f"Updated barrel: {rifle.barrel_length}")
        """
        try:
            # Add updated_at timestamp
            update_data = updates.copy()
            update_data["updated_at"] = datetime.now().isoformat()

            # Perform update
            response = (
                self._supabase.table("rifles")
                .update(update_data)
                .eq("id", rifle_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not response.data or len(response.data) == 0:
                raise Exception(
                    f"Rifle {rifle_id} not found or not owned by user"
                )

            # Return the updated rifle
            return RifleModel.from_supabase_record(response.data[0])

        except Exception as e:
            raise Exception(f"Error updating rifle: {str(e)}")

    def delete_rifle(self, rifle_id: str, user_id: str) -> bool:
        """
        Delete a rifle.

        Args:
            rifle_id: The rifle's unique ID
            user_id: The user's ID (for access control)

        Returns:
            True if deleted successfully
            False if rifle not found or not owned by user

        Raises:
            Exception: If database operation fails

        Example:
            >>> if api.delete_rifle("rifle-123", "user-123"):
            ...     print("Rifle deleted successfully")
            ... else:
            ...     print("Rifle not found or not owned by user")
        """
        try:
            response = (
                self._supabase.table("rifles")
                .delete()
                .eq("id", rifle_id)
                .eq("user_id", user_id)
                .execute()
            )

            # Return True if at least one row was deleted
            return response.data is not None and len(response.data) > 0

        except Exception as e:
            raise Exception(f"Error deleting rifle: {str(e)}")


def _type_check() -> None:
    """
    Type checker validation function.

    This function is never called at runtime - it exists only to verify
    that RiflesAPI correctly implements RiflesAPIProtocol.

    Static type checkers (mypy, pyright) will verify this at compile time.
    """

    def check(api: RiflesAPIProtocol) -> None:
        pass

    # This line will cause a type error if RiflesAPI doesn't match the protocol
    check(RiflesAPI(None))  # type: ignore