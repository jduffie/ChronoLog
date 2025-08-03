from typing import Any, Dict, List, Optional

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


class AdminView:
    """View for admin range submission review functionality."""

    def display_title(self) -> None:
        """Display the admin page title."""
        st.title("Range Submissions Admin Panel")
        st.subheader("Review and approve range submissions")

    def display_no_submissions_message(self) -> None:
        """Display message when no submissions are pending."""
        st.info("📋 No pending submissions to review.")

    def display_submission_count(self, count: int) -> None:
        """Display count of pending submissions."""
        st.markdown(f"### Pending Submissions ({count})")

    def display_submission_details(self, submission: Dict[str, Any], index: int) -> str:
        """Display submission details in an expandable section. Returns review reason."""
        submission_name = submission.get("range_name", "Unnamed Range")
        user_email = submission.get("user_email", "Unknown User")

        with st.expander(f"📍 {submission_name} - {user_email}", expanded=False):
            # Display submission details
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Range Details:**")
                st.write(f"**Name:** {submission.get('range_name', 'N/A')}")
                st.write(
                    f"**Description:** {submission.get('range_description', 'N/A')}"
                )
                st.write(f"**Submitted by:** {submission.get('user_email', 'N/A')}")
                st.write(f"**Submitted:** {submission.get('submitted_at', 'N/A')}")

                st.markdown("**Measurements:**")
                st.write(f"**Distance:** {submission.get('distance_m', 0):.1f} m")
                st.write(f"**Azimuth:** {submission.get('azimuth_deg', 0):.1f}°")
                st.write(
                    f"**Elevation:** {submission.get('elevation_angle_deg', 0):.2f}°"
                )
                st.write(f"**Location:** {submission.get('display_name', 'N/A')}")

            with col2:
                st.markdown("**Coordinates:**")
                st.write(
                    f"**Start (Firing):** {submission.get('start_lat', 0):.6f}, {submission.get('start_lon', 0):.6f}"
                )
                st.write(
                    f"**Start Altitude:** {submission.get('start_altitude_m', 0):.1f} m"
                )
                st.write(
                    f"**End (Target):** {submission.get('end_lat', 0):.6f}, {submission.get('end_lon', 0):.6f}"
                )
                st.write(
                    f"**End Altitude:** {submission.get('end_altitude_m', 0):.1f} m"
                )

            # Display map for this submission
            st.markdown("**Range Visualization:**")
            single_range_map = self.create_submission_map(submission)
            st_folium(single_range_map, use_container_width=True, height=400)

            # Admin actions section
            st.markdown("---")
            st.markdown("**Admin Actions:**")

            # Review reason input
            review_reason = st.text_area(
                "Review Comments (required for acceptance/denial):",
                key=f"reason_{submission['id']}",
                placeholder="Enter reason for acceptance or denial...",
                height=80,
            )

            return review_reason

    def display_submission_actions(
        self, submission: Dict[str, Any], review_reason: str
    ) -> Optional[str]:
        """Display action buttons for a submission. Returns action taken."""
        action_col1, action_col2, action_col3 = st.columns(3)

        action = None

        with action_col1:
            if st.button(
                f"✅ Accept", key=f"accept_{submission['id']}", type="primary"
            ):
                if not review_reason.strip():
                    st.error("❌ Please provide a reason for acceptance.")
                else:
                    action = "approve"

        with action_col2:
            if st.button(f"❌ Deny", key=f"deny_{submission['id']}", type="secondary"):
                if not review_reason.strip():
                    st.error("❌ Please provide a reason for denial.")
                else:
                    action = "deny"

        with action_col3:
            if st.button(f"🔄 Reset Status", key=f"reset_{submission['id']}"):
                action = "reset"

        return action

    def create_submission_map(self, submission: Dict[str, Any]) -> folium.Map:
        """Create a folium map for a single submission."""
        # Calculate center point
        start_lat = submission.get("start_lat", 0)
        start_lon = submission.get("start_lon", 0)
        end_lat = submission.get("end_lat", 0)
        end_lon = submission.get("end_lon", 0)

        center_lat = (start_lat + end_lat) / 2
        center_lon = (start_lon + end_lon) / 2

        # Create map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles=None)

        # Add satellite imagery
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Satellite",
            overlay=False,
            control=True,
        ).add_to(m)

        # Add road overlay
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Roads",
            overlay=True,
            control=True,
            opacity=0.7,
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        # Add firing position marker (blue)
        folium.Marker(
            location=[start_lat, start_lon],
            popup=f"🔫 Firing Position<br>{submission.get('range_name', 'Unnamed Range')}",
            icon=folium.Icon(color="blue", icon="play"),
        ).add_to(m)

        # Add target marker (red)
        folium.Marker(
            location=[end_lat, end_lon],
            popup=f"🎯 Target<br>Distance: {submission.get('distance_m', 0):.1f}m",
            icon=folium.Icon(color="red", icon="stop"),
        ).add_to(m)

        # Add line between points
        folium.PolyLine(
            locations=[[start_lat, start_lon], [end_lat, end_lon]],
            color="yellow",
            weight=3,
            opacity=0.8,
            popup=f"{submission.get('range_name', 'Unnamed')}<br>Distance: {submission.get('distance_m', 0):.1f}m<br>Azimuth: {submission.get('azimuth_deg', 0):.1f}°",
        ).add_to(m)

        return m

    def display_success_message(self, message: str) -> None:
        """Display success message."""
        st.success(message)

    def display_error_message(self, message: str) -> None:
        """Display error message."""
        st.error(message)

    def display_warning_message(self, message: str) -> None:
        """Display warning message."""
        st.warning(message)

    def display_info_message(self, message: str) -> None:
        """Display info message."""
        st.info(message)

    def display_access_denied(self) -> None:
        """Display access denied message for non-admin users."""
        st.error("🚫 Access Denied: This page is restricted to administrators only.")

    def display_submissions_table(
        self, submissions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Display submissions in a table format with filtering options."""
        if not submissions:
            self.display_no_submissions_message()
            return {"action": None, "selected_submissions": []}

        # Convert to DataFrame for display
        display_data = []
        for submission in submissions:
            display_data.append(
                {
                    "ID": submission.get("id", "N/A")[:8]
                    + "...",  # Show first 8 chars of ID
                    "Range Name": submission.get("range_name", "Unnamed"),
                    "User": (
                        submission.get("user_email", "Unknown")[:20] + "..."
                        if len(submission.get("user_email", "")) > 20
                        else submission.get("user_email", "Unknown")
                    ),
                    "Status": submission.get("status", "Unknown"),
                    "Distance (m)": f"{submission.get('distance_m', 0):.1f}",
                    "Location": (
                        submission.get("display_name", "Unknown")[:85] + "..."
                        if len(submission.get("display_name", "")) > 85
                        else submission.get("display_name", "Unknown")
                    ),
                    "Submitted": (
                        submission.get("submitted_at", "Unknown")[:10]
                        if submission.get("submitted_at")
                        else "Unknown"
                    ),  # Show date only
                }
            )

        df = pd.DataFrame(display_data)

        # Display filters
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "Filter by Status:",
                options=["All", "Under Review", "Accepted", "Denied"],
                index=0,
            )

        with col2:
            user_filter = st.text_input(
                "Filter by User Email:", placeholder="Enter email to filter"
            )

        with col3:
            range_filter = st.text_input(
                "Filter by Range Name:", placeholder="Enter range name to filter"
            )

        # Apply filters
        filtered_submissions = submissions.copy()
        if status_filter != "All":
            filtered_submissions = [
                s for s in filtered_submissions if s.get("status") == status_filter
            ]
        if user_filter:
            filtered_submissions = [
                s
                for s in filtered_submissions
                if user_filter.lower() in s.get("user_email", "").lower()
            ]
        if range_filter:
            filtered_submissions = [
                s
                for s in filtered_submissions
                if range_filter.lower() in s.get("range_name", "").lower()
            ]

        # Update display data with filtered results
        filtered_display_data = []
        for submission in filtered_submissions:
            filtered_display_data.append(
                {
                    "ID": submission.get("id", "N/A")[:8] + "...",
                    "Range Name": submission.get("range_name", "Unnamed"),
                    "User": (
                        submission.get("user_email", "Unknown")[:20] + "..."
                        if len(submission.get("user_email", "")) > 20
                        else submission.get("user_email", "Unknown")
                    ),
                    "Status": submission.get("status", "Unknown"),
                    "Distance (m)": f"{submission.get('distance_m', 0):.1f}",
                    "Location": (
                        submission.get("display_name", "Unknown")[:85] + "..."
                        if len(submission.get("display_name", "")) > 85
                        else submission.get("display_name", "Unknown")
                    ),
                    "Submitted": (
                        submission.get("submitted_at", "Unknown")[:10]
                        if submission.get("submitted_at")
                        else "Unknown"
                    ),
                }
            )

        if filtered_display_data:
            filtered_df = pd.DataFrame(filtered_display_data)
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)

            # Show count
            st.markdown(
                f"**Showing {len(filtered_submissions)} of {len(submissions)} submissions**"
            )
        else:
            st.info("No submissions match the current filters.")

        return {
            "action": "filter",
            "filtered_submissions": filtered_submissions,
            "total_count": len(submissions),
            "filtered_count": len(filtered_submissions),
        }

    def display_bulk_actions(self, submissions: List[Dict[str, Any]]) -> Optional[str]:
        """Display bulk action controls for multiple submissions."""
        if not submissions:
            return None

        st.markdown("### Bulk Actions")

        # Multi-select for submissions
        submission_options = {
            i: f"{sub.get('range_name', f'Range {i+1}')} - {sub.get('user_email', 'Unknown')}"
            for i, sub in enumerate(submissions)
        }
        selected_indices = st.multiselect(
            "Select submissions for bulk actions:",
            options=list(submission_options.keys()),
            format_func=lambda x: submission_options[x],
            key="selected_submissions",
        )

        if selected_indices:
            st.markdown(f"**{len(selected_indices)} submissions selected**")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    "✅ Bulk Approve",
                    disabled=not selected_indices,
                    use_container_width=True,
                    type="primary",
                ):
                    return "bulk_approve"

            with col2:
                if st.button(
                    "❌ Bulk Deny",
                    disabled=not selected_indices,
                    use_container_width=True,
                ):
                    return "bulk_deny"

            with col3:
                if st.button(
                    "🔄 Bulk Reset",
                    disabled=not selected_indices,
                    use_container_width=True,
                ):
                    return "bulk_reset"

        return None

    def display_statistics(self, submissions: List[Dict[str, Any]]) -> None:
        """Display submission statistics."""
        if not submissions:
            return

        # Calculate statistics
        total = len(submissions)
        pending = len([s for s in submissions if s.get("status") == "Under Review"])
        approved = len([s for s in submissions if s.get("status") == "Accepted"])
        denied = len([s for s in submissions if s.get("status") == "Denied"])

        # Display in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Submissions", total)

        with col2:
            st.metric(
                "Pending Review",
                pending,
                delta=f"{(pending/total*100):.1f}%" if total > 0 else "0%",
            )

        with col3:
            st.metric(
                "Approved",
                approved,
                delta=f"{(approved/total*100):.1f}%" if total > 0 else "0%",
            )

        with col4:
            st.metric(
                "Denied",
                denied,
                delta=f"{(denied/total*100):.1f}%" if total > 0 else "0%",
            )
