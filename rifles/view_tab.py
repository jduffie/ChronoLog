from datetime import datetime

import pandas as pd
import streamlit as st


@st.cache_data
def get_cartridge_types(_supabase):
    """Get cartridge types from database with caching"""
    try:
        response = _supabase.table("cartridge_types").select("name").execute()
        return sorted([item["name"] for item in response.data])
    except Exception as e:
        return []


def render_view_rifle_tab(user, supabase):
    """Render the View Rifles tab"""
    st.header(" View Rifle Entries")

    try:
        # Get all rifle entries for the user
        response = (
            supabase.table("rifles")
            .select("*")
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .execute()
        )

        if not response.data:
            st.info(
                " No rifle entries found. Go to the 'Create' tab to add your first rifle."
            )
            return

        # Convert to DataFrame for better display
        df = pd.DataFrame(response.data)

        # Display summary stats
        st.subheader(" Summary")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Rifles", len(df))

        with col2:
            # Count unique cartridge types
            cartridge_count = df["cartridge_type"].nunique()
            st.metric("Cartridge Types", cartridge_count)

        # Add filters
        st.subheader(" Filter Options")
        col1, col2 = st.columns(2)

        with col1:
            # Filter by cartridge type
            cartridge_types = df["cartridge_type"].dropna().unique()
            cartridge_options = ["All"] + sorted([c for c in cartridge_types if c])
            selected_cartridge = st.selectbox("Filter by Cartridge Type:", cartridge_options)

        with col2:
            # Filter by twist ratio
            twist_ratios = df["barrel_twist_ratio"].dropna().unique()
            twist_options = ["All"] + sorted([t for t in twist_ratios if t])
            selected_twist = st.selectbox("Filter by Twist Ratio:", twist_options)


        # Apply filters
        filtered_df = df.copy()

        if selected_cartridge != "All":
            filtered_df = filtered_df[
                filtered_df["cartridge_type"] == selected_cartridge
            ]

        if selected_twist != "All":
            filtered_df = filtered_df[
                filtered_df["barrel_twist_ratio"] == selected_twist
            ]

        # Display filtered results count
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df)} of {len(df)} rifles")

        # Display the table
        st.subheader(" Rifle Entries")

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
                "cartridge_type",
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
                "cartridge_type": "Cartridge Type",
                "barrel_twist_ratio": "Twist Ratio",
                "barrel_length": "Barrel Length",
                "sight_offset": "Sight Offset",
                "trigger": "Trigger",
                "scope": "Scope",
                "created_at": "Created",
                "updated_at": "Updated",
            }
        )

        # Display the table with enhanced formatting and selection
        selected_rifle_event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "Rifle Name": st.column_config.TextColumn("Rifle Name", width="medium"),
                "Cartridge Type": st.column_config.TextColumn("Cartridge Type", width="medium"),
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

        # Handle rifle selection from table click
        selected_rifle_data = None
        if selected_rifle_event["selection"]["rows"]:
            selected_row_index = selected_rifle_event["selection"]["rows"][0]
            # Get the rifle data from the filtered_df using the display index
            selected_rifle_data = filtered_df.iloc[selected_row_index].copy()

        # Show detailed view and actions if a rifle is selected
        if selected_rifle_data is not None:
            st.subheader(f"🔍 {selected_rifle_data['name']} Details")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown("**Basic Information**")
                st.write(f"**Name:** {selected_rifle_data['name']}")
                st.write(f"**Cartridge Type:** {selected_rifle_data['cartridge_type']}")
                st.write(
                    f"**Twist Ratio:** {selected_rifle_data['barrel_twist_ratio'] or 'Not specified'}"
                )
                st.write(
                    f"**Barrel Length:** {selected_rifle_data['barrel_length'] or 'Not specified'}"
                )
                st.write(
                    f"**Sight Offset:** {selected_rifle_data['sight_offset'] or 'Not specified'}"
                )

            with col2:
                st.markdown("**Components**")
                st.write(f"**Trigger:** {selected_rifle_data['trigger'] or 'Not specified'}")
                st.write(f"**Scope:** {selected_rifle_data['scope'] or 'Not specified'}")
                st.write(
                    f"**Created:** {pd.to_datetime(selected_rifle_data['created_at']).strftime('%Y-%m-%d %H:%M')}"
                )
                st.write(
                    f"**Updated:** {pd.to_datetime(selected_rifle_data['updated_at']).strftime('%Y-%m-%d %H:%M')}"
                )
            
            with col3:
                st.markdown("**Actions**")
                # Edit button
                if st.button("✏️ Edit", type="secondary", use_container_width=True):
                    st.session_state.editing_rifle_id = selected_rifle_data['id']
                
                # Delete button
                if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                    st.session_state.deleting_rifle_id = selected_rifle_data['id']
        
        else:
            st.info("💡 Click on a rifle in the table above to view details and access Edit/Delete options")

        # Export option
        st.subheader(" Export")
        if st.button(" Download as CSV"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label=" Download CSV",
                data=csv,
                file_name=f"rifles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

        # Handle Edit Modal
        if hasattr(st.session_state, 'editing_rifle_id') and st.session_state.editing_rifle_id:
            # Get the rifle data for editing
            rifle_to_edit = filtered_df[
                filtered_df["id"] == st.session_state.editing_rifle_id
            ].iloc[0] if not filtered_df[filtered_df["id"] == st.session_state.editing_rifle_id].empty else None
            
            if rifle_to_edit is not None:
                st.subheader(f"✏️ Edit {rifle_to_edit['name']}")
                st.info("ℹ️ You can only edit optional attributes. Name and cartridge type cannot be changed.")
                
                # Create edit form with only nullable fields
                with st.form(f"edit_rifle_form_{st.session_state.editing_rifle_id}"):
                    st.markdown("**Editable Attributes:**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_barrel_twist_ratio = st.text_input(
                            "Barrel Twist Ratio",
                            value=rifle_to_edit["barrel_twist_ratio"] or "",
                            placeholder="e.g., 1:8, 1:10, 1:12",
                            help="The barrel twist ratio (e.g., 1:8 means one complete turn in 8 inches)",
                        )

                        new_barrel_length = st.text_input(
                            "Barrel Length",
                            value=rifle_to_edit["barrel_length"] or "",
                            placeholder='e.g., 24 inches, 20", 16.5"',
                            help="The barrel length including units",
                        )

                        new_sight_offset = st.text_input(
                            "Sight Offset/Height",
                            value=rifle_to_edit["sight_offset"] or "",
                            placeholder='e.g., 1.5 inches, 38mm, 1.75"',
                            help="Height of the scope/sight above the bore centerline",
                        )

                    with col2:
                        new_trigger = st.text_input(
                            "Trigger",
                            value=rifle_to_edit["trigger"] or "",
                            placeholder="e.g., Timney 2-stage, Jewell HVR, Stock trigger",
                            help="Trigger type and specifications",
                        )

                        new_scope = st.text_input(
                            "Scope",
                            value=rifle_to_edit["scope"] or "",
                            placeholder="e.g., Vortex Viper PST 5-25x50, Nightforce NXS 3.5-15x50",
                            help="Scope make, model, and specifications",
                        )

                    # Form buttons
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        submitted = st.form_submit_button("💾 Update Rifle", type="primary", use_container_width=True)
                    with col2:
                        cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)

                    if cancelled:
                        del st.session_state.editing_rifle_id
                        st.rerun()

                    if submitted:
                        try:
                            # Prepare update data (only nullable fields)
                            update_data = {
                                "barrel_twist_ratio": new_barrel_twist_ratio.strip() if new_barrel_twist_ratio.strip() else None,
                                "barrel_length": new_barrel_length.strip() if new_barrel_length.strip() else None,
                                "sight_offset": new_sight_offset.strip() if new_sight_offset.strip() else None,
                                "trigger": new_trigger.strip() if new_trigger.strip() else None,
                                "scope": new_scope.strip() if new_scope.strip() else None,
                                "updated_at": datetime.now().isoformat(),
                            }

                            # Update the rifle
                            update_response = (
                                supabase.table("rifles")
                                .update(update_data)
                                .eq("id", st.session_state.editing_rifle_id)
                                .eq("user_id", user["id"])  # Extra security check
                                .execute()
                            )

                            if update_response.data:
                                st.success(f"✅ Successfully updated: {rifle_to_edit['name']}")
                                
                                # Show what changed
                                changes = []
                                if rifle_to_edit["barrel_twist_ratio"] != update_data["barrel_twist_ratio"]:
                                    changes.append(f"Twist Ratio: '{rifle_to_edit['barrel_twist_ratio'] or 'None'}' → '{update_data['barrel_twist_ratio'] or 'None'}'")
                                if rifle_to_edit["barrel_length"] != update_data["barrel_length"]:
                                    changes.append(f"Barrel Length: '{rifle_to_edit['barrel_length'] or 'None'}' → '{update_data['barrel_length'] or 'None'}'")
                                if rifle_to_edit["sight_offset"] != update_data["sight_offset"]:
                                    changes.append(f"Sight Offset: '{rifle_to_edit['sight_offset'] or 'None'}' → '{update_data['sight_offset'] or 'None'}'")
                                if rifle_to_edit["trigger"] != update_data["trigger"]:
                                    changes.append(f"Trigger: '{rifle_to_edit['trigger'] or 'None'}' → '{update_data['trigger'] or 'None'}'")
                                if rifle_to_edit["scope"] != update_data["scope"]:
                                    changes.append(f"Scope: '{rifle_to_edit['scope'] or 'None'}' → '{update_data['scope'] or 'None'}'")
                                
                                if changes:
                                    with st.expander("📝 Changes Made"):
                                        for change in changes:
                                            st.write(f"• {change}")
                                else:
                                    st.info("No changes were made.")

                                del st.session_state.editing_rifle_id
                                st.rerun()
                            else:
                                st.error("❌ Failed to update rifle.")

                        except Exception as e:
                            st.error(f"❌ Error updating rifle: {str(e)}")
            else:
                del st.session_state.editing_rifle_id
                st.rerun()

        # Handle Delete Confirmation
        if hasattr(st.session_state, 'deleting_rifle_id') and st.session_state.deleting_rifle_id:
            # Get the rifle data for deletion
            rifle_to_delete = filtered_df[
                filtered_df["id"] == st.session_state.deleting_rifle_id
            ].iloc[0] if not filtered_df[filtered_df["id"] == st.session_state.deleting_rifle_id].empty else None
            
            if rifle_to_delete is not None:
                st.subheader(f"🗑️ Delete {rifle_to_delete['name']}")
                st.warning("⚠️ This action cannot be undone!")
                st.write(f"Are you sure you want to delete **{rifle_to_delete['name']}** ({rifle_to_delete['cartridge_type']})?")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True):
                        try:
                            # Delete the rifle
                            delete_response = (
                                supabase.table("rifles")
                                .delete()
                                .eq("id", st.session_state.deleting_rifle_id)
                                .eq("user_id", user["id"])  # Extra security check
                                .execute()
                            )

                            if delete_response.data:
                                st.success(f"✅ Deleted: {rifle_to_delete['name']}")
                                del st.session_state.deleting_rifle_id
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete rifle.")
                        except Exception as e:
                            st.error(f"❌ Error deleting rifle: {str(e)}")
                
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        del st.session_state.deleting_rifle_id
                        st.rerun()
            else:
                del st.session_state.deleting_rifle_id
                st.rerun()


    except Exception as e:
        st.error(f"❌ Error loading rifle entries: {str(e)}")
        st.info("Please check your database connection and try again.")
