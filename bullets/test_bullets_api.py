"""
Test suite for Bullets API validation.

This test validates that the bullets module API works end-to-end:
- API facade implements protocol correctly
- Type safety is maintained
- Integration with service layer works
- Module exports are correct
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List

# Test imports work correctly
from bullets import BulletsAPI, BulletModel, BulletsAPIProtocol


class TestBulletsAPIImports:
    """Test that module exports work correctly."""

    def test_can_import_from_bullets_module(self):
        """Verify clean imports from bullets module."""
        from bullets import BulletsAPI, BulletModel, BulletsAPIProtocol

        assert BulletsAPI is not None
        assert BulletModel is not None
        assert BulletsAPIProtocol is not None

    def test_can_import_from_submodules(self):
        """Verify imports from submodules still work."""
        from bullets.api import BulletsAPI
        from bullets.models import BulletModel
        from bullets.protocols import BulletsAPIProtocol

        assert BulletsAPI is not None
        assert BulletModel is not None
        assert BulletsAPIProtocol is not None


class TestBulletsAPIProtocolCompliance:
    """Test that BulletsAPI implements BulletsAPIProtocol correctly."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        return Mock()

    @pytest.fixture
    def api(self, mock_supabase):
        """BulletsAPI instance with mocked Supabase."""
        return BulletsAPI(mock_supabase)

    def test_api_has_all_protocol_methods(self, api):
        """Verify API has all required protocol methods."""
        # Public methods
        assert hasattr(api, 'get_all_bullets')
        assert hasattr(api, 'get_bullet_by_id')
        assert hasattr(api, 'get_bullets_by_ids')
        assert hasattr(api, 'filter_bullets')
        assert hasattr(api, 'get_unique_manufacturers')
        assert hasattr(api, 'get_unique_bore_diameters')
        assert hasattr(api, 'get_unique_weights')

        # Admin methods
        assert hasattr(api, 'create_bullet')
        assert hasattr(api, 'update_bullet')
        assert hasattr(api, 'delete_bullet')

    def test_api_methods_are_callable(self, api):
        """Verify all API methods are callable."""
        assert callable(api.get_all_bullets)
        assert callable(api.get_bullet_by_id)
        assert callable(api.get_bullets_by_ids)
        assert callable(api.filter_bullets)
        assert callable(api.get_unique_manufacturers)
        assert callable(api.get_unique_bore_diameters)
        assert callable(api.get_unique_weights)
        assert callable(api.create_bullet)
        assert callable(api.update_bullet)
        assert callable(api.delete_bullet)


class TestBulletsAPIFunctionality:
    """Test actual API functionality with mocked service."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        mock = Mock()
        # Setup default table chain
        mock.table.return_value.select.return_value.execute.return_value = \
            MagicMock(data=[])
        return mock

    @pytest.fixture
    def api(self, mock_supabase):
        """BulletsAPI instance."""
        return BulletsAPI(mock_supabase)

    def test_get_all_bullets_returns_typed_list(self, api, mock_supabase):
        """Verify get_all_bullets returns List[BulletModel]."""
        # Mock response
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = \
            MagicMock(data=[
                {
                    'id': '1',
                    'user_id': 'admin',
                    'manufacturer': 'Sierra',
                    'model': 'MatchKing',
                    'weight_grains': 168,
                    'bullet_diameter_groove_mm': 7.82,
                    'bore_diameter_land_mm': 7.62,
                }
            ])

        bullets = api.get_all_bullets()

        assert isinstance(bullets, list)
        assert len(bullets) == 1
        assert isinstance(bullets[0], BulletModel)
        assert bullets[0].manufacturer == 'Sierra'

    def test_get_bullet_by_id_returns_optional_bulletmodel(self, api, mock_supabase):
        """Verify get_bullet_by_id returns Optional[BulletModel]."""
        # Mock response
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = \
            MagicMock(data={
                'id': '1',
                'user_id': 'admin',
                'manufacturer': 'Hornady',
                'model': 'ELD-M',
                'weight_grains': 147,
                'bullet_diameter_groove_mm': 6.71,
                'bore_diameter_land_mm': 6.5,
            })

        bullet = api.get_bullet_by_id('1')

        assert bullet is not None
        assert isinstance(bullet, BulletModel)
        assert bullet.manufacturer == 'Hornady'

    def test_get_bullets_by_ids_batch_operation(self, api, mock_supabase):
        """Verify get_bullets_by_ids batch loads bullets."""
        # Mock response
        mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value = \
            MagicMock(data=[
                {
                    'id': '1',
                    'user_id': 'admin',
                    'manufacturer': 'Sierra',
                    'model': 'MatchKing',
                    'weight_grains': 168,
                    'bullet_diameter_groove_mm': 7.82,
                    'bore_diameter_land_mm': 7.62,
                },
                {
                    'id': '2',
                    'user_id': 'admin',
                    'manufacturer': 'Hornady',
                    'model': 'ELD-M',
                    'weight_grains': 147,
                    'bullet_diameter_groove_mm': 6.71,
                    'bore_diameter_land_mm': 6.5,
                }
            ])

        bullet_ids = ['1', '2']
        bullets = api.get_bullets_by_ids(bullet_ids)

        assert isinstance(bullets, list)
        assert len(bullets) == 2
        assert all(isinstance(b, BulletModel) for b in bullets)

    def test_get_bullets_by_ids_empty_list(self, api):
        """Verify get_bullets_by_ids handles empty input."""
        bullets = api.get_bullets_by_ids([])

        assert isinstance(bullets, list)
        assert len(bullets) == 0

    def test_filter_bullets_with_no_filters(self, api, mock_supabase):
        """Verify filter_bullets with no filters returns all bullets."""
        # The service method will be called, which calls the DB
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = \
            MagicMock(data=[])

        bullets = api.filter_bullets()

        assert isinstance(bullets, list)

    def test_filter_bullets_with_manufacturer(self, api, mock_supabase):
        """Verify filter_bullets filters by manufacturer."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = \
            MagicMock(data=[])

        bullets = api.filter_bullets(manufacturer="Sierra")

        assert isinstance(bullets, list)


