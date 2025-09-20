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
    format_energy_for_table,
    format_power_factor_for_table,
    format_pressure_for_table,
    format_speed,
    format_speed_for_table,
    format_temperature_for_table,
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
        # Store expander state
        st.session_state.dope_view["show_advanced_filters"] = True

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
            st.subheader("Time & Status")

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

            # Status filter removed from new schema
            st.info("Status filtering has been removed from the new schema")

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
    active_sessions = len(sessions)  # No status field in new schema
    archived_sessions = total_sessions - active_sessions

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sessions", total_sessions)
    with col2:
        st.metric("Active", active_sessions)
    with col3:
        st.metric("Archived", archived_sessions)
    with col4:
        unique_cartridges = len(
            set(s.cartridge_type for s in sessions if s.cartridge_type)
        )
        st.metric("Cartridge Types", unique_cartridges)


def render_sessions_table(sessions: List[DopeSessionModel]):
    """Render the main sessions data table"""
    if not sessions:
        return

    # Convert sessions to DataFrame for display
    df_data = []
    for session in sessions:
        row = {
            "ID": session.id,
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
            # Status field removed from new schema
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

    # Configure column display
    column_config = {
        "ID": st.column_config.TextColumn("ID", width="small"),
        "Session Name": st.column_config.TextColumn("Session Name", width="medium"),
        "Start Time": st.column_config.TextColumn("Start Time", width="medium"),
        "End Time": st.column_config.TextColumn("End Time", width="medium"),
        "Duration": st.column_config.TextColumn("Duration", width="medium"),
        "Status": st.column_config.TextColumn("Status", width="small"),
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

    # Display table with selection
    selected_rows = st.dataframe(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    # Handle row selection
    if selected_rows.selection.rows:
        selected_idx = selected_rows.selection.rows[0]
        selected_session_id = df.iloc[selected_idx]["ID"]
        st.session_state.dope_view["selected_session_id"] = (
            selected_session_id
        )

    # Export functionality
    if st.button("📥 Export to CSV"):
        export_sessions_to_csv(sessions)


def render_session_details(
    session: DopeSessionModel, service: DopeService, user_id: str
):
    """Render detailed view of selected session"""
    st.subheader(f"📋 Session Details: {session.display_name}")

    # Action buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("✏️ Edit"):
            # TODO: Implement edit functionality
            st.info("Edit functionality coming soon")

    with col2:
        if st.button("📋 Duplicate"):
            # TODO: Implement duplicate functionality
            st.info("Duplicate functionality coming soon")

    with col3:
        # Archive functionality removed with status field
        st.info("Archive functionality is no longer available")

    with col4:
        if st.button("🗑️ Delete", type="secondary"):
            # TODO: Implement delete with confirmation
            st.info("Delete functionality coming soon")

    # Detailed information in tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Session Info", "Rifle", "Cartridge", "Bullet", "Weather", "Shots"]
    )

    with tab1:
        render_session_info_tab(session)

    with tab2:
        render_rifle_info_tab(session)

    with tab3:
        render_cartridge_info_tab(session)

    with tab4:
        render_bullet_info_tab(session)

    with tab5:
        render_weather_info_tab(session)

    with tab6:
        render_shots_tab(session, service)


def render_session_info_tab(session: DopeSessionModel):
    """Render session information tab"""
    col1, col2 = st.columns(2)

    with col1:
        st.write(
            "**Session Name:**",
            session.session_name or "Unnamed Session")
        # Status field removed from new schema
        
        # Prominently display shooting session times
        st.write("**🕐 Session Times:**")
        if session.start_time:
            st.write(f"  **Start:** {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.write("  **Start:** N/A")
            
        if session.end_time:
            st.write(f"  **End:** {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.write("  **End:** N/A")
            
        if session.start_time and session.end_time:
            duration = session.end_time - session.start_time
            st.write(f"  **Duration:** {duration}")
        else:
            st.write("  **Duration:** N/A")
        
        st.write("**Range:**", session.range_name or "Unknown")
        st.write(
            "**Distance:**",
            f"{session.range_distance_m}m" if session.range_distance_m else "Unknown",
        )

    with col2:
        st.write("**Session ID:**", session.id or "Unknown")
        st.write("**Cartridge ID:**", session.cartridge_id or "Unknown")
        st.write("**Chrono Session ID:**",
                 session.chrono_session_id or "Not linked")

        # Location data now stored in lat/lon fields
        if session.lat and session.lon:
            st.write(
                "**Position:**",
                f"{session.lat:.6f}, {session.lon:.6f}")
        if session.azimuth_deg:
            st.write("**Azimuth:**", f"{session.azimuth_deg}°")

    if session.notes:
        st.write("**Notes:**")
        st.text_area(
            label="notes",
            value=session.notes,
            height=100,
            disabled=True,
            key="notes_display",
        )


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
        st.write("**Rifle ID:**", session.rifle_id or "Not specified")


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
        st.write(
            "**Length:**",
            f"{session.bullet_length_mm}mm" if session.bullet_length_mm else "Unknown",
        )
        st.write("**BC G1:**", session.ballistic_coefficient_g1 or "Unknown")

    with col2:
        st.write("**BC G7:**", session.ballistic_coefficient_g7 or "Unknown")
        st.write("**Sectional Density:**",
                 session.sectional_density or "Unknown")
        st.write(
            "**Diameter (Groove):**",
            (
                f"{session.bullet_diameter_groove_mm}mm"
                if session.bullet_diameter_groove_mm
                else "Unknown"
            ),
        )
        st.write(
            "**Diameter (Land):**",
            (
                f"{session.bore_diameter_land_mm}mm"
                if session.bore_diameter_land_mm
                else "Unknown"
            ),
        )
        st.write("**Display:**", session.bullet_display)


def render_weather_info_tab(session: DopeSessionModel):
    """Render weather information tab"""
    col1, col2 = st.columns(2)

    with col1:
        st.write(
            "**Temperature:**",
            (
                f"{session.temperature_c_median}°C"
                if session.temperature_c_median is not None
                else "Unknown"
            ),
        )
        st.write(
            "**Humidity:**",
            (
                f"{session.relative_humidity_pct_median}%"
                if session.relative_humidity_pct_median is not None
                else "Unknown"
            ),
        )
        st.write(
            "**Pressure:**",
            (
                f'{session.barometric_pressure_hpa_median} hPa'
                if session.barometric_pressure_hpa_median is not None
                else "Unknown"
            ),
        )
        st.write(
            "**Wind Speed 1:**",
            (
                f"{session.wind_speed_mps_median}m/s"
                if session.wind_speed_mps_median is not None
                else "Unknown"
            ),
        )

    with col2:
        # Wind Speed 2 field removed in new schema
        st.write("**Wind Speed 2:**", "Field removed in new schema")
        st.write(
            "**Wind Direction:**",
            (
                f"{session.wind_direction_deg_median}°"
                if session.wind_direction_deg_median is not None
                else "Unknown"
            ),
        )
        st.write(
            "**Weather Source:**",
            session.weather_source_id or "Unknown")
        # TODO: Add weather_summary property to DopeSessionModel
        # st.write("**Summary:**", session.weather_summary)


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

            row = {
                "Shot #": measurement.shot_number or '',
                "Time": measurement.datetime_shot or '',
                velocity_header: velocity_display,
                energy_header: energy_display,
                power_factor_header: power_factor_display,
                "Distance (m)": measurement.distance_m or '',
                "Elevation Adjustment": measurement.elevation_adjustment or '',
                "Windage Adjustment": measurement.windage_adjustment or '',
                temperature_header: temperature_display,
                pressure_header: pressure_display,
                "Humidity (%)": measurement.humidity_pct or '',
                "Clean Bore": measurement.clean_bore or '',
                "Cold Bore": measurement.cold_bore or '',
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

        column_config = {
            "Shot #": st.column_config.NumberColumn("Shot #", width="small", disabled=True),  # Don't allow editing shot numbers
            "Time": st.column_config.TextColumn("Time", width="small", disabled=True),  # Don't allow editing timestamps
            velocity_header: st.column_config.NumberColumn(velocity_header, width="medium", format="%.1f"),
            energy_header: st.column_config.NumberColumn(energy_header, width="medium", format="%.1f"),
            "Power Factor": st.column_config.NumberColumn("Power Factor", width="medium", format="%.1f"),
            "Distance (m)": st.column_config.NumberColumn("Distance (m)", width="small", format="%.1f"),
            "Elevation Adjustment": st.column_config.NumberColumn("Elevation Adjustment", width="small", format="%.2f"),
            "Windage Adjustment": st.column_config.NumberColumn("Windage Adjustment", width="small", format="%.2f"),
            temperature_header: st.column_config.NumberColumn(temperature_header, width="small", format="%.1f"),
            pressure_header: st.column_config.NumberColumn(pressure_header, width="small", format="%.1f"),
            "Humidity (%)": st.column_config.NumberColumn("Humidity (%)", width="small", format="%.1f"),
            "Clean Bore": st.column_config.SelectboxColumn("Clean Bore", width="small", options=["yes", "no", ""]),
            "Cold Bore": st.column_config.SelectboxColumn("Cold Bore", width="small", options=["yes", "no", ""]),
            "Notes": st.column_config.TextColumn("Notes", width="large")
        }

        # Display the measurements table
        st.subheader("📊 Shot Measurements")

        # Add editing instructions
        st.info("💡 **Editable Table:** Click on any cell to edit values. Changes are automatically saved when you move to another cell or press Enter.")

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
