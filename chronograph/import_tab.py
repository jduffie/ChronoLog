import streamlit as st

from .service import ChronographService


def render_chronograph_import_tab(user, supabase, bucket):
    """Render chronograph import wizard"""
    st.header("Chronograph Data Import Wizard")
    
    # Initialize chronograph service
    chrono_service = ChronographService(supabase)
    
    # Initialize wizard state only if it doesn't exist
    if "chrono_wizard_state" not in st.session_state:
        st.session_state.chrono_wizard_state = {
            "step": "source_selection",
            "selected_source_id": None
        }
    
    wizard_state = st.session_state.chrono_wizard_state
    
    # Step 1: Source Selection
    if wizard_state["step"] == "source_selection":
        st.subheader("Step 1: Choose Chronograph Source")
        st.write("Select an existing chronograph source or create a new one.")
        
        # Get existing sources
        sources = chrono_service.get_sources_for_user(user["id"])
        
        # Source selection options
        source_choice = st.radio(
            "Choose an option:",
            options=["Select existing source", "Create new source"],
            index=0
        )
        
        if source_choice == "Select existing source":
            if not sources:
                st.warning("No existing chronograph sources found. Please create a new source.")
            else:
                # Show existing sources
                source_options = [f"{s.name} - {s.device_display()}" for s in sources]
                selected_index = st.selectbox(
                    "Select chronograph source:",
                    options=range(len(source_options)),
                    format_func=lambda x: source_options[x]
                )
                
                if st.button("Continue with Selected Source", type="primary"):
                    wizard_state["selected_source_id"] = sources[selected_index].id
                    wizard_state["step"] = "file_upload"
                    st.rerun()
        
        else:  # Create new source
            st.write("#### Create New Chronograph Source")
            
            with st.form("new_chrono_source_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    source_type = st.selectbox(
                        "Source Type*",
                        options=["Chronograph"],
                        help="Select the type of chronograph source"
                    )
                
                with col2:
                    source_make = st.selectbox(
                        "Make*",
                        options=["Garmin"],
                        help="Select the manufacturer"
                    )
                
                name = st.text_input(
                    "Source Name*",
                    placeholder="e.g., Range Garmin Xero, Competition Chronograph",
                    help="Give your chronograph source a unique name"
                )
                
                if st.form_submit_button("Create Source and Continue", type="primary"):
                    if not name.strip():
                        st.error("Source name is required!")
                    else:
                        try:
                            # Check if name already exists
                            existing = chrono_service.get_source_by_name(user["id"], name.strip())
                            if existing:
                                st.error(f"A chronograph source named '{name}' already exists!")
                            else:
                                source_data = {
                                    "user_id": user["id"],
                                    "name": name.strip(),
                                    "make": source_make,
                                    "source_type": source_type.lower(),
                                }
                                
                                source_id = chrono_service.create_source(source_data)
                                wizard_state["selected_source_id"] = source_id
                                wizard_state["step"] = "file_upload"
                                st.success(f"Chronograph source '{name}' created successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error creating chronograph source: {e}")
    
    # Step 2: File Upload
    elif wizard_state["step"] == "file_upload":
        # Get the selected source
        selected_source = chrono_service.get_source_by_id(wizard_state["selected_source_id"], user["id"])
        
        if not selected_source:
            st.error("Selected source not found. Returning to source selection.")
            wizard_state["step"] = "source_selection"
            st.rerun()
            return
        
        st.subheader("Step 2: Upload Data File")
        st.success(f"Selected Source: {selected_source.name} - {selected_source.device_display()}")
        
        # Back button
        if st.button("← Back to Source Selection"):
            wizard_state["step"] = "source_selection"
            wizard_state["selected_source_id"] = None
            st.rerun()
        
        st.write("---")
        
        # Show appropriate upload based on source type
        if selected_source.make and selected_source.make.lower() == "garmin":
            st.write("### Upload Garmin Xero Excel Files")
            render_garmin_file_upload(user, supabase, bucket, chrono_service, selected_source.id)
        else:
            st.info("Upload options for this chronograph type are not yet available.")


def render_garmin_file_upload(user, supabase, bucket, chrono_service, selected_source_id):
    """Render Garmin file upload section"""
    from .garmin_ui import GarminImportUI

    # Get selected source
    selected_source = chrono_service.get_source_by_id(selected_source_id, user["id"])
    
    if not selected_source:
        st.error("Selected chronograph source not found. Please refresh the page.")
        return
    
    # Create Garmin UI and render upload
    garmin_ui = GarminImportUI(supabase)
    garmin_ui.render_file_upload(user, supabase, bucket)
