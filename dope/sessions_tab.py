import streamlit as st
import pandas as pd
import plotly.express as px


def render_sessions_tab(user, supabase):
    """Render the Analytics tab - table view with multi-selection and graphing"""
    st.header("📊 Analytics")

    try:
        # Get user's sessions with datetime_local from chrono_sessions
        # Note: We order by created_at as a fallback since we can't order by joined table fields in Supabase
        sessions_response = (
            supabase.table("dope_sessions")
            .select("*, chrono_sessions(datetime_local)")
            .eq("user_email", user["email"])
            .order("created_at", desc=True)
            .execute()
        )
        sessions = sessions_response.data

        if sessions:
            # Process sessions with aggregated measurement data
            session_summaries = []

            for session in sessions:
                # Get measurements for this session
                measurements_response = (
                    supabase.table("dope_measurements")
                    .select("*")
                    .eq("dope_session_id", session["id"])
                    .execute()
                )
                measurements = measurements_response.data

                # Prepare session timestamp using datetime_local from chrono_sessions
                chrono_session = session.get("chrono_sessions")
                if chrono_session and chrono_session.get("datetime_local"):
                    session_dt = pd.to_datetime(chrono_session["datetime_local"])
                    session_date = session_dt.strftime("%Y-%m-%d")
                    session_time = session_dt.strftime("%H:%M")
                elif session.get("created_at"):
                    # Fallback to created_at if datetime_local not available
                    session_dt = pd.to_datetime(session["created_at"])
                    session_date = session_dt.strftime("%Y-%m-%d")
                    session_time = session_dt.strftime("%H:%M")
                else:
                    session_date = "N/A"
                    session_time = "N/A"

                # Calculate statistics from measurements
                shot_count = len(measurements) if measurements else 0
                avg_velocity = std_velocity = velocity_spread = "N/A"

                if measurements and shot_count > 0:
                    speeds = [
                        m["speed_fps"]
                        for m in measurements
                        if m.get("speed_fps") is not None
                    ]
                    if speeds:
                        avg_velocity = f"{sum(speeds) / len(speeds):.1f}"
                        if len(speeds) > 1:
                            mean_speed = sum(speeds) / len(speeds)
                            variance = sum((x - mean_speed) ** 2 for x in speeds) / len(
                                speeds
                            )
                            std_velocity = f"{variance ** 0.5:.1f}"
                            velocity_spread = f"{max(speeds) - min(speeds):.1f}"
                        else:
                            std_velocity = "0.0"
                            velocity_spread = "0.0"

                row_data = {
                    "Date": session_date,
                    "Time": session_time,
                    "Session Name": session.get("session_name", "N/A"),
                    "Bullet Type": session.get("bullet_type", "N/A"),
                    "Bullet Weight (gr)": session.get("bullet_grain", "N/A"),
                    "Shot Count": shot_count,
                    "Avg Velocity (fps)": avg_velocity,
                    "Std Dev (fps)": std_velocity,
                    "Velocity Spread (fps)": velocity_spread,
                }
                session_summaries.append(row_data)

            # Create DataFrame and display
            if session_summaries:
                sessions_df = pd.DataFrame(session_summaries)
                session_lookup = {}  # For mapping display rows to session data

                # Map session summaries to original session data
                for i, session in enumerate(sessions):
                    session_lookup[i] = session

                st.markdown("### Session Summary")
                st.write(f"Total sessions: {len(sessions)}")
                st.info(
                    "💡 Select one or more rows to view combined metrics and graphs"
                )

                # Display the sessions table with multi-selection
                selected_rows = st.dataframe(
                    sessions_df,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="multi-row",
                    column_config={
                        "Date": st.column_config.DateColumn("Date"),
                        "Time": st.column_config.TextColumn("Time"),
                        "Session Name": st.column_config.TextColumn("Session Name"),
                        "Bullet Type": st.column_config.TextColumn("Bullet Type"),
                        "Bullet Weight (gr)": st.column_config.NumberColumn(
                            "Bullet Weight (gr)", format="%.1f"
                        ),
                        "Shot Count": st.column_config.NumberColumn("Shot Count"),
                        "Avg Velocity (fps)": st.column_config.TextColumn(
                            "Avg Velocity (fps)"
                        ),
                        "Std Dev (fps)": st.column_config.TextColumn("Std Dev (fps)"),
                        "Velocity Spread (fps)": st.column_config.TextColumn(
                            "Velocity Spread (fps)"
                        ),
                    },
                )

                # Handle multi-row selection - show combined metrics and graphs
                if selected_rows.selection.rows:
                    selected_indices = selected_rows.selection.rows
                    selected_sessions = [
                        session_lookup[i]
                        for i in selected_indices
                        if i in session_lookup
                    ]

                    if selected_sessions:
                        st.markdown("---")
                        st.markdown(
                            f"### Combined Metrics ({len(selected_sessions)} sessions selected)"
                        )

                        # Collect all measurements from selected sessions
                        all_measurements = []
                        session_data = []

                        for session in selected_sessions:
                            measurements_response = (
                                supabase.table("dope_measurements")
                                .select("*")
                                .eq("dope_session_id", session["id"])
                                .execute()
                            )
                            measurements = measurements_response.data

                            if measurements:
                                for measurement in measurements:
                                    # Add session info to each measurement
                                    measurement["session_name"] = session.get(
                                        "session_name", "N/A"
                                    )
                                    measurement["bullet_type"] = session.get(
                                        "bullet_type", "N/A"
                                    )
                                    measurement["bullet_grain"] = session.get(
                                        "bullet_grain", "N/A"
                                    )
                                    measurement["created_at"] = session.get(
                                        "created_at", "N/A"
                                    )
                                    all_measurements.append(measurement)

                                # Collect session summary data
                                session_summary = {
                                    "session_name": session.get("session_name", "N/A"),
                                    "bullet_type": session.get("bullet_type", "N/A"),
                                    "bullet_grain": session.get("bullet_grain", "N/A"),
                                    "created_at": session.get("created_at", "N/A"),
                                    "shot_count": len(measurements),
                                    "avg_velocity": (
                                        sum(
                                            m["speed_fps"]
                                            for m in measurements
                                            if m.get("speed_fps")
                                        )
                                        / len(measurements)
                                        if measurements
                                        else 0
                                    ),
                                    "measurements": measurements,
                                }
                                session_data.append(session_summary)

                        if all_measurements:
                            # Convert to DataFrame for analysis
                            measurements_df = pd.DataFrame(all_measurements)

                            # Overall statistics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total Shots", len(all_measurements))
                            with col2:
                                avg_vel = measurements_df["speed_fps"].mean()
                                st.metric("Combined Avg Velocity", f"{avg_vel:.1f} fps")
                            with col3:
                                std_vel = measurements_df["speed_fps"].std()
                                st.metric("Combined Std Dev", f"{std_vel:.1f} fps")
                            with col4:
                                vel_spread = (
                                    measurements_df["speed_fps"].max()
                                    - measurements_df["speed_fps"].min()
                                )
                                st.metric("Combined Spread", f"{vel_spread:.1f} fps")

                            # Create graphs
                            st.markdown("### Velocity Analysis")

                            # Tab layout for different graph types
                            tab1, tab2, tab3, tab4 = st.tabs(
                                [
                                    "Velocity Distribution",
                                    "Session Comparison",
                                    "Shot Sequence",
                                    "Statistics Summary",
                                ]
                            )

                            with tab1:
                                # Histogram of velocity distribution
                                fig_hist = px.histogram(
                                    measurements_df,
                                    x="speed_fps",
                                    color="session_name",
                                    title="Velocity Distribution by Session",
                                    labels={
                                        "speed_fps": "Velocity (fps)",
                                        "count": "Number of Shots",
                                    },
                                    nbins=20,
                                )
                                st.plotly_chart(fig_hist, use_container_width=True)

                            with tab2:
                                # Box plot comparing sessions
                                fig_box = px.box(
                                    measurements_df,
                                    x="session_name",
                                    y="speed_fps",
                                    title="Velocity Distribution by Session",
                                    labels={
                                        "speed_fps": "Velocity (fps)",
                                        "session_name": "Session",
                                    },
                                )
                                fig_box.update_layout(xaxis_tickangle=45)
                                st.plotly_chart(fig_box, use_container_width=True)

                            with tab3:
                                # Line plot of shot sequence
                                measurements_df["shot_sequence"] = (
                                    measurements_df.groupby("session_name").cumcount()
                                    + 1
                                )
                                fig_line = px.line(
                                    measurements_df,
                                    x="shot_sequence",
                                    y="speed_fps",
                                    color="session_name",
                                    title="Velocity by Shot Sequence",
                                    labels={
                                        "shot_sequence": "Shot Number",
                                        "speed_fps": "Velocity (fps)",
                                    },
                                )
                                st.plotly_chart(fig_line, use_container_width=True)

                            with tab4:
                                # Statistics summary table
                                stats_data = []
                                for session_summary in session_data:
                                    measurements = session_summary["measurements"]
                                    speeds = [
                                        m["speed_fps"]
                                        for m in measurements
                                        if m.get("speed_fps")
                                    ]
                                    if speeds:
                                        stats_data.append(
                                            {
                                                "Session": session_summary[
                                                    "session_name"
                                                ],
                                                "Bullet Type": session_summary[
                                                    "bullet_type"
                                                ],
                                                "Weight (gr)": session_summary[
                                                    "bullet_grain"
                                                ],
                                                "Shot Count": len(speeds),
                                                "Avg Velocity (fps)": f"{sum(speeds) / len(speeds):.1f}",
                                                "Std Dev (fps)": f"{(sum((x - sum(speeds) / len(speeds)) ** 2 for x in speeds) / len(speeds)) ** 0.5:.1f}",
                                                "Min (fps)": f"{min(speeds):.1f}",
                                                "Max (fps)": f"{max(speeds):.1f}",
                                                "Spread (fps)": f"{max(speeds) - min(speeds):.1f}",
                                            }
                                        )

                                if stats_data:
                                    stats_df = pd.DataFrame(stats_data)
                                    st.dataframe(
                                        stats_df,
                                        use_container_width=True,
                                        hide_index=True,
                                    )

                        else:
                            st.info("No measurement data found for selected sessions.")
            else:
                st.info("No sessions found.")
        else:
            st.info("No sessions found. Upload files first to create sessions.")

    except Exception as e:
        st.error(f"Error loading sessions: {e}")
