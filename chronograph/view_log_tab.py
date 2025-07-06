import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from .models import ChronographSession, ChronographMeasurement
from .service import ChronographService

def render_view_log_tab(user, supabase):
    """Render the View Log tab for detailed session analysis"""
    st.header("🔍 View Chronograph Log")
    
    try:
        # Initialize service
        chrono_service = ChronographService(supabase)
        
        # Get all sessions for selection
        sessions = chrono_service.get_sessions_for_user(user["email"])
        
        if not sessions:
            st.info("No chronograph logs found. Import some data files to get started!")
            return
        
        # Session selector
        session_options = {
            s.display_name(): s.id
            for s in sessions
        }
        
        # Use selected session from session state if available
        default_session = None
        if 'selected_session_id' in st.session_state:
            for display_name, session_id in session_options.items():
                if session_id == st.session_state['selected_session_id']:
                    default_session = display_name
                    break
        
        selected_session_name = st.selectbox(
            "Select Session to View",
            options=list(session_options.keys()),
            index=list(session_options.keys()).index(default_session) if default_session else 0
        )
        
        if not selected_session_name:
            st.info("Please select a session to view.")
            return
        
        selected_session_id = session_options[selected_session_name]
        
        # Get session details
        session = next(s for s in sessions if s.id == selected_session_id)
        
        # Get measurements for this session using service
        measurements = chrono_service.get_measurements_for_session(user["email"], session.tab_name)
        
        if not measurements:
            st.warning("No measurements found for this session.")
            return
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame([{
            'shot_number': m.shot_number,
            'speed_fps': m.speed_fps,
            'delta_avg_fps': m.delta_avg_fps,
            'ke_ft_lb': m.ke_ft_lb,
            'power_factor': m.power_factor,
            'datetime_local': m.datetime_local,
            'clean_bore': m.clean_bore,
            'cold_bore': m.cold_bore,
            'shot_notes': m.shot_notes
        } for m in measurements])
        
        # Session header
        st.subheader(f"📊 {session.tab_name}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Bullet:** {session.bullet_type}")
            st.write(f"**Grain:** {session.bullet_grain}")
        with col2:
            st.write(f"**Date:** {session.datetime_local.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"**Shots:** {len(measurements)}")
        with col3:
            st.write(f"**Session ID:** {session.id[:8]}...")
            st.write(f"**File:** {session.file_name()}")
        
        # Statistics
        speeds = [m.speed_fps for m in measurements if m.speed_fps]
        if not speeds:
            st.warning("No speed data available for analysis.")
            return
        
        speeds_series = pd.Series(speeds)
        
        # Key Statistics
        st.subheader("📈 Key Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Average Speed", f"{speeds_series.mean():.1f} fps")
        with col2:
            st.metric("Standard Deviation", f"{speeds_series.std():.1f} fps")
        with col3:
            st.metric("Min Speed", f"{speeds_series.min():.1f} fps")
        with col4:
            st.metric("Max Speed", f"{speeds_series.max():.1f} fps")
        
        # Additional stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Range", f"{speeds_series.max() - speeds_series.min():.1f} fps")
        with col2:
            st.metric("Median", f"{speeds_series.median():.1f} fps")
        with col3:
            st.metric("Extreme Spread", f"{speeds_series.max() - speeds_series.min():.1f} fps")
        with col4:
            cv = (speeds_series.std() / speeds_series.mean()) * 100
            st.metric("CV %", f"{cv:.2f}%")
        
        # Charts
        st.subheader("📊 Data Visualization")
        
        # Create tabs for different views
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Speed Chart", "Histogram", "Shot String"])
        
        with chart_tab1:
            # Speed over shots
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df['shot_number'], df['speed_fps'], 'b-o', linewidth=2, markersize=4)
            ax.axhline(y=speeds_series.mean(), color='red', linestyle='--', label='Average')
            ax.axhline(y=speeds_series.mean() + speeds_series.std(), color='orange', linestyle=':', label='+1 SD')
            ax.axhline(y=speeds_series.mean() - speeds_series.std(), color='orange', linestyle=':', label='-1 SD')
            ax.set_xlabel('Shot Number')
            ax.set_ylabel('Velocity (fps)')
            ax.set_title('Velocity vs Shot Number')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        
        with chart_tab2:
            # Histogram
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(speeds, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax.axvline(x=speeds_series.mean(), color='red', linestyle='--', linewidth=2, label='Average')
            ax.set_xlabel('Velocity (fps)')
            ax.set_ylabel('Frequency')
            ax.set_title('Velocity Distribution')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        
        with chart_tab3:
            # Shot string with running statistics
            running_avg = speeds_series.expanding().mean()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df['shot_number'], df['speed_fps'], 'b-o', linewidth=2, markersize=4, label='Velocity')
            ax.plot(df['shot_number'], running_avg, 'r--', linewidth=2, label='Running Average')
            ax.set_xlabel('Shot Number')
            ax.set_ylabel('Velocity (fps)')
            ax.set_title('Shot String Analysis')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        
        # Detailed data table
        st.subheader("📋 Detailed Measurements")
        
        # Format data for display
        display_df = df.copy()
        
        # Format columns
        columns_to_show = ['shot_number', 'speed_fps', 'delta_avg_fps', 'ke_ft_lb', 'power_factor']
        if 'datetime_local' in display_df.columns:
            columns_to_show.append('datetime_local')
        
        display_df = display_df[columns_to_show]
        
        # Rename columns for better display
        column_rename = {
            'shot_number': 'Shot #',
            'speed_fps': 'Speed (fps)',
            'delta_avg_fps': 'Δ Avg (fps)',
            'ke_ft_lb': 'KE (ft-lb)',
            'power_factor': 'Power Factor',
            'datetime_local': 'Time'
        }
        
        display_df = display_df.rename(columns=column_rename)
        
        # Format numbers
        if 'Speed (fps)' in display_df.columns:
            display_df['Speed (fps)'] = display_df['Speed (fps)'].round(1)
        if 'Δ Avg (fps)' in display_df.columns:
            display_df['Δ Avg (fps)'] = display_df['Δ Avg (fps)'].round(1)
        if 'KE (ft-lb)' in display_df.columns:
            display_df['KE (ft-lb)'] = display_df['KE (ft-lb)'].round(1)
        if 'Power Factor' in display_df.columns:
            display_df['Power Factor'] = display_df['Power Factor'].round(1)
        
        st.dataframe(display_df, use_container_width=True)
        
        # Export options
        st.subheader("📤 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"chronograph_data_{session.tab_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON download
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"chronograph_data_{session.tab_name}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    except Exception as e:
        st.error(f"Error loading session data: {str(e)}")