"""
DOPE Create Page Module

This module handles the creation of new DOPE (Data On Previous Engagement) sessions
using a wizard-style workflow.
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chronograph.service import ChronographService
from dope.service import DopeService


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


def render_step_3_cartridge_selection(user_id: str, supabase):
    """Step 3: Select cartridge with filtering"""
    st.subheader("Step 3: Select Cartridge")
    st.write("Use filters to find your cartridge, then select from the filtered list.")
    
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
    
    # Create filter options
    cartridge_types = get_cartridge_types(supabase)
    cartridge_makes = get_unique_cartridge_makes(all_cartridges)
    bullet_grains = get_unique_bullet_grains(all_cartridges)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cartridge_type_filter = st.selectbox(
            "Cartridge Type",
            options=["All"] + cartridge_types,
            help="Filter by cartridge type"
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
    
    # Apply filters
    bullet_grain_value = None if bullet_grain_filter == "All" else int(bullet_grain_filter.replace("gr", ""))
    filtered_cartridges = filter_cartridges(
        all_cartridges, 
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


def render_step_4_session_details():
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


def render_step_5_confirmation(chrono_session, rifle, cartridge, session_details):
    """Step 5: Confirmation and creation"""
    st.subheader("Step 5: Review & Create")
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
        
        with col2:
            st.write("**Session Details:**")
            st.write(f"- Cartridge Type: {cartridge['cartridge_type']}")
            st.write(f"- Session Name: {session_details['session_name'] or 'Not specified'}")
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
    progress_steps = ["Chrono Session", "Rifle", "Cartridge", "Details", "Confirm"]
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
        result = render_step_3_cartridge_selection(user["id"], supabase)
        if result:
            dope_create_state["wizard_data"]["cartridge"] = result
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back"):
                    dope_create_state["wizard_step"] = 2
                    st.rerun()
            with col2:
                if st.button("Next: Session Details", type="primary"):
                    dope_create_state["wizard_step"] = 4
                    st.rerun()

    elif current_step == 4:
        result = render_step_4_session_details()
        dope_create_state["wizard_data"]["session_details"] = result
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                dope_create_state["wizard_step"] = 3
                st.rerun()
        with col2:
            if st.button("Next: Review & Create", type="primary"):
                dope_create_state["wizard_step"] = 5
                st.rerun()

    elif current_step == 5:
        wizard_data = dope_create_state["wizard_data"]
        render_step_5_confirmation(
            wizard_data["chrono_session"],
            wizard_data["rifle"], 
            wizard_data["cartridge"],
            wizard_data["session_details"]
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back"):
                dope_create_state["wizard_step"] = 4
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
                    session_details = wizard_data["session_details"]
                    
                    # Prepare session data for database
                    session_data = {
                        "session_name": session_details.get("session_name") or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        "chrono_session_id": chrono_session.id,
                        "rifle_id": rifle["id"],
                        "cartridge_id": cartridge["id"],
                        "notes": session_details.get("notes"),
                        "status": "active",
                    }
                    
                    # Create the DOPE session
                    service = DopeService(supabase)
                    new_session = service.create_session(session_data, user["id"])
                    
                    st.success(f"✅ DOPE Session created successfully!")
                    st.success(f"Session ID: {new_session.id}")
                    st.info("You can now view your session in the DOPE View page.")
                    

                    if st.button("Create Another Session"):
                        dope_create_state["wizard_step"] = 1
                        dope_create_state["wizard_data"] = {}
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Error creating DOPE session: {str(e)}")
                    st.error("Please check your data and try again.")
