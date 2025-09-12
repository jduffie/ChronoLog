from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from .service import WeatherService

# Configuration for field mappings
FIELD_MAPPINGS = {
    "Temperature": {"db_field": "temperature", "type": "temperature"},
    "Wet Bulb Temp": {"db_field": "wet_bulb_temp", "type": "temperature"},
    "Relative Humidity": {"db_field": "relative_humidity_pct", "type": "percentage"},
    "Barometric Pressure": {"db_field": "barometric_pressure", "type": "pressure"},
    "Altitude": {"db_field": "altitude", "type": "altitude"},
    "Station Pressure": {"db_field": "station_pressure", "type": "pressure"},
    "Wind Speed": {"db_field": "wind_speed", "type": "wind_speed"},
    "Heat Index": {"db_field": "heat_index", "type": "temperature"},
    "Dew Point": {"db_field": "dew_point", "type": "temperature"},
    "Density Altitude": {"db_field": "density_altitude", "type": "altitude"},
    "Crosswind": {"db_field": "crosswind", "type": "wind_speed"},
    "Headwind": {"db_field": "headwind", "type": "wind_speed"},
    "Compass Magnetic Direction": {"db_field": "compass_magnetic_deg", "type": "degrees"},
    "Compass True Direction": {"db_field": "compass_true_deg", "type": "degrees"},
    "Wind Chill": {"db_field": "wind_chill", "type": "temperature"},
    "Data Type": {"db_field": "data_type", "type": "text"},
    "Record name": {"db_field": "record_name", "type": "text"},
    "Start time": {"db_field": "start_time", "type": "text"},
    "Duration (H:M:S)": {"db_field": "duration", "type": "text"},
    "Location description": {"db_field": "location_description", "type": "text"},
    "Location address": {"db_field": "location_address", "type": "text"},
    "Location coordinates": {"db_field": "location_coordinates", "type": "text"},
    "Notes": {"db_field": "notes", "type": "text"},
}

# Unit mapping configurations
IMPERIAL_UNIT_MAPPINGS = {
    '°F': "fahrenheit",
    'ft': "feet",
    'mph': "mph",
    'inHg': "inhg",
    '%': "no_conversion",
    'Deg': "no_conversion"
}

METRIC_UNIT_MAPPINGS = {
    '°C': "celsius",
    'm': "meters",
    'm/s': "mps",
    'hPa': "hpa",
    '%': "no_conversion",
    'Deg': "no_conversion"
}

# CSV structure constants
CSV_DEVICE_NAME_ROW = 0
CSV_DEVICE_MODEL_ROW = 1
CSV_SERIAL_NUMBER_ROW = 2
CSV_HEADERS_ROW = 3
CSV_UNITS_ROW = 4
CSV_DATA_START_ROW = 5


def fahrenheit_to_celsius(f_temp):
    """Convert Fahrenheit to Celsius"""
    if f_temp is None:
        return None
    return (f_temp - 32) * 5 / 9


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
    return (c_temp * 9 / 5) + 32


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
        response = supabase.table(
            "kestrel_unit_mappings").select("*").execute()

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


def _detect_imperial_unit(unit):
    """Extract imperial unit detection logic"""
    return IMPERIAL_UNIT_MAPPINGS.get(unit, "unknown")


def _detect_metric_unit(unit):
    """Extract metric unit detection logic"""
    return METRIC_UNIT_MAPPINGS.get(unit, "unknown")


