from datetime import datetime

import pandas as pd
import streamlit as st

from .service import WeatherService
from utils.ui_formatters import format_temperature, format_pressure, format_wind_speed, format_altitude
from utils.unit_conversions import celsius_to_fahrenheit, hpa_to_inhg, mps_to_mph


def render_weather_view_tab(user, supabase):
    """Render the Weather View tab with filtering and detailed row selection"""

    # Initialize weather service
    weather_service = WeatherService(supabase)

    try:
        # Get all weather sources for the user
        sources = weather_service.get_sources_for_user(user["id"])

        if not sources:
            st.info(
                "No weather sources found. Go to the Sources tab to create weather sources and Import tab to upload data."
            )
            return

        with st.expander("**Filter**", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                # Weather source filter
                source_options = ["All"] + [source.display_name()
                                            for source in sources]
                selected_source = st.selectbox(
                    "Weather Source", source_options)

            with col2:
                # Date range filter
                date_range = st.date_input(
                    "Date Range",
                    value=[],
                    max_value=datetime.now().date(),
                    help="Select single date or date range"
                )

            with col3:
                # Record limit
                max_records = st.number_input(
                    "Max Records",
                    min_value=10,
                    max_value=500,
                    value=100,
                    step=10
                )

            # Apply filters using service
            selected_source_id = None
            if selected_source != "All":
                selected_source_obj = next(
                    (s for s in sources if s.display_name() == selected_source), None)
                if selected_source_obj:
                    selected_source_id = selected_source_obj.id

            start_date_str = None
            end_date_str = None
            if date_range:
                if len(date_range) == 2:
                    start_date_str = date_range[0].isoformat()
                    end_date_str = (
                        date_range[1].strftime("%Y-%m-%d") + "T23:59:59")
                elif len(date_range) == 1:
                    start_date_str = date_range[0].isoformat()
                    end_date_str = (
                        date_range[0].strftime("%Y-%m-%d") + "T23:59:59")

            # Get filtered measurements from service
            filtered_measurements = weather_service.get_measurements_filtered(
                user_id=user["id"],
                source_id=selected_source_id,
                start_date=start_date_str,
                end_date=end_date_str
            )

        # Apply record limit
        filtered_measurements = filtered_measurements[:max_records]

        if not filtered_measurements:
            st.info("No measurements match the selected filters.")
            return

        # Convert measurements to DataFrame for display
        table_data = []
        user_unit_system = user.get("unit_system", "Imperial")
        
        # Define column headers with units based on user preference
        temp_unit = "°F" if user_unit_system == "Imperial" else "°C"
        pressure_unit = "inHg" if user_unit_system == "Imperial" else "hPa"  
        wind_speed_unit = "mph" if user_unit_system == "Imperial" else "m/s"
        
        for i, measurement in enumerate(filtered_measurements):
            # Find source name
            source_name = "Unknown"
            for source in sources:
                if source.id == measurement.weather_source_id:
                    source_name = source.display_name()
                    break

            # Convert values without including units in the cell values
            if measurement.temperature_c is not None:
                temp_value = celsius_to_fahrenheit(measurement.temperature_c) if user_unit_system == "Imperial" else measurement.temperature_c
                temp_display = f"{temp_value:.1f}"
            else:
                temp_display = "N/A"
                
            if measurement.barometric_pressure_hpa is not None:
                pressure_value = hpa_to_inhg(measurement.barometric_pressure_hpa) if user_unit_system == "Imperial" else measurement.barometric_pressure_hpa
                pressure_display = f"{pressure_value:.2f}"
            else:
                pressure_display = "N/A"
                
            if measurement.wind_speed_mps is not None:
                wind_value = mps_to_mph(measurement.wind_speed_mps) if user_unit_system == "Imperial" else measurement.wind_speed_mps
                wind_display = f"{wind_value:.1f}"
            else:
                wind_display = "N/A"

            table_data.append(
                {
                    "index": i,
                    "Source": source_name,
                    "Timestamp": pd.to_datetime(
                        measurement.measurement_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    f"Temperature ({temp_unit})": temp_display,
                    f"Pressure ({pressure_unit})": pressure_display,
                    "Humidity (%)": round(
                        measurement.relative_humidity_pct,
                        1) if measurement.relative_humidity_pct is not None else None,
                    "Wind Dir (°)": round(
                        measurement.compass_true_deg,
                        0) if measurement.compass_true_deg is not None else None,
                    f"Wind Speed ({wind_speed_unit})": wind_display,
                })

        df = pd.DataFrame(table_data)

        # Display table with selection
        selected_rows = st.dataframe(
            df.drop(columns=["index"]),  # Hide index column
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Show detailed view for selected row
        if selected_rows.selection.rows:
            selected_index = selected_rows.selection.rows[0]
            selected_measurement = filtered_measurements[selected_index]

            # Find source for this measurement
            selected_source_obj = next(
                (s for s in sources if s.id == selected_measurement.weather_source_id), None)

            # Display measurement details in organized sections
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Basic Information:**")
                st.write(
                    f"• **Source:** {selected_source_obj.display_name() if selected_source_obj else 'Unknown'}")
                st.write(
                    f"• **Device:** {selected_source_obj.device_display() if selected_source_obj else 'Unknown'}")
                st.write(
                    f"• **Timestamp:** {pd.to_datetime(selected_measurement.measurement_timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
                if selected_measurement.uploaded_at:
                    st.write(
                        f"• **Uploaded:** {pd.to_datetime(selected_measurement.uploaded_at).strftime('%Y-%m-%d %H:%M:%S')}")

                st.write("**Temperature:**")
                if selected_measurement.temperature_c is not None:
                    st.write(
                        f"• **Temperature:** {format_temperature(selected_measurement.temperature_c, user_unit_system)}")
                if selected_measurement.heat_index_c is not None:
                    st.write(
                        f"• **Heat Index:** {format_temperature(selected_measurement.heat_index_c, user_unit_system)}")
                if selected_measurement.dew_point_c is not None:
                    st.write(
                        f"• **Dew Point:** {format_temperature(selected_measurement.dew_point_c, user_unit_system)}")
                if selected_measurement.wind_chill_c is not None:
                    st.write(
                        f"• **Wind Chill:** {format_temperature(selected_measurement.wind_chill_c, user_unit_system)}")

            with col2:
                st.write("**Atmospheric Conditions:**")
                if selected_measurement.barometric_pressure_hpa is not None:
                    st.write(
                        f"• **Barometric Pressure:** {format_pressure(selected_measurement.barometric_pressure_hpa, user_unit_system)}")
                if selected_measurement.station_pressure_hpa is not None:
                    st.write(
                        f"• **Station Pressure:** {format_pressure(selected_measurement.station_pressure_hpa, user_unit_system)}")
                if selected_measurement.relative_humidity_pct is not None:
                    st.write(
                        f"• **Humidity:** {selected_measurement.relative_humidity_pct:.1f}%")
                if selected_measurement.altitude_m is not None:
                    st.write(
                        f"• **Altitude:** {format_altitude(selected_measurement.altitude_m, user_unit_system)}")
                if selected_measurement.density_altitude_m is not None:
                    st.write(
                        f"• **Density Altitude:** {format_altitude(selected_measurement.density_altitude_m, user_unit_system)}")

                st.write("**Wind Conditions:**")
                if selected_measurement.wind_speed_mps is not None:
                    st.write(
                        f"• **Wind Speed:** {format_wind_speed(selected_measurement.wind_speed_mps, user_unit_system)}")
                if selected_measurement.compass_true_deg is not None:
                    st.write(
                        f"• **True Direction:** {selected_measurement.compass_true_deg:.0f}°")
                if selected_measurement.compass_magnetic_deg is not None:
                    st.write(
                        f"• **Magnetic Direction:** {selected_measurement.compass_magnetic_deg:.0f}°")
                if selected_measurement.crosswind_mps is not None:
                    st.write(
                        f"• **Crosswind:** {format_wind_speed(selected_measurement.crosswind_mps, user_unit_system)}")
                if selected_measurement.headwind_mps is not None:
                    st.write(
                        f"• **Headwind:** {format_wind_speed(selected_measurement.headwind_mps, user_unit_system)}")

            # Additional details if available
            if (selected_measurement.location_description or
                selected_measurement.location_address or
                selected_measurement.notes or
                    selected_measurement.record_name):

                st.write("**Additional Information:**")
                if selected_measurement.record_name:
                    st.write(
                        f"• **Record Name:** {selected_measurement.record_name}")
                if selected_measurement.location_description:
                    st.write(
                        f"• **Location:** {selected_measurement.location_description}")
                if selected_measurement.location_address:
                    st.write(
                        f"• **Address:** {selected_measurement.location_address}")
                if selected_measurement.notes:
                    st.write(f"• **Notes:** {selected_measurement.notes}")
                if selected_measurement.file_path:
                    st.write(
                        f"• **Source File:** {selected_measurement.file_path.split('/')[-1]}")

    except Exception as e:
        st.error(f"Error loading weather data: {str(e)}")
