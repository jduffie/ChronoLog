import uuid
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from .dope_model import DopeModel


def find_closest_weather_measurement(
    shot_datetime, weather_data, max_time_diff_minutes=30
):
    """Find the closest weather measurement by timestamp within a time window"""
    if not weather_data or not shot_datetime:
        return None

    try:
        # Parse shot datetime
        if isinstance(shot_datetime, str):
            shot_dt = datetime.fromisoformat(shot_datetime.replace("Z", "+00:00"))
        else:
            shot_dt = shot_datetime

        closest_weather = None
        min_time_diff = timedelta(minutes=max_time_diff_minutes)

        for weather in weather_data:
            # Parse weather measurement timestamp
            weather_timestamp = weather.get("measurement_timestamp")
            if not weather_timestamp:
                continue

            if isinstance(weather_timestamp, str):
                weather_dt = datetime.fromisoformat(
                    weather_timestamp.replace("Z", "+00:00")
                )
            else:
                weather_dt = weather_timestamp

            # Calculate time difference
            time_diff = abs(shot_dt - weather_dt)

            # Check if this is the closest match within the time window
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_weather = weather

        return closest_weather
    except Exception as e:
        print(f"Error finding closest weather measurement: {e}")
        return None


def render_create_session_tab(user, supabase):
    """Render the Create Session tab"""
    st.header("📝 Create New Session")

    # Initialize DOPE model in session state
    if "dope_model" not in st.session_state:
        st.session_state.dope_model = DopeModel()

    dope_model = st.session_state.dope_model

    # Step 1: Select chronograph session
    st.subheader("1. Select Chronograph Session")

    try:
        # Get all chronograph sessions for the user
        chrono_sessions = (
            supabase.table("chrono_sessions")
            .select("*")
            .eq("user_email", user["email"])
            .order("datetime_local", desc=True)
            .execute()
        )

        # Get existing DOPE sessions to find which chrono sessions are already used
        existing_dope_sessions = (
            supabase.table("dope_sessions")
            .select("chrono_session_id")
            .eq("user_email", user["email"])
            .execute()
        )
        used_chrono_session_ids = {
            session["chrono_session_id"]
            for session in existing_dope_sessions.data
            if session.get("chrono_session_id")
        }

        # Filter out chronograph sessions that are already linked to DOPE sessions
        available_chrono_sessions = [
            session
            for session in chrono_sessions.data
            if session["id"] not in used_chrono_session_ids
        ]

        if not available_chrono_sessions:
            if chrono_sessions.data:
                st.warning(
                    "All chronograph sessions have already been used to create DOPE sessions. Please upload new chronograph data."
                )
            else:
                st.warning(
                    "No chronograph sessions found. Please upload chronograph data first."
                )
            return

        # Create dropdown options from available sessions only
        session_options = {}
        for session in available_chrono_sessions:
            label = f"{session['datetime_local']} - {session['bullet_type']} - {session['bullet_grain']}gr "
            session_options[label] = session

        selected_session_label = st.selectbox(
            "Choose a chronograph session:",
            options=list(session_options.keys()),
            index=None,
            placeholder="Select a chronograph session...",
        )

        if selected_session_label:
            selected_session = session_options[selected_session_label]

            # Use chronograph session ID as unique tab name for DOPE session
            tab_name = f"chrono_session_{selected_session['id']}"

            st.subheader("2. Select Optional Sources")

            col1, col2 = st.columns(2)

            with col1:
                # Get range submissions for the user
                range_submissions = (
                    supabase.table("ranges_submissions")
                    .select("*")
                    .eq("user_email", user["email"])
                    .order("submitted_at", desc=True)
                    .execute()
                )

                range_options = {}
                if range_submissions.data:
                    for range_sub in range_submissions.data:
                        label = f"{range_sub['range_name']} - {range_sub['distance_m']:.1f}m ({range_sub['submitted_at'][:10]})"
                        range_options[label] = range_sub

                    selected_range_label = st.selectbox(
                        "***Range:***",
                        options=list(range_options.keys()),
                        index=None,
                        placeholder="Select a range...",
                    )
                else:
                    st.warning("No range submissions found.")
                    selected_range_label = None

            with col2:
                # Get weather sources for the user
                weather_sources = (
                    supabase.table("weather_source")
                    .select("*")
                    .eq("user_email", user["email"])
                    .order("created_at", desc=True)
                    .execute()
                )

                if weather_sources.data:
                    weather_options = {}
                    for weather_source in weather_sources.data:
                        label = f"{weather_source['name']} ({weather_source['make'] or 'Unknown'})"
                        weather_options[label] = weather_source

                    selected_weather_label = st.selectbox(
                        "***Weather source:***",
                        options=list(weather_options.keys()),
                        index=None,
                        placeholder="Select weather source...",
                    )

                    selected_weather = (
                        weather_options[selected_weather_label]
                        if selected_weather_label
                        else None
                    )
                else:
                    st.warning("No weather sources found.")
                    selected_weather = None

            col3, col4 = st.columns(2)

            with col3:
                # Get rifles for the user
                try:
                    rifles_response = (
                        supabase.table("rifles")
                        .select("*")
                        .eq("user_email", user["email"])
                        .order("name")
                        .execute()
                    )

                    rifle_options = {}
                    if rifles_response.data:
                        for rifle in rifles_response.data:
                            # Create a descriptive label
                            label = f"{rifle['name']}"
                            details = []
                            if rifle.get("barrel_length"):
                                details.append(f"Length: {rifle['barrel_length']}")
                            if rifle.get("barrel_twist_ratio"):
                                details.append(f"Twist: {rifle['barrel_twist_ratio']}")
                            if details:
                                label += f" ({', '.join(details)})"
                            rifle_options[label] = rifle

                        selected_rifle_label = st.selectbox(
                            "***Rifle:***",
                            options=list(rifle_options.keys()),
                            index=None,
                            placeholder="Select a rifle...",
                        )

                        selected_rifle = (
                            rifle_options[selected_rifle_label]
                            if selected_rifle_label
                            else None
                        )
                    else:
                        st.warning("No rifles found. Please add rifles first.")
                        selected_rifle = None
                except Exception as e:
                    st.error(f"Error loading rifles: {str(e)}")
                    selected_rifle = None

            with col4:
                # Cartridge selection workflow
                try:
                    selected_cartridge = render_cartridge_selection(user, supabase)
                except Exception as e:
                    st.error(f"Error loading cartridges: {str(e)}")
                    selected_cartridge = None

            # Prepare selected range and weather data
            selected_range = (
                range_options[selected_range_label] if selected_range_label else None
            )

            # Create/update the DOPE session with current selections
            create_dope_session(
                user,
                supabase,
                selected_session,
                selected_range,
                selected_weather,
                selected_rifle,
                selected_cartridge,
                dope_model,
                tab_name,
            )

            # Add spacing before the table
            st.markdown("---")
            st.markdown("<br>", unsafe_allow_html=True)

            # Display the session if it has been created
            if dope_model.is_tab_created(tab_name):
                display_dope_session(user, supabase, dope_model, tab_name)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")


