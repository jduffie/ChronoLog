"""
DOPE Analytics Module

Provides analytical capabilities for DOPE (Data On Previous Engagement) sessions.
"""

from .analytics_service import AnalyticsService
from .filters import SessionFilter

__all__ = [
    "AnalyticsService",
    "SessionFilter",
]
