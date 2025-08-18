import os
import sys

import streamlit as st
import navigation

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from supabase import create_client


def main():
    """Main function for the DOPE Overview page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="DOPE Overview", page_icon="📊", layout="wide")

    # Load custom navigation
    navigation.load()

    # Handle authentication
    user = handle_auth()
    if not user:
        return

    # Supabase setup
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return

    # Display title
    st.title("📊 DOPE Overview")
    
    # Overview content
    st.markdown("""
    ## Data on Prior Engagements Overview
    
    Welcome to the DOPE (Data on Prior Engagements) system. This comprehensive platform allows you to:
    
    ### 📈 **Create DOPE Sessions**
    - Combine chronograph data with environmental conditions
    - Merge range data with equipment specifications
    - Generate precise ballistic calculations
    
    ### 📋 **View DOPE Sessions**
    - Browse your existing DOPE sessions
    - Review ballistic data and calculations
    - Export data for field use
    
    ### 📊 **Analytics & Insights**
    - Analyze performance trends across sessions
    - Compare different ammunition and rifle combinations
    - Generate statistical reports
    
    ### 🎯 **Quick Actions**
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.page_link("pages/2b_📊_DOPE_Create.py", label="🆕 Create New DOPE Session")
    
    with col2:
        st.page_link("pages/2c_📊_DOPE_View.py", label="📋 View DOPE Sessions")
    
    with col3:
        st.page_link("pages/2d_📊_DOPE_Analytics.py", label="📊 View Analytics")

    # Recent activity placeholder
    st.markdown("---")
    st.subheader("📈 Recent Activity")
    st.info("Recent DOPE sessions and analytics will be displayed here.")


if __name__ == "__main__":
    main()
