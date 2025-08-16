from datetime import datetime

import pandas as pd
import streamlit as st

from .dope_model import DopeModel


def render_view_session_tab(user, supabase):
    """Render the View Session tab with selectable table and details"""
    st.header("🔍 View Session")

    # Initialize cache model for View tab
    if "view_model" not in st.session_state:
        st.session_state.view_model = DopeModel()
    view_model = st.session_state.view_model

    try:
        # Get user's sessions with all related data in a single query using JOINs
        sessions_response = (
            supabase.table("dope_sessions")
            .select(
                """
            *, 
            chrono_sessions(datetime_local),
            ranges_submissions(range_name),
            weather_source(name),
            rifles(name)
        """
            )
            .eq("user_email", user["email"])
            .order("created_at", desc=True)
            .execute()
        )
        sessions = sessions_response.data

        if sessions:
            # Process sessions with aggregated measurement data
            session_summaries = []
            session_lookup = {}  # For mapping display rows to session data

            for session in sessions:
                # Get measurements for this session
                measurements_response = (
                    supabase.table("dope_measurements")
                    .select("*")
                    .eq("dope_session_id", session["id"])
                    .execute()
                )
                measurements = measurements_response.data

                # Prepare session timestamp using datetime_local from chrono_sessions
                chrono_session = session.get("chrono_sessions")
                if chrono_session and chrono_session.get("datetime_local"):
                    session_dt = pd.to_datetime(chrono_session["datetime_local"])
                    session_date = session_dt.strftime("%Y-%m-%d")
                    session_time = session_dt.strftime("%H:%M")
                elif session.get("created_at"):
                    # Fallback to created_at if datetime_local not available
                    session_dt = pd.to_datetime(session["created_at"])
                    session_date = session_dt.strftime("%Y-%m-%d")
                    session_time = session_dt.strftime("%H:%M")
                else:
                    session_date = "N/A"
                    session_time = "N/A"

                # Get shot count only
                shot_count = len(measurements) if measurements else 0

                # Get optional source names from joined data (efficient for table display)
                range_name = "N/A"
                weather_name = "N/A"
                rifle_name = "N/A"
                cartridge_name = "N/A"

                # Get range name from joined data
                ranges_data = session.get("ranges_submissions")
                if ranges_data:
                    range_name = ranges_data.get("range_name", "N/A")

                # Get weather source name from joined data
                weather_data = session.get("weather_source")
                if weather_data:
                    weather_name = weather_data.get("name", "N/A")

                # Get rifle name from joined data
                rifle_data = session.get("rifles")
                if rifle_data:
                    rifle_name = rifle_data.get("name", "N/A")

                # Get cartridge information using cartridge_type and cartridge_spec_id
                cartridge_type = session.get("cartridge_type", "")
                cartridge_lot = session.get("cartridge_lot_number", "")
                if cartridge_type:
                    cartridge_name = cartridge_type.title()
                    if cartridge_lot:
                        cartridge_name += f" (Lot: {cartridge_lot})"

                row_data = {
                    "Date": session_date,
                    "Time": session_time,
                    "Session Name": session.get("session_name", "N/A"),
                    "Cartridge Type": cartridge_type.title() if cartridge_type else "N/A",
                    "Lot Number": cartridge_lot if cartridge_lot else "N/A",
                    "Shot Count": shot_count,
                    "Range": range_name,
                    "Weather Source": weather_name,
                    "Rifle": rifle_name,
                    "Cartridge": cartridge_name,
                }
                session_summaries.append(row_data)

                # Map this row to session data for lookup
                session_lookup[len(session_summaries) - 1] = session

            # Create DataFrame and display
            if session_summaries:
                sessions_df = pd.DataFrame(session_summaries)

                st.markdown("### Select Session")
                st.info("💡 Click on any row to view session details and measurements")

                # Add search controls
                with st.expander("🔍 Search & Filter", expanded=False):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        # Get unique ranges for filter
                        unique_ranges = sorted(
                            [r for r in sessions_df["Range"].unique() if r != "N/A"]
                        )
                        if "N/A" in sessions_df["Range"].unique():
                            unique_ranges = ["All"] + unique_ranges + ["N/A"]
                        else:
                            unique_ranges = ["All"] + unique_ranges

                        selected_range = st.selectbox(
                            "Filter by Range:",
                            options=unique_ranges,
                            index=0,
                            key="view_session_range_filter",
                        )

                    with col2:
                        # Get unique rifles for filter
                        unique_rifles = sorted(
                            [r for r in sessions_df["Rifle"].unique() if r != "N/A"]
                        )
                        if "N/A" in sessions_df["Rifle"].unique():
                            unique_rifles = ["All"] + unique_rifles + ["N/A"]
                        else:
                            unique_rifles = ["All"] + unique_rifles

                        selected_rifle = st.selectbox(
                            "Filter by Rifle:",
                            options=unique_rifles,
                            index=0,
                            key="view_session_rifle_filter",
                        )

                    with col3:
                        # Get unique cartridge types for filter
                        unique_cartridge_types = sorted(
                            [c for c in sessions_df["Cartridge Type"].unique() if c != "N/A"]
                        )
                        if "N/A" in sessions_df["Cartridge Type"].unique():
                            unique_cartridge_types = ["All"] + unique_cartridge_types + ["N/A"]
                        else:
                            unique_cartridge_types = ["All"] + unique_cartridge_types

                        selected_cartridge_type = st.selectbox(
                            "Filter by Cartridge Type:",
                            options=unique_cartridge_types,
                            index=0,
                            key="view_session_cartridge_filter",
                        )

                # Apply filters
                filtered_df = sessions_df.copy()

                if selected_range != "All":
                    filtered_df = filtered_df[filtered_df["Range"] == selected_range]

                if selected_rifle != "All":
                    filtered_df = filtered_df[filtered_df["Rifle"] == selected_rifle]

                if selected_cartridge_type != "All":
                    filtered_df = filtered_df[filtered_df["Cartridge Type"] == selected_cartridge_type]

                # Update session lookup for filtered results
                filtered_session_lookup = {}
                for new_index, (original_index, row) in enumerate(
                    filtered_df.iterrows()
                ):
                    if original_index in session_lookup:
                        filtered_session_lookup[new_index] = session_lookup[
                            original_index
                        ]

                # Show filter results info
                if len(filtered_df) != len(sessions_df):
                    st.info(
                        f"🔍 Showing {len(filtered_df)} of {len(sessions_df)} sessions"
                    )

                # Reset the index for the filtered dataframe
                filtered_df = filtered_df.reset_index(drop=True)

                # Display the sessions table with selection
                selected_rows = st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    column_config={
                        "Date": st.column_config.DateColumn("Date"),
                        "Time": st.column_config.TextColumn("Time"),
                        "Session Name": st.column_config.TextColumn("Session Name"),
                        "Cartridge Type": st.column_config.TextColumn("Cartridge Type"),
                        "Lot Number": st.column_config.TextColumn("Lot Number"),
                        "Shot Count": st.column_config.NumberColumn("Shot Count"),
                        "Range": st.column_config.TextColumn("Range"),
                        "Weather Source": st.column_config.TextColumn("Weather Source"),
                        "Rifle": st.column_config.TextColumn("Rifle"),
                        "Cartridge": st.column_config.TextColumn("Cartridge"),
                    },
                )

                # Handle row selection - show session details
                if selected_rows.selection.rows:
                    selected_row_index = selected_rows.selection.rows[0]
                    if selected_row_index in filtered_session_lookup:
                        selected_session = filtered_session_lookup[selected_row_index]

                        # DEBUG: Print session information
                        dope_session_id = selected_session.get("id", "N/A")
                        chrono_session_id = selected_session.get(
                            "chrono_session_id", "N/A"
                        )
                        chrono_session = selected_session.get("chrono_sessions")
                        chrono_datetime = (
                            chrono_session.get("datetime_local", "N/A")
                            if chrono_session
                            else "N/A"
                        )

                        print(f"DEBUG - Selected session:")
                        print(f"  DOPE Session ID: {dope_session_id}")
                        print(f"  Chrono Session ID: {chrono_session_id}")
                        print(f"  Chrono DateTime: {chrono_datetime}")

                        # Load session data into cache when a session is selected
                        tab_name = f"view_session_{selected_session['id']}"

                        # Store session data in cache if not already there
                        if not view_model.is_tab_created(tab_name):
                            load_session_into_cache(
                                view_model, selected_session, tab_name
                            )

                        # Get cached session data (includes any pending edits)
                        cached_session_details = view_model.get_tab_session_details(
                            tab_name
                        )

                        # Display session details
                        st.markdown("---")
                        st.markdown("### Session Details")

                        # Add editing section
                        with st.expander("✏️ Edit Optional Sources", expanded=False):
                            edit_optional_sources_cached(
                                user,
                                supabase,
                                view_model,
                                tab_name,
                                cached_session_details,
                            )

                        # Session info (use cached data which includes any pending edits)
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(
                                "Session Name",
                                cached_session_details.get("session_name", "N/A"),
                            )
                        with col2:
                            cartridge_type = selected_session.get("cartridge_type", "N/A")
                            st.metric(
                                "Cartridge Type",
                                cartridge_type.title() if cartridge_type != "N/A" else "N/A",
                            )
                        with col3:
                            cartridge_lot = selected_session.get("cartridge_lot_number", "N/A")
                            st.metric(
                                "Lot Number",
                                cartridge_lot if cartridge_lot else "N/A",
                            )
                        with col4:
                            # Use datetime_local from chrono_sessions for the session date/time
                            chrono_session = selected_session.get(
                                "chrono_sessions"
                            )  # This metadata doesn't change
                            if chrono_session and chrono_session.get("datetime_local"):
                                session_dt = pd.to_datetime(
                                    chrono_session["datetime_local"]
                                )
                                st.metric(
                                    "Session Date",
                                    session_dt.strftime("%Y-%m-%d %H:%M"),
                                )
                            elif cached_session_details.get("created_at"):
                                # Fallback to created_at
                                created_dt = pd.to_datetime(
                                    cached_session_details["created_at"]
                                )
                                st.metric(
                                    "Created", created_dt.strftime("%Y-%m-%d %H:%M")
                                )
                            else:
                                st.metric("Date", "N/A")

                        # Component 1: Cartridge Details
                        st.markdown("#### Cartridge")
                        cartridge_type = selected_session.get("cartridge_type")
                        cartridge_spec_id = selected_session.get("cartridge_spec_id")
                        
                        if cartridge_type and cartridge_spec_id:
                            # Get cartridge details from cartridge_details view
                            cartridge_response = (
                                supabase.table("cartridge_details")
                                .select("*")
                                .eq("spec_id", cartridge_spec_id)
                                .eq("source", cartridge_type)
                                .execute()
                            )
                            if cartridge_response.data:
                                cartridge_data = cartridge_response.data[0]
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.markdown(
                                        f"<medium><strong>Make:</strong> {cartridge_data.get('manufacturer', 'N/A')}</medium>",
                                        unsafe_allow_html=True,
                                    )
                                with col2:
                                    st.markdown(
                                        f"<medium><strong>Model:</strong> {cartridge_data.get('model', 'N/A')}</medium>",
                                        unsafe_allow_html=True,
                                    )
                                with col3:
                                    st.markdown(
                                        f"<medium><strong>Bullet:</strong> {cartridge_data.get('bullet_model', 'N/A')}</medium>",
                                        unsafe_allow_html=True,
                                    )
                                with col4:
                                    st.markdown(
                                        f"<medium><strong>Weight:</strong> {cartridge_data.get('bullet_weight_grains', 'N/A')}gr</medium>",
                                        unsafe_allow_html=True,
                                    )
                                
                                # Display lot number if available
                                lot_number = selected_session.get("cartridge_lot_number")
                                if lot_number:
                                    st.markdown(f"**Lot Number:** {lot_number}")
                            else:
                                st.info("Cartridge details not found")
                        else:
                            st.info("No cartridge data available for this session")

                        # Component 2: Rifle Details
                        st.markdown("#### Rifle")
                        rifle_data = selected_session.get("rifles")
                        if rifle_data and selected_session.get("rifle_id"):
                            # We need full rifle details, so make a single query for additional fields
                            rifle_response = (
                                supabase.table("rifles")
                                .select("*")
                                .eq("id", selected_session["rifle_id"])
                                .execute()
                            )
                            if rifle_response.data:
                                full_rifle_data = rifle_response.data[0]
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.markdown(
                                        f"<medium><strong>Name:</strong> {full_rifle_data.get('name', 'N/A')}</medium>",
                                        unsafe_allow_html=True,
                                    )
                                with col2:
                                    st.markdown(
                                        f"<medium><strong>Barrel Length:</strong> {full_rifle_data.get('barrel_length', 'N/A')}</medium>",
                                        unsafe_allow_html=True,
                                    )
                                with col3:
                                    st.markdown(
                                        f"<medium><strong>Twist Ratio:</strong> {full_rifle_data.get('barrel_twist_ratio', 'N/A')}</medium>",
                                        unsafe_allow_html=True,
                                    )
                                with col4:
                                    st.markdown(
                                        f"<medium><strong>Scope:</strong> {full_rifle_data.get('scope', 'N/A')}</medium>",
                                        unsafe_allow_html=True,
                                    )
                            else:
                                st.info("Rifle details not found")
                        else:
                            st.info("No rifle data available for this session")

                        # Component 3: Firing Position Details
                        st.markdown("#### Firing Position")
                        # Use cached range data which includes any pending edits
                        if cached_session_details.get("range_submission_id"):
                            range_response = (
                                supabase.table("ranges_submissions")
                                .select("*")
                                .eq("id", cached_session_details["range_submission_id"])
                                .execute()
                            )
                            if range_response.data:
                                full_range_data = range_response.data[0]
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    lat_text = (
                                        f"{full_range_data.get('start_lat', 'N/A'):.6f}"
                                        if full_range_data.get("start_lat")
                                        else "N/A"
                                    )
                                    st.markdown(
                                        f"<medium><strong>Latitude:</strong> {lat_text}</medium>",
                                        unsafe_allow_html=True,
                                    )
                                with col2:
                                    lon_text = (
                                        f"{full_range_data.get('start_lon', 'N/A'):.6f}"
                                        if full_range_data.get("start_lon")
                                        else "N/A"
                                    )
                                    st.markdown(
                                        f"<medium><strong>Longitude:</strong> {lon_text}</medium>",
                                        unsafe_allow_html=True,
                                    )
                                with col3:
                                    alt_text = (
                                        f"{full_range_data.get('start_altitude_m', 'N/A'):.1f}"
                                        if full_range_data.get("start_altitude_m")
                                        else "N/A"
                                    )
                                    st.markdown(
                                        f"<medium><strong>Altitude (m):</strong> {alt_text}</medium>",
                                        unsafe_allow_html=True,
                                    )
                            else:
                                st.info("Range details not found")
                        else:
                            st.info("No range data available for this session")

                        # Get and display measurements
                        measurements_response = (
                            supabase.table("dope_measurements")
                            .select("*")
                            .eq("dope_session_id", selected_session["id"])
                            .execute()
                        )
                        measurements = measurements_response.data

                        if measurements:
                            st.markdown("### Measurements")

                            # Convert to DataFrame
                            measurements_df = pd.DataFrame(measurements)

                            # Select and reorder columns for display
                            display_columns = []
                            if "shot_number" in measurements_df.columns:
                                display_columns.append("shot_number")
                            if "speed_fps" in measurements_df.columns:
                                display_columns.append("speed_fps")
                            if "ke_ft_lb" in measurements_df.columns:
                                display_columns.append("ke_ft_lb")
                            if "power_factor" in measurements_df.columns:
                                display_columns.append("power_factor")
                            if "datetime_shot" in measurements_df.columns:
                                display_columns.append("datetime_shot")
                            if "clean_bore" in measurements_df.columns:
                                display_columns.append("clean_bore")
                            if "cold_bore" in measurements_df.columns:
                                display_columns.append("cold_bore")
                            if "shot_notes" in measurements_df.columns:
                                display_columns.append("shot_notes")

                            # Display measurements table
                            if display_columns:
                                st.dataframe(
                                    measurements_df[display_columns],
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "shot_number": st.column_config.NumberColumn(
                                            "Shot #"
                                        ),
                                        "speed_fps": st.column_config.NumberColumn(
                                            "Speed (fps)", format="%.1f"
                                        ),
                                        "ke_ft_lb": st.column_config.NumberColumn(
                                            "KE (ft-lb)", format="%.1f"
                                        ),
                                        "power_factor": st.column_config.NumberColumn(
                                            "Power Factor", format="%.1f"
                                        ),
                                        "datetime_shot": st.column_config.DatetimeColumn(
                                            "Date/Time"
                                        ),
                                        "clean_bore": st.column_config.TextColumn(
                                            "Clean Bore"
                                        ),
                                        "cold_bore": st.column_config.TextColumn(
                                            "Cold Bore"
                                        ),
                                        "shot_notes": st.column_config.TextColumn(
                                            "Notes"
                                        ),
                                    },
                                )
                            else:
                                st.info("No measurement data columns found.")
                        else:
                            st.info("No measurements found for this session.")

            else:
                st.info("No sessions found.")
        else:
            st.info("No sessions found. Upload files first to create sessions.")

    except Exception as e:
        st.error(f"Error loading sessions: {e}")