class TestBulletModel:
    """Test BulletModel functionality."""

    def test_bullet_model_creation(self):
        """Verify BulletModel can be created."""
        bullet = BulletModel(
            id='1',
            user_id='admin',
            manufacturer='Sierra',
            model='MatchKing',
            weight_grains=168.0,
            bullet_diameter_groove_mm=7.82,
            bore_diameter_land_mm=7.62,
        )

        assert bullet.id == '1'
        assert bullet.manufacturer == 'Sierra'
        assert bullet.model == 'MatchKing'

    def test_bullet_model_display_name_uses_bore_diameter(self):
        """Verify display_name uses bore_diameter_land_mm (caliber)."""
        bullet = BulletModel(
            id='1',
            user_id='admin',
            manufacturer='Sierra',
            model='MatchKing',
            weight_grains=168.0,
            bullet_diameter_groove_mm=7.82,
            bore_diameter_land_mm=7.62,  # Caliber (.308)
        )

        expected = "Sierra MatchKing - 168.0gr - 7.62mm"
        assert bullet.display_name == expected

    def test_bullet_model_from_supabase_record(self):
        """Verify BulletModel.from_supabase_record works."""
        record = {
            'id': '1',
            'user_id': 'admin',
            'manufacturer': 'Sierra',
            'model': 'MatchKing',
            'weight_grains': 168,
            'bullet_diameter_groove_mm': 7.82,
            'bore_diameter_land_mm': 7.62,
        }

        bullet = BulletModel.from_supabase_record(record)

        assert isinstance(bullet, BulletModel)
        assert bullet.id == '1'
        assert bullet.manufacturer == 'Sierra'

    def test_bullet_model_to_dict(self):
        """Verify BulletModel.to_dict works."""
        bullet = BulletModel(
            id='1',
            user_id='admin',
            manufacturer='Sierra',
            model='MatchKing',
            weight_grains=168.0,
            bullet_diameter_groove_mm=7.82,
            bore_diameter_land_mm=7.62,
        )

        bullet_dict = bullet.to_dict()

        assert isinstance(bullet_dict, dict)
        assert bullet_dict['manufacturer'] == 'Sierra'
        assert bullet_dict['weight_grains'] == 168.0


class TestTypeSafety:
    """Test that type safety is maintained."""

    def test_api_type_hints_are_correct(self):
        """Verify API method type hints match protocol."""
        from bullets.api import BulletsAPI
        import inspect

        # Check get_all_bullets return type
        sig = inspect.signature(BulletsAPI.get_all_bullets)
        return_annotation = sig.return_annotation
        assert return_annotation == List[BulletModel]

    def test_protocol_type_check_passes(self):
        """Verify the protocol type check function exists."""
        from bullets.api import _type_check

        # This function exists to satisfy type checkers
        # It should not raise any errors when type-checked
        assert callable(_type_check)


# Integration test (would need real Supabase in integration test suite)
class TestIntegration:
    """
    Integration tests (require real Supabase connection).

    These are marked as integration tests and should be run separately.
    """

    @pytest.mark.integration
    def test_end_to_end_bullet_retrieval(self):
        """
        End-to-end test with real Supabase (integration test).

        This test requires a real Supabase connection and should be run
        as part of integration testing, not unit testing.
        """
        # This would require real supabase_client
        # supabase_client = get_real_supabase_client()
        # api = BulletsAPI(supabase_client)
        # bullets = api.get_all_bullets()
        # assert isinstance(bullets, list)
        pass


if __name__ == '__main__':
    # Run tests with: python -m pytest bullets/test_bullets_api.py -v
    pytest.main([__file__, '-v'])