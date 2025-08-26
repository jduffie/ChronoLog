import pandas as pd
import streamlit as st

from .models import BulletModel
from .service import BulletsService


def render_view_bullets_tab(user, supabase):

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
            unique_weights = df["weight_grains"].nunique()
            st.metric("Weight Variants", unique_weights)

        # Collapsible filters section
        with st.expander("Filter Options", expanded=False):
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

        # Handle bullet selection from table click
        selected_bullet_data = None
        if selected_bullet_event["selection"]["rows"]:
            selected_row_index = selected_bullet_event["selection"]["rows"][0]
            # Get the bullet data from the filtered_bullets using the display index
            selected_bullet_data = filtered_bullets[selected_row_index]

        # Show detailed view if a bullet is selected
        if selected_bullet_data is not None:
            st.markdown(f"**Details: {selected_bullet_data.display_name}**")
            
            # Display detailed information in columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Basic Information**")
                st.write(f"**Manufacturer:** {selected_bullet_data.manufacturer}")
                st.write(f"**Model:** {selected_bullet_data.model}")
                st.write(f"**Weight:** {selected_bullet_data.weight_grains} grains")
                st.write(f"**Bullet Diameter:** {selected_bullet_data.bullet_diameter_groove_mm:.3f} mm")
                st.write(f"**Bore Diameter:** {selected_bullet_data.bore_diameter_land_mm:.3f} mm")
                if selected_bullet_data.bullet_length_mm:
                    st.write(f"**Length:** {selected_bullet_data.bullet_length_mm:.1f} mm")

            with col2:
                st.markdown("**Ballistic Properties**")
                if selected_bullet_data.ballistic_coefficient_g1:
                    st.write(f"**BC G1:** {selected_bullet_data.ballistic_coefficient_g1:.3f}")
                else:
                    st.write("**BC G1:** N/A")
                if selected_bullet_data.ballistic_coefficient_g7:
                    st.write(f"**BC G7:** {selected_bullet_data.ballistic_coefficient_g7:.3f}")
                else:
                    st.write("**BC G7:** N/A")
                if selected_bullet_data.sectional_density:
                    st.write(f"**Sectional Density:** {selected_bullet_data.sectional_density:.3f}")
                else:
                    st.write("**Sectional Density:** N/A")

            with col3:
                st.markdown("**Twist Rate Requirements**")
                if selected_bullet_data.min_req_twist_rate_in_per_rev:
                    st.write(f"**Min Required:** {selected_bullet_data.min_req_twist_rate_in_per_rev:.1f} in/rev")
                else:
                    st.write("**Min Required:** N/A")
                if selected_bullet_data.pref_twist_rate_in_per_rev:
                    st.write(f"**Preferred:** {selected_bullet_data.pref_twist_rate_in_per_rev:.1f} in/rev")
                else:
                    st.write("**Preferred:** N/A")
                if selected_bullet_data.data_source_name:
                    st.write(f"**Data Source:** {selected_bullet_data.data_source_name}")
                if selected_bullet_data.data_source_url:
                    st.write(f"**Source URL:** [Link]({selected_bullet_data.data_source_url})")
        
        else:
            st.info("Click on a bullet in the table above to view detailed information")


    except Exception as e:
        st.error(f"❌ Error loading bullets entries: {str(e)}")
        st.info("Please check your database connection and try again.")
