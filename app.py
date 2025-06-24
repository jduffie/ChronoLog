
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, timezone
from supabase import create_client
import requests
from urllib.parse import urlencode
import math

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
tab1, tab2, tab3 = st.tabs(["Upload Files", "My Files", "View Session"])

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
    st.header("🎯 View Session")
    
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
            
            # Session selection
            selected_session_display = st.selectbox(
                "📅 Select a session by date and time:",
                options=list(session_options.keys()),
                help="Sessions are ordered by upload time (newest first)"
            )
            
            if selected_session_display:
                selected_session = session_options[selected_session_display]
                
                # Display session metadata
                st.subheader("📊 Session Metadata")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Show session timestamp if available
                    if 'session_timestamp' in selected_session and selected_session['session_timestamp']:
                        session_dt = pd.to_datetime(selected_session['session_timestamp'])
                        st.metric("🎯 Session Date", session_dt.strftime('%Y-%m-%d'))
                        st.metric("🕐 Session Time", session_dt.strftime('%H:%M:%S'))
                    else:
                        st.metric("📅 Upload Date", pd.to_datetime(selected_session['uploaded_at']).strftime('%Y-%m-%d'))
                        st.metric("⏰ Upload Time", pd.to_datetime(selected_session['uploaded_at']).strftime('%H:%M:%S'))
                    st.metric("🔫 Bullet Type", selected_session['bullet_type'])
                
                with col2:
                    st.metric("⚖️ Bullet Weight", f"{selected_session['bullet_grain']} gr")
                    with st.container():
                        st.write("📄 **Sheet Name**")
                        st.write(f"<small>{selected_session['sheet_name']}</small>", unsafe_allow_html=True)
                
                # Get measurement count and statistics
                measurements_response = supabase.table("measurements").select("*").eq("session_id", selected_session['id']).execute()
                measurements = measurements_response.data
                
                if measurements:
                    df = pd.DataFrame(measurements)
                    
                    # Statistics
                    st.subheader("📈 Session Statistics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("🔢 Total Shots", len(measurements))
                    
                    with col2:
                        avg_velocity = df['speed_fps'].mean()
                        st.metric("📊 Avg Velocity", f"{avg_velocity:.1f} fps" if not pd.isna(avg_velocity) else "N/A")
                    
                    with col3:
                        std_velocity = df['speed_fps'].std()
                        st.metric("📏 Std Deviation", f"{std_velocity:.1f} fps" if not pd.isna(std_velocity) else "N/A")
                    
                    with col4:
                        max_velocity = df['speed_fps'].max()
                        min_velocity = df['speed_fps'].min()
                        velocity_spread = max_velocity - min_velocity if not pd.isna(max_velocity) and not pd.isna(min_velocity) else None
                        st.metric("📐 Velocity Spread", f"{velocity_spread:.1f} fps" if velocity_spread is not None else "N/A")
                    
                    # Display measurement data table
                    st.subheader("📋 Measurement Data")
                    
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
