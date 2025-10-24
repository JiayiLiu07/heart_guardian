# app.py

import streamlit as st

# === Page Configuration ===
st.set_page_config(page_title="HeartGuardian", layout="wide", initial_sidebar_state="collapsed")

# === CSS to Ensure Navigation Bar is Visible ===
st.markdown("""
<style>
section[data-testid="stSidebar"], .stSidebar, [data-testid="collapsedControl"],
#MainMenu, footer, .css-1d391kg, .stDeployButton {display: none !important;}
.block-container {padding-top: 80px !important; margin-top: 0 !important;}
</style>
""", unsafe_allow_html=True)

# === Login Check ===
if 'user_id' not in st.session_state:
    st.switch_page("pages/p00_intro.py")

# === Define Page Mapping ===
page_map = {
    "overview": "pages/01_overview.py",
    "nutrition": "pages/02_nutrition.py", 
    "ai_doctor": "pages/03_ai_doctor.py",
    "knowledge": "pages/p04_knowledge.py",
    "profile": "pages/p01_profile.py",
    "me": "pages/p05_me.py"
}

# === Initialize Session State ===
if 'current_page' not in st.session_state:
    st.session_state.current_page = "pages/01_overview.py"

# === Render Navigation ===
from components.top_nav import render_nav
with st.container():
    render_nav(page_map)

# === Render Current Page ===
try:
    # Debug: Display current page (hidden)
    st.markdown(f"<div style='display:none'>当前页面: {st.session_state.current_page}</div>", unsafe_allow_html=True)
    
    current_page = st.session_state.current_page
    if current_page == "pages/01_overview.py":
        import pages.p01_overview as overview_page
        overview_page.render()
    elif current_page == "pages/02_nutrition.py":
        import pages.p02_nutrition as nutrition_page
        nutrition_page.show_ai_charts_page()
    elif current_page == "pages/03_ai_doctor.py":
        import pages.p03_ai_doctor as ai_doctor_page
        ai_doctor_page.render()
    elif current_page == "pages/p04_knowledge.py":
        import pages.p04_knowledge as knowledge_page
        knowledge_page.render()
    elif current_page == "pages/p01_profile.py":
        import pages.p01_profile as profile_page
        # p01_profile.py is executed directly
    elif current_page == "pages/p05_me.py":
        import pages.p05_me as me_page
        me_page.render_p05_me()
    else:
        st.error(f"页面未找到: {current_page}")
        st.session_state.current_page = "pages/01_overview.py"
        st.rerun()

except Exception as e:
    st.error(f"页面加载失败: {e}")
    # Fallback to overview page
    st.session_state.current_page = "pages/01_overview.py"
    st.rerun()