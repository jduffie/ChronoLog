"""
RESTful API endpoints for chronograph module.

This module provides a comprehensive REST API for chronograph operations,
following modern API design patterns with proper authentication, validation,
and error handling.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from .api_models import (
    BulkMeasurementRequest,
    ChronographMeasurementRequest,
    ChronographMeasurementResponse,
    ChronographSessionRequest,
    ChronographSessionResponse,
    ChronographSourceRequest,
    ChronographSourceResponse,
    PaginatedResponse,
    SessionStatisticsResponse,
)
from .business_logic import SessionStatisticsCalculator
from .chronograph_session_models import ChronographMeasurement, ChronographSession
from .chronograph_source_models import ChronographSource
from .service import ChronographService

# Initialize router and security
router = APIRouter(prefix="/api/v1/chronograph", tags=["chronograph"])
security = HTTPBearer()


# Import dependency injection functions
from .api_dependencies import get_chronograph_service, get_current_user_id


# Helper functions
def convert_session_to_response(session: ChronographSession) -> ChronographSessionResponse:
    """Convert domain model to API response model"""
    return ChronographSessionResponse(
        id=session.id,
        user_id=session.user_id,
        tab_name=session.tab_name,
        session_name=session.session_name,
        datetime_local=session.datetime_local,
        uploaded_at=session.uploaded_at,
        file_path=session.file_path,
        chronograph_source_id=session.chronograph_source_id,
        shot_count=session.shot_count,
        avg_speed_mps=session.avg_speed_mps,
        std_dev_mps=session.std_dev_mps,
        min_speed_mps=session.min_speed_mps,
        max_speed_mps=session.max_speed_mps,
        created_at=session.created_at,
    )


def convert_measurement_to_response(measurement: ChronographMeasurement) -> ChronographMeasurementResponse:
    """Convert domain model to API response model"""
    return ChronographMeasurementResponse(
        id=measurement.id,
        user_id=measurement.user_id,
        chrono_session_id=measurement.chrono_session_id,
        shot_number=measurement.shot_number,
        speed_mps=measurement.speed_mps,
        datetime_local=measurement.datetime_local,
        delta_avg_mps=measurement.delta_avg_mps,
        ke_j=measurement.ke_j,
        power_factor_kgms=measurement.power_factor_kgms,
        clean_bore=measurement.clean_bore,
        cold_bore=measurement.cold_bore,
        shot_notes=measurement.shot_notes,
    )


def convert_source_to_response(source: ChronographSource) -> ChronographSourceResponse:
    """Convert domain model to API response model"""
    return ChronographSourceResponse(
        id=source.id,
        user_id=source.user_id,
        name=source.name,
        source_type=source.source_type,
        device_name=source.device_name,
        make=source.make,
        model=source.model,
        serial_number=source.serial_number,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )


# Session endpoints
@router.get(
    "/sessions",
    response_model=PaginatedResponse,
    summary="List chronograph sessions",
    description="Get a paginated list of chronograph sessions with optional filtering"
)
async def list_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    bullet_type: Optional[str] = Query(None, description="Filter by bullet type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    chronograph_source_id: Optional[str] = Query(None, description="Filter by chronograph source"),
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """List chronograph sessions with pagination and filtering"""
    try:
        # Get filtered sessions
        sessions = service.get_sessions_filtered(
            user_id=user_id,
            bullet_type=bullet_type,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
        )

        # Apply pagination
        total = len(sessions)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_sessions = sessions[start_idx:end_idx]

        # Convert to response models
        session_responses = [convert_session_to_response(session) for session in paginated_sessions]

        return PaginatedResponse(
            items=[session.dict() for session in session_responses],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        )


@router.post(
    "/sessions",
    response_model=ChronographSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chronograph session",
    description="Create a new chronograph session record"
)
async def create_session(
    session_data: ChronographSessionRequest,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Create a new chronograph session"""
    try:
        # Check if session already exists
        if service.session_exists(
            user_id=user_id,
            tab_name=session_data.tab_name,
            datetime_local=session_data.datetime_local.isoformat()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Session with this tab name and datetime already exists"
            )

        # Create session entity
        session = ChronographSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            tab_name=session_data.tab_name,
            session_name=session_data.session_name,
            datetime_local=session_data.datetime_local,
            uploaded_at=datetime.now(),
            file_path=session_data.file_path,
            chronograph_source_id=session_data.chronograph_source_id,
        )

        # Save to database
        session_id = service.save_chronograph_session(session)
        session.id = session_id

        return convert_session_to_response(session)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}",
    response_model=ChronographSessionResponse,
    summary="Get a specific chronograph session",
    description="Retrieve a chronograph session by its ID"
)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Get a specific chronograph session"""
    try:
        session = service.get_session_by_id(session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        return convert_session_to_response(session)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}/statistics",
    response_model=SessionStatisticsResponse,
    summary="Get session statistics",
    description="Calculate and return statistical analysis for a session"
)
async def get_session_statistics(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Get statistical analysis for a session"""
    try:
        # Verify session exists and belongs to user
        session = service.get_session_by_id(session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Get measurements and calculate statistics
        speeds = service.get_measurements_for_stats(user_id, session_id)
        if not speeds:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No measurements found for session"
            )

        stats = SessionStatisticsCalculator.calculate_session_stats(speeds)

        return SessionStatisticsResponse(
            session_id=session_id,
            shot_count=len(speeds),
            avg_speed_mps=stats["avg_speed_mps"],
            std_dev_mps=stats["std_dev_mps"],
            min_speed_mps=stats["min_speed_mps"],
            max_speed_mps=stats["max_speed_mps"],
            extreme_spread_mps=stats["max_speed_mps"] - stats["min_speed_mps"],
            coefficient_of_variation=(stats["std_dev_mps"] / stats["avg_speed_mps"]) * 100,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating session statistics: {str(e)}"
        )


