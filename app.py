
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, timezone
from supabase import create_client
import requests
from urllib.parse import urlencode
import math

# Set wide layout for more space - must be first Streamlit command
st.set_page_config(layout="wide")

# Auth0 settings
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
CLIENT_ID = st.secrets["auth0"]["client_id"]
CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
REDIRECT_URI = st.secrets["auth0"].get("redirect_uri", "http://localhost:8501")
AUTH0_BASE_URL = f"https://{AUTH0_DOMAIN}"

def show_login_button():
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile email",
        "audience": f"{AUTH0_BASE_URL}/userinfo"
    })
    login_url = f"{AUTH0_BASE_URL}/authorize?{query}"
    st.markdown(f"[Log in with Google]({login_url})")

def get_user_info(code):
    token_url = f"{AUTH0_BASE_URL}/oauth/token"
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    token_resp = requests.post(token_url, json=token_payload).json()
    access_token = token_resp.get("access_token")
    userinfo_url = f"{AUTH0_BASE_URL}/userinfo"
    userinfo_resp = requests.get(
        userinfo_url, headers={"Authorization": f"Bearer {access_token}"}
    )
    return userinfo_resp.json()

# Auth check
query_params = st.query_params
if "code" in query_params:
    code = query_params["code"]
    user_info = get_user_info(code)
    st.session_state["user"] = user_info
    st.query_params.clear()

if "user" not in st.session_state:
    show_login_button()
    st.stop()

user = st.session_state["user"]
st.sidebar.success(f"Logged in as {user['name']}")

# Supabase setup
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
bucket = st.secrets["supabase"]["bucket"]
supabase = create_client(url, key)

# Main app tabs
tab1, tab2, tab3, tab4 = st.tabs(["Upload Files", "My Files", "View Session", "Locations"])

