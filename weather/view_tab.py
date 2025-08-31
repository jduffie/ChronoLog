from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st

from .service import WeatherService


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
                source_options = ["All"] + [source.display_name() for source in sources]
                selected_source = st.selectbox("Weather Source", source_options)

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
                    (s for s in sources if s.display_name() == selected_source), None
                )
                if selected_source_obj:
                    selected_source_id = selected_source_obj.id

            start_date_str = None
            end_date_str = None
            if date_range:
                if len(date_range) == 2:
                    start_date_str = date_range[0].isoformat()
                    end_date_str = (date_range[1].strftime("%Y-%m-%d") + "T23:59:59")
                elif len(date_range) == 1:
                    start_date_str = date_range[0].isoformat()
                    end_date_str = (date_range[0].strftime("%Y-%m-%d") + "T23:59:59")

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
        for i, measurement in enumerate(filtered_measurements):
            # Find source name
            source_name = "Unknown"
            for source in sources:
                if source.id == measurement.weather_source_id:
                    source_name = source.display_name()
                    break

            table_data.append({
                "index": i,
                "Source": source_name,
                "Timestamp": pd.to_datetime(measurement.measurement_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "Temp (°F)": round(measurement.temperature_f, 1) if measurement.temperature_f else None,
                "Pressure (inHg)": round(measurement.barometric_pressure_inhg, 2) if measurement.barometric_pressure_inhg else None,
                "Humidity (%)": round(measurement.relative_humidity_pct, 1) if measurement.relative_humidity_pct else None,
                "Wind Dir (°)": round(measurement.compass_true_deg, 0) if measurement.compass_true_deg else None,
                "Wind Speed (mph)": round(measurement.wind_speed_mph, 1) if measurement.wind_speed_mph else None,
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
                (s for s in sources if s.id == selected_measurement.weather_source_id), None
            )
            
            # Display measurement details in organized sections
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Information:**")
                st.write(f"• **Source:** {selected_source_obj.display_name() if selected_source_obj else 'Unknown'}")
                st.write(f"• **Device:** {selected_source_obj.device_display() if selected_source_obj else 'Unknown'}")
                st.write(f"• **Timestamp:** {pd.to_datetime(selected_measurement.measurement_timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
                if selected_measurement.uploaded_at:
                    st.write(f"• **Uploaded:** {pd.to_datetime(selected_measurement.uploaded_at).strftime('%Y-%m-%d %H:%M:%S')}")
                
                st.write("**Temperature:**")
                if selected_measurement.temperature_f:
                    metric_temp = f" ({selected_measurement.temperature_c:.1f}°C)" if selected_measurement.temperature_c else ""
                    st.write(f"• **Temperature:** {selected_measurement.temperature_f:.1f}°F{metric_temp}")
                if selected_measurement.heat_index_f:
                    metric_heat = f" ({selected_measurement.heat_index_c:.1f}°C)" if selected_measurement.heat_index_c else ""
                    st.write(f"• **Heat Index:** {selected_measurement.heat_index_f:.1f}°F{metric_heat}")
                if selected_measurement.dew_point_f:
                    metric_dew = f" ({selected_measurement.dew_point_c:.1f}°C)" if selected_measurement.dew_point_c else ""
                    st.write(f"• **Dew Point:** {selected_measurement.dew_point_f:.1f}°F{metric_dew}")
                if selected_measurement.wind_chill_f:
                    metric_chill = f" ({selected_measurement.wind_chill_c:.1f}°C)" if selected_measurement.wind_chill_c else ""
                    st.write(f"• **Wind Chill:** {selected_measurement.wind_chill_f:.1f}°F{metric_chill}")

            with col2:
                st.write("**Atmospheric Conditions:**")
                if selected_measurement.barometric_pressure_inhg:
                    metric_pressure = f" ({selected_measurement.barometric_pressure_hpa:.1f} hPa)" if selected_measurement.barometric_pressure_hpa else ""
                    st.write(f"• **Barometric Pressure:** {selected_measurement.barometric_pressure_inhg:.2f} inHg{metric_pressure}")
                if selected_measurement.station_pressure_inhg:
                    metric_station = f" ({selected_measurement.station_pressure_hpa:.1f} hPa)" if selected_measurement.station_pressure_hpa else ""
                    st.write(f"• **Station Pressure:** {selected_measurement.station_pressure_inhg:.2f} inHg{metric_station}")
                if selected_measurement.relative_humidity_pct:
                    st.write(f"• **Humidity:** {selected_measurement.relative_humidity_pct:.1f}%")
                if selected_measurement.altitude_ft:
                    metric_alt = f" ({selected_measurement.altitude_m:.0f} m)" if selected_measurement.altitude_m else ""
                    st.write(f"• **Altitude:** {selected_measurement.altitude_ft:.0f} ft{metric_alt}")
                if selected_measurement.density_altitude_ft:
                    metric_density = f" ({selected_measurement.density_altitude_m:.0f} m)" if selected_measurement.density_altitude_m else ""
                    st.write(f"• **Density Altitude:** {selected_measurement.density_altitude_ft:.0f} ft{metric_density}")

                st.write("**Wind Conditions:**")
                if selected_measurement.wind_speed_mph:
                    metric_wind = f" ({selected_measurement.wind_speed_mps:.1f} m/s)" if selected_measurement.wind_speed_mps else ""
                    st.write(f"• **Wind Speed:** {selected_measurement.wind_speed_mph:.1f} mph{metric_wind}")
                if selected_measurement.compass_true_deg:
                    st.write(f"• **True Direction:** {selected_measurement.compass_true_deg:.0f}°")
                if selected_measurement.compass_magnetic_deg:
                    st.write(f"• **Magnetic Direction:** {selected_measurement.compass_magnetic_deg:.0f}°")
                if selected_measurement.crosswind_mph:
                    metric_cross = f" ({selected_measurement.crosswind_mps:.1f} m/s)" if selected_measurement.crosswind_mps else ""
                    st.write(f"• **Crosswind:** {selected_measurement.crosswind_mph:.1f} mph{metric_cross}")
                if selected_measurement.headwind_mph:
                    metric_head = f" ({selected_measurement.headwind_mps:.1f} m/s)" if selected_measurement.headwind_mps else ""
                    st.write(f"• **Headwind:** {selected_measurement.headwind_mph:.1f} mph{metric_head}")

            # Additional details if available
            if (selected_measurement.location_description or 
                selected_measurement.location_address or 
                selected_measurement.notes or
                selected_measurement.record_name):
                
                st.write("**Additional Information:**")
                if selected_measurement.record_name:
                    st.write(f"• **Record Name:** {selected_measurement.record_name}")
                if selected_measurement.location_description:
                    st.write(f"• **Location:** {selected_measurement.location_description}")
                if selected_measurement.location_address:
                    st.write(f"• **Address:** {selected_measurement.location_address}")
                if selected_measurement.notes:
                    st.write(f"• **Notes:** {selected_measurement.notes}")
                if selected_measurement.file_path:
                    st.write(f"• **Source File:** {selected_measurement.file_path.split('/')[-1]}")

    except Exception as e:
        st.error(f"Error loading weather data: {str(e)}")