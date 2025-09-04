from typing import Any, Dict, Optional

import streamlit as st


class UserView:
    """Handles user interface components for user management."""

    def __init__(self):
        pass

    def display_profile_setup_form(
        self, user: Dict[str, Any], existing_profile: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Display profile setup form and return form data if submitted."""
        st.title("Complete Your Profile")
        st.markdown(
            "Please provide the following information to complete your account setup:"
        )

        # Pre-fill with existing data if available
        default_username = (
            existing_profile.get("username", "") if existing_profile else ""
        )
        default_state = existing_profile.get(
            "state", "") if existing_profile else ""
        default_country = (
            existing_profile.get("country", "United States")
            if existing_profile
            else "United States"
        )
        default_units = (
            existing_profile.get("unit_system", "Imperial")
            if existing_profile
            else "Imperial"
        )

        with st.form("profile_setup"):
            # User info display
            st.markdown("### Account Information")
            st.write(f"**Name:** {user['name']}")
            st.write(f"**Email:** {user['email']}")

            st.markdown("### Profile Details")

            # Username input
            username = st.text_input(
                "Username *",
                value=default_username,
                placeholder="Enter a unique username",
                help="Your username will be visible to other users. 3-30 characters, letters, numbers, underscore, and hyphen only.",
            )

            # State/Province input
            state = st.text_input(
                "State/Province *",
                value=default_state,
                placeholder="e.g., California, Ontario, etc.",
            )

            # Country dropdown
            countries = [
                "United States",
                "Canada",
                "United Kingdom",
                "Australia",
                "New Zealand",
                "Germany",
                "France",
                "Italy",
                "Spain",
                "Netherlands",
                "Switzerland",
                "Norway",
                "Sweden",
                "Denmark",
                "Finland",
                "Austria",
                "Belgium",
                "Ireland",
                "Portugal",
                "Poland",
                "Czech Republic",
                "Hungary",
                "Japan",
                "South Korea",
                "Singapore",
                "Other",
            ]

            country = st.selectbox(
                "Country *",
                options=countries,
                index=(
                    countries.index(default_country)
                    if default_country in countries
                    else 0
                ),
            )

            # Unit system preference
            unit_system = st.radio(
                "Preferred Unit System *",
                options=[
                    "Imperial",
                    "Metric"],
                index=0 if default_units == "Imperial" else 1,
                help="Imperial: yards, feet, inches, pounds | Metric: meters, centimeters, kilograms",
            )

            st.markdown("*Required fields")

            # Submit button
            submitted = st.form_submit_button(
                "Save Profile", type="primary", use_container_width=True
            )

            if submitted:
                # Return form data for validation in controller
                return {
                    "email": user["email"],
                    "name": user["name"],
                    "username": username.strip(),
                    "state": state.strip(),
                    "country": country,
                    "unit_system": unit_system,
                    "sub": user.get("sub", ""),
                    "picture": user.get("picture", ""),
                }

        return None

    def display_profile_view(self, profile: Dict[str, Any]) -> None:
        """Display user profile information."""
        st.markdown("### Your Profile")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Account Information**")
            st.write(f"Name: {profile['name']}")
            st.write(f"Email: {profile['email']}")
            st.write(f"Username: {profile['username']}")

        with col2:
            st.markdown("**Location & Preferences**")
            st.write(f"Location: {profile['state']}, {profile['country']}")
            st.write(f"Unit System: {profile['unit_system']}")

        if st.button("Edit Profile"):
            st.session_state["edit_profile"] = True
            st.rerun()

    def display_validation_errors(self, errors: list[str]) -> None:
        """Display validation errors."""
        for error in errors:
            st.error(error)

    def display_success_message(self, message: str) -> None:
        """Display success message."""
        st.success(message)

    def display_error_message(self, message: str) -> None:
        """Display error message."""
        st.error(message)

    def display_sidebar_info(self, profile: Dict[str, Any]) -> None:
        """Display user info in sidebar."""
        st.sidebar.success(f"Logged in as {profile['name']}")

    def display_user_management_admin(
        self, users: list[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Display admin interface for user management."""
        st.title("User Management")

        if not users:
            st.info("No users found.")
            return None

        st.write(f"Total Users: {len(users)}")

        # Display users table
        import pandas as pd

        # Prepare data for display
        display_data = []
        for user in users:
            display_data.append(
                {
                    "Select": False,
                    "Username": user.get("username", ""),
                    "Name": user.get("name", ""),
                    "Email": user.get("email", ""),
                    "State": user.get("state", ""),
                    "Country": user.get("country", ""),
                    "Unit System": user.get("unit_system", ""),
                    "Created": (
                        user.get("created_at", "")[:10]
                        if user.get("created_at")
                        else ""
                    ),
                    "Profile Complete": "✅" if user.get("profile_complete") else "❌",
                }
            )

        df = pd.DataFrame(display_data)

        # Display as editable dataframe
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select", width="small", default=False
                ),
                "Username": st.column_config.TextColumn(
                    "Username", width="medium", disabled=True
                ),
                "Name": st.column_config.TextColumn(
                    "Name", width="medium", disabled=True
                ),
                "Email": st.column_config.TextColumn(
                    "Email", width="large", disabled=True
                ),
                "State": st.column_config.TextColumn(
                    "State", width="medium", disabled=True
                ),
                "Country": st.column_config.TextColumn(
                    "Country", width="medium", disabled=True
                ),
                "Unit System": st.column_config.TextColumn(
                    "Units", width="small", disabled=True
                ),
                "Created": st.column_config.TextColumn(
                    "Created", width="small", disabled=True
                ),
                "Profile Complete": st.column_config.TextColumn(
                    "Complete", width="small", disabled=True
                ),
            },
            key="users_table",
        )

        # Get selected users
        selected_indices = []
        if edited_df is not None:
            selected_rows = edited_df[edited_df["Select"]]
            selected_indices = selected_rows.index.tolist()

        # Action buttons
        col1, col2, col3 = st.columns(3)

        action_result = {"action": None, "selected_indices": selected_indices}

        with col1:
            if selected_indices:
                st.info(f"{len(selected_indices)} user(s) selected")
            else:
                st.info("Select users above")

        with col2:
            if st.button(
                "🗑️ Delete Selected",
                disabled=not selected_indices,
                    type="secondary"):
                action_result["action"] = "delete"

        with col3:
            if st.button("🔄 Refresh"):
                st.rerun()

        return action_result

    def display_delete_confirmation(
        self, users: list[Dict[str, Any]], selected_indices: list[int]
    ) -> Optional[str]:
        """Display delete confirmation dialog."""
        if not selected_indices:
            return None

        selected_users = [users[i] for i in selected_indices]

        st.warning(
            f"⚠️ Are you sure you want to delete the following {len(selected_users)} user(s)?"
        )

        for user in selected_users:
            st.write(f"• {user.get('name', '')} ({user.get('email', '')})")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "✅ Confirm Delete",
                type="primary",
                    use_container_width=True):
                return "confirm"

        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                return "cancel"

        return None
