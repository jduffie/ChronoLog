import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mapping.admin_model import AdminModel
from mapping.admin_view import AdminView
from auth import handle_auth
from supabase import create_client
from typing import Dict, Any, List


class AdminController:
    """Controller for admin range submission review functionality."""
    
    def __init__(self):
        self.model = AdminModel()
        self.view = AdminView()

    def _get_supabase_client(self):
        """Get authenticated Supabase client."""
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)

    def _is_admin(self, user: Dict[str, Any]) -> bool:
        """Check if user has admin privileges."""
        return user.get("email") == "johnduffie91@gmail.com"

    def _handle_submission_action(self, submission: Dict[str, Any], action: str, review_reason: str) -> None:
        """Handle individual submission actions."""
        try:
            supabase = self._get_supabase_client()
            success = False
            
            if action == "approve":
                success = self.model.approve_submission(submission['id'], review_reason.strip(), supabase)
                if success:
                    self.view.display_success_message("✅ Range approved and added to public ranges!")
                    st.rerun()
                else:
                    self.view.display_error_message("❌ Failed to approve range. Please try again.")
                    
            elif action == "deny":
                success = self.model.deny_submission(submission['id'], review_reason.strip(), supabase)
                if success:
                    self.view.display_success_message("✅ Range denied with feedback sent to user.")
                    st.rerun()
                else:
                    self.view.display_error_message("❌ Failed to deny range. Please try again.")
                    
            elif action == "reset":
                success = self.model.reset_submission_status(submission['id'], supabase)
                if success:
                    self.view.display_success_message("✅ Status reset to 'Under Review'.")
                    st.rerun()
                else:
                    self.view.display_error_message("❌ Failed to reset status. Please try again.")
                    
        except Exception as e:
            self.view.display_error_message(f"❌ Error processing action: {str(e)}")

    def _handle_bulk_actions(self, submissions: List[Dict[str, Any]], action: str) -> None:
        """Handle bulk actions on multiple submissions."""
        selected_indices = st.session_state.get("selected_submissions", [])
        
        if not selected_indices:
            self.view.display_warning_message("No submissions selected for bulk action.")
            return

        # Get bulk review reason
        bulk_reason = st.text_area(
            f"Bulk {action.replace('bulk_', '').title()} Reason:",
            key=f"bulk_reason_{action}",
            placeholder="Enter reason for bulk action...",
            height=80
        )

        if not bulk_reason.strip() and action in ["bulk_approve", "bulk_deny"]:
            self.view.display_error_message("Please provide a reason for bulk action.")
            return

        # Confirm bulk action
        if st.button(f"Confirm Bulk {action.replace('bulk_', '').title()}", type="primary"):
            try:
                supabase = self._get_supabase_client()
                success_count = 0
                
                for idx in selected_indices:
                    if idx < len(submissions):
                        submission = submissions[idx]
                        
                        if action == "bulk_approve":
                            if self.model.approve_submission(submission['id'], bulk_reason.strip(), supabase):
                                success_count += 1
                        elif action == "bulk_deny":
                            if self.model.deny_submission(submission['id'], bulk_reason.strip(), supabase):
                                success_count += 1
                        elif action == "bulk_reset":
                            if self.model.reset_submission_status(submission['id'], supabase):
                                success_count += 1

                if success_count > 0:
                    self.view.display_success_message(f"✅ Successfully processed {success_count} submissions!")
                    # Clear selection
                    if "selected_submissions" in st.session_state:
                        del st.session_state["selected_submissions"]
                    st.rerun()
                else:
                    self.view.display_error_message("❌ Failed to process submissions.")
                    
            except Exception as e:
                self.view.display_error_message(f"❌ Error processing bulk action: {str(e)}")

    def run(self) -> None:
        """Main controller method to run the admin page."""
        # Set page configuration
        st.set_page_config(
            page_title="Admin - ChronoLog Mapping",
            page_icon="👑",
            layout="wide"
        )
        
        # Set app identifier for auth system
        if "app" not in st.query_params:
            st.query_params["app"] = "mapping"
            
        # Handle authentication
        user = handle_auth()
        if not user:
            return

        # Check admin privileges
        if not self._is_admin(user):
            self.view.display_access_denied()
            return

        # Display title
        self.view.display_title()

        try:
            supabase = self._get_supabase_client()
            
            # Create tabs for different admin views
            tab1, tab2, tab3 = st.tabs(["Pending Review", "All Submissions", "Statistics"])
            
            with tab1:
                # Fetch pending submissions
                pending_submissions = self.model.get_all_pending_submissions(supabase)
                
                if not pending_submissions:
                    self.view.display_no_submissions_message()
                else:
                    self.view.display_submission_count(len(pending_submissions))
                    
                    # Display each submission for review
                    for submission in pending_submissions:
                        review_reason = self.view.display_submission_details(submission, 0)
                        action = self.view.display_submission_actions(submission, review_reason)
                        
                        if action:
                            self._handle_submission_action(submission, action, review_reason)
            
            with tab2:
                # Fetch all submissions
                all_submissions = self.model.get_all_submissions(supabase)
                
                if all_submissions:
                    # Display submissions table with filtering
                    table_result = self.view.display_submissions_table(all_submissions)
                    
                    # Display bulk actions
                    bulk_action = self.view.display_bulk_actions(table_result.get("filtered_submissions", []))
                    
                    if bulk_action:
                        self._handle_bulk_actions(table_result.get("filtered_submissions", []), bulk_action)
                else:
                    self.view.display_info_message("No submissions found in the system.")
            
            with tab3:
                # Display statistics
                all_submissions = self.model.get_all_submissions(supabase)
                self.view.display_statistics(all_submissions)
                
                # Additional statistics
                if all_submissions:
                    st.markdown("### Submission Details")
                    
                    # Group by status
                    status_groups = {}
                    for submission in all_submissions:
                        status = submission.get('status', 'Unknown')
                        if status not in status_groups:
                            status_groups[status] = []
                        status_groups[status].append(submission)
                    
                    for status, submissions in status_groups.items():
                        with st.expander(f"{status} ({len(submissions)} submissions)"):
                            for submission in submissions[:10]:  # Show first 10
                                st.write(f"**{submission.get('range_name', 'Unnamed')}** by {submission.get('user_email', 'Unknown')}")
                            if len(submissions) > 10:
                                st.write(f"... and {len(submissions) - 10} more")

        except Exception as e:
            self.view.display_error_message(f"Error loading admin data: {str(e)}")

    def get_pending_submissions(self):
        """Get all pending submissions."""
        try:
            supabase = self._get_supabase_client()
            return self.model.get_all_pending_submissions(supabase)
        except Exception as e:
            self.view.display_error_message(f"Error fetching pending submissions: {str(e)}")
            return []

    def approve_submission(self, submission_id: str, reason: str) -> bool:
        """Approve a specific submission."""
        try:
            supabase = self._get_supabase_client()
            return self.model.approve_submission(submission_id, reason, supabase)
        except Exception as e:
            self.view.display_error_message(f"Error approving submission: {str(e)}")
            return False

    def deny_submission(self, submission_id: str, reason: str) -> bool:
        """Deny a specific submission."""
        try:
            supabase = self._get_supabase_client()
            return self.model.deny_submission(submission_id, reason, supabase)
        except Exception as e:
            self.view.display_error_message(f"Error denying submission: {str(e)}")
            return False