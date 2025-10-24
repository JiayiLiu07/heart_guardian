# components/top_nav.py

import streamlit as st

def render_nav(page_map):
    current = st.session_state.get('current_page', 'pages/01_overview.py')
    current_short = current.split('/')[-1].replace('.py', '')

    # 定义导航标签
    nav_labels = {
        "01_overview": "总览",
        "02_nutrition": "饮食", 
        "03_ai_doctor": "咨询",
        "p04_knowledge": "知识",
        "p01_profile": "档案",
        "p05_me": "我的"
    }

    # CSS for fixed top navigation
    st.markdown("""
    <style>
    :root {
        --primary: #1a237e;
        --accent: #00e5ff;
        --bg: #0f1629;
        --text: #e1f5fe;
    }
    .cyber-nav {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 64px;
        background: linear-gradient(90deg, var(--primary), #283593, #3949ab, #283593, var(--primary));
        background-size: 300% 100%;
        animation: gradientFlow 8s ease infinite;
        display: flex !important;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        z-index: 1000000 !important;
        box-shadow: 0 4px 20px rgba(0,229,255,.3);
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent);
        letter-spacing: 1px;
    }
    .nav-links {
        display: flex !important;
        gap: 1rem;
        align-items: center;
    }
    .nav-btn {
        color: var(--text);
        background: none;
        border: none;
        font-weight: 500;
        padding: .5rem 1rem;
        border-radius: 8px;
        transition: all .2s ease;
        font-size: 0.95rem;
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
        cursor: pointer;
    }
    .nav-btn:hover,
    .nav-btn.active {
        background: rgba(0,229,255,.2);
        color: var(--accent);
        box-shadow: 0 0 12px rgba(0,229,255,.6);
    }
    </style>
    """, unsafe_allow_html=True)

    # 渲染导航栏
    with st.container():
        st.markdown('<div class="cyber-nav"><div class="logo">HeartGuardian</div><div class="nav-links">', unsafe_allow_html=True)
        
        # 创建导航按钮
        for page_file, page_label in nav_labels.items():
            page_key = page_file.replace('01_', '').replace('02_', '').replace('03_', '').replace('p0', '').replace('p', '')
            is_active = current_short == page_file
            
            # 使用st.button而不是HTML按钮
            if st.button(page_label, key=f"nav_{page_key}", type="primary" if is_active else "secondary"):
                target_page = page_map.get(page_key)
                if target_page and st.session_state.current_page != target_page:
                    st.session_state.current_page = target_page
                    st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)