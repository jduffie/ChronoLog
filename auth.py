import streamlit as st
import requests
from urllib.parse import urlencode

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

def handle_auth():
    """Handle authentication flow and return user or None"""
    # Auth check
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        user_info = get_user_info(code)
        st.session_state["user"] = user_info
        st.query_params.clear()

    if "user" not in st.session_state:
        show_login_button()
        return None
    
    user = st.session_state["user"]
    st.sidebar.success(f"Logged in as {user['name']}")
    return user