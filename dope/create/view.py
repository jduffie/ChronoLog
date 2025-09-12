"""
DOPE Create UI View

Handles all Streamlit UI components for DOPE session creation.
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Tuple


class DopeCreateView:
    """UI view layer for DOPE session creation"""
    
    def render_progress_indicator(self, current_step: int, progress_steps: List[str]):
        """Render the progress bar"""
        progress_cols = st.columns(len(progress_steps))
        for i, (col, step_name) in enumerate(zip(progress_cols, progress_steps), 1):
            with col:
                if current_step == 8:  # Success step - show all as completed
                    st.success(f"✅ {step_name}")
                elif i < current_step:
                    st.success(f"✅ {step_name}")
                elif i == current_step:
                    st.info(f"▶️ {step_name}")
                else:
                    st.write(f"⏸️ {step_name}")
        
        st.divider()
    
    def render_chrono_selection(self, unused_sessions) -> Optional[Any]:
        """Render chronograph session selection step"""
        st.subheader("Step 1: Select Chronograph Session")
        
        if not unused_sessions:
            st.warning("⚠️ No unused chronograph sessions found.")
            st.write("You need to upload chronograph data first before creating a DOPE session.")
            st.info("💡 Go to the Chronograph page to upload your shooting data, then return here.")
            return None
        
        # Create options for selectbox
        session_options = {}
        for session in unused_sessions:
            display_name = f"{session.datetime_local.strftime('%Y-%m-%d %H:%M')} - {session.session_name} - {session.shot_count} shots"
            session_options[display_name] = session
        
        selected_display = st.selectbox(
            "Available Chronograph Sessions",
            options=list(session_options.keys()),
            help="Sessions are listed by bullet type, grain weight, date, and shot count"
        )
        
        selected_session = session_options[selected_display]
        
        # Show session details
        with st.expander("📊 Session Details", expanded=True):
            col2, col3 = st.columns(2)
            
            with col2:
                st.metric("Shot Count", selected_session.shot_count)
                st.metric("Avg Velocity", f"{selected_session.avg_speed_fps:.1f} fps")
            
            with col3:
                st.metric("Std Deviation", f"{selected_session.std_dev_fps:.1f} fps")
                st.metric("Date", selected_session.datetime_local.strftime('%Y-%m-%d'))
        
        return selected_session
    
    def render_rifle_selection(self, rifles) -> Optional[Any]:
        """Render rifle selection step"""
        st.subheader("Step 2: Select Rifle")
        st.write("Choose the rifle used for this session.")
        
        if not rifles:
            st.warning("⚠️ No rifles found in your inventory.")
            st.write("You need to create a rifle entry first.")
            st.info("💡 **How to create a rifle:**\n"
                    "1. Go to the **Rifles** page in the navigation menu\n"
                    "2. Click on the **Create** tab\n"
                    "3. Fill out the rifle details and save\n"
                    "4. Return to this page and start over")
            return None
        
        # Create rifle options - handle both model objects and dictionaries
        rifle_options = {}
        for rifle in rifles:
            if hasattr(rifle, 'name'):  # Model object
                display_name = rifle.name
                cartridge_type = getattr(rifle, 'cartridge_type', None)
            else:  # Dictionary
                display_name = rifle['name']
                cartridge_type = rifle.get('cartridge_type')
            
            if cartridge_type:
                display_name += f" ({cartridge_type})"
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
                name = selected_rifle.name if hasattr(selected_rifle, 'name') else selected_rifle['name']
                cartridge_type = (getattr(selected_rifle, 'cartridge_type', None) 
                                if hasattr(selected_rifle, 'cartridge_type') 
                                else selected_rifle.get('cartridge_type', 'Not specified'))
                
                st.write(f"**Name:** {name}")
                st.write(f"**Cartridge Type:** {cartridge_type or 'Not specified'}")
            
            with col2:
                barrel_length = (getattr(selected_rifle, 'barrel_length', None)
                               if hasattr(selected_rifle, 'barrel_length')
                               else selected_rifle.get('barrel_length', 'Not specified'))
                barrel_twist = (getattr(selected_rifle, 'barrel_twist_ratio', None)
                              if hasattr(selected_rifle, 'barrel_twist_ratio')
                              else selected_rifle.get('barrel_twist_ratio', 'Not specified'))
                
                st.write(f"**Barrel Length:** {barrel_length or 'Not specified'}")
                st.write(f"**Twist Rate:** {barrel_twist or 'Not specified'}")
        
        return selected_rifle
    
    def render_cartridge_selection(
        self,
        all_cartridges,
        compatible_cartridges,
        cartridge_types,
        rifle_cartridge_type: str
    ) -> Optional[Any]:
        """Render cartridge selection step"""
        st.subheader("Step 3: Select Cartridge")
        st.write(f"Showing cartridges compatible with your rifle's cartridge type: **{rifle_cartridge_type}**")
        
        if not all_cartridges:
            st.warning("⚠️ No cartridges found in your inventory.")
            st.write("You need to create a cartridge entry first.")
            st.info("💡 **How to create a cartridge:**\n"
                    "1. Go to the **Cartridges** page in the navigation menu\n"
                    "2. Click on the **Create** tab\n"
                    "3. Add a factory or custom cartridge\n"
                    "4. Return to this page and start over")
            return None
        
        if not compatible_cartridges:
            st.warning(f"⚠️ No cartridges found that match your rifle's cartridge type: {rifle_cartridge_type}")
            st.write("You need to create a compatible cartridge first.")
            st.info("💡 **How to create a compatible cartridge:**\n"
                    "1. Go to the **Cartridges** page in the navigation menu\n"
                    "2. Click on the **Create** tab\n"
                    f"3. Add a cartridge with cartridge type: **{rifle_cartridge_type}**\n"
                    "4. Return to this page and start over")
            return None
        
        return compatible_cartridges
    
    def render_cartridge_filters(
        self,
        cartridge_types: List[str],
        cartridge_makes: List[str],
        bullet_grains: List[float],
        rifle_cartridge_type: str
    ) -> Dict[str, Any]:
        """Render cartridge filter controls"""
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
        
        # Convert bullet grain filter to numeric value
        bullet_grain_value = (None if bullet_grain_filter == "All" 
                             else float(bullet_grain_filter.replace("gr", "")))
        
        return {
            "cartridge_type": cartridge_type_filter if cartridge_type_filter != "All" else None,
            "cartridge_make": cartridge_make_filter if cartridge_make_filter != "All" else None,
            "bullet_grain": bullet_grain_value
        }
    
    def render_cartridge_options(self, filtered_cartridges) -> Optional[Any]:
        """Render cartridge selection dropdown"""
        if not filtered_cartridges:
            st.warning("⚠️ No cartridges match your filter criteria.")
            st.write("Try adjusting your filters or create a new cartridge.")
            return None
        
        st.write("---")
        
        # Create cartridge options
        cartridge_options = {}
        for cartridge in filtered_cartridges:
            make = cartridge.make or "Unknown"
            model = cartridge.model or "Unknown"
            bullet_make = cartridge.bullet_manufacturer or "Unknown"
            bullet_model = cartridge.bullet_model or "Unknown"
            bullet_weight = cartridge.bullet_weight_grains or "Unknown"
            
            display_name = f"{make} {model} - {bullet_make} {bullet_model} ({bullet_weight}gr)"
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
                st.write(f"**Cartridge Type:** {selected_cartridge.cartridge_type or 'Not specified'}")
                st.write(f"**Make:** {selected_cartridge.make or 'Unknown'}")
                st.write(f"**Model:** {selected_cartridge.model or 'Unknown'}")
            
            with col2:
                if selected_cartridge.bullet_manufacturer:
                    st.write(f"**Bullet:** {selected_cartridge.bullet_manufacturer} {selected_cartridge.bullet_model or ''}")
                    st.write(f"**Weight:** {selected_cartridge.bullet_weight_grains or 'Unknown'} gr")
                else:
                    st.write("**Bullet:** Not specified")
        
        return selected_cartridge
    
    def render_range_selection(self, ranges) -> Optional[Dict]:
        """Render range selection step"""
        st.subheader("Step 4: Select Range (Optional)")
        st.write("Choose the range where this session took place, or skip this step.")
        
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
    
    def render_weather_selection(self, weather_sources) -> Optional[Any]:
        """Render weather source selection step"""
        st.subheader("Step 5: Select Weather Source (Optional)")
        st.write("Choose the weather measurement device used, or skip this step.")
        
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
    
    def render_session_details(self) -> Dict[str, str]:
        """Render session details input step"""
        st.subheader("Step 6: Session Details")
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
    
    def render_confirmation(
        self,
        chrono_session,
        rifle,
        cartridge,
        range_data,
        weather_data,
        session_details
    ):
        """Render confirmation step"""
        st.subheader("Step 7: Review & Create")
        st.write("Review your DOPE session details before creating.")
        
        # Summary of selections
        with st.expander("Session Summary", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Chronograph Session:**")
                st.write(f"- Date: {chrono_session.datetime_local.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"- Shots: {chrono_session.shot_count}")
                
                st.write("**Rifle:**")
                rifle_name = rifle.name if hasattr(rifle, 'name') else rifle['name']
                rifle_cartridge = (getattr(rifle, 'cartridge_type', 'Not specified')
                                 if hasattr(rifle, 'cartridge_type')
                                 else rifle.get('cartridge_type', 'Not specified'))
                st.write(f"- Name: {rifle_name}")
                st.write(f"- Cartridge: {rifle_cartridge}")
                
                st.write("**Range:**")
                if range_data:
                    st.write(f"- Name: {range_data['range_name']}")
                    st.write(f"- Distance: {range_data.get('distance_m', 'Unknown')} meters")
                else:
                    st.write("- None selected")
            
            with col2:
                st.write("**Cartridge:**")
                cartridge_type = (cartridge.cartridge_type if hasattr(cartridge, 'cartridge_type')
                                else cartridge['cartridge_type'])
                cartridge_make = (cartridge.make if hasattr(cartridge, 'make')
                                else cartridge.get('make', 'Unknown'))
                cartridge_model = (cartridge.model if hasattr(cartridge, 'model')
                                 else cartridge.get('model', 'Unknown'))
                
                st.write(f"- Type: {cartridge_type}")
                st.write(f"- Make/Model: {cartridge_make} - {cartridge_model}")
                
                st.write("**Bullet:**")
                if hasattr(cartridge, 'bullet_manufacturer'):
                    bullet_make = cartridge.bullet_manufacturer or 'Unknown'
                    bullet_model = cartridge.bullet_model or 'Unknown'
                    bullet_weight = cartridge.bullet_weight_grains or 'Unknown'
                    st.write(f"- Make/Model: {bullet_make} - {bullet_model}")
                    st.write(f"- Weight: {bullet_weight}gr")
                else:
                    # Handle dictionary format for backward compatibility
                    bullet = cartridge.get('bullets', {})
                    if bullet:
                        st.write(f"- Make/Model: {bullet.get('manufacturer', 'Unknown')} - {bullet.get('model', 'Unknown')}")
                        st.write(f"- Weight: {bullet.get('weight_grains', 'Unknown')}gr")
                    else:
                        st.write("- Unknown")
                
                st.write("**Weather Source:**")
                if weather_data:
                    st.write(f"- Name: {weather_data.name}")
                    st.write(f"- Type: {weather_data.source_type}")
                else:
                    st.write("- None selected")
                
                st.write("**Session:**")
                st.write(f"- Name: {session_details['session_name'] or 'Not specified'}")
                notes = session_details.get('notes', '')
                display_notes = notes[:50] + '...' if len(notes) > 50 else notes or 'None'
                st.write(f"- Notes: {display_notes}")
    
    def render_success(self, created_session, weather_results):
        """Render success step"""
        st.subheader("✅ DOPE Session Created Successfully!")
        
        if created_session:
            st.success(f"Session ID: {created_session.id}")
            
            if weather_results and not weather_results.get("error"):
                st.success(f"🌤️ Weather data processed: {weather_results['weather_measurement_count']} measurements")
                st.success(f"🎯 Shot associations: {weather_results['associations_made']} of {weather_results['dope_measurement_count']} shots")
                st.info("Weather measurements have been associated with your shots.")
            elif weather_results and weather_results.get("error"):
                st.warning(f"⚠️ Weather association warning: {weather_results['error']}")
                st.info("DOPE session created successfully, but weather data could not be processed.")
        
        st.info("You can now view your session in the DOPE View page.")
    
    def render_navigation_buttons(self, current_step: int, max_step: int, data_valid: bool = True):
        """Render navigation buttons"""
        col1, col2 = st.columns(2)
        
        with col1:
            if current_step > 1 and current_step < 8:  # Not on first step or success step
                return st.button("← Back")
        
        with col2:
            if current_step < max_step and data_valid:
                if current_step == max_step - 1:  # Last step before confirmation
                    return st.button("Next: Review & Create", type="primary")
                elif current_step == max_step:  # Confirmation step
                    return st.button("Create DOPE Session", type="primary")
                else:
                    next_labels = {
                        1: "Next: Select Rifle",
                        2: "Next: Select Cartridge", 
                        3: "Next: Select Range",
                        4: "Next: Select Weather",
                        5: "Next: Session Details"
                    }
                    return st.button(next_labels.get(current_step, "Next"), type="primary")
            elif current_step == 8:  # Success step
                return st.button("Create Another Session", type="primary")
        
        return False