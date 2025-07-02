import streamlit as st

def render_locations_tab(user, supabase):
    """Render the Locations tab"""
    st.header("Locations")
    
    # Display locations table first
    try:
        # Get all approved locations (global read access)
        locations_response = supabase.table("locations").select("*").execute()
        approved_locations = locations_response.data
        
        # Get user's draft location requests
        draft_locations_response = supabase.table("locations_draft").select("*").eq("user_email", user["email"]).execute()
        user_draft_locations = draft_locations_response.data
        
        # Display approved locations first
        if approved_locations:
            st.subheader("📍 Available Locations")
            
            # Add headers first
            col1, col2, col3, col4, col5 = st.columns([4, 2, 2, 2, 2])
            with col1:
                st.markdown("**Name**")
            with col2:
                st.markdown("**Altitude (ft)**")
            with col3:
                st.markdown("**Azimuth (°)**")
            with col4:
                st.markdown("**Latitude**")
            with col5:
                st.markdown("**Longitude**")
            
            st.markdown("---")
            
            # Create a row for each approved location
            for i, location in enumerate(approved_locations):
                col1, col2, col3, col4, col5 = st.columns([4, 2, 2, 2, 2])
                
                with col1:
                    if location.get('google_maps_link'):
                        st.markdown(f"[{location['name']}]({location['google_maps_link']})")
                    else:
                        st.write(location['name'])
                
                with col2:
                    st.write(f"{location['altitude']}")
                
                with col3:
                    st.write(f"{location['azimuth']}")
                
                with col4:
                    st.write(f"{location['latitude']:.6f}" if location['latitude'] else "")
                
                with col5:
                    st.write(f"{location['longitude']:.6f}" if location['longitude'] else "")
        
        # Display user's draft location requests
        if user_draft_locations:
            st.subheader("🟡 Your Pending Requests")
            
            # Add headers first
            col1, col2, col3, col4, col5 = st.columns([4, 2, 2, 2, 2])
            with col1:
                st.markdown("**Name**")
            with col2:
                st.markdown("**Altitude (ft)**")
            with col3:
                st.markdown("**Azimuth (°)**")
            with col4:
                st.markdown("**Latitude**")
            with col5:
                st.markdown("**Longitude**")
            
            st.markdown("---")
            
            # Create a row for each draft location
            for i, location in enumerate(user_draft_locations):
                col1, col2, col3, col4, col5 = st.columns([4, 2, 2, 2, 2])
                
                with col1:
                    if location.get('google_maps_link'):
                        st.markdown(f"🟡 [{location['name']}]({location['google_maps_link']})")
                    else:
                        st.write(f"🟡 {location['name']}")
                
                with col2:
                    st.write(f"{location['altitude']}")
                
                with col3:
                    st.write(f"{location['azimuth']}")
                
                with col4:
                    st.write(f"{location['latitude']:.6f}" if location['latitude'] else "")
                
                with col5:
                    st.write(f"{location['longitude']:.6f}" if location['longitude'] else "")
        
        # Show message if no locations at all
        if not approved_locations and not user_draft_locations:
            st.info("No locations available. Submit a request to add a new location!")
            
    except Exception as e:
        st.error(f"Error loading locations: {e}")
    
    # Add some spacing
    st.markdown("---")
    
    # Location request form below the table - left-aligned with fixed width
    form_col, _ = st.columns([400, 1])
    
    with form_col:
        st.subheader("📋 Request New Location")
        
        with st.form("location_request_form"):
            st.write("Fill in all fields to request a new location:")
            
            # Location name with max 45 characters
            location_name = st.text_input(
                "Location Name *",
                placeholder="e.g., Frontline Defense - 1000yd",
                help="Descriptive name for the shooting location",
                max_chars=45
            )
            
            # Create two rows for number inputs
            col_alt, col_az = st.columns(2)
            
            with col_alt:
                altitude = st.number_input(
                    "Altitude (ft) *",
                    min_value=0.0,
                    max_value=20000.0,
                    step=1.0,
                    help="Elevation above sea level in feet"
                )
            
            with col_az:
                azimuth = st.number_input(
                    "Azimuth (°) *",
                    min_value=0.0,
                    max_value=360.0,
                    step=0.1,
                    help="Shooting direction in degrees (0-360)"
                )
            
            col_lat, col_lon = st.columns(2)
            
            with col_lat:
                latitude = st.number_input(
                    "Latitude *",
                    min_value=-90.0,
                    max_value=90.0,
                    step=0.000001,
                    format="%.6f",
                    help="Latitude in decimal degrees"
                )
            
            with col_lon:
                longitude = st.number_input(
                    "Longitude *",
                    min_value=-180.0,
                    max_value=180.0,
                    step=0.000001,
                    format="%.6f",
                    help="Longitude in decimal degrees"
                )
            
            # Submit button
            submitted = st.form_submit_button("📍 Submit Location Request", type="primary")
        
        if submitted:
            # Validate required fields
            if not location_name or not location_name.strip():
                st.error("❌ Location name is required")
            elif altitude <= 0:
                st.error("❌ Altitude must be greater than 0")
            elif latitude == 0.0 and longitude == 0.0:
                st.error("❌ Please provide valid coordinates")
            else:
                try:
                    # Generate Google Maps link
                    google_maps_link = f"https://maps.google.com/?q={latitude},{longitude}"
                    
                    # Create location request record
                    location_data = {
                        "user_email": user["email"],
                        "name": location_name.strip(),
                        "altitude": altitude,
                        "azimuth": azimuth,
                        "latitude": latitude,
                        "longitude": longitude,
                        "google_maps_link": google_maps_link
                    }
                    
                    # Insert into locations_draft table
                    supabase.table("locations_draft").insert(location_data).execute()
                    
                    st.success("✅ Location request submitted successfully!")
                    st.info("📋 Your location request is pending approval and will be reviewed by administrators.")
                    st.info(f"📍 [View on Google Maps]({google_maps_link})")
                    
                    # Rerun to clear the form
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Failed to submit location request: {e}")