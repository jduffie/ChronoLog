import streamlit as st

# -------------------------
# SVG ICON DEFINITIONS
# (keep your existing ones, just showing placeholders here)
# -------------------------
ICON_CHRONO_MONO = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" ...>...</svg>"""
ICON_WEATHER_MONO = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" ...>...</svg>"""
ICON_RANGES_MONO  = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" ...>...</svg>"""
ICON_RIFLES_MONO  = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" ...>...</svg>"""
ICON_CARTRIDGES_MONO = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" ...>...</svg>"""
ICON_BULLETS_MONO = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" ...>...</svg>"""
ICON_DOPE_TURRET_MONO = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" ...>...</svg>"""

import streamlit as st

# -------------------------
# GLOBAL SIDEBAR SETTINGS
# -------------------------
ICON_SIZE = 22        # ← change this once to resize ALL icons
CHILD_INDENT = 26     # ← indent for child rows (Factory/Custom)

# Hide Streamlit's default multipage nav (keep your custom nav only)
st.markdown("""
<style>
  [data-testid='stSidebarNav']{display:none}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR HELPERS (auto-size icons)
# -------------------------
def _svg_with_css_scale(svg_text: str) -> str:
    """
    Ensure the root <svg> scales to its container (100% width/height),
    without needing to touch width/height attributes in the SVG string.
    """
    # Inject style on the FIRST <svg ...> only
    return svg_text.replace("<svg", "<svg style=\"width:100%;height:100%;\"", 1)

def sidebar_icon_link(icon_svg: str, page_path: str, label: str, *, indent_px: int = 0):
    """
    One sidebar row with an icon (auto-sized from ICON_SIZE) + page link.
    Use indent_px for hierarchical layout.
    """
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown(
            f"""
            <div style="padding-left:{indent_px}px; display:flex; align-items:center; justify-content:center;">
              <div style="width:{ICON_SIZE}px; height:{ICON_SIZE}px; line-height:0; display:block;">
                {_svg_with_css_scale(icon_svg)}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.page_link(page_path, label=label)

def sidebar_child_link(page_path: str, label: str, *, indent_px: int = CHILD_INDENT):
    """
    Child row with no icon, aligned with icon cell width and indented.
    """
    cols = st.sidebar.columns([1, 9], gap="small")
    with cols[0]:
        st.markdown(f"<div style='padding-left:{indent_px}px;'>&nbsp;</div>", unsafe_allow_html=True)
    with cols[1]:
        st.page_link(page_path, label=label)

# -------------------------
# YOUR SVG ICONS
# (keep your existing definitions as-is)
# e.g. ICON_DOPE_TURRET_MONO, ICON_CHRONO_MONO, ICON_WEATHER_MONO, ICON_RANGES_MONO,
#      ICON_RIFLES_MONO, ICON_CARTRIDGES_MONO, ICON_BULLETS_MONO, etc.
# -------------------------


# -------------------------
# SIDEBAR LAYOUT (hierarchy)
# -------------------------
# DOPE (standalone above dataset group)
st.sidebar.divider()
st.sidebar.header("Data on Prior Engagements")
sidebar_icon_link(ICON_DOPE_TURRET_MONO, "pages/2_📊_DOPE.py", "Create")
sidebar_icon_link(ICON_DOPE_TURRET_MONO, "pages/2_📊_DOPE.py", "View")


st.sidebar.divider()
st.sidebar.header("Data Sets")

# Top-level dataset items (with icons)
sidebar_icon_link(ICON_CHRONO_MONO, "pages/3_⏱️_Chronograph.py", "Chronograph")
sidebar_icon_link(ICON_WEATHER_MONO, "pages/4_🌤️_Weather.py", "Weather")
sidebar_icon_link(ICON_RANGES_MONO,  "pages/5_🌍_Ranges.py", "Ranges")
sidebar_icon_link(ICON_RIFLES_MONO,  "pages/6_📏_Rifles.py", "Rifles")

## Cartridges (parent has icon)
# sidebar_icon_link(ICON_CARTRIDGES_MONO, "pages/10_👑_Admin.py", "Cartridges")

# Children (no icons)
sidebar_icon_link(ICON_CARTRIDGES_MONO,"pages/7_🏭_Factory_Cartridges.py", "Factory Cartridges")
sidebar_icon_link(ICON_CARTRIDGES_MONO, "pages/8_🎯_Custom_Cartridges.py",  "Custom Cartridges")

# Bullets (icon)
sidebar_icon_link(ICON_BULLETS_MONO, "pages/9_📦_Bullets.py", "Bullets")

# -------------------------
# MAIN CONTENT (optional)
# -------------------------
st.title("ChronoLog")
st.write("Use the sidebar to navigate.")