# Measurement endpoints
@router.get(
    "/sessions/{session_id}/measurements",
    response_model=List[ChronographMeasurementResponse],
    summary="Get measurements for a session",
    description="Retrieve all measurements for a specific chronograph session"
)
async def list_measurements_for_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Get all measurements for a specific session"""
    try:
        # Verify session exists and belongs to user
        session = service.get_session_by_id(session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        measurements = service.get_measurements_for_session(user_id, session_id)
        return [convert_measurement_to_response(measurement) for measurement in measurements]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving measurements: {str(e)}"
        )


@router.post(
    "/measurements",
    response_model=ChronographMeasurementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new measurement",
    description="Create a new chronograph measurement record"
)
async def create_measurement(
    measurement_data: ChronographMeasurementRequest,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Create a new chronograph measurement"""
    try:
        # Verify session exists and belongs to user
        session = service.get_session_by_id(measurement_data.chrono_session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Create measurement entity
        measurement = ChronographMeasurement(
            id=str(uuid.uuid4()),
            user_id=user_id,
            chrono_session_id=measurement_data.chrono_session_id,
            shot_number=measurement_data.shot_number,
            speed_mps=measurement_data.speed_mps,
            datetime_local=measurement_data.datetime_local,
            delta_avg_mps=measurement_data.delta_avg_mps,
            ke_j=measurement_data.ke_j,
            power_factor_kgms=measurement_data.power_factor_kgms,
            clean_bore=measurement_data.clean_bore,
            cold_bore=measurement_data.cold_bore,
            shot_notes=measurement_data.shot_notes,
        )

        # Save to database
        measurement_id = service.save_chronograph_measurement(measurement)
        measurement.id = measurement_id

        # Recalculate session statistics
        service.calculate_and_update_session_stats(user_id, measurement_data.chrono_session_id)

        return convert_measurement_to_response(measurement)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating measurement: {str(e)}"
        )


