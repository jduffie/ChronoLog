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
            .eq("user_id", user["email"])
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
            unique_bullet_length = df["bullet_length_mm"].nunique()
            st.metric("Bullet Length", unique_bullet_length)

        with col4:
            weight_grains = df["weight_grains"].nunique()
            st.metric("Weights", weight_grains)

        # Add filters
        st.subheader("🔍 Filter Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            manufacturers = ["All"] + sorted(df["manufacturer"].unique().tolist())
            selected_manufacturer = st.selectbox("Filter by Manufacturer:", manufacturers)

        with col2:
            bullet_length_mms = ["All"] + sorted(df["bullet_length_mm"].unique().tolist())
            selected_bullet_length_mm = st.selectbox("Filter by Bullet Length:", bullet_length_mms)

        with col3:
            weights = ["All"] + sorted(df["weight_grains"].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight:", weights)

        # Apply filters
        filtered_df = df.copy()
        if selected_manufacturer != "All":
            filtered_df = filtered_df[filtered_df["manufacturer"] == selected_manufacturer]
        if selected_bullet_length_mm != "All":
            filtered_df = filtered_df[filtered_df["bullet_length_mm"] == selected_bullet_length_mm]
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

        # Select and rename columns for display
        display_df = display_df[
            ["manufacturer", "model", "bullet_length_mm", "weight_grains"]
        ].rename(
            columns={
                "manufacturer": "Manufacturer",
                "model": "Model",
                "bullet_length_mm": "Bullet Length",
                "weight_grains": "Weight",
            }
        )

        # Display the table with enhanced formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Manufacturer": st.column_config.TextColumn(
                    "Manufacturer", width="medium"
                ),
                "Model": st.column_config.TextColumn("Model", width="medium"),
                "Bullet Length": st.column_config.TextColumn("Bullet Length", width="medium"),
                "Weight": st.column_config.TextColumn("Weight", width="small"),
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
                    f"{row['manufacturer']} {row['model']} - {row['bullet_length_mm']} - {row['weight_grains']}"
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
