"""
Settings page for ChronoLog Mapping application.

This page allows users to view and edit their profile settings.
"""

import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from auth import handle_auth
from users import UserController


def main():
    """Main settings page function."""
    # Set page configuration
    st.set_page_config(
        page_title="Settings - ChronoLog Mapping", page_icon="⚙️", layout="wide"
    )

    # Set app identifier for auth system
    if "app" not in st.query_params:
        st.query_params["app"] = "mapping"

    # Handle authentication
    user_profile = handle_auth()
    if not user_profile:
        return

    # Display settings page
    display_settings_page(user_profile)


def display_settings_page(user_profile):
    """Display the main settings page."""
    st.title("⚙️ Settings")
    st.markdown("Manage your account settings and preferences.")

    # Create tabs for different settings sections
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔧 Preferences", "📊 Account Info"])

    with tab1:
        display_profile_settings(user_profile)

    with tab2:
        display_preferences_settings(user_profile)

    with tab3:
        display_account_info(user_profile)


def display_profile_settings(user_profile):
    """Display profile settings section."""
    st.header("👤 Profile Settings")
    st.markdown("View and edit your profile information.")

    # Display current profile information
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Profile")

        # Display profile picture if available
        if user_profile.get("picture"):
            st.image(user_profile["picture"], width=100)

        st.write(f"**Name:** {user_profile['name']}")
        st.write(f"**Email:** {user_profile['email']}")
        st.write(f"**Username:** {user_profile['username']}")
        st.write(f"**Location:** {user_profile['state']}, {user_profile['country']}")
        st.write(f"**Unit System:** {user_profile['unit_system']}")

        # Account dates
        if user_profile.get("created_at"):
            created_date = user_profile["created_at"][:10]  # Just the date part
            st.write(f"**Member Since:** {created_date}")

        if user_profile.get("updated_at"):
            updated_date = user_profile["updated_at"][:10]  # Just the date part
            st.write(f"**Last Updated:** {updated_date}")

    with col2:
        st.subheader("Edit Profile")

        # Edit profile button
        if st.button("✏️ Edit Profile", type="primary", use_container_width=True):
            st.session_state["edit_profile"] = True
            st.rerun()

        # Show edit form if edit mode is active
        if st.session_state.get("edit_profile", False):
            st.info(
                "📝 You can edit your profile below. The form will appear in the main content area."
            )

            if st.button("❌ Cancel Edit", use_container_width=True):
                st.session_state["edit_profile"] = False
                st.rerun()


def display_preferences_settings(user_profile):
    """Display preferences settings section."""
    st.header("🔧 Preferences")
    st.markdown("Customize your application preferences.")

    # Unit system preference
    st.subheader("📏 Unit System")
    current_units = user_profile.get("unit_system", "Imperial")

    st.write(f"**Current Unit System:** {current_units}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Imperial System:**")
        st.write("• Distance: yards, feet, inches")
        st.write("• Weight: pounds, ounces")
        st.write("• Temperature: Fahrenheit")

    with col2:
        st.markdown("**Metric System:**")
        st.write("• Distance: meters, centimeters")
        st.write("• Weight: kilograms, grams")
        st.write("• Temperature: Celsius")

    # Quick unit system toggle
    if current_units == "Imperial":
        if st.button("🔄 Switch to Metric", type="secondary"):
            update_unit_preference(user_profile, "Metric")
    else:
        if st.button("🔄 Switch to Imperial", type="secondary"):
            update_unit_preference(user_profile, "Imperial")

    # Future preferences can be added here
    st.subheader("🎨 Interface Preferences")
    st.info("Additional interface preferences will be available in future updates.")

    st.subheader("🔔 Notification Settings")
    st.info("Notification preferences will be available in future updates.")


def display_account_info(user_profile):
    """Display account information section."""
    st.header("📊 Account Information")
    st.markdown("View your account statistics and information.")

    # Get user statistics
    controller = UserController()

    # Account overview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("👤 Account Status", "Active")

    with col2:
        # Get user's range count (if available)
        try:
            from supabase import create_client

            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            supabase = create_client(url, key)

            # Count user's range submissions
            result = (
                supabase.table("ranges_submissions")
                .select("id", count="exact")
                .eq("user_email", user_profile["email"])
                .execute()
            )
            range_count = result.count if result.count else 0

            st.metric("📍 Ranges Submitted", f"{range_count}/40")
        except:
            st.metric("📍 Ranges Submitted", "N/A")

    with col3:
        profile_complete = (
            "✅ Complete" if user_profile.get("profile_complete") else "❌ Incomplete"
        )
        st.metric("📋 Profile Status", profile_complete)

    # Account details
    st.subheader("📋 Account Details")

    account_info = {
        "Email Address": user_profile["email"],
        "Full Name": user_profile["name"],
        "Username": user_profile["username"],
        "Location": f"{user_profile['state']}, {user_profile['country']}",
        "Preferred Units": user_profile["unit_system"],
        "Account Created": (
            user_profile.get("created_at", "Unknown")[:19]
            if user_profile.get("created_at")
            else "Unknown"
        ),
        "Last Updated": (
            user_profile.get("updated_at", "Unknown")[:19]
            if user_profile.get("updated_at")
            else "Unknown"
        ),
        "Profile Complete": "Yes" if user_profile.get("profile_complete") else "No",
    }

    # Display as a nice table
    import pandas as pd

    df = pd.DataFrame(list(account_info.items()), columns=["Setting", "Value"])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Setting": st.column_config.TextColumn("Setting", width="medium"),
            "Value": st.column_config.TextColumn("Value", width="large"),
        },
    )

    # Privacy and security section
    st.subheader("🔒 Privacy & Security")
    st.markdown("Your account is secured through Google authentication via Auth0.")

    privacy_info = [
        "🔐 **Authentication**: Your account uses Google OAuth for secure login",
        "📧 **Email**: Your email is used only for account identification",
        "🔒 **Data Privacy**: Your data is stored securely in our database",
        "🚫 **No Passwords**: We don't store passwords - authentication is handled by Google",
        "📊 **Usage Data**: Only range submission data is stored for the application",
    ]

    for info in privacy_info:
        st.markdown(info)

    # Logout button
    st.subheader("🚪 Account Actions")
    if st.button("🚪 Logout", type="secondary"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Logged out successfully!")
        st.rerun()


def update_unit_preference(user_profile, new_unit_system):
    """Update user's unit system preference."""
    try:
        controller = UserController()

        # Update the unit system
        update_data = {
            "username": user_profile["username"],
            "state": user_profile["state"],
            "country": user_profile["country"],
            "unit_system": new_unit_system,
        }

        success = controller.model.update_user_profile(
            user_profile["email"], update_data
        )

        if success:
            st.success(f"✅ Unit system updated to {new_unit_system}!")
            # Update the session state to reflect the change
            st.rerun()
        else:
            st.error("❌ Failed to update unit system. Please try again.")

    except Exception as e:
        st.error(f"❌ Error updating preferences: {str(e)}")


if __name__ == "__main__":
    main()
