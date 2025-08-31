from datetime import datetime
from typing import Any, Dict, cast

import pandas as pd
import streamlit as st

from .service import WeatherService


def render_weather_logs_tab(user, supabase):
    """Render the Weather Logs tab showing weather sources and measurements"""
    st.header(" Weather Logs")

    try:
        # Initialize weather service
        weather_service = WeatherService(supabase)

        # Get all weather sources for the user
        sources = weather_service.get_sources_for_user(user["id"])

        if not sources:
            st.info(
                "No weather sources found. Import some Kestrel data files to get started!"
            )
            return

        # Get all measurements for the user
        measurements = weather_service.get_all_measurements_for_user(user["id"])

        # Detailed measurements with filtering
        st.subheader("️ Detailed Weather Measurements")

        if not measurements:
            st.info("No weather measurements found.")
            return

        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            source_options = ["All"] + [
                f"{source.display_name()}" for source in sources
            ]
            selected_source = st.selectbox("Filter by Weather Source", source_options)

        with col2:
            date_range = st.date_input(
                "Filter by Date Range", value=[], max_value=datetime.now().date()
            )

        with col3:
            # Limit number of records to display
            max_records = st.number_input(
                "Max Records to Display",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
            )

        # Apply filters
        filtered_measurements = measurements

        if selected_source != "All":
            # Find the selected source
            selected_source_obj = None
            for source in sources:
                if source.display_name() == selected_source:
                    selected_source_obj = source
                    break

            if selected_source_obj:
                filtered_measurements = [
                    m
                    for m in filtered_measurements
                    if m.weather_source_id == selected_source_obj.id
                ]

        if date_range:
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_measurements = [
                    m
                    for m in filtered_measurements
                    if start_date
                    <= pd.to_datetime(m.measurement_timestamp).date()
                    <= end_date
                ]
            elif len(date_range) == 1:
                target_date = date_range[0]
                filtered_measurements = [
                    m
                    for m in filtered_measurements
                    if pd.to_datetime(m.measurement_timestamp).date() == target_date
                ]

        # Limit records
        filtered_measurements = filtered_measurements[:max_records]

        # Group measurements by source and date for display
        if filtered_measurements:
            # Group by source first, then by date
            measurements_by_source = {}
            for measurement in filtered_measurements:
                source_id = measurement.weather_source_id
                if source_id not in measurements_by_source:
                    measurements_by_source[source_id] = {}

                date_key = pd.to_datetime(measurement.measurement_timestamp).strftime(
                    "%Y-%m-%d"
                )
                if date_key not in measurements_by_source[source_id]:
                    measurements_by_source[source_id][date_key] = []
                measurements_by_source[source_id][date_key].append(measurement)

            # Display each source group
            for source_id, dates_data in measurements_by_source.items():
                # Find the source object
                source_obj = None
                for source in sources:
                    if source.id == source_id:
                        source_obj = source
                        break

                if source_obj:
                    total_measurements = sum(
                        len(date_measurements)
                        for date_measurements in dates_data.values()
                    )

                    with st.expander(
                        f"📡 {source_obj.display_name()} ({total_measurements} measurements)",
                        expanded=True,
                    ):
                        st.write(f"**Device:** {source_obj.device_display()}")

                        # Display each date group within this source
                        for date_str, date_measurements in sorted(
                            dates_data.items(), reverse=True
                        ):
                            with st.expander(
                                f"📅 {date_str} ({len(date_measurements)} measurements)",
                                expanded=False,
                            ):

                                # Convert measurements to dict format for DataFrame
                                measurements_dict = []
                                for m in date_measurements:
                                    measurements_dict.append(
                                        {
                                            "measurement_timestamp": m.measurement_timestamp,
                                            "temperature_f": m.temperature_f,
                                            "relative_humidity_pct": m.relative_humidity_pct,
                                            "barometric_pressure_inhg": m.barometric_pressure_inhg,
                                            "wind_speed_mph": m.wind_speed_mph,
                                            "location_description": m.location_description,
                                        }
                                    )

                                # Create DataFrame for this date
                                df_date = pd.DataFrame(measurements_dict)

                                # Select and format columns for display
                                display_columns = [
                                    "measurement_timestamp",
                                    "temperature_f",
                                    "relative_humidity_pct",
                                    "barometric_pressure_inhg",
                                    "wind_speed_mph",
                                ]

                                # Only include columns that exist and have data
                                available_columns = []
                                column_renames = {}

                                for col in display_columns:
                                    if (
                                        col in df_date.columns
                                        and not df_date[col].isna().all()
                                    ):
                                        available_columns.append(col)
                                        if col == "measurement_timestamp":
                                            column_renames[col] = "Time"
                                        elif col == "temperature_f":
                                            column_renames[col] = "Temp (°F)"
                                        elif col == "relative_humidity_pct":
                                            column_renames[col] = "Humidity (%)"
                                        elif col == "barometric_pressure_inhg":
                                            column_renames[col] = "Pressure (inHg)"
                                        elif col == "wind_speed_mph":
                                            column_renames[col] = "Wind (mph)"

                                if available_columns:
                                    display_df = df_date[available_columns].copy()

                                    # Format timestamp
                                    if "measurement_timestamp" in display_df.columns:
                                        display_df["measurement_timestamp"] = (
                                            pd.to_datetime(
                                                display_df["measurement_timestamp"]
                                            ).dt.strftime("%Y-%m-%d %H:%M:%S")
                                        )

                                    # Round numeric columns
                                    numeric_columns = [
                                        "temperature_f",
                                        "relative_humidity_pct",
                                        "barometric_pressure_inhg",
                                        "wind_speed_mph",
                                    ]
                                    for col in numeric_columns:
                                        if col in display_df.columns:
                                            display_df[col] = display_df[col].round(1)

                                    # Rename columns
                                    display_df = display_df.rename(
                                        columns=column_renames
                                    )

                                    st.dataframe(display_df, use_container_width=True)

                                    # Show location if available
                                    if measurements_dict and measurements_dict[0].get(
                                        "location_description"
                                    ):
                                        st.write(
                                            f"**Location:** {measurements_dict[0]['location_description']}"
                                        )

                                    # Quick stats for this date
                                    if len(date_measurements) > 1:
                                        st.write("**Daily Summary:**")
                                        col1, col2, col3 = st.columns(3)

                                        with col1:
                                            if "temperature_f" in df_date.columns:
                                                temps = df_date[
                                                    "temperature_f"
                                                ].dropna()
                                                if not temps.empty:
                                                    st.write(
                                                        f"• Temp: {temps.min():.1f}°F - {temps.max():.1f}°F"
                                                    )

                                        with col2:
                                            if (
                                                "relative_humidity_pct"
                                                in df_date.columns
                                            ):
                                                humidity = df_date[
                                                    "relative_humidity_pct"
                                                ].dropna()
                                                if not humidity.empty:
                                                    st.write(
                                                        f"• Humidity: {humidity.min():.1f}% - {humidity.max():.1f}%"
                                                    )

                                        with col3:
                                            if "wind_speed_mph" in df_date.columns:
                                                wind = df_date[
                                                    "wind_speed_mph"
                                                ].dropna()
                                                if not wind.empty:
                                                    st.write(
                                                        f"• Wind: {wind.min():.1f} - {wind.max():.1f} mph"
                                                    )

                                    # View button for detailed analysis
                                    if st.button(
                                        f"View Detailed Analysis",
                                        key=f"view_weather_{source_obj.id}_{date_str}",
                                    ):
                                        # Update weather sources page state for navigation
                                        if (
                                            "weather_sources_page_state"
                                            not in st.session_state
                                        ):
                                            weather_state: Dict[str, Any] = {
                                                "selected_weather_source_id": None,
                                                "selected_weather_date": None,
                                                "edit_sources": {},
                                                "confirm_deletes": {},
                                            }
                                            st.session_state.weather_sources_page_state = (
                                                weather_state
                                            )

                                        # Type cast to avoid type checker warnings
                                        weather_state = cast(
                                            Dict[str, Any],
                                            st.session_state.weather_sources_page_state,
                                        )
                                        weather_state["selected_weather_source_id"] = (
                                            source_obj.id
                                        )
                                        weather_state["selected_weather_date"] = (
                                            date_str
                                        )
                                        st.info(
                                            "Date and source selected! Go to the 'View Log' tab to see detailed weather analysis."
                                        )
                                else:
                                    st.info(
                                        "No displayable weather data for this date."
                                    )
        else:
            st.info("No weather measurements match the selected filters.")

    except Exception as e:
        st.error(f"Error loading weather logs: {str(e)}")
