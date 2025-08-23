import streamlit as st
import pandas as pd
from cartridges.models import CartridgeModel


def render_edit_cartridges_tab(user, supabase):
    """Render the Create/Edit Cartridges tab"""
    st.header("➕ Create New Cartridge")
    st.markdown("Create a new cartridge specification by selecting a bullet and providing manufacturer details.")

    try:
        # Get available cartridge types
        cartridge_types_response = (
            supabase.table("cartridge_types")
            .select("name")
            .execute()
        )
        
        if not cartridge_types_response.data:
            st.error("No cartridge types found. Please ensure cartridge types are loaded in the database.")
            return
            
        cartridge_type_options = [ct["name"] for ct in cartridge_types_response.data]

        # Get available bullets
        bullets_response = (
            supabase.table("bullets")
            .select("id, manufacturer, model, weight_grains, ballistic_coefficient_g1, ballistic_coefficient_g7")
            .execute()
        )
        
        if not bullets_response.data:
            st.error("No bullets found. Please ensure bullets are loaded in the database.")
            return

        # Create bullet options with detailed descriptions
        bullet_options = {}
        bullet_lookup = {}
        
        for bullet in bullets_response.data:
            description = f"{bullet['manufacturer']} {bullet['model']} {bullet['weight_grains']}gr"
            if bullet.get('ballistic_coefficient_g1'):
                description += f" (BC G1: {bullet['ballistic_coefficient_g1']})"
            bullet_options[description] = bullet['id']
            bullet_lookup[bullet['id']] = bullet

        # Form for creating new cartridge
        with st.form("create_cartridge_form", clear_on_submit=True):
            st.subheader("🔧 Cartridge Details")
            
            # Basic cartridge information
            col1, col2 = st.columns(2)
            
            with col1:
                manufacturer = st.text_input(
                    "Manufacturer *",
                    placeholder="e.g., Federal, Hornady, Winchester",
                    help="The ammunition manufacturer"
                )
                
                cartridge_type = st.selectbox(
                    "Cartridge Type *",
                    options=cartridge_type_options,
                    help="Select the cartridge type"
                )
                
                data_source_name = st.text_input(
                    "Data Source Name",
                    placeholder="e.g., Manufacturer Catalog, User Manual",
                    help="Optional: Name of the data source"
                )

            with col2:
                model = st.text_input(
                    "Model *",
                    placeholder="e.g., Gold Medal Match, Precision Hunter",
                    help="The specific ammunition model/line"
                )
                
                bullet_selection = st.selectbox(
                    "Bullet *",
                    options=[None] + list(bullet_options.keys()),
                    format_func=lambda x: "Select a bullet..." if x is None else x,
                    help="Select the bullet used in this cartridge"
                )
                
                data_source_link = st.text_input(
                    "Data Source URL",
                    placeholder="https://...",
                    help="Optional: URL to the data source"
                )

            # Display selected bullet information
            if bullet_selection:
                selected_bullet_id = bullet_options[bullet_selection]
                selected_bullet = bullet_lookup[selected_bullet_id]
                
                st.subheader(" Selected Bullet Details")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Manufacturer:** {selected_bullet['manufacturer']}")
                    st.write(f"**Model:** {selected_bullet['model']}")
                    
                with col2:
                    st.write(f"**Weight:** {selected_bullet['weight_grains']} grains")
                    if selected_bullet.get('ballistic_coefficient_g1'):
                        st.write(f"**BC G1:** {selected_bullet['ballistic_coefficient_g1']}")
                        
                with col3:
                    if selected_bullet.get('ballistic_coefficient_g7'):
                        st.write(f"**BC G7:** {selected_bullet['ballistic_coefficient_g7']}")

            # Form submission
            submitted = st.form_submit_button("➕ Create Cartridge", type="primary", use_container_width=True)

            if submitted:
                # Validation
                errors = []
                
                if not manufacturer.strip():
                    errors.append("Manufacturer is required")
                if not model.strip():
                    errors.append("Model is required")
                if not cartridge_type:
                    errors.append("Cartridge Type is required")
                if not bullet_selection:
                    errors.append("Bullet selection is required")
                
                # Validate URL format if provided
                if data_source_link.strip() and not data_source_link.startswith(('http://', 'https://')):
                    errors.append("Data Source URL must start with http:// or https://")
                
                if errors:
                    st.error("Please fix the following errors:")
                    for error in errors:
                        st.write(f"• {error}")
                    return

                # Create cartridge record
                try:
                    cartridge_data = {
                        "owner_id": user["id"],  # User-owned cartridge
                        "make": manufacturer.strip(),
                        "model": model.strip(),
                        "cartridge_type": cartridge_type,
                        "bullet_id": bullet_options[bullet_selection],
                        "data_source_name": data_source_name.strip() if data_source_name.strip() else None,
                        "data_source_link": data_source_link.strip() if data_source_link.strip() else None,
                    }

                    # Insert the cartridge
                    response = (
                        supabase.table("cartridges")
                        .insert(cartridge_data)
                        .execute()
                    )

                    if response.data:
                        st.success("✅ Cartridge created successfully!")
                        st.info("The new cartridge will appear in the View tab after refresh.")
                    else:
                        st.error("Failed to create cartridge. Please try again.")

                except Exception as e:
                    st.error(f"Error creating cartridge: {str(e)}")
                    if "duplicate key value violates unique constraint" in str(e):
                        st.info("A cartridge with this combination already exists.")

        # Show existing user cartridges
        st.subheader(" Your Cartridges")
        user_cartridges_response = (
            supabase.table("cartridges")
            .select("""
                *,
                bullets:bullet_id (
                    manufacturer,
                    model,
                    weight_grains
                )
            """)
            .eq("owner_id", user["id"])
            .execute()
        )

        if user_cartridges_response.data:
            # Process and display user cartridges
            user_cartridges = []
            for cartridge in user_cartridges_response.data:
                bullet_info = cartridge.get('bullets', {}) or {}
                user_cartridges.append({
                    'Manufacturer': cartridge.get('make', ''),
                    'Model': cartridge.get('model', ''),
                    'Cartridge Type': cartridge.get('cartridge_type', ''),
                    'Bullet': f"{bullet_info.get('manufacturer', '')} {bullet_info.get('model', '')} {bullet_info.get('weight_grains', '')}gr".strip(),
                    'Created': cartridge.get('created_at', '')[:10] if cartridge.get('created_at') else '',
                })
            
            if user_cartridges:
                df = pd.DataFrame(user_cartridges)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )
                st.info(f"You have created {len(user_cartridges)} custom cartridge(s).")
            else:
                st.info("You haven't created any custom cartridges yet.")
        else:
            st.info("You haven't created any custom cartridges yet.")

    except Exception as e:
        st.error(f"❌ Error loading cartridge creation form: {str(e)}")
        st.info("Please check your database connection and ensure required tables exist.")