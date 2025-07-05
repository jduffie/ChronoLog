import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, timezone
import math

def render_upload_tab(user, supabase, bucket):
    """Render the Upload Files tab"""
    st.header("📤 Upload Files")
    
    # Create two columns for different upload types
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Garmin Xero Chronograph")
        render_garmin_upload(user, supabase, bucket)
    
    with col2:
        st.subheader("🌤️ Weather Data (Kestrel)")
        render_weather_upload(user, supabase, bucket)

def render_garmin_upload(user, supabase, bucket):
    """Render Garmin file upload section"""
    
    # Upload and parse Excel
    uploaded_file = st.file_uploader("Upload Garmin Xero Excel File", type=["xlsx"])
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        file_name = f"{user['email']}/garmin/{uploaded_file.name}"
        
        # Try to upload file, handle duplicate error
        try:
            supabase.storage.from_(bucket).upload(file_name, file_bytes, {"content-type": uploaded_file.type})
        except Exception as e:
            if "already exists" in str(e) or "409" in str(e):
                st.error(f"❌ File '{uploaded_file.name}' already exists in storage.")
                st.info("💡 Go to the 'My Files' tab to delete the existing file if you want to re-upload it.")
                return
            else:
                st.error(f"❌ Error uploading file: {e}")
                return

        xls = pd.ExcelFile(uploaded_file)
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
            bullet_meta = df.iloc[0, 0]
            parts = bullet_meta.split(",")
            bullet_type = parts[0].strip()
            bullet_grain = float(parts[1].strip().replace("gr", "")) if len(parts) > 1 else None

            header_row = 1
            data = df.iloc[header_row+1:].dropna(subset=[1])
            data.columns = df.iloc[header_row]
            
            # Extract session timestamp from the DATE cell at the bottom of the sheet
            session_timestamp = None
            try:
                # Look for the date in the last few rows of the sheet
                for i in range(len(df) - 1, max(len(df) - 10, 0), -1):
                    for col in range(df.shape[1]):
                        cell_value = df.iloc[i, col]
                        if pd.notna(cell_value):
                            cell_str = str(cell_value).strip()
                            # Look for date patterns like "May 26, 2025 at 11:01 AM"
                            if " at " in cell_str and any(month in cell_str for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                                try:
                                    # Parse the date string
                                    parsed_date = pd.to_datetime(cell_str)
                                    session_timestamp = parsed_date.isoformat()
                                    break
                                except:
                                    continue
                    if session_timestamp:
                        break
            except:
                pass
            
            # Fall back to current date if we couldn't extract from sheet
            if not session_timestamp:
                session_timestamp = datetime.now(timezone.utc).isoformat()

            # Check if a session already exists at this date/time for this user
            existing_session_response = supabase.table("chrono_sessions").select("id").eq("user_email", user["email"]).eq("tab_name", sheet).eq("datetime_local", session_timestamp).execute()
            
            if existing_session_response.data:
                st.warning(f"⚠️ Session already exists for {pd.to_datetime(session_timestamp).strftime('%Y-%m-%d %H:%M')} - skipping sheet '{sheet}'")
                continue

            # Helper function to safely convert to float, returning None for NaN/invalid values
            def safe_float(value):
                try:
                    if pd.isna(value) or value == '' or value is None:
                        return None
                    float_val = float(value)
                    if math.isnan(float_val):
                        return None
                    return float_val
                except (ValueError, TypeError):
                    return None

            # Helper function to safely convert to int
            def safe_int(value):
                try:
                    if pd.isna(value) or value == '' or value is None:
                        return None
                    return int(float(value))  # Convert via float first to handle "1.0" format
                except (ValueError, TypeError):
                    return None

            session_id = str(uuid.uuid4())
            supabase.table("chrono_sessions").insert({
                "id": session_id,
                "user_email": user["email"],
                "tab_name": sheet,
                "bullet_type": bullet_type,
                "bullet_grain": bullet_grain,
                "datetime_local": session_timestamp,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "file_path": file_name
            }).execute()

            valid_measurements = 0
            skipped_measurements = 0

            for _, row in data.iterrows():
                # Validate required fields
                shot_number = safe_int(row.get("#"))
                speed_fps = safe_float(row.get("Speed (FPS)"))
                
                # Skip rows without essential data
                if shot_number is None or speed_fps is None:
                    skipped_measurements += 1
                    continue

                try:
                    # Clean time string and create datetime
                    def clean_time_string(time_value):
                        if pd.isna(time_value) or time_value is None:
                            return None
                        time_str = str(time_value)
                        # Replace non-breaking space and other Unicode spaces with regular space
                        time_str = time_str.replace('\u202f', ' ')  # Non-breaking thin space
                        time_str = time_str.replace('\u00a0', ' ')  # Non-breaking space
                        time_str = time_str.replace('\u2009', ' ')  # Thin space
                        time_str = time_str.strip()
                        return time_str if time_str else None

                    def create_datetime_local(time_value, session_timestamp):
                        time_str = clean_time_string(time_value)
                        if not time_str:
                            return None
                        try:
                            # Get session date
                            if session_timestamp:
                                session_date = pd.to_datetime(session_timestamp).strftime('%Y-%m-%d')
                            else:
                                session_date = pd.Timestamp.now().strftime('%Y-%m-%d')
                            
                            # Combine date with time
                            datetime_str = f"{session_date} {time_str}"
                            return pd.to_datetime(datetime_str).isoformat()
                        except:
                            return None

                    # Extract session date for chrono_measurements
                    session_date = pd.to_datetime(session_timestamp).date().isoformat() if session_timestamp else None
                    
                    # Extract time component for time_local field
                    time_str = clean_time_string(row.get("Time"))
                    time_local = None
                    if time_str:
                        try:
                            time_local = pd.to_datetime(time_str, format='%H:%M:%S').time().isoformat()
                        except:
                            try:
                                time_local = pd.to_datetime(time_str).time().isoformat()
                            except:
                                time_local = None
                    
                    measurement_data = {
                        "user_email": user["email"],
                        "tab_name": sheet,
                        "bullet_type": bullet_type,
                        "bullet_grain": bullet_grain,
                        "session_date": session_date,
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "file_path": file_name,
                        "shot_number": shot_number,
                        "speed_fps": speed_fps,
                        "delta_avg_fps": safe_float(row.get("Δ AVG (FPS)")),
                        "ke_ft_lb": safe_float(row.get("KE (FT-LB)")),
                        "power_factor": safe_float(row.get("Power Factor (kgr⋅ft/s)")),
                        "time_local": time_local,
                        "datetime_local": create_datetime_local(row.get("Time"), session_timestamp),
                        "clean_bore": bool(row.get("Clean Bore")) if "Clean Bore" in row and not pd.isna(row.get("Clean Bore")) else None,
                        "cold_bore": bool(row.get("Cold Bore")) if "Cold Bore" in row and not pd.isna(row.get("Cold Bore")) else None,
                        "shot_notes": str(row.get("Shot Notes")) if "Shot Notes" in row and not pd.isna(row.get("Shot Notes")) else None
                    }
                    
                    supabase.table("chrono_measurements").insert(measurement_data).execute()
                    valid_measurements += 1
                    
                except Exception as e:
                    st.warning(f"Skipped row {shot_number}: {e}")
                    skipped_measurements += 1

            # Calculate and update session summary statistics
            if valid_measurements > 0:
                # Get all measurements for this session to calculate stats
                session_measurements = supabase.table("chrono_measurements").select("speed_fps").eq("user_email", user["email"]).eq("tab_name", sheet).eq("session_date", session_date).execute()
                
                if session_measurements.data:
                    speeds = [m['speed_fps'] for m in session_measurements.data if m.get('speed_fps') is not None]
                    
                    if speeds:
                        avg_speed = sum(speeds) / len(speeds)
                        min_speed = min(speeds)
                        max_speed = max(speeds)
                        
                        # Calculate standard deviation
                        std_dev = 0
                        if len(speeds) > 1:
                            variance = sum((x - avg_speed) ** 2 for x in speeds) / len(speeds)
                            std_dev = variance ** 0.5
                        
                        # Update the chrono_sessions record with calculated stats
                        supabase.table("chrono_sessions").update({
                            "shot_count": len(speeds),
                            "avg_speed_fps": avg_speed,
                            "std_dev_fps": std_dev,
                            "min_speed_fps": min_speed,
                            "max_speed_fps": max_speed
                        }).eq("id", session_id).execute()

            # Show upload summary
            if skipped_measurements > 0:
                st.warning(f"⚠️ Processed {valid_measurements} measurements, skipped {skipped_measurements} rows with missing data")
            else:
                st.success(f"✅ Successfully processed {valid_measurements} measurements")

        st.success("Upload complete!")

def render_weather_upload(user, supabase, bucket):
    """Render weather file upload section"""
    
    # Upload and parse CSV
    uploaded_file = st.file_uploader("Upload Weather Data CSV File", type=["csv"], key="weather_upload")
    if uploaded_file:
        try:
            file_bytes = uploaded_file.getvalue()
            file_name = f"{user['email']}/kestrel/{uploaded_file.name}"

            # Try to upload file, handle duplicate error
            try:
                supabase.storage.from_(bucket).upload(file_name, file_bytes, {"content-type": "text/csv"})
            except Exception as upload_error:
                if "already exists" in str(upload_error) or "409" in str(upload_error):
                    st.error(f"❌ Weather file '{uploaded_file.name}' already exists in storage.")
                    st.info("💡 Go to the 'My Files' tab to delete the existing file if you want to re-upload it.")
                    return
                else:
                    st.error(f"❌ Error uploading weather file: {upload_error}")
                    return

            # Read the file as text and parse manually
            uploaded_file.seek(0)
            content = uploaded_file.getvalue().decode('utf-8')
            lines = content.strip().split('\n')
            
            if len(lines) < 6:
                st.error("❌ Invalid weather file format. File must have metadata and data rows.")
                return
            
            # Parse metadata from first 3 rows
            device_name = lines[0].split(',')[1] if ',' in lines[0] and len(lines[0].split(',')) > 1 else ""
            device_model = lines[1].split(',')[1] if ',' in lines[1] and len(lines[1].split(',')) > 1 else ""  
            serial_number = lines[2].split(',')[1] if ',' in lines[2] and len(lines[2].split(',')) > 1 else ""
            
            # Headers are in row 4 (index 3), data starts row 6 (index 5)
            headers = [h.strip() for h in lines[3].split(',')]
            
            # Process data rows (starting from index 5)
            data_rows = []
            for i in range(5, len(lines)):
                line = lines[i].strip()
                if line:  # Skip empty lines
                    row_data = [cell.strip() for cell in line.split(',')]
                    # Check if we have data in the first column (timestamp)
                    if len(row_data) > 0 and row_data[0] and row_data[0] != 'nan':
                        data_rows.append(row_data)
            
            if not data_rows:
                st.warning("⚠️ No data rows found in weather file.")
                st.info(f"Debug: Found {len(lines)} total lines, expected data starting from line 6")
                st.info(f"Debug: Device info - Name: {device_name}, Model: {device_model}, Serial: {serial_number}")
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
                    
                    # Check if measurement already exists (unique key: serial_number + timestamp)
                    existing_measurement = supabase.table("weather_measurements").select("id").eq("serial_number", serial_number).eq("measurement_timestamp", measurement_timestamp).execute()
                    
                    if existing_measurement.data:
                        skipped_measurements += 1
                        continue
                    
                    # Helper function to safely convert to float
                    def safe_float(value, default=None):
                        try:
                            if pd.isna(value) or value == '' or value is None:
                                return default
                            return float(value)
                        except (ValueError, TypeError):
                            return default
                    
                    # Create measurement record with all available fields
                    measurement_data = {
                        "user_email": user["email"],
                        "device_name": device_name,
                        "device_model": device_model,
                        "serial_number": serial_number,
                        "measurement_timestamp": measurement_timestamp,
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "file_path": file_name
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
                                "Notes": "notes"
                            }
                            
                            if header in field_mapping:
                                db_field = field_mapping[header]
                                # Convert numeric fields to float, keep text fields as string
                                if header in ["Temperature", "Wet Bulb Temp", "Relative Humidity", "Barometric Pressure", 
                                            "Altitude", "Station Pressure", "Wind Speed", "Heat Index", "Dew Point", 
                                            "Density Altitude", "Crosswind", "Headwind", "Compass Magnetic Direction", 
                                            "Compass True Direction", "Wind Chill"]:
                                    measurement_data[db_field] = safe_float(value)
                                else:
                                    measurement_data[db_field] = value if value else None
                    
                    # Insert into weather_measurements table
                    supabase.table("weather_measurements").insert(measurement_data).execute()
                    valid_measurements += 1
                    
                except Exception as e:
                    st.warning(f"Skipped weather measurement at {timestamp_str if 'timestamp_str' in locals() else 'unknown time'}: {e}")
                    skipped_measurements += 1
            
            # Show upload summary
            if skipped_measurements > 0:
                st.warning(f"⚠️ Processed {valid_measurements} weather measurements, skipped {skipped_measurements} rows")
            else:
                st.success(f"✅ Successfully processed {valid_measurements} weather measurements")
                
            # Display metadata summary
            st.info(f"📱 Device: {device_name} ({device_model}) - Serial: {serial_number}")
            
        except Exception as e:
            st.error(f"❌ Error processing weather file: {e}")