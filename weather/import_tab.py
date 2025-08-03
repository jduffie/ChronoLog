import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from .service import WeatherService


def render_weather_import_tab(user, supabase, bucket):
    """Render weather file upload section"""

    # Initialize weather service
    weather_service = WeatherService(supabase)

    # Get existing weather sources for the user
    sources = weather_service.get_sources_for_user(user["email"])

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
            f"📡 Selected: {selected_source.name} - {selected_source.device_display()}"
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
            st.info("📝 Upload options for this source type are not yet available.")


def render_file_upload(user, supabase, bucket, weather_service, selected_meter_id):
    """Render the file upload section"""

    # Get selected meter
    selected_source = weather_service.get_source_by_id(selected_meter_id, user["email"])

    if not selected_source:
        st.error("❌ Selected weather source not found. Please refresh the page.")
        return

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

            if len(lines) < 6:
                st.error(
                    "❌ Invalid weather file format. File must have metadata and data rows."
                )
                return

            # Parse metadata from first 3 rows
            device_name = (
                lines[0].split(",")[1]
                if "," in lines[0] and len(lines[0].split(",")) > 1
                else ""
            )
            device_model = (
                lines[1].split(",")[1]
                if "," in lines[1] and len(lines[1].split(",")) > 1
                else ""
            )
            serial_number = (
                lines[2].split(",")[1]
                if "," in lines[2] and len(lines[2].split(",")) > 1
                else ""
            )

            # Headers are in row 4 (index 3), data starts row 6 (index 5)
            headers = [h.strip() for h in lines[3].split(",")]

            # Process data rows (starting from index 5)
            data_rows = []
            for i in range(5, len(lines)):
                line = lines[i].strip()
                print("line-", line)
                if line:  # Skip empty lines
                    row_data = [cell.strip() for cell in line.split(",")]
                    print("    row_data", row_data)

                    # Check if we have data in the first column (timestamp)
                    if len(row_data) > 0 and row_data[0] and row_data[0] != "nan":
                        data_rows.append(row_data)

            if not data_rows:
                st.warning("⚠️ No data rows found in weather file.")
                st.info(
                    f"Debug: Found {len(lines)} total lines, expected data starting from line 6"
                )
                st.info(
                    f"Debug: Device info - Name: {device_name}, Model: {device_model}, Serial: {serial_number}"
                )
                return

            # Update selected meter with device info from CSV
            try:
                weather_service.update_source_with_device_info(
                    selected_meter_id,
                    user["email"],
                    device_name,
                    device_model,
                    serial_number,
                )
                source_id = selected_meter_id
            except Exception as e:
                st.error(f"❌ Failed to update weather meter with device info: {e}")
                return

            # Process each data row
            valid_measurements = 0
            skipped_measurements = 0

            for row_data in data_rows:
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
                        user["email"], source_id, measurement_timestamp
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
                        "user_email": user["email"],
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
                                "Temperature": "temperature_f",
                                "Wet Bulb Temp": "wet_bulb_temp_f",
                                "Relative Humidity": "relative_humidity_pct",
                                "Barometric Pressure": "barometric_pressure_inhg",
                                "Altitude": "altitude_ft",
                                "Station Pressure": "station_pressure_inhg",
                                "Wind Speed": "wind_speed_mph",
                                "Heat Index": "heat_index_f",
                                "Dew Point": "dew_point_f",
                                "Density Altitude": "density_altitude_ft",
                                "Crosswind": "crosswind_mph",
                                "Headwind": "headwind_mph",
                                "Compass Magnetic Direction": "compass_magnetic_deg",
                                "Compass True Direction": "compass_true_deg",
                                "Wind Chill": "wind_chill_f",
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
                                db_field = field_mapping[header]
                                # Convert numeric fields to float, keep text fields as string
                                if header in [
                                    "Temperature",
                                    "Wet Bulb Temp",
                                    "Relative Humidity",
                                    "Barometric Pressure",
                                    "Altitude",
                                    "Station Pressure",
                                    "Wind Speed",
                                    "Heat Index",
                                    "Dew Point",
                                    "Density Altitude",
                                    "Crosswind",
                                    "Headwind",
                                    "Compass Magnetic Direction",
                                    "Compass True Direction",
                                    "Wind Chill",
                                ]:
                                    measurement_data[db_field] = safe_float(value)
                                else:
                                    measurement_data[db_field] = (
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
                source = weather_service.get_source_by_id(source_id, user["email"])
                if source:
                    st.info(
                        f"📱 Weather Source: {source.display_name()} - {source.device_display()}"
                    )
                else:
                    st.info(
                        f"📱 Device: {device_name} ({device_model}) - Serial: {serial_number}"
                    )
            except:
                st.info(
                    f"📱 Device: {device_name} ({device_model}) - Serial: {serial_number}"
                )

        except Exception as e:
            st.error(f"❌ Error processing weather file: {e}")
