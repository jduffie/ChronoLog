import streamlit as st

def render_locations_tab(user, supabase):
    """Render the Locations tab"""
    st.header("Locations")
    
    # Display locations table first
    try:
        # Get all approved locations (global read access)
        locations_response = supabase.table("locations").select("*").execute()
        approved_locations = locations_response.data
        
        
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
        
        # Show message if no locations available
        if not approved_locations:
            st.info("No locations available.")
            
    except Exception as e:
        st.error(f"Error loading locations: {e}")