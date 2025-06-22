
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from supabase import create_client
import requests
from urllib.parse import urlencode

# Auth0 settings
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
CLIENT_ID = st.secrets["auth0"]["client_id"]
CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
REDIRECT_URI = "https://<your-app>.streamlit.app"
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
query_params = st.experimental_get_query_params()
if "code" in query_params:
    code = query_params["code"][0]
    user_info = get_user_info(code)
    st.session_state["user"] = user_info
    st.experimental_set_query_params()

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

        session_id = str(uuid.uuid4())
        supabase.table("sessions").insert({
            "id": session_id,
            "user_email": user["email"],
            "sheet_name": sheet,
            "bullet_type": bullet_type,
            "bullet_grain": bullet_grain,
            "uploaded_at": datetime.utcnow().isoformat(),
            "file_path": file_name
        }).execute()

        for _, row in data.iterrows():
            supabase.table("measurements").insert({
                "session_id": session_id,
                "shot_number": int(row["#"]),
                "speed_fps": float(row["Speed (FPS)"]),
                "delta_avg_fps": float(row["Δ AVG (FPS)"]),
                "ke_ft_lb": float(row["KE (FT-LB)"]),
                "power_factor": float(row["Power Factor (kgr⋅ft/s)"]),
                "time_local": row["Time"],
                "clean_bore": bool(row.get("Clean Bore")) if "Clean Bore" in row else None,
                "cold_bore": bool(row.get("Cold Bore")) if "Cold Bore" in row else None,
                "shot_notes": row.get("Shot Notes")
            }).execute()

    st.success("Upload complete.")
