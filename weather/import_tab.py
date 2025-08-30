from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from .service import WeatherService


def fahrenheit_to_celsius(f_temp):
    """Convert Fahrenheit to Celsius"""
    if f_temp is None:
        return None
    return (f_temp - 32) * 5/9


def feet_to_meters(feet):
    """Convert feet to meters"""
    if feet is None:
        return None
    return feet * 0.3048


def inhg_to_hpa(inhg):
    """Convert inches of mercury to hectopascals (hPa)"""
    if inhg is None:
        return None
    return inhg * 33.8639


def mph_to_mps(mph):
    """Convert miles per hour to meters per second"""
    if mph is None:
        return None
    return mph * 0.44704


def celsius_to_fahrenheit(c_temp):
    """Convert Celsius to Fahrenheit"""
    if c_temp is None:
        return None
    return (c_temp * 9/5) + 32


def meters_to_feet(meters):
    """Convert meters to feet"""
    if meters is None:
        return None
    return meters / 0.3048


def hpa_to_inhg(hpa):
    """Convert hectopascals (hPa) to inches of mercury"""
    if hpa is None:
        return None
    return hpa / 33.8639


def mps_to_mph(mps):
    """Convert meters per second to miles per hour"""
    if mps is None:
        return None
    return mps / 0.44704


def render_weather_import_tab(user, supabase, bucket):
    """Render weather file upload section"""

    # Initialize weather service
    weather_service = WeatherService(supabase)

    # Get existing weather sources for the user
    sources = weather_service.get_sources_for_user(user["id"])

    st.write("Import weather data from your weather devices.")

    if not sources:
        st.warning(
            "⚠️ No weather sources found. Please go to the **Sources** tab to create a weather source first."
        )
        return

    # Select Weather Source
    st.write("### Select Weather Source")

    # Create source options with names only
    source_options = [""] + [
        source.name for source in sources
    ]  # Empty string for initial undefined state

    selected_source_name = st.selectbox(
        "Choose weather source for this import",
        options=source_options,
        index=0,  # Start with empty selection
        help="Select which weather source to associate with the imported data",
    )

    # Only show upload options if a source is selected
    if selected_source_name:
        # Find the selected source object
        selected_source = next(s for s in sources if s.name == selected_source_name)

        # Show selected source info
        st.success(
            f" Selected: {selected_source.name} - {selected_source.device_display()}"
        )

        # Check if it's a Kestrel meter and show appropriate upload option
        if selected_source.make and selected_source.make.lower() == "kestrel":
            st.write("---")
            st.write("### Upload Kestrel CSV Files")
            render_file_upload(
                user, supabase, bucket, weather_service, selected_source.id
            )
        else:
            st.write("---")
            st.info(" Upload options for this source type are not yet available.")


