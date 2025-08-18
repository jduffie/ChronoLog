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
                    bore_diameter_land_mm,
                    ballistic_coefficient_g1,
                    ballistic_coefficient_g7
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
                "cartridge_make": item["make"],
                "cartridge_model": item["model"],
                "bullet_id": item["bullet_id"],
                "bullet_manufacturer": bullet_info["manufacturer"],
                "bullet_model": bullet_info["model"],
                "bullet_weight_grains": bullet_info["weight_grains"],
                "bore_diameter_land_mm": bullet_info["bore_diameter_land_mm"],
                "ballistic_coefficient_g1": bullet_info.get("ballistic_coefficient_g1"),
                "ballistic_coefficient_g7": bullet_info.get("ballistic_coefficient_g7"),
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
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            calibers = ["All"] + sorted(df["bore_diameter_land_mm"].unique().tolist())
            selected_bore_diameter_mm = st.selectbox("Bore Diameter:", calibers)

        with col2:
            cartridge_makes = ["All"] + sorted(df["cartridge_make"].unique().tolist())
            selected_cartridge_make = st.selectbox("Cartridge Manufacturer:", cartridge_makes)

        with col3:
            cartridge_models = ["All"] + sorted(df["cartridge_model"].unique().tolist())
            selected_cartridge_model = st.selectbox("Cartridge Model:", cartridge_models)

        with col4:
            bullet_manufacturers = ["All"] + sorted(df["bullet_manufacturer"].unique().tolist())
            selected_bullet_manufacturer = st.selectbox("Bullet Manufacturer:", bullet_manufacturers)

        with col5:
            bullet_models = ["All"] + sorted(df["bullet_model"].unique().tolist())
            selected_bullet_model = st.selectbox("Bullet Model:", bullet_models)

        # Apply filters
        filtered_df = df.copy()
        if selected_bore_diameter_mm != "All":
            filtered_df = filtered_df[filtered_df["bore_diameter_land_mm"] == selected_bore_diameter_mm]
        if selected_cartridge_make != "All":
            filtered_df = filtered_df[filtered_df["cartridge_make"] == selected_cartridge_make]
        if selected_cartridge_model != "All":
            filtered_df = filtered_df[filtered_df["cartridge_model"] == selected_cartridge_model]
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
        display_df["ballistic_coefficient_g1"] = display_df["ballistic_coefficient_g1"].fillna("N/A")
        display_df["ballistic_coefficient_g7"] = display_df["ballistic_coefficient_g7"].fillna("N/A")

        # Select and rename columns for display
        display_df = display_df[
            [
                "cartridge_make",
                "cartridge_model",
                "bullet_manufacturer",
                "bullet_model",
                "bullet_weight_grains",
                "bore_diameter_land_mm",
                "ballistic_coefficient_g1",
                "ballistic_coefficient_g7"
            ]
        ].rename(
            columns={
                "cartridge_make": "Cartridge Make",
                "cartridge_model": "Cartridge Model",
                "bullet_manufacturer": "Bullet Make",
                "bullet_model": "Bullet Model",
                "bullet_weight_grains": "Weight (gr)",
                "bore_diameter_land_mm": "Bore Dia (mm)",
                "ballistic_coefficient_g1": "BC G1",
                "ballistic_coefficient_g7": "BC G7"
            }
        )

        # Display the table with enhanced formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cartridge Make": st.column_config.TextColumn("Cartridge Make", width="small"),
                "Cartridge Model": st.column_config.TextColumn("Cartridge Model", width="medium"),
                "Bullet Make": st.column_config.TextColumn("Bullet Make", width="small"),
                "Bullet Model": st.column_config.TextColumn("Bullet Model", width="small"),
                "Weight (gr)": st.column_config.NumberColumn("Weight (gr)", width="small"),
                "Diameter (mm)": st.column_config.NumberColumn("Diameter (mm)", width="small", format="%.3f"),
                "Bore Dia (mm)": st.column_config.NumberColumn("Bore Dia (mm)", width="small", format="%.3f"),
                "BC G1": st.column_config.TextColumn("BC G1", width="small"),
                "BC G7": st.column_config.TextColumn("BC G7", width="small")
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