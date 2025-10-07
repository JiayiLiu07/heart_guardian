import streamlit as st
import time
import os
from dashscope import Generation
from pages.p04_knowledge import KNOWLEDGE_BASE, flatten_kb
from pages.p01_profile import load_profile_data
from pages.p05_me import save_user_base_info, load_user_base_info

# --- API Key and Client Initialization ---
ALI_ACCESS_KEY_ID = os.environ.get("ALI_ACCESS_KEY_ID")
ALI_ACCESS_KEY_SECRET = os.environ.get("ALI_ACCESS_KEY_SECRET")

client_dashscope = None
try:
    if ALI_ACCESS_KEY_ID and ALI_ACCESS_KEY_SECRET:
        os.environ['DASHSCOPE_API_KEY'] = ALI_ACCESS_KEY_SECRET
        client_dashscope = Generation
except Exception as e:
    st.error(f"Dashscope 初始化失败: {e}")

# --- Prompt Template ---
PROMPT_TEMPLATE_USER = """
你是一名专业的AI心脏健康助手，请根据用户提供的症状和信息，给出专业的、易于理解的医疗建议。
回答时请遵循以下规则：
1. **专业性**: 确保信息准确，符合医学常识，参考《2023 Braunwald’s Heart Disease》和《2022 ESC/ACC 指南》。
2. **易懂性**: 使用通俗易懂的语言，避免过多专业术语。
3. **信息引用**: 在回答末尾简要提及信息来源（如：《2021 ESC 心血管预防指南》第 42 页）。
4. **行动建议**: 给出明确的下一步行动建议（如：就医、调整生活方式）。
5. **不诊断**: **绝对不要**给出疾病诊断，只提供建议和信息。
6. **用户数据**: 考虑用户档案数据（如果有）：{user_data}
用户输入：{user_input}
"""

# --- Quick Questions ---
QUICK_QUESTIONS = {
    "高血压": "我的血压经常在 140/90 mmHg 以上，应该怎么办？",
    "冠心病": "我有时胸口痛，尤其运动时，可能是冠心病吗？",
    "心力衰竭": "我感觉气短和脚肿，可能和心脏有关吗？",
    "心律失常": "我经常心悸，感觉心跳不规律，怎么办？",
    "心肌病": "我被确诊为心肌病，应该注意什么？",
    "心脏瓣膜病": "我有瓣膜病，饮食和生活上需要注意什么？"
}

def ask_ai_doctor(user_query, user_data):
    prompt = PROMPT_TEMPLATE_USER.format(user_input=user_query, user_data=str(user_data))
    if client_dashscope:
        try:
            response = client_dashscope.call(
                model="qwen-turbo",
                prompt=prompt
            )
            return response.output.text
        except Exception as e:
            st.error(f"Dashscope 调用失败: {e}")
            return "AI 建议: 请咨询专业医生。"
    else:
        return "AI 医生服务不可用，使用 dummy 建议: 多喝水，注意休息，请咨询医生。"

def render():
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("请先登录以使用 AI 医生。")
        user_id = 'default_user'
        user_data = {}
    else:
        user_id = st.session_state.user_id
        user_data = load_profile_data(user_id)

    st.title("AI医生咨询")

    # 初始化历史记录
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # 两列布局：左侧对话区，右侧历史记录抽屉
    col1, col2 = st.columns([8, 4])
    
    with col1:
        st.markdown("### 咨询 AI 医生")
        # 快捷问题按钮
        st.markdown("#### 快捷问题")
        cols = st.columns(3)
        for i, (disease, question) in enumerate(QUICK_QUESTIONS.items()):
            with cols[i % 3]:
                if st.button(disease, key=f"quick_{disease}"):
                    st.session_state.current_question = question

        # 用户输入
        user_input = st.text_input("请输入您的症状或问题:", value=st.session_state.get('current_question', ''), key="user_input")
        if user_input == '':
            st.info("暂无对话，试试输入“我血压 140/90 怎么办”")
        
        if st.button("咨询 AI", key="consult_ai"):
            if user_input:
                st.info("AI 正在思考...")
                full_response = ask_ai_doctor(user_input, user_data)
                st.markdown(full_response)
                # 添加知识引用
                related_knowledge = [item for item in flatten_kb(KNOWLEDGE_BASE) if any(keyword in item['path'] or keyword in item['content'] for keyword in user_input.split())]
                if related_knowledge:
                    full_response += "\n\n**知识来源**："
                    for item in related_knowledge[:2]:
                        full_response += f"\n- 《{item['path']}》（知识库）"
                else:
                    full_response += "\n\n**知识来源**：基于《2021 ESC 心血管预防指南》第 42 页"
                # 保存到历史记录
                st.session_state.chat_history.append({"question": user_input, "answer": full_response, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
                # 保存到笔记
                if st.button("保存对话到笔记", key="save_to_notes"):
                    notes = f"咨询问题: {user_input}\nAI回答: {full_response}\n时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    current_notes = load_user_base_info(user_id).get('health_notes', '')
                    save_user_base_info(user_id, {'health_notes': current_notes + notes})
                    st.success("对话已保存到笔记")
            else:
                st.warning("请输入问题。")

    with col2:
        st.markdown("### 历史记录 🕘")
        with st.expander("查看历史记录"):
            if st.session_state.chat_history:
                for i, chat in enumerate(st.session_state.chat_history):
                    st.markdown(f"**{chat['timestamp']}**")
                    st.markdown(f"**问**: {chat['question']}")
                    st.markdown(f"**答**: {chat['answer']}")
                    st.markdown("---")
            else:
                st.info("暂无历史记录")

if __name__ == "__main__":
    render()