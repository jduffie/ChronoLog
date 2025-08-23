from datetime import datetime
from typing import Dict, Any, Optional, cast

import pandas as pd
import streamlit as st

from .service import WeatherService


def render_weather_sources_tab(user, supabase):
    """Render the Weather Sources tab for managing weather meters"""
    # Initialize private session state for weather sources page
    if "weather_sources_page_state" not in st.session_state:
        weather_state: Dict[str, Any] = {
            "selected_weather_source_id": None,
            "selected_weather_date": None,
            "edit_sources": {},  # {source_id: bool}
            "confirm_deletes": {}  # {source_id: bool}
        }
        st.session_state.weather_sources_page_state = weather_state
    
    st.header("📡 Weather Sources")

    try:
        # Initialize weather service
        weather_service = WeatherService(supabase)

        # Get all weather sources for the user
        sources = weather_service.get_sources_for_user(user["id"])

        # Create tabs for manage and add sources
        manage_tab, add_tab = st.tabs(["Manage Sources", "Add Source"])

        with manage_tab:
            st.subheader("🔧 Manage Weather Sources")

            if not sources:
                st.info(
                    "No weather sources found. Use the 'Add Source' tab to create your first weather source."
                )

            # Get measurements for statistics
            measurements = weather_service.get_all_measurements_for_user(user["id"])

            # Display sources with their statistics
            for source in sources:
                # Get measurements for this source
                source_measurements = [
                    m for m in measurements if m.weather_source_id == source.id
                ]

                with st.expander(f"📡 {source.display_name()}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Source Information:**")
                        st.write(f"• **Name:** {source.name}")
                        st.write(f"• **Device:** {source.device_display()}")
                        if source.serial_number:
                            st.write(f"• **Serial Number:** {source.serial_number}")
                        if source.created_at:
                            st.write(
                                f"• **Created:** {pd.to_datetime(source.created_at).strftime('%Y-%m-%d %H:%M')}"
                            )

                    with col2:
                        st.write("**Measurement Statistics:**")
                        if source_measurements:
                            measurement_count = len(source_measurements)
                            st.write(f"• **Total Measurements:** {measurement_count}")

                            # Date range
                            timestamps = [
                                pd.to_datetime(m.measurement_timestamp)
                                for m in source_measurements
                            ]
                            first_date = min(timestamps).date()
                            last_date = max(timestamps).date()
                            if first_date == last_date:
                                st.write(f"• **Data Date:** {first_date}")
                            else:
                                st.write(
                                    f"• **Date Range:** {first_date} to {last_date}"
                                )

                            # Last upload
                            last_upload = max(
                                [
                                    pd.to_datetime(m.uploaded_at)
                                    for m in source_measurements
                                ]
                            ).date()
                            st.write(f"• **Last Upload:** {last_upload}")
                        else:
                            st.write("• **Total Measurements:** 0")
                            st.write("• **Status:** No data uploaded")

                    # Action buttons
                    st.write("**Actions:**")
                    button_col1, button_col2, button_col3 = st.columns(3)

                    with button_col1:
                        if st.button("Edit", key=f"edit_{source.id}"):
                            st.session_state.weather_sources_page_state["edit_sources"][source.id] = True

                    with button_col2:
                        if source_measurements:
                            if st.button("View Data", key=f"view_{source.id}"):
                                # Set session state for view log tab
                                if source_measurements:
                                    latest_date = max(
                                        [
                                            pd.to_datetime(m.measurement_timestamp)
                                            for m in source_measurements
                                        ]
                                    ).strftime("%Y-%m-%d")
                                    # Type cast to avoid type checker warnings
                                    weather_state = cast(Dict[str, Any], st.session_state.weather_sources_page_state)
                                    weather_state["selected_weather_source_id"] = source.id
                                    weather_state["selected_weather_date"] = latest_date
                                    st.info(
                                        "Source selected! Go to the 'View Log' tab to see detailed weather analysis."
                                    )

                    with button_col3:
                        if st.button(
                            "Delete", key=f"delete_{source.id}", type="secondary"
                        ):
                            st.session_state.weather_sources_page_state["confirm_deletes"][source.id] = True

                    # Edit form
                    if st.session_state.weather_sources_page_state["edit_sources"].get(source.id, False):
                        st.write("---")
                        st.write("**Edit Weather Source:**")

                        with st.form(f"edit_form_{source.id}"):
                            new_name = st.text_input("Source Name", value=source.name)
                            new_device_name = st.text_input(
                                "Device Name", value=source.device_name or ""
                            )
                            new_make = st.text_input(
                                "Make/Manufacturer", value=source.make or ""
                            )
                            new_model = st.text_input("Model", value=source.model or "")
                            new_serial = st.text_input(
                                "Serial Number", value=source.serial_number or ""
                            )

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Save Changes"):
                                    try:
                                        updates = {
                                            "name": new_name,
                                            "device_name": (
                                                new_device_name
                                                if new_device_name
                                                else None
                                            ),
                                            "make": new_make if new_make else None,
                                            "model": new_model if new_model else None,
                                            "serial_number": (
                                                new_serial if new_serial else None
                                            ),
                                        }
                                        weather_service.update_source(
                                            source.id, user["id"], updates
                                        )
                                        st.success(
                                            "Weather source updated successfully!"
                                        )
                                        st.session_state.weather_sources_page_state["edit_sources"][source.id] = False
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating weather source: {e}")

                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state.weather_sources_page_state["edit_sources"][source.id] = False
                                    st.rerun()

                    # Delete confirmation
                    if st.session_state.weather_sources_page_state["confirm_deletes"].get(source.id, False):
                        st.write("---")
                        st.warning(
                            f"⚠️ Are you sure you want to delete '{source.name}'?"
                        )
                        if source_measurements:
                            st.warning(
                                f"This will also delete {len(source_measurements)} weather measurements!"
                            )

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(
                                "Yes, Delete",
                                key=f"confirm_yes_{source.id}",
                                type="primary",
                            ):
                                try:
                                    weather_service.delete_source(
                                        source.id, user["id"]
                                    )
                                    st.success(
                                        f"Weather source '{source.name}' deleted successfully!"
                                    )
                                    st.session_state.weather_sources_page_state["confirm_deletes"][source.id] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting weather source: {e}")

                        with col2:
                            if st.button("Cancel", key=f"confirm_no_{source.id}"):
                                st.session_state.weather_sources_page_state["confirm_deletes"][source.id] = False
                                st.rerun()

        with add_tab:
            st.subheader("➕ Add New Weather Source")
            st.write("Create a new weather source for organizing your weather data.")

            with st.form("add_source_form"):
                col1, col2 = st.columns(2)

                with col1:
                    source_type = st.selectbox(
                        "Source Type*",
                        options=["Meter"],
                        help="Select the type of weather source",
                    )

                with col2:
                    source_make = st.selectbox(
                        "Make*",
                        options=["Kestrel"],
                        help="Select the manufacturer",
                        disabled=(source_type != "Meter"),
                    )

                name = st.text_input(
                    "Source Name*",
                    placeholder="e.g., Range Kestrel, Hunting Meter",
                    help="Give your weather source a unique name",
                )

                if st.form_submit_button("Save Weather Source", type="primary"):
                    if not name.strip():
                        st.error("Source name is required!")
                    else:
                        try:
                            # Check if name already exists
                            existing = weather_service.get_source_by_name(
                                user["id"], name.strip()
                            )
                            if existing:
                                st.error(
                                    f"A weather source named '{name}' already exists!"
                                )
                            else:
                                source_data = {
                                    "user_id": user["id"],
                                    "name": name.strip(),
                                    "make": source_make,
                                    "source_type": source_type.lower(),
                                }

                                source_id = weather_service.create_source(source_data)
                                st.success(
                                    f"Weather source '{name}' created successfully!"
                                )
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error creating weather source: {e}")

            st.write("---")
            st.info(
                "💡 **Tip:** Create weather sources here first, then go to the Import tab to upload Kestrel CSV files. Device details will be automatically extracted from your CSV files."
            )

    except Exception as e:
        st.error(f"Error loading weather sources: {str(e)}")
