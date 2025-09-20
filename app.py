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
import streamlit_option_menu as option_menu
import pyttsx3
from streamlit.components.v1 import html

# 配置日志用于调试
logging.basicConfig(level=logging.INFO)

# 立即初始化会话状态默认值
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
        'current_page': "_home",
        'subtype': 'WCHT',
        'dark_mode': False,
        'accessibility_mode': False,
        'animation_enabled': True
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    logging.info("会话状态初始化成功")

# 立即调用初始化
init_session_state()

# 加载环境变量
load_dotenv()

# --- Streamlit 页面配置 ---
st.set_page_config(page_title="心守护 - 健康管理", page_icon="❤️", layout="wide", initial_sidebar_state="expanded")

# --- 全局 CSS 和 Tailwind CSS 加载 ---
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    :root {
        --color-primary: #7F8CF3;
        --color-danger: #F25F5C;
        --color-success: #70E000;
        --font-family: "PingFang SC", "HarmonyOS Sans";
        --border-radius: 12px;
        --shadow: 0 4px 12px rgba(0,0,30,0.1);
    }
    .main { background-color: #f9fafb; padding: 2rem; }
    .card { @apply bg-white p-6 rounded-lg shadow-md mb-6 border border-gray-200; }
    .metric { @apply text-2xl font-bold text-indigo-600; }
    .btn { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 min-h-[44px] font-semibold transition-colors duration-200; }
    .suggestion-box { @apply bg-gradient-to-r from-blue-50 to-green-50 p-4 rounded-lg border border-blue-200 mt-4 flex items-center gap-4 animate-slideIn; }
    .video-container { @apply relative w-full h-0 pb-[56.25%] rounded-lg overflow-hidden shadow-md mb-4; }
    .video-container iframe { @apply absolute top-0 left-0 w-full h-full; }
    .video-carousel { width: 100%; overflow: hidden; position: relative; }
    .video-carousel-inner { display: flex; transition: transform 0.5s ease-in-out; }
    .video-carousel-item { min-width: 100%; }
    @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    .carousel { width: 100%; overflow: hidden; position: relative; background: linear-gradient(135deg, #F5F7FA, #E3F2FD); border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .carousel-inner { display: flex; animation: slide 40s infinite; }
    .carousel-item { min-width: 100%; padding: 20px; text-align: center; font-size: 16px; line-height: 1.6; }
    @keyframes slide { 0%, 20% { transform: translateX(0); } 25%, 45% { transform: translateX(-100%); } 50%, 70% { transform: translateX(-200%); } 75%, 95% { transform: translateX(-300%); } 100% { transform: translateX(-400%); } }
    .carousel:hover .carousel-inner { animation-play-state: paused; }
    [data-theme="dark"] { background-color: #1a1a1a; color: #fff; }
    [data-accessibility="true"] { font-size: 150%; filter: contrast(200%); }
    .sidebar .video-container { max-width: 100%; }
</style>
""", unsafe_allow_html=True)

# 暗色模式和无障碍模式检查
if st.session_state.dark_mode:
    st.markdown('<body data-theme="dark">', unsafe_allow_html=True)
if st.session_state.accessibility_mode:
    st.markdown('<body data-accessibility="true">', unsafe_allow_html=True)

# 初始化 Redis 和 UserManager
redis_manager = RedisManager()
user_manager = UserManager(redis_manager)

def show_health_tips():
    health_tips = [
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

    if not st.session_state.logged_in:  # 如果用户未登录，显示视频和用户见证
        # --- 即刻行动 ---
        st.sidebar.markdown("""
        <div class="card">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">即刻行动</h2>
            <h3 class="text-xl font-semibold text-gray-600 mb-2">心血管疾病科普小视频</h3>
            <p class="text-gray-600 mb-4">💡提示：点击视频以启用声音</p>
            <div class="video-container">
                <iframe id="video1" src="https://player.bilibili.com/player.html?bvid=BV1xZ4y1Z7Xw&page=1&high_quality=1&danmaku=0&autoplay=1" allow="autoplay; encrypted-media" frameborder="0" allowfullscreen></iframe>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 视频播放的 JavaScript
        st.sidebar.markdown("""
        <script>
            const video = document.getElementById('video1');

            // Ensure video is unmuted after user interaction
            function enableVideoSound() {
                video.contentWindow.postMessage('{"event":"command","func":"unmute","args":""}', '*');
                video.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*');
            }

            // Try to play video on load
            setTimeout(() => {
                enableVideoSound();
            }, 1000); // Delay to ensure iframe is loaded

            // Add click event to ensure sound on user interaction
            video.addEventListener('click', enableVideoSound);
        </script>
        """, unsafe_allow_html=True)

        # --- 用户见证 ---
        st.sidebar.markdown("""
        <div class="card">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">用户见证</h2>
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
                        <p>⭐⭐⭐⭐ "症状记录让我及时发现问题，医生也夸我数据全！" - 陈先生，50岁</p>
                    </div>
                    <div class="carousel-item">
                        <p>⭐⭐⭐⭐⭐ "食谱定制贴合我的需求，健康饮食很简单！" - 赵女士，60岁</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:  # 用户已登录时显示健康提示和导航
        show_health_tips()
        st.sidebar.success(f"欢迎, {st.session_state.username}!")
        selected = option_menu.option_menu(
            menu_title=None,
            options=["主页", "健康概览", "AI问医生", "饮食助手", "我的档案"],
            icons=["house", "activity", "robot", "apple", "file-person"],
            menu_icon="cast",
            default_index=0,
        )
        pages = {
            "主页": "_home",
            "健康概览": "_01_dashboard",
            "AI问医生": "_03_ai_doctor",
            "饮食助手": "_02_nutrition",
            "我的档案": "_04_profile"
        }
        target_page_key = pages[selected]

        if st.session_state.current_page != target_page_key:
            st.session_state.current_page = target_page_key
            try:
                st.switch_page(f"pages/{target_page_key}.py")
            except Exception as e:
                st.error(f"页面加载失败: {str(e)}")

        if st.sidebar.button("退出登录", key="logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session_state()
            st.rerun()

# --- 侧边栏渲染 ---
render_sidebar()

# --- 主内容区域渲染 ---
if st.session_state.logged_in:
    if st.session_state.current_page == "_home":
        try:
            st.switch_page("pages/_01_dashboard.py")
        except Exception as e:
            st.error(f"页面加载失败: {str(e)}")
else:
    # --- 未登录时的首页内容 ---
    st.markdown("""
    <div class="bg-gradient-to-r from-indigo-500 to-green-500 p-10 rounded-lg text-white text-center">
        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTUwIDEwQzI1LjE0IDI4Ljg2IDEwIDUwIDUwIDkwQzkwIDUwIDc0Ljg2IDI4Ljg2IDUwIDEwWiIgZmlsbD0iI0ZGMjkyOSIvPjwvc3ZnPg==" class="w-16 mx-auto mb-4">
        <h1 class="text-3xl font-bold">心守护 - 您的健康管理专家</h1>
        <p class="text-lg">精准管理心血管疾病，守护健康每一天</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])  # 左侧列宽2，右侧列宽1

    with col1:
        st.markdown("""
        <div class="card">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">为什么选择心守护？</h2>
            <ul class="list-disc pl-6 text-gray-600">
                <li><strong>精准管理</strong>: 支持多种心血管疾病的个性化管理</li>
                <li><strong>智能饮食</strong>: AI驱动的食物识别和饮食建议</li>
                <li><strong>实时监控</strong>: 全天候健康数据追踪和分析</li>
                <li><strong>AI医生</strong>: 24/7智能健康咨询服务</li>
                <li><strong>用药提醒</strong>: 智能用药管理和提醒</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">支持的疾病类型</h2>
        """, unsafe_allow_html=True)

        diseases = [
            {"疾病": "高血压 (HTN)", "亚型": "白大衣高血压, 隐匿性高血压", "限制": "钠摄入限制: 1500mg/天"},
            {"疾病": "冠心病 (CAD)", "亚型": "冠心病", "限制": "低脂饮食，控制胆固醇"},
            {"疾病": "心力衰竭 (HF)", "亚型": "射血分数降低型心衰", "限制": "严格限制钠和液体摄入"},
            {"疾病": "心房颤动 (AF)", "亚型": "心房颤动", "限制": "避免刺激性食物饮料"},
            {"疾病": "脑血管病 (CVD)", "亚型": "脑血管病", "限制": "控制血压血脂"},
            {"疾病": "外周动脉疾病 (PAD)", "亚型": "外周动脉疾病", "限制": "戒烟，控制血糖"}
        ]
        df = pd.DataFrame(diseases)
        st.dataframe(df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # --- 登录/注册 ---
        st.markdown("""
        <div class="card">
            <h2 class="text-xl font-semibold text-gray-700 mb-4">注册/登录</h2>
        """, unsafe_allow_html=True)

        # "健康生活从心开始" 图片
        try:
            st.image("assets/heart_health.jpg", caption="健康生活从心开始")
        except Exception as e:
            st.error(f"本地图片加载失败: {str(e)}")

        tab1, tab2 = st.tabs(["登录", "注册"])

        with tab1:
            login_username = st.text_input("用户名", key="login_user_main")
            login_password = st.text_input("密码", type="password", key="login_pass_main")
            if st.button("登录", key="login_btn_main"):
                hashed_pass = hashlib.sha256(login_password.encode()).hexdigest()
                user_id = user_manager.login_user(login_username, hashed_pass)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = login_username
                    user_data = user_manager.get_user_info(user_id)
                    if user_data:
                        for key in ['disease_tags', 'basic_info', 'risk_score', 'risk_history', 'today_data', 'food_log', 'weekly_menu', 'case_files', 'symptom_history', 'medication_history', 'chat_history']:
                            st.session_state[key] = user_data.get(key, st.session_state.get(key))
                    st.success("登录成功！")
                    logging.info(f"用户 {login_username} 登录成功，用户ID: {user_id[:10]}...")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
                    logging.error(f"登录失败: 用户名 '{login_username}'")
        with tab2:
            reg_username = st.text_input("用户名", key="reg_user_main")
            reg_password = st.text_input("密码", type="password", key="reg_pass_main")
            reg_confirm = st.text_input("确认密码", type="password", key="reg_confirm_main")
            if st.button("注册", key="reg_btn_main"):
                if reg_password != reg_confirm:
                    st.error("密码不一致")
                elif len(reg_username) < 3:
                    st.error("用户名至少3个字符")
                else:
                    success, result = user_manager.register_user(reg_username, reg_password)
                    if success:
                        st.success("注册成功！已升级为正式账户，请登录")
                        logging.info(f"用户 {reg_username} 注册成功")
                    else:
                        st.error(result)
                        logging.error(f"注册失败: {result}")
        st.markdown("</div>", unsafe_allow_html=True)

# 紧急警报 (仅在已登录时显示)
if st.session_state.logged_in:
    user_data = user_manager.get_user_info(st.session_state.user_id)
    if user_data:
        ap_hi = user_data.get('today_data', {}).get('ap_hi', 0)
        ap_lo = user_data.get('today_data', {}).get('ap_lo', 0)
        hr = user_data.get('today_data', {}).get('heart_rate', 0)
        if ap_hi > 180 or ap_lo > 110 or hr > 150:
            st.markdown('<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(255,0,0,0.5);z-index:999;display:flex;justify-content:center;align-items:center;"><h1>紧急！立即拨打120</h1></div>', unsafe_allow_html=True)
            try:
                engine = pyttsx3.init()
                engine.say("紧急预警，血压或心率异常，请立即求医")
                engine.runAndWait()
            except Exception as e:
                logging.error(f"TTS 引擎错误: {e}")
    else:
        logging.warning(f"无法获取用户 {st.session_state.user_id} 的数据进行紧急警报检查")

# Hero 区 3D 心脏动画 (应该在所有页面都显示)
html("""
<div id="heart-3d"></div>
<script src="https://lottiefiles.com/lottie-player"></script>
<!-- 假设 Lottie 或 WebGL 集成 -->
""")

# 离线缓存 PWA (应该在所有页面都显示)
html("""
<link rel="manifest" href="/manifest.json">
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js');
    }
</script>
""")