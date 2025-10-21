"""
Test suite for Rifles API validation.

This test validates that the rifles module API works end-to-end:
- API facade implements protocol correctly
- Type safety is maintained
- Integration with service layer works
- Module exports are correct
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from typing import List

# Test imports work correctly
from rifles import (
    RiflesAPI,
    RifleModel,
    RiflesAPIProtocol,
)


class TestRiflesAPIImports:
    """Test that module exports work correctly."""

    def test_can_import_from_rifles_module(self):
        """Verify clean imports from rifles module."""
        from rifles import (
            RiflesAPI,
            RifleModel,
            RiflesAPIProtocol,
        )

        assert RiflesAPI is not None
        assert RifleModel is not None
        assert RiflesAPIProtocol is not None

    def test_can_import_from_submodules(self):
        """Verify imports from submodules still work."""
        from rifles.api import RiflesAPI
        from rifles.models import RifleModel
        from rifles.protocols import RiflesAPIProtocol

        assert RiflesAPI is not None
        assert RifleModel is not None
        assert RiflesAPIProtocol is not None


class TestRiflesAPIProtocolCompliance:
    """Test that RiflesAPI implements RiflesAPIProtocol correctly."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        return Mock()

    @pytest.fixture
    def api(self, mock_supabase):
        """RiflesAPI instance with mocked Supabase."""
        return RiflesAPI(mock_supabase)

    def test_api_has_all_protocol_methods(self, api):
        """Verify API has all required protocol methods."""
        # Read methods
        assert hasattr(api, "get_all_rifles")
        assert hasattr(api, "get_rifle_by_id")
        assert hasattr(api, "get_rifle_by_name")
        assert hasattr(api, "filter_rifles")

        # Metadata methods
        assert hasattr(api, "get_unique_cartridge_types")
        assert hasattr(api, "get_unique_twist_ratios")

        # Write methods
        assert hasattr(api, "create_rifle")
        assert hasattr(api, "update_rifle")
        assert hasattr(api, "delete_rifle")

    def test_api_methods_are_callable(self, api):
        """Verify all API methods are callable."""
        assert callable(api.get_all_rifles)
        assert callable(api.get_rifle_by_id)
        assert callable(api.get_rifle_by_name)
        assert callable(api.filter_rifles)
        assert callable(api.get_unique_cartridge_types)
        assert callable(api.get_unique_twist_ratios)
        assert callable(api.create_rifle)
        assert callable(api.update_rifle)
        assert callable(api.delete_rifle)


