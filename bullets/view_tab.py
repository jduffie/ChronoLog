import pandas as pd
import streamlit as st

from .models import BulletModel
from .service import BulletsService


def render_view_bullets_tab(user, supabase):
    """Render the View Bullets tab"""
    st.header(" View Bullets Entries")

    # Initialize service
    bullets_service = BulletsService(supabase)

    try:
        # Get all bullets entries (globally available, admin-maintained)
        bullets = bullets_service.get_all_bullets()

        if not bullets:
            st.info(
                "📭 No bullets available in the database. Please contact an administrator to add bullet specifications."
            )
            return

        # Convert to DataFrame for better display
        bullet_dicts = [bullet.__dict__ for bullet in bullets]
        df = pd.DataFrame(bullet_dicts)

        # Display summary stats
        st.subheader(" Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Entries", len(df))

        with col2:
            unique_manufacturers = df["manufacturer"].nunique()
            st.metric("Manufacturers", unique_manufacturers)

        with col3:
            unique_calibers = df["bullet_diameter_groove_mm"].nunique()
            st.metric("Calibers", unique_calibers)

        # Add filters
        st.subheader(" Filter Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            manufacturers = ["All"] + sorted(df["manufacturer"].unique().tolist())
            selected_manufacturer = st.selectbox(
                "Filter by Manufacturer:", manufacturers
            )

        with col2:
            calibers = ["All"] + sorted(df["bore_diameter_land_mm"].unique().tolist())
            selected_bore_diameter_mm = st.selectbox(
                "Filter by Bore Diameter:", calibers
            )

        with col3:
            weights = ["All"] + sorted(df["weight_grains"].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight:", weights)

        # Apply filters using service
        if (
            selected_manufacturer == "All"
            and selected_bore_diameter_mm == "All"
            and selected_weight == "All"
        ):
            filtered_bullets = bullets
        else:
            filtered_bullets = bullets_service.filter_bullets(
                manufacturer=(
                    selected_manufacturer if selected_manufacturer != "All" else None
                ),
                bore_diameter_mm=(
                    selected_bore_diameter_mm
                    if selected_bore_diameter_mm != "All"
                    else None
                ),
                weight_grains=selected_weight if selected_weight != "All" else None,
            )

        # Convert filtered results to DataFrame
        filtered_bullet_dicts = [bullet.__dict__ for bullet in filtered_bullets]
        filtered_df = (
            pd.DataFrame(filtered_bullet_dicts) if filtered_bullets else pd.DataFrame()
        )

        # Display filtered results count
        if len(filtered_bullets) != len(bullets):
            st.info(f"Showing {len(filtered_bullets)} of {len(bullets)} entries")

        # Display the table
        st.subheader(" Bullets Entries")

        if len(filtered_df) == 0:
            st.warning("No entries match the selected filters.")
            return

        # Prepare display DataFrame
        display_df = filtered_df.copy()

        # No date formatting needed since we removed created_at and updated_at

        # Handle nullable fields by filling NaN values
        display_df["bullet_length_mm"] = display_df["bullet_length_mm"].fillna("N/A")
        display_df["ballistic_coefficient_g1"] = display_df[
            "ballistic_coefficient_g1"
        ].fillna("N/A")
        display_df["ballistic_coefficient_g7"] = display_df[
            "ballistic_coefficient_g7"
        ].fillna("N/A")
        display_df["sectional_density"] = display_df["sectional_density"].fillna("N/A")
        display_df["min_req_twist_rate_in_per_rev"] = display_df[
            "min_req_twist_rate_in_per_rev"
        ].fillna("N/A")
        display_df["pref_twist_rate_in_per_rev"] = display_df[
            "pref_twist_rate_in_per_rev"
        ].fillna("N/A")
        display_df["data_source_name"] = display_df["data_source_name"].fillna("N/A")
        display_df["data_source_url"] = display_df["data_source_url"].fillna("N/A")

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
                "pref_twist_rate_in_per_rev",
                "data_source_name",
                "data_source_url",
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
                "pref_twist_rate_in_per_rev": "Pref Twist Rate",
                "data_source_name": "Data Source",
                "data_source_url": "Source URL",
            }
        )

        # Display the table with enhanced formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Manufacturer": st.column_config.TextColumn(
                    "Manufacturer", width="small"
                ),
                "Model": st.column_config.TextColumn("Model", width="small"),
                "Weight (gr)": st.column_config.NumberColumn(
                    "Weight (gr)", width="small"
                ),
                "Diameter (mm)": st.column_config.NumberColumn(
                    "Diameter (mm)", width="small", format="%.3f"
                ),
                "Bore Dia (mm)": st.column_config.NumberColumn(
                    "Bore Dia (mm)", width="small", format="%.3f"
                ),
                "Length (mm)": st.column_config.TextColumn(
                    "Length (mm)", width="small"
                ),
                "BC G1": st.column_config.TextColumn("BC G1", width="small"),
                "BC G7": st.column_config.TextColumn("BC G7", width="small"),
                "Sectional Density": st.column_config.TextColumn(
                    "Sectional Density", width="small"
                ),
                "Min Twist Rate": st.column_config.TextColumn(
                    "Min Twist Rate", width="small"
                ),
                "Pref Twist Rate": st.column_config.TextColumn(
                    "Pref Twist Rate", width="small"
                ),
                "Data Source": st.column_config.TextColumn(
                    "Data Source", width="medium"
                ),
                "Source URL": st.column_config.LinkColumn("Source URL", width="medium"),
            },
        )

        # Admin-only functionality
        is_admin = (
            user.get("user_metadata", {}).get("is_admin", False)
            or user.get("email") == "johnduffie91@gmail.com"
        )

        if is_admin:
            # Edit functionality (admin only)
            st.subheader("✏ Edit Entry (Admin Only)")
            with st.expander("Edit a bullet entry"):
                # Create list of entries for editing
                entry_options = []
                for bullet in filtered_bullets:
                    entry_options.append((bullet.display_name, bullet))

                if entry_options:
                    selected_entry = st.selectbox(
                        "Select entry to edit:",
                        options=[None] + entry_options,
                        format_func=lambda x: (
                            "Select an entry..." if x is None else x[0]
                        ),
                        key="edit_selector",
                    )

                    if selected_entry:
                        bullet_model = selected_entry[1]

                        # Create edit form
                        with st.form("edit_bullet_form"):
                            st.subheader(" Edit Basic Information")
                            col1, col2 = st.columns(2)

                            with col1:
                                manufacturer = st.text_input(
                                    "Manufacturer/Brand *",
                                    value=bullet_model.manufacturer,
                                    help="The bullet manufacturer or brand name",
                                )

                                model = st.text_input(
                                    "Model/Type *",
                                    value=bullet_model.model,
                                    help="The specific bullet model or type",
                                )

                                weight_grains = st.number_input(
                                    "Weight (grains) *",
                                    min_value=1,
                                    max_value=1000,
                                    step=1,
                                    value=bullet_model.weight_grains,
                                    help="The bullet weight in grains",
                                )

                            with col2:
                                bullet_diameter_groove_mm = st.number_input(
                                    "Bullet Diameter (mm) *",
                                    min_value=0.001,
                                    max_value=50.0,
                                    step=0.001,
                                    format="%.3f",
                                    value=bullet_model.bullet_diameter_groove_mm,
                                    help="The bullet diameter at the groove in millimeters",
                                )

                                bore_diameter_land_mm = st.number_input(
                                    "Bore Diameter (mm) *",
                                    min_value=0.001,
                                    max_value=50.0,
                                    step=0.001,
                                    format="%.3f",
                                    value=bullet_model.bore_diameter_land_mm,
                                    help="The bore diameter at the land in millimeters",
                                )

                            st.subheader("📐 Physical Properties (Optional)")
                            col3, col4 = st.columns(2)

                            with col3:
                                bullet_length_mm = st.number_input(
                                    "Bullet Length (mm)",
                                    min_value=0.0,
                                    max_value=200.0,
                                    step=0.1,
                                    format="%.1f",
                                    value=(
                                        bullet_model.bullet_length_mm
                                        if bullet_model.bullet_length_mm is not None
                                        else 0.0
                                    ),
                                    help="The bullet length in millimeters (optional)",
                                )

                                sectional_density = st.number_input(
                                    "Sectional Density",
                                    min_value=0.0,
                                    max_value=2.0,
                                    step=0.001,
                                    format="%.3f",
                                    value=(
                                        bullet_model.sectional_density
                                        if bullet_model.sectional_density is not None
                                        else 0.0
                                    ),
                                    help="The sectional density (weight/diameter²) (optional)",
                                )

                            with col4:
                                ballistic_coefficient_g1 = st.number_input(
                                    "Ballistic Coefficient G1",
                                    min_value=0.0,
                                    max_value=2.0,
                                    step=0.001,
                                    format="%.3f",
                                    value=(
                                        bullet_model.ballistic_coefficient_g1
                                        if bullet_model.ballistic_coefficient_g1
                                        is not None
                                        else 0.0
                                    ),
                                    help="The G1 ballistic coefficient (optional)",
                                )

                                ballistic_coefficient_g7 = st.number_input(
                                    "Ballistic Coefficient G7",
                                    min_value=0.0,
                                    max_value=2.0,
                                    step=0.001,
                                    format="%.3f",
                                    value=(
                                        bullet_model.ballistic_coefficient_g7
                                        if bullet_model.ballistic_coefficient_g7
                                        is not None
                                        else 0.0
                                    ),
                                    help="The G7 ballistic coefficient (optional)",
                                )

                            st.subheader("🌪️ Twist Rate Requirements (Optional)")
                            col5, col6 = st.columns(2)

                            with col5:
                                min_req_twist_rate_in_per_rev = st.number_input(
                                    "Minimum Required Twist Rate (in/rev)",
                                    min_value=0.0,
                                    max_value=50.0,
                                    step=0.1,
                                    format="%.1f",
                                    value=(
                                        bullet_model.min_req_twist_rate_in_per_rev
                                        if bullet_model.min_req_twist_rate_in_per_rev
                                        is not None
                                        else 0.0
                                    ),
                                    help="Minimum required twist rate in inches per revolution (optional)",
                                )

                            with col6:
                                pref_twist_rate_in_per_rev = st.number_input(
                                    "Preferred Twist Rate (in/rev)",
                                    min_value=0.0,
                                    max_value=50.0,
                                    step=0.1,
                                    format="%.1f",
                                    value=(
                                        bullet_model.pref_twist_rate_in_per_rev
                                        if bullet_model.pref_twist_rate_in_per_rev
                                        is not None
                                        else 0.0
                                    ),
                                    help="Preferred twist rate in inches per revolution (optional)",
                                )

                            st.subheader("📄 Data Source (Optional)")
                            col7, col8 = st.columns(2)

                            with col7:
                                data_source_name = st.text_input(
                                    "Data Source Name",
                                    value=(
                                        bullet_model.data_source_name
                                        if bullet_model.data_source_name is not None
                                        else ""
                                    ),
                                    help="Name or description of where this data came from (optional)",
                                )

                            with col8:
                                data_source_url = st.text_input(
                                    "Data Source URL",
                                    value=(
                                        bullet_model.data_source_url
                                        if bullet_model.data_source_url is not None
                                        else ""
                                    ),
                                    help="URL or reference to the original data source (optional)",
                                )

                            # Submit button
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                submitted = st.form_submit_button(
                                    " Save Changes", type="primary"
                                )

                            if submitted:
                                # Validate required fields
                                if (
                                    not manufacturer
                                    or not model
                                    or weight_grains == 0
                                    or bullet_diameter_groove_mm == 0.0
                                    or bore_diameter_land_mm == 0.0
                                ):
                                    st.error(
                                        "❌ Please fill in all required fields (marked with *)"
                                    )
                                else:
                                    # Clean up text inputs
                                    manufacturer = manufacturer.strip()
                                    model = model.strip()
                                    data_source_name_cleaned = (
                                        data_source_name.strip()
                                        if data_source_name
                                        else None
                                    )
                                    data_source_url_cleaned = (
                                        data_source_url.strip()
                                        if data_source_url
                                        else None
                                    )

                                    # Convert zero values to None for optional fields
                                    bullet_length_mm_value = (
                                        bullet_length_mm
                                        if bullet_length_mm > 0
                                        else None
                                    )
                                    ballistic_coefficient_g1_value = (
                                        ballistic_coefficient_g1
                                        if ballistic_coefficient_g1 > 0
                                        else None
                                    )
                                    ballistic_coefficient_g7_value = (
                                        ballistic_coefficient_g7
                                        if ballistic_coefficient_g7 > 0
                                        else None
                                    )
                                    sectional_density_value = (
                                        sectional_density
                                        if sectional_density > 0
                                        else None
                                    )
                                    min_req_twist_rate_value = (
                                        min_req_twist_rate_in_per_rev
                                        if min_req_twist_rate_in_per_rev > 0
                                        else None
                                    )
                                    pref_twist_rate_value = (
                                        pref_twist_rate_in_per_rev
                                        if pref_twist_rate_in_per_rev > 0
                                        else None
                                    )

                                    # Convert empty strings to None for data source fields
                                    data_source_name_value = (
                                        data_source_name_cleaned
                                        if data_source_name_cleaned
                                        else None
                                    )
                                    data_source_url_value = (
                                        data_source_url_cleaned
                                        if data_source_url_cleaned
                                        else None
                                    )

                                    try:
                                        # Update the entry
                                        update_data = {
                                            "manufacturer": manufacturer,
                                            "model": model,
                                            "weight_grains": weight_grains,
                                            "bullet_diameter_groove_mm": bullet_diameter_groove_mm,
                                            "bore_diameter_land_mm": bore_diameter_land_mm,
                                            "bullet_length_mm": bullet_length_mm_value,
                                            "ballistic_coefficient_g1": ballistic_coefficient_g1_value,
                                            "ballistic_coefficient_g7": ballistic_coefficient_g7_value,
                                            "sectional_density": sectional_density_value,
                                            "min_req_twist_rate_in_per_rev": min_req_twist_rate_value,
                                            "pref_twist_rate_in_per_rev": pref_twist_rate_value,
                                            "data_source_name": data_source_name_value,
                                            "data_source_url": data_source_url_value,
                                        }

                                        updated_bullet = bullets_service.update_bullet(
                                            bullet_model.id, update_data
                                        )
                                        st.success(
                                            f"✅ Updated: {updated_bullet.display_name}"
                                        )
                                        st.rerun()

                                    except Exception as e:
                                        st.error(f"❌ Error updating entry: {str(e)}")
                else:
                    st.info("No entries available for editing with current filters.")

            # Delete functionality (admin only)
            st.subheader("🗑️ Delete Entry (Admin Only)")
            with st.expander("Delete a bullet entry"):
                st.warning("⚠️ This action cannot be undone!")

                # Create list of entries for deletion
                entry_options = []
                for bullet in filtered_bullets:
                    entry_options.append((bullet.display_name, bullet.id))

                if entry_options:
                    selected_entry = st.selectbox(
                        "Select entry to delete:",
                        options=[None] + entry_options,
                        format_func=lambda x: (
                            "Select an entry..." if x is None else x[0]
                        ),
                        key="delete_selector",
                    )

                    if selected_entry:
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if st.button("🗑️ Delete", type="secondary"):
                                try:
                                    # Delete the entry
                                    if bullets_service.delete_bullet(selected_entry[1]):
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
            st.info(
                "ℹ️ This is a read-only view of the global bullet database maintained by administrators."
            )

    except Exception as e:
        st.error(f"❌ Error loading bullets entries: {str(e)}")
        st.info("Please check your database connection and try again.")
