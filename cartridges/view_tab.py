from datetime import datetime

import pandas as pd
import streamlit as st


def render_view_cartridges_tab(user, supabase):
    
    # Clear any existing cartridges session state when navigating to page
    if 'cartridges' in st.session_state:
        del st.session_state.cartridges

    try:
        # Get cartridges: both user-owned and global ones
        # Query the cartridges table directly with JOIN to bullets
        response = (
            supabase.table("cartridges")
            .select(
                """
                *,
                bullets:bullet_id (
                    id,
                    manufacturer,
                    model,
                    weight_grains,
                    bullet_diameter_groove_mm,
                    bore_diameter_land_mm,
                    bullet_length_mm,
                    ballistic_coefficient_g1,
                    ballistic_coefficient_g7,
                    sectional_density,
                    min_req_twist_rate_in_per_rev,
                    pref_twist_rate_in_per_rev
                )
            """
            )
            .or_(f"owner_id.eq.{user['id']},owner_id.is.null")
            .execute()
        )

        if not response.data:
            st.info(
                "No cartridge entries found. Create factory cartridges or custom cartridges to see them here."
            )
            return

        # Process the response data to flatten the bullet information
        processed_data = []
        for cartridge in response.data:
            # Flatten the nested bullet data
            bullet_info = cartridge.get("bullets", {}) or {}

            # Ensure consistent data types for Arrow compatibility
            processed_record = {
                "id": cartridge.get("id", ""),
                "owner_id": cartridge.get("owner_id", ""),
                "make": cartridge.get("make", ""),
                "model": cartridge.get("model", ""),
                "cartridge_type": cartridge.get("cartridge_type", ""),
                "bullet_id": cartridge.get("bullet_id", ""),
                "data_source_name": cartridge.get("data_source_name", ""),
                "data_source_link": cartridge.get("data_source_link", ""),
                "created_at": cartridge.get("created_at", ""),
                "updated_at": cartridge.get("updated_at", ""),
                "source": "Public" if cartridge.get("owner_id") is None else "User",
                "manufacturer": cartridge.get("make", ""),
                "bullet_manufacturer": bullet_info.get("manufacturer") or "",
                "bullet_model": bullet_info.get("model") or "",
                "bullet_weight_grains": str(bullet_info.get("weight_grains") or ""),
                "bullet_diameter_groove_mm": str(
                    bullet_info.get("bullet_diameter_groove_mm") or ""
                ),
                "bore_diameter_land_mm": str(
                    bullet_info.get("bore_diameter_land_mm") or ""
                ),
                "bullet_length_mm": str(bullet_info.get("bullet_length_mm") or ""),
                "ballistic_coefficient_g1": str(
                    bullet_info.get("ballistic_coefficient_g1") or ""
                ),
                "ballistic_coefficient_g7": str(
                    bullet_info.get("ballistic_coefficient_g7") or ""
                ),
                "sectional_density": str(bullet_info.get("sectional_density") or ""),
                "min_req_twist_rate_in_per_rev": str(
                    bullet_info.get("min_req_twist_rate_in_per_rev") or ""
                ),
                "pref_twist_rate_in_per_rev": str(
                    bullet_info.get("pref_twist_rate_in_per_rev") or ""
                ),
                "bullet_name": f"{bullet_info.get('manufacturer') or ''} {bullet_info.get('model') or ''} {bullet_info.get('weight_grains') or ''}gr".strip()
                or "Unknown",
            }
            processed_data.append(processed_record)

        # Convert to DataFrame for better display
        df = pd.DataFrame(processed_data)

        # Convert all columns to string type to avoid Arrow serialization issues
        df = df.astype(str)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Cartridges", len(df))

        with col2:
            unique_cartridge_types = (
                df["cartridge_type"].nunique() if "cartridge_type" in df.columns else 0
            )
            st.metric("Cartridge Types", unique_cartridge_types)

        with col3:
            unique_manufacturers = (
                df["manufacturer"].dropna().nunique()
                if "manufacturer" in df.columns
                else 0
            )
            st.metric("Manufacturers", unique_manufacturers)

        with col4:
            global_count = (
                len(df[df["source"] == "Public"]) if "source" in df.columns else 0
            )
            user_count = (
                len(df[df["source"] == "User"]) if "source" in df.columns else 0
            )
            st.metric("Public/User", f"{global_count}/{user_count}")

        # Collapsible filters section
        with st.expander("Filter Options", expanded=False):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                sources = (
                    ["All"] + sorted(df["source"].unique().tolist())
                    if "source" in df.columns
                    else ["All"]
                )
                selected_source = st.selectbox("Filter by Source:", sources)

            with col2:
                manufacturers = (
                    ["All"] + sorted(df["manufacturer"].dropna().unique().tolist())
                    if "manufacturer" in df.columns
                    else ["All"]
                )
                selected_manufacturer = st.selectbox(
                    "Filter by Manufacturer:", manufacturers
                )

            with col3:
                cartridge_types = (
                    ["All"] + sorted(df["cartridge_type"].dropna().unique().tolist())
                    if "cartridge_type" in df.columns
                    else ["All"]
                )
                selected_cartridge_type = st.selectbox(
                    "Filter by Cartridge Type:", cartridge_types
                )

            with col4:
                bullet_weights = (
                    ["All"] + sorted(df["bullet_weight_grains"].dropna().unique().tolist())
                    if "bullet_weight_grains" in df.columns
                    else ["All"]
                )
                selected_bullet_weight = st.selectbox(
                    "Filter by Bullet Weight:", bullet_weights
                )


        # Apply filters
        filtered_df = df.copy()
        if selected_source != "All" and "source" in df.columns:
            filtered_df = filtered_df[filtered_df["source"] == selected_source]
        if selected_manufacturer != "All" and "manufacturer" in df.columns:
            filtered_df = filtered_df[
                filtered_df["manufacturer"] == selected_manufacturer
            ]
        if selected_cartridge_type != "All" and "cartridge_type" in df.columns:
            filtered_df = filtered_df[
                filtered_df["cartridge_type"] == selected_cartridge_type
            ]
        if selected_bullet_weight != "All" and "bullet_weight_grains" in df.columns:
            filtered_df = filtered_df[
                filtered_df["bullet_weight_grains"] == selected_bullet_weight
            ]

        # Display filtered results count
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df)} of {len(df)} entries")

        if len(filtered_df) == 0:
            st.warning("No entries match the selected filters.")
            return

        # Prepare display DataFrame
        display_df = filtered_df.copy()

        # Handle nullable fields by filling NaN values
        for col in [
            "manufacturer",
            "model",
            "bullet_manufacturer",
            "bullet_model",
            "bullet_weight_grains",
            "bullet_diameter_groove_mm",
            "bore_diameter_land_mm",
            "bullet_length_mm",
            "ballistic_coefficient_g1",
            "ballistic_coefficient_g7",
            "sectional_density",
            "min_req_twist_rate_in_per_rev",
            "pref_twist_rate_in_per_rev",
        ]:
            if col in display_df.columns:
                display_df[col] = display_df[col].fillna("N/A")

        # Show all available fields from the new view schema
        available_cols = [
            "source",
            "manufacturer",
            "cartridge_type",
            "model",
            "bullet_name",
            "bullet_manufacturer",
            "bullet_model",
            "bullet_weight_grains",
            "bullet_diameter_groove_mm",
            "bore_diameter_land_mm",
            "bullet_length_mm",
            "ballistic_coefficient_g1",
            "ballistic_coefficient_g7",
            "sectional_density",
            "min_req_twist_rate_in_per_rev",
            "pref_twist_rate_in_per_rev",
        ]

        # Only include columns that exist in the DataFrame
        display_cols = [col for col in available_cols if col in display_df.columns]

        display_df = display_df[display_cols].rename(
            columns={
                "source": "Source",
                "manufacturer": "Manufacturer",
                "cartridge_type": "Cartridge Type",
                "model": "Cartridge Model",
                "bullet_name": "Bullet",
                "bullet_manufacturer": "Bullet Make",
                "bullet_model": "Bullet Model",
                "bullet_weight_grains": "Bullet Weight (gr)",
                "bullet_diameter_groove_mm": "Bullet Dia (mm)",
                "bore_diameter_land_mm": "Bore Dia (mm)",
                "bullet_length_mm": "Bullet Length (mm)",
                "ballistic_coefficient_g1": "BC G1",
                "ballistic_coefficient_g7": "BC G7",
                "sectional_density": "Sect. Density",
                "min_req_twist_rate_in_per_rev": "Min Twist",
                "pref_twist_rate_in_per_rev": "Pref Twist",
            }
        )

        # Display the table with enhanced formatting
        column_config = {}
        for col in display_df.columns:
            if col in [
                "Bullet Weight (gr)",
                "Bullet Dia (mm)",
                "Bore Dia (mm)",
                "Bullet Length (mm)",
                "BC G1",
                "BC G7",
                "Sect. Density",
                "Min Twist",
                "Pref Twist",
            ]:
                column_config[col] = st.column_config.TextColumn(col, width="small")
            elif col in [
                "Cartridge Type",
                "Cartridge Model",
                "Bullet",
                "Bullet Make",
                "Bullet Model",
            ]:
                column_config[col] = st.column_config.TextColumn(col, width="medium")
            else:
                column_config[col] = st.column_config.TextColumn(col, width="small")

        # Display the table with enhanced formatting and selection
        selected_cartridge_event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config=column_config,
        )

        # Handle cartridge selection from table click
        selected_cartridge_data = None
        if selected_cartridge_event["selection"]["rows"]:
            selected_row_index = selected_cartridge_event["selection"]["rows"][0]
            # Get the cartridge data from the filtered_df using the display index
            selected_cartridge_data = filtered_df.iloc[selected_row_index]

        # Show read-only details when a cartridge is selected
        if selected_cartridge_data is not None:
            source = selected_cartridge_data.get("source", "N/A")
            manufacturer = selected_cartridge_data.get("manufacturer", "N/A")
            cartridge_type = selected_cartridge_data.get("cartridge_type", "N/A")
            model = selected_cartridge_data.get("model", "N/A")
            bullet_name = selected_cartridge_data.get("bullet_name", "N/A")
            
            st.markdown(f"**Details: {manufacturer} {cartridge_type} {model} - {bullet_name}**")
            
            # Display detailed information in columns
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                st.markdown("**Cartridge Info**")
                st.write(f"**Source:** {source}")
                st.write(f"**Manufacturer:** {manufacturer}")
                st.write(f"**Cartridge Type:** {cartridge_type}")
                st.write(f"**Cartridge Model:** {model}")
                if selected_cartridge_data.get("data_source_name") and selected_cartridge_data.get("data_source_name") != "":
                    st.write(f"**Data Source:** {selected_cartridge_data['data_source_name']}")
                if selected_cartridge_data.get("created_at"):
                    st.write(f"**Created:** {selected_cartridge_data['created_at'][:10]}")

            with col2:
                st.markdown("**Bullet Info**")
                st.write(f"**Description:** {bullet_name}")
                st.write(f"**Bullet Manufacturer:** {selected_cartridge_data.get('bullet_manufacturer', 'N/A')}")
                st.write(f"**Bullet Model:** {selected_cartridge_data.get('bullet_model', 'N/A')}")
                st.write(f"**Weight:** {selected_cartridge_data.get('bullet_weight_grains', 'N/A')} gr")
                st.write(f"**Bullet Diameter:** {selected_cartridge_data.get('bullet_diameter_groove_mm', 'N/A')} mm")
                st.write(f"**Bore Diameter:** {selected_cartridge_data.get('bore_diameter_land_mm', 'N/A')} mm")
                if selected_cartridge_data.get("bullet_length_mm") and selected_cartridge_data.get("bullet_length_mm") != "":
                    st.write(f"**Length:** {selected_cartridge_data['bullet_length_mm']} mm")

            with col3:
                st.markdown("**Ballistic Properties**")
                if selected_cartridge_data.get("ballistic_coefficient_g1") and selected_cartridge_data.get("ballistic_coefficient_g1") != "":
                    st.write(f"**BC G1:** {selected_cartridge_data['ballistic_coefficient_g1']}")
                else:
                    st.write("**BC G1:** N/A")
                if selected_cartridge_data.get("ballistic_coefficient_g7") and selected_cartridge_data.get("ballistic_coefficient_g7") != "":
                    st.write(f"**BC G7:** {selected_cartridge_data['ballistic_coefficient_g7']}")
                else:
                    st.write("**BC G7:** N/A")
                if selected_cartridge_data.get("sectional_density") and selected_cartridge_data.get("sectional_density") != "":
                    st.write(f"**Sectional Density:** {selected_cartridge_data['sectional_density']}")
                else:
                    st.write("**Sectional Density:** N/A")
                if selected_cartridge_data.get("min_req_twist_rate_in_per_rev") and selected_cartridge_data.get("min_req_twist_rate_in_per_rev") != "":
                    st.write(f"**Min Twist Rate:** {selected_cartridge_data['min_req_twist_rate_in_per_rev']} in/rev")
                else:
                    st.write("**Min Twist Rate:** N/A")
                if selected_cartridge_data.get("pref_twist_rate_in_per_rev") and selected_cartridge_data.get("pref_twist_rate_in_per_rev") != "":
                    st.write(f"**Pref Twist Rate:** {selected_cartridge_data['pref_twist_rate_in_per_rev']} in/rev")
                else:
                    st.write("**Pref Twist Rate:** N/A")
            
            with col4:
                st.markdown("**Actions**")
                # Delete button
                if st.button("Delete", type="secondary", use_container_width=True):
                    if 'cartridges' not in st.session_state:
                        st.session_state.cartridges = {}
                    st.session_state.cartridges['deleting_cartridge_id'] = selected_cartridge_data['id']
        
        else:
            st.info("Click on a cartridge in the table above to view details")

        # Handle Delete Confirmation
        if 'cartridges' in st.session_state and 'deleting_cartridge_id' in st.session_state.cartridges:
            # Get the cartridge data for deletion
            cartridge_to_delete = filtered_df[
                filtered_df["id"] == st.session_state.cartridges['deleting_cartridge_id']
            ].iloc[0] if not filtered_df[filtered_df["id"] == st.session_state.cartridges['deleting_cartridge_id']].empty else None
            
            if cartridge_to_delete is not None:
                st.subheader(f"Delete {cartridge_to_delete['make']} {cartridge_to_delete['model']}")
                st.warning("⚠️ This action cannot be undone!")
                st.write(f"Are you sure you want to delete **{cartridge_to_delete['make']} {cartridge_to_delete['model']}** ({cartridge_to_delete['cartridge_type']})?")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Yes, Delete", type="primary", use_container_width=True):
                        try:
                            # Delete the cartridge
                            delete_response = (
                                supabase.table("cartridges")
                                .delete()
                                .eq("id", st.session_state.cartridges['deleting_cartridge_id'])
                                .execute()
                            )

                            if delete_response.data:
                                st.success(f"Deleted: {cartridge_to_delete['make']} {cartridge_to_delete['model']}")
                                del st.session_state.cartridges['deleting_cartridge_id']
                                st.rerun()
                            else:
                                st.error("Failed to delete cartridge.")
                        except Exception as e:
                            st.error(f"Error deleting cartridge: {str(e)}")
                
                with col2:
                    if st.button("Cancel", use_container_width=True):
                        del st.session_state.cartridges['deleting_cartridge_id']
                        st.rerun()
            else:
                del st.session_state.cartridges['deleting_cartridge_id']
                st.rerun()

        # Export option
        st.subheader("Export")
        if st.button("Download as CSV"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"cartridge_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"Error loading cartridge details: {str(e)}")
        st.info(
            "Please check your database connection and ensure the cartridges and bullets tables exist."
        )
