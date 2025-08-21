"""
DOPE View Page

Comprehensive interface for viewing, filtering, searching, and managing DOPE sessions.
Displays all session data in a sortable table with advanced filtering capabilities.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dope.service import DopeService
from dope.models import DopeSessionModel


def render_view_page():
    """Render the comprehensive DOPE view page with filtering and session management"""
    # Check authentication - with fallback for testing
    if "user" not in st.session_state or not st.session_state.user:
        st.warning("No user authentication found - using test user for development")
        # Create a mock user for testing
        st.session_state.user = {
            "id": "google-oauth2|111273793361054745867",
            "sub": "google-oauth2|111273793361054745867",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    
    user_id = st.session_state.user.get("id")
    if not user_id:
        # Try alternative ways to get user ID
        user_id = st.session_state.user.get("sub")  # Auth0 sometimes uses 'sub' field
        if not user_id:
            user_id = st.session_state.user.get("user_id")
        if not user_id:
            # For testing, use the correct user ID
            user_id = "google-oauth2|111273793361054745867"
            st.warning(f"Using test user ID: {user_id}")
    
    
    st.title("📊 View DOPE Sessions")
    
    # Initialize service (with mocked client for now)
    service = DopeService(None)  # TODO: Pass actual Supabase client
    
    try:
        # Initialize session state for filters and selections
        if "dope_filters" not in st.session_state:
            st.session_state.dope_filters = {}
        if "selected_session_id" not in st.session_state:
            st.session_state.selected_session_id = None
        if "show_advanced_filters" not in st.session_state:
            st.session_state.show_advanced_filters = False
        
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
        sessions = get_filtered_sessions(service, user_id, st.session_state.dope_filters)
        
        if not sessions:
            st.info("No DOPE sessions found matching your filters. Try adjusting the filters or create a new session.")
            if st.button("Clear All Filters"):
                st.session_state.dope_filters = {}
                st.rerun()
            return
        
        # Display session statistics
        render_session_statistics(sessions)
        
        # Render main data table
        render_sessions_table(sessions)
        
        # Show session details if one is selected
        if st.session_state.selected_session_id:
            selected_session = next(
                (s for s in sessions if s.id == st.session_state.selected_session_id), 
                None
            )
            if selected_session:
                render_session_details(selected_session, service, user_id)
    
    except Exception as e:
        st.error(f"Error loading DOPE sessions: {str(e)}")
        st.info("Please try refreshing the page or contact support if the problem persists.")


def render_main_page_filters(service: DopeService, user_id: str):
    """Render advanced filters section on the main page with expandable controls"""
    # Advanced Filters Section with expander
    with st.expander("🔍 All Filters", expanded=st.session_state.get("show_advanced_filters", False)):
        # Store expander state
        st.session_state.show_advanced_filters = True
        
        # Quick actions row
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Global search
            search_term = st.text_input(
                "🔍 Search Sessions",
                value=st.session_state.dope_filters.get("search", ""),
                placeholder="Search names, cartridges, bullets, ranges...",
                help="Search across all text fields"
            )
            if search_term:
                st.session_state.dope_filters["search"] = search_term
            elif "search" in st.session_state.dope_filters:
                del st.session_state.dope_filters["search"]
        
        with col2:
            if st.button("🔄 Apply Filters", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("🧹 Clear All", use_container_width=True):
                st.session_state.dope_filters = {}
                st.rerun()
        
        st.divider()
        
        # Get unique values for filters
        try:
            rifle_names = service.get_unique_values(user_id, "rifle_name")
            cartridge_types = service.get_unique_values(user_id, "cartridge_type")
            cartridge_makes = service.get_unique_values(user_id, "cartridge_make")
            bullet_makes = service.get_unique_values(user_id, "bullet_make")
            range_names = service.get_unique_values(user_id, "range_name")
        except Exception:
            rifle_names = cartridge_types = cartridge_makes = bullet_makes = range_names = []
        
        # Filter sections in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📅 Time & Status")
            
            # Date range filter
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                date_from = st.date_input(
                    "From Date",
                    value=st.session_state.dope_filters.get("date_from"),
                    key="date_from_filter"
                )
            with date_col2:
                date_to = st.date_input(
                    "To Date", 
                    value=st.session_state.dope_filters.get("date_to"),
                    key="date_to_filter"
                )
            
            if date_from:
                st.session_state.dope_filters["date_from"] = datetime.combine(date_from, datetime.min.time())
            if date_to:
                st.session_state.dope_filters["date_to"] = datetime.combine(date_to, datetime.max.time())
            
            # Status filter
            status_options = ["All", "active", "archived"]
            status = st.selectbox(
                "Status",
                options=status_options,
                index=status_options.index(st.session_state.dope_filters.get("status", "All"))
            )
            if status != "All":
                st.session_state.dope_filters["status"] = status
            elif "status" in st.session_state.dope_filters:
                del st.session_state.dope_filters["status"]
        
        with col2:
            st.subheader("🔫 Equipment")
            
            # Rifle filter
            if rifle_names:
                rifle_name = st.selectbox(
                    "Rifle Name",
                    options=["All"] + rifle_names,
                    index=0 if st.session_state.dope_filters.get("rifle_name") not in rifle_names 
                           else rifle_names.index(st.session_state.dope_filters.get("rifle_name")) + 1
                )
                if rifle_name != "All":
                    st.session_state.dope_filters["rifle_name"] = rifle_name
                elif "rifle_name" in st.session_state.dope_filters:
                    del st.session_state.dope_filters["rifle_name"]
            
            # Range filter
            if range_names:
                range_name = st.selectbox(
                    "Range Name",
                    options=["All"] + range_names,
                    index=0 if st.session_state.dope_filters.get("range_name") not in range_names
                           else range_names.index(st.session_state.dope_filters.get("range_name")) + 1
                )
                if range_name != "All":
                    st.session_state.dope_filters["range_name"] = range_name
                elif "range_name" in st.session_state.dope_filters:
                    del st.session_state.dope_filters["range_name"]
            
            # Distance filter
            distance_range = st.slider(
                "Distance (meters)",
                min_value=0,
                max_value=1000,
                value=st.session_state.dope_filters.get("distance_range", (0, 1000)),
                step=25
            )
            if distance_range != (0, 1000):
                st.session_state.dope_filters["distance_range"] = distance_range
            elif "distance_range" in st.session_state.dope_filters:
                del st.session_state.dope_filters["distance_range"]
        
        with col3:
            st.subheader("🎯 Ammunition")
            
            # Cartridge filters
            if cartridge_makes:
                cartridge_make = st.selectbox(
                    "Cartridge Make",
                    options=["All"] + cartridge_makes,
                    key="cartridge_make_filter"
                )
                if cartridge_make != "All":
                    st.session_state.dope_filters["cartridge_make"] = cartridge_make
                elif "cartridge_make" in st.session_state.dope_filters:
                    del st.session_state.dope_filters["cartridge_make"]
            
            if cartridge_types:
                cartridge_type = st.selectbox(
                    "Cartridge Type",
                    options=["All"] + cartridge_types,
                    key="cartridge_type_filter"
                )
                if cartridge_type != "All":
                    st.session_state.dope_filters["cartridge_type"] = cartridge_type
                elif "cartridge_type" in st.session_state.dope_filters:
                    del st.session_state.dope_filters["cartridge_type"]
            
            # Bullet filters
            if bullet_makes:
                bullet_make = st.selectbox(
                    "Bullet Make",
                    options=["All"] + bullet_makes,
                    key="bullet_make_filter"
                )
                if bullet_make != "All":
                    st.session_state.dope_filters["bullet_make"] = bullet_make
                elif "bullet_make" in st.session_state.dope_filters:
                    del st.session_state.dope_filters["bullet_make"]
            
            # Bullet weight range
            weight_range = st.slider(
                "Bullet Weight (grains)",
                min_value=50,
                max_value=300,
                value=st.session_state.dope_filters.get("bullet_weight_range", (50, 300)),
                step=5
            )
            if weight_range != (50, 300):
                st.session_state.dope_filters["bullet_weight_range"] = weight_range
            elif "bullet_weight_range" in st.session_state.dope_filters:
                del st.session_state.dope_filters["bullet_weight_range"]
        
        # Weather filters in a separate row
        st.divider()
        st.subheader("🌤️ Weather Conditions")
        
        weather_col1, weather_col2, weather_col3 = st.columns(3)
        
        with weather_col1:
            temp_range = st.slider(
                "Temperature (°C)",
                min_value=-20.0,
                max_value=50.0,
                value=st.session_state.dope_filters.get("temperature_range", (-20.0, 50.0)),
                step=1.0
            )
            if temp_range != (-20.0, 50.0):
                st.session_state.dope_filters["temperature_range"] = temp_range
            elif "temperature_range" in st.session_state.dope_filters:
                del st.session_state.dope_filters["temperature_range"]
        
        with weather_col2:
            humidity_range = st.slider(
                "Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.dope_filters.get("humidity_range", (0.0, 100.0)),
                step=5.0
            )
            if humidity_range != (0.0, 100.0):
                st.session_state.dope_filters["humidity_range"] = humidity_range
            elif "humidity_range" in st.session_state.dope_filters:
                del st.session_state.dope_filters["humidity_range"]
        
        with weather_col3:
            wind_range = st.slider(
                "Wind Speed (km/h)",
                min_value=0.0,
                max_value=50.0,
                value=st.session_state.dope_filters.get("wind_speed_range", (0.0, 50.0)),
                step=1.0
            )
            if wind_range != (0.0, 50.0):
                st.session_state.dope_filters["wind_speed_range"] = wind_range
            elif "wind_speed_range" in st.session_state.dope_filters:
                del st.session_state.dope_filters["wind_speed_range"]




def get_filtered_sessions(service: DopeService, user_id: str, filters: Dict[str, Any]) -> List[DopeSessionModel]:
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
    active_sessions = len([s for s in sessions if s.status == "active"])
    archived_sessions = total_sessions - active_sessions
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", total_sessions)
    with col2:
        st.metric("Active", active_sessions)
    with col3:
        st.metric("Archived", archived_sessions)
    with col4:
        unique_cartridges = len(set(s.cartridge_type for s in sessions if s.cartridge_type))
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
            "Created": session.datetime_local.strftime("%Y-%m-%d %H:%M") if session.datetime_local else "",
            "Status": session.status or "unknown",
            "Rifle": session.rifle_name or "Unknown",
            "Cartridge": f"{session.cartridge_make} {session.cartridge_model}" if session.cartridge_make else "Unknown",
            "Cartridge Type": session.cartridge_type or "Unknown",
            "Bullet": f"{session.bullet_make} {session.bullet_model}" if session.bullet_make else "Unknown",
            "Bullet Weight (gr)": float(session.bullet_weight) if session.bullet_weight else None,
            "Distance (m)": session.distance_m if session.distance_m else None,
            "Range": session.range_name or "Unknown",
            "Temperature (°C)": session.temperature_c if session.temperature_c is not None else None,
            "Humidity (%)": session.relative_humidity_pct if session.relative_humidity_pct is not None else None,
            "Wind Speed (km/h)": session.wind_speed_1_kmh if session.wind_speed_1_kmh is not None else None,
            "Notes": (session.notes[:50] + "...") if session.notes and len(session.notes) > 50 else (session.notes or "")
        }
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Configure column display
    column_config = {
        "ID": st.column_config.TextColumn("ID", width="small"),
        "Session Name": st.column_config.TextColumn("Session Name", width="medium"),
        "Created": st.column_config.DatetimeColumn("Created", width="medium"),
        "Status": st.column_config.TextColumn("Status", width="small"),
        "Rifle": st.column_config.TextColumn("Rifle", width="medium"),
        "Cartridge": st.column_config.TextColumn("Cartridge", width="medium"),
        "Cartridge Type": st.column_config.TextColumn("Type", width="medium"),
        "Bullet": st.column_config.TextColumn("Bullet", width="medium"),
        "Bullet Weight (gr)": st.column_config.NumberColumn("Weight (gr)", width="small"),
        "Distance (m)": st.column_config.NumberColumn("Distance (m)", width="small"),
        "Range": st.column_config.TextColumn("Range", width="medium"),
        "Temperature (°C)": st.column_config.NumberColumn("Temp (°C)", width="small"),
        "Humidity (%)": st.column_config.NumberColumn("Humidity (%)", width="small"),
        "Wind Speed (km/h)": st.column_config.NumberColumn("Wind (km/h)", width="small"),
        "Notes": st.column_config.TextColumn("Notes", width="large")
    }
    
    # Display table with selection
    selected_rows = st.dataframe(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Handle row selection
    if selected_rows.selection.rows:
        selected_idx = selected_rows.selection.rows[0]
        selected_session_id = df.iloc[selected_idx]["ID"]
        st.session_state.selected_session_id = selected_session_id
    
    # Export functionality
    if st.button("📥 Export to CSV"):
        export_sessions_to_csv(sessions)


def render_session_details(session: DopeSessionModel, service: DopeService, user_id: str):
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
        archive_label = "📁 Archive" if session.status == "active" else "📂 Unarchive"
        if st.button(archive_label):
            # TODO: Implement archive toggle
            st.info("Archive functionality coming soon")
    
    with col4:
        if st.button("🗑️ Delete", type="secondary"):
            # TODO: Implement delete with confirmation
            st.info("Delete functionality coming soon")
    
    # Detailed information in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Session Info", "🔫 Rifle", "🎯 Cartridge", "🏹 Bullet", "🌤️ Weather"
    ])
    
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


def render_session_info_tab(session: DopeSessionModel):
    """Render session information tab"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Session Name:**", session.session_name or "Unnamed Session")
        st.write("**Status:**", session.status or "Unknown")
        st.write("**Created:**", session.datetime_local.strftime("%Y-%m-%d %H:%M:%S") if session.datetime_local else "Unknown")
        st.write("**Range:**", session.range_name or "Unknown")
        st.write("**Distance:**", f"{session.distance_m}m" if session.distance_m else "Unknown")
    
    with col2:
        st.write("**Session ID:**", session.id or "Unknown")
        st.write("**Cartridge Spec ID:**", session.cartridge_spec_id or "Unknown")
        st.write("**Chrono Session ID:**", session.chrono_session_id or "Not linked")
        
        if session.start_lat and session.start_lon:
            st.write("**Position:**", f"{session.start_lat:.6f}, {session.start_lon:.6f}")
        if session.azimuth_deg:
            st.write("**Azimuth:**", f"{session.azimuth_deg}°")
    
    if session.notes:
        st.write("**Notes:**")
        st.text_area("", value=session.notes, height=100, disabled=True, key="notes_display")