def create_dope_session(
    user,
    supabase,
    chrono_session,
    range_data,
    weather_source,
    selected_rifle,
    selected_cartridge,
    dope_model,
    tab_name,
):
    """Create and store the merged DOPE session data in the model"""

    try:
        # Get chronograph measurements for the selected session
        measurements = (
            supabase.table("chrono_measurements")
            .select("*")
            .eq("chrono_session_id", chrono_session["id"])
            .order("shot_number")
            .execute()
        )

        if not measurements.data:
            st.warning("No measurements found for the selected chronograph session.")
            return

        # Get weather measurements only if a weather source is selected
        weather_data = []
        if weather_source:
            weather_measurements = (
                supabase.table("weather_measurements")
                .select("*")
                .eq("weather_source_id", weather_source["id"])
                .execute()
            )
            weather_data = (
                weather_measurements.data if weather_measurements.data else []
            )

        # Create the measurements data table
        measurements_data = []

        for measurement in measurements.data:
            # Find closest weather measurement by timestamp
            shot_datetime = measurement.get("datetime_local", "")
            closest_weather = find_closest_weather_measurement(
                shot_datetime, weather_data
            )

            row = {
                # Chronograph measurement data
                "datetime": measurement.get("datetime_local", ""),
                "shot_number": measurement.get("shot_number", ""),
                "speed": measurement.get("speed_fps", ""),
                "ke_ft_lb": measurement.get("ke_ft_lb", ""),
                "power_factor": measurement.get("power_factor", ""),
                # Range measurement data (per shot)
                "azimuth": range_data.get("azimuth_deg", "") if range_data else "",
                "elevation_angle": (
                    range_data.get("elevation_angle_deg", "") if range_data else ""
                ),
                # Weather data (matched by timestamp)
                "temperature": (
                    closest_weather.get("temperature_f", "") if closest_weather else ""
                ),
                "pressure": (
                    closest_weather.get("barometric_pressure_inhg", "")
                    if closest_weather
                    else ""
                ),
                "humidity": (
                    closest_weather.get("relative_humidity_pct", "")
                    if closest_weather
                    else ""
                ),
                # Optional DOPE data (to be filled by user later)
                "distance": "",  # User-provided distance (separate from range distance)
                "elevation_adjustment": "",  # Elevation adjustment in RADS or MOA
                "windage_adjustment": "",  # Windage adjustment in RADS or MOA
                "clean_bore": measurement.get("clean_bore") or "",
                "cold_bore": measurement.get("cold_bore") or "",
                "shot_notes": measurement.get("shot_notes") or "",
            }
            measurements_data.append(row)

        # Store in model
        dope_model.set_tab_measurements(tab_name, measurements_data)

        # Store session details
        session_details = {
            "range_name": range_data.get("range_name", "") if range_data else "",
            "weather_source": weather_source,  # Store entire weather source object
            "weather_source_name": (
                weather_source.get("name", "") if weather_source else ""
            ),
            "distance_m": range_data.get("distance_m", "") if range_data else "",
            "chrono_session": chrono_session,  # Store entire chrono session object
            "range_data": range_data,  # Store entire range data object
            "rifle": selected_rifle,  # Store entire rifle object
            "rifle_name": selected_rifle.get("name", "") if selected_rifle else "",
            "cartridge": selected_cartridge,  # Store entire cartridge object
            "cartridge_description": (
                selected_cartridge.get("description", "")
                if selected_cartridge
                else ""
            ),
        }
        dope_model.set_tab_session_details(tab_name, session_details)

    except Exception as e:
        st.error(f"Error creating DOPE session: {str(e)}")


