# components/top_nav.py
import streamlit as st

def render_nav():
    current = st.session_state.get('current_page', 'overview')
    pages = {
        "overview": "总览",
        "nutrition": "饮食",
        "ai_doctor": "咨询",
        "knowledge": "知识",
        "profile": "档案",
        "me": "我的"
    }

    nav_items = ""
    for key, name in pages.items():
        active = 'active' if current == key else ''
        nav_items += f'<a href="#" onclick="navigate(\'{key}\')" class="nav-btn {active}">{name}</a>'

    # 用户头像（首字母）
    user_id = st.session_state.get('user_id', 'U')
    avatar_letter = user_id[0].upper() if user_id else 'U'

    st.markdown(f"""
    <div class="nav-bar">
        <div class="logo">HeartGuardian</div>
        <div class="nav-links">{nav_items}</div>
        <div class="user-menu">
            <div class="avatar">{avatar_letter}</div>
            <div class="dropdown">
                <a href="#" onclick="navigate('me')">个人中心</a>
                <a href="#" onclick="logout()">注销</a>
            </div>
        </div>
        <div class="hamburger">☰</div>
    </div>
    <style>
    :root {{
        --primary: #1a237e;
        --accent: #00e5ff;
        --danger: #ff5252;
        --bg: #0f1629;
        --text: #e1f5fe;
    }}
    body {{ background: var(--bg); color: var(--text); }}
    @keyframes gradientFlow {{
        0% {{ background-position: 0% 50%; }}
        100% {{ background-position: 200% 50%; }}
    }}
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(0,229,255,.7); }}
        70% {{ box-shadow: 0 0 0 10px rgba(0,229,255,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0,229,255,0); }}
    }}
    .nav-bar {{
        background: linear-gradient(90deg, var(--primary), #283593, #3949ab, #283593, var(--primary));
        background-size: 300% 100%;
        animation: gradientFlow 8s ease infinite;
        padding: 1rem 2rem;
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 30px rgba(0,0,0,.4);
        border-bottom: 1px solid rgba(0,229,255,.3);
        font-family: 'Segoe UI', sans-serif;
    }}
    .logo {{
        color: var(--accent);
        font-size: 1.8rem;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0,229,255,.6);
        animation: pulse 2s infinite;
    }}
    .nav-btn {{
        background: rgba(255,255,255,.1);
        color: var(--text);
        border: none;
        padding: .7rem 1.5rem;
        border-radius: 25px;
        font-size: 1rem;
        font-weight: 500;
        text-decoration: none;
        transition: all .3s;
        backdrop-filter: blur(5px);
    }}
    .nav-btn:hover {{
        background: var(--accent);
        color: var(--primary);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,229,255,.4);
    }}
    .nav-btn.active {{
        background: var(--danger);
        color: white;
        font-weight: bold;
        box-shadow: 0 0 15px rgba(255,82,82,.6);
        animation: pulse 1.5s infinite;
    }}
    .user-menu {{
        position: relative;
    }}
    .avatar {{
        width: 40px; height: 40px;
        border-radius: 50%;
        background: var(--accent);
        color: var(--primary);
        font-weight: bold;
        font-size: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all .3s;
    }}
    .avatar:hover {{
        transform: scale(1.1);
        box-shadow: 0 0 15px rgba(0,229,255,.6);
    }}
    .dropdown {{
        position: absolute;
        right: 0;
        top: 50px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0,0,0,.3);
        min-width: 160px;
        display: none;
        flex-direction: column;
        overflow: hidden;
    }}
    .dropdown a {{
        padding: .8rem 1rem;
        color: var(--primary);
        text-decoration: none;
        transition: all .2s;
    }}
    .dropdown a:hover {{
        background: #f0f7ff;
        color: var(--accent);
    }}
    .hamburger {{
        display: none;
        color: var(--text);
        font-size: 1.5rem;
        cursor: pointer;
        padding: .5rem;
    }}
    @media (max-width: 768px) {{
        .nav-links {{
            position: absolute;
            top: 100%;
            left: 0; right: 0;
            background: var(--primary);
            flex-direction: column;
            padding: 1rem;
            display: none;
            box-shadow: 0 4px 20px rgba(0,0,0,.3);
        }}
        .nav-links.active {{ display: flex; }}
        .hamburger {{ display: block; }}
    }}
    </style>

    <script>
    function navigate(page) {{
        const params = new URLSearchParams(window.location.search);
        params.set('page', page);
        window.location.search = params.toString();
    }}
    // 汉堡菜单切换
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    hamburger.addEventListener('click', () => {{
        navLinks.classList.toggle('active');
    }});

    // 头像下拉
    const avatar = document.querySelector('.avatar');
    const dropdown = document.querySelector('.dropdown');
    avatar.addEventListener('click', (e) => {{
        e.stopPropagation();
        dropdown.style.display = dropdown.style.display === 'flex' ? 'none' : 'flex';
    }});

    // 点击空白关闭下拉
    document.addEventListener('click', () => {{
        dropdown.style.display = 'none';
    }});

    // 注销
    function logout() {{
        window.location.href = "?logout=true";
    }}
    </script>
    """, unsafe_allow_html=True)

    # 留出高度
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)