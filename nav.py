import streamlit as st

# -------------------------
# GLOBAL SIDEBAR SETTINGS
# -------------------------
# (No icon settings needed now)

# Hide Streamlit's default multipage nav (keep your custom nav only)
st.markdown("""
<style>
  [data-testid='stSidebarNav']{display:none}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR HELPERS (no icons)
# -------------------------
INDENT_PX = 26  # default indent for child rows

def sidebar_link(page_path: str, label: str, *, indent_px: int = 0):
    """
    Render a single sidebar row with an optional left indent and a Streamlit page_link.
    This version does NOT use icons.
    """
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        # spacer cell to keep alignment similar to the old icon column
        st.markdown(f"<div style='padding-left:{indent_px}px;'>&nbsp;</div>", unsafe_allow_html=True)
    with cols[1]:
        st.page_link(page_path, label=label)

def sidebar_child_link(page_path: str, label: str, *, indent_px: int = INDENT_PX):
    """
    Child row convenience wrapper (indented by default).
    """
    sidebar_link(page_path, label, indent_px=indent_px)


# -------------------------
# SIDEBAR LAYOUT (hierarchy) — NO ICONS
# -------------------------

# DOPE (standalone group)
st.sidebar.divider()
st.sidebar.header("Data on Prior Engagements")
sidebar_link("pages/2_DOPE.py", label="Overview")
sidebar_link("pages/2_DOPE.py", label="Create")
sidebar_link("pages/2_DOPE.py", label="View")

st.sidebar.divider()
st.sidebar.header("Data Sets")

# Top-level dataset items (no icons)
sidebar_link("pages/3_Chronograph.py", "Chronograph")
sidebar_link("pages/4_Weather.py", "Weather")
sidebar_link("pages/5_Ranges.py", "Ranges")
sidebar_link("pages/6_Rifles.py", "Rifles")

# Cartridges parent (clickable) + children
sidebar_link("pages/7_Factory_Cartridges.py", "Cartridges-Factory")
sidebar_link("pages/8_Custom_Cartridges.py",  "Cartridges-Custom")

# Bullets
sidebar_link("pages/9_Bullets.py", "Bullets")

# -------------------------
# MAIN CONTENT (optional)
# -------------------------
st.title("ChronoLog")
st.write("Use the sidebar to navigate.")