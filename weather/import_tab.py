from datetime import datetime, timezone
import os

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


def load_kestrel_units_mapping(supabase):
    """Load the Kestrel units mapping from Supabase table"""
    try:
        # Query the kestrel_unit_mappings table
        response = supabase.table("kestrel_unit_mappings").select("*").execute()
        
        # Create mapping from measurement name to unit info
        unit_mapping = {}
        for record in response.data:
            measurement = record['measurement']
            imperial_unit = record['imperial_units'].strip()
            metric_unit = record['metric_units'].strip()
            unit_mapping[measurement] = {
                'imperial': imperial_unit,
                'metric': metric_unit
            }
        
        return unit_mapping
    except Exception as e:
        st.error(f"Error loading Kestrel units mapping: {e}")
        return {}


def detect_column_units(headers, units_row, supabase):
    """Detect unit type for each column using Kestrel units mapping and actual CSV units"""
    # Load the mapping from Supabase
    unit_mapping = load_kestrel_units_mapping(supabase)
    column_units = {}
    
    for i, (header, unit) in enumerate(zip(headers, units_row)):
        unit = unit.strip()
        
        # Skip timestamp column
        if header == "FORMATTED DATE_TIME":
            column_units[i] = "timestamp"
            continue
            
        # Check if this header matches a known measurement type
        if header in unit_mapping:
            measurement_units = unit_mapping[header]
            
            # Check if the actual unit matches imperial or metric
            if unit == measurement_units['imperial']:
                if unit in ['°F']:
                    column_units[i] = "fahrenheit"
                elif unit in ['ft']:
                    column_units[i] = "feet"
                elif unit in ['mph']:
                    column_units[i] = "mph"
                elif unit in ['inHg']:
                    column_units[i] = "inhg"
                elif unit in ['%', 'Deg']:
                    column_units[i] = "no_conversion"
                else:
                    column_units[i] = "unknown"
            elif unit == measurement_units['metric']:
                if unit in ['°C']:
                    column_units[i] = "celsius"
                elif unit in ['m']:
                    column_units[i] = "meters"
                elif unit in ['m/s']:
                    column_units[i] = "mps"
                elif unit in ['hPa']:
                    column_units[i] = "hpa"
                elif unit in ['%', 'Deg']:
                    column_units[i] = "no_conversion"
                else:
                    column_units[i] = "unknown"
            else:
                column_units[i] = "unknown"
        else:
            # Unknown measurement type
            column_units[i] = "unknown"
    
    return column_units


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


    # Processing options
    st.write("### Processing Options")
    processing_mode = st.radio(
        "Choose processing mode",
        options=["Real-time", "Background"],
        index=0,
        help="Real-time shows progress updates. Background allows you to navigate away during import."
    )
    
    if processing_mode == "Background":
        st.info("🔄 Background mode: You can navigate away during import. Check back later for results.")
    
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
                    "❌ Invalid weather file format. File must have metadata, headers, units, and data rows."
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

            # Headers are in row 4 (index 3), units in row 5 (index 4), data starts row 6 (index 5)
            headers = [h.strip() for h in lines[3].split(",")]
            units_row = [u.strip() for u in lines[4].split(",")]

            # Detect units for each column using the mapping
            column_units = detect_column_units(headers, units_row, supabase)
            recognized_units = [u for u in column_units.values() if u not in ['unknown', 'timestamp']]
            st.info(f"🔍 Detected units for {len(recognized_units)} columns using Kestrel mapping")

            # Process data rows (starting from index 5)
            data_rows = []
            for i in range(5, len(lines)):
                line = lines[i].strip()
                if line:  # Skip empty lines
                    row_data = [cell.strip() for cell in line.split(",")]

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
                    user["id"],
                    device_name,
                    device_model,
                    serial_number,
                )
                source_id = selected_meter_id
            except Exception as e:
                st.error(f"❌ Failed to update weather meter with device info: {e}")
                return

            # Process measurements in batches
            if processing_mode == "Background":
                process_weather_data_background(data_rows, headers, column_units, user, source_id, file_name, weather_service)
            else:
                process_weather_data_realtime(data_rows, headers, column_units, user, source_id, file_name, weather_service)

        except Exception as e:
            st.error(f"❌ Error processing weather file: {e}")


def process_weather_data_realtime(data_rows, headers, column_units, user, source_id, file_name, weather_service):
    """Process weather data with real-time progress updates"""
    valid_measurements = 0
    skipped_measurements = 0
    total_rows = len(data_rows)
    
    # Show processing message and create progress bar
    st.info("🔄 **Processing weather measurements...**")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Process in batches of 50 records
    batch_size = 50
    batch_data = []
    
    for row_index, row_data in enumerate(data_rows):
        try:
            measurement_data = process_single_measurement(row_data, headers, column_units, user, source_id, file_name)
            if measurement_data:
                batch_data.append(measurement_data)
                
                # Process batch when it reaches batch_size or is the last record
                if len(batch_data) >= batch_size or row_index == len(data_rows) - 1:
                    try:
                        weather_service.create_measurements_batch(batch_data)
                        valid_measurements += len(batch_data)
                        batch_data = []  # Clear batch
                    except Exception as batch_error:
                        st.warning(f"Batch processing error: {batch_error}")
                        skipped_measurements += len(batch_data)
                        batch_data = []
            else:
                skipped_measurements += 1

        except Exception as e:
            skipped_measurements += 1
        
        # Update progress bar and status
        progress = (row_index + 1) / total_rows
        progress_bar.progress(progress)
        status_text.text(f"Processing record {row_index + 1} of {total_rows} - {valid_measurements} processed, {skipped_measurements} skipped")
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Show final results
    show_import_results(valid_measurements, skipped_measurements, source_id, user, weather_service)


