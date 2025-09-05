import pandas as pd
import streamlit as st

from .service import BulletsService


def render_view_bullets_tab(user, supabase):

    # Clear any existing bullets session state when navigating to page
    if 'bullets' in st.session_state:
        del st.session_state.bullets

    # Initialize service
    bullets_service = BulletsService(supabase)

    try:
        # Get all bullets entries (globally available, admin-maintained)
        bullets = bullets_service.get_all_bullets()

        if not bullets:
            st.info(
                " No bullets available in the database. Please contact an administrator to add bullet specifications."
            )
            return

        # Convert to DataFrame for better display
        bullet_dicts = [bullet.__dict__ for bullet in bullets]
        df = pd.DataFrame(bullet_dicts)

        # Collapsible filters section
        with st.expander("**Filter**", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                manufacturers = ["All"] + \
                    sorted(df["manufacturer"].unique().tolist())
                selected_manufacturer = st.selectbox(
                    "Filter by Manufacturer:", manufacturers
                )

            with col2:
                calibers = ["All"] + \
                    sorted(df["bore_diameter_land_mm"].unique().tolist())
                selected_bore_diameter_mm = st.selectbox(
                    "Filter by Bore Diameter (Caliber):", calibers
                )

            with col3:
                weights = ["All"] + \
                    sorted(df["weight_grains"].unique().tolist())
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
        filtered_bullet_dicts = [
            bullet.__dict__ for bullet in filtered_bullets]
        filtered_df = (pd.DataFrame(filtered_bullet_dicts)
                       if filtered_bullets else pd.DataFrame())

        # Display filtered results count
        if len(filtered_bullets) != len(bullets):
            st.info(
                f"Showing {len(filtered_bullets)} of {len(bullets)} entries")

        if len(filtered_df) == 0:
            st.warning("No entries match the selected filters.")
            return

        # Prepare display DataFrame
        display_df = filtered_df.copy()

        # No date formatting needed since we removed created_at and updated_at

        # Handle nullable fields by filling NaN values and converting to
        # strings
        display_df["weight_grains"] = display_df["weight_grains"].astype(str)
        display_df["bullet_length_mm"] = display_df["bullet_length_mm"].fillna(
            "N/A").astype(str)
        display_df["ballistic_coefficient_g1"] = display_df[
            "ballistic_coefficient_g1"
        ].fillna("N/A").astype(str)
        display_df["ballistic_coefficient_g7"] = display_df[
            "ballistic_coefficient_g7"
        ].fillna("N/A").astype(str)
        display_df["sectional_density"] = display_df["sectional_density"].fillna(
            "N/A").astype(str)
        display_df["min_req_twist_rate_in_per_rev"] = display_df[
            "min_req_twist_rate_in_per_rev"
        ].fillna("N/A").astype(str)
        display_df["pref_twist_rate_in_per_rev"] = display_df[
            "pref_twist_rate_in_per_rev"
        ].fillna("N/A").astype(str)
        display_df["data_source_name"] = display_df["data_source_name"].fillna(
            "N/A").astype(str)
        display_df["data_source_url"] = display_df["data_source_url"].fillna(
            "N/A").astype(str)

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

        # Display the table with enhanced formatting and selection
        selected_bullet_event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "Manufacturer": st.column_config.TextColumn(
                    "Manufacturer", width="small"
                ),
                "Model": st.column_config.TextColumn("Model", width="small"),
                "Weight (gr)": st.column_config.NumberColumn(
                    "Weight (gr)", width="small", format="%.1f"
                ),
                "Diameter (mm)": st.column_config.NumberColumn(
                    "Diameter (mm)", width="small", format="%.3f"
                ),
                "Bore Dia (mm)": st.column_config.NumberColumn(
                    "Bore Dia (mm)", width="small", format="%.3f"
                ),
                "Length (mm)": st.column_config.NumberColumn(
                    "Length (mm)", width="small", format="%.3f"
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

        # Handle bullet selection from table click
        selected_bullet_data = None
        if selected_bullet_event["selection"]["rows"]:
            selected_row_index = selected_bullet_event["selection"]["rows"][0]
            # Get the bullet data from the filtered_bullets using the display
            # index
            selected_bullet_data = filtered_bullets[selected_row_index]

        # Show form/details when a bullet is selected
        if selected_bullet_data is not None:
            # Check if user is admin
            is_admin = (
                user.get("user_metadata", {}).get("is_admin", False)
                or user.get("email") == "johnduffie91@gmail.com"
            )

            if is_admin:
                # Admin sees edit form
                st.markdown(f"**Edit: {selected_bullet_data.display_name}**")

                with st.form(f"edit_bullet_form_{selected_bullet_data.id}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        manufacturer = st.text_input(
                            "Manufacturer/Brand *",
                            value=selected_bullet_data.manufacturer,
                            help="The bullet manufacturer or brand name",
                        )

                        model = st.text_input(
                            "Model/Type *",
                            value=selected_bullet_data.model,
                            help="The specific bullet model or type",
                        )

                        weight_grains = st.number_input(
                            "Weight (grains) *",
                            min_value=1.0,
                            max_value=1000.0,
                            step=1.0,
                            format="%.1f",
                            value=selected_bullet_data.weight_grains,
                            help="The bullet weight in grains",
                        )

                        bullet_diameter_groove_mm = st.number_input(
                            "Bullet Diameter (mm) *",
                            min_value=0.001,
                            max_value=50.0,
                            step=0.001,
                            format="%.3f",
                            value=selected_bullet_data.bullet_diameter_groove_mm,
                            help="The bullet diameter at the groove in millimeters",
                        )

                        bore_diameter_land_mm = st.number_input(
                            "Bore Diameter (mm) *",
                            min_value=0.001,
                            max_value=50.0,
                            step=0.001,
                            format="%.3f",
                            value=selected_bullet_data.bore_diameter_land_mm,
                            help="The bore diameter at the land in millimeters",
                        )

                    with col2:
                        bullet_length_mm = st.number_input(
                            "Bullet Length (mm)",
                            min_value=0.0,
                            max_value=200.0,
                            step=0.1,
                            format="%.1f",
                            value=(
                                selected_bullet_data.bullet_length_mm
                                if selected_bullet_data.bullet_length_mm is not None
                                else 0.0
                            ),
                            help="The bullet length in millimeters (optional)",
                        )

                        ballistic_coefficient_g1 = st.number_input(
                            "Ballistic Coefficient G1",
                            min_value=0.0,
                            max_value=2.0,
                            step=0.001,
                            format="%.3f",
                            value=(
                                selected_bullet_data.ballistic_coefficient_g1
                                if selected_bullet_data.ballistic_coefficient_g1 is not None
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
                                selected_bullet_data.ballistic_coefficient_g7
                                if selected_bullet_data.ballistic_coefficient_g7 is not None
                                else 0.0
                            ),
                            help="The G7 ballistic coefficient (optional)",
                        )

                        sectional_density = st.number_input(
                            "Sectional Density",
                            min_value=0.0,
                            max_value=2.0,
                            step=0.001,
                            format="%.3f",
                            value=(
                                selected_bullet_data.sectional_density
                                if selected_bullet_data.sectional_density is not None
                                else 0.0
                            ),
                            help="The sectional density (weight/diameter²) (optional)",
                        )

                        min_req_twist_rate_in_per_rev = st.number_input(
                            "Min Required Twist Rate (in/rev)",
                            min_value=0,
                            max_value=30,
                            step=1,
                            format="%d",
                            value=(
                                selected_bullet_data.min_req_twist_rate_in_per_rev
                                if selected_bullet_data.min_req_twist_rate_in_per_rev is not None
                                else 0
                            ),
                            help="Minimum required twist rate in inches per revolution (optional)",
                        )

                    col3, col4 = st.columns(2)

                    with col3:
                        pref_twist_rate_in_per_rev = st.number_input(
                            "Preferred Twist Rate (in/rev)",
                            min_value=0,
                            max_value=30,
                            step=1,
                            format="%d",
                            value=(
                                selected_bullet_data.pref_twist_rate_in_per_rev
                                if selected_bullet_data.pref_twist_rate_in_per_rev is not None
                                else 0
                            ),
                            help="Preferred twist rate in inches per revolution (optional)",
                        )

                        data_source_name = st.text_input(
                            "Data Source Name",
                            value=(
                                selected_bullet_data.data_source_name
                                if selected_bullet_data.data_source_name is not None
                                else ""
                            ),
                            help="Name or description of where this data came from (optional)",
                        )

                    with col4:
                        data_source_url = st.text_input(
                            "Data Source URL",
                            value=(
                                selected_bullet_data.data_source_url
                                if selected_bullet_data.data_source_url is not None
                                else ""
                            ),
                            help="URL or reference to the original data source (optional)",
                        )

                    # Form buttons
                    col_save, col_cancel = st.columns([1, 1])
                    with col_save:
                        submitted = st.form_submit_button(
                            "Save Changes", type="primary", use_container_width=True)
                    with col_cancel:
                        cancelled = st.form_submit_button(
                            "Cancel", use_container_width=True)

                    if cancelled:
                        st.rerun()

                    if submitted:
                        # Validate required fields
                        if (
                            not manufacturer
                            or not model
                            or weight_grains == 0.0
                            or bullet_diameter_groove_mm == 0.0
                            or bore_diameter_land_mm == 0.0
                        ):
                            st.error(
                                "Please fill in all required fields (marked with *)")
                        else:
                            try:
                                # Clean up text inputs
                                manufacturer = manufacturer.strip()
                                model = model.strip()
                                data_source_name_cleaned = (
                                    data_source_name.strip() if data_source_name else None)
                                data_source_url_cleaned = (
                                    data_source_url.strip() if data_source_url else None)

                                # Convert zero values to None for optional
                                # fields
                                bullet_length_mm_value = bullet_length_mm if bullet_length_mm > 0 else None
                                ballistic_coefficient_g1_value = ballistic_coefficient_g1 if ballistic_coefficient_g1 > 0 else None
                                ballistic_coefficient_g7_value = ballistic_coefficient_g7 if ballistic_coefficient_g7 > 0 else None
                                sectional_density_value = sectional_density if sectional_density > 0 else None
                                min_req_twist_rate_value = min_req_twist_rate_in_per_rev if min_req_twist_rate_in_per_rev > 0 else None
                                pref_twist_rate_value = pref_twist_rate_in_per_rev if pref_twist_rate_in_per_rev > 0 else None

                                # Convert empty strings to None for data source
                                # fields
                                data_source_name_value = data_source_name_cleaned if data_source_name_cleaned else None
                                data_source_url_value = data_source_url_cleaned if data_source_url_cleaned else None

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
                                    selected_bullet_data.id, update_data
                                )
                                st.success(
                                    f"Successfully updated: {updated_bullet.display_name}")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Error updating bullet: {str(e)}")
            else:
                # Non-admin sees read-only details
                st.markdown(
                    f"**Details: {selected_bullet_data.display_name}**")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Basic Information**")
                    st.write(
                        f"**Manufacturer:** {selected_bullet_data.manufacturer}")
                    st.write(f"**Model:** {selected_bullet_data.model}")
                    st.write(
                        f"**Weight:** {selected_bullet_data.weight_grains:1f} grains")
                    st.write(
                        f"**Bullet Diameter:** {selected_bullet_data.bullet_diameter_groove_mm:.3f} mm")
                    st.write(
                        f"**Bore Diameter:** {selected_bullet_data.bore_diameter_land_mm:.3f} mm")
                    if selected_bullet_data.bullet_length_mm:
                        st.write(
                            f"**Length:** {selected_bullet_data.bullet_length_mm:.1f} mm")

                with col2:
                    st.markdown("**Ballistic Properties**")
                    if selected_bullet_data.ballistic_coefficient_g1:
                        st.write(
                            f"**BC G1:** {selected_bullet_data.ballistic_coefficient_g1:.3f}")
                    else:
                        st.write("**BC G1:** N/A")
                    if selected_bullet_data.ballistic_coefficient_g7:
                        st.write(
                            f"**BC G7:** {selected_bullet_data.ballistic_coefficient_g7:.3f}")
                    else:
                        st.write("**BC G7:** N/A")
                    if selected_bullet_data.sectional_density:
                        st.write(
                            f"**Sectional Density:** {selected_bullet_data.sectional_density:.3f}")
                    else:
                        st.write("**Sectional Density:** N/A")

                with col3:
                    st.markdown("**Twist Rate Requirements**")
                    if selected_bullet_data.min_req_twist_rate_in_per_rev:
                        st.write(
                            f"**Min Required:** {selected_bullet_data.min_req_twist_rate_in_per_rev:.1f} in/rev")
                    else:
                        st.write("**Min Required:** N/A")
                    if selected_bullet_data.pref_twist_rate_in_per_rev:
                        st.write(
                            f"**Preferred:** {selected_bullet_data.pref_twist_rate_in_per_rev:.1f} in/rev")
                    else:
                        st.write("**Preferred:** N/A")
                    if selected_bullet_data.data_source_name:
                        st.write(
                            f"**Data Source:** {selected_bullet_data.data_source_name}")
                    if selected_bullet_data.data_source_url:
                        st.write(
                            f"**Source URL:** [Link]({selected_bullet_data.data_source_url})")

        else:
            st.info(
                "Click on a bullet in the table above to view details" + (
                    " or edit (admins)" if user.get(
                        "user_metadata",
                        {}).get(
                        "is_admin",
                        False) or user.get("email") == "johnduffie91@gmail.com" else ""))

    except Exception as e:
        st.error(f"Error loading bullets entries: {str(e)}")
        st.info("Please check your database connection and try again.")
