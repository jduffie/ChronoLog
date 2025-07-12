import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from supabase import create_client
from dope.create_session_tab import render_create_session_tab
from dope.sessions_tab import render_sessions_tab
from dope.view_session_tab import render_view_session_tab

def main():
    """Main function for the Sessions page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(
        page_title="DOPE",
        page_icon="📊",
        layout="wide"
    )
    
    # Handle authentication
    user = handle_auth()
    if not user:
        return
        
    # Display user info in sidebar
    st.sidebar.success(f"Logged in as {user['name']}")
    
    # Supabase setup
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return
    
    # Display title
    st.title("Data on Prior Engagements")
    
    # Create tabs for Create, View, and Analytics
    tab1, tab2, tab3 = st.tabs(["Create", "View", "Analytics"])
    
    with tab1:
        # Clear DOPE model state when Create tab is accessed
        if "dope_tab_create_visited" not in st.session_state:
            st.session_state.dope_tab_create_visited = True
            
            # Clear DOPE model data
            if "dope_model" in st.session_state:
                for tab_name in list(st.session_state.dope_model.get_all_tabs()):
                    st.session_state.dope_model.clear_tab_data(tab_name)
            
            # Reset other tab visit flags
            st.session_state.pop("dope_tab_sessions_visited", None)
            st.session_state.pop("dope_tab_view_visited", None)
            
            # Clear any Create tab related session state
            keys_to_clear = []
            for key in st.session_state.keys():
                if key.startswith(('edit_range_', 'edit_weather_', 'edit_rifle_', 'edit_ammo_', 'dope_measurements_table_')):
                    keys_to_clear.append(key)
            
            for key in keys_to_clear:
                del st.session_state[key]
        
        render_create_session_tab(user, supabase)
    
    with tab2:
        # Clear DOPE model state when View tab is accessed
        if "dope_tab_view_visited" not in st.session_state:
            st.session_state.dope_tab_view_visited = True
            if "dope_model" in st.session_state:
                for tab_name in list(st.session_state.dope_model.get_all_tabs()):
                    st.session_state.dope_model.clear_tab_data(tab_name)
            # Reset other tab visit flags
            st.session_state.pop("dope_tab_create_visited", None)
            st.session_state.pop("dope_tab_sessions_visited", None)
        
        render_view_session_tab(user, supabase)
    
    with tab3:
        # Clear DOPE model state when Analytics tab is accessed
        if "dope_tab_sessions_visited" not in st.session_state:
            st.session_state.dope_tab_sessions_visited = True
            if "dope_model" in st.session_state:
                for tab_name in list(st.session_state.dope_model.get_all_tabs()):
                    st.session_state.dope_model.clear_tab_data(tab_name)
            # Reset other tab visit flags
            st.session_state.pop("dope_tab_create_visited", None)
            st.session_state.pop("dope_tab_view_visited", None)
        
        render_sessions_tab(user, supabase)

if __name__ == "__main__":
    main()