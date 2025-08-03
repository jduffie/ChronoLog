import re
from typing import Any, Dict, Optional

import streamlit as st
from supabase import create_client


class UserModel:
    """Handles user data operations and database interactions."""

    def __init__(self):
        self.supabase = None

    def _get_supabase_client(self):
        """Get Supabase client."""
        if not self.supabase:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self.supabase = create_client(url, key)
        return self.supabase

    def get_user_profile(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user profile from database."""
        try:
            supabase = self._get_supabase_client()
            result = supabase.table("users").select("*").eq("email", email).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            st.error(f"Error fetching user profile: {str(e)}")
            return None

    def create_user_profile(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user profile."""
        try:
            supabase = self._get_supabase_client()

            # Prepare user data
            profile_data = {
                "email": user_data["email"],
                "name": user_data["name"],
                "username": user_data["username"],
                "state": user_data["state"],
                "country": user_data["country"],
                "unit_system": user_data["unit_system"],
                "profile_complete": True,
                "auth0_sub": user_data.get("sub", ""),
                "picture": user_data.get("picture", ""),
            }

            result = supabase.table("users").insert(profile_data).execute()

            if result.data:
                return True
            return False
        except Exception as e:
            st.error(f"Error creating user profile: {str(e)}")
            return False

    def update_user_profile(self, email: str, user_data: Dict[str, Any]) -> bool:
        """Update existing user profile."""
        try:
            supabase = self._get_supabase_client()

            # Prepare update data
            update_data = {
                "username": user_data["username"],
                "state": user_data["state"],
                "country": user_data["country"],
                "unit_system": user_data["unit_system"],
                "profile_complete": True,
            }

            result = (
                supabase.table("users").update(update_data).eq("email", email).execute()
            )

            if result.data:
                return True
            return False
        except Exception as e:
            st.error(f"Error updating user profile: {str(e)}")
            return False

    def is_username_available(self, username: str, current_email: str = None) -> bool:
        """Check if username is available."""
        try:
            supabase = self._get_supabase_client()
            query = supabase.table("users").select("email").eq("username", username)

            # If updating existing user, exclude their current record
            if current_email:
                query = query.neq("email", current_email)

            result = query.execute()

            return len(result.data) == 0
        except Exception as e:
            st.error(f"Error checking username availability: {str(e)}")
            return False

    def validate_username(self, username: str) -> tuple[bool, str]:
        """Validate username format and availability."""
        # Check length
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        if len(username) > 30:
            return False, "Username must be 30 characters or less"

        # Check format (alphanumeric, underscore, hyphen)
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            return (
                False,
                "Username can only contain letters, numbers, underscores, and hyphens",
            )

        # Check if starts with letter or number
        if not username[0].isalnum():
            return False, "Username must start with a letter or number"

        return True, ""

    def get_all_users(self) -> list[Dict[str, Any]]:
        """Get all users (admin function)."""
        try:
            supabase = self._get_supabase_client()
            result = (
                supabase.table("users")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
            return []

    def get_user_count(self) -> int:
        """Get total number of registered users."""
        try:
            supabase = self._get_supabase_client()
            result = supabase.table("users").select("id", count="exact").execute()
            return result.count if result.count else 0
        except Exception as e:
            st.error(f"Error getting user count: {str(e)}")
            return 0

    def delete_user(self, email: str) -> bool:
        """Delete a user profile (admin function)."""
        try:
            supabase = self._get_supabase_client()
            result = supabase.table("users").delete().eq("email", email).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting user: {str(e)}")
            return False
