import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from .service import WeatherService

def render_weather_view_log_tab(user, supabase):
    """Render the Weather View Log tab for detailed weather analysis"""
    st.header("🔍 View Weather Log")
    
    try:
        # Initialize weather service
        weather_service = WeatherService(supabase)
        
        # Get all weather sources for the user
        sources = weather_service.get_sources_for_user(user["email"])
        
        if not sources:
            st.info("No weather sources found. Import some Kestrel data files to get started!")
            return
        
        # Get all measurements for the user
        measurements = weather_service.get_all_measurements_for_user(user["email"])
        
        if not measurements:
            st.info("No weather measurements found.")
            return
        
        # Create source/date selector
        source_date_options = {}
        for measurement in measurements:
            # Find the source for this measurement
            source_obj = None
            for source in sources:
                if source.id == measurement.weather_source_id:
                    source_obj = source
                    break
            
            if source_obj:
                date_str = pd.to_datetime(measurement.measurement_timestamp).strftime('%Y-%m-%d')
                option_key = f"{source_obj.display_name()} | {date_str}"
                source_date_options[option_key] = {
                    'source_id': source_obj.id,
                    'source_name': source_obj.display_name(),
                    'date': date_str,
                    'device_display': source_obj.device_display()
                }
        
        # Remove duplicates and sort
        unique_options = list(set(source_date_options.keys()))
        unique_options.sort(reverse=True)  # Most recent first
        
        # Use selected source/date from session state if available
        default_selection = None
        if 'selected_weather_source_id' in st.session_state and 'selected_weather_date' in st.session_state:
            target_source_id = st.session_state['selected_weather_source_id']
            target_date = st.session_state['selected_weather_date']
            for option_key, info in source_date_options.items():
                if info['source_id'] == target_source_id and info['date'] == target_date:
                    default_selection = option_key
                    break
        
        if not unique_options:
            st.info("No weather data available for analysis.")
            return
        
        selected_option = st.selectbox(
            "Select Weather Source & Date to View",
            options=unique_options,
            index=unique_options.index(default_selection) if default_selection and default_selection in unique_options else 0
        )
        
        if not selected_option:
            st.info("Please select a weather source and date to view.")
            return
        
        selection_info = source_date_options[selected_option]
        
        # Filter measurements for selected source and date
        selected_measurements = [
            m for m in measurements 
            if (m.weather_source_id == selection_info['source_id'] and
                pd.to_datetime(m.measurement_timestamp).strftime('%Y-%m-%d') == selection_info['date'])
        ]
        
        if not selected_measurements:
            st.warning("No measurements found for selected weather source and date.")
            return
        
        # Convert to DataFrame for analysis
        measurements_dict = []
        for m in selected_measurements:
            measurements_dict.append({
                'measurement_timestamp': m.measurement_timestamp,
                'temperature_f': m.temperature_f,
                'relative_humidity_pct': m.relative_humidity_pct,
                'barometric_pressure_inhg': m.barometric_pressure_inhg,
                'wind_speed_mph': m.wind_speed_mph,
                'density_altitude_ft': m.density_altitude_ft,
                'location_description': m.location_description
            })
        
        df = pd.DataFrame(measurements_dict)
        df['timestamp'] = pd.to_datetime(df['measurement_timestamp'])
        df = df.sort_values('timestamp')
        
        # Session header
        st.subheader(f"🌤️ Weather Data - {selection_info['date']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Weather Source:** {selection_info['source_name']}")
            st.write(f"**Device:** {selection_info['device_display']}")
        with col2:
            st.write(f"**Measurements:** {len(selected_measurements)}")
            time_range = f"{df['timestamp'].min().strftime('%H:%M')} - {df['timestamp'].max().strftime('%H:%M')}"
            st.write(f"**Time Range:** {time_range}")
        with col3:
            if measurements_dict and measurements_dict[0].get('location_description'):
                st.write(f"**Location:** {measurements_dict[0]['location_description']}")
        
        # Key Statistics
        st.subheader("📈 Weather Statistics")
        
        # Temperature stats
        if 'temperature_f' in df.columns and not df['temperature_f'].isna().all():
            temps = df['temperature_f'].dropna()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Temperature", f"{temps.mean():.1f}°F")
            with col2:
                st.metric("Min Temperature", f"{temps.min():.1f}°F")
            with col3:
                st.metric("Max Temperature", f"{temps.max():.1f}°F")
            with col4:
                st.metric("Temp Range", f"{temps.max() - temps.min():.1f}°F")
        
        # Humidity and pressure stats
        col1, col2, col3, col4 = st.columns(4)
        
        if 'relative_humidity_pct' in df.columns and not df['relative_humidity_pct'].isna().all():
            humidity = df['relative_humidity_pct'].dropna()
            with col1:
                st.metric("Avg Humidity", f"{humidity.mean():.1f}%")
        
        if 'barometric_pressure_inhg' in df.columns and not df['barometric_pressure_inhg'].isna().all():
            pressure = df['barometric_pressure_inhg'].dropna()
            with col2:
                st.metric("Avg Pressure", f"{pressure.mean():.2f} inHg")
        
        if 'wind_speed_mph' in df.columns and not df['wind_speed_mph'].isna().all():
            wind = df['wind_speed_mph'].dropna()
            with col3:
                st.metric("Avg Wind Speed", f"{wind.mean():.1f} mph")
        
        if 'density_altitude_ft' in df.columns and not df['density_altitude_ft'].isna().all():
            density_alt = df['density_altitude_ft'].dropna()
            with col4:
                st.metric("Avg Density Alt", f"{density_alt.mean():.0f} ft")
        
        # Charts
        st.subheader("📊 Weather Trends")
        
        # Create tabs for different views
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Temperature & Humidity", "Pressure & Wind", "All Parameters"])
        
        with chart_tab1:
            # Temperature and humidity over time
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            
            # Temperature plot
            if 'temperature_f' in df.columns and not df['temperature_f'].isna().all():
                ax1.plot(df['timestamp'], df['temperature_f'], 'r-o', linewidth=2, markersize=3, label='Temperature')
                ax1.set_ylabel('Temperature (°F)', color='red')
                ax1.tick_params(axis='y', labelcolor='red')
                ax1.grid(True, alpha=0.3)
                ax1.set_title('Temperature Over Time')
            
            # Humidity plot
            if 'relative_humidity_pct' in df.columns and not df['relative_humidity_pct'].isna().all():
                ax2.plot(df['timestamp'], df['relative_humidity_pct'], 'b-o', linewidth=2, markersize=3, label='Humidity')
                ax2.set_ylabel('Humidity (%)', color='blue')
                ax2.tick_params(axis='y', labelcolor='blue')
                ax2.grid(True, alpha=0.3)
                ax2.set_title('Humidity Over Time')
            
            ax2.set_xlabel('Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        
        with chart_tab2:
            # Pressure and wind over time
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            
            # Pressure plot
            if 'barometric_pressure_inhg' in df.columns and not df['barometric_pressure_inhg'].isna().all():
                ax1.plot(df['timestamp'], df['barometric_pressure_inhg'], 'g-o', linewidth=2, markersize=3, label='Pressure')
                ax1.set_ylabel('Pressure (inHg)', color='green')
                ax1.tick_params(axis='y', labelcolor='green')
                ax1.grid(True, alpha=0.3)
                ax1.set_title('Barometric Pressure Over Time')
            
            # Wind speed plot
            if 'wind_speed_mph' in df.columns and not df['wind_speed_mph'].isna().all():
                ax2.plot(df['timestamp'], df['wind_speed_mph'], 'm-o', linewidth=2, markersize=3, label='Wind Speed')
                ax2.set_ylabel('Wind Speed (mph)', color='magenta')
                ax2.tick_params(axis='y', labelcolor='magenta')
                ax2.grid(True, alpha=0.3)
                ax2.set_title('Wind Speed Over Time')
            
            ax2.set_xlabel('Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        
        with chart_tab3:
            # All parameters normalized on same plot
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Normalize all parameters to 0-1 scale for comparison
            params_to_plot = []
            
            if 'temperature_f' in df.columns and not df['temperature_f'].isna().all():
                temp_norm = (df['temperature_f'] - df['temperature_f'].min()) / (df['temperature_f'].max() - df['temperature_f'].min())
                ax.plot(df['timestamp'], temp_norm, 'r-', linewidth=2, label='Temperature (normalized)')
                params_to_plot.append('temperature')
            
            if 'relative_humidity_pct' in df.columns and not df['relative_humidity_pct'].isna().all():
                humidity_norm = df['relative_humidity_pct'] / 100  # Already 0-100, just scale to 0-1
                ax.plot(df['timestamp'], humidity_norm, 'b-', linewidth=2, label='Humidity (normalized)')
                params_to_plot.append('humidity')
            
            if 'barometric_pressure_inhg' in df.columns and not df['barometric_pressure_inhg'].isna().all():
                pressure_norm = (df['barometric_pressure_inhg'] - df['barometric_pressure_inhg'].min()) / (df['barometric_pressure_inhg'].max() - df['barometric_pressure_inhg'].min())
                ax.plot(df['timestamp'], pressure_norm, 'g-', linewidth=2, label='Pressure (normalized)')
                params_to_plot.append('pressure')
            
            if params_to_plot:
                ax.set_ylabel('Normalized Value (0-1)')
                ax.set_xlabel('Time')
                ax.set_title('All Weather Parameters (Normalized)')
                ax.legend()
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No data available for normalized comparison chart.")
        
        # Detailed data table
        st.subheader("📋 Detailed Measurements")
        
        # Format data for display
        display_df = df.copy()
        
        # Select relevant columns
        columns_to_show = ['timestamp', 'temperature_f', 'relative_humidity_pct', 'barometric_pressure_inhg', 
                          'wind_speed_mph', 'density_altitude_ft']
        
        # Only include columns that exist and have data
        available_columns = []
        for col in columns_to_show:
            if col in display_df.columns and not display_df[col].isna().all():
                available_columns.append(col)
        
        if available_columns:
            display_df = display_df[available_columns]
            
            # Format timestamp
            if 'timestamp' in display_df.columns:
                display_df['timestamp'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
            
            # Round numeric columns
            numeric_columns = ['temperature_f', 'relative_humidity_pct', 'barometric_pressure_inhg', 
                             'wind_speed_mph', 'density_altitude_ft']
            for col in numeric_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].round(1)
            
            # Rename columns for better display
            column_rename = {
                'timestamp': 'Time',
                'temperature_f': 'Temp (°F)',
                'relative_humidity_pct': 'Humidity (%)',
                'barometric_pressure_inhg': 'Pressure (inHg)',
                'wind_speed_mph': 'Wind (mph)',
                'density_altitude_ft': 'Density Alt (ft)'
            }
            
            display_df = display_df.rename(columns=column_rename)
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
                file_name=f"weather_data_{selection_info['source_name'].replace(' ', '_')}_{selection_info['date']}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON download
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"weather_data_{selection_info['source_name'].replace(' ', '_')}_{selection_info['date']}.json",
                mime="application/json"
            )
    
    except Exception as e:
        st.error(f"Error loading weather data: {str(e)}")