"""
Unit tests for DOPE Analytics module
"""

import sys
import os
from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dope.analytics.filters import SessionFilter
from dope.analytics.analytics_service import AnalyticsService
from dope.models import DopeSessionModel, DopeMeasurementModel


class TestSessionFilter:
    """Test SessionFilter dataclass"""

    def test_filter_creation_with_defaults(self):
        """Test creating filter with default values"""
        filter = SessionFilter()
        assert filter.rifle_id is None
        assert filter.cartridge_id is None
        assert not filter.has_filters()

    def test_filter_creation_with_values(self):
        """Test creating filter with specific values"""
        filter = SessionFilter(
            rifle_id="rifle-123",
            cartridge_type="308 Winchester",
            start_date=datetime(2025, 1, 1),
        )
        assert filter.rifle_id == "rifle-123"
        assert filter.cartridge_type == "308 Winchester"
        assert filter.start_date == datetime(2025, 1, 1)
        assert filter.has_filters()

    def test_has_filters_returns_true_for_rifle_filter(self):
        """Test has_filters detects rifle filter"""
        filter = SessionFilter(rifle_id="rifle-123")
        assert filter.has_filters()

    def test_has_filters_returns_true_for_date_filter(self):
        """Test has_filters detects date filter"""
        filter = SessionFilter(start_date=datetime(2025, 1, 1))
        assert filter.has_filters()

    def test_has_filters_returns_false_for_empty(self):
        """Test has_filters returns False when empty"""
        filter = SessionFilter()
        assert not filter.has_filters()

    def test_to_dict_converts_dates(self):
        """Test to_dict converts datetime to ISO format"""
        start = datetime(2025, 1, 1, 10, 30)
        filter = SessionFilter(start_date=start)
        result = filter.to_dict()
        assert result["start_date"] == start.isoformat()

    def test_to_dict_handles_none_dates(self):
        """Test to_dict handles None dates"""
        filter = SessionFilter()
        result = filter.to_dict()
        assert result["start_date"] is None
        assert result["end_date"] is None


