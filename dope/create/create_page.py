"""
DOPE Create Page Module

This module handles the creation of new DOPE (Data On Previous Engagement) sessions
using a wizard-style workflow.
"""

import streamlit as st
from datetime import datetime
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chronograph.service import ChronographService
from dope.service import DopeService
from weather.service import WeatherService
from mapping.submission.submission_model import SubmissionModel
from dope.weather_associator import WeatherSessionAssociator


def get_unused_chrono_sessions(user_id: str, supabase):
    """Get chronograph sessions not yet used in any DOPE session"""
    try:
        chrono_service = ChronographService(supabase)
        dope_service = DopeService(supabase)
        
        # Get all chrono sessions for user
        all_chrono_sessions = chrono_service.get_sessions_for_user(user_id)
        
        # Get all DOPE sessions to find used chrono session IDs
        all_dope_sessions = dope_service.get_sessions_for_user(user_id)
        used_chrono_ids = {session.chrono_session_id for session in all_dope_sessions if session.chrono_session_id}
        
        # Filter out already used sessions
        unused_sessions = [session for session in all_chrono_sessions if session.id not in used_chrono_ids]
        
        return unused_sessions
    except Exception as e:
        st.error(f"Error loading chronograph sessions: {str(e)}")
        return []


@st.cache_data
def get_rifles_for_user(_supabase, user_id: str):
    """Get all rifles for the current user with caching"""
    try:
        response = _supabase.table("rifles").select("*").eq("user_id", user_id).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error loading rifles: {str(e)}")
        return []


@st.cache_data
def get_cartridge_types(_supabase):
    """Get cartridge types from database with caching"""
    try:
        response = _supabase.table("cartridge_types").select("name").execute()
        return sorted([item["name"] for item in response.data])
    except Exception as e:
        st.error(f"Error loading cartridge types: {str(e)}")
        return []


@st.cache_data
def get_cartridges_for_user(_supabase, user_id: str):
    """Get all cartridges for user with bullet details"""
    try:
        response = (_supabase.table("cartridges")
                    .select("""
            *,
            bullets!bullet_id (
                manufacturer,
                model,
                weight_grains
            )
        """).or_(f"owner_id.eq.{user_id},owner_id.is.null")
                    .execute())
        
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error loading cartridges: {str(e)}")
        return []


def get_unique_cartridge_makes(cartridges):
    """Extract unique cartridge makes from cartridges list"""
    makes = set()
    for cartridge in cartridges:
        if cartridge.get("make"):
            makes.add(cartridge["make"])
    return sorted(list(makes))


def get_unique_bullet_grains(cartridges):
    """Extract unique bullet grain weights from cartridges list"""
    grains = set()
    for cartridge in cartridges:
        if cartridge.get("bullets") and cartridge["bullets"].get("weight_grains"):
            grains.add(cartridge["bullets"]["weight_grains"])
    return sorted(list(grains))


def filter_cartridges(cartridges, cartridge_type_filter, cartridge_make_filter, bullet_grain_filter):
    """Filter cartridges based on selected filters"""
    filtered = cartridges
    
    # Filter by cartridge type
    if cartridge_type_filter and cartridge_type_filter != "All":
        filtered = [c for c in filtered if c.get("cartridge_type") == cartridge_type_filter]
    
    # Filter by cartridge make
    if cartridge_make_filter and cartridge_make_filter != "All":
        filtered = [c for c in filtered if c.get("make") == cartridge_make_filter]
    
    # Filter by bullet grain
    if bullet_grain_filter and bullet_grain_filter != "All":
        filtered = [c for c in filtered 
                   if c.get("bullets") and c["bullets"].get("weight_grains") == bullet_grain_filter]
    
    return filtered