def render_rifle_info_tab(session: DopeSessionModel):
    """Render rifle information tab"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Rifle Name:**", session.rifle_name or "Unknown")
        st.write("**Barrel Length:**", f"{session.rifle_barrel_length_cm}cm" if session.rifle_barrel_length_cm else "Unknown")
        st.write("**Barrel Twist:**", f"1:{session.rifle_barrel_twist_in_per_rev}\"" if session.rifle_barrel_twist_in_per_rev else "Unknown")
    
    with col2:
        st.write("**Rifle ID:**", session.rifle_id or "Not specified")


def render_cartridge_info_tab(session: DopeSessionModel):
    """Render cartridge information tab"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Make:**", session.cartridge_make or "Unknown")
        st.write("**Model:**", session.cartridge_model or "Unknown")
        st.write("**Type:**", session.cartridge_type or "Unknown")
        st.write("**Lot Number:**", session.cartridge_lot_number or "Not specified")
    
    with col2:
        st.write("**Display:**", session.cartridge_display)


def render_bullet_info_tab(session: DopeSessionModel):
    """Render bullet information tab"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Make:**", session.bullet_make or "Unknown")
        st.write("**Model:**", session.bullet_model or "Unknown")
        st.write("**Weight:**", f"{session.bullet_weight}gr" if session.bullet_weight else "Unknown")
        st.write("**Length:**", f"{session.bullet_length_mm}mm" if session.bullet_length_mm else "Unknown")
        st.write("**BC G1:**", session.ballistic_coefficient_g1 or "Unknown")
    
    with col2:
        st.write("**BC G7:**", session.ballistic_coefficient_g7 or "Unknown")
        st.write("**Sectional Density:**", session.sectional_density or "Unknown")
        st.write("**Diameter (Groove):**", f"{session.bullet_diameter_groove_mm}mm" if session.bullet_diameter_groove_mm else "Unknown")
        st.write("**Diameter (Land):**", f"{session.bore_diameter_land_mm}mm" if session.bore_diameter_land_mm else "Unknown")
        st.write("**Display:**", session.bullet_display)


def render_weather_info_tab(session: DopeSessionModel):
    """Render weather information tab"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Temperature:**", f"{session.temperature_c}°C" if session.temperature_c is not None else "Unknown")
        st.write("**Humidity:**", f"{session.relative_humidity_pct}%" if session.relative_humidity_pct is not None else "Unknown")
        st.write("**Pressure:**", f"{session.barometric_pressure_inhg}\" Hg" if session.barometric_pressure_inhg is not None else "Unknown")
        st.write("**Wind Speed 1:**", f"{session.wind_speed_1_kmh}km/h" if session.wind_speed_1_kmh is not None else "Unknown")
    
    with col2:
        st.write("**Wind Speed 2:**", f"{session.wind_speed_2_kmh}km/h" if session.wind_speed_2_kmh is not None else "Unknown")
        st.write("**Wind Direction:**", f"{session.wind_direction_deg}°" if session.wind_direction_deg is not None else "Unknown")
        st.write("**Weather Source:**", session.weather_source_name or "Unknown")
        st.write("**Summary:**", session.weather_summary)


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
            help="Download all session data as CSV file"
        )
        
        st.success(f"✅ Prepared {len(sessions)} sessions for download")
        
    except Exception as e:
        st.error(f"Error exporting sessions: {str(e)}")