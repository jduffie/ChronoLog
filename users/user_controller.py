import streamlit as st
from typing import Dict, Any, Optional
from .user_model import UserModel
from .user_view import UserView


class UserController:
    """Controls user management logic and coordinates model/view interactions."""

    def __init__(self):
        self.model = UserModel()
        self.view = UserView()

    def handle_profile_setup(
        self, user: Dict[str, Any], existing_profile: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Handle profile setup/editing flow."""
        # Display the form
        form_data = self.view.display_profile_setup_form(user, existing_profile)

        if form_data:
            # Validate form data
            errors = self._validate_form_data(form_data, user["email"])

            if errors:
                self.view.display_validation_errors(errors)
                return None

            # Save profile
            if existing_profile:
                success = self.model.update_user_profile(user["email"], form_data)
                message = "Profile updated successfully!"
            else:
                success = self.model.create_user_profile(form_data)
                message = "Profile created successfully!"

            if success:
                self.view.display_success_message(message)
                # Clear edit mode if it was set
                if "edit_profile" in st.session_state:
                    del st.session_state["edit_profile"]
                st.rerun()
            else:
                self.view.display_error_message(
                    "Failed to save profile. Please try again."
                )

        return None

    def _validate_form_data(
        self, form_data: Dict[str, Any], current_email: str
    ) -> list[str]:
        """Validate form data and return list of errors."""
        errors = []

        # Validate username
        if not form_data.get("username", "").strip():
            errors.append("Username is required")
        else:
            username = form_data["username"].strip()
            is_valid, error_msg = self.model.validate_username(username)
            if not is_valid:
                errors.append(f"Username: {error_msg}")
            elif not self.model.is_username_available(username, current_email):
                errors.append("Username is already taken")

        # Validate state
        if not form_data.get("state", "").strip():
            errors.append("State/Province is required")

        # Validate country
        if not form_data.get("country"):
            errors.append("Country is required")

        return errors

    def get_complete_user_profile(
        self, user: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get user profile if complete, otherwise handle setup."""
        existing_profile = self.model.get_user_profile(user["email"])

        # Check if profile setup is needed
        if not existing_profile or not existing_profile.get("profile_complete", False):
            # Handle profile setup
            self.handle_profile_setup(user, existing_profile)
            return None  # Profile not complete yet

        # Check if user wants to edit profile
        if st.session_state.get("edit_profile", False):
            self.handle_profile_setup(user, existing_profile)
            return existing_profile  # Return existing profile while editing

        return existing_profile

    def display_profile_in_sidebar(self, profile: Dict[str, Any]) -> None:
        """Display user profile info in sidebar."""
        self.view.display_sidebar_info(profile)

    def handle_user_management_admin(self) -> None:
        """Handle admin user management interface."""
        # Get all users
        users = self.model.get_all_users()

        # Display management interface
        action_result = self.view.display_user_management_admin(users)

        if action_result and action_result["action"] == "delete":
            selected_indices = action_result["selected_indices"]
            if selected_indices:
                # Show confirmation dialog
                confirmation = self.view.display_delete_confirmation(
                    users, selected_indices
                )

                if confirmation == "confirm":
                    # Delete selected users
                    deleted_count = 0
                    for idx in selected_indices:
                        if idx < len(users):
                            user = users[idx]
                            if self.model.delete_user(user["email"]):
                                deleted_count += 1

                    if deleted_count > 0:
                        self.view.display_success_message(
                            f"Successfully deleted {deleted_count} user(s)"
                        )
                        st.rerun()
                    else:
                        self.view.display_error_message("Failed to delete users")

                elif confirmation == "cancel":
                    st.rerun()  # Clear confirmation dialog

    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        total_users = self.model.get_user_count()
        all_users = self.model.get_all_users()

        # Calculate stats
        imperial_users = len(
            [u for u in all_users if u.get("unit_system") == "Imperial"]
        )
        metric_users = len([u for u in all_users if u.get("unit_system") == "Metric"])
        complete_profiles = len([u for u in all_users if u.get("profile_complete")])

        return {
            "total_users": total_users,
            "imperial_users": imperial_users,
            "metric_users": metric_users,
            "complete_profiles": complete_profiles,
            "incomplete_profiles": total_users - complete_profiles,
        }
