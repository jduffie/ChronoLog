from datetime import datetime

import pandas as pd
import streamlit as st


def render_view_cartridge_tab(user, supabase):
    """Render the View Cartridges tab"""
    st.header("📋 View Cartridge Details")

    try:
        # First, let's check what columns actually exist in the view
        test_response = (
            supabase.table("cartridge_details")
            .select("*")
            .limit(1)
            .execute()
        )
        
        if test_response.data:
            available_columns = list(test_response.data[0].keys())
            st.info(f"Available columns: {', '.join(available_columns)}")
        
        # Get all cartridge details for the user from the cartridge_details view
        response = (
            supabase.table("cartridge_details")
            .select("*")
            .eq("user_id", user["id"])
            .execute()
        )

        if not response.data:
            st.info(
                "📭 No cartridge entries found. Create factory cartridges or custom cartridges to see them here."
            )
            return

        # Convert to DataFrame for better display
        df = pd.DataFrame(response.data)

        # Display summary stats
        st.subheader("📊 Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Cartridges", len(df))

        with col2:
            unique_cartridge_types = df["cartridge_type"].nunique() if "cartridge_type" in df.columns else 0
            st.metric("Cartridge Types", unique_cartridge_types)

        with col3:
            unique_manufacturers = df["manufacturer"].dropna().nunique() if "manufacturer" in df.columns else 0
            st.metric("Manufacturers", unique_manufacturers)

        with col4:
            factory_count = len(df[df["source"] == "factory"]) if "source" in df.columns else 0
            custom_count = len(df[df["source"] == "custom"]) if "source" in df.columns else 0
            st.metric("Factory/Custom", f"{factory_count}/{custom_count}")

        # Add filters
        st.subheader("🔍 Filter Options")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            sources = ["All"] + sorted(df["source"].unique().tolist()) if "source" in df.columns else ["All"]
            selected_source = st.selectbox("Filter by Source:", sources)

        with col2:
            manufacturers = ["All"] + sorted(df["manufacturer"].dropna().unique().tolist()) if "manufacturer" in df.columns else ["All"]
            selected_manufacturer = st.selectbox("Filter by Manufacturer:", manufacturers)

        with col3:
            cartridge_types = ["All"] + sorted(df["cartridge_type"].dropna().unique().tolist()) if "cartridge_type" in df.columns else ["All"]
            selected_cartridge_type = st.selectbox("Filter by Cartridge Type:", cartridge_types)

        with col4:
            bullet_weights = ["All"] + sorted(df["bullet_weight_grains"].dropna().unique().tolist()) if "bullet_weight_grains" in df.columns else ["All"]
            selected_bullet_weight = st.selectbox("Filter by Bullet Weight:", bullet_weights)

        # Apply filters
        filtered_df = df.copy()
        if selected_source != "All" and "source" in df.columns:
            filtered_df = filtered_df[filtered_df["source"] == selected_source]
        if selected_manufacturer != "All" and "manufacturer" in df.columns:
            filtered_df = filtered_df[filtered_df["manufacturer"] == selected_manufacturer]
        if selected_cartridge_type != "All" and "cartridge_type" in df.columns:
            filtered_df = filtered_df[filtered_df["cartridge_type"] == selected_cartridge_type]
        if selected_bullet_weight != "All" and "bullet_weight_grains" in df.columns:
            filtered_df = filtered_df[filtered_df["bullet_weight_grains"] == selected_bullet_weight]

        # Display filtered results count
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df)} of {len(df)} entries")

        # Display the table
        st.subheader("🎯 Cartridge Details")

        if len(filtered_df) == 0:
            st.warning("No entries match the selected filters.")
            return

        # Prepare display DataFrame
        display_df = filtered_df.copy()

        # Handle nullable fields by filling NaN values
        for col in ["manufacturer", "model", "bullet_manufacturer", "bullet_model", "bullet_weight_grains", 
                   "bullet_diameter_groove_mm", "bore_diameter_land_mm", "bullet_length_mm", "ballistic_coefficient_g1", 
                   "ballistic_coefficient_g7", "sectional_density", "min_req_twist_rate_in_per_rev", "pref_twist_rate_in_per_rev"]:
            if col in display_df.columns:
                display_df[col] = display_df[col].fillna("N/A")

        # Show all available fields from the new view schema
        available_cols = [
            "source", "manufacturer", "cartridge_type", "model", "bullet_name", "bullet_manufacturer", "bullet_model", 
            "bullet_weight_grains", "bullet_diameter_groove_mm", "bore_diameter_land_mm", "bullet_length_mm",
            "ballistic_coefficient_g1", "ballistic_coefficient_g7", "sectional_density",
            "min_req_twist_rate_in_per_rev", "pref_twist_rate_in_per_rev"
        ]
        
        # Only include columns that exist in the DataFrame
        display_cols = [col for col in available_cols if col in display_df.columns]
        
        display_df = display_df[display_cols].rename(
            columns={
                "source": "Source",
                "manufacturer": "Manufacturer",
                "cartridge_type": "Cartridge Type",
                "model": "Model",
                "bullet_name": "Bullet",
                "bullet_manufacturer": "Bullet Make",
                "bullet_model": "Bullet Model",
                "bullet_weight_grains": "Weight (gr)",
                "bullet_diameter_groove_mm": "Bullet Dia (mm)",
                "bore_diameter_land_mm": "Bore Dia (mm)",
                "bullet_length_mm": "Length (mm)",
                "ballistic_coefficient_g1": "BC G1",
                "ballistic_coefficient_g7": "BC G7",
                "sectional_density": "Sect. Density",
                "min_req_twist_rate_in_per_rev": "Min Twist",
                "pref_twist_rate_in_per_rev": "Pref Twist"
            }
        )

        # Display the table with enhanced formatting
        column_config = {}
        for col in display_df.columns:
            if col in ["Weight (gr)", "Bullet Dia (mm)", "Bore Dia (mm)", "Length (mm)", "BC G1", "BC G7", "Sect. Density", "Min Twist", "Pref Twist"]:
                column_config[col] = st.column_config.TextColumn(col, width="small")
            elif col in ["Cartridge Type", "Model", "Bullet", "Bullet Make", "Bullet Model"]:
                column_config[col] = st.column_config.TextColumn(col, width="medium")
            else:
                column_config[col] = st.column_config.TextColumn(col, width="small")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
        )

        # Export option
        st.subheader("📤 Export")
        if st.button("📥 Download as CSV"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"cartridge_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

        # Display additional details section
        st.subheader("📄 Additional Details")
        with st.expander("View detailed information for selected cartridges"):
            if len(filtered_df) > 0:
                # Create a selectbox for detailed view
                detail_options = []
                detail_lookup = {}
                
                for _, row in filtered_df.iterrows():
                    source = row.get('source', 'N/A')
                    manufacturer = row.get('manufacturer', 'N/A')
                    cartridge_type = row.get('cartridge_type', 'N/A')
                    model = row.get('model', 'N/A')
                    bullet_name = row.get('bullet_name', 'N/A')
                    label = f"{source.title()}: {manufacturer} {cartridge_type} {model} - {bullet_name}"
                    detail_options.append(label)
                    detail_lookup[label] = row

                selected_detail = st.selectbox(
                    "Select cartridge for detailed view:",
                    options=[None] + detail_options,
                    format_func=lambda x: "Select a cartridge..." if x is None else x,
                )

                if selected_detail:
                    row = detail_lookup[selected_detail]
                    
                    # Display detailed information in columns
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Cartridge Info**")
                        st.write(f"**Spec ID:** {row.get('spec_id', 'N/A')}")
                        st.write(f"**Source:** {row.get('source', 'N/A').title()}")
                        st.write(f"**Manufacturer:** {row.get('manufacturer', 'N/A')}")
                        st.write(f"**Cartridge Type:** {row.get('cartridge_type', 'N/A')}")
                        st.write(f"**Model:** {row.get('model', 'N/A')}")
                        
                    with col2:
                        st.markdown("**Bullet Info**")
                        st.write(f"**Bullet ID:** {row.get('bullet_id', 'N/A')}")
                        st.write(f"**Description:** {row.get('bullet_name', 'N/A')}")
                        st.write(f"**Manufacturer:** {row.get('bullet_manufacturer', 'N/A')}")
                        st.write(f"**Model:** {row.get('bullet_model', 'N/A')}")
                        st.write(f"**Weight:** {row.get('bullet_weight_grains', 'N/A')} gr")
                        st.write(f"**Diameter:** {row.get('bullet_diameter_groove_mm', 'N/A')} mm")
                        st.write(f"**Bore Diameter:** {row.get('bore_diameter_land_mm', 'N/A')} mm")
                        if row.get('bullet_length_mm'):
                            st.write(f"**Length:** {row['bullet_length_mm']} mm")
                        
                    with col3:
                        st.markdown("**Ballistic Properties**")
                        if row.get('ballistic_coefficient_g1'):
                            st.write(f"**BC G1:** {row['ballistic_coefficient_g1']}")
                        if row.get('ballistic_coefficient_g7'):
                            st.write(f"**BC G7:** {row['ballistic_coefficient_g7']}")
                        if row.get('sectional_density'):
                            st.write(f"**Sectional Density:** {row['sectional_density']}")
                        if row.get('min_req_twist_rate_in_per_rev'):
                            st.write(f"**Min Twist Rate:** {row['min_req_twist_rate_in_per_rev']} in/rev")
                        if row.get('pref_twist_rate_in_per_rev'):
                            st.write(f"**Pref Twist Rate:** {row['pref_twist_rate_in_per_rev']} in/rev")
                    
                    # No lot information or notes in the simplified view

    except Exception as e:
        st.error(f"❌ Error loading cartridge details: {str(e)}")
        st.info("Please check your database connection and ensure the cartridge_details view exists.")