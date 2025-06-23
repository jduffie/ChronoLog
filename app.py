
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
tab1, tab2 = st.tabs(["Upload Files", "My Files"])

with tab2:
    st.header("📁 My Uploaded Files")
    
    try:
        # Get user's sessions from database
        sessions_response = supabase.table("sessions").select("*").eq("user_email", user["email"]).order("uploaded_at", desc=True).execute()
        sessions = sessions_response.data
        
        if sessions:
            st.write(f"You have uploaded {len(sessions)} file(s):")
            
            for session in sessions:
                with st.expander(f"📄 {session['file_path'].split('/')[-1]} - {session['bullet_type']} ({session['bullet_grain']}gr)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Uploaded:** {pd.to_datetime(session['uploaded_at']).strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Sheet:** {session['sheet_name']}")
                        st.write(f"**Bullet Type:** {session['bullet_type']}")
                        st.write(f"**Bullet Weight:** {session['bullet_grain']}gr")
                    
                    with col2:
                        # Get measurement count for this session
                        measurements_response = supabase.table("measurements").select("*", count="exact").eq("session_id", session['id']).execute()
                        measurement_count = measurements_response.count
                        st.write(f"**Shots Recorded:** {measurement_count}")
                        
                        # Download button for original file
                        if st.button("📥 Download Original File", key=f"download_{session['id']}"):
                            try:
                                file_data = supabase.storage.from_(bucket).download(session['file_path'])
                                st.download_button(
                                    label="💾 Save File",
                                    data=file_data,
                                    file_name=session['file_path'].split('/')[-1],
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"save_{session['id']}"
                                )
                            except Exception as e:
                                st.error(f"Error downloading file: {e}")
                        
                        # Delete button with confirmation
                        if st.button("🗑️ Delete File", key=f"delete_{session['id']}", type="secondary"):
                            st.session_state[f"confirm_delete_{session['id']}"] = True
                        
                        # Show confirmation dialog
                        if st.session_state.get(f"confirm_delete_{session['id']}", False):
                            st.warning("⚠️ Are you sure you want to delete this file? This action cannot be undone!")
                            col_yes, col_no = st.columns(2)
                            
                            with col_yes:
                                if st.button("✅ Yes, Delete", key=f"confirm_yes_{session['id']}", type="primary"):
                                    try:
                                        # Delete measurements first (foreign key constraint)
                                        supabase.table("measurements").delete().eq("session_id", session['id']).execute()
                                        
                                        # Delete session record
                                        supabase.table("sessions").delete().eq("id", session['id']).execute()
                                        
                                        # Delete file from storage
                                        supabase.storage.from_(bucket).remove([session['file_path']])
                                        
                                        # Clear confirmation state and rerun
                                        del st.session_state[f"confirm_delete_{session['id']}"]
                                        st.success("File deleted successfully!")
                                        st.rerun()
                                        
                                    except Exception as e:
                                        st.error(f"Error deleting file: {e}")
                            
                            with col_no:
                                if st.button("❌ Cancel", key=f"confirm_no_{session['id']}"):
                                    del st.session_state[f"confirm_delete_{session['id']}"]
                                    st.rerun()
                    
                    # Show measurement data
                    if st.checkbox(f"Show measurement data", key=f"show_data_{session['id']}"):
                        measurements_response = supabase.table("measurements").select("*").eq("session_id", session['id']).order("shot_number").execute()
                        measurements = measurements_response.data
                        
                        if measurements:
                            df = pd.DataFrame(measurements)
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
            st.info("No files uploaded yet. Use the 'Upload Files' tab to get started!")
            
    except Exception as e:
        st.error(f"Error loading your files: {e}")

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
