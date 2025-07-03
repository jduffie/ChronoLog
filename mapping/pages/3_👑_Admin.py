import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mapping.mapping_model import MappingModel
from mapping.mapping_view import MappingView
from auth import handle_auth
from supabase import create_client

# Set page configuration
st.set_page_config(
    page_title="Admin - ChronoLog Mapping",
    page_icon="👑",
    layout="wide"
)

def main():
    """Main function for the Admin page."""
    # Set app identifier for auth system
    if "app" not in st.query_params:
        st.query_params["app"] = "mapping"
        
    # Handle authentication
    user = handle_auth()
    if not user:
        return
    
    # Check if user is admin
    if user["email"] != "johnduffie91@gmail.com":
        st.error("🚫 Access Denied: This page is restricted to administrators only.")
        return
        
    # Display user info in sidebar
    st.sidebar.success(f"Logged in as Admin: {user['name']}")
    
    # Initialize model and view
    model = MappingModel()
    view = MappingView()
    
    # Database connection
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return
    
    # Display title
    st.title("Range Submissions Admin Panel")
    st.subheader("Review and approve range submissions")
    
    # Fetch all pending submissions
    try:
        pending_submissions = model.get_all_pending_submissions(supabase)
        
        if not pending_submissions:
            st.info("📋 No pending submissions to review.")
            return
            
        st.markdown(f"### Pending Submissions ({len(pending_submissions)})")
        
        # Display each submission for review
        for i, submission in enumerate(pending_submissions):
            with st.expander(f"📍 {submission.get('range_name', 'Unnamed Range')} - {submission.get('user_email', 'Unknown User')}", expanded=False):
                
                # Display submission details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Range Details:**")
                    st.write(f"**Name:** {submission.get('range_name', 'N/A')}")
                    st.write(f"**Description:** {submission.get('range_description', 'N/A')}")
                    st.write(f"**Submitted by:** {submission.get('user_email', 'N/A')}")
                    st.write(f"**Submitted:** {submission.get('submitted_at', 'N/A')}")
                    
                    st.markdown("**Measurements:**")
                    st.write(f"**Distance:** {submission.get('distance_m', 0):.1f} m")
                    st.write(f"**Azimuth:** {submission.get('azimuth_deg', 0):.1f}°")
                    st.write(f"**Elevation:** {submission.get('elevation_angle_deg', 0):.2f}°")
                    st.write(f"**Location:** {submission.get('display_name', 'N/A')}")
                
                with col2:
                    st.markdown("**Coordinates:**")
                    st.write(f"**Start (Firing):** {submission.get('start_lat', 0):.6f}, {submission.get('start_lon', 0):.6f}")
                    st.write(f"**Start Altitude:** {submission.get('start_altitude_m', 0):.1f} m")
                    st.write(f"**End (Target):** {submission.get('end_lat', 0):.6f}, {submission.get('end_lon', 0):.6f}")
                    st.write(f"**End Altitude:** {submission.get('end_altitude_m', 0):.1f} m")
                
                # Display map for this submission
                st.markdown("**Range Visualization:**")
                single_range_map = view.display_ranges_map([submission], [0])
                st_folium = __import__('streamlit_folium', fromlist=['st_folium']).st_folium
                st_folium(single_range_map, use_container_width=True, height=400)
                
                # Admin actions
                st.markdown("---")
                st.markdown("**Admin Actions:**")
                
                # Review reason input
                review_reason = st.text_area(
                    "Review Comments (required for acceptance/denial):",
                    key=f"reason_{submission['id']}",
                    placeholder="Enter reason for acceptance or denial...",
                    height=80
                )
                
                # Action buttons
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    if st.button(f"✅ Accept", key=f"accept_{submission['id']}", type="primary"):
                        if not review_reason.strip():
                            st.error("❌ Please provide a reason for acceptance.")
                        else:
                            success = model.approve_submission(submission['id'], review_reason.strip(), supabase)
                            if success:
                                st.success("✅ Range approved and added to public ranges!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to approve range. Please try again.")
                
                with action_col2:
                    if st.button(f"❌ Deny", key=f"deny_{submission['id']}", type="secondary"):
                        if not review_reason.strip():
                            st.error("❌ Please provide a reason for denial.")
                        else:
                            success = model.deny_submission(submission['id'], review_reason.strip(), supabase)
                            if success:
                                st.success("✅ Range denied with feedback sent to user.")
                                st.rerun()
                            else:
                                st.error("❌ Failed to deny range. Please try again.")
                
                with action_col3:
                    if st.button(f"🔄 Reset Status", key=f"reset_{submission['id']}"):
                        success = model.reset_submission_status(submission['id'], supabase)
                        if success:
                            st.success("✅ Status reset to 'Under Review'.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to reset status. Please try again.")
    
    except Exception as e:
        st.error(f"Error loading submissions: {str(e)}")

if __name__ == "__main__":
    main()