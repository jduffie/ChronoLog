from datetime import datetime

import pandas as pd
import streamlit as st


def render_view_bullets_tab(user, supabase):
    """Render the View Bullets tab"""
    st.header("📋 View Bullets Entries")

    try:
        # Get all bullets entries for the user
        response = (
            supabase.table("bullets")
            .select("*")
            .eq("user_id", user["id"])
            .order("id", desc=True)
            .execute()
        )

        if not response.data:
            st.info(
                "📭 No bullets entries found. Go to the 'Create' tab to add your first bullets entry."
            )
            return

        # Convert to DataFrame for better display
        df = pd.DataFrame(response.data)

        # Display summary stats
        st.subheader("📊 Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Entries", len(df))

        with col2:
            unique_manufacturers = df["manufacturer"].nunique()
            st.metric("Manufacturers", unique_manufacturers)

        with col3:
            unique_calibers = df["bullet_diameter_groove_mm"].nunique()
            st.metric("Calibers", unique_calibers)

        with col4:
            avg_bc_g1 = df["ballistic_coefficient_g1"].mean()
            if pd.notna(avg_bc_g1):
                st.metric("Avg BC (G1)", f"{avg_bc_g1:.3f}")
            else:
                st.metric("Avg BC (G1)", "N/A")

        # Add filters
        st.subheader("🔍 Filter Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            manufacturers = ["All"] + sorted(df["manufacturer"].unique().tolist())
            selected_manufacturer = st.selectbox("Filter by Manufacturer:", manufacturers)

        with col2:
            calibers = ["All"] + sorted(df["bore_diameter_land_mm"].unique().tolist())
            selected_caliber = st.selectbox("Filter by Bore Diameter:", calibers)

        with col3:
            weights = ["All"] + sorted(df["weight_grains"].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight:", weights)

        # Apply filters
        filtered_df = df.copy()
        if selected_manufacturer != "All":
            filtered_df = filtered_df[filtered_df["manufacturer"] == selected_manufacturer]
        if selected_caliber != "All":
            filtered_df = filtered_df[filtered_df["bullet_diameter_groove_mm"] == selected_caliber]
        if selected_weight != "All":
            filtered_df = filtered_df[filtered_df["weight_grains"] == selected_weight]

        # Display filtered results count
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df)} of {len(df)} entries")

        # Display the table
        st.subheader("📝 Bullets Entries")

        if len(filtered_df) == 0:
            st.warning("No entries match the selected filters.")
            return

        # Prepare display DataFrame
        display_df = filtered_df.copy()

        # No date formatting needed since we removed created_at and updated_at

        # Handle nullable fields by filling NaN values
        display_df["bullet_length_mm"] = display_df["bullet_length_mm"].fillna("N/A")
        display_df["ballistic_coefficient_g1"] = display_df["ballistic_coefficient_g1"].fillna("N/A")
        display_df["ballistic_coefficient_g7"] = display_df["ballistic_coefficient_g7"].fillna("N/A")
        display_df["sectional_density"] = display_df["sectional_density"].fillna("N/A")
        display_df["min_req_twist_rate_in_per_rev"] = display_df["min_req_twist_rate_in_per_rev"].fillna("N/A")
        display_df["pref_twist_rate_in_per_rev"] = display_df["pref_twist_rate_in_per_rev"].fillna("N/A")

        # Select and rename columns for display
        display_df = display_df[
            [
                "manufacturer", 
                "model", 
                "weight_grains", 
                "bullet_diameter_groove_mm", 
                "bore_diameter_land_mm",
                "bullet_length_mm", 
                "ballistic_coefficient_g1", 
                "ballistic_coefficient_g7",
                "sectional_density",
                "min_req_twist_rate_in_per_rev",
                "pref_twist_rate_in_per_rev"
            ]
        ].rename(
            columns={
                "manufacturer": "Manufacturer",
                "model": "Model",
                "weight_grains": "Weight (gr)",
                "bullet_diameter_groove_mm": "Diameter (mm)",
                "bore_diameter_land_mm": "Bore Dia (mm)",
                "bullet_length_mm": "Length (mm)",
                "ballistic_coefficient_g1": "BC G1",
                "ballistic_coefficient_g7": "BC G7",
                "sectional_density": "Sectional Density",
                "min_req_twist_rate_in_per_rev": "Min Twist Rate",
                "pref_twist_rate_in_per_rev": "Pref Twist Rate"
            }
        )

        # Display the table with enhanced formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Manufacturer": st.column_config.TextColumn("Manufacturer", width="small"),
                "Model": st.column_config.TextColumn("Model", width="small"),
                "Weight (gr)": st.column_config.NumberColumn("Weight (gr)", width="small"),
                "Diameter (mm)": st.column_config.NumberColumn("Diameter (mm)", width="small", format="%.3f"),
                "Bore Dia (mm)": st.column_config.NumberColumn("Bore Dia (mm)", width="small", format="%.3f"),
                "Length (mm)": st.column_config.TextColumn("Length (mm)", width="small"),
                "BC G1": st.column_config.TextColumn("BC G1", width="small"),
                "BC G7": st.column_config.TextColumn("BC G7", width="small"),
                "Sectional Density": st.column_config.TextColumn("Sectional Density", width="small"),
                "Min Twist Rate": st.column_config.TextColumn("Min Twist Rate", width="small"),
                "Pref Twist Rate": st.column_config.TextColumn("Pref Twist Rate", width="small")
            },
        )

        # Export option
        st.subheader("📤 Export")
        if st.button("📥 Download as CSV"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"bullets_entries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

        # Delete functionality
        st.subheader("🗑️ Delete Entry")
        with st.expander("Delete an bullets entry"):
            st.warning("⚠️ This action cannot be undone!")

            # Create list of entries for deletion
            entry_options = []
            for _, row in filtered_df.iterrows():
                entry_label = (
                    f"{row['manufacturer']} {row['model']} - {row['weight_grains']}gr - {row['bullet_diameter_groove_mm']}mm"
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
                                    supabase.table("bullets")
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

    except Exception as e:
        st.error(f"❌ Error loading bullets entries: {str(e)}")
        st.info("Please check your database connection and try again.")
