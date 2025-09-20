# app.py
import streamlit as st
from dotenv import load_dotenv
import os
import time
import hashlib
from utils.database import UserManager, RedisManager
from utils.config import Config
import pandas as pd
import numpy as np
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)

# Initialize session state defaults to ensure consistency across pages
def init_session_state():
    defaults = {
        'logged_in': False,
        'user_id': None,
        'username': '',
        'disease_tags': [],
        'basic_info': {},
        'risk_score': 0,
        'risk_history': [],
        'today_data': {},
        'food_log': [],
        'weekly_menu': None,
        'case_files': [],
        'symptom_history': [],
        'medication_history': [],
        'health_tips_index': 0,
        'last_tip_update': time.time(),
        'chat_history': [{"role": "assistant", "content": "您好！我是您的AI健康顾问，有什么可以帮您的？"}],
        'current_page': "_home" # Default to home page
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Load environment variables (e.g., from .env file)
load_dotenv()

st.set_page_config(page_title="心守护 - 健康管理", page_icon="❤️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    .main { background-color: #f9fafb; padding: 2rem; }
    .card { @apply bg-white p-6 rounded-lg shadow-md mb-4 border border-gray-200; }
    .metric { @apply text-2xl font-bold text-indigo-600; }
    .btn { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 min-h-[44px] font-semibold transition-colors duration-200; }
    .suggestion-box { @apply bg-gradient-to-r from-blue-50 to-green-50 p-4 rounded-lg border border-blue-200 mt-4 flex items-center gap-4 animate-slideIn; }
    @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    /* Carousel styling for testimonials */
    .carousel { width: 100%; overflow: hidden; position: relative; background: linear-gradient(135deg, #F5F7FA, #E3F2FD); border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .carousel-inner { display: flex; animation: slide 40s infinite; }
    .carousel-item { min-width: 100%; padding: 20px; text-align: center; font-size: 16px; line-height: 1.6; }
    @keyframes slide { 0%, 20% { transform: translateX(0); } 25%, 45% { transform: translateX(-100%); } 50%, 70% { transform: translateX(-200%); } 75%, 95% { transform: translateX(-300%); } 100% { transform: translateX(-400%); } }
    .carousel:hover .carousel-inner { animation-play-state: paused; }
</style>
""", unsafe_allow_html=True)

# Initialize Redis and UserManager
redis_manager = RedisManager()
user_manager = UserManager(redis_manager)

def show_health_tips():
    health_tips = [
        "💡 每天食盐摄入量应控制在5克以下",
        "❤️ 每周至少进行150分钟中等强度运动",
        "🍎 多吃蔬菜水果，少吃加工食品",
        "⚠️ 定期监测血压，及时调整用药"
    ]
    current_time = time.time()
    if current_time - st.session_state.last_tip_update > 30:
        st.session_state.health_tips_index = (st.session_state.health_tips_index + 1) % len(health_tips)
        st.session_state.last_tip_update = current_time
    st.sidebar.markdown(f'<div class="suggestion-box"><span class="text-2xl">💡</span><span>{health_tips[st.session_state.health_tips_index]}</span></div>', unsafe_allow_html=True)

def render_sidebar():
    st.sidebar.markdown('<div class="text-center"><h2 class="text-2xl font-bold text-indigo-600">❤️ 心守护</h2></div>', unsafe_allow_html=True)
    if st.session_state.logged_in:
        st.sidebar.success(f"欢迎, {st.session_state.username}!")
        pages = {
            "主页": "_home",
            "健康概览": "_01_dashboard",
            "AI问医生": "_03_ai_doctor",
            "饮食助手": "_02_nutrition",
            "我的档案": "_04_profile"
        }
        selected_page_name = st.sidebar.radio("导航", list(pages.keys()), label_visibility="collapsed")

        # Navigate to the selected page
        target_page_key = pages[selected_page_name]
        if st.session_state.current_page != target_page_key:
            st.session_state.current_page = target_page_key
            try:
                st.switch_page(f"pages/{target_page_key}.py")
            except Exception as e:
                st.error(f"页面加载失败: {str(e)}")

        if st.sidebar.button("退出登录", key="logout"):
            init_session_state() # Reset session state on logout
            st.rerun()
        show_health_tips()
    else:
        tab1, tab2 = st.sidebar.tabs(["登录", "注册"])
        with tab1:
            login_username = st.text_input("用户名", key="login_user")
            login_password = st.text_input("密码", type="password", key="login_pass")
            if st.button("登录", key="login_btn"):
                user_id = user_manager.authenticate_user(login_username, login_password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = login_username
                    user_data = user_manager.get_user_info(user_id)
                    # Update session state with user data
                    for key in ['disease_tags', 'basic_info', 'risk_score', 'risk_history', 'today_data', 'food_log', 'weekly_menu', 'case_files', 'symptom_history', 'medication_history', 'chat_history']:
                        st.session_state[key] = user_data.get(key, st.session_state[key]) # Use get for safety
                    st.sidebar.success("登录成功！")
                    logging.info(f"用户 {login_username} 登录成功，用户ID: {user_id[:10]}...")
                    st.rerun()
                else:
                    st.sidebar.error("用户名或密码错误")
                    logging.error(f"登录失败: 用户名 '{login_username}'")
        with tab2:
            reg_username = st.text_input("用户名", key="reg_user")
            reg_password = st.text_input("密码", type="password", key="reg_pass")
            reg_confirm = st.text_input("确认密码", type="password", key="reg_confirm")
            if st.button("注册", key="reg_btn"):
                if reg_password != reg_confirm:
                    st.sidebar.error("密码不一致")
                elif len(reg_username) < 3:
                    st.sidebar.error("用户名至少3个字符")
                else:
                    success, result = user_manager.register_user(reg_username, reg_password)
                    if success:
                        st.sidebar.success("注册成功！已升级为正式账户，请登录")
                        logging.info(f"用户 {reg_username} 注册成功")
                    else:
                        st.sidebar.error(result)
                        logging.error(f"注册失败: {result}")

# Initialize session state at the beginning of the app
init_session_state()
render_sidebar()

if not st.session_state.logged_in:
    st.markdown("""
    <div class="bg-gradient-to-r from-indigo-500 to-green-500 p-10 rounded-lg text-white text-center">
        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTUwIDEwQzI1LjE0IDI4Ljg2IDEwIDUwIDUwIDkwQzkwIDUwIDc0Ljg2IDI4Ljg2IDUwIDEwWiIgZmlsbD0iI0ZGMjkyOSIvPjwvc3ZnPg==" class="w-16 mx-auto mb-4">
        <h1 class="text-3xl font-bold">心守护 - 您的健康管理专家</h1>
        <p class="text-lg">精准管理心血管疾病，守护健康每一天</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 为什么选择心守护？
        - 🎯 **精准分型**: 支持6种心血管疾病亚型的个性化管理
        - 🍎 **智能饮食**: AI驱动的食物识别和饮食建议
        - 📊 **实时监控**: 全天候健康数据追踪和分析
        - 🤖 **AI医生**: 24/7智能健康咨询服务
        - 💊 **用药提醒**: 智能用药管理和提醒
        """)
        st.subheader("支持的疾病类型")
        diseases = [
            {"疾病": "高血压 (HTN)", "亚型": "白大衣高血压, 隐匿性高血压", "限制": "钠摄入限制: 1500mg/天"},
            {"疾病": "冠心病 (CAD)", "亚型": "冠心病", "限制": "低脂饮食，控制胆固醇"},
            {"疾病": "心力衰竭 (HF)", "亚型": "射血分数降低型心衰", "限制": "严格限制钠和液体摄入"},
            {"疾病": "心房颤动 (AF)", "亚型": "心房颤动", "限制": "避免刺激性食物饮料"},
            {"疾病": "脑血管病 (CVD)", "亚型": "脑血管病", "限制": "控制血压血脂"},
            {"疾病": "外周动脉疾病 (PAD)", "亚型": "外周动脉疾病", "限制": "戒烟，控制血糖"}
        ]
        df = pd.DataFrame(diseases)
        st.dataframe(df, width='stretch')
    with col2:
        try:
            st.image("assets/heart_health.jpg", caption="健康生活从心开始")
        except Exception as e:
            st.error(f"图片加载失败: {str(e)}")
        st.info("**即刻行动**：注册账号 → 定制疾病管理 → 开启健康新生活！")
    st.subheader("用户见证")
    st.markdown("""
    <div class="carousel">
        <div class="carousel-inner">
            <div class="carousel-item">
                <p>⭐⭐⭐⭐⭐ "心守护帮我管理高血压（WCHT），血压稳定多了！" - 张先生，55岁</p>
            </div>
            <div class="carousel-item">
                <p>⭐⭐⭐⭐ "AI饮食建议让我轻松控制钠摄入，太实用！" - 李女士，48岁，HF</p>
            </div>
            <div class="carousel-item">
                <p>⭐⭐⭐⭐⭐ "用药提醒从不漏掉，生活更有规律！" - 王女士，62岁，AF</p>
            </div>
            <div class="carousel-item">
                <p>⭐⭐⭐⭐ "症状记录让我及时发现问题，医生也夸我数据全！" - 陈先生，50岁，CAD</p>
            </div>
            <div class="carousel-item">
                <p>⭐⭐⭐⭐⭐ "食谱定制贴合我的心衰需求，健康饮食很简单！" - 赵女士，60岁，HF</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<footer class="text-center text-gray-500 mt-5">© 2025 心守护 | 隐私政策 | 帮助中心</footer>', unsafe_allow_html=True)
else:
    # Redirect to dashboard if logged in
    try:
        st.switch_page("pages/_01_dashboard.py")
    except Exception as e:
        st.error(f"页面加载失败: {str(e)}")