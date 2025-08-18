from datetime import datetime

import pandas as pd
import streamlit as st


def render_view_cartridge_tab(user, supabase):
    """Render the View Factory Cartridges tab"""
    st.header("📋 View Factory Cartridge Entries")

    try:
        # Get all factory cartridge entries (globally available, admin-maintained)
        response = (
            supabase.table("factory_cartridge_specs")
            .select(
                """
                *,
                bullets!inner(
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
                    pref_twist_rate_in_per_rev,
                    data_source_name,
                    data_source_url
                )
                """
            )
            .order("make, model")
            .execute()
        )

        if not response.data:
            st.info(
                "📭 No factory cartridge specifications available in the database. Please contact an administrator to add factory cartridge specifications."
            )
            return

        # Process the data to flatten the nested bullet information
        processed_data = []
        for item in response.data:
            bullet_info = item["bullets"]
            processed_item = {
                "id": item["id"],
                "cartridge_type": item.get("cartridge_type", ""),
                "cartridge_make": item["make"],
                "cartridge_model": item["model"],
                "bullet_id": item["bullet_id"],
                "bullet_manufacturer": bullet_info["manufacturer"],
                "bullet_model": bullet_info["model"],
                "bullet_weight_grains": bullet_info["weight_grains"],
                "bullet_diameter_groove_mm": bullet_info["bullet_diameter_groove_mm"],
                "bore_diameter_land_mm": bullet_info["bore_diameter_land_mm"],
                "bullet_length_mm": bullet_info.get("bullet_length_mm"),
                "ballistic_coefficient_g1": bullet_info.get("ballistic_coefficient_g1"),
                "ballistic_coefficient_g7": bullet_info.get("ballistic_coefficient_g7"),
                "sectional_density": bullet_info.get("sectional_density"),
                "min_req_twist_rate_in_per_rev": bullet_info.get("min_req_twist_rate_in_per_rev"),
                "pref_twist_rate_in_per_rev": bullet_info.get("pref_twist_rate_in_per_rev"),
                "data_source_name": bullet_info.get("data_source_name"),
                "data_source_url": bullet_info.get("data_source_url"),
            }
            processed_data.append(processed_item)

        # Convert to DataFrame for better display
        df = pd.DataFrame(processed_data)

        # Display summary stats
        st.subheader("📊 Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Entries", len(df))

        with col2:
            unique_makes = df["cartridge_make"].nunique()
            st.metric("Manufacturers", unique_makes)

        with col3:
            unique_calibers = df["bore_diameter_land_mm"].nunique()
            st.metric("Calibers", unique_calibers)

        with col4:
            unique_bullets = df["bullet_id"].nunique()
            st.metric("Unique Bullets", unique_bullets)

        # Add filters
        st.subheader("🔍 Filter Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            cartridge_types = ["All"] + sorted([ct for ct in df["cartridge_type"].unique().tolist() if ct])
            selected_cartridge_type = st.selectbox("Cartridge Type:", cartridge_types)

        with col2:
            cartridge_makes = ["All"] + sorted(df["cartridge_make"].unique().tolist())
            selected_cartridge_make = st.selectbox("Cartridge Manufacturer:", cartridge_makes)

        with col3:
            cartridge_models = ["All"] + sorted(df["cartridge_model"].unique().tolist())
            selected_cartridge_model = st.selectbox("Cartridge Model:", cartridge_models)

        col4, col5, col6 = st.columns(3)

        with col4:
            bullet_weights = ["All"] + sorted(df["bullet_weight_grains"].unique().tolist())
            selected_bullet_weight = st.selectbox("Bullet Weight:", bullet_weights)

        with col5:
            bullet_manufacturers = ["All"] + sorted(df["bullet_manufacturer"].unique().tolist())
            selected_bullet_manufacturer = st.selectbox("Bullet Manufacturer:", bullet_manufacturers)

        with col6:
            bullet_models = ["All"] + sorted(df["bullet_model"].unique().tolist())
            selected_bullet_model = st.selectbox("Bullet Model:", bullet_models)

        # Apply filters
        filtered_df = df.copy()
        if selected_cartridge_type != "All":
            filtered_df = filtered_df[filtered_df["cartridge_type"] == selected_cartridge_type]
        if selected_cartridge_make != "All":
            filtered_df = filtered_df[filtered_df["cartridge_make"] == selected_cartridge_make]
        if selected_cartridge_model != "All":
            filtered_df = filtered_df[filtered_df["cartridge_model"] == selected_cartridge_model]
        if selected_bullet_weight != "All":
            filtered_df = filtered_df[filtered_df["bullet_weight_grains"] == selected_bullet_weight]
        if selected_bullet_manufacturer != "All":
            filtered_df = filtered_df[filtered_df["bullet_manufacturer"] == selected_bullet_manufacturer]
        if selected_bullet_model != "All":
            filtered_df = filtered_df[filtered_df["bullet_model"] == selected_bullet_model]

        # Display filtered results count
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df)} of {len(df)} entries")

        # Display the table
        st.subheader("📦 Factory Cartridge Entries")

        if len(filtered_df) == 0:
            st.warning("No entries match the selected filters.")
            return

        # Prepare display DataFrame
        display_df = filtered_df.copy()

        # Handle nullable fields by filling NaN values
        display_df["cartridge_type"] = display_df["cartridge_type"].fillna("N/A")
        display_df["bullet_length_mm"] = display_df["bullet_length_mm"].fillna("N/A")
        display_df["ballistic_coefficient_g1"] = display_df["ballistic_coefficient_g1"].fillna("N/A")
        display_df["ballistic_coefficient_g7"] = display_df["ballistic_coefficient_g7"].fillna("N/A")
        display_df["sectional_density"] = display_df["sectional_density"].fillna("N/A")
        display_df["min_req_twist_rate_in_per_rev"] = display_df["min_req_twist_rate_in_per_rev"].fillna("N/A")
        display_df["pref_twist_rate_in_per_rev"] = display_df["pref_twist_rate_in_per_rev"].fillna("N/A")
        display_df["data_source_name"] = display_df["data_source_name"].fillna("N/A")
        display_df["data_source_url"] = display_df["data_source_url"].fillna("N/A")

        # Select and rename columns for display
        display_df = display_df[
            [
                "cartridge_type",
                "cartridge_make",
                "cartridge_model",
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
                "data_source_name",
                "data_source_url"
            ]
        ].rename(
            columns={
                "cartridge_type": "Cartridge Type",
                "cartridge_make": "Cartridge Make",
                "cartridge_model": "Cartridge Model",
                "bullet_manufacturer": "Bullet Make",
                "bullet_model": "Bullet Model",
                "bullet_weight_grains": "Weight (gr)",
                "bullet_diameter_groove_mm": "Bullet Dia (mm)",
                "bore_diameter_land_mm": "Bore Dia (mm)",
                "bullet_length_mm": "Length (mm)",
                "ballistic_coefficient_g1": "BC G1",
                "ballistic_coefficient_g7": "BC G7",
                "sectional_density": "Sectional Density",
                "min_req_twist_rate_in_per_rev": "Min Twist Rate",
                "pref_twist_rate_in_per_rev": "Pref Twist Rate",
                "data_source_name": "Data Source",
                "data_source_url": "Source URL"
            }
        )

        # Display the table with enhanced formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cartridge Type": st.column_config.TextColumn("Cartridge Type", width="small"),
                "Cartridge Make": st.column_config.TextColumn("Cartridge Make", width="small"),
                "Cartridge Model": st.column_config.TextColumn("Cartridge Model", width="medium"),
                "Bullet Make": st.column_config.TextColumn("Bullet Make", width="small"),
                "Bullet Model": st.column_config.TextColumn("Bullet Model", width="small"),
                "Weight (gr)": st.column_config.NumberColumn("Weight (gr)", width="small"),
                "Bullet Dia (mm)": st.column_config.NumberColumn("Bullet Dia (mm)", width="small", format="%.3f"),
                "Bore Dia (mm)": st.column_config.NumberColumn("Bore Dia (mm)", width="small", format="%.3f"),
                "Length (mm)": st.column_config.TextColumn("Length (mm)", width="small"),
                "BC G1": st.column_config.TextColumn("BC G1", width="small"),
                "BC G7": st.column_config.TextColumn("BC G7", width="small"),
                "Sectional Density": st.column_config.TextColumn("Sectional Density", width="small"),
                "Min Twist Rate": st.column_config.TextColumn("Min Twist Rate", width="small"),
                "Pref Twist Rate": st.column_config.TextColumn("Pref Twist Rate", width="small"),
                "Data Source": st.column_config.TextColumn("Data Source", width="medium"),
                "Source URL": st.column_config.LinkColumn("Source URL", width="medium")
            },
        )

        # Admin-only functionality
        is_admin = user.get("user_metadata", {}).get("is_admin", False) or user.get("email") == "johnduffie91@gmail.com"
        
        if is_admin:
            # Delete functionality (admin only)
            st.subheader("🗑️ Delete Entry (Admin Only)")
            with st.expander("Delete a factory cartridge entry"):
                st.warning("⚠️ This action cannot be undone!")

                # Create list of entries for deletion
                entry_options = []
                for _, row in filtered_df.iterrows():
                    entry_label = (
                        f"{row['cartridge_make']} {row['cartridge_model']} - {row['bullet_manufacturer']} {row['bullet_model']} {row['bullet_weight_grains']}gr"
                    )
                    entry_options.append((entry_label, row["id"]))

                if entry_options:
                    selected_entry = st.selectbox(
                        "Select entry to delete:",
                        options=[None] + entry_options,
                        format_func=lambda x: "Select an entry..." if x is None else x[0],
                    )

                    if selected_entry:
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if st.button("🗑️ Delete", type="secondary"):
                                try:
                                    # Delete the entry
                                    delete_response = (
                                        supabase.table("factory_cartridge_specs")
                                        .delete()
                                        .eq("id", selected_entry[1])
                                        .execute()
                                    )

                                    if delete_response.data:
                                        st.success(f"✅ Deleted: {selected_entry[0]}")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to delete entry.")
                                except Exception as e:
                                    st.error(f"❌ Error deleting entry: {str(e)}")
                else:
                    st.info("No entries available for deletion with current filters.")
        else:
            # Info for non-admin users
            st.info("ℹ️ This is a read-only view of the global factory cartridge database maintained by administrators.")

    except Exception as e:
        st.error(f"❌ Error loading factory cartridge entries: {str(e)}")
        st.info("Please check your database connection and try again.")