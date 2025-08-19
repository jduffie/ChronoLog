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
        # Get user's sessions with all related data including measurements in a single query
        sessions_response = (
            supabase.table("dope_sessions")
            .select(
                """
            *, 
            chrono_sessions(datetime_local),
            ranges_submissions(range_name),
            weather_source(name),
            rifles(name),
            dope_measurements(*)
        """
            )
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .execute()
        )
        sessions = sessions_response.data

        if sessions:
            # Process sessions with aggregated measurement data
            session_summaries = []
            session_lookup = {}  # For mapping display rows to session data

            for session in sessions:
                # Get measurements from joined data (no additional query needed)
                measurements = session.get("dope_measurements", [])

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
                cartridge_type = session.get("cartridge_type") or ""
                cartridge_spec_id = session.get("cartridge_spec_id")
                cartridge_lot = session.get("cartridge_lot_number") or ""
                cartridge_manufacturer = "N/A"
                cartridge_model = "N/A"
                bullet_weight = "N/A"
                
                if cartridge_type and cartridge_spec_id:
                    # Get detailed cartridge info from cartridge_details view
                    cartridge_details_response = (
                        supabase.table("cartridge_details")
                        .select("manufacturer, model, bullet_weight_grains")
                        .eq("spec_id", cartridge_spec_id)
                        .eq("source", cartridge_type)
                        .execute()
                    )
                    if cartridge_details_response.data:
                        cartridge_data = cartridge_details_response.data[0]
                        cartridge_manufacturer = cartridge_data.get("manufacturer", "N/A")
                        cartridge_model = cartridge_data.get("model", "N/A")
                        bullet_weight = cartridge_data.get("bullet_weight_grains", "N/A")
                
                if cartridge_type:
                    cartridge_name = cartridge_type.title()
                    if cartridge_lot:
                        cartridge_name += f" (Lot: {cartridge_lot})"
                else:
                    cartridge_name = "N/A"

                row_data = {
                    "Date": session_date,
                    "Time": session_time,
                    "Session Name": session.get("session_name", "N/A"),
                    "Cartridge Type": cartridge_type.title() if cartridge_type else "N/A",
                    "Cartridge Manufacturer": cartridge_manufacturer,
                    "Cartridge Model": cartridge_model,
                    "Bullet Weight": bullet_weight,
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
                        "Cartridge Manufacturer": st.column_config.TextColumn("Cartridge Manufacturer"),
                        "Cartridge Model": st.column_config.TextColumn("Cartridge Model"),
                        "Bullet Weight": st.column_config.TextColumn("Bullet Weight"),
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

                # Display measurements for all selected sessions in a unified table
                st.markdown("---")
                st.markdown("### 📊 DOPE Measurements")
                
                # Collect all measurements from sessions that have selections
                all_measurements = []
                if selected_rows.selection.rows:
                    for selected_row_index in selected_rows.selection.rows:
                        if selected_row_index in filtered_session_lookup:
                            session = filtered_session_lookup[selected_row_index]
                            measurements = session.get("dope_measurements", [])
                            
                            # Add session context to each measurement
                            for measurement in measurements:
                                enhanced_measurement = measurement.copy()
                                enhanced_measurement["session_name"] = session.get("session_name", "N/A")
                                enhanced_measurement["session_date"] = session_date if 'session_date' in locals() else "N/A"
                                
                                # Get session date from chrono data
                                chrono_session = session.get("chrono_sessions")
                                if chrono_session and chrono_session.get("datetime_local"):
                                    session_dt = pd.to_datetime(chrono_session["datetime_local"])
                                    enhanced_measurement["session_date"] = session_dt.strftime("%Y-%m-%d")
                                elif session.get("created_at"):
                                    session_dt = pd.to_datetime(session["created_at"])
                                    enhanced_measurement["session_date"] = session_dt.strftime("%Y-%m-%d")
                                
                                all_measurements.append(enhanced_measurement)
                
                if all_measurements:
                    # Convert to DataFrame
                    measurements_df = pd.DataFrame(all_measurements)
                    
                    # Select and reorder columns for display
                    display_columns = []
                    if "session_name" in measurements_df.columns:
                        display_columns.append("session_name")
                    if "session_date" in measurements_df.columns:
                        display_columns.append("session_date")
                    if "shot_number" in measurements_df.columns:
                        display_columns.append("shot_number")
                    if "speed_fps" in measurements_df.columns:
                        display_columns.append("speed_fps")
                    if "ke_ft_lb" in measurements_df.columns:
                        display_columns.append("ke_ft_lb")
                    if "power_factor" in measurements_df.columns:
                        display_columns.append("power_factor")
                    if "azimuth_deg" in measurements_df.columns:
                        display_columns.append("azimuth_deg")
                    if "elevation_angle_deg" in measurements_df.columns:
                        display_columns.append("elevation_angle_deg")
                    if "temperature_f" in measurements_df.columns:
                        display_columns.append("temperature_f")
                    if "pressure_inhg" in measurements_df.columns:
                        display_columns.append("pressure_inhg")
                    if "humidity_pct" in measurements_df.columns:
                        display_columns.append("humidity_pct")
                    if "datetime_shot" in measurements_df.columns:
                        display_columns.append("datetime_shot")
                    if "clean_bore" in measurements_df.columns:
                        display_columns.append("clean_bore")
                    if "cold_bore" in measurements_df.columns:
                        display_columns.append("cold_bore")
                    if "shot_notes" in measurements_df.columns:
                        display_columns.append("shot_notes")
                    if "distance" in measurements_df.columns:
                        display_columns.append("distance")
                    if "elevation_adjustment" in measurements_df.columns:
                        display_columns.append("elevation_adjustment")
                    if "windage_adjustment" in measurements_df.columns:
                        display_columns.append("windage_adjustment")

                    # Display measurements table
                    if display_columns:
                        st.info(f"📈 Showing {len(measurements_df)} measurements from {len(selected_rows.selection.rows)} selected session(s)")
                        
                        st.dataframe(
                            measurements_df[display_columns],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "session_name": st.column_config.TextColumn("Session Name"),
                                "session_date": st.column_config.DateColumn("Session Date"),
                                "shot_number": st.column_config.NumberColumn("Shot #"),
                                "speed_fps": st.column_config.NumberColumn("Speed (fps)", format="%.1f"),
                                "ke_ft_lb": st.column_config.NumberColumn("KE (ft-lb)", format="%.1f"),
                                "power_factor": st.column_config.NumberColumn("Power Factor", format="%.1f"),
                                "azimuth_deg": st.column_config.NumberColumn("Azimuth (°)", format="%.2f"),
                                "elevation_angle_deg": st.column_config.NumberColumn("Elevation (°)", format="%.2f"),
                                "temperature_f": st.column_config.NumberColumn("Temp (°F)", format="%.1f"),
                                "pressure_inhg": st.column_config.NumberColumn("Pressure (inHg)", format="%.2f"),
                                "humidity_pct": st.column_config.NumberColumn("Humidity (%)", format="%.1f"),
                                "datetime_shot": st.column_config.DatetimeColumn("Date/Time"),
                                "clean_bore": st.column_config.TextColumn("Clean Bore"),
                                "cold_bore": st.column_config.TextColumn("Cold Bore"),
                                "shot_notes": st.column_config.TextColumn("Notes"),
                                "distance": st.column_config.TextColumn("Distance"),
                                "elevation_adjustment": st.column_config.TextColumn("Elevation Adj"),
                                "windage_adjustment": st.column_config.TextColumn("Windage Adj"),
                            },
                        )
                    else:
                        st.info("No measurement data columns found.")
                else:
                    st.info("No measurements found for selected session(s). Select a session above to view measurements.")

            else:
                st.info("No sessions found.")
        else:
            st.info("No sessions found. Upload files first to create sessions.")

    except Exception as e:
        st.error(f"Error loading sessions: {e}")


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
