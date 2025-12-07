"""
DOPE Analytics Module

Provides analytical capabilities for DOPE (Data On Previous Engagement) sessions.
"""

from .analytics_service import AnalyticsService
from .filters import SessionFilter
from .statistics import (
    VelocityStats,
    QualityIndicator,
    calculate_velocity_stats,
    detect_outliers,
    check_normality,
    check_data_quality,
)

__all__ = [
    "AnalyticsService",
    "SessionFilter",
    "VelocityStats",
    "QualityIndicator",
    "calculate_velocity_stats",
    "detect_outliers",
    "check_normality",
    "check_data_quality",
]