def _parse_kestrel_file_structure(lines):
    """Parse Kestrel CSV file structure and extract metadata and data"""
    try:
        # Parse metadata from first 3 rows using constants
        device_name = (
            lines[CSV_DEVICE_NAME_ROW].split(",")[1]
            if "," in lines[CSV_DEVICE_NAME_ROW] and len(lines[CSV_DEVICE_NAME_ROW].split(",")) > 1
            else ""
        )
        device_model = (
            lines[CSV_DEVICE_MODEL_ROW].split(",")[1]
            if "," in lines[CSV_DEVICE_MODEL_ROW] and len(lines[CSV_DEVICE_MODEL_ROW].split(",")) > 1
            else ""
        )
        serial_number = (
            lines[CSV_SERIAL_NUMBER_ROW].split(",")[1]
            if "," in lines[CSV_SERIAL_NUMBER_ROW] and len(lines[CSV_SERIAL_NUMBER_ROW].split(",")) > 1
            else ""
        )

        # Extract headers and units using constants
        headers = [h.strip() for h in lines[CSV_HEADERS_ROW].split(",")]
        units_row = [u.strip() for u in lines[CSV_UNITS_ROW].split(",")]

        # Process data rows starting from CSV_DATA_START_ROW
        data_rows = []
        for i in range(CSV_DATA_START_ROW, len(lines)):
            line = lines[i].strip()
            if line:  # Skip empty lines
                row_data = [cell.strip() for cell in line.split(",")]

                # Check if we have data in the first column (timestamp)
                if len(row_data) > 0 and row_data[0] and row_data[0] != "nan":
                    data_rows.append(row_data)

        return device_name, device_model, serial_number, headers, units_row, data_rows

    except (IndexError, ValueError) as e:
        st.error(f"Error parsing CSV structure: {e}")
        return None


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
                column_units[i] = _detect_imperial_unit(unit)
            elif unit == measurement_units['metric']:
                column_units[i] = _detect_metric_unit(unit)
            else:
                column_units[i] = "unknown"
        else:
            # Unknown measurement type
            column_units[i] = "unknown"

    return column_units


def render_weather_import_tab(user, supabase, bucket):
    """Render weather import wizard"""
    st.header("Weather Data Import Wizard")

    # Initialize weather service
    weather_service = WeatherService(supabase)

    # Initialize wizard state only if it doesn't exist
    if "weather_wizard_state" not in st.session_state:
        st.session_state.weather_wizard_state = {
            "step": "source_selection",
            "selected_source_id": None,
            "new_source_data": None
        }

    wizard_state = st.session_state.weather_wizard_state

    # Step 1: Source Selection
    if wizard_state["step"] == "source_selection":
        st.subheader("Step 1: Choose Weather Source")
        st.write("Select an existing weather source or create a new one.")

        # Get existing sources
        sources = weather_service.get_sources_for_user(user["id"])

        # Source selection options
        source_choice = st.radio(
            "Choose an option:",
            options=["Select existing source", "Create new source"],
            index=0
        )

        if source_choice == "Select existing source":
            if not sources:
                st.warning(
                    "No existing weather sources found. Please create a new source.")
            else:
                # Show existing sources
                source_options = [
                    f"{s.name} - {s.device_display()}" for s in sources]
                selected_index = st.selectbox(
                    "Select weather source:",
                    options=range(len(source_options)),
                    format_func=lambda x: source_options[x]
                )

                if st.button("Continue with Selected Source", type="primary"):
                    wizard_state["selected_source_id"] = sources[selected_index].id
                    wizard_state["step"] = "file_upload"
                    st.rerun()

        else:  # Create new source
            st.write("#### Create New Weather Source")

            with st.form("new_source_form"):
                col1, col2 = st.columns(2)

                with col1:
                    source_type = st.selectbox(
                        "Source Type*",
                        options=["Meter"],
                        help="Select the type of weather source"
                    )

                with col2:
                    source_make = st.selectbox(
                        "Make*",
                        options=["Kestrel"],
                        help="Select the manufacturer"
                    )

                name = st.text_input(
                    "Source Name*",
                    placeholder="e.g., Range Kestrel, Hunting Meter",
                    help="Give your weather source a unique name"
                )

                if st.form_submit_button(
                    "Create Source and Continue",
                        type="primary"):
                    if not name.strip():
                        st.error("Source name is required!")
                    else:
                        try:
                            # Check if name already exists
                            existing = weather_service.get_source_by_name(
                                user["id"], name.strip())
                            if existing:
                                st.error(
                                    f"A weather source named '{name}' already exists!")
                            else:
                                source_data = {
                                    "user_id": user["id"],
                                    "name": name.strip(),
                                    "make": source_make,
                                    "source_type": source_type.lower(),
                                }

                                source_id = weather_service.create_source(
                                    source_data)
                                wizard_state["selected_source_id"] = source_id
                                wizard_state["step"] = "file_upload"
                                st.success(
                                    f"Weather source '{name}' created successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error creating weather source: {e}")

    # Step 2: File Upload
    elif wizard_state["step"] == "file_upload":
        # Get the selected source
        selected_source = weather_service.get_source_by_id(
            wizard_state["selected_source_id"], user["id"])

        if not selected_source:
            st.error("Selected source not found. Returning to source selection.")
            wizard_state["step"] = "source_selection"
            st.rerun()
            return

        st.subheader("Step 2: Upload Data File")
        st.success(
            f"Selected Source: {selected_source.name} - {selected_source.device_display()}")

        # Back button
        if st.button("← Back to Source Selection"):
            wizard_state["step"] = "source_selection"
            wizard_state["selected_source_id"] = None
            st.rerun()

        st.write("---")

        # Show appropriate upload based on source type
        if selected_source.make and selected_source.make.lower() == "kestrel":
            st.write("### Upload Kestrel CSV Files")
            render_file_upload(
                user,
                supabase,
                bucket,
                weather_service,
                selected_source.id)
        else:
            st.info("Upload options for this source type are not yet available.")


