import streamlit as st


def  render_create_cartridge_tab(user, supabase):
    """Render the Create Factory Cartridge tab"""
    st.header("➕ Create New Factory Cartridge")
    
    # Check if user is admin
    is_admin = user.get("user_metadata", {}).get("is_admin", False) or user.get("email") == "johnduffie91@gmail.com"
    
    if not is_admin:
        st.warning("🔒 Access Denied: Only administrators can create factory cartridge entries.")
        st.info("This global factory cartridge database is maintained by administrators to ensure data quality and consistency.")
        return

    # Create form for factory cartridge entry
    with st.form("create_cartridge_form"):
        st.subheader("📦 Cartridge Information")
        col1, col2 = st.columns(2)

        with col1:
            make = st.text_input(
                "Manufacturer/Make *",
                placeholder="e.g., Federal, Hornady, Winchester, Remington",
                help="The cartridge manufacturer or brand name",
            )

        with col2:
            model = st.text_input(
                "Model/Name *",
                placeholder="e.g., Gold Medal Match, Precision Hunter, Super-X",
                help="The specific cartridge model or product name",
            )

        st.subheader("🎯 Bullet Selection")
        
        # Get available bullets from global database to create a dropdown
        try:
            bullets_response = (
                supabase.table("bullets")
                .select("id, manufacturer, model, weight_grains, bullet_diameter_groove_mm")
                .order("manufacturer, model, weight_grains")
                .execute()
            )
            
            if bullets_response.data:
                # Create bullet options for dropdown
                bullet_options = []
                bullet_lookup = {}
                
                for bullet in bullets_response.data:
                    label = f"{bullet['manufacturer']} {bullet['model']} - {bullet['weight_grains']}gr - {bullet['bullet_diameter_groove_mm']}mm"
                    bullet_options.append(label)
                    bullet_lookup[label] = bullet['id']
                
                selected_bullet_label = st.selectbox(
                    "Select Bullet *",
                    options=[None] + bullet_options,
                    format_func=lambda x: "Select a bullet..." if x is None else x,
                    help="Choose the bullet used in this factory cartridge"
                )
                
                selected_bullet_id = bullet_lookup.get(selected_bullet_label) if selected_bullet_label else None
                
            else:
                st.warning("⚠️ No bullets found in the global database. Please add bullets first before creating factory cartridges.")
                selected_bullet_id = None
                
        except Exception as e:
            st.error(f"❌ Error loading bullets: {str(e)}")
            selected_bullet_id = None

        # Submit button
        submitted = st.form_submit_button("💾 Create Factory Cartridge", type="primary")

        if submitted:
            # Validate required fields
            if not make or not model or not selected_bullet_id:
                st.error("❌ Please fill in all required fields (marked with *)")
                return

            # Clean up inputs
            make = make.strip()
            model = model.strip()

            try:
                # Create factory cartridge entry
                cartridge_data = {
                    "user_id": user["id"],
                    "make": make,
                    "model": model,
                    "bullet_id": selected_bullet_id,
                }

                # Insert into database
                response = supabase.table("factory_cartridge_specs").insert(cartridge_data).execute()

                if response.data:
                    st.success(f"✅ Factory cartridge created successfully!")
                    st.info(f"📦 **{make} {model}** linked to selected bullet")

                    # Clear form by rerunning (this will reset the form)
                    st.rerun()
                else:
                    st.error("❌ Failed to create factory cartridge. Please try again.")

            except Exception as e:
                if "duplicate key value violates unique constraint" in str(e):
                    st.error(
                        "❌ This factory cartridge already exists. Each make/model combination must be unique."
                    )
                elif "violates foreign key constraint" in str(e):
                    st.error("❌ Invalid bullet selection. Please try again.")
                else:
                    st.error(f"❌ Error creating factory cartridge: {str(e)}")

    # Display helpful information
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown(
        """
    - **Make/Manufacturer**: The company that manufactures the cartridge (e.g., Federal, Hornady, Winchester)
    - **Model/Name**: The specific product name or line (e.g., Gold Medal Match, Precision Hunter, Super-X)
    - **Bullet Selection**: Choose from bullets you've already added to your database
    - Each make/model combination must be unique in your database
    - You must have bullets in your database before creating factory cartridges
    """
    )

    st.markdown("### 📝 Examples")
    examples = [
        {
            "make": "Federal",
            "model": "Gold Medal Match",
            "bullet_example": "Sierra MatchKing 168gr"
        },
        {
            "make": "Hornady",
            "model": "Precision Hunter",
            "bullet_example": "ELD-X 143gr"
        },
        {
            "make": "Winchester",
            "model": "Super-X",
            "bullet_example": "Power-Point 150gr"
        },
    ]

    for example in examples:
        st.markdown(
            f"- **{example['make']} {example['model']}** (typically paired with {example['bullet_example']})"
        )