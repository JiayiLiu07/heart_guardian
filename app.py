import streamlit as st
import os

# ----- 全局配置和初始化 -----
st.set_page_config(
    page_title="CardioGuard AI",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----- 自定义CSS样式 -----
st.markdown("""
<style>
    /* 隐藏侧边栏 */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* 顶部导航栏样式 */
    .top-nav {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 15px 30px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-brand {
        font-size: 1.5rem;
        font-weight: bold;
        color: #FF6B6B;
    }
    
    .auth-buttons {
        display: flex;
        gap: 10px;
    }
    
    .auth-button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        padding: 8px 20px;
        border: none;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        cursor: pointer;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .auth-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        color: white;
        text-decoration: none;
    }
    
    .user-info {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .user-name {
        color: #666;
        font-weight: 500;
    }
    
    /* 主内容区域样式 */
    .main-content {
        margin-top: 80px;
    }
</style>
""", unsafe_allow_html=True)

# ----- 登录状态管理 -----
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""

# ----- 顶部导航栏 -----
st.markdown("""
<div class="top-nav">
    <div class="nav-brand">❤️ CardioGuard AI</div>
    <div class="auth-buttons">
""", unsafe_allow_html=True)

if not st.session_state.is_logged_in:
    st.markdown("""
        <a href="/pages/00_auth" class="auth-button">🔑 登录/注册</a>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="user-info">
            <span class="user-name">欢迎, {st.session_state.username}</span>
            <a href="/pages/05_me" class="auth-button">👤 个人中心</a>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    </div>
</div>
<div class="main-content">
""", unsafe_allow_html=True)

# ----- 主内容区域 -----
try:
    from pages.p00_intro import render as render_intro
    render_intro()
except Exception as e:
    st.error(f"加载首页时出错: {e}")
    st.info("如果页面无法正常显示，请检查文件路径和依赖项。")

st.markdown('</div>', unsafe_allow_html=True)