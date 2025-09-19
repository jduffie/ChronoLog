"""
Comprehensive tests for chronograph API endpoints.

This module provides unit and integration tests for the chronograph API,
following the project's testing patterns with mocked Supabase client.
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chronograph.api import router
from chronograph.api_models import (
    BulkMeasurementRequest,
    ChronographMeasurementRequest,
    ChronographSessionRequest,
    ChronographSourceRequest,
)
from chronograph.chronograph_session_models import (
    ChronographMeasurement,
    ChronographSession,
)
from chronograph.chronograph_source_models import ChronographSource
from chronograph.service import ChronographService

# Test app setup
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestChronographAPI:
    """Test class for chronograph API endpoints"""

    def setup_method(self):
        """Setup test fixtures"""
        self.user_id = "test_user_123"
        self.session_id = str(uuid.uuid4())
        self.measurement_id = str(uuid.uuid4())
        self.source_id = str(uuid.uuid4())

        # Mock authentication
        self.auth_patcher = patch('chronograph.api.get_current_user_id')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = self.user_id

        # Mock service
        self.service_patcher = patch('chronograph.api.get_chronograph_service')
        self.mock_service_dep = self.service_patcher.start()
        self.mock_service = Mock(spec=ChronographService)
        self.mock_service_dep.return_value = self.mock_service

    def teardown_method(self):
        """Cleanup after tests"""
        self.auth_patcher.stop()
        self.service_patcher.stop()

    def create_sample_session(self) -> ChronographSession:
        """Create a sample chronograph session for testing"""
        return ChronographSession(
            id=self.session_id,
            user_id=self.user_id,
            tab_name="Test Session",
            session_name="308 Winchester Test",
            datetime_local=datetime.now(),
            uploaded_at=datetime.now(),
            file_path="test/file.xlsx",
            chronograph_source_id=self.source_id,
            shot_count=5,
            avg_speed_mps=762.5,
            std_dev_mps=8.2,
            min_speed_mps=751.3,
            max_speed_mps=775.1,
        )

    def create_sample_measurement(self) -> ChronographMeasurement:
        """Create a sample chronograph measurement for testing"""
        return ChronographMeasurement(
            id=self.measurement_id,
            user_id=self.user_id,
            chrono_session_id=self.session_id,
            shot_number=1,
            speed_mps=762.5,
            datetime_local=datetime.now(),
            delta_avg_mps=0.0,
            ke_j=3456.2,
            power_factor_kgms=0.0123,
        )

    def create_sample_source(self) -> ChronographSource:
        """Create a sample chronograph source for testing"""
        return ChronographSource(
            id=self.source_id,
            user_id=self.user_id,
            name="Test Chronograph",
            source_type="chronograph",
            device_name="Garmin Xero C1",
            make="Garmin",
            model="Xero C1",
            serial_number="123456789",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    # Session endpoint tests
    def test_list_sessions_success(self):
        """Test successful session listing with pagination"""
        # Setup
        sessions = [self.create_sample_session()]
        self.mock_service.get_sessions_filtered.return_value = sessions

        # Execute
        response = client.get("/api/v1/chronograph/sessions?page=1&size=20")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["size"] == 20
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == self.session_id

        self.mock_service.get_sessions_filtered.assert_called_once_with(
            user_id=self.user_id,
            bullet_type=None,
            start_date=None,
            end_date=None,
        )

    def test_list_sessions_with_filters(self):
        """Test session listing with filters"""
        # Setup
        self.mock_service.get_sessions_filtered.return_value = []

        # Execute
        response = client.get(
            "/api/v1/chronograph/sessions"
            "?bullet_type=308 Winchester"
            "&start_date=2025-01-01T00:00:00"
            "&end_date=2025-01-31T23:59:59"
        )

        # Assert
        assert response.status_code == 200
        self.mock_service.get_sessions_filtered.assert_called_once_with(
            user_id=self.user_id,
            bullet_type="308 Winchester",
            start_date="2025-01-01T00:00:00",
            end_date="2025-01-31T23:59:59",
        )

    def test_create_session_success(self):
        """Test successful session creation"""
        # Setup
        session_data = ChronographSessionRequest(
            tab_name="Test Session",
            session_name="308 Winchester Test",
            datetime_local=datetime.now(),
            file_path="test/file.xlsx",
            chronograph_source_id=self.source_id,
        )
        self.mock_service.session_exists.return_value = False
        self.mock_service.save_chronograph_session.return_value = self.session_id

        # Execute
        response = client.post(
            "/api/v1/chronograph/sessions",
            json=session_data.dict(),
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["tab_name"] == session_data.tab_name
        assert data["session_name"] == session_data.session_name
        assert data["user_id"] == self.user_id

    def test_create_session_conflict(self):
        """Test session creation with conflict"""
        # Setup
        session_data = ChronographSessionRequest(
            tab_name="Test Session",
            session_name="308 Winchester Test",
            datetime_local=datetime.now(),
        )
        self.mock_service.session_exists.return_value = True

        # Execute
        response = client.post(
            "/api/v1/chronograph/sessions",
            json=session_data.dict(),
        )

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["message"]

    def test_get_session_success(self):
        """Test successful session retrieval"""
        # Setup
        session = self.create_sample_session()
        self.mock_service.get_session_by_id.return_value = session

        # Execute
        response = client.get(f"/api/v1/chronograph/sessions/{self.session_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.session_id
        assert data["user_id"] == self.user_id

    def test_get_session_not_found(self):
        """Test session retrieval when not found"""
        # Setup
        self.mock_service.get_session_by_id.return_value = None

        # Execute
        response = client.get(f"/api/v1/chronograph/sessions/{self.session_id}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["message"]

    def test_get_session_statistics_success(self):
        """Test successful session statistics calculation"""
        # Setup
        session = self.create_sample_session()
        speeds = [751.3, 762.5, 775.1, 760.2, 768.9]
        self.mock_service.get_session_by_id.return_value = session
        self.mock_service.get_measurements_for_stats.return_value = speeds

        with patch('chronograph.api.SessionStatisticsCalculator.calculate_session_stats') as mock_calc:
            mock_calc.return_value = {
                "avg_speed_mps": 763.6,
                "std_dev_mps": 8.2,
                "min_speed_mps": 751.3,
                "max_speed_mps": 775.1,
            }

            # Execute
            response = client.get(f"/api/v1/chronograph/sessions/{self.session_id}/statistics")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == self.session_id
            assert data["shot_count"] == 5
            assert data["avg_speed_mps"] == 763.6
            assert data["extreme_spread_mps"] == 23.8

    # Measurement endpoint tests
    def test_list_measurements_for_session_success(self):
        """Test successful measurement listing for session"""
        # Setup
        session = self.create_sample_session()
        measurements = [self.create_sample_measurement()]
        self.mock_service.get_session_by_id.return_value = session
        self.mock_service.get_measurements_for_session.return_value = measurements

        # Execute
        response = client.get(f"/api/v1/chronograph/sessions/{self.session_id}/measurements")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == self.measurement_id

    def test_create_measurement_success(self):
        """Test successful measurement creation"""
        # Setup
        measurement_data = ChronographMeasurementRequest(
            chrono_session_id=self.session_id,
            shot_number=1,
            speed_mps=762.5,
            datetime_local=datetime.now(),
        )
        session = self.create_sample_session()
        self.mock_service.get_session_by_id.return_value = session
        self.mock_service.save_chronograph_measurement.return_value = self.measurement_id

        # Execute
        response = client.post(
            "/api/v1/chronograph/measurements",
            json=measurement_data.dict(),
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["chrono_session_id"] == self.session_id
        assert data["shot_number"] == 1
        assert data["speed_mps"] == 762.5

    def test_create_measurement_invalid_session(self):
        """Test measurement creation with invalid session"""
        # Setup
        measurement_data = ChronographMeasurementRequest(
            chrono_session_id=self.session_id,
            shot_number=1,
            speed_mps=762.5,
            datetime_local=datetime.now(),
        )
        self.mock_service.get_session_by_id.return_value = None

        # Execute
        response = client.post(
            "/api/v1/chronograph/measurements",
            json=measurement_data.dict(),
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["message"]

    def test_create_measurements_bulk_success(self):
        """Test successful bulk measurement creation"""
        # Setup
        measurements_data = [
            ChronographMeasurementRequest(
                chrono_session_id=self.session_id,
                shot_number=1,
                speed_mps=762.5,
                datetime_local=datetime.now(),
            ),
            ChronographMeasurementRequest(
                chrono_session_id=self.session_id,
                shot_number=2,
                speed_mps=765.1,
                datetime_local=datetime.now() + timedelta(seconds=30),
            ),
        ]
        bulk_data = BulkMeasurementRequest(measurements=measurements_data)
        session = self.create_sample_session()
        self.mock_service.get_session_by_id.return_value = session
        self.mock_service.save_chronograph_measurement.side_effect = [str(uuid.uuid4()), str(uuid.uuid4())]

        # Execute
        response = client.post(
            "/api/v1/chronograph/measurements/bulk",
            json=bulk_data.dict(),
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 2
        assert self.mock_service.save_chronograph_measurement.call_count == 2
        assert self.mock_service.calculate_and_update_session_stats.called

    # Source endpoint tests
    def test_list_sources_success(self):
        """Test successful source listing"""
        # Setup
        sources = [self.create_sample_source()]
        self.mock_service.get_sources_for_user.return_value = sources

        # Execute
        response = client.get("/api/v1/chronograph/sources")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == self.source_id

    def test_create_source_success(self):
        """Test successful source creation"""
        # Setup
        source_data = ChronographSourceRequest(
            name="Test Chronograph",
            source_type="chronograph",
            device_name="Garmin Xero C1",
            make="Garmin",
            model="Xero C1",
            serial_number="123456789",
        )
        self.mock_service.get_source_by_name.return_value = None
        self.mock_service.create_source.return_value = self.source_id
        self.mock_service.get_source_by_id.return_value = self.create_sample_source()

        # Execute
        response = client.post(
            "/api/v1/chronograph/sources",
            json=source_data.dict(),
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == source_data.name
        assert data["user_id"] == self.user_id

    def test_create_source_conflict(self):
        """Test source creation with name conflict"""
        # Setup
        source_data = ChronographSourceRequest(
            name="Test Chronograph",
            source_type="chronograph",
        )
        self.mock_service.get_source_by_name.return_value = self.create_sample_source()

        # Execute
        response = client.post(
            "/api/v1/chronograph/sources",
            json=source_data.dict(),
        )

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["message"]

    def test_get_source_success(self):
        """Test successful source retrieval"""
        # Setup
        source = self.create_sample_source()
        self.mock_service.get_source_by_id.return_value = source

        # Execute
        response = client.get(f"/api/v1/chronograph/sources/{self.source_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.source_id

    def test_update_source_success(self):
        """Test successful source update"""
        # Setup
        source_data = ChronographSourceRequest(
            name="Updated Chronograph",
            source_type="chronograph",
        )
        existing_source = self.create_sample_source()
        updated_source = self.create_sample_source()
        updated_source.name = "Updated Chronograph"

        self.mock_service.get_source_by_id.side_effect = [existing_source, updated_source]
        self.mock_service.get_source_by_name.return_value = None

        # Execute
        response = client.put(
            f"/api/v1/chronograph/sources/{self.source_id}",
            json=source_data.dict(),
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Chronograph"

    def test_delete_source_success(self):
        """Test successful source deletion"""
        # Setup
        source = self.create_sample_source()
        self.mock_service.get_source_by_id.return_value = source

        # Execute
        response = client.delete(f"/api/v1/chronograph/sources/{self.source_id}")

        # Assert
        assert response.status_code == 204
        self.mock_service.delete_source.assert_called_once_with(self.source_id, self.user_id)

    def test_delete_source_not_found(self):
        """Test source deletion when not found"""
        # Setup
        self.mock_service.get_source_by_id.return_value = None

        # Execute
        response = client.delete(f"/api/v1/chronograph/sources/{self.source_id}")

        # Assert
        assert response.status_code == 404

    # Utility endpoint tests
    def test_get_bullet_types_success(self):
        """Test successful bullet types retrieval"""
        # Setup
        bullet_types = ["308 Winchester", "223 Remington", "30-06 Springfield"]
        self.mock_service.get_unique_bullet_types.return_value = bullet_types

        # Execute
        response = client.get("/api/v1/chronograph/bullet-types")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == bullet_types

    # Validation tests
    def test_measurement_validation_invalid_speed(self):
        """Test measurement validation with invalid speed"""
        measurement_data = {
            "chrono_session_id": self.session_id,
            "shot_number": 1,
            "speed_mps": -100,  # Invalid negative speed
            "datetime_local": datetime.now().isoformat(),
        }

        response = client.post(
            "/api/v1/chronograph/measurements",
            json=measurement_data,
        )

        assert response.status_code == 422
        data = response.json()
        assert "ValidationError" in data["error"]

    def test_measurement_validation_speed_range(self):
        """Test measurement validation with out-of-range speed"""
        measurement_data = {
            "chrono_session_id": self.session_id,
            "shot_number": 1,
            "speed_mps": 5000,  # Too high
            "datetime_local": datetime.now().isoformat(),
        }

        response = client.post(
            "/api/v1/chronograph/measurements",
            json=measurement_data,
        )

        assert response.status_code == 422

    def test_pagination_validation(self):
        """Test pagination parameter validation"""
        # Test invalid page number
        response = client.get("/api/v1/chronograph/sessions?page=0")
        assert response.status_code == 422

        # Test invalid page size
        response = client.get("/api/v1/chronograph/sessions?size=200")
        assert response.status_code == 422

    def test_missing_required_fields(self):
        """Test validation of missing required fields"""
        # Missing required fields for session creation
        incomplete_data = {
            "tab_name": "Test Session",
            # Missing session_name and datetime_local
        }

        response = client.post(
            "/api/v1/chronograph/sessions",
            json=incomplete_data,
        )

        assert response.status_code == 422
        data = response.json()
        assert "ValidationError" in data["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])