def render_file_upload(
        user,
        supabase,
        bucket,
        weather_service,
        selected_meter_id):
    """Render the file upload section"""

    # Get selected meter
    selected_source = weather_service.get_source_by_id(
        selected_meter_id, user["id"])

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
        st.info(
            "🔄 Background mode: You can navigate away during import. Check back later for results.")

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
                if "already exists" in str(
                        upload_error) or "409" in str(upload_error):
                    # File already exists - prompt user for action
                    st.warning(
                        f"⚠️ Weather file '{uploaded_file.name}' already exists in storage."
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(
                            "🔄 Overwrite File",
                            key="overwrite_file",
                                type="primary"):
                            try:
                                # Remove existing file and upload new one
                                supabase.storage.from_(
                                    bucket).remove([file_name])
                                supabase.storage.from_(bucket).upload(
                                    file_name, file_bytes, {"content-type": "text/csv"}
                                )
                                st.success("✅ File overwritten successfully!")
                                # Continue with processing by not returning
                                # here
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

            # Parse file structure
            parsed_data = _parse_kestrel_file_structure(lines)
            if not parsed_data:
                st.error("❌ Failed to parse file structure.")
                return

            device_name, device_model, serial_number, headers, units_row, data_rows = parsed_data

            # Detect units for each column using the mapping
            column_units = detect_column_units(headers, units_row, supabase)
            recognized_units = [
                u for u in column_units.values() if u not in [
                    'unknown', 'timestamp']]
            st.info(
                f"🔍 Detected units for {len(recognized_units)} columns using Kestrel mapping")

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
                st.error(
                    f"❌ Failed to update weather meter with device info: {e}")
                return

            # Process measurements in batches
            if processing_mode == "Background":
                process_weather_data_background(
                    data_rows,
                    headers,
                    column_units,
                    user,
                    source_id,
                    file_name,
                    weather_service)
            else:
                process_weather_data_realtime(
                    data_rows,
                    headers,
                    column_units,
                    user,
                    source_id,
                    file_name,
                    weather_service)

        except Exception as e:
            st.error(f"❌ Error processing weather file: {e}")


def process_weather_data_realtime(
        data_rows,
        headers,
        column_units,
        user,
        source_id,
        file_name,
        weather_service):
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
            measurement_data = process_single_measurement(
                row_data, headers, column_units, user, source_id, file_name)
            if measurement_data:
                batch_data.append(measurement_data)

                # Process batch when it reaches batch_size or is the last
                # record
                if len(batch_data) >= batch_size or row_index == len(
                        data_rows) - 1:
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
        status_text.text(
            f"Processing record {row_index + 1} of {total_rows} - {valid_measurements} processed, {skipped_measurements} skipped")

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    # Show final results
    show_import_results(
        valid_measurements,
        skipped_measurements,
        source_id,
        user,
        weather_service)


def process_weather_data_background(
        data_rows,
        headers,
        column_units,
        user,
        source_id,
        file_name,
        weather_service):
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
                    measurement_data = process_single_measurement(
                        row_data, headers, column_units, user, source_id, file_name)
                    if measurement_data:
                        batch_data.append(measurement_data)
                    else:
                        batch_skipped += 1
                except BaseException:
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
        st.info(
            f"🔄 Processing batch {state['current_batch']}... ({state['processed']} processed, {state['skipped']} skipped)")

    elif state["status"] == "completed":
        show_import_results(
            state["processed"],
            state["skipped"],
            source_id,
            user,
            weather_service)
        # Clear state for next import
        del st.session_state.weather_import_state


def _safe_float(value, default=None):
    """Helper function to safely convert to float"""
    try:
        if pd.isna(value) or value == "" or value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def _process_field_by_type(field_config, raw_value, column_unit, base_field):
    """Process field based on its type and unit"""
    field_data = {}
    field_type = field_config["type"]

    if field_type == "temperature":
        if column_unit == "fahrenheit":
            # Convert imperial to metric and store only metric
            if raw_value is not None:
                field_data[f"{base_field}_c"] = fahrenheit_to_celsius(raw_value)
        elif column_unit == "celsius":
            # Store metric directly
            field_data[f"{base_field}_c"] = raw_value

    elif field_type == "pressure":
        if column_unit == "inhg":
            # Convert imperial to metric and store only metric
            if raw_value is not None:
                field_data[f"{base_field}_hpa"] = inhg_to_hpa(raw_value)
        elif column_unit == "hpa":
            # Store metric directly
            field_data[f"{base_field}_hpa"] = raw_value

    elif field_type == "altitude":
        if column_unit == "feet":
            # Convert imperial to metric and store only metric
            if raw_value is not None:
                field_data[f"{base_field}_m"] = feet_to_meters(raw_value)
        elif column_unit == "meters":
            # Store metric directly
            field_data[f"{base_field}_m"] = raw_value

    elif field_type == "wind_speed":
        if column_unit == "mph":
            # Convert imperial to metric and store only metric
            if raw_value is not None:
                field_data[f"{base_field}_mps"] = mph_to_mps(raw_value)
        elif column_unit == "mps":
            # Store metric directly
            field_data[f"{base_field}_mps"] = raw_value

    elif field_type in ["percentage", "degrees"] or column_unit == "no_conversion":
        field_data[base_field] = raw_value

    elif field_type == "text":
        # For text fields, don't convert to float
        field_data[base_field] = raw_value if raw_value else None

    return field_data


def process_single_measurement(row_data, headers, column_units, user, source_id, file_name):
    """Process a single measurement row and return measurement data"""
    # Parse timestamp (first column)
    timestamp_str = row_data[0]
    if not timestamp_str:
        return None

    # Parse timestamp
    measurement_timestamp = pd.to_datetime(timestamp_str).isoformat()

    # Create measurement record with base fields
    measurement_data = {
        "user_id": user["id"],
        "weather_source_id": source_id,
        "measurement_timestamp": measurement_timestamp,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "file_path": file_name,
    }

    # Process each data column using field mappings
    for i, header in enumerate(headers):
        if i < len(row_data) and header != "FORMATTED DATE_TIME":
            value = row_data[i]

            if header in FIELD_MAPPINGS:
                field_config = FIELD_MAPPINGS[header]
                base_field = field_config["db_field"]
                column_unit = column_units.get(i, "unknown")

                # Handle text fields differently (don't convert to float)
                if field_config["type"] == "text":
                    raw_value = value if value else None
                else:
                    raw_value = _safe_float(value)

                # Process field based on type
                field_data = _process_field_by_type(field_config, raw_value, column_unit, base_field)
                measurement_data.update(field_data)

    return measurement_data


def show_import_results(
        valid_measurements,
        skipped_measurements,
        source_id,
        user,
        weather_service):
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
    except BaseException:
        st.info(f"📱 Weather Source: Selected source")
