# pages/03_ai_doctor.py
import streamlit as st
import time
import os
from utils.api import client
from pages.p01_profile import load_profile_data
from utils.disease_dict import DISEASE_ENUM
from utils.cache import cache_response, load_cached_response

PROMPT_TEMPLATE = """
你是一名专业AI心脏健康助手，根据用户症状和档案{user_data}，给出易懂建议。
规则：专业准确，通俗语言，不诊断，只建议。引用来源如《2023 Braunwald’s Heart Disease》。
用户输入：{user_input}
"""

def ask_ai_doctor(user_query, user_data):
    cache_key = f"ai_doctor_{hash(user_query)}_{st.session_state.get('user_id')}"
    cached = load_cached_response(cache_key)
    if cached:
        return cached
    prompt = PROMPT_TEMPLATE.format(user_data=user_data, user_input=user_query)
    with st.spinner("生成AI建议..."):
        try:
            response = client.chat.completions.create(model="qwen-turbo", messages=[{"role": "user", "content": prompt}])
            answer = response.choices[0].message.content
            cache_response(cache_key, answer)
            return answer
        except Exception as e:
            st.error(f"AI咨询失败: {str(e)}")
            return None

def render():
    st.markdown("<style>section[data-testid='stSidebar'], .stSidebar, [data-testid='collapsedControl'], #MainMenu, footer {display: none !important;}</style>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    :root{--p:#1a237e;--a:#00e5ff;--bg:#0f1629;}
    body{background:var(--bg);color:#e1f5fe;}
    .hero{background:linear-gradient(135deg,var(--p),#283593,#3949ab);padding:3rem 1rem;border-radius:15px;text-align:center;color:white;margin:2rem 0;}
    .chat-container {height:60vh;overflow-y:auto;scroll-behavior:smooth;padding:1rem;border:1px solid rgba(0,229,255,.2);border-radius:15px;background:rgba(255,255,255,.05);backdrop-filter:blur(10px);}
    .chat-container::-webkit-scrollbar {width:8px;}
    .chat-container::-webkit-scrollbar-thumb {background:var(--a);border-radius:4px;}
    .bubble-user {background:rgba(0,229,255,.2);border-radius:18px 18px 0 18px;padding:1rem;margin:1rem 0;max-width:70%;align-self:flex-end;color:white;}
    .bubble-ai {background:white;border-radius:18px 18px 18px 0;padding:1rem;margin:1rem 0;max-width:70%;align-self:flex-start;border-left:4px solid var(--danger);color:var(--p);}
    .send-btn {animation:heartbeat 1.5s infinite;}
    @keyframes heartbeat {0%{transform:scale(1)}14%{transform:scale(1.3)}28%{transform:scale(1)}42%{transform:scale(1.3)}70%{transform:scale(1)}}
    .quick-btn {background:rgba(255,255,255,.1);border:1px solid var(--a);border-radius:12px;padding:.5rem;margin:.25rem;color:white;width:100%;transition:all .3s;}
    .quick-btn:hover {background:var(--a);color:var(--p);}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hero"><h1>AI 心脏医生</h1><p>专业咨询，守护健康</p></div>', unsafe_allow_html=True)

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.warning("请登录")
        return

    user_data = load_profile_data(user_id)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    cols = st.columns(5)
    quick_questions = {k: f"关于{DISEASE_ENUM[k]['label']}的建议" for k in DISEASE_ENUM if k != 'none'}
    for i, (k, q) in enumerate(quick_questions.items()):
        if i < 15:  # 5列 x 3行
            with cols[i % 5]:
                if st.button(q, type="secondary", key=f"q_{i}"):
                    response = ask_ai_doctor(q, user_data)
                    if response:
                        st.session_state.chat_history.append({"question": q, "answer": response})
                        st.rerun()

    chat = st.container()
    with chat:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            st.markdown(f'<div class="bubble-user">{msg["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bubble-ai">{msg["answer"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    input_col, btn_col = st.columns([8,2])
    with input_col:
        user_input = st.text_input("您的症状或问题", placeholder="例如: 血压140/90怎么办?")
    with btn_col:
        if st.button("发送", type="primary", key="send"):
            if user_input:
                response = ask_ai_doctor(user_input, user_data)
                if response:
                    st.session_state.chat_history.append({"question": user_input, "answer": response})
                    st.rerun()

if __name__ == "__main__":
    render()