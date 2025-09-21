"""
DOPE View Page

Comprehensive interface for viewing, filtering, searching, and managing DOPE sessions.
Displays all session data in a sortable table with advanced filtering capabilities.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from dope.models import DopeSessionModel
from dope.service import DopeService
from supabase import create_client
from utils.ui_formatters import (
    format_energy,
    format_energy_for_table,
    format_power_factor,
    format_power_factor_for_table,
    format_pressure_for_table,
    format_speed,
    format_speed_for_table,
    format_temperature,
    format_temperature_for_table,
    format_wind_speed,
)
from utils.unit_conversions import (
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    fps_to_mps,
    ftlb_to_joules,
    grainft_to_kgms,
    hpa_to_inhg,
    inhg_to_hpa,
    joules_to_ftlb,
    kgms_to_grainft,
    mph_to_mps,
    mps_to_fps,
    mps_to_mph,
)

# Add the root directory to the path so we can import our modules
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))


def render_view_page():
    """Render the comprehensive DOPE view page with filtering and session management"""
    # Check authentication - with fallback for testing
    if "user" not in st.session_state or not st.session_state.user:
        st.warning(
            "No user authentication found - using test user for development")
        # Create a mock user for testing
        st.session_state.user = {
            "id": "google-oauth2|111273793361054745867",
            "sub": "google-oauth2|111273793361054745867",
            "email": "test@example.com",
            "name": "Test User",
        }

    user_id = st.session_state.user.get("id")
    if not user_id:
        # Try alternative ways to get user ID
        # Auth0 sometimes uses 'sub' field
        user_id = st.session_state.user.get("sub")
        if not user_id:
            user_id = st.session_state.user.get("user_id")
        if not user_id:
            # For testing, use the correct user ID
            user_id = "google-oauth2|111273793361054745867"
            st.warning(f"Using test user ID: {user_id}")

    st.title("DOPE Sessions")

    # Initialize Supabase client
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
        service = DopeService(supabase)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        st.info("Using mock data for development")
        service = DopeService(None)

    try:
        # Initialize private session state for DOPE view page
        if "dope_view" not in st.session_state:
            st.session_state.dope_view = {
                "filters": {},
                "selected_session_id": None,
                "show_advanced_filters": False,
            }

        # Remove sidebar filters - all filters now on main page

        # Main content area
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.header("Sessions")

        with col2:
            if st.button("🔄 Refresh", help="Reload data from database"):
                st.cache_data.clear()
                st.rerun()

        with col3:
            if st.button("➕ Create New", help="Create a new DOPE session"):
                st.switch_page("pages/2b_DOPE_Create.py")

        # Advanced Filters Section (on main page)
        render_main_page_filters(service, user_id)

        # Get filtered sessions
        sessions = get_filtered_sessions(
            service, user_id, st.session_state.dope_view["filters"]
        )

        if not sessions:
            st.info(
                "No DOPE sessions found matching your filters. Try adjusting the filters or create a new session."
            )
            if st.button("Clear All Filters"):
                st.session_state.dope_view["filters"] = {}
                st.rerun()
            return

        # Display session statistics
        render_session_statistics(sessions)

        # Render main data table
        render_sessions_table(sessions)

        # Show session details if one is selected
        if st.session_state.dope_view["selected_session_id"]:
            selected_session = next(
                (
                    s
                    for s in sessions
                    if s.id
                    == st.session_state.dope_view["selected_session_id"]
                ),
                None,
            )
            if selected_session:
                render_session_details(selected_session, service, user_id)

    except Exception as e:
        st.error(f"Error loading DOPE sessions: {str(e)}")
        st.info(
            "Please try refreshing the page or contact support if the problem persists."
        )


def render_main_page_filters(service: DopeService, user_id: str):
    """Render advanced filters section on the main page with expandable controls"""
    # Advanced Filters Section with expander
    with st.expander(
        "🔍 All Filters",
        expanded=st.session_state.dope_view["show_advanced_filters"],
    ):
        # The expander state is controlled by Streamlit's expanded parameter
        # We don't force it to True here to avoid auto-opening on row selection
        pass

        # Quick actions row
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            # Global search
            search_term = st.text_input(
                "🔍 Search Sessions",
                value=st.session_state.dope_view["filters"].get(
                    "search", ""
                ),
                placeholder="Search names, cartridges, bullets, ranges...",
                help="Search across all text fields",
            )
            if search_term:
                st.session_state.dope_view["filters"]["search"] = search_term
            elif "search" in st.session_state.dope_view["filters"]:
                del st.session_state.dope_view["filters"]["search"]

        with col2:
            if st.button("🔄 Apply Filters", use_container_width=True):
                st.rerun()

        with col3:
            if st.button("🧹 Clear All", use_container_width=True):
                st.session_state.dope_view["filters"] = {}
                st.rerun()

        st.divider()

        # Get unique values for filters
        try:
            rifle_names = service.get_unique_values(user_id, "rifle_name")
            cartridge_types = service.get_unique_values(
                user_id, "cartridge_type")
            cartridge_makes = service.get_unique_values(
                user_id, "cartridge_make")
            bullet_makes = service.get_unique_values(user_id, "bullet_make")
            range_names = service.get_unique_values(user_id, "range_name")
        except Exception:
            rifle_names = cartridge_types = cartridge_makes = bullet_makes = (
                range_names
            ) = []

        # Filter sections in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Time Range")

            # Date range filter
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                date_from = st.date_input(
                    "From Date",
                    value=st.session_state.dope_view["filters"].get(
                        "date_from"
                    ),
                    key="date_from_filter",
                )
            with date_col2:
                date_to = st.date_input(
                    "To Date",
                    value=st.session_state.dope_view["filters"].get(
                        "date_to"
                    ),
                    key="date_to_filter",
                )

            if date_from:
                st.session_state.dope_view["filters"]["date_from"] = (
                    datetime.combine(date_from, datetime.min.time())
                )
            if date_to:
                st.session_state.dope_view["filters"]["date_to"] = (
                    datetime.combine(date_to, datetime.max.time())
                )

            # Additional time-based filters can be added here as needed

        with col2:
            st.subheader("Equipment")

            # Rifle filter
            if rifle_names:
                # Initialize widget with current filter value only on first run
                if "rifle_name_selectbox" not in st.session_state:
                    current_value = st.session_state.dope_view[
                        "filters"
                    ].get("rifle_name", "All")
                    if current_value in rifle_names:
                        st.session_state.rifle_name_selectbox = current_value
                    else:
                        st.session_state.rifle_name_selectbox = "All"

                rifle_name = st.selectbox(
                    "Rifle Name",
                    options=["All", "Not Defined"] + rifle_names,
                    key="rifle_name_selectbox",
                )

                # Update private state based on widget value
                if rifle_name != "All":
                    st.session_state.dope_view["filters"][
                        "rifle_name"
                    ] = rifle_name
                elif "rifle_name" in st.session_state.dope_view["filters"]:
                    del st.session_state.dope_view["filters"]["rifle_name"]

            # Range filter
            if range_names:
                # Initialize widget with current filter value only on first run
                if "range_name_selectbox" not in st.session_state:
                    current_value = st.session_state.dope_view[
                        "filters"
                    ].get("range_name", "All")
                    if current_value in range_names:
                        st.session_state.range_name_selectbox = current_value
                    else:
                        st.session_state.range_name_selectbox = "All"

                range_name = st.selectbox(
                    "Range Name",
                    options=["All", "Not Defined"] + range_names,
                    key="range_name_selectbox",
                )

                # Update private state based on widget value
                if range_name != "All":
                    st.session_state.dope_view["filters"][
                        "range_name"
                    ] = range_name
                elif "range_name" in st.session_state.dope_view["filters"]:
                    del st.session_state.dope_view["filters"]["range_name"]

            # Distance filter
            distance_range = st.slider(
                "Distance (meters)",
                min_value=0,
                max_value=1000,
                value=st.session_state.dope_view["filters"].get(
                    "distance_range", (0, 1000)
                ),
                step=25,
            )
            if distance_range != (0, 1000):
                st.session_state.dope_view["filters"][
                    "distance_range"
                ] = distance_range
            elif "distance_range" in st.session_state.dope_view["filters"]:
                del st.session_state.dope_view["filters"]["distance_range"]

        with col3:
            st.subheader("Ammunition")

            # Cartridge filters
            if cartridge_makes:
                # Initialize widget with current filter value only on first run
                if "cartridge_make_selectbox" not in st.session_state:
                    current_value = st.session_state.dope_view[
                        "filters"
                    ].get("cartridge_make", "All")
                    if current_value in cartridge_makes:
                        st.session_state.cartridge_make_selectbox = current_value
                    else:
                        st.session_state.cartridge_make_selectbox = "All"

                cartridge_make = st.selectbox(
                    "Cartridge Make",
                    options=["All", "Not Defined"] + cartridge_makes,
                    key="cartridge_make_selectbox",
                )

                # Update private state based on widget value
                if cartridge_make != "All":
                    st.session_state.dope_view["filters"][
                        "cartridge_make"
                    ] = cartridge_make
                elif (
                    "cartridge_make" in st.session_state.dope_view["filters"]
                ):
                    del st.session_state.dope_view["filters"][
                        "cartridge_make"
                    ]

            if cartridge_types:
                # Initialize widget with current filter value only on first run
                if "cartridge_type_selectbox" not in st.session_state:
                    current_value = st.session_state.dope_view[
                        "filters"
                    ].get("cartridge_type", "All")
                    if current_value in cartridge_types:
                        st.session_state.cartridge_type_selectbox = current_value
                    else:
                        st.session_state.cartridge_type_selectbox = "All"

                cartridge_type = st.selectbox(
                    "Cartridge Type",
                    options=["All", "Not Defined"] + cartridge_types,
                    key="cartridge_type_selectbox",
                )

                # Update private state based on widget value
                if cartridge_type != "All":
                    st.session_state.dope_view["filters"][
                        "cartridge_type"
                    ] = cartridge_type
                elif (
                    "cartridge_type" in st.session_state.dope_view["filters"]
                ):
                    del st.session_state.dope_view["filters"][
                        "cartridge_type"
                    ]

            # Bullet filters
            if bullet_makes:
                # Initialize widget with current filter value only on first run
                if "bullet_make_selectbox" not in st.session_state:
                    current_value = st.session_state.dope_view[
                        "filters"
                    ].get("bullet_make", "All")
                    if current_value in bullet_makes:
                        st.session_state.bullet_make_selectbox = current_value
                    else:
                        st.session_state.bullet_make_selectbox = "All"

                bullet_make = st.selectbox(
                    "Bullet Make",
                    options=["All", "Not Defined"] + bullet_makes,
                    key="bullet_make_selectbox",
                )

                # Update private state based on widget value
                if bullet_make != "All":
                    st.session_state.dope_view["filters"][
                        "bullet_make"
                    ] = bullet_make
                elif "bullet_make" in st.session_state.dope_view["filters"]:
                    del st.session_state.dope_view["filters"]["bullet_make"]

            # Bullet weight range
            weight_range = st.slider(
                "Bullet Weight (grains)",
                min_value=50,
                max_value=300,
                value=st.session_state.dope_view["filters"].get(
                    "bullet_weight_range", (50, 300)
                ),
                step=5,
            )
            if weight_range != (50, 300):
                st.session_state.dope_view["filters"][
                    "bullet_weight_range"
                ] = weight_range
            elif (
                "bullet_weight_range"
                in st.session_state.dope_view["filters"]
            ):
                del st.session_state.dope_view["filters"][
                    "bullet_weight_range"
                ]

        # Weather filters in a separate row
        st.divider()
        st.subheader("Weather Conditions")

        # Get user preferences for unit display
        user_unit_system = st.session_state.get("user", {}).get("unit_system", "Imperial")

        weather_col1, weather_col2, weather_col3 = st.columns(3)

        with weather_col1:
            # Temperature slider with unit conversion
            if user_unit_system == "Imperial":
                # Convert metric defaults to Fahrenheit for display
                temp_label = "Temperature (°F)"
                temp_min_display = celsius_to_fahrenheit(-20.0)  # -4°F
                temp_max_display = celsius_to_fahrenheit(50.0)   # 122°F
                temp_default_display = (temp_min_display, temp_max_display)
                temp_step = 2.0  # Larger step for Fahrenheit

                # Get current filter value and convert to display units
                current_temp_metric = st.session_state.dope_view["filters"].get("temperature_range", (-20.0, 50.0))
                current_temp_display = (
                    celsius_to_fahrenheit(current_temp_metric[0]),
                    celsius_to_fahrenheit(current_temp_metric[1])
                )
            else:
                temp_label = "Temperature (°C)"
                temp_min_display = -20.0
                temp_max_display = 50.0
                temp_default_display = (temp_min_display, temp_max_display)
                temp_step = 1.0
                current_temp_display = st.session_state.dope_view["filters"].get("temperature_range", (-20.0, 50.0))

            temp_range_display = st.slider(
                temp_label,
                min_value=temp_min_display,
                max_value=temp_max_display,
                value=current_temp_display,
                step=temp_step,
            )

            # Convert back to metric for storage
            if user_unit_system == "Imperial":
                temp_range_metric = (
                    fahrenheit_to_celsius(temp_range_display[0]),
                    fahrenheit_to_celsius(temp_range_display[1])
                )
            else:
                temp_range_metric = temp_range_display

            # Store in metric units
            if temp_range_metric != (-20.0, 50.0):
                st.session_state.dope_view["filters"]["temperature_range"] = temp_range_metric
            elif "temperature_range" in st.session_state.dope_view["filters"]:
                del st.session_state.dope_view["filters"]["temperature_range"]

        with weather_col2:
            # Humidity is always in percentage - no conversion needed
            humidity_range = st.slider(
                "Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.dope_view["filters"].get(
                    "humidity_range", (0.0, 100.0)
                ),
                step=5.0,
            )
            if humidity_range != (0.0, 100.0):
                st.session_state.dope_view["filters"]["humidity_range"] = humidity_range
            elif "humidity_range" in st.session_state.dope_view["filters"]:
                del st.session_state.dope_view["filters"]["humidity_range"]

        with weather_col3:
            # Wind speed with unit conversion
            if user_unit_system == "Imperial":
                # Convert m/s to mph for display
                wind_label = "Wind Speed (mph)"
                wind_min_display = 0.0
                wind_max_display = mps_to_mph(50.0)  # ~112 mph
                wind_default_display = (wind_min_display, wind_max_display)
                wind_step = 2.0

                # Get current filter value and convert to display units
                current_wind_metric = st.session_state.dope_view["filters"].get("wind_speed_range", (0.0, 50.0))
                current_wind_display = (
                    mps_to_mph(current_wind_metric[0]) if current_wind_metric[0] else 0.0,
                    mps_to_mph(current_wind_metric[1]) if current_wind_metric[1] else wind_max_display
                )
            else:
                wind_label = "Wind Speed (m/s)"
                wind_min_display = 0.0
                wind_max_display = 50.0
                wind_default_display = (wind_min_display, wind_max_display)
                wind_step = 1.0
                current_wind_display = st.session_state.dope_view["filters"].get("wind_speed_range", (0.0, 50.0))

            wind_range_display = st.slider(
                wind_label,
                min_value=wind_min_display,
                max_value=wind_max_display,
                value=current_wind_display,
                step=wind_step,
            )

            # Convert back to metric for storage
            if user_unit_system == "Imperial":
                wind_range_metric = (
                    mph_to_mps(wind_range_display[0]),
                    mph_to_mps(wind_range_display[1])
                )
            else:
                wind_range_metric = wind_range_display

            # Store in metric units
            if wind_range_metric != (0.0, 50.0):
                st.session_state.dope_view["filters"]["wind_speed_range"] = wind_range_metric
            elif "wind_speed_range" in st.session_state.dope_view["filters"]:
                del st.session_state.dope_view["filters"]["wind_speed_range"]


def get_filtered_sessions(
    service: DopeService, user_id: str, filters: Dict[str, Any]
) -> List[DopeSessionModel]:
    """Get sessions with applied filters"""
    try:
        # Start with all sessions
        if filters.get("search"):
            sessions = service.search_sessions(user_id, filters["search"])
        else:
            sessions = service.get_sessions_for_user(user_id)

        # Apply filters
        sessions = service.filter_sessions(user_id, filters)

        return sessions
    except Exception as e:
        st.error(f"Error filtering sessions: {str(e)}")
        return []


def render_session_statistics(sessions: List[DopeSessionModel]):
    """Display session statistics"""
    total_sessions = len(sessions)
    
    # Calculate useful statistics for DOPE session analysis
    unique_cartridges = len(set(s.cartridge_type for s in sessions if s.cartridge_type))
    unique_rifles = len(set(s.rifle_name for s in sessions if s.rifle_name))
    unique_ranges = len(set(s.range_name for s in sessions if s.range_name))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sessions", total_sessions)
    with col2:
        st.metric("Cartridge Types", unique_cartridges)
    with col3:
        st.metric("Rifles Used", unique_rifles)
    with col4:
        st.metric("Ranges Visited", unique_ranges)


def render_sessions_table(sessions: List[DopeSessionModel]):
    """Render the main sessions data table with sorting, column visibility, and pagination"""
    if not sessions:
        return

    # Initialize table state in session state
    if "table_settings" not in st.session_state.dope_view:
        st.session_state.dope_view["table_settings"] = {
            "sort_column": "Start Time",
            "sort_ascending": False,  # Default: newest first
            "visible_columns": _get_default_visible_columns(),
            "page_size": 50,
            "current_page": 0
        }

    # Render table controls
    _render_table_controls(len(sessions))

    # Convert sessions to DataFrame for display
    df_data = []
    for session in sessions:
        row = {
            "Session Name": session.session_name or "Unnamed Session",
            "Start Time": (
                session.start_time.strftime("%Y-%m-%d %H:%M")
                if session.start_time
                else "N/A"
            ),
            "End Time": (
                session.end_time.strftime("%Y-%m-%d %H:%M")
                if session.end_time
                else "N/A"
            ),
            "Duration": (
                str(session.end_time - session.start_time)
                if session.start_time and session.end_time
                else "N/A"
            ),
    
            "Rifle": session.rifle_name or "Unknown",
            "Cartridge": (
                f"{session.cartridge_make} {session.cartridge_model}"
                if session.cartridge_make
                else "Unknown"
            ),
            "Cartridge Type": session.cartridge_type or "Unknown",
            "Bullet": (
                f"{session.bullet_make} {session.bullet_model}"
                if session.bullet_make
                else "Unknown"
            ),
            "Bullet Weight (gr)": (
                float(session.bullet_weight) if session.bullet_weight else None
            ),
            "Distance (m)": session.range_distance_m if session.range_distance_m else None,
            "Range": session.range_name or "Unknown",
            "Temperature (°C)": (
                session.temperature_c_median if session.temperature_c_median is not None else None
            ),
            "Humidity (%)": (
                session.relative_humidity_pct_median
                if session.relative_humidity_pct_median is not None
                else None
            ),
            "Wind Speed (m/s)": (
                session.wind_speed_mps_median
                if session.wind_speed_mps_median is not None
                else None
            ),
            "Notes": (
                (session.notes[:50] + "...")
                if session.notes and len(session.notes) > 50
                else (session.notes or "")
            ),
        }
        df_data.append(row)

    df = pd.DataFrame(df_data)

    # Apply sorting and pagination
    df_display = _apply_table_sorting_and_pagination(df)

    # Configure column display
    column_config = {
        "Session Name": st.column_config.TextColumn("Session Name", width="medium"),
        "Start Time": st.column_config.TextColumn("Start Time", width="medium"),
        "End Time": st.column_config.TextColumn("End Time", width="medium"),
        "Duration": st.column_config.TextColumn("Duration", width="medium"),

        "Rifle": st.column_config.TextColumn("Rifle", width="medium"),
        "Cartridge": st.column_config.TextColumn("Cartridge", width="medium"),
        "Cartridge Type": st.column_config.TextColumn("Type", width="medium"),
        "Bullet": st.column_config.TextColumn("Bullet", width="medium"),
        "Bullet Weight (gr)": st.column_config.NumberColumn(
            "Weight (gr)", width="small"
        ),
        "Distance (m)": st.column_config.NumberColumn("Distance (m)", width="small"),
        "Range": st.column_config.TextColumn("Range", width="medium"),
        "Temperature (°C)": st.column_config.NumberColumn("Temp (°C)", width="small"),
        "Humidity (%)": st.column_config.NumberColumn("Humidity (%)", width="small"),
        "Wind Speed (m/s)": st.column_config.NumberColumn(
            "Wind (m/s)", width="small"
        ),
        "Notes": st.column_config.TextColumn("Notes", width="large"),
    }

    # Only show column config for visible columns
    visible_config = {k: v for k, v in column_config.items() if k in df_display.columns}

    # Display table with selection - use multi-row to get selector column
    selected_rows = st.dataframe(
        df_display,
        column_config=visible_config,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
    )

    # Handle row selection (adjust for pagination) - use first selected row for details
    if selected_rows.selection.rows:
        selected_idx = selected_rows.selection.rows[0]  # Use first selected row for details
        # Get session ID from original sessions list using the displayed row index
        actual_session_idx = st.session_state.dope_view["table_settings"]["current_page"] * st.session_state.dope_view["table_settings"]["page_size"] + selected_idx
        if actual_session_idx < len(sessions):
            selected_session_id = sessions[actual_session_idx].id
            st.session_state.dope_view["selected_session_id"] = selected_session_id
        else:
            st.session_state.dope_view["selected_session_id"] = None
    else:
        # Clear selection if no rows selected
        st.session_state.dope_view["selected_session_id"] = None

    # Export functionality
    if st.button("📥 Export to CSV"):
        export_sessions_to_csv(sessions)


def render_session_details(
    session: DopeSessionModel, service: DopeService, user_id: str
):
    """Render detailed view of selected session"""
    st.subheader(f"📋 Session Details: {session.display_name}")

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✏️ Edit"):
            # TODO: Implement edit functionality
            st.info("Edit functionality coming soon")

    with col2:
        if st.button("📊 Analytics"):
            # TODO: Implement session analytics functionality
            st.info("Session analytics coming soon")

    with col3:
        if st.button("🗑️ Delete", type="secondary"):
            # TODO: Implement delete with confirmation
            st.info("Delete functionality coming soon")

    # Detailed information in tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["Session Info", "Range", "Rifle", "Cartridge", "Bullet", "Weather", "Shots"]
    )

    with tab1:
        render_session_info_tab(session)

    with tab2:
        render_range_info_tab(session)

    with tab3:
        render_rifle_info_tab(session)

    with tab4:
        render_cartridge_info_tab(session)

    with tab5:
        render_bullet_info_tab(session)

    with tab6:
        render_weather_info_tab(session)

    with tab7:
        render_shots_tab(session, service)


def render_session_info_tab(session: DopeSessionModel):
    """Render session information tab"""
    col1, col2 = st.columns(2)

    with col1:
        # Required: Session name, start time, end time
        st.write(
            "**Session Name:**",
            session.session_name or "Unnamed Session")

        # Prominently display shooting session times
        if session.start_time:
            st.write(f"**Start Time:** {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.write("**Start Time:** N/A")
            
        if session.end_time:
            st.write(f"**End Time:** {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.write("**End Time:** N/A")

    with col2:
        # Required: Single reference to all data sources
        st.write("**Data Sources:**")
        
        # Chronograph name - show actual session name if available
        chrono_name = session.chrono_session_name if session.chrono_session_name else ("Linked" if session.chrono_session_id else "Not-linked")
        st.write(f"    **Chronograph:** {chrono_name}")
        
        # Weather name or "not-linked"
        weather_name = session.weather_source_name if session.weather_source_name else "Not-linked"
        st.write(f"    **Weather:** {weather_name}")
        
        # Range name
        range_name = session.range_name if session.range_name else "Unknown"
        st.write(f"    **Range:** {range_name}")
        
        # Bullet display name
        bullet_display = session.bullet_display if hasattr(session, 'bullet_display') and session.bullet_display else f"{session.bullet_make} {session.bullet_model}" if session.bullet_make else "Unknown"
        st.write(f"    **Bullet:** {bullet_display}")
        
        # Cartridge display name
        cartridge_display = session.cartridge_display if hasattr(session, 'cartridge_display') and session.cartridge_display else f"{session.cartridge_make} {session.cartridge_model}" if session.cartridge_make else "Unknown"
        st.write(f"    **Cartridge:** {cartridge_display}")
        
        # Rifle name
        rifle_name = session.rifle_name if session.rifle_name else "Unknown"
        st.write(f"    **Rifle:** {rifle_name}")


def render_range_info_tab(session: DopeSessionModel):
    """Render range information tab"""
    col1, col2 = st.columns(2)

    with col1:
        # Lat/Lon with hyperlink to Google Maps
        if session.lat and session.lon:
            st.write("**Location:**")
            st.write(f"  **Latitude:** {session.lat:.6f}")
            st.write(f"  **Longitude:** {session.lon:.6f}")
            
            # Create Google Maps hyperlink
            maps_url = f"https://www.google.com/maps?q={session.lat},{session.lon}"
            st.markdown(f"  [📍 **View on Google Maps**]({maps_url})")
        else:
            st.write("**Location:** Not available")
            
        # Altitude
        if session.start_altitude:
            st.write(f"**Altitude:** {session.start_altitude:.1f}m")
        else:
            st.write("**Altitude:** Not available")

    with col2:
        # Azimuth and Elevation angles
        if session.azimuth_deg is not None:
            st.write(f"**Azimuth Angle:** {session.azimuth_deg:.2f}°")
        else:
            st.write("**Azimuth Angle:** Not available")
            
        if session.elevation_angle_deg is not None:
            st.write(f"**Elevation Angle:** {session.elevation_angle_deg:.2f}°")
        else:
            st.write("**Elevation Angle:** Not available")


def render_rifle_info_tab(session: DopeSessionModel):
    """Render rifle information tab"""
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Rifle Name:**", session.rifle_name or "Unknown")
        st.write(
            "**Barrel Length:**",
            (
                f"{session.rifle_barrel_length_cm}cm"
                if session.rifle_barrel_length_cm
                else "Unknown"
            ),
        )
        st.write(
            "**Barrel Twist:**",
            (
                f'1:{session.rifle_barrel_twist_in_per_rev}"'
                if session.rifle_barrel_twist_in_per_rev
                else "Unknown"
            ),
        )

    with col2:
        # Remove UUID display - rifle information is already shown in col1
        pass


def render_cartridge_info_tab(session: DopeSessionModel):
    """Render cartridge information tab"""
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Make:**", session.cartridge_make or "Unknown")
        st.write("**Model:**", session.cartridge_model or "Unknown")
        st.write("**Type:**", session.cartridge_type or "Unknown")
        st.write(
            "**Lot Number:**",
            session.cartridge_lot_number or "Not specified")

    with col2:
        st.write("**Display:**", session.cartridge_display)


def render_bullet_info_tab(session: DopeSessionModel):
    """Render bullet information tab"""
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Make:**", session.bullet_make or "Unknown")
        st.write("**Model:**", session.bullet_model or "Unknown")
        st.write(
            "**Weight:**",
            f"{session.bullet_weight}gr" if session.bullet_weight else "Unknown",
        )
        st.write("**Sectional Density:**",
                 session.sectional_density or "Unknown")
        st.write("**Display:**", session.bullet_display)
        
        # Group: Physical Measurements
        st.write("**Physical Measurements:**")
        st.write(
            "  **Length:**",
            f"{session.bullet_length_mm}mm" if session.bullet_length_mm else "Unknown",
        )
        st.write(
            "  **Diameter (Land):**",
            (
                f"{session.bore_diameter_land_mm}mm"
                if session.bore_diameter_land_mm
                else "Unknown"
            ),
        )
        st.write(
            "  **Diameter (Groove):**",
            (
                f"{session.bullet_diameter_groove_mm}mm"
                if session.bullet_diameter_groove_mm
                else "Unknown"
            ),
        )

    with col2:
        # Group: Ballistic Coefficients
        st.write("**Ballistic Coefficients:**")
        st.write("  **BC G1:**", session.ballistic_coefficient_g1 or "Unknown")
        st.write("  **BC G7:**", session.ballistic_coefficient_g7 or "Unknown")


def render_weather_info_tab(session: DopeSessionModel):
    """Render weather information tab"""
    # Get user preferences for unit display
    user_unit_system = st.session_state.get("user", {}).get("unit_system", "Imperial")
    
    col1, col2 = st.columns(2)

    with col1:
        # Temperature with user preferences
        if session.temperature_c_median is not None:
            if user_unit_system == "Imperial":
                temp_f = celsius_to_fahrenheit(session.temperature_c_median)
                st.write(f"**Temperature:** {temp_f:.1f}°F")
            else:
                st.write(f"**Temperature:** {session.temperature_c_median:.1f}°C")
        else:
            st.write("**Temperature:** Unknown")
            
        # Humidity (always in percentage)
        st.write(
            "**Humidity:**",
            (
                f"{session.relative_humidity_pct_median:.1f}%"
                if session.relative_humidity_pct_median is not None
                else "Unknown"
            ),
        )
        
        # Pressure with user preferences
        if session.barometric_pressure_hpa_median is not None:
            if user_unit_system == "Imperial":
                pressure_inhg = hpa_to_inhg(session.barometric_pressure_hpa_median)
                st.write(f"**Pressure:** {pressure_inhg:.2f} inHg")
            else:
                st.write(f"**Pressure:** {session.barometric_pressure_hpa_median:.1f} hPa")
        else:
            st.write("**Pressure:** Unknown")
            
        # Weather source
        weather_source_name = getattr(session, 'weather_source_name', None)
        if weather_source_name:
            st.write("**Weather Source:**", weather_source_name)
        else:
            st.write("**Weather Source:**", "Unknown")

    with col2:
        # Group Wind measurements together on the right side
        st.write("**Wind Measurements:**")
        
        # Wind Speed 1 with user preferences
        if session.wind_speed_mps_median is not None:
            if user_unit_system == "Imperial":
                wind_speed_mph = mps_to_mph(session.wind_speed_mps_median)
                st.write(f"    **Wind Speed 1:** {wind_speed_mph:.1f} mph")
            else:
                st.write(f"    **Wind Speed 1:** {session.wind_speed_mps_median:.1f} m/s")
        else:
            st.write("    **Wind Speed 1:** Unknown")
            
        # Wind Speed 2 with user preferences
        if session.wind_speed_2_mps_median is not None:
            if user_unit_system == "Imperial":
                wind_speed_2_mph = mps_to_mph(session.wind_speed_2_mps_median)
                st.write(f"    **Wind Speed 2:** {wind_speed_2_mph:.1f} mph")
            else:
                st.write(f"    **Wind Speed 2:** {session.wind_speed_2_mps_median:.1f} m/s")
        else:
            st.write("    **Wind Speed 2:** Unknown")
            
        # Wind Direction (always in degrees)
        st.write(
            "    **Wind Direction:**",
            (
                f"{session.wind_direction_deg_median:.0f}°"
                if session.wind_direction_deg_median is not None
                else "Unknown"
            ),
        )


def export_sessions_to_csv(sessions: List[DopeSessionModel]):
    """Export sessions to CSV format"""
    try:
        # Convert sessions to detailed DataFrame
        df_data = []
        for session in sessions:
            row = session.to_dict()
            df_data.append(row)

        df = pd.DataFrame(df_data)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dope_sessions_{timestamp}.csv"

        # Convert to CSV
        csv = df.to_csv(index=False)

        # Offer download
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=filename,
            mime="text/csv",
            help="Download all session data as CSV file",
        )

        st.success(f"✅ Prepared {len(sessions)} sessions for download")

    except Exception as e:
        st.error(f"Error exporting sessions: {str(e)}")


def render_shots_tab(session: DopeSessionModel, service: DopeService):
    """Render shots/measurements tab"""
    try:
        # Get measurements for this DOPE session
        measurements = service.get_measurements_for_dope_session(
            session.id, session.user_id)

        if not measurements:
            st.info("📊 No shot measurements found for this session.")
            if session.chrono_session_id:
                st.write(
                    f"**Linked Chronograph Session:** {session.chrono_session_id}")
                st.info(
                    "Measurements may be available in the linked chronograph session but not yet copied to DOPE measurements.")
            return

        # Display shot count and summary
        shot_count = len(measurements)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Shots", shot_count)

        with col2:
            # Calculate average velocity if available - use metric data and convert for display
            velocities = [m.speed_mps
                          for m in measurements if m.speed_mps]
            avg_velocity_mps = sum(velocities) / \
                len(velocities) if velocities else 0

            # Get user preferences for unit display
            user_unit_system = st.session_state.get("user", {}).get("unit_system", "Imperial")
            avg_velocity_display = format_speed(avg_velocity_mps, user_unit_system) if avg_velocity_mps else "N/A"
            st.metric("Avg Velocity", avg_velocity_display)

        with col3:
            # Calculate standard deviation if we have velocities
            if len(velocities) > 1:
                mean = avg_velocity_mps
                variance = sum(
                    (v - mean) ** 2 for v in velocities) / len(velocities)
                std_dev_mps = variance ** 0.5
                std_dev_display = format_speed(std_dev_mps, user_unit_system)
                st.metric("Std Dev", std_dev_display)
            else:
                st.metric("Std Dev", "N/A")

        with col4:
            # Show linked chrono session if available
            if session.chrono_session_id:
                st.metric("Chrono Session", "✅ Linked")
            else:
                st.metric("Chrono Session", "❌ None")

        # Create measurements table using metric data and convert for display
        df_data = []
        for measurement in measurements:
            # Use metric data and convert for display based on user preferences (table format - no units)
            velocity_display = format_speed_for_table(measurement.speed_mps, user_unit_system) if measurement.speed_mps else ''
            energy_display = format_energy_for_table(measurement.ke_j, user_unit_system) if measurement.ke_j else ''
            power_factor_display = format_power_factor_for_table(measurement.power_factor_kgms, user_unit_system) if measurement.power_factor_kgms else ''
            temperature_display = format_temperature_for_table(measurement.temperature_c, user_unit_system) if measurement.temperature_c else ''
            pressure_display = format_pressure_for_table(measurement.pressure_hpa, user_unit_system) if measurement.pressure_hpa else ''

            # Get column headers based on unit system
            velocity_header = "Velocity (fps)" if user_unit_system == "Imperial" else "Velocity (m/s)"
            energy_header = "Energy (ft·lb)" if user_unit_system == "Imperial" else "Energy (J)"
            power_factor_header = "Power Factor" # Always show as text
            temperature_header = "Temperature (°F)" if user_unit_system == "Imperial" else "Temperature (°C)"
            pressure_header = "Pressure (inHg)" if user_unit_system == "Imperial" else "Pressure (hPa)"
            wind_speed_header = "Wind Speed (mph)" if user_unit_system == "Imperial" else "Wind Speed (m/s)"

            # Handle wind data - check if fields exist in measurement object
            wind_speed_display = ''
            wind_direction_display = ''
            
            if hasattr(measurement, 'wind_speed_mps') and measurement.wind_speed_mps is not None:
                if user_unit_system == "Imperial":
                    wind_speed_display = f"{mps_to_mph(measurement.wind_speed_mps):.1f}"
                else:
                    wind_speed_display = f"{measurement.wind_speed_mps:.1f}"
            
            if hasattr(measurement, 'wind_direction_deg') and measurement.wind_direction_deg is not None:
                wind_direction_display = f"{measurement.wind_direction_deg:.0f}"

            row = {
                "Shot #": measurement.shot_number or '',
                "Time": measurement.datetime_shot or '',
                velocity_header: velocity_display,
                "Distance (m)": measurement.distance_m or '',
                "Elevation Offset": measurement.elevation_adjustment or '',
                "Windage Offset": measurement.windage_adjustment or '',
                wind_speed_header: wind_speed_display,
                "Wind Direction (°)": wind_direction_display,
                temperature_header: temperature_display,
                pressure_header: pressure_display,
                "Humidity (%)": measurement.humidity_pct or '',
                "Notes": measurement.shot_notes or ''
            }
            df_data.append(row)

        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame(df_data)

        # Format timestamp column if present
        if 'Time' in df.columns and not df['Time'].empty:
            try:
                df['Time'] = pd.to_datetime(df['Time']).dt.strftime('%H:%M:%S')
            except BaseException:
                pass  # Keep original format if conversion fails

        # Replace empty/None values with empty strings for better display
        df = df.fillna('')

        # Configure column display dynamically based on user preferences
        velocity_header = "Velocity (fps)" if user_unit_system == "Imperial" else "Velocity (m/s)"
        energy_header = "Energy (ft·lb)" if user_unit_system == "Imperial" else "Energy (J)"
        temperature_header = "Temperature (°F)" if user_unit_system == "Imperial" else "Temperature (°C)"
        pressure_header = "Pressure (inHg)" if user_unit_system == "Imperial" else "Pressure (hPa)"
        wind_speed_header = "Wind Speed (mph)" if user_unit_system == "Imperial" else "Wind Speed (m/s)"

        column_config = {
            "Shot #": st.column_config.NumberColumn("Shot #", width="small", disabled=True),  # Don't allow editing shot numbers
            "Time": st.column_config.TextColumn("Time", width="small", disabled=True),  # Don't allow editing timestamps
            velocity_header: st.column_config.NumberColumn(velocity_header, width="medium", format="%.1f"),
            "Distance (m)": st.column_config.NumberColumn("Distance (m)", width="small", format="%.1f"),
            "Elevation Offset": st.column_config.NumberColumn("Elevation Offset", width="small", format="%.2f"),
            "Windage Offset": st.column_config.NumberColumn("Windage Offset", width="small", format="%.2f"),
            wind_speed_header: st.column_config.NumberColumn(wind_speed_header, width="small", format="%.1f"),
            "Wind Direction (°)": st.column_config.NumberColumn("Wind Direction (°)", width="small", format="%.0f"),
            temperature_header: st.column_config.NumberColumn(temperature_header, width="small", format="%.1f"),
            pressure_header: st.column_config.NumberColumn(pressure_header, width="small", format="%.1f"),
            "Humidity (%)": st.column_config.NumberColumn("Humidity (%)", width="small", format="%.1f"),
            "Notes": st.column_config.TextColumn("Notes", width="large")
        }

        # Display the measurements table
        st.subheader("📊 Shot Measurements")

        # Add editing instructions
        st.info("💡 **Editable Table:** Click on any cell to edit values. Changes are automatically saved when you move to another cell or press Enter.")

        # Create tabs for different interaction modes
        edit_tab, select_tab = st.tabs(["📝 Edit Mode", "🎯 Select Mode"])

        with edit_tab:
            # Create editable table
            edited_df = st.data_editor(
                df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",  # Prevent adding/deleting rows
                key=f"shots_editor_{session.id}"  # Unique key per session
            )

            # Check for changes and save them
            if not df.equals(edited_df):
                _save_measurement_changes(df, edited_df, measurements, service, user_unit_system)

        with select_tab:
            # Create selectable table
            selected_data = st.dataframe(
                df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                selection_mode="single-row",
                key=f"shots_selector_{session.id}",
                on_select="rerun"
            )

            # Display selected row details
            if selected_data.selection.rows:
                selected_row_idx = selected_data.selection.rows[0]
                selected_measurement = measurements[selected_row_idx]

                st.subheader("🎯 Selected Shot Details")

                # Create columns for organized display
                detail_col1, detail_col2, detail_col3 = st.columns(3)

                with detail_col1:
                    st.write("**Basic Info**")
                    st.write(f"Shot Number: {selected_measurement.shot_number or 'N/A'}")
                    st.write(f"Time: {selected_measurement.datetime_shot or 'N/A'}")
                    st.write(f"Distance: {selected_measurement.distance_m or 'N/A'} m")

                with detail_col2:
                    st.write("**Ballistic Data**")
                    if selected_measurement.speed_mps:
                        velocity_display = format_speed(selected_measurement.speed_mps, user_unit_system)
                        st.write(f"Velocity: {velocity_display}")
                    else:
                        st.write("Velocity: N/A")

                    if selected_measurement.ke_j:
                        energy_display = format_energy(selected_measurement.ke_j, user_unit_system)
                        st.write(f"Kinetic Energy: {energy_display}")
                    else:
                        st.write("Kinetic Energy: N/A")

                    if selected_measurement.power_factor_kgms:
                        pf_display = format_power_factor(selected_measurement.power_factor_kgms, user_unit_system)
                        st.write(f"Power Factor: {pf_display}")
                    else:
                        st.write("Power Factor: N/A")

                with detail_col3:
                    st.write("**Adjustments & Environment**")
                    st.write(f"Elevation Adj: {selected_measurement.elevation_adjustment or 'N/A'}")
                    st.write(f"Windage Adj: {selected_measurement.windage_adjustment or 'N/A'}")

                    if hasattr(selected_measurement, 'temperature_c') and selected_measurement.temperature_c is not None:
                        temp_display = format_temperature(selected_measurement.temperature_c, user_unit_system)
                        st.write(f"Temperature: {temp_display}")
                    else:
                        st.write("Temperature: N/A")

                    if hasattr(selected_measurement, 'wind_speed_mps') and selected_measurement.wind_speed_mps is not None:
                        wind_display = format_wind_speed(selected_measurement.wind_speed_mps, user_unit_system)
                        st.write(f"Wind Speed: {wind_display}")
                    else:
                        st.write("Wind Speed: N/A")

                # Notes section (full width)
                if selected_measurement.shot_notes:
                    st.write("**Notes**")
                    st.write(selected_measurement.shot_notes)
            else:
                st.info("👆 Select a row from the table above to view detailed shot information.")

        # Export functionality for shots data
        if st.button("📥 Export Shots to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Shots CSV",
                data=csv,
                file_name=f"dope_shots_{session.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download shot measurements as CSV file")

    except Exception as e:
        st.error(f"Error loading shot measurements: {str(e)}")
        st.info(
            "Unable to load shot data. This may be due to database connectivity issues.")


def _save_measurement_changes(original_df, edited_df, measurements, service: DopeService, user_unit_system: str):
    """
    Save changes made to measurement data back to the database.

    Args:
        original_df: Original DataFrame before edits
        edited_df: Modified DataFrame with user edits
        measurements: List of DopeMeasurementModel objects
        service: DopeService instance for database operations
        user_unit_system: "Imperial" or "Metric" for unit conversions
    """
    try:
        # Find which rows have changed
        changes_made = []

        for index, (orig_row, edited_row) in enumerate(zip(original_df.itertuples(), edited_df.itertuples())):
            # Compare each row to find changes
            if orig_row != edited_row:
                # Get the corresponding measurement
                if index < len(measurements):
                    measurement = measurements[index]

                    # Convert edited values back to metric units for storage
                    update_data = _convert_edited_row_to_metric(
                        edited_row, original_df.columns, user_unit_system
                    )

                    # Only include fields that actually changed
                    changed_fields = {}
                    for col_name, new_value in update_data.items():
                        # Get original value for comparison
                        orig_value = getattr(measurement, col_name, None)

                        # Compare values (handle None, empty strings, and type differences)
                        if _values_different(orig_value, new_value):
                            changed_fields[col_name] = new_value

                    if changed_fields:
                        # Save changes to database
                        try:
                            service.update_measurement(
                                measurement.id, changed_fields, measurement.user_id
                            )
                            changes_made.append(f"Shot #{measurement.shot_number}")
                        except Exception as e:
                            st.error(f"Failed to save changes for Shot #{measurement.shot_number}: {str(e)}")

        if changes_made:
            st.success(f"✅ Saved changes for: {', '.join(changes_made)}")
            # Refresh the page to show updated data
            st.rerun()

    except Exception as e:
        st.error(f"Error saving measurement changes: {str(e)}")


def _convert_edited_row_to_metric(edited_row, column_names, user_unit_system: str) -> dict:
    """
    Convert edited row values from display units back to metric units for database storage.

    Args:
        edited_row: Edited row data from pandas DataFrame
        column_names: List of column names
        user_unit_system: "Imperial" or "Metric"

    Returns:
        Dict of field names to metric values
    """
    update_data = {}

    # Create a mapping from column names to values
    row_data = {}
    for i, col_name in enumerate(column_names):
        if i + 1 < len(edited_row):  # +1 because itertuples includes index
            row_data[col_name] = edited_row[i + 1]

    # Convert velocity
    velocity_col = "Velocity (fps)" if user_unit_system == "Imperial" else "Velocity (m/s)"
    if velocity_col in row_data and row_data[velocity_col]:
        try:
            velocity_val = float(row_data[velocity_col])
            if user_unit_system == "Imperial":
                update_data["speed_mps"] = fps_to_mps(velocity_val)
            else:
                update_data["speed_mps"] = velocity_val
        except (ValueError, TypeError):
            pass

    # Convert energy
    energy_col = "Energy (ft·lb)" if user_unit_system == "Imperial" else "Energy (J)"
    if energy_col in row_data and row_data[energy_col]:
        try:
            energy_val = float(row_data[energy_col])
            if user_unit_system == "Imperial":
                update_data["ke_j"] = ftlb_to_joules(energy_val)
            else:
                update_data["ke_j"] = energy_val
        except (ValueError, TypeError):
            pass

    # Convert power factor
    if "Power Factor" in row_data and row_data["Power Factor"]:
        try:
            pf_val = float(row_data["Power Factor"])
            if user_unit_system == "Imperial":
                # Power factor in display is grain*ft/s, convert to kg*m/s
                update_data["power_factor_kgms"] = grainft_to_kgms(pf_val)
            else:
                update_data["power_factor_kgms"] = pf_val
        except (ValueError, TypeError):
            pass

    # Convert temperature
    temp_col = "Temperature (°F)" if user_unit_system == "Imperial" else "Temperature (°C)"
    if temp_col in row_data and row_data[temp_col]:
        try:
            temp_val = float(row_data[temp_col])
            if user_unit_system == "Imperial":
                update_data["temperature_c"] = fahrenheit_to_celsius(temp_val)
            else:
                update_data["temperature_c"] = temp_val
        except (ValueError, TypeError):
            pass

    # Convert pressure
    pressure_col = "Pressure (inHg)" if user_unit_system == "Imperial" else "Pressure (hPa)"
    if pressure_col in row_data and row_data[pressure_col]:
        try:
            pressure_val = float(row_data[pressure_col])
            if user_unit_system == "Imperial":
                update_data["pressure_hpa"] = inhg_to_hpa(pressure_val)
            else:
                update_data["pressure_hpa"] = pressure_val
        except (ValueError, TypeError):
            pass

    # Handle fields that don't need unit conversion
    direct_fields = {
        "Shot #": "shot_number",
        "Distance (m)": "distance_m",
        "Elevation Adjustment": "elevation_adjustment",
        "Windage Adjustment": "windage_adjustment",
        "Humidity (%)": "humidity_pct",
        "Clean Bore": "clean_bore",
        "Cold Bore": "cold_bore",
        "Notes": "shot_notes"
    }

    for display_name, field_name in direct_fields.items():
        if display_name in row_data and row_data[display_name] != '':
            value = row_data[display_name]
            # Convert numeric fields to appropriate types
            if field_name in ["shot_number", "distance_m", "elevation_adjustment", "windage_adjustment", "humidity_pct"]:
                try:
                    update_data[field_name] = float(value) if value else None
                except (ValueError, TypeError):
                    update_data[field_name] = None
            else:
                update_data[field_name] = value

    return update_data


def _values_different(orig_value, new_value) -> bool:
    """
    Compare two values to determine if they're different, handling None, empty strings, and type differences.

    Args:
        orig_value: Original value from model
        new_value: New value from edited table

    Returns:
        True if values are different and should be updated
    """
    # Handle None values
    if orig_value is None and (new_value is None or new_value == '' or new_value == 0):
        return False

    if new_value is None and (orig_value is None or orig_value == '' or orig_value == 0):
        return False

    # Handle empty strings
    if orig_value == '' and (new_value == '' or new_value is None):
        return False

    # Handle numeric comparisons with tolerance for floating point
    if isinstance(orig_value, (int, float)) and isinstance(new_value, (int, float)):
        return abs(orig_value - new_value) > 1e-6

    # Try to convert to same types for comparison
    try:
        if isinstance(orig_value, (int, float)) and isinstance(new_value, str):
            new_value = float(new_value)
            return abs(orig_value - new_value) > 1e-6

        if isinstance(new_value, (int, float)) and isinstance(orig_value, str):
            orig_value = float(orig_value)
            return abs(orig_value - new_value) > 1e-6
    except (ValueError, TypeError):
        pass

    # String comparison
    return str(orig_value) != str(new_value)


def _get_default_visible_columns() -> List[str]:
    """Get default visible columns for the table per requirements: Selector, Start Time, Session Name, Range Name, Rifle, Cartridge Type, Bullet, Bullet Weight"""
    return [
        "Start Time", "Session Name", "Range", "Rifle", "Cartridge Type",
        "Bullet", "Bullet Weight (gr)"
    ]


def _get_all_available_columns() -> List[str]:
    """Get all available columns for visibility toggle"""
    return [
        "Session Name", "Start Time", "End Time", "Duration",
        "Rifle", "Cartridge", "Cartridge Type", "Bullet", "Bullet Weight (gr)",
        "Distance (m)", "Range", "Temperature (°C)", "Humidity (%)",
        "Wind Speed (m/s)", "Notes"
    ]


def _render_table_controls(total_sessions: int):
    """Render table sorting, column visibility, and pagination controls"""
    settings = st.session_state.dope_view["table_settings"]

    # Table controls in columns
    control_col1, control_col2, control_col3, control_col4 = st.columns([2, 2, 2, 1])

    with control_col1:
        # Sorting controls
        st.write("**Sort By:**")
        sort_col1, sort_col2 = st.columns([3, 1])

        with sort_col1:
            sort_column = st.selectbox(
                "Column",
                options=_get_all_available_columns(),
                index=_get_all_available_columns().index(settings["sort_column"])
                    if settings["sort_column"] in _get_all_available_columns() else 0,
                key="sort_column_select",
                label_visibility="collapsed"
            )
            settings["sort_column"] = sort_column

        with sort_col2:
            sort_ascending = st.selectbox(
                "Order",
                options=["Asc", "Desc"],
                index=0 if settings["sort_ascending"] else 1,
                key="sort_order_select",
                label_visibility="collapsed"
            )
            settings["sort_ascending"] = (sort_ascending == "Asc")

    with control_col2:
        # Column visibility toggle
        st.write("**Visible Columns:**")
        with st.popover("🔧 Configure Columns"):
            st.write("**Select columns to display:**")

            # High priority columns (always visible)
            st.write("*Essential Columns:*")
            high_priority = ["Session Name", "Start Time", "Cartridge Type", "Bullet Weight (gr)"]
            for col in high_priority:
                st.checkbox(col, value=True, disabled=True, key=f"col_high_{col}")

            st.divider()
            st.write("*Optional Columns:*")

            # Other columns (toggleable)
            all_columns = _get_all_available_columns()
            optional_columns = [col for col in all_columns if col not in high_priority]

            visible_columns = settings["visible_columns"]
            new_visible = high_priority.copy()  # Always include high priority

            for col in optional_columns:
                if st.checkbox(col, value=(col in visible_columns), key=f"col_opt_{col}"):
                    new_visible.append(col)

            settings["visible_columns"] = new_visible

    with control_col3:
        # Pagination controls
        st.write("**Pagination:**")
        page_col1, page_col2 = st.columns([1, 2])

        with page_col1:
            page_size = st.selectbox(
                "Per page",
                options=[25, 50, 100, 200],
                index=[25, 50, 100, 200].index(settings["page_size"]),
                key="page_size_select",
                label_visibility="collapsed"
            )
            settings["page_size"] = page_size

        with page_col2:
            # Calculate pagination
            total_pages = max(1, (total_sessions + page_size - 1) // page_size)
            current_page = min(settings["current_page"], total_pages - 1)

            if total_pages > 1:
                new_page = st.number_input(
                    f"Page (1-{total_pages})",
                    min_value=1,
                    max_value=total_pages,
                    value=current_page + 1,
                    key="page_number_input",
                    label_visibility="collapsed"
                ) - 1
                settings["current_page"] = new_page
            else:
                settings["current_page"] = 0
                st.write("Page 1 of 1")

    with control_col4:
        # Pagination navigation buttons
        if total_sessions > settings["page_size"]:
            st.write("**Navigate:**")
            nav_col1, nav_col2 = st.columns(2)

            with nav_col1:
                if st.button("◀️", disabled=(current_page == 0), key="prev_page"):
                    settings["current_page"] = max(0, current_page - 1)
                    st.rerun()

            with nav_col2:
                if st.button("▶️", disabled=(current_page >= total_pages - 1), key="next_page"):
                    settings["current_page"] = min(total_pages - 1, current_page + 1)
                    st.rerun()

    # Show pagination info
    start_idx = settings["current_page"] * settings["page_size"]
    end_idx = min(start_idx + settings["page_size"], total_sessions)
    if total_sessions > settings["page_size"]:
        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_sessions} sessions")


def _apply_table_sorting_and_pagination(df: pd.DataFrame) -> pd.DataFrame:
    """Apply sorting and pagination to the DataFrame"""
    settings = st.session_state.dope_view["table_settings"]

    # Apply sorting
    if settings["sort_column"] in df.columns:
        df = df.sort_values(
            by=settings["sort_column"],
            ascending=settings["sort_ascending"]
        ).reset_index(drop=True)

    # Apply column visibility
    visible_columns = settings["visible_columns"]
    columns_to_show = visible_columns

    # Filter to only existing columns
    columns_to_show = [col for col in columns_to_show if col in df.columns]
    df = df[columns_to_show]

    # Apply pagination
    start_idx = settings["current_page"] * settings["page_size"]
    end_idx = start_idx + settings["page_size"]
    df_page = df.iloc[start_idx:end_idx].copy()

    return df_page