def display_dope_session(user, supabase, dope_model, tab_name):
    """Display the DOPE session with editable measurements table"""

    # Get session details and measurements from model
    session_details = dope_model.get_tab_session_details(tab_name)
    current_df = dope_model.get_tab_measurements_df(tab_name)

    if current_df is None:
        st.warning("No DOPE session data found.")
        return

    st.subheader("3. DOPE Session")

    # Component 1: Cartridge Details
    st.markdown("#### Cartridge")
    if session_details.get("cartridge"):
        cartridge_data = session_details["cartridge"]
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
                f"<medium><strong>Bullet:</strong> {cartridge_data.get('bullet_name', 'N/A')}</medium>",
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f"<medium><strong>Weight:</strong> {cartridge_data.get('bullet_weight_grains', 'N/A')}gr</medium>",
                unsafe_allow_html=True,
            )
    else:
        st.info("No cartridge data available for this session")

    # Component 2: Rifle Details
    st.markdown("#### Rifle")
    if session_details.get("rifle"):
        rifle_data = session_details["rifle"]
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"<medium><strong>Name:</strong> {rifle_data.get('name', 'N/A')}</medium>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<medium><strong>Barrel Length:</strong> {rifle_data.get('barrel_length', 'N/A')}</medium>",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"<medium><strong>Twist Ratio:</strong> {rifle_data.get('barrel_twist_ratio', 'N/A')}</medium>",
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f"<medium><strong>Scope:</strong> {rifle_data.get('scope', 'N/A')}</medium>",
                unsafe_allow_html=True,
            )
    else:
        st.info("No rifle data available for this session")

    # Component 3: Location Details
    st.markdown("#### Firing Position")
    if session_details.get("range_data"):
        range_data = session_details["range_data"]
        col1, col2, col3 = st.columns(3)

        with col1:
            lat_text = (
                f"{range_data.get('start_lat', 'N/A'):.6f}"
                if range_data.get("start_lat")
                else "N/A"
            )
            st.markdown(
                f"<medium><strong>Latitude:</strong> {lat_text}</medium>",
                unsafe_allow_html=True,
            )
        with col2:
            lon_text = (
                f"{range_data.get('start_lon', 'N/A'):.6f}"
                if range_data.get("start_lon")
                else "N/A"
            )
            st.markdown(
                f"<medium><strong>Longitude:</strong> {lon_text}</medium>",
                unsafe_allow_html=True,
            )
        with col3:
            alt_text = (
                f"{range_data.get('start_altitude_m', 'N/A'):.1f}"
                if range_data.get("start_altitude_m")
                else "N/A"
            )
            st.markdown(
                f"<medium><strong>Altitude (m):</strong> {alt_text}</medium>",
                unsafe_allow_html=True,
            )
    else:
        st.info("No range data available for this session")

    # Component 2: DOPE Session Measurements Table
    st.markdown("#### Measurements")

    # Display editable measurements table
    edited_df = st.data_editor(
        current_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            # Read-only chronograph data columns
            "datetime": st.column_config.TextColumn(
                "DateTime", width="medium", disabled=True
            ),
            "shot_number": st.column_config.NumberColumn(
                "Shot #", width="small", disabled=True
            ),
            "speed": st.column_config.NumberColumn(
                "Speed (fps)", width="small", disabled=True
            ),
            "ke_ft_lb": st.column_config.NumberColumn(
                "KE (ft-lb)", width="small", disabled=True
            ),
            "power_factor": st.column_config.NumberColumn(
                "PF", width="small", disabled=True
            ),
            # Read-only range measurement columns
            "azimuth": st.column_config.NumberColumn(
                "Azimuth (°)", width="small", format="%.2f", disabled=True
            ),
            "elevation_angle": st.column_config.NumberColumn(
                "Elevation Angle (°)", width="small", format="%.2f", disabled=True
            ),
            # Read-only weather data columns
            "temperature": st.column_config.NumberColumn(
                "Temp (°F)", width="small", format="%.1f", disabled=True
            ),
            "pressure": st.column_config.NumberColumn(
                "Pressure (inHg)", width="small", format="%.2f", disabled=True
            ),
            "humidity": st.column_config.NumberColumn(
                "Humidity (%)", width="small", format="%.1f", disabled=True
            ),
            # User DOPE adjustments (editable)
            "distance": st.column_config.TextColumn(
                "Distance", width="small", help="User-provided distance"
            ),
            "elevation_adjustment": st.column_config.TextColumn(
                "Elevation Adj",
                width="medium",
                help="Elevation adjustment in RADS or MOA",
            ),
            "windage_adjustment": st.column_config.TextColumn(
                "Windage Adj", width="medium", help="Windage adjustment in RADS or MOA"
            ),
            # Shot metadata (editable, far right)
            "clean_bore": st.column_config.TextColumn(
                "Clean Bore", width="small", help="Clean bore indicator"
            ),
            "cold_bore": st.column_config.TextColumn(
                "Cold Bore", width="small", help="Cold bore indicator"
            ),
            "shot_notes": st.column_config.TextColumn(
                "Shot Notes", width="medium", help="Notes for this shot"
            ),
        },
        key=f"dope_measurements_table_{tab_name}",
    )

    # Update model with any edits
    if not edited_df.equals(current_df):
        dope_model.update_tab_measurements(tab_name, edited_df)
        st.info(
            "💡 Changes saved automatically. Click 'Save Session' to persist to database."
        )

    # Save session button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button(
            "💾 Save Session", type="primary", help="Save this DOPE session to database"
        ):
            save_dope_session(user, supabase, dope_model, tab_name)