def render_step_1_chrono_selection(user_id: str, supabase):
    """Step 1: Select chronograph session"""
    st.subheader("Step 1: Select Chronograph Session")
    unused_sessions = get_unused_chrono_sessions(user_id, supabase)
    
    if not unused_sessions:
        st.warning("⚠️ No unused chronograph sessions found.")
        st.write("You need to upload chronograph data first before creating a DOPE session.")
        st.info("💡 Go to the Chronograph page to upload your shooting data, then return here.")
        return None
    
    # Create options for selectbox
    session_options = {}
    for session in unused_sessions:
        display_name = f"{session.bullet_type} ({session.bullet_grain}gr) - {session.datetime_local.strftime('%Y-%m-%d %H:%M')} - {session.shot_count} shots"
        session_options[display_name] = session
    
    selected_display = st.selectbox(
        "Available Chronograph Sessions",
        options=list(session_options.keys()),
        help="Sessions are listed by bullet type, grain weight, date, and shot count"
    )
    
    selected_session = session_options[selected_display]
    
    # Show session details
    with st.expander("📊 Session Details", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Bullet Type", selected_session.bullet_type)
            st.metric("Bullet Weight", f"{selected_session.bullet_grain} gr")
        
        with col2:
            st.metric("Shot Count", selected_session.shot_count)
            st.metric("Avg Velocity", f"{selected_session.avg_speed_fps:.1f} fps")
        
        with col3:
            st.metric("Std Deviation", f"{selected_session.std_dev_fps:.1f} fps")
            st.metric("Date", selected_session.datetime_local.strftime('%Y-%m-%d'))
    
    return selected_session


def render_step_2_rifle_selection(user_id: str, supabase):
    """Step 2: Select rifle"""
    st.subheader("Step 2: Select Rifle")
    st.write("Choose the rifle used for this session.")
    
    rifles = get_rifles_for_user(supabase, user_id)
    
    if not rifles:
        st.warning("⚠️ No rifles found in your inventory.")
        st.write("You need to create a rifle entry first.")
        st.info("💡 **How to create a rifle:**\n"
                "1. Go to the **Rifles** page in the navigation menu\n"
                "2. Click on the **Create** tab\n" 
                "3. Fill out the rifle details and save\n"
                "4. Return to this page and start over")
        return None
    
    # Create rifle options
    rifle_options = {}
    for rifle in rifles:
        display_name = f"{rifle['name']}"
        if rifle.get('cartridge_type'):
            display_name += f" ({rifle['cartridge_type']})"
        rifle_options[display_name] = rifle
    
    selected_display = st.selectbox(
        "Select Rifle",
        options=list(rifle_options.keys()),
        help="Choose the rifle used for this shooting session"
    )
    
    selected_rifle = rifle_options[selected_display]
    
    # Show rifle details
    with st.expander("Rifle Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {selected_rifle['name']}")
            st.write(f"**Cartridge Type:** {selected_rifle.get('cartridge_type', 'Not specified')}")
            
        with col2:
            st.write(f"**Barrel Length:** {selected_rifle.get('barrel_length', 'Not specified')}")
            st.write(f"**Twist Rate:** {selected_rifle.get('barrel_twist_ratio', 'Not specified')}")
    
    return selected_rifle


def render_step_3_cartridge_selection(user_id: str, supabase, rifle_cartridge_type: str):
    """Step 3: Select cartridge filtered by rifle cartridge type"""
    st.subheader("Step 3: Select Cartridge")
    st.write(f"Showing cartridges compatible with your rifle's cartridge type: **{rifle_cartridge_type}**")
    
    # Get all cartridges for user
    all_cartridges = get_cartridges_for_user(supabase, user_id)
    
    if not all_cartridges:
        st.warning("⚠️ No cartridges found in your inventory.")
        st.write("You need to create a cartridge entry first.")
        st.info("💡 **How to create a cartridge:**\n"
                "1. Go to the **Cartridges** page in the navigation menu\n"
                "2. Click on the **Create** tab\n" 
                "3. Add a factory or custom cartridge\n"
                "4. Return to this page and start over")
        return None
    
    # Filter cartridges to only show those matching the rifle's cartridge_type
    compatible_cartridges = []
    if rifle_cartridge_type:
        compatible_cartridges = [c for c in all_cartridges if c.get("cartridge_type") == rifle_cartridge_type]
    else:
        compatible_cartridges = all_cartridges
    
    if not compatible_cartridges:
        st.warning(f"⚠️ No cartridges found that match your rifle's cartridge type: {rifle_cartridge_type}")
        st.write("You need to create a compatible cartridge first.")
        st.info("💡 **How to create a compatible cartridge:**\n"
                "1. Go to the **Cartridges** page in the navigation menu\n"
                "2. Click on the **Create** tab\n" 
                f"3. Add a cartridge with cartridge type: **{rifle_cartridge_type}**\n"
                "4. Return to this page and start over")
        return None
    
    # Create filter options based on compatible cartridges
    cartridge_types = get_cartridge_types(supabase)
    cartridge_makes = get_unique_cartridge_makes(compatible_cartridges)
    bullet_grains = get_unique_bullet_grains(compatible_cartridges)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Default to rifle's cartridge type, but allow "All" if user wants to see everything
        default_index = 0
        type_options = ["All"] + cartridge_types
        if rifle_cartridge_type in cartridge_types:
            default_index = type_options.index(rifle_cartridge_type)
        
        cartridge_type_filter = st.selectbox(
            "Cartridge Type",
            options=type_options,
            index=default_index,
            help="Filter by cartridge type (pre-filtered to your rifle's cartridge type)"
        )
    
    with col2:
        cartridge_make_filter = st.selectbox(
            "Cartridge Make",
            options=["All"] + cartridge_makes,
            help="Filter by cartridge manufacturer"
        )
    
    with col3:
        bullet_grain_filter = st.selectbox(
            "Bullet Weight",
            options=["All"] + [f"{g}gr" for g in bullet_grains],
            help="Filter by bullet grain weight"
        )
    
    # Apply filters to compatible cartridges
    bullet_grain_value = None if bullet_grain_filter == "All" else int(bullet_grain_filter.replace("gr", ""))
    filtered_cartridges = filter_cartridges(
        compatible_cartridges, 
        cartridge_type_filter, 
        cartridge_make_filter, 
        bullet_grain_value
    )
    
    if not filtered_cartridges:
        st.warning("⚠️ No cartridges match your filter criteria.")
        st.write("Try adjusting your filters or create a new cartridge.")
        return None
    
    st.write("---")
    
    # Create cartridge options
    cartridge_options = {}
    for cartridge in filtered_cartridges:
        bullet = cartridge.get("bullets", {})
        display_name = f"{cartridge.get('make', 'Unknown')} {cartridge.get('model', 'Unknown')} - {bullet.get('manufacturer', 'Unknown')} {bullet.get('model', 'Unknown')} ({bullet.get('weight_grains', 'Unknown')}gr)"
        cartridge_options[display_name] = cartridge
    
    selected_cartridge_display = st.selectbox(
        "Select Cartridge",
        options=list(cartridge_options.keys()),
        help="Choose the specific cartridge used in this session"
    )
    
    selected_cartridge = cartridge_options[selected_cartridge_display]
    
    # Show cartridge details
    with st.expander("Cartridge Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Cartridge Type:** {selected_cartridge.get('cartridge_type', 'Not specified')}")
            st.write(f"**Make:** {selected_cartridge.get('make', 'Unknown')}")
            st.write(f"**Model:** {selected_cartridge.get('model', 'Unknown')}")
        
        with col2:
            bullet = selected_cartridge.get("bullets", {})
            if bullet:
                st.write(f"**Bullet:** {bullet.get('manufacturer', 'Unknown')} {bullet.get('model', 'Unknown')}")
                st.write(f"**Weight:** {bullet.get('weight_grains', 'Unknown')} gr")
            else:
                st.write("**Bullet:** Not specified")
    
    return selected_cartridge


def render_step_4_range_selection(user_id: str, supabase):
    """Step 4: Select range (optional)"""
    st.subheader("Step 4: Select Range (Optional)")
    st.write("Choose the range where this session took place, or skip this step.")
    
    try:
        submission_model = SubmissionModel()
        ranges = submission_model.get_user_ranges(user_id, supabase)
    except Exception as e:
        st.error(f"Error loading ranges: {str(e)}")
        ranges = []
    
    range_options = {"Skip (No Range)": None}
    
    if not ranges:
        st.info("No ranges found in your submissions.")
        st.info("You can create ranges in the Ranges page, or skip this step.")
    else:
        for range_data in ranges:
            display_name = f"{range_data['range_name']} - {range_data.get('distance_m', 'Unknown')}m"
            if range_data.get('status'):
                display_name += f" ({range_data['status']})"
            range_options[display_name] = range_data
    
    selected_range_display = st.selectbox(
        "Select Range",
        options=list(range_options.keys()),
        help="Choose the range used for this session, or skip if not applicable"
    )
    
    selected_range = range_options[selected_range_display]
    
    if selected_range:
        with st.expander("Range Details", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {selected_range['range_name']}")
                st.write(f"**Distance:** {selected_range.get('distance_m', 'Unknown')} meters")
                st.write(f"**Status:** {selected_range.get('status', 'Unknown')}")
            
            with col2:
                if selected_range.get('azimuth_deg'):
                    st.write(f"**Azimuth:** {selected_range['azimuth_deg']}°")
                if selected_range.get('elevation_angle_deg'):
                    st.write(f"**Elevation:** {selected_range['elevation_angle_deg']}°")
    
    return selected_range


def render_step_5_weather_selection(user_id: str, supabase, time_window: Optional[tuple] = None):
    """Step 5: Select weather source (optional)"""
    st.subheader("Step 5: Select Weather Source (Optional)")
    st.write("Choose the weather measurement device used, or skip this step.")
    
    try:
        weather_service = WeatherService(supabase)
        weather_sources = weather_service.get_sources_for_user(user_id)
    except Exception as e:
        st.error(f"Error loading weather sources: {str(e)}")
        weather_sources = []
    
    weather_options = {"Skip (No Weather Data)": None}
    
    if not weather_sources:
        st.info("No weather sources found.")
        st.info("You can create weather sources in the Weather page, or skip this step.")
    else:
        for source in weather_sources:
            display_name = f"{source.name}"
            if source.make:
                display_name += f" ({source.make}"
                if source.model:
                    display_name += f" {source.model}"
                display_name += ")"
            weather_options[display_name] = source
    
    selected_weather_display = st.selectbox(
        "Select Weather Source",
        options=list(weather_options.keys()),
        help="Choose the weather measurement device used, or skip if not applicable"
    )
    
    selected_weather = weather_options[selected_weather_display]
    
    if selected_weather:
        with st.expander("Weather Source Details", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {selected_weather.name}")
                st.write(f"**Type:** {selected_weather.source_type}")
            
            with col2:
                if selected_weather.make:
                    st.write(f"**Make:** {selected_weather.make}")
                if selected_weather.model:
                    st.write(f"**Model:** {selected_weather.model}")
    
    return selected_weather


def render_step_6_session_details():
    """Step 4: Additional session details"""
    st.subheader("Step 4: Session Details")
    st.write("Provide additional details for your DOPE session.")
    
    session_name = st.text_input(
        "Session Name",
        placeholder="e.g., Morning Range Session, Load Development",
        help="A descriptive name for this DOPE session"
    )
    
    notes = st.text_area(
        "Notes",
        placeholder="Additional notes about this session...",
        help="Any additional observations or notes about this session"
    )
    
    return {
        "session_name": session_name,
        "notes": notes
    }


def render_step_7_confirmation(chrono_session, rifle, cartridge, range_data, weather_data, session_details):
    """Step 7: Confirmation and creation"""
    st.subheader("Step 7: Review & Create")
    st.write("Review your DOPE session details before creating.")
    
    # Summary of selections
    with st.expander("Session Summary", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Chronograph Session:**")
            st.write(f"- Bullet: {chrono_session.bullet_type} ({chrono_session.bullet_grain}gr)")
            st.write(f"- Date: {chrono_session.datetime_local.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"- Shots: {chrono_session.shot_count}")
            
            st.write("**Rifle:**")
            st.write(f"- Name: {rifle['name']}")
            st.write(f"- Cartridge: {rifle.get('cartridge_type', 'Not specified')}")
            
            st.write("**Range:**")
            if range_data:
                st.write(f"- Name: {range_data['range_name']}")
                st.write(f"- Distance: {range_data.get('distance_m', 'Unknown')} meters")
            else:
                st.write("- None selected")
        
        with col2:
            st.write("**Cartridge:**")
            st.write(f"- Type: {cartridge['cartridge_type']}")
            st.write(f"- Make/Model: {cartridge.get('make', 'Unknown')} {cartridge.get('model', 'Unknown')}")
            
            st.write("**Weather Source:**")
            if weather_data:
                st.write(f"- Name: {weather_data.name}")
                st.write(f"- Type: {weather_data.source_type}")
            else:
                st.write("- None selected")
            
            st.write("**Session:**")
            st.write(f"- Name: {session_details['session_name'] or 'Not specified'}")
            st.write(f"- Notes: {session_details['notes'][:50] + '...' if len(session_details.get('notes', '')) > 50 else session_details.get('notes', 'None')}")
    
    return True


def render_create_page(user, supabase):
    """
    Render the DOPE Create page with wizard-style workflow.
    """
    print("start render_create_page")

    st.title("Create DOPE Session")
    st.write("Follow the steps below to create a new DOPE (Data On Previous Engagement) session.")

    # Initialize private session state for DOPE Create
    if "dope_create" not in st.session_state:
        st.session_state.dope_create = {}
    
    dope_create_state = st.session_state.dope_create
    
    # Initialize wizard state
    if "wizard_step" not in dope_create_state:
        dope_create_state["wizard_step"] = 1
    if "wizard_data" not in dope_create_state:
        dope_create_state["wizard_data"] = {}

    # Progress indicator
    progress_steps = ["Chrono", "Rifle", "Cartridge", "Range", "Weather", "Details", "Confirm"]
    current_step = dope_create_state["wizard_step"]
    
    # Create progress bar
    progress_cols = st.columns(len(progress_steps))
    for i, (col, step_name) in enumerate(zip(progress_cols, progress_steps), 1):
        with col:
            if i < current_step:
                st.success(f"✅ {step_name}")
            elif i == current_step:
                st.info(f"▶️ {step_name}")
            else:
                st.write(f"⏸️ {step_name}")

    st.divider()

    # Render current step
    if current_step == 1:
        result = render_step_1_chrono_selection(user["id"], supabase)
        if result:
            dope_create_state["wizard_data"]["chrono_session"] = result
            
            # Capture time window for weather measurement filtering
            try:
                weather_associator = WeatherSessionAssociator(supabase)
                time_window = weather_associator.get_chrono_session_time_window(user["id"], result.id)
                dope_create_state["wizard_data"]["time_window"] = time_window
            except Exception as e:
                st.warning(f"Could not determine time window for weather filtering: {str(e)}")
                dope_create_state["wizard_data"]["time_window"] = None
            
            if st.button("Next: Select Rifle", type="primary"):
                dope_create_state["wizard_step"] = 2
                st.rerun()

    elif current_step == 2:
        result = render_step_2_rifle_selection(user["id"], supabase)
        if result:
            dope_create_state["wizard_data"]["rifle"] = result
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back"):
                    dope_create_state["wizard_step"] = 1
                    st.rerun()
            with col2:
                if st.button("Next: Select Cartridge", type="primary"):
                    dope_create_state["wizard_step"] = 3
                    st.rerun()

    elif current_step == 3:
        result = render_step_3_cartridge_selection(user["id"], supabase, dope_create_state["wizard_data"]["rifle"].get("cartridge_type"))
        if result:
            dope_create_state["wizard_data"]["cartridge"] = result
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back"):
                    dope_create_state["wizard_step"] = 2
                    st.rerun()
            with col2:
                if st.button("Next: Select Range", type="primary"):
                    dope_create_state["wizard_step"] = 4
                    st.rerun()

    elif current_step == 4:
        result = render_step_4_range_selection(user["id"], supabase)
        dope_create_state["wizard_data"]["range"] = result
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                dope_create_state["wizard_step"] = 3
                st.rerun()
        with col2:
            if st.button("Next: Select Weather", type="primary"):
                dope_create_state["wizard_step"] = 5
                st.rerun()

    elif current_step == 5:
        time_window = dope_create_state["wizard_data"].get("time_window")
        result = render_step_5_weather_selection(user["id"], supabase, time_window)
        dope_create_state["wizard_data"]["weather"] = result
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                dope_create_state["wizard_step"] = 4
                st.rerun()
        with col2:
            if st.button("Next: Session Details", type="primary"):
                dope_create_state["wizard_step"] = 6
                st.rerun()

    elif current_step == 6:
        result = render_step_6_session_details()
        dope_create_state["wizard_data"]["session_details"] = result
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                dope_create_state["wizard_step"] = 5
                st.rerun()
        with col2:
            if st.button("Next: Review & Create", type="primary"):
                dope_create_state["wizard_step"] = 7
                st.rerun()

    elif current_step == 7:
        wizard_data = dope_create_state["wizard_data"]
        render_step_7_confirmation(
            wizard_data["chrono_session"],
            wizard_data["rifle"], 
            wizard_data["cartridge"],
            wizard_data.get("range"),
            wizard_data.get("weather"),
            wizard_data["session_details"]
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back"):
                dope_create_state["wizard_step"] = 6
                st.rerun()
        
        with col2:
            if st.button("Start Over"):
                dope_create_state["wizard_step"] = 1
                dope_create_state["wizard_data"] = {}
                st.rerun()
        
        with col3:
            if st.button("Create DOPE Session", type="primary"):
                try:
                    # Extract data from wizard
                    chrono_session = wizard_data["chrono_session"]
                    rifle = wizard_data["rifle"]
                    cartridge = wizard_data["cartridge"]
                    range_data = wizard_data.get("range")
                    weather_data = wizard_data.get("weather")
                    session_details = wizard_data["session_details"]
                    time_window = wizard_data.get("time_window")
                    
                    # Prepare session data for database
                    session_data = {
                        "session_name": session_details.get("session_name") or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        "chrono_session_id": chrono_session.id,
                        "rifle_id": rifle["id"],
                        "cartridge_id": cartridge["id"],
                        "range_submission_id": range_data["id"] if range_data else None,
                        "weather_source_id": weather_data.id if weather_data else None,
                        "start_time": time_window[0].isoformat() if time_window else None,
                        "end_time": time_window[1].isoformat() if time_window else None,
                        "notes": session_details.get("notes"),
                        "status": "active",
                    }
                    
                    # Create the DOPE session
                    service = DopeService(supabase)
                    new_session = service.create_session(session_data, user["id"])
                    
                    # Process weather association if weather source was selected
                    weather_association_results = None
                    if weather_data and time_window:
                        try:
                            weather_associator = WeatherSessionAssociator(supabase)
                            weather_association_results = weather_associator.associate_weather_with_dope_session(
                                user["id"],
                                new_session.id,
                                weather_data.id,
                                time_window[0],
                                time_window[1]
                            )
                            
                            if weather_association_results.get("error"):
                                st.warning(f"⚠️ Weather association warning: {weather_association_results['error']}")
                            else:
                                # Update DOPE session with median weather values
                                median_weather = weather_association_results.get("median_weather", {})
                                if median_weather:
                                    weather_update_data = {}
                                    
                                    # Map median weather values to dope_session fields
                                    field_mapping = {
                                        'temperature_f': 'temperature_f',
                                        'relative_humidity_pct': 'humidity_pct', 
                                        'barometric_pressure_inhg': 'pressure_inhg',
                                        'altitude_ft': 'altitude_ft',
                                        'wind_speed_mph': 'wind_speed_mph',
                                        'density_altitude_ft': 'density_altitude_ft'
                                    }
                                    
                                    for weather_field, dope_field in field_mapping.items():
                                        if weather_field in median_weather:
                                            weather_update_data[dope_field] = median_weather[weather_field]
                                    
                                    if weather_update_data:
                                        # Update the DOPE session with median weather values
                                        supabase.table("dope_sessions").update(weather_update_data).eq("id", new_session.id).execute()
                                
                                st.success(f"🌤️ Weather data processed: {weather_association_results['weather_measurement_count']} measurements")
                                st.success(f"🎯 Shot associations: {weather_association_results['associations_made']} of {weather_association_results['dope_measurement_count']} shots")
                        
                        except Exception as weather_error:
                            st.warning(f"⚠️ Weather association failed: {str(weather_error)}")
                            st.info("DOPE session created successfully, but weather data could not be processed.")
                    
                    st.success(f"✅ DOPE Session created successfully!")
                    st.success(f"Session ID: {new_session.id}")
                    
                    if weather_association_results and not weather_association_results.get("error"):
                        st.info("Weather measurements have been associated with your shots.")
                    
                    st.info("You can now view your session in the DOPE View page.")

                    if st.button("Create Another Session"):
                        dope_create_state["wizard_step"] = 1
                        dope_create_state["wizard_data"] = {}
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Error creating DOPE session: {str(e)}")
                    st.error("Please check your data and try again.")
