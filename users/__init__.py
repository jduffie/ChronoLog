"""
Users module for ChronoLog application.

This module handles user authentication, profile management, and preferences.
"""

from .user_model import UserModel
from .user_view import UserView
from .user_controller import UserController
from .user_profile import (
    handle_user_profile,
    display_user_management_page,
    get_user_statistics,
    display_user_profile_page,
)

__all__ = [
    "UserModel",
    "UserView",
    "UserController",
    "handle_user_profile",
    "display_user_management_page",
    "get_user_statistics",
    "display_user_profile_page",
]
