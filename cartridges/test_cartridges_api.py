"""
Test suite for Cartridges API validation.

This test validates that the cartridges module API works end-to-end:
- API facade implements protocol correctly
- Type safety is maintained
- Integration with service layer works
- Module exports are correct
- Dual ownership model (global + user-owned) works correctly
"""

from typing import List
from unittest.mock import MagicMock, Mock

import pytest

# Test imports work correctly
from cartridges import (
    CartridgeModel,
    CartridgesAPI,
    CartridgesAPIProtocol,
    CartridgeTypeModel,
)


class TestCartridgesAPIImports:
    """Test that module exports work correctly."""

    def test_can_import_from_cartridges_module(self):
        """Verify clean imports from cartridges module."""
        from cartridges import (
            CartridgeModel,
            CartridgesAPI,
            CartridgesAPIProtocol,
            CartridgeTypeModel,
        )

        assert CartridgesAPI is not None
        assert CartridgeModel is not None
        assert CartridgeTypeModel is not None
        assert CartridgesAPIProtocol is not None

    def test_can_import_from_submodules(self):
        """Verify imports from submodules still work."""
        from cartridges.api import CartridgesAPI
        from cartridges.models import CartridgeModel, CartridgeTypeModel
        from cartridges.protocols import CartridgesAPIProtocol

        assert CartridgesAPI is not None
        assert CartridgeModel is not None
        assert CartridgeTypeModel is not None
        assert CartridgesAPIProtocol is not None


