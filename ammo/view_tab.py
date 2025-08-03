from datetime import datetime

import pandas as pd
import streamlit as st


def render_view_ammo_tab(user, supabase):
    """Render the View Ammo tab"""
    st.header("📋 View Ammo Entries")

    try:
        # Get all ammo entries for the user
        response = (
            supabase.table("ammo")
            .select("*")
            .eq("user_email", user["email"])
            .order("created_at", desc=True)
            .execute()
        )

        if not response.data:
            st.info(
                "📭 No ammo entries found. Go to the 'Create' tab to add your first ammo entry."
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
            unique_makes = df["make"].nunique()
            st.metric("Manufacturers", unique_makes)

        with col3:
            unique_calibers = df["caliber"].nunique()
            st.metric("Calibers", unique_calibers)

        with col4:
            unique_weights = df["weight"].nunique()
            st.metric("Weights", unique_weights)

        # Add filters
        st.subheader("🔍 Filter Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            makes = ["All"] + sorted(df["make"].unique().tolist())
            selected_make = st.selectbox("Filter by Manufacturer:", makes)

        with col2:
            calibers = ["All"] + sorted(df["caliber"].unique().tolist())
            selected_caliber = st.selectbox("Filter by Caliber:", calibers)

        with col3:
            weights = ["All"] + sorted(df["weight"].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight:", weights)

        # Apply filters
        filtered_df = df.copy()
        if selected_make != "All":
            filtered_df = filtered_df[filtered_df["make"] == selected_make]
        if selected_caliber != "All":
            filtered_df = filtered_df[filtered_df["caliber"] == selected_caliber]
        if selected_weight != "All":
            filtered_df = filtered_df[filtered_df["weight"] == selected_weight]

        # Display filtered results count
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df)} of {len(df)} entries")

        # Display the table
        st.subheader("📝 Ammo Entries")

        if len(filtered_df) == 0:
            st.warning("No entries match the selected filters.")
            return

        # Prepare display DataFrame
        display_df = filtered_df.copy()

        # Format dates for display
        display_df["created_at"] = pd.to_datetime(display_df["created_at"]).dt.strftime(
            "%Y-%m-%d %H:%M"
        )
        display_df["updated_at"] = pd.to_datetime(display_df["updated_at"]).dt.strftime(
            "%Y-%m-%d %H:%M"
        )

        # Select and rename columns for display
        display_df = display_df[
            ["make", "model", "caliber", "weight", "created_at", "updated_at"]
        ].rename(
            columns={
                "make": "Manufacturer",
                "model": "Model",
                "caliber": "Caliber",
                "weight": "Weight",
                "created_at": "Created",
                "updated_at": "Updated",
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
                "Caliber": st.column_config.TextColumn("Caliber", width="medium"),
                "Weight": st.column_config.TextColumn("Weight", width="small"),
                "Created": st.column_config.TextColumn("Created", width="medium"),
                "Updated": st.column_config.TextColumn("Updated", width="medium"),
            },
        )

        # Export option
        st.subheader("📤 Export")
        if st.button("📥 Download as CSV"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"ammo_entries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

        # Delete functionality
        st.subheader("🗑️ Delete Entry")
        with st.expander("Delete an ammo entry"):
            st.warning("⚠️ This action cannot be undone!")

            # Create list of entries for deletion
            entry_options = []
            for _, row in filtered_df.iterrows():
                entry_label = (
                    f"{row['make']} {row['model']} - {row['caliber']} - {row['weight']}"
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
                                    supabase.table("ammo")
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
        st.error(f"❌ Error loading ammo entries: {str(e)}")
        st.info("Please check your database connection and try again.")
