from datetime import datetime, timezone

import streamlit as st


def render_create_bullets_tab(user, supabase):
    """Render the Create Bullets tab"""
    st.header("➕ Create New Bullets Entry")

    # Create form for bullets entry
    with st.form("create_bullets_form"):
        st.subheader("📋 Basic Information")
        col1, col2 = st.columns(2)

        with col1:
            manufacturer = st.text_input(
                "Manufacturer/Brand *",
                placeholder="e.g., Hornady, Federal, Winchester",
                help="The bullet manufacturer or brand name",
            )

            model = st.text_input(
                "Model/Type *",
                placeholder="e.g., ELD-M, Gold Medal, Ballistic Tip",
                help="The specific bullet model or type",
            )

            weight_grains = st.number_input(
                "Weight (grains) *",
                min_value=1,
                max_value=1000,
                step=1,
                help="The bullet weight in grains",
            )

        with col2:
            bullet_diameter_groove_mm = st.number_input(
                "Bullet Diameter (mm) *",
                min_value=0.001,
                max_value=50.0,
                step=0.001,
                format="%.3f",
                help="The bullet diameter at the groove in millimeters",
            )

            bore_diameter_land_mm = st.number_input(
                "Bore Diameter (mm) *",
                min_value=0.001,
                max_value=50.0,
                step=0.001,
                format="%.3f",
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
                value=0.0,
                help="The bullet length in millimeters (optional)",
            )

            sectional_density = st.number_input(
                "Sectional Density",
                min_value=0.0,
                max_value=2.0,
                step=0.001,
                format="%.3f",
                value=0.0,
                help="The sectional density (weight/diameter²) (optional)",
            )

        with col4:
            ballistic_coefficient_g1 = st.number_input(
                "Ballistic Coefficient G1",
                min_value=0.0,
                max_value=2.0,
                step=0.001,
                format="%.3f",
                value=0.0,
                help="The G1 ballistic coefficient (optional)",
            )

            ballistic_coefficient_g7 = st.number_input(
                "Ballistic Coefficient G7",
                min_value=0.0,
                max_value=2.0,
                step=0.001,
                format="%.3f",
                value=0.0,
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
                value=0.0,
                help="Minimum required twist rate in inches per revolution (optional)",
            )

        with col6:
            pref_twist_rate_in_per_rev = st.number_input(
                "Preferred Twist Rate (in/rev)",
                min_value=0.0,
                max_value=50.0,
                step=0.1,
                format="%.1f",
                value=0.0,
                help="Preferred twist rate in inches per revolution (optional)",
            )

        # Submit button
        submitted = st.form_submit_button("💾 Create Bullets Entry", type="primary")

        if submitted:
            # Validate required fields
            if not manufacturer or not model or weight_grains == 0 or bullet_diameter_groove_mm == 0.0 or bore_diameter_land_mm == 0.0:
                st.error("❌ Please fill in all required fields (marked with *)")
                return

            # Clean up text inputs
            manufacturer = manufacturer.strip()
            model = model.strip()
            
            # Convert zero values to None for optional fields
            bullet_length_mm_value = bullet_length_mm if bullet_length_mm > 0 else None
            ballistic_coefficient_g1_value = ballistic_coefficient_g1 if ballistic_coefficient_g1 > 0 else None
            ballistic_coefficient_g7_value = ballistic_coefficient_g7 if ballistic_coefficient_g7 > 0 else None
            sectional_density_value = sectional_density if sectional_density > 0 else None
            min_req_twist_rate_value = min_req_twist_rate_in_per_rev if min_req_twist_rate_in_per_rev > 0 else None
            pref_twist_rate_value = pref_twist_rate_in_per_rev if pref_twist_rate_in_per_rev > 0 else None

            try:
                # Create bullets entry
                bullets_data = {
                    "user_id": user["id"],
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
                }

                # Insert into database
                response = supabase.table("bullets").insert(bullets_data).execute()

                if response.data:
                    st.success(f"✅ Bullet entry created successfully!")
                    st.info(f"📋 **{manufacturer} {model}** - {weight_grains}gr - {bullet_diameter_groove_mm}mm")

                    # Clear form by rerunning (this will reset the form)
                    st.rerun()
                else:
                    st.error("❌ Failed to create bullet entry. Please try again.")

            except Exception as e:
                if "duplicate key value violates unique constraint" in str(e):
                    st.error(
                        "❌ This bullets entry already exists. Please check your entries."
                    )
                else:
                    st.error(f"❌ Error creating bullets entry: {str(e)}")

    # Display helpful information
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown(
        """
    - **Manufacturer/Brand**: The company that makes the bullets (e.g., Hornady, Federal, Winchester)
    - **Model/Type**: The specific product line or bullet type (e.g., ELD-M, Gold Medal, Ballistic Tip)
    - **Weight**: The bullet weight in grains (e.g., 147, 168, 55)
    - **Bullet Diameter**: The diameter of the bullet at the groove in mm (e.g., 6.5mm = 0.264, .308 = 7.82mm)
    - **Bore Diameter**: The diameter of the bore at the land in mm (slightly smaller than bullet diameter)
    - **Optional Fields**: Leave at 0 if unknown - they will be stored as null in the database
    """
    )

    st.markdown("### 📝 Examples")
    examples = [
        {
            "manufacturer": "Hornady",
            "model": "ELD-M",
            "weight": "147gr",
            "diameter": "6.50mm",
            "bc_g1": "0.697"
        },
        {
            "manufacturer": "Federal",
            "model": "Gold Medal",
            "weight": "168gr",
            "diameter": "7.82mm (.308)",
            "bc_g1": "0.465"
        },
        {
            "manufacturer": "Sierra",
            "model": "MatchKing",
            "weight": "77gr",
            "diameter": "5.70mm (.224)",
            "bc_g1": "0.372"
        },
    ]

    for example in examples:
        st.markdown(
            f"- **{example['manufacturer']} {example['model']}** - {example['weight']} - {example['diameter']} - BC G1: {example['bc_g1']}"
        )