class TestCartridgesAPIProtocolCompliance:
    """Test that CartridgesAPI implements CartridgesAPIProtocol correctly."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        return Mock()

    @pytest.fixture
    def api(self, mock_supabase):
        """CartridgesAPI instance with mocked Supabase."""
        return CartridgesAPI(mock_supabase)

    def test_api_has_all_protocol_methods(self, api):
        """Verify API has all required protocol methods."""
        # Public methods
        assert hasattr(api, "get_all_cartridges")
        assert hasattr(api, "get_cartridge_by_id")
        assert hasattr(api, "get_cartridges_by_ids")
        assert hasattr(api, "filter_cartridges")
        assert hasattr(api, "get_cartridge_types")
        assert hasattr(api, "get_unique_makes")
        assert hasattr(api, "get_unique_models")

        # User methods
        assert hasattr(api, "create_user_cartridge")
        assert hasattr(api, "update_user_cartridge")
        assert hasattr(api, "delete_user_cartridge")

        # Admin methods
        assert hasattr(api, "create_global_cartridge")
        assert hasattr(api, "update_global_cartridge")
        assert hasattr(api, "delete_global_cartridge")

    def test_api_methods_are_callable(self, api):
        """Verify all API methods are callable."""
        assert callable(api.get_all_cartridges)
        assert callable(api.get_cartridge_by_id)
        assert callable(api.get_cartridges_by_ids)
        assert callable(api.filter_cartridges)
        assert callable(api.get_cartridge_types)
        assert callable(api.get_unique_makes)
        assert callable(api.get_unique_models)
        assert callable(api.create_user_cartridge)
        assert callable(api.update_user_cartridge)
        assert callable(api.delete_user_cartridge)
        assert callable(api.create_global_cartridge)
        assert callable(api.update_global_cartridge)
        assert callable(api.delete_global_cartridge)


class TestCartridgesAPIFunctionality:
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
        """CartridgesAPI instance."""
        return CartridgesAPI(mock_supabase)

    @pytest.fixture
    def user_id(self):
        """Test user ID."""
        return "test-user-123"

    def test_get_all_cartridges_returns_typed_list(
        self, api, mock_supabase, user_id
    ):
        """Verify get_all_cartridges returns List[CartridgeModel]."""
        # Mock response with both global and user-owned
        mock_supabase.table.return_value.select.return_value.or_.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": "1",
                    "owner_id": None,  # Global
                    "make": "Federal",
                    "model": "Gold Medal",
                    "bullet_id": "bullet-1",
                    "cartridge_type": "6.5 Creedmoor",
                    "bullets": {
                        "manufacturer": "Hornady",
                        "model": "ELD Match",
                        "weight_grains": 147,
                    },
                },
                {
                    "id": "2",
                    "owner_id": user_id,  # User-owned
                    "make": "Custom Load",
                    "model": "Match",
                    "bullet_id": "bullet-2",
                    "cartridge_type": "6.5 Creedmoor",
                    "bullets": {
                        "manufacturer": "Sierra",
                        "model": "MatchKing",
                        "weight_grains": 140,
                    },
                },
            ]
        )

        cartridges = api.get_all_cartridges(user_id)

        assert isinstance(cartridges, list)
        assert len(cartridges) == 2
        assert all(isinstance(c, CartridgeModel) for c in cartridges)
        assert cartridges[0].is_global  # First is global
        assert cartridges[1].is_user_owned  # Second is user-owned

    def test_get_cartridge_by_id_returns_optional(self, api, mock_supabase, user_id):
        """Verify get_cartridge_by_id returns Optional[CartridgeModel]."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.or_.return_value.single.return_value.execute.return_value = MagicMock(
            data={
                "id": "1",
                "owner_id": None,
                "make": "Federal",
                "model": "Gold Medal",
                "bullet_id": "bullet-1",
                "cartridge_type": "6.5 Creedmoor",
                "bullets": {
                    "manufacturer": "Hornady",
                    "model": "ELD Match",
                    "weight_grains": 147,
                },
            }
        )

        cartridge = api.get_cartridge_by_id("1", user_id)

        assert cartridge is not None
        assert isinstance(cartridge, CartridgeModel)
        assert cartridge.make == "Federal"
        assert cartridge.is_global

    def test_get_cartridges_by_ids_batch_operation(
        self, api, mock_supabase, user_id
    ):
        """Verify get_cartridges_by_ids batch loads cartridges."""
        mock_supabase.table.return_value.select.return_value.in_.return_value.or_.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": "1",
                    "owner_id": None,
                    "make": "Federal",
                    "model": "Gold Medal",
                    "bullet_id": "bullet-1",
                    "cartridge_type": "6.5 Creedmoor",
                    "bullets": {"manufacturer": "Hornady"},
                },
                {
                    "id": "2",
                    "owner_id": user_id,
                    "make": "Custom Load",
                    "model": "Match",
                    "bullet_id": "bullet-2",
                    "cartridge_type": "6.5 Creedmoor",
                    "bullets": {"manufacturer": "Sierra"},
                },
            ]
        )

        cartridge_ids = ["1", "2"]
        cartridges = api.get_cartridges_by_ids(cartridge_ids, user_id)

        assert isinstance(cartridges, list)
        assert len(cartridges) == 2
        assert all(isinstance(c, CartridgeModel) for c in cartridges)

    def test_get_cartridges_by_ids_empty_list(self, api, user_id):
        """Verify get_cartridges_by_ids handles empty input."""
        cartridges = api.get_cartridges_by_ids([], user_id)

        assert isinstance(cartridges, list)
        assert len(cartridges) == 0

    def test_filter_cartridges_no_filters(self, api, mock_supabase, user_id):
        """Verify filter_cartridges with no filters."""
        mock_supabase.table.return_value.select.return_value.or_.return_value.execute.return_value = MagicMock(
            data=[]
        )

        cartridges = api.filter_cartridges(user_id)

        assert isinstance(cartridges, list)

    def test_filter_cartridges_with_make(self, api, mock_supabase, user_id):
        """Verify filter_cartridges filters by make."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.or_.return_value.execute.return_value = MagicMock(
            data=[]
        )

        cartridges = api.filter_cartridges(user_id, make="Federal")

        assert isinstance(cartridges, list)

    def test_get_cartridge_types(self, api, mock_supabase):
        """Verify get_cartridge_types returns list of strings."""
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[{"name": "6.5 Creedmoor"}, {"name": ".308 Winchester"}]
        )

        types = api.get_cartridge_types()

        assert isinstance(types, list)


class TestCartridgeModel:
    """Test CartridgeModel functionality."""

    def test_cartridge_model_creation(self):
        """Verify CartridgeModel can be created."""
        cartridge = CartridgeModel(
            id="1",
            owner_id=None,
            make="Federal",
            model="Gold Medal",
            bullet_id="bullet-1",
            cartridge_type="6.5 Creedmoor",
        )

        assert cartridge.id == "1"
        assert cartridge.make == "Federal"
        assert cartridge.model == "Gold Medal"
        assert cartridge.is_global

    def test_cartridge_model_display_name(self):
        """Verify display_name property."""
        cartridge = CartridgeModel(
            id="1",
            owner_id=None,
            make="Federal",
            model="Gold Medal",
            bullet_id="bullet-1",
            cartridge_type="6.5 Creedmoor",
        )

        expected = "Federal Gold Medal (6.5 Creedmoor)"
        assert cartridge.display_name == expected

    def test_cartridge_model_is_global(self):
        """Verify is_global property."""
        global_cart = CartridgeModel(
            id="1",
            owner_id=None,  # Global
            make="Federal",
            model="Gold Medal",
            bullet_id="bullet-1",
            cartridge_type="6.5 Creedmoor",
        )

        user_cart = CartridgeModel(
            id="2",
            owner_id="user-123",  # User-owned
            make="Custom Load",
            model="Match",
            bullet_id="bullet-2",
            cartridge_type="6.5 Creedmoor",
        )

        assert global_cart.is_global is True
        assert global_cart.is_user_owned is False

        assert user_cart.is_global is False
        assert user_cart.is_user_owned is True

    def test_cartridge_model_from_supabase_record(self):
        """Verify CartridgeModel.from_supabase_record works."""
        record = {
            "id": "1",
            "owner_id": None,
            "make": "Federal",
            "model": "Gold Medal",
            "bullet_id": "bullet-1",
            "cartridge_type": "6.5 Creedmoor",
            "bullet_manufacturer": "Hornady",
            "bullet_model": "ELD Match",
            "bullet_weight_grains": 147,
        }

        cartridge = CartridgeModel.from_supabase_record(record)

        assert isinstance(cartridge, CartridgeModel)
        assert cartridge.id == "1"
        assert cartridge.make == "Federal"
        assert cartridge.bullet_manufacturer == "Hornady"

    def test_cartridge_model_to_dict(self):
        """Verify CartridgeModel.to_dict works."""
        cartridge = CartridgeModel(
            id="1",
            owner_id=None,
            make="Federal",
            model="Gold Medal",
            bullet_id="bullet-1",
            cartridge_type="6.5 Creedmoor",
        )

        cart_dict = cartridge.to_dict()

        assert isinstance(cart_dict, dict)
        assert cart_dict["make"] == "Federal"
        assert cart_dict["model"] == "Gold Medal"


class TestTypeSafety:
    """Test that type safety is maintained."""

    def test_api_type_hints_are_correct(self):
        """Verify API method type hints match protocol."""
        import inspect

        from cartridges.api import CartridgesAPI

        # Check get_all_cartridges return type
        sig = inspect.signature(CartridgesAPI.get_all_cartridges)
        return_annotation = sig.return_annotation
        assert return_annotation == List[CartridgeModel]

    def test_protocol_type_check_passes(self):
        """Verify the protocol type check function exists."""
        from cartridges.api import _type_check

        # This function exists to satisfy type checkers
        assert callable(_type_check)


if __name__ == "__main__":
    # Run tests with: python -m pytest cartridges/test_cartridges_api.py -v
    pytest.main([__file__, "-v"])