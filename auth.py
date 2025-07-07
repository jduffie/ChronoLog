import streamlit as st
import requests
from urllib.parse import urlencode
from users import handle_user_profile

# Auth0 settings
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
CLIENT_ID = st.secrets["auth0"]["client_id"]
CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
def get_redirect_uri():
    """Get the appropriate redirect URI based on the current application."""
    # Check query params for app identifier
    query_params = st.query_params
    
    # Determine if running locally or in production
    try:
        # In production, use the secrets URIs
        if "app" in query_params and query_params["app"] == "mapping":
            # For Range_Library.py
            return st.secrets["auth0"]["mapping_redirect_uri"]
        else:
            # For main ChronoLog.py (also handles "chronolog" app identifier)
            return st.secrets["auth0"]["redirect_uri"]
    except KeyError:
        # In local development, use localhost with appropriate ports
        if "app" in query_params and query_params["app"] == "mapping":
            # For Range_Library.py locally - port 8502
            return "http://localhost:8502"
        else:
            # For main ChronoLog.py locally - port 8501
            return "http://localhost:8501"

def get_app_name():
    """Get the current application name."""
    query_params = st.query_params
    if "app" in query_params and query_params["app"] == "mapping":
        return "ChronoLog Mapping Tool"
    else:
        return "ChronoLog"

AUTH0_BASE_URL = f"https://{AUTH0_DOMAIN}"

def show_login_button():
    redirect_uri = get_redirect_uri()
    app_name = get_app_name()
    
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "openid profile email",
        "audience": f"{AUTH0_BASE_URL}/userinfo"
    })
    login_url = f"{AUTH0_BASE_URL}/authorize?{query}"
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"### Welcome to {app_name}")
        st.markdown("Please sign in to continue")
        st.markdown("")
        
        # Google login button with styling
        google_button_html = f"""
        <div style="display: flex; justify-content: center; margin: 20px 0;">
            <a href="{login_url}" style="text-decoration: none;">
                <div style="
                    display: flex;
                    align-items: center;
                    background-color: #fff;
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                    color: #3c4043;
                    cursor: pointer;
                    font-family: 'Roboto', arial, sans-serif;
                    font-size: 14px;
                    height: 40px;
                    padding: 0 12px;
                    transition: background-color 0.218s, border-color 0.218s, box-shadow 0.218s;
                    box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.30), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
                ">
                    <svg width="18" height="18" viewBox="0 0 24 24" style="margin-right: 8px;">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Sign in with Google
                </div>
            </a>
        </div>
        """
        
        st.markdown(google_button_html, unsafe_allow_html=True)

def get_user_info(code):
    redirect_uri = get_redirect_uri()
    token_url = f"{AUTH0_BASE_URL}/oauth/token"
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri
    }
    token_resp = requests.post(token_url, json=token_payload).json()
    access_token = token_resp.get("access_token")
    userinfo_url = f"{AUTH0_BASE_URL}/userinfo"
    userinfo_resp = requests.get(
        userinfo_url, headers={"Authorization": f"Bearer {access_token}"}
    )
    return userinfo_resp.json()

def handle_auth():
    """Handle authentication flow and return user profile or None"""
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
    
    # Handle user profile setup/management
    user_profile = handle_user_profile(user)
    
    # Return user profile (sidebar display is handled in users module)
    return user_profile