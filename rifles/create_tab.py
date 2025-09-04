import uuid
from datetime import datetime, timezone

import streamlit as st

from .service import RifleService


@st.cache_data
def get_cartridge_types(_supabase):
    """Get cartridge types from database with caching"""
    try:
        # Get cartridge types from cartridge_types table (using 'name' column)
        response = _supabase.table("cartridge_types").select("name").execute()
        return sorted([item["name"] for item in response.data])
    except Exception as e:
        st.error(f"❌ Error loading cartridge types: {str(e)}")
        return []


def render_create_rifle_tab(user, supabase):
    """Render the Create Rifle tab"""
    st.header("Create New Rifle Entry")

    # Load cartridge types from database (cached)
    cartridge_options = get_cartridge_types(supabase)
    if not cartridge_options:
        st.error(
            "❌ Unable to load cartridge types. Please check your database connection.")
        return

    # Create form for rifle entry
    with st.form("create_rifle_form"):
        # Required fields
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Rifle Name *",
                placeholder="e.g., My Precision Rifle, Hunting Rifle #1",
                help="A unique name to identify this rifle",
            )

        with col2:
            cartridge_type = st.selectbox(
                "Cartridge Type *",
                options=[None] + cartridge_options,
                format_func=lambda x: "Select cartridge type..." if x is None else x,
                help="Primary cartridge type this rifle is chambered for",
            )

        # Optional fields in two columns
        col1, col2 = st.columns(2)

        with col1:
            barrel_twist_ratio = st.text_input(
                "Barrel Twist Ratio",
                placeholder="e.g., 1:8, 1:10, 1:12",
                help="The barrel twist ratio (e.g., 1:8 means one complete turn in 8 inches)",
            )

            barrel_length = st.text_input(
                "Barrel Length",
                placeholder='e.g., 24 inches, 20", 16.5"',
                help="The barrel length including units",
            )

            sight_offset = st.text_input(
                "Sight Offset/Height",
                placeholder='e.g., 1.5 inches, 38mm, 1.75"',
                help="Height of the scope/sight above the bore centerline",
            )

        with col2:
            trigger = st.text_input(
                "Trigger",
                placeholder="e.g., Timney 2-stage, Jewell HVR, Stock trigger",
                help="Trigger type and specifications",
            )

            scope = st.text_input(
                "Scope",
                placeholder="e.g., Vortex Viper PST 5-25x50, Nightforce NXS 3.5-15x50",
                help="Scope make, model, and specifications",
            )

        # Submit button
        submitted = st.form_submit_button("Create Rifle Entry", type="primary")

        if submitted:
            # Validate required fields
            if not name:
                st.error("❌ Please enter a rifle name (required field)")
                return

            if not cartridge_type:
                st.error("❌ Please select a cartridge type (required field)")
                return

            # Clean up inputs
            name = name.strip()
            barrel_twist_ratio = (
                barrel_twist_ratio.strip() if barrel_twist_ratio else None
            )
            barrel_length = barrel_length.strip() if barrel_length else None
            sight_offset = sight_offset.strip() if sight_offset else None
            trigger = trigger.strip() if trigger else None
            scope = scope.strip() if scope else None

            try:
                # Create rifle entry
                rifle_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": user["id"],
                    "name": name,
                    "cartridge_type": cartridge_type,
                    "barrel_twist_ratio": barrel_twist_ratio,
                    "barrel_length": barrel_length,
                    "sight_offset": sight_offset,
                    "trigger": trigger,
                    "scope": scope,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }

                # Insert into database using service
                rifle_service = RifleService(supabase)
                rifle_id = rifle_service.create_rifle(rifle_data)

                st.success(f"✅ Rifle entry '{name}' created successfully!")

            except Exception as e:
                if "duplicate key value violates unique constraint" in str(e):
                    st.error(
                        "❌ A rifle with this name already exists. Please choose a different name."
                    )
                else:
                    st.error(f"❌ Error creating rifle entry: {str(e)}")

    # Display helpful information
    st.markdown("---")
    st.markdown("###  Tips")
    st.markdown(
        """
    - **Rifle Name**: Give each rifle a unique, descriptive name (e.g., "My Precision Rifle", "Hunting AR-15")
    - **Cartridge Type**: Select the primary cartridge type this rifle is chambered for
    - **Barrel Twist Ratio**: Expressed as 1:X where X is inches per complete turn (e.g., 1:8, 1:10)
    - **Barrel Length**: Include units for clarity (e.g., "24 inches", "20\\"")
    - **Sight Offset**: Height from bore centerline to scope centerline (e.g., "1.5 inches", "38mm")
    - **Trigger**: Include brand and type (e.g., "Timney 2-stage", "Geissele SSA-E")
    - **Scope**: Full specifications help with ballistic calculations (e.g., "Vortex Viper PST 5-25x50 FFP")
    """
    )

    st.markdown("###  Examples")
    examples = [
        {
            "name": "Precision 6.5 Creedmoor",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "24 inches",
            "sight_offset": "1.5 inches",
            "trigger": "Timney 2-stage",
            "scope": "Vortex Viper PST 5-25x50 FFP",
        },
        {
            "name": "Hunting AR-15",
            "cartridge_type": "223 Remington",
            "barrel_twist_ratio": "1:9",
            "barrel_length": "18 inches",
            "sight_offset": "2.6 inches",
            "trigger": "Geissele SSA-E",
            "scope": "Leupold VX-5HD 3-15x44",
        },
    ]

    for example in examples:
        st.markdown(f"**{example['name']}** ({example['cartridge_type']})")
        st.markdown(
            f"- Twist: {example['barrel_twist_ratio']}, Length: {example['barrel_length']}"
        )
        st.markdown(
            f"- Offset: {example['sight_offset']}, Trigger: {example['trigger']}"
        )
        st.markdown(f"- Scope: {example['scope']}")
        st.markdown("")