def edit_optional_sources(user, supabase, selected_session):
    """Display editable dropdowns for optional sources"""
    st.markdown("**Update the optional sources for this session:**")

    try:
        # Get current values
        current_range_id = selected_session.get("range_submission_id")
        current_weather_id = selected_session.get("weather_source_id")
        current_rifle_id = selected_session.get("rifle_id")
        current_ammo_id = selected_session.get("ammo_id")

        col1, col2 = st.columns(2)

        with col1:
            # Range dropdown
            range_submissions = (
                supabase.table("ranges_submissions")
                .select("*")
                .eq("user_email", user["email"])
                .order("submitted_at", desc=True)
                .execute()
            )

            range_options = {"None": None}
            current_range_index = 0
            if range_submissions.data:
                for i, range_sub in enumerate(range_submissions.data):
                    label = f"{range_sub['range_name']} - {range_sub['distance_m']:.1f}m ({range_sub['submitted_at'][:10]})"
                    range_options[label] = range_sub["id"]
                    if current_range_id and range_sub["id"] == current_range_id:
                        current_range_index = i + 1  # +1 because "None" is at index 0

            selected_range_label = st.selectbox(
                "Range:",
                options=list(range_options.keys()),
                index=current_range_index,
                key=f"edit_range_{selected_session['id']}",
            )
            new_range_id = range_options[selected_range_label]

            # Weather source dropdown
            weather_sources = (
                supabase.table("weather_source")
                .select("*")
                .eq("user_email", user["email"])
                .order("created_at", desc=True)
                .execute()
            )

            weather_options = {"None": None}
            current_weather_index = 0
            if weather_sources.data:
                for i, weather_source in enumerate(weather_sources.data):
                    label = f"{weather_source['name']} ({weather_source['make'] or 'Unknown'})"
                    weather_options[label] = weather_source["id"]
                    if (
                        current_weather_id
                        and weather_source["id"] == current_weather_id
                    ):
                        current_weather_index = i + 1

            selected_weather_label = st.selectbox(
                "Weather source:",
                options=list(weather_options.keys()),
                index=current_weather_index,
                key=f"edit_weather_{selected_session['id']}",
            )
            new_weather_id = weather_options[selected_weather_label]

        with col2:
            # Rifle dropdown
            rifles_response = (
                supabase.table("rifles")
                .select("*")
                .eq("user_email", user["email"])
                .order("name")
                .execute()
            )

            rifle_options = {"None": None}
            current_rifle_index = 0
            if rifles_response.data:
                for i, rifle in enumerate(rifles_response.data):
                    label = f"{rifle['name']}"
                    details = []
                    if rifle.get("barrel_length"):
                        details.append(f"Length: {rifle['barrel_length']}")
                    if rifle.get("barrel_twist_ratio"):
                        details.append(f"Twist: {rifle['barrel_twist_ratio']}")
                    if details:
                        label += f" ({', '.join(details)})"
                    rifle_options[label] = rifle["id"]
                    if current_rifle_id and rifle["id"] == current_rifle_id:
                        current_rifle_index = i + 1

            selected_rifle_label = st.selectbox(
                "Rifle:",
                options=list(rifle_options.keys()),
                index=current_rifle_index,
                key=f"edit_rifle_{selected_session['id']}",
            )
            new_rifle_id = rifle_options[selected_rifle_label]

            # Cartridge selection
            st.markdown("**Cartridge:**")
            
            # Get current cartridge values
            current_cartridge_type = selected_session.get("cartridge_type", "")
            current_cartridge_spec_id = selected_session.get("cartridge_spec_id")
            current_cartridge_lot = selected_session.get("cartridge_lot_number", "")
            
            # Cartridge type selection
            cartridge_type_options = ["None", "factory"]
            current_type_index = 0
            if current_cartridge_type == "factory":
                current_type_index = 1
                
            selected_cartridge_type = st.selectbox(
                "Cartridge Type:",
                options=cartridge_type_options,
                index=current_type_index,
                key=f"edit_cartridge_type_{selected_session['id']}",
            )
            
            new_cartridge_type = selected_cartridge_type if selected_cartridge_type != "None" else None
            new_cartridge_spec_id = None
            new_cartridge_lot = None
            
            if selected_cartridge_type == "factory":
                # Get factory cartridges from cartridge_details view
                factory_response = (
                    supabase.table("cartridge_details")
                    .select("*")
                    .eq("source", "factory")
                    .execute()
                )
                
                if factory_response.data:
                    cartridge_options = {"None": None}
                    current_cartridge_index = 0
                    
                    for i, cartridge in enumerate(factory_response.data):
                        label = f"{cartridge['manufacturer']} {cartridge['model']} - {cartridge['bullet_model']} ({cartridge['bullet_weight_grains']}gr)"
                        cartridge_options[label] = cartridge["spec_id"]
                        if current_cartridge_spec_id and cartridge["spec_id"] == current_cartridge_spec_id:
                            current_cartridge_index = i + 1
                    
                    selected_cartridge_label = st.selectbox(
                        "Factory Cartridge:",
                        options=list(cartridge_options.keys()),
                        index=current_cartridge_index,
                        key=f"edit_factory_cartridge_{selected_session['id']}",
                    )
                    new_cartridge_spec_id = cartridge_options[selected_cartridge_label]
                    
                    # Lot number input
                    new_cartridge_lot = st.text_input(
                        "Lot Number (optional):",
                        value=current_cartridge_lot,
                        key=f"edit_cartridge_lot_{selected_session['id']}",
                    )
                    new_cartridge_lot = new_cartridge_lot.strip() if new_cartridge_lot.strip() else None
                else:
                    st.warning("No factory cartridges available.")
            elif selected_cartridge_type == "None":
                new_cartridge_type = None
                new_cartridge_spec_id = None
                new_cartridge_lot = None

        # Check if any changes were made
        changes_made = (
            new_range_id != current_range_id
            or new_weather_id != current_weather_id
            or new_rifle_id != current_rifle_id
            or new_cartridge_type != current_cartridge_type
            or new_cartridge_spec_id != current_cartridge_spec_id
            or new_cartridge_lot != current_cartridge_lot
        )

        if changes_made:
            st.info("💡 Changes detected. Click 'Update Session' to save.")

        # Update button
        if st.button(
            "🔄 Update Session",
            type="primary",
            key=f"update_session_{selected_session['id']}",
        ):
            try:
                # Update the DOPE session with new optional source IDs
                update_data = {
                    "range_submission_id": new_range_id,
                    "weather_source_id": new_weather_id,
                    "rifle_id": new_rifle_id,
                    "cartridge_type": new_cartridge_type,
                    "cartridge_spec_id": new_cartridge_spec_id,
                    "cartridge_lot_number": new_cartridge_lot,
                    "updated_at": datetime.now().isoformat(),
                }

                response = (
                    supabase.table("dope_sessions")
                    .update(update_data)
                    .eq("id", selected_session["id"])
                    .execute()
                )

                if response.data:
                    st.success("✅ Session updated successfully!")
                    # Don't use st.rerun() - just show success message
                    # The updated data will be available on next natural page refresh
                else:
                    st.error("❌ Failed to update session.")

            except Exception as e:
                st.error(f"Error updating session: {str(e)}")

    except Exception as e:
        st.error(f"Error loading optional sources: {str(e)}")


