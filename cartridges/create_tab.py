import pandas as pd
import streamlit as st


def render_create_cartridge_tab(user, supabase):
    """Render the Create Cartridge tab"""
    st.header("➕ Create New Cartridge Batch")
    
    # Source selection dropdown
    st.subheader("📦 Select Cartridge Source")
    source = st.selectbox(
        "Choose cartridge source:",
        options=["", "factory", "custom"],
        format_func=lambda x: "Select source..." if x == "" else x.title(),
        help="Select whether you want to create a batch from factory cartridges or custom loads"
    )
    
    if source == "custom":
        st.info("🚧 Custom cartridge functionality will be implemented later.")
        return
    
    elif source == "factory":
        st.subheader("🏭 Select Factory Cartridge Specification")
        
        # Get factory cartridge specs with bullet details (globally available)
        try:
            response = (
                supabase.table("factory_cartridge_specs")
                .select("""
                    *,
                    bullets!inner(
                        manufacturer,
                        model,
                        weight_grains,
                        bore_diameter_land_mm
                    )
                """)
                .execute()
            )
            
            if not response.data:
                st.warning("⚠️ No factory cartridge specifications found. Please contact an administrator to add factory cartridge specifications.")
                return
            
            # Process the data to flatten the nested bullet information
            processed_data = []
            for item in response.data:
                bullet_info = item["bullets"]
                processed_item = {
                    "id": item["id"],
                    "make": item["make"],
                    "model": item["model"],
                    "cartridge_type": item.get("cartridge_type", "N/A"),
                    "bullet_manufacturer": bullet_info["manufacturer"],
                    "bullet_model": bullet_info["model"],
                    "bullet_weight_grains": bullet_info["weight_grains"],
                    "bore_diameter_land_mm": bullet_info["bore_diameter_land_mm"],
                }
                processed_data.append(processed_item)
            
            # Convert to DataFrame for filtering
            df = pd.DataFrame(processed_data)
            
            # Add filters
            st.markdown("**🔍 Filter Options**")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                manufacturers = ["All"] + sorted(df["make"].unique().tolist())
                selected_manufacturer = st.selectbox("Manufacturer:", manufacturers)
            
            with col2:
                bullet_makes = ["All"] + sorted(df["bullet_manufacturer"].unique().tolist())
                selected_bullet_make = st.selectbox("Bullet Make:", bullet_makes)
            
            with col3:
                bullet_models = ["All"] + sorted(df["bullet_model"].unique().tolist())
                selected_bullet_model = st.selectbox("Bullet Model:", bullet_models)
            
            with col4:
                bore_diameters = ["All"] + sorted(df["bore_diameter_land_mm"].unique().tolist())
                selected_bore_diameter = st.selectbox("Bore Diameter:", bore_diameters)
            
            with col5:
                bullet_weights = ["All"] + sorted(df["bullet_weight_grains"].unique().tolist())
                selected_bullet_weight = st.selectbox("Bullet Weight:", bullet_weights)
            
            # Apply filters
            filtered_df = df.copy()
            if selected_manufacturer != "All":
                filtered_df = filtered_df[filtered_df["make"] == selected_manufacturer]
            if selected_bullet_make != "All":
                filtered_df = filtered_df[filtered_df["bullet_manufacturer"] == selected_bullet_make]
            if selected_bullet_model != "All":
                filtered_df = filtered_df[filtered_df["bullet_model"] == selected_bullet_model]
            if selected_bore_diameter != "All":
                filtered_df = filtered_df[filtered_df["bore_diameter_land_mm"] == selected_bore_diameter]
            if selected_bullet_weight != "All":
                filtered_df = filtered_df[filtered_df["bullet_weight_grains"] == selected_bullet_weight]
            
            if len(filtered_df) == 0:
                st.warning("No factory cartridges match the selected filters.")
                return
            
            # Display the filtered table for selection
            st.markdown(f"**📋 Available Factory Cartridges ({len(filtered_df)} found)**")
            
            # Prepare display DataFrame
            display_df = filtered_df.copy()
            display_df = display_df[[
                "make", "model", "cartridge_type", "bullet_manufacturer", 
                "bullet_model", "bullet_weight_grains", "bore_diameter_land_mm"
            ]].rename(columns={
                "make": "Manufacturer",
                "model": "Model", 
                "cartridge_type": "Cartridge Type",
                "bullet_manufacturer": "Bullet Make",
                "bullet_model": "Bullet Model",
                "bullet_weight_grains": "Weight (gr)",
                "bore_diameter_land_mm": "Bore Dia (mm)"
            })
            
            # Add selection column using session state
            if "selected_cartridge_id" not in st.session_state:
                st.session_state.selected_cartridge_id = None
            
            # Display table with selection
            selected_rows = st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Get selected cartridge
            selected_cartridge = None
            if selected_rows["selection"]["rows"]:
                selected_row_idx = selected_rows["selection"]["rows"][0]
                selected_cartridge = filtered_df.iloc[selected_row_idx]
                st.session_state.selected_cartridge_id = selected_cartridge["id"]
                
                # Show selected cartridge details
                st.success(f"✅ Selected: {selected_cartridge['make']} {selected_cartridge['model']} - {selected_cartridge['bullet_manufacturer']} {selected_cartridge['bullet_model']} {selected_cartridge['bullet_weight_grains']}gr")
            
            # Batch number input and save
            if st.session_state.selected_cartridge_id:
                st.markdown("---")
                st.subheader("📝 Batch Information")
                
                with st.form("create_cartridge_batch_form"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        batch_number = st.text_input(
                            "Batch Number *",
                            placeholder="e.g., BATCH-001, LOT-2024-001",
                            help="Enter a unique identifier for this batch of cartridges"
                        )
                    
                    with col2:
                        st.write("")  # Spacer
                        st.write("")  # Spacer
                        submitted = st.form_submit_button("💾 Save Cartridge Batch", type="primary")
                    
                    notes = st.text_area(
                        "Notes (optional)",
                        placeholder="Additional notes about this batch...",
                        help="Optional notes about this cartridge batch"
                    )
                    
                    if submitted:
                        if not batch_number or not batch_number.strip():
                            st.error("❌ Please enter a batch number.")
                        else:
                            batch_number = batch_number.strip()
                            
                            try:
                                # Create cartridge batch entry
                                cartridge_data = {
                                    "user_id": user["id"],
                                    "source": "factory",
                                    "batch_number": batch_number,
                                    "factory_spec_id": st.session_state.selected_cartridge_id,
                                    "notes": notes.strip() if notes.strip() else None
                                }
                                
                                # Insert into database
                                response = supabase.table("cartridges").insert(cartridge_data).execute()
                                
                                if response.data:
                                    # Get the created cartridge info for display
                                    created_cartridge = response.data[0]
                                    selected_spec = filtered_df[filtered_df["id"] == st.session_state.selected_cartridge_id].iloc[0]
                                    
                                    st.success(f"✅ Cartridge batch created successfully!")
                                    st.info(f"📦 **Batch:** {batch_number}")
                                    st.info(f"🏭 **Cartridge:** {selected_spec['make']} {selected_spec['model']}")
                                    st.info(f"🎯 **Bullet:** {selected_spec['bullet_manufacturer']} {selected_spec['bullet_model']} {selected_spec['bullet_weight_grains']}gr")
                                    
                                    # Clear selection and rerun
                                    st.session_state.selected_cartridge_id = None
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to create cartridge batch. Please try again.")
                                    
                            except Exception as e:
                                if "duplicate key value violates unique constraint" in str(e):
                                    st.error(f"❌ Batch number '{batch_number}' already exists. Please use a different batch number.")
                                else:
                                    st.error(f"❌ Error creating cartridge batch: {str(e)}")
            
        except Exception as e:
            st.error(f"❌ Error loading factory cartridge specifications: {str(e)}")
    
    else:
        st.info("👆 Please select a cartridge source to begin.")