class TestAnalyticsService:
    """Test AnalyticsService class"""

    @pytest.fixture
    def mock_supabase(self):
        """Create mock Supabase client"""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_supabase):
        """Create AnalyticsService instance"""
        return AnalyticsService(mock_supabase)

    @pytest.fixture
    def sample_sessions(self):
        """Create sample DOPE sessions for testing"""
        return [
            DopeSessionModel(
                id="session-1",
                user_id="user-123",
                session_name="Session 1",
                rifle_id="rifle-1",
                cartridge_id="cart-1",
                bullet_id="bullet-1",
                cartridge_type="308 Winchester",
                speed_mps_avg=800.0,
                temperature_c_median=20.0,
                start_time=datetime(2025, 1, 1),
                end_time=datetime(2025, 1, 1, 1, 0),
            ),
            DopeSessionModel(
                id="session-2",
                user_id="user-123",
                session_name="Session 2",
                rifle_id="rifle-2",
                cartridge_id="cart-1",
                bullet_id="bullet-1",
                cartridge_type="308 Winchester",
                speed_mps_avg=805.0,
                temperature_c_median=25.0,
                start_time=datetime(2025, 1, 2),
                end_time=datetime(2025, 1, 2, 1, 0),
            ),
            DopeSessionModel(
                id="session-3",
                user_id="user-123",
                session_name="Session 3",
                rifle_id="rifle-1",
                cartridge_id="cart-2",
                bullet_id="bullet-2",
                cartridge_type="6.5 Creedmoor",
                speed_mps_avg=750.0,
                temperature_c_median=15.0,
                start_time=datetime(2025, 1, 3),
                end_time=datetime(2025, 1, 3, 1, 0),
            ),
        ]

    def test_service_creation_requires_supabase(self):
        """Test service creation validates Supabase client"""
        with pytest.raises(ValueError, match="Supabase client is required"):
            AnalyticsService(None)

    def test_service_creation_success(self, mock_supabase):
        """Test service creates successfully with valid client"""
        service = AnalyticsService(mock_supabase)
        assert service is not None
        assert service._supabase is mock_supabase

    def test_get_sessions_for_analysis_no_filters(self, service, sample_sessions, mocker):
        """Test getting sessions without filters returns all"""
        # Mock the DopeAPI.get_sessions_for_user method
        mocker.patch.object(
            service._dope_api, "get_sessions_for_user", return_value=sample_sessions
        )

        result = service.get_sessions_for_analysis("user-123")

        assert len(result) == 3
        assert result == sample_sessions

    def test_get_sessions_for_analysis_with_rifle_filter(
        self, service, sample_sessions, mocker
    ):
        """Test filtering sessions by rifle_id"""
        mocker.patch.object(
            service._dope_api, "get_sessions_for_user", return_value=sample_sessions
        )

        filter = SessionFilter(rifle_id="rifle-1")
        result = service.get_sessions_for_analysis("user-123", filter)

        assert len(result) == 2
        assert all(s.rifle_id == "rifle-1" for s in result)

    def test_get_sessions_for_analysis_with_cartridge_type_filter(
        self, service, sample_sessions, mocker
    ):
        """Test filtering sessions by cartridge type"""
        mocker.patch.object(
            service._dope_api, "get_sessions_for_user", return_value=sample_sessions
        )

        filter = SessionFilter(cartridge_type="308 Winchester")
        result = service.get_sessions_for_analysis("user-123", filter)

        assert len(result) == 2
        assert all(s.cartridge_type == "308 Winchester" for s in result)

    def test_get_sessions_for_analysis_with_date_range(
        self, service, sample_sessions, mocker
    ):
        """Test filtering sessions by date range"""
        mocker.patch.object(
            service._dope_api, "get_sessions_for_user", return_value=sample_sessions
        )

        filter = SessionFilter(
            start_date=datetime(2025, 1, 2), end_date=datetime(2025, 1, 3)
        )
        result = service.get_sessions_for_analysis("user-123", filter)

        assert len(result) == 2
        assert result[0].id == "session-2"
        assert result[1].id == "session-3"

    def test_get_sessions_for_analysis_with_temperature_range(
        self, service, sample_sessions, mocker
    ):
        """Test filtering sessions by temperature range"""
        mocker.patch.object(
            service._dope_api, "get_sessions_for_user", return_value=sample_sessions
        )

        filter = SessionFilter(temperature_min_c=18.0, temperature_max_c=22.0)
        result = service.get_sessions_for_analysis("user-123", filter)

        assert len(result) == 1
        assert result[0].temperature_c_median == 20.0

    def test_get_sessions_for_analysis_with_velocity_range(
        self, service, sample_sessions, mocker
    ):
        """Test filtering sessions by velocity range"""
        mocker.patch.object(
            service._dope_api, "get_sessions_for_user", return_value=sample_sessions
        )

        filter = SessionFilter(velocity_min_mps=800.0)
        result = service.get_sessions_for_analysis("user-123", filter)

        assert len(result) == 2
        assert all(s.speed_mps_avg >= 800.0 for s in result)

    def test_get_sessions_for_analysis_with_multiple_filters(
        self, service, sample_sessions, mocker
    ):
        """Test filtering with multiple criteria"""
        mocker.patch.object(
            service._dope_api, "get_sessions_for_user", return_value=sample_sessions
        )

        filter = SessionFilter(
            rifle_id="rifle-1", cartridge_type="308 Winchester", velocity_min_mps=795.0
        )
        result = service.get_sessions_for_analysis("user-123", filter)

        assert len(result) == 1
        assert result[0].id == "session-1"

    def test_get_sessions_for_analysis_with_session_ids(
        self, service, sample_sessions, mocker
    ):
        """Test filtering by specific session IDs"""
        mocker.patch.object(
            service._dope_api, "get_sessions_for_user", return_value=sample_sessions
        )

        filter = SessionFilter(session_ids=["session-1", "session-3"])
        result = service.get_sessions_for_analysis("user-123", filter)

        assert len(result) == 2
        assert result[0].id == "session-1"
        assert result[1].id == "session-3"

    def test_get_sessions_for_analysis_with_exclude_ids(
        self, service, sample_sessions, mocker
    ):
        """Test excluding specific session IDs"""
        mocker.patch.object(
            service._dope_api, "get_sessions_for_user", return_value=sample_sessions
        )

        filter = SessionFilter(exclude_session_ids=["session-2"])
        result = service.get_sessions_for_analysis("user-123", filter)

        assert len(result) == 2
        assert all(s.id != "session-2" for s in result)

    def test_get_measurements_for_sessions(self, service, mocker):
        """Test getting measurements for multiple sessions"""
        mock_measurements = [
            DopeMeasurementModel(
                id="meas-1",
                dope_session_id="session-1",
                user_id="user-123",
                shot_number=1,
                speed_mps=800.0,
            ),
            DopeMeasurementModel(
                id="meas-2",
                dope_session_id="session-1",
                user_id="user-123",
                shot_number=2,
                speed_mps=805.0,
            ),
        ]

        mocker.patch.object(
            service._dope_api,
            "get_measurements_for_dope_session",
            return_value=mock_measurements,
        )

        result = service.get_measurements_for_sessions(
            ["session-1", "session-2"], "user-123"
        )

        # Should call get_measurements twice (once per session)
        assert service._dope_api.get_measurements_for_dope_session.call_count == 2
        # Should have 4 total measurements (2 per session)
        assert len(result) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])