def render_file_upload(user, supabase, bucket, weather_service, selected_meter_id):
    """Render the file upload section"""

    # Get selected meter
    selected_source = weather_service.get_source_by_id(selected_meter_id, user["id"])

    if not selected_source:
        st.error("❌ Selected weather source not found. Please refresh the page.")
        return

    # Unit selection
    st.write("### Data Unit System")
    unit_system = st.selectbox(
        "Select the unit system of your CSV data",
        options=["Imperial", "Metric"],
        index=0,  # Default to Imperial
        help="Choose Imperial for Fahrenheit/feet/mph/inHg or Metric for Celsius/meters/m/s/hPa"
    )

    # Upload and parse CSV
    uploaded_file = st.file_uploader(
        "Upload Kestrel CSV File", type=["csv"], key="weather_upload"
    )
    if uploaded_file:
        try:
            file_bytes = uploaded_file.getvalue()
            file_name = f"{user['email']}/kestrel/{uploaded_file.name}"

            # Try to upload file, handle duplicate error
            try:
                supabase.storage.from_(bucket).upload(
                    file_name, file_bytes, {"content-type": "text/csv"}
                )
            except Exception as upload_error:
                if "already exists" in str(upload_error) or "409" in str(upload_error):
                    # File already exists - prompt user for action
                    st.warning(
                        f"⚠️ Weather file '{uploaded_file.name}' already exists in storage."
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(
                            "🔄 Overwrite File", key="overwrite_file", type="primary"
                        ):
                            try:
                                # Remove existing file and upload new one
                                supabase.storage.from_(bucket).remove([file_name])
                                supabase.storage.from_(bucket).upload(
                                    file_name, file_bytes, {"content-type": "text/csv"}
                                )
                                st.success("✅ File overwritten successfully!")
                                # Continue with processing by not returning here
                            except Exception as overwrite_error:
                                st.error(
                                    f"❌ Error overwriting file: {overwrite_error}"
                                )
                                return

                    with col2:
                        if st.button("❌ Cancel Import", key="cancel_import"):
                            st.info(
                                "Import cancelled. You can go to the 'My Files' tab to manage existing files."
                            )
                            return

                    # If neither button was clicked, stop processing
                    if (
                        "overwrite_file" not in st.session_state
                        and "cancel_import" not in st.session_state
                    ):
                        return
                else:
                    st.error(f"❌ Error uploading weather file: {upload_error}")
                    return

            # Read the file as text and parse manually
            uploaded_file.seek(0)
            content = uploaded_file.getvalue().decode("utf-8")
            lines = content.strip().split("\n")

            if len(lines) < 2:
                st.error(
                    "❌ Invalid weather file format. File must have headers and data rows."
                )
                return

            # Headers are in row 1 (index 0), data starts row 2 (index 1)
            headers = [h.strip() for h in lines[0].split(",")]

            # Process data rows (starting from index 1)
            data_rows = []
            for i in range(1, len(lines)):
                line = lines[i].strip()
                if line:  # Skip empty lines
                    row_data = [cell.strip() for cell in line.split(",")]

                    # Check if we have data in the first column (timestamp)
                    if len(row_data) > 0 and row_data[0] and row_data[0] != "nan":
                        data_rows.append(row_data)

            if not data_rows:
                st.warning("⚠️ No data rows found in weather file.")
                st.info(
                    f"Debug: Found {len(lines)} total lines, headers: {headers[:5]}..."
                )
                return

            # Use selected source ID directly
            source_id = selected_meter_id

            # Process each data row with progress tracking
            valid_measurements = 0
            skipped_measurements = 0
            total_rows = len(data_rows)
            
            # Show processing message and create progress bar
            st.info("🔄 **Processing weather measurements...**")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for row_index, row_data in enumerate(data_rows):
                try:
                    # Parse timestamp (first column)
                    timestamp_str = row_data[0]
                    if not timestamp_str:
                        skipped_measurements += 1
                        continue

                    # Parse timestamp to check for duplicates
                    measurement_timestamp = pd.to_datetime(timestamp_str).isoformat()

                    # Check if measurement already exists using service
                    if weather_service.measurement_exists(
                        user["id"], source_id, measurement_timestamp
                    ):
                        skipped_measurements += 1
                        continue

                    # Helper function to safely convert to float
                    def safe_float(value, default=None):
                        try:
                            if pd.isna(value) or value == "" or value is None:
                                return default
                            return float(value)
                        except (ValueError, TypeError):
                            return default

                    # Create measurement record with all available fields
                    measurement_data = {
                        "user_id": user["id"],
                        "weather_source_id": source_id,
                        "measurement_timestamp": measurement_timestamp,
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "file_path": file_name,
                    }

                    # Map data columns to database fields (based on header names)
                    for i, header in enumerate(headers):
                        if i < len(row_data):
                            value = row_data[i]

                            # Skip the timestamp column (already processed)
                            if header == "FORMATTED DATE_TIME":
                                continue

                            # Map specific headers to database columns
                            field_mapping = {
                                "Temperature": "temperature",
                                "Wet Bulb Temp": "wet_bulb_temp",
                                "Relative Humidity": "relative_humidity_pct",
                                "Barometric Pressure": "barometric_pressure",
                                "Altitude": "altitude",
                                "Station Pressure": "station_pressure",
                                "Wind Speed": "wind_speed",
                                "Heat Index": "heat_index",
                                "Dew Point": "dew_point",
                                "Density Altitude": "density_altitude",
                                "Crosswind": "crosswind",
                                "Headwind": "headwind",
                                "Compass Magnetic Direction": "compass_magnetic_deg",
                                "Compass True Direction": "compass_true_deg",
                                "Wind Chill": "wind_chill",
                                "Data Type": "data_type",
                                "Record name": "record_name",
                                "Start time": "start_time",
                                "Duration (H:M:S)": "duration",
                                "Location description": "location_description",
                                "Location address": "location_address",
                                "Location coordinates": "location_coordinates",
                                "Notes": "notes",
                            }

                            if header in field_mapping:
                                base_field = field_mapping[header]
                                raw_value = safe_float(value)
                                
                                # Handle temperature fields
                                if header in ["Temperature", "Wet Bulb Temp", "Heat Index", "Dew Point", "Wind Chill"]:
                                    if unit_system == "Imperial":
                                        # Input is Fahrenheit, save F and convert to C
                                        measurement_data[f"{base_field}_f"] = raw_value
                                        if raw_value is not None:
                                            measurement_data[f"{base_field}_c"] = fahrenheit_to_celsius(raw_value)
                                    else:
                                        # Input is Celsius, save C and convert to F
                                        measurement_data[f"{base_field}_c"] = raw_value
                                        if raw_value is not None:
                                            measurement_data[f"{base_field}_f"] = celsius_to_fahrenheit(raw_value)
                                
                                # Handle pressure fields
                                elif header in ["Barometric Pressure", "Station Pressure"]:
                                    if unit_system == "Imperial":
                                        # Input is inHg, save inHg and convert to hPa
                                        measurement_data[f"{base_field}_inhg"] = raw_value
                                        if raw_value is not None:
                                            measurement_data[f"{base_field}_hpa"] = inhg_to_hpa(raw_value)
                                    else:
                                        # Input is hPa, save hPa and convert to inHg
                                        measurement_data[f"{base_field}_hpa"] = raw_value
                                        if raw_value is not None:
                                            measurement_data[f"{base_field}_inhg"] = hpa_to_inhg(raw_value)
                                
                                # Handle altitude fields
                                elif header in ["Altitude", "Density Altitude"]:
                                    if unit_system == "Imperial":
                                        # Input is feet, save ft and convert to m
                                        measurement_data[f"{base_field}_ft"] = raw_value
                                        if raw_value is not None:
                                            measurement_data[f"{base_field}_m"] = feet_to_meters(raw_value)
                                    else:
                                        # Input is meters, save m and convert to ft
                                        measurement_data[f"{base_field}_m"] = raw_value
                                        if raw_value is not None:
                                            measurement_data[f"{base_field}_ft"] = meters_to_feet(raw_value)
                                
                                # Handle wind speed fields
                                elif header in ["Wind Speed", "Crosswind", "Headwind"]:
                                    if unit_system == "Imperial":
                                        # Input is mph, save mph and convert to m/s
                                        measurement_data[f"{base_field}_mph"] = raw_value
                                        if raw_value is not None:
                                            measurement_data[f"{base_field}_mps"] = mph_to_mps(raw_value)
                                    else:
                                        # Input is m/s, save m/s and convert to mph
                                        measurement_data[f"{base_field}_mps"] = raw_value
                                        if raw_value is not None:
                                            measurement_data[f"{base_field}_mph"] = mps_to_mph(raw_value)
                                
                                # Handle other numeric fields (no conversion needed)
                                elif header in [
                                    "Relative Humidity",
                                    "Compass Magnetic Direction",
                                    "Compass True Direction",
                                ]:
                                    measurement_data[base_field] = raw_value
                                
                                # Handle text fields
                                else:
                                    measurement_data[base_field] = (
                                        value if value else None
                                    )

                    # Insert measurement using service
                    weather_service.create_measurement(measurement_data)
                    valid_measurements += 1

                except Exception as e:
                    st.warning(
                        f"Skipped weather measurement at {timestamp_str if 'timestamp_str' in locals() else 'unknown time'}: {e}"
                    )
                    skipped_measurements += 1
                
                # Update progress bar and status
                progress = (row_index + 1) / total_rows
                progress_bar.progress(progress)
                status_text.text(f"Processing record {row_index + 1} of {total_rows} - {valid_measurements} processed, {skipped_measurements} skipped")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

            # Import completed successfully

            # Show upload summary
            if skipped_measurements > 0:
                st.warning(
                    f"⚠️ Processed {valid_measurements} weather measurements, skipped {skipped_measurements} rows"
                )
            else:
                st.success(
                    f"✅ Successfully processed {valid_measurements} weather measurements"
                )

            # Display source information
            try:
                source = weather_service.get_source_by_id(source_id, user["id"])
                if source:
                    st.info(
                        f"📱 Weather Source: {source.display_name()} - {source.device_display()}"
                    )
            except:
                st.info(f"📱 Weather Source: {selected_source.name}")

        except Exception as e:
            st.error(f"❌ Error processing weather file: {e}")
