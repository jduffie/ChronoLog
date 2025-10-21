"""
Rifles Module API Protocol

This module defines the type-safe protocol (interface) for the Rifles API.
Using Python's Protocol class provides compile-time type checking without
runtime overhead of abstract base classes.

The RiflesAPIProtocol defines the complete public API contract for rifle operations.
All implementations must provide these methods with matching signatures.

Ownership Model:
    Rifles are user-scoped only (each rifle belongs to a single user).
    No global/shared rifles.

Type Safety:
    - All methods are fully type-hinted
    - Return types use domain models (RifleModel)
    - Enables static type checking with mypy/pyright

Example:
    >>> from rifles import RiflesAPI, RiflesAPIProtocol
    >>> from typing import TYPE_CHECKING
    >>>
    >>> if TYPE_CHECKING:
    >>>     api: RiflesAPIProtocol = RiflesAPI(supabase_client)
    >>>
    >>> # Type checker ensures this matches protocol
    >>> rifles = api.get_all_rifles(user_id)  # -> List[RifleModel]
"""

from typing import List, Optional, Protocol

from .models import RifleModel


class RiflesAPIProtocol(Protocol):
    """
    Protocol defining the public API contract for rifle operations.

    All rifle operations are user-scoped - each rifle belongs to a single user.

    Methods are organized into categories:
    - Read operations: get_all_rifles, get_rifle_by_id, get_rifle_by_name,
                      filter_rifles
    - Metadata operations: get_unique_cartridge_types, get_unique_twist_ratios
    - Write operations: create_rifle, update_rifle, delete_rifle
    - Batch operations: get_rifles_by_ids (if needed)

    Type Safety:
        All methods use RifleModel for type safety and clear contracts.
        Optional parameters are explicitly typed.
    """

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

    # Write Operations

    def create_rifle(self, rifle_data: dict, user_id: str) -> RifleModel:
        """
        Create a new rifle.

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
            Created RifleModel with generated ID

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
            >>> print(f"Created: {rifle.id}")
        """
        ...

    def update_rifle(
        self, rifle_id: str, updates: dict, user_id: str
    ) -> RifleModel:
        """
        Update an existing rifle.

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
        ...

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
            ...     print("Rifle deleted")
        """
        ...


def _type_check_rifles() -> None:
    """
    Type checker validation function.

    This function is never called at runtime - it exists only to verify
    that RiflesAPI correctly implements RiflesAPIProtocol.

    Static type checkers (mypy, pyright) will verify this at compile time.
    """
    from .api import RiflesAPI  # type: ignore

    def check(api: RiflesAPIProtocol) -> None:
        pass

    # This line will cause a type error if RiflesAPI doesn't match the protocol
    check(RiflesAPI(None))  # type: ignore