def load_session_into_cache(view_model, selected_session, tab_name):
    """Load session data into the cache model"""
    # Store the session details in cache
    session_details = {
        "session_id": selected_session["id"],
        "session_name": selected_session.get("session_name", ""),
        "cartridge_type": selected_session.get("cartridge_type", ""),
        "cartridge_spec_id": selected_session.get("cartridge_spec_id", ""),
        "cartridge_lot_number": selected_session.get("cartridge_lot_number", ""),
        "range_submission_id": selected_session.get("range_submission_id"),
        "weather_source_id": selected_session.get("weather_source_id"),
        "rifle_id": selected_session.get("rifle_id"),
        "created_at": selected_session.get("created_at", ""),
        "updated_at": selected_session.get("updated_at", ""),
    }

    view_model.set_tab_session_details(tab_name, session_details)
    # Mark as created so it's cached
    view_model.get_tab_data(tab_name)["is_created"] = True


def edit_optional_sources_cached(
    user, supabase, view_model, tab_name, cached_session_details
):
    """Display editable dropdowns for optional sources using cache"""
    st.markdown("**Update the optional sources for this session:**")

    try:
        # Get current values from cache
        current_range_id = cached_session_details.get("range_submission_id")
        current_weather_id = cached_session_details.get("weather_source_id")
        current_rifle_id = cached_session_details.get("rifle_id")
        current_ammo_id = cached_session_details.get("ammo_id")

        col1, col2 = st.columns(2)

        with col1:
            # Range dropdown
            range_submissions = (
                supabase.table("ranges_submissions")
                .select("*")
                .eq("user_email", user["email"])
                .order("submitted_at", desc=True)
                .execute()
            )

            range_options = {"None": None}
            current_range_index = 0
            if range_submissions.data:
                for i, range_sub in enumerate(range_submissions.data):
                    label = f"{range_sub['range_name']} - {range_sub['distance_m']:.1f}m ({range_sub['submitted_at'][:10]})"
                    range_options[label] = range_sub["id"]
                    if current_range_id and range_sub["id"] == current_range_id:
                        current_range_index = i + 1  # +1 because "None" is at index 0

            selected_range_label = st.selectbox(
                "Range:",
                options=list(range_options.keys()),
                index=current_range_index,
                key=f"cached_edit_range_{cached_session_details['session_id']}",
            )
            new_range_id = range_options[selected_range_label]

            # Weather source dropdown
            weather_sources = (
                supabase.table("weather_source")
                .select("*")
                .eq("user_email", user["email"])
                .order("created_at", desc=True)
                .execute()
            )

            weather_options = {"None": None}
            current_weather_index = 0
            if weather_sources.data:
                for i, weather_source in enumerate(weather_sources.data):
                    label = f"{weather_source['name']} ({weather_source['make'] or 'Unknown'})"
                    weather_options[label] = weather_source["id"]
                    if (
                        current_weather_id
                        and weather_source["id"] == current_weather_id
                    ):
                        current_weather_index = i + 1

            selected_weather_label = st.selectbox(
                "Weather source:",
                options=list(weather_options.keys()),
                index=current_weather_index,
                key=f"cached_edit_weather_{cached_session_details['session_id']}",
            )
            new_weather_id = weather_options[selected_weather_label]

        with col2:
            # Rifle dropdown
            rifles_response = (
                supabase.table("rifles")
                .select("*")
                .eq("user_email", user["email"])
                .order("name")
                .execute()
            )

            rifle_options = {"None": None}
            current_rifle_index = 0
            if rifles_response.data:
                for i, rifle in enumerate(rifles_response.data):
                    label = f"{rifle['name']}"
                    details = []
                    if rifle.get("barrel_length"):
                        details.append(f"Length: {rifle['barrel_length']}")
                    if rifle.get("barrel_twist_ratio"):
                        details.append(f"Twist: {rifle['barrel_twist_ratio']}")
                    if details:
                        label += f" ({', '.join(details)})"
                    rifle_options[label] = rifle["id"]
                    if current_rifle_id and rifle["id"] == current_rifle_id:
                        current_rifle_index = i + 1

            selected_rifle_label = st.selectbox(
                "Rifle:",
                options=list(rifle_options.keys()),
                index=current_rifle_index,
                key=f"cached_edit_rifle_{cached_session_details['session_id']}",
            )
            new_rifle_id = rifle_options[selected_rifle_label]

            # Cartridge selection
            st.markdown("**Cartridge:**")
            
            # Get current cartridge values from cache
            current_cartridge_type = cached_session_details.get("cartridge_type", "")
            current_cartridge_spec_id = cached_session_details.get("cartridge_spec_id")
            current_cartridge_lot = cached_session_details.get("cartridge_lot_number", "")
            
            # Cartridge type selection
            cartridge_type_options = ["None", "factory"]
            current_type_index = 0
            if current_cartridge_type == "factory":
                current_type_index = 1
                
            selected_cartridge_type = st.selectbox(
                "Cartridge Type:",
                options=cartridge_type_options,
                index=current_type_index,
                key=f"cached_edit_cartridge_type_{cached_session_details['session_id']}",
            )
            
            new_cartridge_type = selected_cartridge_type if selected_cartridge_type != "None" else None
            new_cartridge_spec_id = None
            new_cartridge_lot = None
            
            if selected_cartridge_type == "factory":
                # Get factory cartridges from cartridge_details view
                factory_response = (
                    supabase.table("cartridge_details")
                    .select("*")
                    .eq("source", "factory")
                    .execute()
                )
                
                if factory_response.data:
                    cartridge_options = {"None": None}
                    current_cartridge_index = 0
                    
                    for i, cartridge in enumerate(factory_response.data):
                        label = f"{cartridge['manufacturer']} {cartridge['model']} - {cartridge['bullet_model']} ({cartridge['bullet_weight_grains']}gr)"
                        cartridge_options[label] = cartridge["spec_id"]
                        if current_cartridge_spec_id and cartridge["spec_id"] == current_cartridge_spec_id:
                            current_cartridge_index = i + 1
                    
                    selected_cartridge_label = st.selectbox(
                        "Factory Cartridge:",
                        options=list(cartridge_options.keys()),
                        index=current_cartridge_index,
                        key=f"cached_edit_factory_cartridge_{cached_session_details['session_id']}",
                    )
                    new_cartridge_spec_id = cartridge_options[selected_cartridge_label]
                    
                    # Lot number input
                    new_cartridge_lot = st.text_input(
                        "Lot Number (optional):",
                        value=current_cartridge_lot,
                        key=f"cached_edit_cartridge_lot_{cached_session_details['session_id']}",
                    )
                    new_cartridge_lot = new_cartridge_lot.strip() if new_cartridge_lot.strip() else None
                else:
                    st.warning("No factory cartridges available.")
            elif selected_cartridge_type == "None":
                new_cartridge_type = None
                new_cartridge_spec_id = None
                new_cartridge_lot = None

        # Check if any changes were made (compared to current cache, not original DB)
        changes_made = (
            new_range_id != current_range_id
            or new_weather_id != current_weather_id
            or new_rifle_id != current_rifle_id
            or new_cartridge_type != current_cartridge_type
            or new_cartridge_spec_id != current_cartridge_spec_id
            or new_cartridge_lot != current_cartridge_lot
        )

        # Update cache immediately when changes are made
        if changes_made:
            # Update the cache with new values
            updated_details = cached_session_details.copy()
            updated_details.update(
                {
                    "range_submission_id": new_range_id,
                    "weather_source_id": new_weather_id,
                    "rifle_id": new_rifle_id,
                    "cartridge_type": new_cartridge_type,
                    "cartridge_spec_id": new_cartridge_spec_id,
                    "cartridge_lot_number": new_cartridge_lot,
                    "updated_at": datetime.now().isoformat(),
                }
            )
            view_model.set_tab_session_details(tab_name, updated_details)

            st.info(
                "💡 Changes are visible immediately. Click 'Save to Database' to persist changes."
            )

        # Check if there are any unsaved changes in cache vs database
        session_response = (
            supabase.table("dope_sessions")
            .select("range_submission_id, weather_source_id, rifle_id, cartridge_type, cartridge_spec_id, cartridge_lot_number")
            .eq("id", cached_session_details["session_id"])
            .execute()
        )
        if session_response.data:
            db_data = session_response.data[0]
            unsaved_changes = (
                cached_session_details.get("range_submission_id")
                != db_data.get("range_submission_id")
                or cached_session_details.get("weather_source_id")
                != db_data.get("weather_source_id")
                or cached_session_details.get("rifle_id") != db_data.get("rifle_id")
                or cached_session_details.get("cartridge_type") != db_data.get("cartridge_type")
                or cached_session_details.get("cartridge_spec_id") != db_data.get("cartridge_spec_id")
                or cached_session_details.get("cartridge_lot_number") != db_data.get("cartridge_lot_number")
            )

            if unsaved_changes:
                st.warning("⚠️ You have unsaved changes that are only visible to you.")

        # Save to database button
        if st.button(
            "💾 Save to Database",
            type="primary",
            key=f"save_cached_session_{cached_session_details['session_id']}",
        ):
            try:
                # Update the DOPE session with cached values
                update_data = {
                    "range_submission_id": cached_session_details.get(
                        "range_submission_id"
                    ),
                    "weather_source_id": cached_session_details.get(
                        "weather_source_id"
                    ),
                    "rifle_id": cached_session_details.get("rifle_id"),
                    "cartridge_type": cached_session_details.get("cartridge_type"),
                    "cartridge_spec_id": cached_session_details.get("cartridge_spec_id"),
                    "cartridge_lot_number": cached_session_details.get("cartridge_lot_number"),
                    "updated_at": datetime.now().isoformat(),
                }

                response = (
                    supabase.table("dope_sessions")
                    .update(update_data)
                    .eq("id", cached_session_details["session_id"])
                    .execute()
                )

                if response.data:
                    st.success("✅ Session saved to database successfully!")
                else:
                    st.error("❌ Failed to save session to database.")

            except Exception as e:
                st.error(f"Error saving session: {str(e)}")

    except Exception as e:
        st.error(f"Error loading optional sources: {str(e)}")
