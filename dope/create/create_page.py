"""
DOPE Create Page Module

This module orchestrates the creation of new DOPE (Data On Previous Engagement) sessions
using a wizard-style workflow. It coordinates between the business logic and UI view layers.
"""

import streamlit as st
from datetime import datetime
from .business import DopeCreateBusiness
from .view import DopeCreateView


def render_create_page(user, supabase):
    """
    Render the DOPE Create page with wizard-style workflow.
    
    This function orchestrates between the business logic and UI view layers.
    """
    st.write("Follow the steps below to create a new DOPE (Data On Previous Engagement) session.")
    
    # Initialize services
    business = DopeCreateBusiness(supabase)
    view = DopeCreateView()
    
    # Initialize private session state for DOPE Create
    if "dope_create" not in st.session_state:
        st.session_state.dope_create = {}
    
    dope_create_state = st.session_state.dope_create
    
    # Reset state when navigating from another page (detect fresh page load)
    if "dope_create_initialized" not in dope_create_state:
        dope_create_state["wizard_step"] = 1
        dope_create_state["wizard_data"] = {}
        dope_create_state["dope_create_initialized"] = True
    
    # Initialize wizard state if missing
    if "wizard_step" not in dope_create_state:
        dope_create_state["wizard_step"] = 1
    if "wizard_data" not in dope_create_state:
        dope_create_state["wizard_data"] = {}
    
    # Progress indicator
    progress_steps = ["Chrono", "Rifle", "Cartridge", "Range", "Weather", "Details", "Confirm"]
    current_step = dope_create_state["wizard_step"]
    
    # Render progress bar
    view.render_progress_indicator(current_step, progress_steps)
    
    # Handle each step
    try:
        if current_step == 1:
            _handle_chrono_selection_step(business, view, dope_create_state, user["id"])
        
        elif current_step == 2:
            _handle_rifle_selection_step(business, view, dope_create_state, user["id"])
        
        elif current_step == 3:
            _handle_cartridge_selection_step(business, view, dope_create_state, user["id"])
        
        elif current_step == 4:
            _handle_range_selection_step(business, view, dope_create_state, user["id"])
        
        elif current_step == 5:
            _handle_weather_selection_step(business, view, dope_create_state, user["id"])
        
        elif current_step == 6:
            _handle_session_details_step(view, dope_create_state)
        
        elif current_step == 7:
            _handle_confirmation_step(business, view, dope_create_state, user["id"])
        
        elif current_step == 8:
            _handle_success_step(view, dope_create_state)
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.error("Please check your data and try again.")


def _handle_chrono_selection_step(business, view, dope_create_state, user_id):
    """Handle chronograph session selection step"""
    unused_sessions = business.get_unused_chrono_sessions(user_id)
    result = view.render_chrono_selection(unused_sessions)
    
    if result:
        dope_create_state["wizard_data"]["chrono_session"] = result
        
        # Capture time window for weather measurement filtering
        try:
            time_window = business.get_chrono_session_time_window(user_id, result.id)
            dope_create_state["wizard_data"]["time_window"] = time_window
        except Exception as e:
            st.warning(f"Could not determine time window for weather filtering: {str(e)}")
            dope_create_state["wizard_data"]["time_window"] = None
        
        if st.button("Next: Select Rifle", type="primary"):
            dope_create_state["wizard_step"] = 2
            st.rerun()


def _handle_rifle_selection_step(business, view, dope_create_state, user_id):
    """Handle rifle selection step"""
    rifles = business.get_rifles_for_user(user_id)
    result = view.render_rifle_selection(rifles)
    
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