def process_weather_data_background(data_rows, headers, column_units, user, source_id, file_name, weather_service):
    """Process weather data in background with batched commits"""
    
    # Store processing state in session
    if "weather_import_state" not in st.session_state:
        st.session_state.weather_import_state = {
            "status": "starting",
            "total_rows": len(data_rows),
            "processed": 0,
            "skipped": 0,
            "current_batch": 0
        }
    
    state = st.session_state.weather_import_state
    
    if state["status"] == "starting":
        st.info("🔄 **Starting background processing...**")
        state["status"] = "processing"
        
        # Process all data in larger batches
        batch_size = 100
        total_batches = (len(data_rows) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(data_rows))
            batch_rows = data_rows[start_idx:end_idx]
            
            batch_data = []
            batch_skipped = 0
            
            for row_data in batch_rows:
                try:
                    measurement_data = process_single_measurement(row_data, headers, column_units, user, source_id, file_name)
                    if measurement_data:
                        batch_data.append(measurement_data)
                    else:
                        batch_skipped += 1
                except:
                    batch_skipped += 1
            
            # Commit batch to database
            if batch_data:
                try:
                    weather_service.create_measurements_batch(batch_data)
                    state["processed"] += len(batch_data)
                except Exception as e:
                    state["skipped"] += len(batch_data)
            
            state["skipped"] += batch_skipped
            state["current_batch"] = batch_num + 1
        
        state["status"] = "completed"
        st.rerun()
    
    elif state["status"] == "processing":
        st.info(f"🔄 Processing batch {state['current_batch']}... ({state['processed']} processed, {state['skipped']} skipped)")
        
    elif state["status"] == "completed":
        show_import_results(state["processed"], state["skipped"], source_id, user, weather_service)
        # Clear state for next import
        del st.session_state.weather_import_state


def process_single_measurement(row_data, headers, column_units, user, source_id, file_name):
    """Process a single measurement row and return measurement data"""
    # Helper function to safely convert to float
    def safe_float(value, default=None):
        try:
            if pd.isna(value) or value == "" or value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    # Parse timestamp (first column)
    timestamp_str = row_data[0]
    if not timestamp_str:
        return None

    # Parse timestamp
    measurement_timestamp = pd.to_datetime(timestamp_str).isoformat()

    # Create measurement record with all available fields
    measurement_data = {
        "user_id": user["id"],
        "weather_source_id": source_id,
        "measurement_timestamp": measurement_timestamp,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "file_path": file_name,
    }

    # Map data columns to database fields
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

    for i, header in enumerate(headers):
        if i < len(row_data):
            value = row_data[i]

            # Skip the timestamp column (already processed)
            if header == "FORMATTED DATE_TIME":
                continue

            if header in field_mapping:
                base_field = field_mapping[header]
                raw_value = safe_float(value)
                column_unit = column_units.get(i, "unknown")
                
                # Handle temperature fields
                if header in ["Temperature", "Wet Bulb Temp", "Heat Index", "Dew Point", "Wind Chill"]:
                    if column_unit == "fahrenheit":
                        measurement_data[f"{base_field}_f"] = raw_value
                        if raw_value is not None:
                            measurement_data[f"{base_field}_c"] = fahrenheit_to_celsius(raw_value)
                    elif column_unit == "celsius":
                        measurement_data[f"{base_field}_c"] = raw_value
                        if raw_value is not None:
                            measurement_data[f"{base_field}_f"] = celsius_to_fahrenheit(raw_value)
                
                # Handle pressure fields
                elif header in ["Barometric Pressure", "Station Pressure"]:
                    if column_unit == "inhg":
                        measurement_data[f"{base_field}_inhg"] = raw_value
                        if raw_value is not None:
                            measurement_data[f"{base_field}_hpa"] = inhg_to_hpa(raw_value)
                    elif column_unit == "hpa":
                        measurement_data[f"{base_field}_hpa"] = raw_value
                        if raw_value is not None:
                            measurement_data[f"{base_field}_inhg"] = hpa_to_inhg(raw_value)
                
                # Handle altitude fields
                elif header in ["Altitude", "Density Altitude"]:
                    if column_unit == "feet":
                        measurement_data[f"{base_field}_ft"] = raw_value
                        if raw_value is not None:
                            measurement_data[f"{base_field}_m"] = feet_to_meters(raw_value)
                    elif column_unit == "meters":
                        measurement_data[f"{base_field}_m"] = raw_value
                        if raw_value is not None:
                            measurement_data[f"{base_field}_ft"] = meters_to_feet(raw_value)
                
                # Handle wind speed fields
                elif header in ["Wind Speed", "Crosswind", "Headwind"]:
                    if column_unit == "mph":
                        measurement_data[f"{base_field}_mph"] = raw_value
                        if raw_value is not None:
                            measurement_data[f"{base_field}_mps"] = mph_to_mps(raw_value)
                    elif column_unit == "mps":
                        measurement_data[f"{base_field}_mps"] = raw_value
                        if raw_value is not None:
                            measurement_data[f"{base_field}_mph"] = mps_to_mph(raw_value)
                
                # Handle fields that don't need conversion (percentages, degrees)
                elif header in [
                    "Relative Humidity",
                    "Compass Magnetic Direction", 
                    "Compass True Direction",
                ] or column_unit == "no_conversion":
                    measurement_data[base_field] = raw_value
                
                # Handle text fields
                else:
                    measurement_data[base_field] = value if value else None

    return measurement_data


def show_import_results(valid_measurements, skipped_measurements, source_id, user, weather_service):
    """Display import results"""
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
        st.info(f"📱 Weather Source: Selected source")
