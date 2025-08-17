import math
import uuid
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from .service import ChronographService


def render_chronograph_import_tab(user, supabase, bucket):
    """Render Garmin file upload section"""

    # Upload and parse Excel
    uploaded_file = st.file_uploader("Upload Garmin Xero Excel File", type=["xlsx"])
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        file_name = f"{user['email']}/garmin/{uploaded_file.name}"

        # Try to upload file, handle duplicate error
        try:
            supabase.storage.from_(bucket).upload(
                file_name, file_bytes, {"content-type": uploaded_file.type}
            )
        except Exception as e:
            if "already exists" in str(e) or "409" in str(e):
                st.error(f"❌ File '{uploaded_file.name}' already exists in storage.")
                st.info(
                    "💡 Go to the 'My Files' tab to delete the existing file if you want to re-upload it."
                )
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
            bullet_grain = (
                float(parts[1].strip().replace("gr", "")) if len(parts) > 1 else None
            )

            header_row = 1
            data = df.iloc[header_row + 1 :].dropna(subset=[1])
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
                            if " at " in cell_str and any(
                                month in cell_str
                                for month in [
                                    "Jan",
                                    "Feb",
                                    "Mar",
                                    "Apr",
                                    "May",
                                    "Jun",
                                    "Jul",
                                    "Aug",
                                    "Sep",
                                    "Oct",
                                    "Nov",
                                    "Dec",
                                ]
                            ):
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

            # Extract session date for use in measurements
            session_date = (
                pd.to_datetime(session_timestamp).date().isoformat()
                if session_timestamp
                else None
            )

            # Initialize chronograph service
            chrono_service = ChronographService(supabase)

            # Check if a session already exists at this date/time for this user
            if chrono_service.session_exists(user["id"], sheet, session_timestamp):
                st.warning(
                    f"⚠️ Session already exists for {pd.to_datetime(session_timestamp).strftime('%Y-%m-%d %H:%M')} - skipping sheet '{sheet}'"
                )
                continue

            # Helper function to safely convert to float, returning None for NaN/invalid values
            def safe_float(value):
                try:
                    if pd.isna(value) or value == "" or value is None:
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
                    if pd.isna(value) or value == "" or value is None:
                        return None
                    return int(
                        float(value)
                    )  # Convert via float first to handle "1.0" format
                except (ValueError, TypeError):
                    return None

            session_id = str(uuid.uuid4())
            session_data = {
                "id": session_id,
                "user_id": user["id"],
                "tab_name": sheet,
                "bullet_type": bullet_type,
                "bullet_grain": bullet_grain,
                "datetime_local": session_timestamp,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "file_path": file_name,
            }
            chrono_service.create_session(session_data)

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
                        time_str = time_str.replace(
                            "\u202f", " "
                        )  # Non-breaking thin space
                        time_str = time_str.replace("\u00a0", " ")  # Non-breaking space
                        time_str = time_str.replace("\u2009", " ")  # Thin space
                        time_str = time_str.strip()
                        return time_str if time_str else None

                    def create_datetime_local(time_value, session_timestamp):
                        time_str = clean_time_string(time_value)
                        if not time_str:
                            return None
                        try:
                            # Get session date
                            if session_timestamp:
                                session_date = pd.to_datetime(
                                    session_timestamp
                                ).strftime("%Y-%m-%d")
                            else:
                                session_date = pd.Timestamp.now().strftime("%Y-%m-%d")

                            # Combine date with time
                            datetime_str = f"{session_date} {time_str}"
                            return pd.to_datetime(datetime_str).isoformat()
                        except:
                            return None

                    # Extract time component for time_local field
                    time_str = clean_time_string(row.get("Time"))
                    time_local = None
                    if time_str:
                        try:
                            time_local = (
                                pd.to_datetime(time_str, format="%H:%M:%S")
                                .time()
                                .isoformat()
                            )
                        except:
                            try:
                                time_local = pd.to_datetime(time_str).time().isoformat()
                            except:
                                time_local = None

                    measurement_data = {
                        "user_email": user["email"],
                        "user_id": user["id"],
                        "chrono_session_id": session_id,
                        "shot_number": shot_number,
                        "speed_fps": speed_fps,
                        "delta_avg_fps": safe_float(row.get("Δ AVG (FPS)")),
                        "ke_ft_lb": safe_float(row.get("KE (FT-LB)")),
                        "power_factor": safe_float(row.get("Power Factor (kgr⋅ft/s)")),
                        "datetime_local": create_datetime_local(
                            row.get("Time"), session_timestamp
                        ),
                        "clean_bore": (
                            bool(row.get("Clean Bore"))
                            if "Clean Bore" in row
                            and not pd.isna(row.get("Clean Bore"))
                            else None
                        ),
                        "cold_bore": (
                            bool(row.get("Cold Bore"))
                            if "Cold Bore" in row and not pd.isna(row.get("Cold Bore"))
                            else None
                        ),
                        "shot_notes": (
                            str(row.get("Shot Notes"))
                            if "Shot Notes" in row
                            and not pd.isna(row.get("Shot Notes"))
                            else None
                        ),
                    }

                    chrono_service.create_measurement(measurement_data)
                    valid_measurements += 1

                except Exception as e:
                    st.warning(f"Skipped row {shot_number}: {e}")
                    skipped_measurements += 1

            # Calculate and update session summary statistics
            if valid_measurements > 0:
                # Get all measurements for this session to calculate stats
                speeds = chrono_service.get_measurements_for_stats(
                    user["id"], session_id
                )

                if speeds:
                    avg_speed = sum(speeds) / len(speeds)
                    min_speed = min(speeds)
                    max_speed = max(speeds)

                    # Calculate standard deviation
                    std_dev = 0
                    if len(speeds) > 1:
                        variance = sum((x - avg_speed) ** 2 for x in speeds) / len(
                            speeds
                        )
                        std_dev = variance**0.5

                    # Update the chrono_sessions record with calculated stats
                    stats = {
                        "shot_count": len(speeds),
                        "avg_speed_fps": avg_speed,
                        "std_dev_fps": std_dev,
                        "min_speed_fps": min_speed,
                        "max_speed_fps": max_speed,
                    }
                    chrono_service.update_session_stats(session_id, stats)

            # Show upload summary
            if skipped_measurements > 0:
                st.warning(
                    f"⚠️ Processed {valid_measurements} measurements, skipped {skipped_measurements} rows with missing data"
                )
            else:
                st.success(
                    f"✅ Successfully processed {valid_measurements} measurements"
                )

        st.success("Upload complete!")
