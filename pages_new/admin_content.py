import os
import sys
import streamlit as st

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.users_tab import render_users_tab
from supabase import create_client

def render_admin_content():
    """Render the admin page content."""
    
    # Get user from session state (should be set by main app)
    if "user" not in st.session_state:
        st.error("User not authenticated")
        return
    
    user = st.session_state.user
    
    # Check if user has admin role
    user_email = user.get("email")
    if not user_email:
        st.error("❌ Unable to verify user identity.")
        return

    # Supabase setup
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return

    # Check admin role from users table
    try:
        user_response = (
            supabase.table("users")
            .select("roles")
            .eq("email", user_email)
            .execute()
        )
        
        is_admin = False
        if user_response.data:
            user_roles = user_response.data[0].get("roles", [])
            is_admin = "admin" in user_roles if user_roles else False
        
        # Fallback check for specific admin email
        if not is_admin and user_email == "johnduffie91@gmail.com":
            is_admin = True
            
    except Exception as e:
        st.error(f"Error checking admin privileges: {str(e)}")
        return

    if not is_admin:
        st.error("❌ Access Denied")
        st.warning("🔒 This page requires administrator privileges.")
        st.info("Contact an administrator if you believe you should have access to this page.")
        return

    # Display title
    st.title("👑 Administration Panel")
    
    # Create tabs for different admin functions
    tab1 = st.tabs(["Users"])[0]

    with tab1:
        render_users_tab(user, supabase)