def _handle_cartridge_selection_step(business, view, dope_create_state, user_id):
    """Handle cartridge selection step"""
    all_cartridges = business.get_cartridges_for_user(user_id)
    
    # Get rifle cartridge type
    rifle = dope_create_state["wizard_data"]["rifle"]
    rifle_cartridge_type = (rifle.cartridge_type if hasattr(rifle, 'cartridge_type') 
                           else rifle.get("cartridge_type"))
    
    # Filter cartridges by rifle type
    compatible_cartridges = business.filter_cartridges_by_rifle_type(
        all_cartridges, rifle_cartridge_type
    )
    
    # Get filter options
    cartridge_types = business.get_cartridge_types()
    
    # Check if we have compatible cartridges before proceeding
    cartridge_result = view.render_cartridge_selection(
        all_cartridges, compatible_cartridges, cartridge_types, rifle_cartridge_type or "Unknown"
    )
    
    if cartridge_result:
        # Render filters
        cartridge_makes = business.get_unique_cartridge_makes(compatible_cartridges)
        bullet_grains = business.get_unique_bullet_grains(compatible_cartridges)
        
        filters = view.render_cartridge_filters(
            cartridge_types, cartridge_makes, bullet_grains, rifle_cartridge_type or ""
        )
        
        # Apply filters
        filtered_cartridges = business.filter_cartridges(
            compatible_cartridges,
            filters["cartridge_type"],
            filters["cartridge_make"], 
            filters["bullet_grain"]
        )
        
        # Render cartridge selection
        selected_cartridge = view.render_cartridge_options(filtered_cartridges)
        
        if selected_cartridge:
            dope_create_state["wizard_data"]["cartridge"] = selected_cartridge
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back"):
                    dope_create_state["wizard_step"] = 2
                    st.rerun()
            with col2:
                if st.button("Next: Select Range", type="primary"):
                    dope_create_state["wizard_step"] = 4
                    st.rerun()


def _handle_range_selection_step(business, view, dope_create_state, user_id):
    """Handle range selection step"""
    ranges = business.get_ranges_for_user(user_id)
    result = view.render_range_selection(ranges)
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


def _handle_weather_selection_step(business, view, dope_create_state, user_id):
    """Handle weather selection step"""
    weather_sources = business.get_weather_sources_for_user(user_id)
    result = view.render_weather_selection(weather_sources)
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


def _handle_session_details_step(view, dope_create_state):
    """Handle session details input step"""
    result = view.render_session_details()
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


def _handle_confirmation_step(business, view, dope_create_state, user_id):
    """Handle confirmation and creation step"""
    wizard_data = dope_create_state["wizard_data"]
    
    view.render_confirmation(
        wizard_data["chrono_session"],
        wizard_data["rifle"],
        wizard_data["cartridge"],
        wizard_data.get("range"),
        wizard_data.get("weather"),
        wizard_data["session_details"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            dope_create_state["wizard_step"] = 6
            st.rerun()
    
    with col2:
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
                session_data = business.prepare_session_data(
                    chrono_session, rifle, cartridge, range_data,
                    weather_data, session_details, time_window
                )
                
                # Create the DOPE session
                new_session = business.create_dope_session(session_data, user_id)
                
                # Process weather association if weather source was selected
                weather_association_results = None
                if weather_data and time_window:
                    try:
                        weather_association_results = business.associate_weather_with_session(
                            user_id, new_session.id, weather_data.id, 
                            time_window[0], time_window[1]
                        )
                        
                        if weather_association_results.get("error"):
                            st.warning(f"⚠️ Weather association warning: {weather_association_results['error']}")
                        else:
                            # Update DOPE session with median weather values
                            business.update_session_with_weather_data(
                                new_session.id, weather_association_results
                            )
                            st.success(f"🌤️ Weather data processed: {weather_association_results['weather_measurement_count']} measurements")
                            st.success(f"🎯 Shot associations: {weather_association_results['associations_made']} of {weather_association_results['dope_measurement_count']} shots")
                    
                    except Exception as weather_error:
                        st.warning(f"⚠️ Weather association failed: {str(weather_error)}")
                        st.info("DOPE session created successfully, but weather data could not be processed.")
                
                # Advance to success step (step 8)
                dope_create_state["wizard_step"] = 8
                dope_create_state["wizard_data"]["created_session"] = new_session
                dope_create_state["wizard_data"]["weather_results"] = weather_association_results
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error creating DOPE session: {str(e)}")
                st.error("Please check your data and try again.")


def _handle_success_step(view, dope_create_state):
    """Handle success step"""
    wizard_data = dope_create_state["wizard_data"]
    created_session = wizard_data.get("created_session")
    weather_results = wizard_data.get("weather_results")
    
    view.render_success(created_session, weather_results)
    
    if st.button("Create Another Session", type="primary"):
        dope_create_state["wizard_step"] = 1
        dope_create_state["wizard_data"] = {}
        st.rerun()