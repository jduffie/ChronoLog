import streamlit as st
import uuid
from datetime import datetime, timezone


def render_create_ammo_tab(user, supabase):
    """Render the Create Ammo tab"""
    st.header("➕ Create New Ammo Entry")

    # Create form for ammo entry
    with st.form("create_ammo_form"):
        col1, col2 = st.columns(2)

        with col1:
            make = st.text_input(
                "Manufacturer/Brand *",
                placeholder="e.g., Hornady, Federal, Winchester",
                help="The ammunition manufacturer or brand name",
            )

            model = st.text_input(
                "Model/Type *",
                placeholder="e.g., ELD-M, Gold Medal, Ballistic Tip",
                help="The specific ammunition model or type",
            )

        with col2:
            caliber = st.text_input(
                "Caliber *",
                placeholder="e.g., 6.5 Creedmoor, .308 Win, .223 Rem",
                help="The ammunition caliber",
            )

            weight = st.text_input(
                "Weight *",
                placeholder="e.g., 147gr, 168gr, 55gr",
                help="The bullet weight (include 'gr' suffix)",
            )

        # Submit button
        submitted = st.form_submit_button("💾 Create Ammo Entry", type="primary")

        if submitted:
            # Validate required fields
            if not make or not model or not caliber or not weight:
                st.error("❌ Please fill in all required fields (marked with *)")
                return

            # Clean up inputs
            make = make.strip()
            model = model.strip()
            caliber = caliber.strip()
            weight = weight.strip()

            try:
                # Create ammo entry
                ammo_data = {
                    "id": str(uuid.uuid4()),
                    "user_email": user["email"],
                    "make": make,
                    "model": model,
                    "caliber": caliber,
                    "weight": weight,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }

                # Insert into database
                response = supabase.table("ammo").insert(ammo_data).execute()

                if response.data:
                    st.success(f"✅ Ammo entry created successfully!")
                    st.info(f"📋 **{make} {model}** - {caliber} - {weight}")

                    # Clear form by rerunning (this will reset the form)
                    st.rerun()
                else:
                    st.error("❌ Failed to create ammo entry. Please try again.")

            except Exception as e:
                if "duplicate key value violates unique constraint" in str(e):
                    st.error(
                        "❌ This ammo entry already exists. Please check your entries."
                    )
                else:
                    st.error(f"❌ Error creating ammo entry: {str(e)}")

    # Display helpful information
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown(
        """
    - **Manufacturer/Brand**: The company that makes the ammunition (e.g., Hornady, Federal, Winchester)
    - **Model/Type**: The specific product line or bullet type (e.g., ELD-M, Gold Medal, Ballistic Tip)
    - **Caliber**: The cartridge caliber (e.g., 6.5 Creedmoor, .308 Winchester, .223 Remington)
    - **Weight**: The bullet weight with 'gr' suffix (e.g., 147gr, 168gr, 55gr)
    """
    )

    st.markdown("### 📝 Examples")
    examples = [
        {
            "make": "Hornady",
            "model": "ELD-M",
            "caliber": "6.5 Creedmoor",
            "weight": "147gr",
        },
        {
            "make": "Federal",
            "model": "Gold Medal",
            "caliber": ".308 Winchester",
            "weight": "168gr",
        },
        {
            "make": "Winchester",
            "model": "Ballistic Tip",
            "caliber": ".223 Remington",
            "weight": "55gr",
        },
    ]

    for example in examples:
        st.markdown(
            f"- **{example['make']} {example['model']}** - {example['caliber']} - {example['weight']}"
        )