class TestRiflesAPIFunctionality:
    """Test actual API functionality with mocked service."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        mock = Mock()
        # Setup default table chain
        mock.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[]
        )
        return mock

    @pytest.fixture
    def api(self, mock_supabase):
        """RiflesAPI instance."""
        return RiflesAPI(mock_supabase)

    @pytest.fixture
    def user_id(self):
        """Test user ID."""
        return "test-user-123"

    def test_get_all_rifles_returns_typed_list(
        self, api, mock_supabase, user_id
    ):
        """Verify get_all_rifles returns List[RifleModel]."""
        # Mock response
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": "1",
                    "user_id": user_id,
                    "name": "Remington 700",
                    "cartridge_type": "6.5 Creedmoor",
                    "barrel_twist_ratio": "1:8",
                    "barrel_length": "24 inches",
                    "created_at": "2025-01-15T10:30:00",
                    "updated_at": "2025-01-15T10:30:00",
                },
                {
                    "id": "2",
                    "user_id": user_id,
                    "name": "Bergara HMR",
                    "cartridge_type": "6.5 Creedmoor",
                    "barrel_twist_ratio": "1:8",
                    "barrel_length": "26 inches",
                    "created_at": "2025-01-15T11:00:00",
                    "updated_at": "2025-01-15T11:00:00",
                },
            ]
        )

        rifles = api.get_all_rifles(user_id)

        assert isinstance(rifles, list)
        assert len(rifles) == 2
        assert all(isinstance(r, RifleModel) for r in rifles)
        assert rifles[0].name == "Remington 700"
        assert rifles[1].name == "Bergara HMR"

    def test_get_rifle_by_id_returns_optional(self, api, mock_supabase, user_id):
        """Verify get_rifle_by_id returns Optional[RifleModel]."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={
                "id": "1",
                "user_id": user_id,
                "name": "Remington 700",
                "cartridge_type": "6.5 Creedmoor",
                "barrel_twist_ratio": "1:8",
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-15T10:30:00",
            }
        )

        rifle = api.get_rifle_by_id("1", user_id)

        assert rifle is not None
        assert isinstance(rifle, RifleModel)
        assert rifle.name == "Remington 700"
        assert rifle.cartridge_type == "6.5 Creedmoor"

    def test_get_rifle_by_name_returns_optional(self, api, mock_supabase, user_id):
        """Verify get_rifle_by_name returns Optional[RifleModel]."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={
                "id": "1",
                "user_id": user_id,
                "name": "Remington 700",
                "cartridge_type": "6.5 Creedmoor",
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-15T10:30:00",
            }
        )

        rifle = api.get_rifle_by_name(user_id, "Remington 700")

        assert rifle is not None
        assert isinstance(rifle, RifleModel)
        assert rifle.name == "Remington 700"

    def test_filter_rifles_no_filters(self, api, mock_supabase, user_id):
        """Verify filter_rifles with no filters."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[]
        )

        rifles = api.filter_rifles(user_id)

        assert isinstance(rifles, list)

    def test_filter_rifles_with_cartridge_type(self, api, mock_supabase, user_id):
        """Verify filter_rifles filters by cartridge type."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[]
        )

        rifles = api.filter_rifles(user_id, cartridge_type="6.5 Creedmoor")

        assert isinstance(rifles, list)

    def test_get_unique_cartridge_types(self, api, mock_supabase, user_id):
        """Verify get_unique_cartridge_types returns list of strings."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {"cartridge_type": "6.5 Creedmoor"},
                {"cartridge_type": "308 Winchester"},
                {"cartridge_type": "6.5 Creedmoor"},  # Duplicate
            ]
        )

        types = api.get_unique_cartridge_types(user_id)

        assert isinstance(types, list)
        assert len(types) == 2  # Duplicates removed
        assert "6.5 Creedmoor" in types
        assert "308 Winchester" in types

    def test_get_unique_twist_ratios(self, api, mock_supabase, user_id):
        """Verify get_unique_twist_ratios returns list of strings."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {"barrel_twist_ratio": "1:8"},
                {"barrel_twist_ratio": "1:9"},
                {"barrel_twist_ratio": "1:8"},  # Duplicate
            ]
        )

        ratios = api.get_unique_twist_ratios(user_id)

        assert isinstance(ratios, list)
        assert len(ratios) == 2  # Duplicates removed
        assert "1:8" in ratios
        assert "1:9" in ratios

    def test_create_rifle(self, api, mock_supabase, user_id):
        """Verify create_rifle returns RifleModel."""
        rifle_data = {
            "name": "Test Rifle",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
        }

        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": "new-rifle-id",
                    "user_id": user_id,
                    "name": "Test Rifle",
                    "cartridge_type": "6.5 Creedmoor",
                    "barrel_twist_ratio": "1:8",
                    "created_at": "2025-01-15T10:30:00",
                    "updated_at": "2025-01-15T10:30:00",
                }
            ]
        )

        rifle = api.create_rifle(rifle_data, user_id)

        assert isinstance(rifle, RifleModel)
        assert rifle.name == "Test Rifle"
        assert rifle.user_id == user_id
        assert rifle.id == "new-rifle-id"

    def test_update_rifle(self, api, mock_supabase, user_id):
        """Verify update_rifle returns updated RifleModel."""
        updates = {"barrel_length": "26 inches"}

        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": "rifle-123",
                    "user_id": user_id,
                    "name": "Remington 700",
                    "cartridge_type": "6.5 Creedmoor",
                    "barrel_length": "26 inches",
                    "created_at": "2025-01-15T10:30:00",
                    "updated_at": "2025-01-15T11:00:00",
                }
            ]
        )

        rifle = api.update_rifle("rifle-123", updates, user_id)

        assert isinstance(rifle, RifleModel)
        assert rifle.barrel_length == "26 inches"

    def test_delete_rifle_success(self, api, mock_supabase, user_id):
        """Verify delete_rifle returns True when successful."""
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "rifle-123"}]  # Non-empty means success
        )

        result = api.delete_rifle("rifle-123", user_id)

        assert result is True

    def test_delete_rifle_not_found(self, api, mock_supabase, user_id):
        """Verify delete_rifle returns False when rifle not found."""
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]  # Empty means not found
        )

        result = api.delete_rifle("rifle-123", user_id)

        assert result is False


class TestRifleModel:
    """Test RifleModel functionality."""

    def test_rifle_model_creation(self):
        """Verify RifleModel can be created."""
        rifle = RifleModel(
            id="1",
            user_id="user-123",
            name="Remington 700",
            cartridge_type="6.5 Creedmoor",
            barrel_twist_ratio="1:8",
            barrel_length="24 inches",
        )

        assert rifle.id == "1"
        assert rifle.name == "Remington 700"
        assert rifle.cartridge_type == "6.5 Creedmoor"
        assert rifle.barrel_twist_ratio == "1:8"
        assert rifle.barrel_length == "24 inches"

    def test_rifle_model_display_name(self):
        """Verify display_name property."""
        rifle = RifleModel(
            id="1",
            user_id="user-123",
            name="Remington 700",
            cartridge_type="6.5 Creedmoor",
        )

        expected = "Remington 700 (6.5 Creedmoor)"
        assert rifle.display_name() == expected

    def test_rifle_model_barrel_display(self):
        """Verify barrel_display property."""
        # With both length and twist
        rifle = RifleModel(
            id="1",
            user_id="user-123",
            name="Test",
            cartridge_type="6.5 Creedmoor",
            barrel_length="24 inches",
            barrel_twist_ratio="1:8",
        )
        assert rifle.barrel_display() == "24 inches - Twist: 1:8"

        # With length only
        rifle.barrel_twist_ratio = None
        assert rifle.barrel_display() == "24 inches"

        # With twist only
        rifle.barrel_length = None
        rifle.barrel_twist_ratio = "1:8"
        assert rifle.barrel_display() == "Twist: 1:8"

        # With neither
        rifle.barrel_twist_ratio = None
        assert rifle.barrel_display() == "Not specified"

    def test_rifle_model_optics_display(self):
        """Verify optics_display property."""
        rifle = RifleModel(
            id="1",
            user_id="user-123",
            name="Test",
            cartridge_type="6.5 Creedmoor",
            scope="Vortex Viper PST 5-25x50",
            sight_offset="1.5 inches",
        )

        expected = "Scope: Vortex Viper PST 5-25x50 - Offset: 1.5 inches"
        assert rifle.optics_display() == expected

        # With scope only
        rifle.sight_offset = None
        assert rifle.optics_display() == "Scope: Vortex Viper PST 5-25x50"

        # With neither
        rifle.scope = None
        assert rifle.optics_display() == "Not specified"

    def test_rifle_model_trigger_display(self):
        """Verify trigger_display property."""
        rifle = RifleModel(
            id="1",
            user_id="user-123",
            name="Test",
            cartridge_type="6.5 Creedmoor",
            trigger="Timney 2-stage 2.5lb",
        )

        assert rifle.trigger_display() == "Timney 2-stage 2.5lb"

        rifle.trigger = None
        assert rifle.trigger_display() == "Not specified"

    def test_rifle_model_from_supabase_record(self):
        """Verify RifleModel.from_supabase_record works."""
        record = {
            "id": "1",
            "user_id": "user-123",
            "name": "Remington 700",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "24 inches",
            "created_at": "2025-01-15T10:30:00",
            "updated_at": "2025-01-15T10:30:00",
        }

        rifle = RifleModel.from_supabase_record(record)

        assert isinstance(rifle, RifleModel)
        assert rifle.id == "1"
        assert rifle.name == "Remington 700"

    def test_rifle_model_to_dict(self):
        """Verify RifleModel.to_dict works."""
        rifle = RifleModel(
            id="1",
            user_id="user-123",
            name="Remington 700",
            cartridge_type="6.5 Creedmoor",
            barrel_twist_ratio="1:8",
        )

        rifle_dict = rifle.to_dict()

        assert isinstance(rifle_dict, dict)
        assert rifle_dict["id"] == "1"
        assert rifle_dict["name"] == "Remington 700"
        assert rifle_dict["barrel_twist_ratio"] == "1:8"


class TestTypeSafety:
    """Test that type safety is maintained."""

    def test_api_type_hints_are_correct(self):
        """Verify API method type hints match protocol."""
        from rifles.api import RiflesAPI
        import inspect

        # Check get_all_rifles return type
        sig = inspect.signature(RiflesAPI.get_all_rifles)
        return_annotation = sig.return_annotation
        assert return_annotation == List[RifleModel]

    def test_protocol_type_check_passes(self):
        """Verify the protocol type check function exists."""
        from rifles.api import _type_check

        # This function exists to satisfy type checkers
        assert callable(_type_check)


if __name__ == "__main__":
    # Run tests with: python -m pytest rifles/test_rifles_api.py -v
    pytest.main([__file__, "-v"])
