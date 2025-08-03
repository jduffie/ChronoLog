import streamlit as st
import pandas as pd
from datetime import datetime


def render_view_rifle_tab(user, supabase):
    """Render the View Rifles tab"""
    st.header("📋 View Rifle Entries")

    try:
        # Get all rifle entries for the user
        response = (
            supabase.table("rifles")
            .select("*")
            .eq("user_email", user["email"])
            .order("created_at", desc=True)
            .execute()
        )

        if not response.data:
            st.info(
                "📭 No rifle entries found. Go to the 'Create' tab to add your first rifle."
            )
            return

        # Convert to DataFrame for better display
        df = pd.DataFrame(response.data)

        # Display summary stats
        st.subheader("📊 Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Rifles", len(df))

        with col2:
            # Count rifles with twist ratio specified
            twist_count = df["barrel_twist_ratio"].notna().sum()
            st.metric("With Twist Ratio", twist_count)

        with col3:
            # Count rifles with scope specified
            scope_count = df["scope"].notna().sum()
            st.metric("With Scope", scope_count)

        with col4:
            # Count rifles with trigger specified
            trigger_count = df["trigger"].notna().sum()
            st.metric("With Trigger Info", trigger_count)

        # Add filters
        st.subheader("🔍 Filter Options")
        col1, col2 = st.columns(2)

        with col1:
            # Filter by twist ratio
            twist_ratios = df["barrel_twist_ratio"].dropna().unique()
            twist_options = ["All"] + sorted([t for t in twist_ratios if t])
            selected_twist = st.selectbox("Filter by Twist Ratio:", twist_options)

        with col2:
            # Filter by rifles with complete info
            completeness_options = ["All", "Complete Info Only", "Missing Info Only"]
            selected_completeness = st.selectbox(
                "Filter by Completeness:", completeness_options
            )

        # Apply filters
        filtered_df = df.copy()

        if selected_twist != "All":
            filtered_df = filtered_df[
                filtered_df["barrel_twist_ratio"] == selected_twist
            ]

        if selected_completeness == "Complete Info Only":
            # Filter to rifles with all major fields filled
            filtered_df = filtered_df[
                filtered_df["barrel_twist_ratio"].notna()
                & filtered_df["barrel_length"].notna()
                & filtered_df["sight_offset"].notna()
                & filtered_df["trigger"].notna()
                & filtered_df["scope"].notna()
            ]
        elif selected_completeness == "Missing Info Only":
            # Filter to rifles with any missing major fields
            filtered_df = filtered_df[
                filtered_df["barrel_twist_ratio"].isna()
                | filtered_df["barrel_length"].isna()
                | filtered_df["sight_offset"].isna()
                | filtered_df["trigger"].isna()
                | filtered_df["scope"].isna()
            ]

        # Display filtered results count
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df)} of {len(df)} rifles")

        # Display the table
        st.subheader("🔫 Rifle Entries")

        if len(filtered_df) == 0:
            st.warning("No rifles match the selected filters.")
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

        # Replace NaN values with empty strings for better display
        display_df = display_df.fillna("")

        # Select and rename columns for display
        display_df = display_df[
            [
                "name",
                "barrel_twist_ratio",
                "barrel_length",
                "sight_offset",
                "trigger",
                "scope",
                "created_at",
                "updated_at",
            ]
        ].rename(
            columns={
                "name": "Rifle Name",
                "barrel_twist_ratio": "Twist Ratio",
                "barrel_length": "Barrel Length",
                "sight_offset": "Sight Offset",
                "trigger": "Trigger",
                "scope": "Scope",
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
                "Rifle Name": st.column_config.TextColumn("Rifle Name", width="medium"),
                "Twist Ratio": st.column_config.TextColumn(
                    "Twist Ratio", width="small"
                ),
                "Barrel Length": st.column_config.TextColumn(
                    "Barrel Length", width="small"
                ),
                "Sight Offset": st.column_config.TextColumn(
                    "Sight Offset", width="small"
                ),
                "Trigger": st.column_config.TextColumn("Trigger", width="medium"),
                "Scope": st.column_config.TextColumn("Scope", width="large"),
                "Created": st.column_config.TextColumn("Created", width="medium"),
                "Updated": st.column_config.TextColumn("Updated", width="medium"),
            },
        )

        # Detailed view for individual rifles
        st.subheader("🔍 Detailed View")
        with st.expander("View individual rifle details"):
            rifle_names = filtered_df["name"].tolist()
            selected_rifle_name = st.selectbox("Select a rifle:", rifle_names)

            if selected_rifle_name:
                rifle_data = filtered_df[
                    filtered_df["name"] == selected_rifle_name
                ].iloc[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Basic Information**")
                    st.write(f"**Name:** {rifle_data['name']}")
                    st.write(
                        f"**Twist Ratio:** {rifle_data['barrel_twist_ratio'] or 'Not specified'}"
                    )
                    st.write(
                        f"**Barrel Length:** {rifle_data['barrel_length'] or 'Not specified'}"
                    )
                    st.write(
                        f"**Sight Offset:** {rifle_data['sight_offset'] or 'Not specified'}"
                    )

                with col2:
                    st.markdown("**Components**")
                    st.write(f"**Trigger:** {rifle_data['trigger'] or 'Not specified'}")
                    st.write(f"**Scope:** {rifle_data['scope'] or 'Not specified'}")
                    st.write(
                        f"**Created:** {pd.to_datetime(rifle_data['created_at']).strftime('%Y-%m-%d %H:%M')}"
                    )
                    st.write(
                        f"**Updated:** {pd.to_datetime(rifle_data['updated_at']).strftime('%Y-%m-%d %H:%M')}"
                    )

        # Export option
        st.subheader("📤 Export")
        if st.button("📥 Download as CSV"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"rifles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

        # Delete functionality
        st.subheader("🗑️ Delete Entry")
        with st.expander("Delete a rifle entry"):
            st.warning("⚠️ This action cannot be undone!")

            # Create list of rifles for deletion
            rifle_options = []
            for _, row in filtered_df.iterrows():
                rifle_label = f"{row['name']}"
                if row["barrel_twist_ratio"] or row["barrel_length"]:
                    details = []
                    if row["barrel_twist_ratio"]:
                        details.append(f"Twist: {row['barrel_twist_ratio']}")
                    if row["barrel_length"]:
                        details.append(f"Length: {row['barrel_length']}")
                    rifle_label += f" ({', '.join(details)})"
                rifle_options.append((rifle_label, row["id"]))

            if rifle_options:
                selected_rifle = st.selectbox(
                    "Select rifle to delete:",
                    options=[None] + rifle_options,
                    format_func=lambda x: "Select a rifle..." if x is None else x[0],
                )

                if selected_rifle:
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("🗑️ Delete", type="secondary"):
                            try:
                                # Delete the rifle
                                delete_response = (
                                    supabase.table("rifles")
                                    .delete()
                                    .eq("id", selected_rifle[1])
                                    .execute()
                                )

                                if delete_response.data:
                                    st.success(f"✅ Deleted: {selected_rifle[0]}")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete rifle.")
                            except Exception as e:
                                st.error(f"❌ Error deleting rifle: {str(e)}")
            else:
                st.info("No rifles available for deletion with current filters.")

    except Exception as e:
        st.error(f"❌ Error loading rifle entries: {str(e)}")
        st.info("Please check your database connection and try again.")
