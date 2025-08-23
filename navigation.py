import streamlit as st


def load():
    """Load and render the custom navigation sidebar."""

    # Hide Streamlit's default multipage nav with very aggressive CSS
    st.markdown(
        """
    <style>
    /* Hide the default Streamlit navigation */
    [data-testid='stSidebarNav'] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    
    [data-testid='stSidebarNav'] > ul {
        display: none !important;
        visibility: hidden !important;
    }
    
    .css-1d391kg {
        display: none !important;
    }
    
    .css-1y4p8pa {
        display: none !important;
    }
    
    /* Additional selectors to ensure navigation is hidden */
    [data-testid='stSidebarNav'] ul li {
        display: none !important;
    }
    
    [data-testid='stSidebarNav'] ul li a {
        display: none !important;
    }
    
    /* Hide any navigation list items */
    .css-1vencpc {
        display: none !important;
    }
    
    /* Hide navigation container */
    .css-17lntkn {
        display: none !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # App title
    st.sidebar.header("ChronoLog")

    # Data on Prior Engagements section
    # st.sidebar.divider()
    st.sidebar.subheader("Data on Prior Engagements")

    # Overview
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/2a_DOPE_Overview.py", label="Overview")

    # Create
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/2b_DOPE_Create.py", label="Create")

    # View
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/2c_DOPE_View.py", label="View")

    # Analytics
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/2d_DOPE_Analytics.py", label="Analytics")

    # st.sidebar.divider()
    st.sidebar.header("Data Sets")

    # Data sets items
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/3_Chronograph.py", label="Chronograph")

    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/4_Weather.py", label="Weather")

    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/5_Ranges.py", label="Ranges")

    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/6_Rifles.py", label="Rifles")

    # Cartridges
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/7_Cartridges.py", label="Cartridges")

    # Bullets
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/9_Bullets.py", label="Bullets")

    # Admin section
    st.sidebar.divider()
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/10_Admin.py", label="Admin")