@router.post(
    "/measurements/bulk",
    response_model=List[ChronographMeasurementResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple measurements",
    description="Create multiple chronograph measurements in a single request"
)
async def create_measurements_bulk(
    bulk_data: BulkMeasurementRequest,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Create multiple chronograph measurements in bulk"""
    try:
        created_measurements = []
        session_ids_to_update = set()

        for measurement_data in bulk_data.measurements:
            # Verify session exists and belongs to user
            session = service.get_session_by_id(measurement_data.chrono_session_id, user_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session {measurement_data.chrono_session_id} not found"
                )

            # Create measurement entity
            measurement = ChronographMeasurement(
                id=str(uuid.uuid4()),
                user_id=user_id,
                chrono_session_id=measurement_data.chrono_session_id,
                shot_number=measurement_data.shot_number,
                speed_mps=measurement_data.speed_mps,
                datetime_local=measurement_data.datetime_local,
                delta_avg_mps=measurement_data.delta_avg_mps,
                ke_j=measurement_data.ke_j,
                power_factor_kgms=measurement_data.power_factor_kgms,
                clean_bore=measurement_data.clean_bore,
                cold_bore=measurement_data.cold_bore,
                shot_notes=measurement_data.shot_notes,
            )

            # Save to database
            measurement_id = service.save_chronograph_measurement(measurement)
            measurement.id = measurement_id
            created_measurements.append(measurement)
            session_ids_to_update.add(measurement_data.chrono_session_id)

        # Recalculate statistics for all affected sessions
        for session_id in session_ids_to_update:
            service.calculate_and_update_session_stats(user_id, session_id)

        return [convert_measurement_to_response(measurement) for measurement in created_measurements]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating bulk measurements: {str(e)}"
        )


# Source endpoints
@router.get(
    "/sources",
    response_model=List[ChronographSourceResponse],
    summary="List chronograph sources",
    description="Get all chronograph sources for the current user"
)
async def list_sources(
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """List all chronograph sources for the user"""
    try:
        sources = service.get_sources_for_user(user_id)
        return [convert_source_to_response(source) for source in sources]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sources: {str(e)}"
        )


@router.post(
    "/sources",
    response_model=ChronographSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chronograph source",
    description="Create a new chronograph device source"
)
async def create_source(
    source_data: ChronographSourceRequest,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Create a new chronograph source"""
    try:
        # Check if source with same name already exists
        existing_source = service.get_source_by_name(user_id, source_data.name)
        if existing_source:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Source with this name already exists"
            )

        # Create source data
        source_dict = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": source_data.name,
            "source_type": source_data.source_type,
            "device_name": source_data.device_name,
            "make": source_data.make,
            "model": source_data.model,
            "serial_number": source_data.serial_number,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Save to database
        source_id = service.create_source(source_dict)

        # Retrieve and return the created source
        created_source = service.get_source_by_id(source_id, user_id)
        if not created_source:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created source"
            )

        return convert_source_to_response(created_source)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating source: {str(e)}"
        )


@router.get(
    "/sources/{source_id}",
    response_model=ChronographSourceResponse,
    summary="Get a specific chronograph source",
    description="Retrieve a chronograph source by its ID"
)
async def get_source(
    source_id: str,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Get a specific chronograph source"""
    try:
        source = service.get_source_by_id(source_id, user_id)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found"
            )

        return convert_source_to_response(source)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving source: {str(e)}"
        )


@router.put(
    "/sources/{source_id}",
    response_model=ChronographSourceResponse,
    summary="Update a chronograph source",
    description="Update an existing chronograph source"
)
async def update_source(
    source_id: str,
    source_data: ChronographSourceRequest,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Update an existing chronograph source"""
    try:
        # Verify source exists and belongs to user
        existing_source = service.get_source_by_id(source_id, user_id)
        if not existing_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found"
            )

        # Check if new name conflicts with another source
        if source_data.name != existing_source.name:
            name_conflict = service.get_source_by_name(user_id, source_data.name)
            if name_conflict and name_conflict.id != source_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Another source with this name already exists"
                )

        # Update source
        updates = {
            "name": source_data.name,
            "source_type": source_data.source_type,
            "device_name": source_data.device_name,
            "make": source_data.make,
            "model": source_data.model,
            "serial_number": source_data.serial_number,
        }

        service.update_source(source_id, user_id, updates)

        # Retrieve and return updated source
        updated_source = service.get_source_by_id(source_id, user_id)
        return convert_source_to_response(updated_source)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating source: {str(e)}"
        )


@router.delete(
    "/sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chronograph source",
    description="Delete an existing chronograph source"
)
async def delete_source(
    source_id: str,
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Delete a chronograph source"""
    try:
        # Verify source exists and belongs to user
        existing_source = service.get_source_by_id(source_id, user_id)
        if not existing_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found"
            )

        # Delete the source
        service.delete_source(source_id, user_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting source: {str(e)}"
        )


# Utility endpoints
@router.get(
    "/bullet-types",
    response_model=List[str],
    summary="Get unique bullet types",
    description="Get a list of unique bullet types used by the current user"
)
async def get_bullet_types(
    user_id: str = Depends(get_current_user_id),
    service: ChronographService = Depends(get_chronograph_service),
):
    """Get unique bullet types for the user"""
    try:
        return service.get_unique_bullet_types(user_id)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving bullet types: {str(e)}"
        )