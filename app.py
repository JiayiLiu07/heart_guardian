# app.py
import streamlit as st
from dotenv import load_dotenv

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass  # Cloud 不需要 .env

# === 页面配置 ===
st.set_page_config(page_title="HeartGuardian", layout="wide", initial_sidebar_state="collapsed")

# === 隐藏所有默认 UI ===
st.markdown("""
<style>
section[data-testid="stSidebar"], .stSidebar, [data-testid="collapsedControl"],
#MainMenu, footer, .css-1d391kg {display: none !important;}
.block-container {padding-top: 5.5rem !important;}
</style>
""", unsafe_allow_html=True)

# === 登录检查 ===
if 'user_id' not in st.session_state:
    st.switch_page("pages/p00_intro.py")

# === 渲染顶部导航 ===
from components.top_nav import render_nav
render_nav()

# === 路由控制 ===
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'overview'

query_params = st.query_params
if "page" in query_params:
    page_key = query_params["page"][0]
    valid_pages = {
        "overview": "pages/01_overview.py",
        "nutrition": "pages/02_nutrition.py",
        "ai_doctor": "pages/03_ai_doctor.py",
        "knowledge": "pages/p04_knowledge.py",
        "profile": "pages/p01_profile.py",
        "me": "pages/p05_me.py"
    }
    if page_key in valid_pages and page_key != st.session_state.current_page:
        st.session_state.current_page = page_key
        st.switch_page(valid_pages[page_key])

# 默认跳转
page_map = {
    "overview": "pages/01_overview.py",
    "nutrition": "pages/02_nutrition.py",
    "ai_doctor": "pages/03_ai_doctor.py",
    "knowledge": "pages/p04_knowledge.py",
    "profile": "pages/p01_profile.py",
    "me": "pages/p05_me.py"
}
st.switch_page(page_map[st.session_state.current_page])