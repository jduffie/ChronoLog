import uuid
from datetime import datetime, timezone

import streamlit as st


def render_create_bullets_tab(user, supabase):
    """Render the Create Bullets tab"""
    st.header("➕ Create New Bullets Entry")

    # Create form for bullets entry
    with st.form("create_bullets_form"):
        col1, col2 = st.columns(2)

        with col1:
            manufacturer = st.text_input(
                "Manufacturer/Brand *",
                placeholder="e.g., Hornady, Federal, Winchester",
                help="The bullets manufacturer or brand name",
            )

            model = st.text_input(
                "Model/Type *",
                placeholder="e.g., ELD-M, Gold Medal, Ballistic Tip",
                help="The specific bullets model or type",
            )

        with col2:
            bullet_length_mm = st.text_input(
                "Caliber *",
                placeholder="e.g., 6.5 Creedmoor, .308 Win, .223 Rem",
                help="The bullets bullet_length_mm",
            )

            weight_grains = st.text_input(
                "Weight *",
                placeholder="e.g., 147gr, 168gr, 55gr",
                help="The bullet weight_grains (include 'gr' suffix)",
            )

        # Submit button
        submitted = st.form_submit_button("💾 Create Bullets Entry", type="primary")

        if submitted:
            # Validate required fields
            if not manufacturer or not model or not bullet_length_mm or not weight_grains:
                st.error("❌ Please fill in all required fields (marked with *)")
                return

            # Clean up inputs
            manufacturer = manufacturer.strip()
            model = model.strip()
            bullet_length_mm = bullet_length_mm.strip()
            weight_grains = weight_grains.strip()

            try:
                # Create bullets entry
                bullets_data = {
                    "id": str(uuid.uuid4()),
                    "user_email": user["email"],
                    "manufacturer": manufacturer,
                    "model": model,
                    "bullet_length_mm": bullet_length_mm,
                    "weight_grains": weight_grains,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }

                # Insert into database
                # response = supabase.table("bullets").insert(bullets_data).execute()

                # if response.data:
                #     st.success(f"✅ Bullets entry created successfully!")
                #     st.info(f"📋 **{manufacturer} {model}** - {bullet_length_mm} - {weight_grains}")
                #
                #     # Clear form by rerunning (this will reset the form)
                #     st.rerun()
                # else:
                #     st.error("❌ Failed to create bullets entry. Please try again.")

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
    - **Caliber**: The cartridge bullet_length_mm (e.g., 6.5 Creedmoor, .308 Winchester, .223 Remington)
    - **Weight**: The bullet weight_grains with 'gr' suffix (e.g., 147gr, 168gr, 55gr)
    """
    )

    st.markdown("### 📝 Examples")
    examples = [
        {
            "manufacturer": "Hornady",
            "model": "ELD-M",
            "bullet_length_mm": "6.5 Creedmoor",
            "weight_grains": "147gr",
        },
        {
            "manufacturer": "Federal",
            "model": "Gold Medal",
            "bullet_length_mm": ".308 Winchester",
            "weight_grains": "168gr",
        },
        {
            "manufacturer": "Winchester",
            "model": "Ballistic Tip",
            "bullet_length_mm": ".223 Remington",
            "weight_grains": "55gr",
        },
    ]

    for example in examples:
        st.markdown(
            f"- **{example['manufacturer']} {example['model']}** - {example['bullet_length_mm']} - {example['weight_grains']}"
        )
