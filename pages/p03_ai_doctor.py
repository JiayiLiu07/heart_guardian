# pages/p03_ai_doctor.py
import streamlit as st
from openai import OpenAI
from datetime import datetime
import uuid

# 配置 DashScope API
client = OpenAI(
    api_key="sk-e200005b066942eebc8c5426df92a6d5",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

st.set_page_config(page_title="AI 医生 · CardioGuard AI", layout="wide")

# ==========================================
# CSS 样式 - 严格对齐 p01_overview.py
# 主题色：智慧神经紫 (#8B5CF6 / #6D28D9)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        /* AI 医生专属配色 */
        --primary: #8B5CF6;
        --primary-dark: #6D28D9;
        --primary-light: #EDE9FE;
        
        /* 通用变量 */
        --gray-50: #F9FAFB;
        --gray-100: #F3F4F6;
        --gray-200: #E5E7EB;
        --gray-600: #4B5563;
        --gray-800: #1F2937;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .stApp {
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        background-color: #f8fafc;
    }
    
    .main > div { padding-top: 0 !important; }
    .block-container { padding: 1rem 2rem 2rem !important; max-width: 1400px; margin: 0 auto; }
    
    #MainMenu, footer, section[data-testid="stSidebar"] { display: none !important; }
    
    /* --- 导航栏 (严格对齐 Overview) --- */
    .top-navbar {
        background: white;
        padding: 0 2.5rem; /* 内边距一致 */
        height: 70px;      /* 高度一致 */
        box-shadow: var(--shadow-sm);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 9999;
        border-bottom: 1px solid var(--gray-200);
    }
    
    .nav-logo { 
        font-weight: 700; 
        font-size: 1.4rem; 
        color: var(--primary); /* 动态主色 */
        cursor: default; 
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .nav-links { 
        display: flex; 
        gap: 8px; /* 间距一致 */
    }
    .nav-links a { 
        text-decoration: none; 
        color: var(--gray-600); 
        font-weight: 500; 
        padding: 8px 16px; 
        border-radius: 20px; 
        transition: all 0.3s; 
        font-size: 0.95rem;
    }
    .nav-links a:hover { 
        background-color: var(--primary-light);
        color: var(--primary); 
    }
    .nav-links a.active { 
        background: var(--primary); /* 动态主色 */
        color: white; 
    }
    
    /* --- Hero 区域 (严格对齐 Overview) --- */
    .hero-box { 
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); /* 动态渐变 */
        padding: 2.5rem 2rem;   /* 内边距一致 */
        border-radius: 30px;    /* 圆角一致 */
        text-align: center; 
        color: white; 
        margin: 1rem 0 2rem 0; 
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .hero-box::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
        z-index: 1;
    }
    
    .hero-box::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.05) 25%, transparent 25%,
                    transparent 50%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.05) 75%,
                    transparent 75%, transparent);
        background-size: 30px 30px;
        animation: move 10s linear infinite;
        z-index: 1;
    }
    
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes move { 0% { background-position: 0 0; } 100% { background-position: 30px 30px; } }
    
    .hero-title, .hero-sub { position: relative; z-index: 2; }
    .hero-title { 
        font-size: 2.5rem; /* 字体大小一致 */
        font-weight: 700;  /* 字重一致 */
        margin: 0; 
        text-shadow: 0 2px 4px rgba(0,0,0,0.2); 
    }
    .hero-sub { 
        font-size: 1.1rem; 
        opacity: 0.95; 
        margin-top: 0.5rem; 
        text-shadow: 0 1px 2px rgba(0,0,0,0.1); 
    }
    
    /* 聊天区域 */
    .chat-section {
        margin-top: 1rem;
    }
    
    /* 示例问题区域 */
    .example-section {
        margin: 2rem 0 1rem 0;
    }
    .example-title {
        font-size: 1rem;
        color: var(--gray-600);
        margin-bottom: 0.8rem;
    }
    
    /* 聊天消息容器 */
    .stChatMessageContainer { 
        max-height: calc(100vh - 300px);
        overflow-y: auto;
        padding: 1rem;
        background: white;
        border-radius: 20px;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--gray-200);
    }
    
    /* 聊天输入框 */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 1.5rem !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: calc(100% - 25rem) !important;
        max-width: 900px !important;
        z-index: 9999 !important;
        background: white !important;
        border: 2px solid var(--primary-light) !important;
        border-radius: 9999px !important;
        box-shadow: var(--shadow-lg) !important;
        padding: 0.3rem 1rem !important;
    }
    
    /* --- 历史记录三列布局 (操作-时间-内容) --- */
    .history-row {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 4px;
        border-radius: 8px;
        margin-bottom: 4px;
        transition: background-color 0.2s;
    }
    .history-row:hover { background-color: var(--gray-50); }
    .history-row.active { background-color: var(--primary-light); }

    .col-action { flex: 0 0 30px; display: flex; justify-content: flex-start; align-items: center; }
    .col-time {
        flex: 0 0 55px;
        text-align: right;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--gray-600);
        font-family: 'Monaco', 'Consolas', monospace;
        line-height: 1.2;
        padding-top: 2px;
    }
    .history-row.active .col-time { color: var(--primary); }

    .col-content { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
    
    .mini-delete-btn {
        background: transparent !important;
        border: none !important;
        color: var(--gray-600) !important;
        font-size: 1rem !important;
        padding: 4px !important;
        margin: 0 !important;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
    }
    .mini-delete-btn:hover { color: #EF4444 !important; transform: scale(1.1); }

    .history-preview-text {
        font-size: 0.9rem;
        color: var(--gray-800);
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin: 0;
        padding: 2px 0;
    }
    .history-row.active .history-preview-text { color: var(--primary); font-weight: 600; }

    /* 按钮样式 */
    .stButton > button {
        background: white !important;
        color: var(--primary) !important;
        border: 1px solid var(--primary) !important;
        border-radius: 30px !important;
        font-weight: 500 !important;
        padding: 0.4rem 1.2rem !important;
        font-size: 0.9rem !important;
        transition: all 0.3s !important;
        width: 100%;
    }
    .stButton > button:hover {
        background: var(--primary) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md) !important;
    }
    
    /* 免责声明框 */
    .disclaimer-box {
        background-color: #FFFBEB;
        border-left: 4px solid #FCD34D;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        font-size: 0.8rem;
        color: #92400E;
        line-height: 1.4;
    }
    .disclaimer-title { font-weight: 700; margin-bottom: 0.4rem; font-size: 0.85rem; display: flex; align-items: center; gap: 6px; }

    /* 布局 */
    .flex-row { display: flex; gap: 2rem; }
    .flex-1 { flex: 1; }
    
    @media (max-width: 768px) { .flex-row { flex-direction: column; } }
</style>
""", unsafe_allow_html=True)

# ================= 逻辑部分 =================

def init_session_state():
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = {}
    if 'current_session_id' not in st.session_state:
        session_id = str(uuid.uuid4())
        now = datetime.now()
        st.session_state.chat_sessions[session_id] = {
            'id': session_id,
            'title': '新对话',
            'timestamp': now,
            'messages': [{"role": "assistant", "content": "您好！我是您的专属 AI 健康顾问。请描述您的症状或提出健康问题。"}]
        }
        st.session_state.current_session_id = session_id

def create_new_session():
    session_id = str(uuid.uuid4())
    now = datetime.now()
    st.session_state.chat_sessions[session_id] = {
        'id': session_id,
        'title': f'对话 {len(st.session_state.chat_sessions) + 1}',
        'timestamp': now,
        'messages': [{"role": "assistant", "content": "您好！我是您的专属 AI 健康顾问。请描述您的症状或提出健康问题。"}]
    }
    st.session_state.current_session_id = session_id

def delete_session(session_id):
    if session_id in st.session_state.chat_sessions:
        del st.session_state.chat_sessions[session_id]
        if session_id == st.session_state.current_session_id:
            if st.session_state.chat_sessions:
                latest = max(st.session_state.chat_sessions.values(), key=lambda x: x['timestamp'])
                st.session_state.current_session_id = latest['id']
            else:
                create_new_session()

def clear_all_history():
    st.session_state.chat_sessions = {}
    create_new_session()

def update_session_title(session_id, first_message):
    if session_id in st.session_state.chat_sessions:
        title = first_message[:15] + "..." if len(first_message) > 15 else first_message
        st.session_state.chat_sessions[session_id]['title'] = title
        now = datetime.now()
        st.session_state.chat_sessions[session_id]['timestamp'] = now

def main():
    init_session_state()
    
    # 顶部导航 (样式已统一)
    st.markdown("""
    <div class="top-navbar">
        <div class="nav-logo">❤️ CardioGuard AI</div>
        <div class="nav-links">
             <a href="/p00_home">🏠 首页</a>
            <a href="/p01_profile">📋 健康档案</a>
            <a href="/p01_overview">📊 健康总览</a>
            <a href="/p02_nutrition">🥗 营养建议</a>
            <a href="/p03_ai_doctor" class="active">🩺 AI 医生</a>
            <a href="/p04_knowledge">📚 知识库</a>
            <a href="/p05_me">👤 我的中心</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero 区域 (样式已统一)
    st.markdown("""
    <div class="hero-box">
        <h1 class="hero-title">🩺 AI 医生</h1>
        <p class="hero-sub">24小时心血管健康咨询，专业解答您的健康疑问</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        current_session = st.session_state.chat_sessions[st.session_state.current_session_id]
        messages = current_session['messages']
        
        # 聊天展示
        chat_container = st.container()
        with chat_container:
            for msg in messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        # 示例问题
        st.markdown('<div class="example-section">', unsafe_allow_html=True)
        st.markdown('<div class="example-title">💡 您可以这样提问：</div>', unsafe_allow_html=True)
        
        examples = ["高血压怎么控制", "冠心病有哪些症状", "房颤需要抗凝吗", "如何预防心力衰竭", "心梗急救怎么做"]
        cols = st.columns(5)
        for i, ex in enumerate(examples):
            with cols[i]:
                if st.button(ex, key=f"ex_{i}", use_container_width=True):
                    st.session_state.pending_prompt = ex
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 输入框
        prompt = st.chat_input("请输入您的问题...")
        if 'pending_prompt' in st.session_state:
            prompt = st.session_state.pop('pending_prompt')
        
        if prompt:
            if len([m for m in messages if m['role'] == 'user']) == 0:
                update_session_title(st.session_state.current_session_id, prompt)
            
            messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.spinner("AI 医生正在思考..."):
                try:
                    response = client.chat.completions.create(model="qwen-max", messages=messages)
                    ai_resp = response.choices[0].message.content
                    messages.append({"role": "assistant", "content": ai_resp})
                    with st.chat_message("assistant"): st.markdown(ai_resp)
                    
                    now = datetime.now()
                    st.session_state.chat_sessions[st.session_state.current_session_id]['timestamp'] = now
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        # 免责声明
        st.markdown("""
        <div class="disclaimer-box">
            <div class="disclaimer-title">⚠️ 重要医疗免责声明</div>
            <div>信息仅供参考，不能替代专业诊断。如有紧急情况，请立即就医。</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 新建按钮
        if st.button("➕ 新建对话", key="new_chat", use_container_width=True):
            create_new_session()
            st.rerun()
        
        # 清空按钮
        if st.button("🗑️ 清空历史", key="clear_hist", use_container_width=True):
            clear_all_history()
            st.rerun()
        
        st.markdown("<div style='height:1px; background:#E5E7EB; margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.8rem; color:#9CA3AF; margin-bottom:0.5rem;'>历史记录</div>", unsafe_allow_html=True)

        # 历史记录列表 (三列布局)
        if st.session_state.chat_sessions:
            sorted_sessions = sorted(st.session_state.chat_sessions.values(), key=lambda x: x['timestamp'], reverse=True)
            
            for session in sorted_sessions:
                is_active = session['id'] == st.session_state.current_session_id
                active_class = "active" if is_active else ""
                
                user_msgs = [m for m in session['messages'] if m['role'] == 'user']
                preview_text = user_msgs[0]['content'] if user_msgs else "新对话"
                if len(preview_text) > 18: preview_text = preview_text[:18] + "..."
                
                time_str = session['timestamp'].strftime("%H:%M")
                date_str = session['timestamp'].strftime("%m-%d")

                c_action, c_time, c_content = st.columns([0.15, 0.25, 0.6], gap="small")
                
                with c_action:
                    if st.button("🗑️", key=f"del_{session['id']}", help="删除此对话"):
                        delete_session(session['id'])
                        st.rerun()
                
                with c_time:
                    st.markdown(f"""
                    <div style="text-align:right; font-size:0.75rem; color:{'#8B5CF6' if is_active else '#9CA3AF'}; font-weight:600; font-family:monospace; padding-top:4px;">
                        {time_str}<br><span style="font-size:0.65rem; opacity:0.7">{date_str}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with c_content:
                    btn_type = "primary" if is_active else "secondary"
                    if st.button(
                        preview_text, 
                        key=f"load_{session['id']}", 
                        use_container_width=True,
                        type=btn_type if not is_active else "primary",
                        help="点击加载此对话"
                    ):
                        st.session_state.current_session_id = session['id']
                        st.rerun()
                
                st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style="text-align:center; padding:2rem; color:#9CA3AF;">
                <div style="font-size:2rem;">📭</div>
                <p style="font-size:0.9rem;">暂无历史记录</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()