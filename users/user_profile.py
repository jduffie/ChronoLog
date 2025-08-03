"""
Main user profile handler module.

This module provides the main interface for user profile management
that integrates with the authentication system.
"""

from typing import Any, Dict, Optional

from .user_controller import UserController


def handle_user_profile(user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Handle user profile management and return complete profile or None.

    This is the main entry point for user profile management that should be
    called from the authentication system.

    Args:
        user: User information from Auth0

    Returns:
        Complete user profile dict if profile is complete, None otherwise
    """
    controller = UserController()

    # Get complete user profile (handles setup if needed)
    user_profile = controller.get_complete_user_profile(user)

    if user_profile:
        # Profile is complete, display sidebar info
        controller.display_profile_in_sidebar(user_profile)
        return user_profile
    else:
        # Profile is incomplete, user is in setup process
        return None


def display_user_management_page():
    """Display admin user management page."""
    controller = UserController()
    controller.handle_user_management_admin()


def get_user_statistics() -> Dict[str, Any]:
    """Get user statistics for admin dashboard."""
    controller = UserController()
    return controller.get_user_stats()


def display_user_profile_page(user_profile: Dict[str, Any]):
    """Display dedicated user profile page."""
    from .user_view import UserView

    view = UserView()
    view.display_profile_view(user_profile)
