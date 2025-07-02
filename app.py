import streamlit as st
from supabase import create_client
from auth import handle_auth
from upload_tab import render_upload_tab
from sessions_tab import render_sessions_tab
from view_session_tab import render_view_session_tab
from locations_tab import render_locations_tab
from files_tab import render_files_tab

# Set wide layout for more space - must be first Streamlit command
st.set_page_config(layout="wide")

# Handle authentication
user = handle_auth()
if not user:
    st.stop()

# Supabase setup
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
bucket = st.secrets["supabase"]["bucket"]
supabase = create_client(url, key)

# Main app tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Upload Files", "Sessions", "View Session", "Locations", "My Files"])

with tab1:
    render_upload_tab(user, supabase, bucket)

with tab2:
    render_sessions_tab(user, supabase)

with tab3:
    render_view_session_tab(user, supabase)

with tab4:
    render_locations_tab(user, supabase)

with tab5:
    render_files_tab(user, supabase, bucket)