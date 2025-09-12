from datetime import datetime

import pandas as pd
import streamlit as st

from .service import ChronographService
from utils.ui_formatters import format_speed, format_delta_speed, format_energy, format_power_factor
from utils.unit_conversions import mps_to_fps, joules_to_ftlb, kgms_to_grainft


def render_logs_tab(user, supabase):
    """Render the View tab showing all chronograph sessions"""
    st.header(" Chronograph Sessions")

    try:
        # Initialize service
        chrono_service = ChronographService(supabase)

        # Get all sessions for the user
        sessions = chrono_service.get_sessions_for_user(user["id"])

        if not sessions:
            st.info(
                "No chronograph logs found. Import some data files to get started!")
            return

        # Get all chronograph sources for the user to create a lookup
        # dictionary
        sources = chrono_service.get_sources_for_user(user["id"])
        source_lookup = {source.id: source.display_name()
                         for source in sources}

        # Extract all unique session names and source names for dropdowns
        all_session_names = set()
        all_source_names = set()
        for session in sessions:
            session_name = session.session_name
            if session_name:
                all_session_names.add(session_name)

            # Get chronograph source name from lookup
            source_name = source_lookup.get(
                session.chronograph_source_id, "Unknown Source")
            all_source_names.add(source_name)

        # Search controls
        st.subheader(" Search & Filter")
        col1, col2, col3 = st.columns(3)

        with col1:
            # Session name dropdown filter
            session_options = ["All Sessions"] + \
                sorted(list(all_session_names))
            selected_session = st.selectbox(
                "Filter by Session Name:",
                options=session_options,
                index=0,
                key="chronograph_session_filter",
            )

        with col2:
            # Chronograph source dropdown filter
            source_options = ["All Sources"] + sorted(list(all_source_names))
            selected_source = st.selectbox(
                "Filter by Chronograph:",
                options=source_options,
                index=0,
                key="chronograph_source_filter",
            )

        with col3:
            # Date range filter
            date_range = st.date_input(
                "Filter by Date Range:",
                value=[],
                max_value=datetime.now().date(),
                help="Select a date range to filter sessions",
                key="chronograph_date_filter",
            )

        # Apply filters
        filtered_sessions = sessions.copy()

        # Filter by session name
        if selected_session != "All Sessions":
            filtered_sessions = [
                session
                for session in filtered_sessions
                if session.session_name == selected_session
            ]

        # Filter by chronograph source
        if selected_source != "All Sources":
            filtered_sessions = [
                session for session in filtered_sessions if source_lookup.get(
                    session.chronograph_source_id,
                    "Unknown Source") == selected_source]

        # Filter by date range
        if date_range:
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_sessions = [
                    session
                    for session in filtered_sessions
                    if start_date <= session.datetime_local.date() <= end_date
                ]
            elif len(date_range) == 1:
                selected_date = date_range[0]
                filtered_sessions = [
                    session
                    for session in filtered_sessions
                    if session.datetime_local.date() == selected_date
                ]

        # Show filtered count
        if len(filtered_sessions) != len(sessions):
            st.info(
                f" Showing {len(filtered_sessions)} of {len(sessions)} sessions")
        else:
            st.subheader(f"Chronograph Sessions ({len(sessions)})")

        # Check if no results after filtering
        if not filtered_sessions:
            st.warning(
                " No sessions match your search criteria. Try adjusting your filters."
            )
            return

        # Create display data with selection column
        table_data = []
        user_unit_system = user.get("unit_system", "Imperial")
        speed_units = "fps" if user_unit_system == "Imperial" else "m/s"
        
        for i, session in enumerate(filtered_sessions):
            # Convert average speed to correct units without formatting
            if session.avg_speed_mps is not None:
                if user_unit_system == "Imperial":
                    avg_speed_value = mps_to_fps(session.avg_speed_mps)
                else:
                    avg_speed_value = session.avg_speed_mps
                avg_speed_display = f"{avg_speed_value:.1f}"
            else:
                avg_speed_display = "N/A"
            
            table_data.append(
                {
                    # Radio button column (only one can be True)
                    "Select": False,
                    "Date": session.datetime_local.strftime("%Y-%m-%d %H:%M"),
                    "Session Name": session.session_name,
                    "Shots": session.shot_count if session.shot_count else 0,
                    f"Avg Speed ({speed_units})": avg_speed_display,
                    "Chronograph": source_lookup.get(session.chronograph_source_id, "Unknown Source"),
                    "Session": session.tab_name,
                }
            )

        # Display as an editable dataframe with radio button selection
        df = pd.DataFrame(table_data)

        # Use st.data_editor with selection column
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select", width="small", default=False
                ),
                "Date": st.column_config.TextColumn(
                    "Date", width="medium", disabled=True
                ),
                "Session": st.column_config.TextColumn(
                    "Session", width="medium", disabled=True
                ),
                "Session Name": st.column_config.TextColumn(
                    "Session Name", width="medium", disabled=True
                ),
                "Chronograph": st.column_config.TextColumn(
                    "Chronograph", width="medium", disabled=True
                ),
                "Shots": st.column_config.NumberColumn(
                    "Shots", width="small", disabled=True
                ),
                "Avg Speed": st.column_config.TextColumn(
                    "Avg Speed", width="small", disabled=True
                ),
                "Session ID": st.column_config.TextColumn(
                    "Session ID", width="medium", disabled=True
                ),
            },
            key="chronograph_sessions_table",
        )

        # Handle multiple row selection
        selected_indices = []
        if edited_df is not None:
            for i, selected in enumerate(edited_df["Select"]):
                if selected:
                    selected_indices.append(i)

        # Store selected sessions in session state
        if selected_indices:
            selected_sessions = [filtered_sessions[i]
                                 for i in selected_indices]
            st.session_state["selected_session_ids"] = [
                session.id for session in selected_sessions
            ]
            st.success(f" Selected {len(selected_sessions)} session(s)")
        else:
            # Clear selection if nothing is selected
            if "selected_session_ids" in st.session_state:
                del st.session_state["selected_session_ids"]

        # Shot Data section
        if selected_indices:
            st.subheader(" Shot Data")

            # Get measurement data for all selected sessions  
            all_measurements = []
            raw_measurements = []  # Keep raw data for calculations
            
            # Define units for column headers
            energy_units = "ft-lb" if user_unit_system == "Imperial" else "J"
            delta_units = speed_units
            
            for idx in selected_indices:
                session = filtered_sessions[idx]
                try:
                    measurements = chrono_service.get_measurements_by_session_id(
                        session.id, user["id"])
                    for measurement in measurements:
                        # Convert values to display units without string formatting
                        if measurement.speed_mps is not None:
                            speed_value = mps_to_fps(measurement.speed_mps) if user_unit_system == "Imperial" else measurement.speed_mps
                            speed_display = f"{speed_value:.1f}"
                        else:
                            speed_value = None
                            speed_display = "N/A"
                            
                        if measurement.delta_avg_mps is not None:
                            delta_value = mps_to_fps(measurement.delta_avg_mps) if user_unit_system == "Imperial" else measurement.delta_avg_mps
                            delta_display = f"{delta_value:+.1f}"
                        else:
                            delta_value = None
                            delta_display = "N/A"
                            
                        if measurement.ke_j is not None:
                            ke_value = joules_to_ftlb(measurement.ke_j) if user_unit_system == "Imperial" else measurement.ke_j
                            ke_display = f"{ke_value:.1f}"
                        else:
                            ke_value = None
                            ke_display = "N/A"
                            
                        if measurement.power_factor_kgms is not None:
                            pf_value = kgms_to_grainft(measurement.power_factor_kgms) if user_unit_system == "Imperial" else measurement.power_factor_kgms
                            pf_display = f"{pf_value:.1f}"
                        else:
                            pf_value = None
                            pf_display = "N/A"
                        
                        # Store display data for table
                        all_measurements.append(
                            {
                                "Date": session.datetime_local.strftime("%Y-%m-%d %H:%M"),
                                "Session Name": session.session_name,
                                "Shot #": measurement.shot_number,
                                f"Speed ({speed_units})": speed_display,
                                f"Δ AVG ({delta_units})": delta_display,
                                f"KE ({energy_units})": ke_display,
                                "Power Factor": pf_display,
                                "Time": (
                                    measurement.datetime_local.strftime("%H:%M:%S")
                                    if measurement.datetime_local
                                    else None
                                ),
                                "Clean Bore": (
                                    "Yes"
                                    if measurement.clean_bore
                                    else (
                                        "No"
                                        if measurement.clean_bore is False
                                        else None
                                    )
                                ),
                                "Cold Bore": (
                                    "Yes"
                                    if measurement.cold_bore
                                    else (
                                        "No" if measurement.cold_bore is False else None
                                    )
                                ),
                                "Notes": (
                                    measurement.shot_notes
                                    if measurement.shot_notes
                                    else None
                                ),
                            }
                        )
                        
                        # Store raw numeric values for calculations
                        raw_measurements.append({
                            "speed": speed_value,
                            "power_factor": pf_value
                        })
                except Exception as e:
                    st.error(
                        f"Error loading measurements for session {session.display_name()}: {str(e)}"
                    )

            if all_measurements:
                # Display measurements table
                measurements_df = pd.DataFrame(all_measurements)
                st.dataframe(
                    measurements_df,
                    use_container_width=True,
                    hide_index=True)

                # Show summary stats
                if len(raw_measurements) > 0:
                    st.subheader(" Summary Statistics")

                    # Extract numeric data for calculations
                    speeds = [
                        m["speed"]
                        for m in raw_measurements
                        if m["speed"] is not None
                    ]
                    power_factors = [
                        m["power_factor"]
                        for m in raw_measurements
                        if m["power_factor"] is not None
                    ]

                    if speeds:
                        # Calculate statistics
                        min_speed = min(speeds)
                        max_speed = max(speeds)
                        avg_speed = sum(speeds) / len(speeds)

                        # Calculate standard deviation
                        variance = sum(
                            (x - avg_speed) ** 2 for x in speeds) / len(speeds)
                        std_dev = variance**0.5

                        # Calculate spread (max - min)
                        spread = max_speed - min_speed

                        # Calculate average power factor
                        avg_power_factor = (
                            sum(power_factors) / len(power_factors)
                            if power_factors
                            else None
                        )

                        # Display in two rows of metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Min Speed", f"{min_speed:.1f} {speed_units}")
                        with col2:
                            st.metric("Max Speed", f"{max_speed:.1f} {speed_units}")
                        with col3:
                            st.metric("Average Speed", f"{avg_speed:.1f} {speed_units}")

                        col4, col5, col6 = st.columns(3)
                        with col4:
                            st.metric("Std Dev", f"{std_dev:.1f} {speed_units}")
                        with col5:
                            st.metric("Spread", f"{spread:.1f} {speed_units}")
                        with col6:
                            if avg_power_factor is not None:
                                st.metric(
                                    "Avg Power Factor", f"{avg_power_factor:.1f}")
                            else:
                                st.metric("Avg Power Factor", "N/A")

                        # Add histogram
                        st.subheader(" Velocity Distribution")
                        import matplotlib.pyplot as plt

                        fig, ax = plt.subplots(figsize=(10, 6))

                        # Create histogram
                        n_bins = min(
                            20, len(speeds) // 2) if len(speeds) > 10 else 10
                        counts, bins, patches = ax.hist(
                            speeds,
                            bins=n_bins,
                            alpha=0.7,
                            color="steelblue",
                            edgecolor="black",
                        )

                        # Add vertical lines for statistics
                        ax.axvline(
                            avg_speed,
                            color="red",
                            linestyle="--",
                            linewidth=2,
                            label=f"Average: {avg_speed:.1f} {speed_units}",
                        )
                        ax.axvline(
                            avg_speed - std_dev,
                            color="orange",
                            linestyle=":",
                            linewidth=2,
                            label=f"-1 sigma: {avg_speed - std_dev:.1f} {speed_units}",
                        )
                        ax.axvline(
                            avg_speed + std_dev,
                            color="orange",
                            linestyle=":",
                            linewidth=2,
                            label=f"+1 sigma: {avg_speed + std_dev:.1f} {speed_units}",
                        )

                        # Formatting
                        ax.set_xlabel(f"Velocity ({speed_units})", fontsize=12)
                        ax.set_ylabel("Frequency", fontsize=12)
                        ax.set_title(
                            "Shot Velocity Distribution",
                            fontsize=14,
                            fontweight="bold")
                        ax.grid(True, alpha=0.3)
                        ax.legend()

                        # Display the plot
                        st.pyplot(fig)
                        plt.close()
            else:
                st.info("No measurement data found for selected sessions.")

    except Exception as e:
        st.error(f"Error loading logs: {str(e)}")
