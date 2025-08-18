import streamlit as st

def render_home_content():
    """Render the home page content."""
    
    # Display landing page content
    st.title("🎯 ChronoLog")
    st.subheader("Automated DOPE Construction from Multiple Data Sources")

    # Hero section
    st.markdown(
        """
    ### 🤖 **The Power of Automation**
    
    Stop manually transcribing data between spreadsheets, weather apps, and range cards. 
    ChronoLog automatically merges data from multiple sources to build your DOPE (Data On Previous Engagements) 
    with precision and speed.
    """
    )

    # Key benefits
    st.markdown("---")
    st.markdown("### ⚡ **Automatic Data Integration**")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        **📊 Chronograph Data**
        - Upload Garmin Xero Excel files
        - Automatic bullet speed analysis
        - Shot-by-shot metrics
        """
        )

    with col2:
        st.markdown(
            """
        **🌡️ Weather Data**
        - Import Kestrel meter readings
        - Timestamp-matched conditions
        - Environmental factors
        """
        )

    with col3:
        st.markdown(
            """
        **🎯 Range Data**
        - Precise GPS coordinates
        - Distance & elevation angles
        - Ballistic calculations
        """
        )

    # Equipment tracking
    st.markdown("---")
    st.markdown("### 🔧 **Equipment Tracking**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **📦 Ammunition Management**
        - Track make, model, caliber, grain weight
        - Link ammo to shooting sessions
        - Performance analysis by load
        """
        )

    with col2:
        st.markdown(
            """
        **📏 Rifle Specifications**
        - Barrel twist ratio & length
        - Sight offset & trigger details
        - Scope configurations
        """
        )

    # Quick start section
    st.markdown("---")
    st.markdown("## 🚀 **Quick Start Guide**")

    st.markdown(
        """
    ### Get started in 3 simple steps:
    
    1. **📈 Upload Chronograph Data**
       - Go to the **Chronograph** page
       - Upload your Garmin Xero Excel files
       - Review imported shot data
    
    2. **🌍 Add Supporting Data** *(Optional)*
       - **Weather**: Import Kestrel CSV files
       - **Ranges**: Submit or use existing range data
       - **Equipment**: Add your rifles and ammo
    
    3. **🎯 Create DOPE Sessions**
       - Go to the **DOPE** page
       - Select your chronograph session
       - Choose range and weather data
       - Select rifle and ammo
       - System automatically merges all data
       - Edit adjustments and save your DOPE
    """
    )

    # Call to action
    st.markdown("---")
    st.info(
        """
    💡 **Ready to get started?**
    
    Head to the **Chronograph** page to upload your first data file, 
    then visit the **DOPE** page to create your automated ballistic log!
    """
    )

    # Disclaimer
    st.markdown("---")
    st.warning(
        "⚠️ **This is a prototype. There are no guarantees. Use at your own risk.**"
    )