with tab2:
    st.header("📁 My Uploaded Files")
    
    try:
        # Get files directly from storage
        files_list = supabase.storage.from_(bucket).list(f"{user['email']}")
        
        if files_list:
            st.write(f"You have {len(files_list)} file(s) in storage:")
            
            for file_item in files_list:
                if file_item.get('name'):
                    file_path = f"{user['email']}/{file_item['name']}"
                    
                    with st.expander(f"📄 {file_item['name']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if 'created_at' in file_item:
                                st.write(f"**Uploaded:** {pd.to_datetime(file_item['created_at']).strftime('%Y-%m-%d %H:%M')}")
                            if 'metadata' in file_item and file_item['metadata']:
                                if 'size' in file_item['metadata']:
                                    size_mb = file_item['metadata']['size'] / (1024 * 1024)
                                    st.write(f"**Size:** {size_mb:.2f} MB")
                        
                        with col2:
                            # Download button for file
                            if st.button("📥 Download File", key=f"download_file_{file_item['name']}"):
                                try:
                                    file_data = supabase.storage.from_(bucket).download(file_path)
                                    st.download_button(
                                        label="💾 Save File",
                                        data=file_data,
                                        file_name=file_item['name'],
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key=f"save_file_{file_item['name']}"
                                    )
                                except Exception as e:
                                    st.error(f"Error downloading file: {e}")
                            
                            # Delete button with confirmation
                            if st.button("🗑️ Delete File", key=f"delete_file_{file_item['name']}", type="secondary"):
                                st.session_state[f"confirm_delete_file_{file_item['name']}"] = True
                            
                            # Show confirmation dialog
                            if st.session_state.get(f"confirm_delete_file_{file_item['name']}", False):
                                st.warning("⚠️ Are you sure you want to delete this file? This action cannot be undone!")
                                col_yes, col_no = st.columns(2)
                                
                                with col_yes:
                                    if st.button("✅ Yes, Delete", key=f"confirm_yes_file_{file_item['name']}", type="primary"):
                                        try:
                                            # Only delete file from storage
                                            supabase.storage.from_(bucket).remove([file_path])
                                            
                                            # Clear confirmation state and rerun
                                            del st.session_state[f"confirm_delete_file_{file_item['name']}"]
                                            st.success("File deleted successfully!")
                                            st.rerun()
                                            
                                        except Exception as e:
                                            st.error(f"Error deleting file: {e}")
                                
                                with col_no:
                                    if st.button("❌ Cancel", key=f"confirm_no_file_{file_item['name']}"):
                                        del st.session_state[f"confirm_delete_file_{file_item['name']}"]
                                        st.rerun()
        else:
            st.info("No files uploaded yet. Use the 'Upload Files' tab to get started!")
            
    except Exception as e:
        st.error(f"Error loading your files: {e}")

with tab3:
    st.header("View Session")
    
    try:
        # Get user's sessions for selection
        sessions_response = supabase.table("sessions").select("*").eq("user_email", user["email"]).order("uploaded_at", desc=True).execute()
        sessions = sessions_response.data
        
        if sessions:
            # Create session options for selectbox
            session_options = {}
            for session in sessions:
                # Use session_timestamp if available, otherwise fall back to uploaded_at
                if 'session_timestamp' in session and session['session_timestamp']:
                    session_time = pd.to_datetime(session['session_timestamp']).strftime('%Y-%m-%d %H:%M')
                else:
                    session_time = pd.to_datetime(session['uploaded_at']).strftime('%Y-%m-%d %H:%M')
                display_name = f"{session_time} - {session['bullet_type']} ({session['bullet_grain']}gr) - {session['sheet_name']}"
                session_options[display_name] = session
            
            # Make session selection more prominent
            st.markdown("### Select Session to View")
            selected_session_display = st.selectbox(
                "Sessions:",
                options=list(session_options.keys()),
                help="Sessions are ordered by upload time (newest first)",
                key="session_selector"
            )
            
            if selected_session_display:
                selected_session = session_options[selected_session_display]
                
                # Prepare session details values
                if 'session_timestamp' in selected_session and selected_session['session_timestamp']:
                    session_dt = pd.to_datetime(selected_session['session_timestamp'])
                    datetime_value = session_dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    upload_dt = pd.to_datetime(selected_session['uploaded_at'])
                    datetime_value = f"{upload_dt.strftime('%Y-%m-%d %H:%M:%S')} (upload)"
                
                # Create session details table
                session_details_df = pd.DataFrame({
                    'Date/Time': [datetime_value],
                    'Bullet Type': [selected_session['bullet_type']],
                    'Bullet Weight': [f"{selected_session['bullet_grain']} gr"],
                    'Sheet Name': [selected_session['sheet_name']]
                })
                
                st.dataframe(session_details_df, use_container_width=True, hide_index=True)
                
                # Location Section
                st.subheader("Location")
                
                # Get locations for dropdown (all approved locations)
                try:
                    locations_response = supabase.table("locations").select("*").execute()
                    active_locations = locations_response.data
                except:
                    active_locations = []
                
                # Location dropdown
                location_options = ["None"] + [f"{loc['name']}" for loc in active_locations]
                location_ids = [None] + [loc['id'] for loc in active_locations]
                
                # Find current location index
                current_location_index = 0
                if selected_session.get('location_id'):
                    try:
                        current_location_index = location_ids.index(selected_session['location_id'])
                    except ValueError:
                        current_location_index = 0
                
                selected_location = st.selectbox(
                    "Location:",
                    options=location_options,
                    index=current_location_index,
                    help="Select the shooting location for this session"
                )
                
                # Update location if changed
                if selected_location != "None":
                    selected_location_id = location_ids[location_options.index(selected_location)]
                    if selected_location_id != selected_session.get('location_id'):
                        try:
                            supabase.table("sessions").update({"location_id": selected_location_id}).eq("id", selected_session['id']).execute()
                            st.success(f"Location updated to: {selected_location}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update location: {e}")
                elif selected_session.get('location_id'):
                    # User selected "None" but session had a location - clear it
                    try:
                        supabase.table("sessions").update({"location_id": None}).eq("id", selected_session['id']).execute()
                        st.success("Location cleared")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to clear location: {e}")
                
                # Get current location details for display
                if selected_session.get('location_id'):
                    # Get full location details from database
                    try:
                        location_response = supabase.table("locations").select("*").eq("id", selected_session['location_id']).execute()
                        if location_response.data:
                            current_location = location_response.data[0]
                            
                            # Create location details table
                            location_df = pd.DataFrame({
                                'Name': [current_location['name']],
                                'Altitude (ft)': [current_location['altitude']],
                                'Azimuth (°)': [current_location['azimuth']],
                                'Latitude': [f"{current_location['latitude']:.6f}" if current_location['latitude'] else ""],
                                'Longitude': [f"{current_location['longitude']:.6f}" if current_location['longitude'] else ""]
                            })
                            
                            st.dataframe(location_df, use_container_width=True, hide_index=True)
                            
                            # Add Google Maps link if available
                            if current_location.get('google_maps_link'):
                                st.markdown(f"📍 [View on Google Maps]({current_location['google_maps_link']})")
                        
                        else:
                            st.info("Location details not found")
                    except Exception as e:
                        st.error(f"Error loading location details: {e}")
                else:
                    st.info("No location assigned to this session")
                
                # Get measurement count and statistics
                measurements_response = supabase.table("measurements").select("*").eq("session_id", selected_session['id']).execute()
                measurements = measurements_response.data
                
                if measurements:
                    df = pd.DataFrame(measurements)
                    
                    # Statistics
                    st.subheader("Session Statistics")
                    
                    # Calculate statistics
                    avg_velocity = df['speed_fps'].mean()
                    std_velocity = df['speed_fps'].std()
                    max_velocity = df['speed_fps'].max()
                    min_velocity = df['speed_fps'].min()
                    velocity_spread = max_velocity - min_velocity if not pd.isna(max_velocity) and not pd.isna(min_velocity) else None
                    
                    # Create statistics table
                    statistics_df = pd.DataFrame({
                        'Total Shots': [len(measurements)],
                        'Avg Velocity (fps)': [f"{avg_velocity:.1f}" if not pd.isna(avg_velocity) else "N/A"],
                        'Std Deviation (fps)': [f"{std_velocity:.1f}" if not pd.isna(std_velocity) else "N/A"],
                        'Velocity Spread (fps)': [f"{velocity_spread:.1f}" if velocity_spread is not None else "N/A"]
                    })
                    
                    st.dataframe(statistics_df, use_container_width=True, hide_index=True)
                    
                    # Display measurement data table
                    st.subheader("Measurement Data")
                    
                    # Reorder columns for better display
                    display_columns = ['shot_number', 'speed_fps', 'delta_avg_fps', 'ke_ft_lb', 'power_factor', 'time_local']
                    if 'clean_bore' in df.columns:
                        display_columns.append('clean_bore')
                    if 'cold_bore' in df.columns:
                        display_columns.append('cold_bore')
                    if 'shot_notes' in df.columns:
                        display_columns.append('shot_notes')
                    
                    # Only show columns that exist
                    display_columns = [col for col in display_columns if col in df.columns]
                    st.dataframe(df[display_columns], use_container_width=True)
                else:
                    st.warning("No measurement data found for this session.")
        else:
            st.info("No sessions found. Upload a file first to create sessions.")
            
    except Exception as e:
        st.error(f"Error loading sessions: {e}")

with tab1:
    st.header("📤 Upload Garmin Xero File")
    
    # Upload and parse Excel
    uploaded_file = st.file_uploader("Upload Garmin Xero Excel File", type=["xlsx"])
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        file_name = f"{user['email']}/{uploaded_file.name}"
        supabase.storage.from_(bucket).upload(file_name, file_bytes, {"content-type": uploaded_file.type})

        xls = pd.ExcelFile(uploaded_file)
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
            bullet_meta = df.iloc[0, 0]
            parts = bullet_meta.split(",")
            bullet_type = parts[0].strip()
            bullet_grain = float(parts[1].strip().replace("gr", "")) if len(parts) > 1 else None

            header_row = 1
            data = df.iloc[header_row+1:].dropna(subset=[1])
            data.columns = df.iloc[header_row]
            
            # Extract session timestamp from the DATE cell at the bottom of the sheet
            session_timestamp = None
            try:
                # Look for the date in the last few rows of the sheet
                for i in range(len(df) - 1, max(len(df) - 10, 0), -1):
                    for col in range(df.shape[1]):
                        cell_value = df.iloc[i, col]
                        if pd.notna(cell_value):
                            cell_str = str(cell_value).strip()
                            # Look for date patterns like "May 26, 2025 at 11:01 AM"
                            if " at " in cell_str and any(month in cell_str for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                                try:
                                    # Parse the date string
                                    parsed_date = pd.to_datetime(cell_str)
                                    session_timestamp = parsed_date.isoformat()
                                    break
                                except:
                                    continue
                    if session_timestamp:
                        break
            except:
                pass
            
            # Fall back to current date if we couldn't extract from sheet
            if not session_timestamp:
                session_timestamp = datetime.now(timezone.utc).isoformat()

            # Helper function to safely convert to float, returning None for NaN/invalid values
            def safe_float(value):
                try:
                    if pd.isna(value) or value == '' or value is None:
                        return None
                    float_val = float(value)
                    if math.isnan(float_val):
                        return None
                    return float_val
                except (ValueError, TypeError):
                    return None

            # Helper function to safely convert to int
            def safe_int(value):
                try:
                    if pd.isna(value) or value == '' or value is None:
                        return None
                    return int(float(value))  # Convert via float first to handle "1.0" format
                except (ValueError, TypeError):
                    return None

            session_id = str(uuid.uuid4())
            supabase.table("sessions").insert({
                "id": session_id,
                "user_email": user["email"],
                "sheet_name": sheet,
                "bullet_type": bullet_type,
                "bullet_grain": bullet_grain,
                "session_timestamp": session_timestamp,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "file_path": file_name
            }).execute()

            valid_measurements = 0
            skipped_measurements = 0

            for _, row in data.iterrows():
                # Validate required fields
                shot_number = safe_int(row.get("#"))
                speed_fps = safe_float(row.get("Speed (FPS)"))
                
                # Skip rows without essential data
                if shot_number is None or speed_fps is None:
                    skipped_measurements += 1
                    continue

                try:
                    # Clean time string to remove non-breaking spaces and other Unicode issues
                    def clean_time_string(time_value):
                        if pd.isna(time_value) or time_value is None:
                            return None
                        time_str = str(time_value)
                        # Replace non-breaking space and other Unicode spaces with regular space
                        time_str = time_str.replace('\u202f', ' ')  # Non-breaking thin space
                        time_str = time_str.replace('\u00a0', ' ')  # Non-breaking space
                        time_str = time_str.replace('\u2009', ' ')  # Thin space
                        time_str = time_str.strip()
                        return time_str if time_str else None

                    measurement_data = {
                        "session_id": session_id,
                        "shot_number": shot_number,
                        "speed_fps": speed_fps,
                        "delta_avg_fps": safe_float(row.get("Δ AVG (FPS)")),
                        "ke_ft_lb": safe_float(row.get("KE (FT-LB)")),
                        "power_factor": safe_float(row.get("Power Factor (kgr⋅ft/s)")),
                        "time_local": clean_time_string(row.get("Time")),
                        "clean_bore": bool(row.get("Clean Bore")) if "Clean Bore" in row and not pd.isna(row.get("Clean Bore")) else None,
                        "cold_bore": bool(row.get("Cold Bore")) if "Cold Bore" in row and not pd.isna(row.get("Cold Bore")) else None,
                        "shot_notes": str(row.get("Shot Notes")) if "Shot Notes" in row and not pd.isna(row.get("Shot Notes")) else None
                    }
                    
                    supabase.table("measurements").insert(measurement_data).execute()
                    valid_measurements += 1
                    
                except Exception as e:
                    st.warning(f"Skipped row {shot_number}: {e}")
                    skipped_measurements += 1

            # Show upload summary
            if skipped_measurements > 0:
                st.warning(f"⚠️ Processed {valid_measurements} measurements, skipped {skipped_measurements} rows with missing data")
            else:
                st.success(f"✅ Successfully processed {valid_measurements} measurements")

        st.success("Upload complete!")

with tab4:
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