def save_dope_session(user, supabase, dope_model, tab_name):
    """Save the DOPE session and measurements to the database"""

    try:
        # Get session details and measurements from model
        session_details = dope_model.get_tab_session_details(tab_name)
        measurements_df = dope_model.get_tab_measurements_df(tab_name)

        if not session_details or measurements_df is None:
            st.error("No DOPE session data to save.")
            return

        chrono_session = session_details.get("chrono_session")
        if not chrono_session:
            st.error("No chronograph session found.")
            return

        # Check if DOPE session already exists for this chronograph session
        existing_dope_session = (
            supabase.table("dope_sessions")
            .select("*")
            .eq("chrono_session_id", chrono_session["id"])
            .execute()
        )

        # Generate session name based on cartridge info and timestamp
        cartridge_data = session_details.get("cartridge", {})
        cartridge_name = cartridge_data.get("description", "Unknown")
        bullet_weight = cartridge_data.get("bullet_weight_grains", "")
        weight_text = f"-{bullet_weight}gr" if bullet_weight else ""
        session_name = f"{cartridge_name}{weight_text}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        if existing_dope_session.data:
            # Update existing DOPE session
            dope_session_id = existing_dope_session.data[0]["id"]
            session_name = existing_dope_session.data[0][
                "session_name"
            ]  # Use existing session name
            st.info(
                f"🔄 Updating existing DOPE session for this chronograph session..."
            )

            # Delete existing measurements
            supabase.table("dope_measurements").delete().eq(
                "dope_session_id", dope_session_id
            ).execute()

        else:
            # Create new DOPE session
            dope_session_id = str(uuid.uuid4())

            weather_source = session_details.get("weather_source")
            range_data = session_details.get("range_data")
            rifle_data = session_details.get("rifle")
            cartridge_data = session_details.get("cartridge")
            
            # Extract cartridge reference data instead of copying all details
            cartridge_type = None
            cartridge_spec_id = None
            cartridge_lot_number = None
            
            if cartridge_data:
                # Determine cartridge type and get the appropriate ID
                cartridge_source = cartridge_data.get("source", "")
                if cartridge_source == "factory":
                    cartridge_type = "factory"
                    cartridge_spec_id = cartridge_data.get("spec_id")  # factory_cartridge_specs.id
                elif cartridge_source == "custom":
                    cartridge_type = "custom"
                    cartridge_spec_id = cartridge_data.get("spec_id")  # custom_cartridge_specs.id
                
                # Get lot number from the selection workflow
                cartridge_lot_number = cartridge_data.get("factory_lot")
            
            session_data = {
                "id": dope_session_id,
                "user_email": user["email"],
                "session_name": session_name,
                "range_name": session_details.get("range_name", ""),
                "distance_m": (
                    float(session_details.get("distance_m", 0))
                    if session_details.get("distance_m")
                    else None
                ),
                "chrono_session_id": chrono_session.get("id"),
                "range_submission_id": range_data.get("id") if range_data else None,
                "weather_source_id": (
                    weather_source.get("id") if weather_source else None
                ),
                "rifle_id": rifle_data.get("id") if rifle_data else None,
                "cartridge_type": cartridge_type,
                "cartridge_spec_id": cartridge_spec_id,
                "cartridge_lot_number": cartridge_lot_number,
                "notes": f"Created from DOPE session on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            }

            # Insert dope_session
            session_response = (
                supabase.table("dope_sessions").insert(session_data).execute()
            )

            if not session_response.data:
                st.error("Failed to save DOPE session.")
                return

        # Helper function to safely convert values
        def safe_float(value):
            try:
                if value is None or value == "" or str(value).strip() == "":
                    return None
                return float(value)
            except (ValueError, TypeError):
                return None

        def safe_int(value):
            try:
                if value is None or value == "" or str(value).strip() == "":
                    return None
                return int(value)
            except (ValueError, TypeError):
                return None

        def safe_text(value):
            if value is None or value == "" or str(value).strip() == "":
                return None
            return str(value)

        # Create dope_measurements records
        measurements_data = []
        for _, row in measurements_df.iterrows():
            measurement_data = {
                "dope_session_id": dope_session_id,
                "user_email": user["email"],
                "shot_number": safe_int(row.get("shot_number")),
                "datetime_shot": row.get("datetime") if row.get("datetime") else None,
                # Source chronograph data
                "speed_fps": safe_float(row.get("speed")),
                "ke_ft_lb": safe_float(row.get("ke_ft_lb")),
                "power_factor": safe_float(row.get("power_factor")),
                # Source range data (per-shot directional data)
                "azimuth_deg": safe_float(row.get("azimuth")),
                "elevation_angle_deg": safe_float(row.get("elevation_angle")),
                # Source weather data
                "temperature_f": safe_float(row.get("temperature")),
                "pressure_inhg": safe_float(row.get("pressure")),
                "humidity_pct": safe_float(row.get("humidity")),
                # User-editable DOPE data
                "clean_bore": safe_text(row.get("clean_bore")),
                "cold_bore": safe_text(row.get("cold_bore")),
                "shot_notes": safe_text(row.get("shot_notes")),
                "distance": safe_text(row.get("distance")),
                "elevation_adjustment": safe_text(row.get("elevation_adjustment")),
                "windage_adjustment": safe_text(row.get("windage_adjustment")),
            }
            measurements_data.append(measurement_data)

        # Insert dope_measurements
        if measurements_data:
            measurements_response = (
                supabase.table("dope_measurements").insert(measurements_data).execute()
            )

            if not measurements_response.data:
                st.error("Failed to save DOPE measurements.")
                return

        # Success message
        st.success(
            f"✅ DOPE session '{session_name}' saved successfully with {len(measurements_data)} measurements!"
        )
        st.info(f"💾 Session ID: {dope_session_id}")

    except Exception as e:
        st.error(f"Error saving DOPE session: {str(e)}")
        print(f"Save error details: {e}")  # For debugging


def render_cartridge_selection(user, supabase):
    """Render the cartridge selection workflow"""
    st.markdown("***Cartridge:***")
    
    # Step 1: Cartridge type selection
    cartridge_type = st.selectbox(
        "Cartridge Type:",
        options=["", "factory"],
        format_func=lambda x: "Select type..." if x == "" else x.title(),
        help="Select cartridge type (custom coming later)"
    )
    
    if cartridge_type == "":
        return None
    
    if cartridge_type == "factory":
        # Get factory cartridge specs from cartridge_details view (globally available)
        try:
            response = (
                supabase.table("cartridge_details")
                .select("*")
                .eq("source", "factory")
                .execute()
            )
            
            if not response.data:
                st.warning("⚠️ No factory cartridge specifications available.")
                return None
            
            # Convert to DataFrame for filtering
            df = pd.DataFrame(response.data)
            
            # Add filters
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                manufacturers = ["All"] + sorted(df["manufacturer"].dropna().unique().tolist())
                selected_manufacturer = st.selectbox("Cartridge Manufacturer:", manufacturers)
            
            with col2:
                bore_diameters = ["All"] + sorted(df["bore_diameter_land_mm"].dropna().unique().tolist())
                selected_bore_diameter = st.selectbox("Bullet Bore Diameter (mm):", bore_diameters)
            
            with col3:
                weights = ["All"] + sorted(df["bullet_weight_grains"].dropna().unique().tolist())
                selected_weight = st.selectbox("Bullet Weight (gr):", weights)
                
            with col4:
                bullet_models = ["All"] + sorted(df["bullet_model"].dropna().unique().tolist())
                selected_bullet_model = st.selectbox("Bullet Model:", bullet_models)
            
            # Apply filters
            filtered_df = df.copy()
            if selected_manufacturer != "All":
                filtered_df = filtered_df[filtered_df["manufacturer"] == selected_manufacturer]
            if selected_bore_diameter != "All":
                filtered_df = filtered_df[filtered_df["bore_diameter_land_mm"] == selected_bore_diameter]
            if selected_weight != "All":
                filtered_df = filtered_df[filtered_df["bullet_weight_grains"] == selected_weight]
            if selected_bullet_model != "All":
                filtered_df = filtered_df[filtered_df["bullet_model"] == selected_bullet_model]
            
            if len(filtered_df) == 0:
                st.warning("No factory cartridges match the selected filters.")
                return None
            
            # Display the filtered table for selection
            st.markdown(f"**Available Factory Cartridges ({len(filtered_df)} found)**")
            
            # Prepare display DataFrame
            display_df = filtered_df[[
                "manufacturer", "model", "bullet_model", "bullet_weight_grains", "bore_diameter_land_mm"
            ]].rename(columns={
                "manufacturer": "Cartridge Make",
                "model": "Cartridge Model", 
                "bullet_model": "Bullet Model",
                "bullet_weight_grains": "Weight (gr)",
                "bore_diameter_land_mm": "Bore Ø (mm)"
            })
            
            # Use session state for selection
            cartridge_key = f"dope_cartridge_selection_{cartridge_type}"
            if cartridge_key not in st.session_state:
                st.session_state[cartridge_key] = None
            
            # Display table with selection
            selected_rows = st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Get selected cartridge
            if selected_rows["selection"]["rows"]:
                selected_row_idx = selected_rows["selection"]["rows"][0]
                selected_cartridge_data = filtered_df.iloc[selected_row_idx]
                st.session_state[cartridge_key] = selected_cartridge_data.to_dict()
                
                # Show selected cartridge details
                st.success(f"✅ Selected: {selected_cartridge_data['manufacturer']} {selected_cartridge_data['model']} - {selected_cartridge_data['bullet_model']} ({selected_cartridge_data['bullet_weight_grains']}gr)")
                
                # Factory lot number input
                factory_lot = st.text_input(
                    "Factory Lot Number (optional):",
                    placeholder="e.g., LOT-2024-001",
                    help="Optional factory lot number for this cartridge batch"
                )
                
                # Return complete cartridge info
                cartridge_info = selected_cartridge_data.to_dict()
                cartridge_info["factory_lot"] = factory_lot.strip() if factory_lot.strip() else None
                cartridge_info["description"] = f"{selected_cartridge_data['manufacturer']} {selected_cartridge_data['model']}"
                
                return cartridge_info
            
            elif st.session_state[cartridge_key]:
                # Show previously selected cartridge
                prev_cartridge = st.session_state[cartridge_key]
                st.info(f"Previously selected: {prev_cartridge.get('manufacturer', '')} {prev_cartridge.get('model', '')}")
                return prev_cartridge
                
        except Exception as e:
            st.error(f"Error loading factory cartridges: {str(e)}")
            return None
    
    else:  # custom type (future implementation)
        st.info("🚧 Custom cartridge functionality will be implemented later.")
        return None
    
    return None
