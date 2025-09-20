# pages/_03_ai_doctor.py

import streamlit as st
import pandas as pd
import numpy as np  # Import numpy
from utils.ai_utils import get_ai_symptom_advice, nl_to_sql_cardio
from utils.database import UserManager, RedisManager
from utils.config import Config  # Ensure this is imported correctly
from datetime import datetime
import random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os # Added for font path checking

st.set_page_config(page_title="心守护 - AI问医生", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

# Register Chinese font
# Try to find SimSun.ttf in common locations or current directory
font_path = None
possible_font_paths = [
    'SimSun.ttf', # Current directory
    os.path.join(os.path.dirname(__file__), 'SimSun.ttf'), # Same directory as script
    os.path.join(os.path.dirname(__file__), '..', 'SimSun.ttf'), # Parent directory
    '/System/Library/Fonts/STHeiti Light.ttc', # Common macOS Chinese font
    '/Library/Fonts/SimSun.ttf',
    '/usr/share/fonts/truetype/simsun/SimSun.ttf' # Linux common path
]
for path in possible_font_paths:
    if os.path.exists(path):
        font_path = path
        break

if font_path:
    try:
        pdfmetrics.registerFont(TTFont('SimSun', font_path))
        st.sidebar.success(" SimSun 字体已成功加载。") # Use sidebar for less intrusive messages
    except Exception as e:
        st.sidebar.warning(f"注册 SimSun 字体失败：{e}")
else:
    st.sidebar.warning("未找到 SimSun.ttf 字体，将使用默认字体。")


st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    .main { background-color: #f9fafb; padding: 2rem; }
    .card { background: linear-gradient(145deg, #ffffff, #f1f5f9); border-radius: 12px; padding: 18px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,30,0.1); transition: transform 0.25s; }
    .card:hover { box-shadow: 0 6px 16px rgba(0,0,30,0.15); transform: scale(1.02); }
    .btn { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 min-h-[44px] font-semibold transition-colors duration-200; }
    .chat-container { @apply bg-white p-4 rounded-lg shadow-md border border-gray-200 max-h-[500px] overflow-y-auto; }
    .chat-bubble-user { @apply bg-gradient-to-r from-green-100 to-green-200 p-3 rounded-lg my-2 ml-auto max-w-[70%] border border-green-200 flex items-start gap-2 relative animate-slideInChat; }
    .chat-bubble-ai { @apply bg-gradient-to-r from-blue-100 to-blue-200 p-3 rounded-lg my-2 mr-auto max-w-[70%] border border-blue-200 flex items-start gap-2 animate-slideInChat; }
    @keyframes slideInChat { from { transform: translateX(20px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
</style>
""", unsafe_allow_html=True)


def speech_input_component(key):
    return st.components.v1.html(
        f"""
        <button id="speech-btn-{key}" class="btn" aria-label="开始或停止语音输入">🎤 开始/停止语音</button>
        <p style="color: #555; font-size: 12px;">请使用 Chrome 或 Edge 浏览器以获得最佳语音体验</p>
        <script>
            try {{
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'zh-CN';
                recognition.continuous = true;
                recognition.maxAlternatives = 1;
                let isRecording = false;
                recognition.onresult = (event) => {{
                    const transcript = event.results[event.results.length-1][0].transcript;
                    Streamlit.setComponentValue(transcript, '{key}');
                }};
                recognition.onend = () => {{
                    isRecording = false;
                    document.getElementById('speech-btn-{key}').innerText = '🎤 开始/停止语音';
                }};
                recognition.onerror = (event) => {{
                    console.error('Speech recognition error: ', event.error);
                }};
                document.getElementById('speech-btn-{key}').addEventListener('click', () => {{
                    if (isRecording) {{
                        recognition.stop();
                    }} else {{
                        recognition.start();
                        document.getElementById('speech-btn-{key}').innerText = '🎤 录音中...';
                        // Consider a more robust timeout or user-controlled stop
                        // setTimeout(() => {{ recognition.stop(); }}, 30000); // 30 seconds timeout
                    }}
                    isRecording = !isRecording;
                }});
            }} catch (e) {{
                console.error('Speech recognition not supported: ', e);
            }}
        </script>
        """, height=80
    )

def check_medication_compatibility(medication_history: list, disease_tags: list) -> list:
    """
    Checks for potential drug interactions based on medication history and diseases.
    Returns a list of warning messages.
    """
    warnings = []

    # Process medication_history to get a consistent list of medication names (strings)
    medication_names = []
    if isinstance(medication_history, list):
        for med_item in medication_history:
            if isinstance(med_item, str):
                medication_names.append(med_item)
            elif isinstance(med_item, dict) and 'name' in med_item:
                medication_names.append(med_item['name'])
            # Optionally, log a warning for unexpected item types
            # else:
            #     st.warning(f"Unexpected item type in medication history: {type(med_item)}")

    # Get disease tags config from the Config class
    disease_tags_config = Config.get_disease_tags()

    for tag in disease_tags:  # Iterate through the list of disease tags for the user
        if ':' not in tag:
            continue
        main_type, subtype = tag.split(':')

        # Safely access config values using the class method and .get() for nested dicts
        disease_config = disease_tags_config.get(main_type, {}).get('subtypes', {}).get(subtype, {})

        # Case-insensitive comparisons for tags and medication names
        if 'PAD' in tag.upper():
            # Check if any medication name contains 'NSAID' (case-insensitive)
            if any('NSAID' in med.upper() for med in medication_names):
                warnings.append("警告：外周动脉疾病患者需谨慎使用非甾体抗炎药，请咨询医生（ADA 2021, PMID: 33298413）")

        elif 'HFrEF' in tag.upper() and any('NSAID' in med.upper() for med in medication_names):
            warnings.append("警告：射血分数降低型心衰患者禁用非甾体抗炎药，可能加重心衰（ESC 2021, PMID: 34447992）")

        elif 'CAD' in tag.upper() and not any('statin' in med.lower() for med in medication_names):
            warnings.append("警告：冠心病患者建议使用他汀类药物控制胆固醇（ESC 2019, PMID: 31504424）")

        elif 'AF' in tag.upper() and any('caffeine' in med.lower() for med in medication_names):
            warnings.append("警告：心房颤动患者避免含咖啡因药物，可能诱发心律失常（EHRA 2021, PMID: 34097040）")

        elif 'CVD' in tag.upper() and not any('antihypertensive' in med.lower() for med in medication_names):
            warnings.append("警告：脑血管病患者需使用降压药控制血压（AHA 2021, PMID: 34109933）")

    return warnings


def main():
    # Initialize session state if not already done
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "您好！我是您的AI健康顾问，有什么可以帮您的？"}]
    if 'selected_symptoms' not in st.session_state:
        st.session_state.selected_symptoms = []
    if 'severity' not in st.session_state:
        st.session_state.severity = ["中等"]
    if 'user_id' not in st.session_state or not st.session_state.user_id:
        # Handle case where user_id is not set, e.g., redirect or show error
        st.error("请先登录！")
        # Assuming app.py is your login/landing page
        st.switch_page("app.py")
        st.stop()

    user_manager = UserManager(RedisManager())
    user_data = user_manager.get_user_info(st.session_state.user_id)

    # Define default user_data structure if user info is not found
    default_user_data = {
        'disease_tags': ['HTN:WCHT'],
        'medication_history': [],
        'symptom_history': [],
        'cardio_daily': [],
        'today_data': {'sodium_intake': 0.0, 'ap_hi': 120.0, 'ap_lo': 80.0, 'heart_rate': 70.0}, # Ensure all required keys exist with floats
        'chat_history': [{"role": "assistant", "content": "您好！我是您的AI健康顾问，有什么可以帮您的？"}]
    }
    # Merge user_data with defaults, prioritizing user_data if it exists
    if user_data is None:
        user_data = default_user_data
    else:
        # Update user_data with defaults to ensure all keys are present
        for key, default_value in default_user_data.items():
            if key not in user_data:
                user_data[key] = default_value
            # Special handling for nested dicts like today_data
            elif isinstance(default_value, dict) and isinstance(user_data.get(key), dict):
                for sub_key, default_sub_value in default_value.items():
                    if sub_key not in user_data[key]:
                        user_data[key][sub_key] = default_sub_value
            elif isinstance(default_value, list) and isinstance(user_data.get(key), list):
                # No specific update needed for lists if they exist, but ensures key is present
                pass


    # Ensure subtype is derived from the potentially updated user_data
    subtype = user_data.get('disease_tags', ['HTN:WCHT'])[0].split(':')[1] if user_data.get('disease_tags') else 'WCHT'


    # Safely get today_data with float defaults, assuming the merge above handled defaults
    today_data = {
        'ap_hi': float(user_data.get('today_data', {}).get('ap_hi', 120.0)),
        'ap_lo': float(user_data.get('today_data', {}).get('ap_lo', 80.0)),
        'heart_rate': float(user_data.get('today_data', {}).get('heart_rate', 70.0)),
        'sodium_intake': float(user_data.get('today_data', {}).get('sodium_intake', 0.0))
    }


    with st.sidebar:
        st.markdown('<h3 class="text-lg font-semibold text-gray-700">导航</h3>', unsafe_allow_html=True)
        if st.button("🏠 返回主页"):
            st.switch_page("app.py")
        st.markdown('<hr class="my-4">', unsafe_allow_html=True)

        with st.expander("近期症状记录"):
            symptom_history = user_data.get('symptom_history', [])
            if symptom_history:
                # Sort by date, ensuring date is valid before parsing
                symptom_history_sorted = sorted(
                    [s for s in symptom_history if s.get('date')], # Filter out entries without date
                    key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
                    reverse=True
                )
                for symptom in symptom_history_sorted[-5:]:
                    st.markdown(f"- {symptom.get('symptom', '未知症状')} ({symptom.get('severity', '未知')}, {symptom.get('date', '未知日期')})")
            else:
                st.info("暂无症状记录")

    tab1, tab2 = st.tabs(["症状咨询", "数据问答"])

    with tab1:
        st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">症状咨询</h3>', unsafe_allow_html=True)
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f'<div class="chat-bubble-user"><span class="text-2xl">👤</span>{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai"><span class="text-2xl">🤖</span>{msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input("描述您的症状：", placeholder="例如：我最近感到胸痛和心悸", key="symptom_query")
        with col2:
            speech_input_component("symptom_query")

        if st.button("提交症状"):
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                selected_symptoms = st.session_state.get('selected_symptoms', [])
                severity = st.session_state.get('severity', ["中等"])
                # Safely get sodium intake from today_data
                current_sodium_intake = today_data.get('sodium_intake', 0.0)

                try:
                    # Pass the correct user_data object to the function
                    response = get_ai_symptom_advice(user_data, selected_symptoms, severity, current_sodium_intake)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    # Ensure user_manager is initialized correctly and update user info
                    user_manager.update_user_info(st.session_state.user_id, {'chat_history': st.session_state.chat_history})
                    st.rerun()
                except Exception as e:
                    st.error(f"获取建议失败：{str(e)}")
            else:
                st.warning("请输入症状描述。")

        col_buttons1, col_buttons2 = st.columns(2)
        with col_buttons1:
            if st.button("清除聊天记录", key="clear_chat", type="secondary"):
                st.session_state.chat_history = []
                user_manager.update_user_info(st.session_state.user_id, {'chat_history': []})
                st.rerun()
        with col_buttons2:
            if st.button("生成症状建议书"):
                with st.spinner("正在生成建议书..."):
                    buffer = BytesIO()
                    c = canvas.Canvas(buffer, pagesize=A4)
                    font_name = 'SimSun' if 'SimSun' in pdfmetrics.getRegisteredFontNames() else "Helvetica"
                    c.setFont(font_name, 16)
                    c.drawString(50, A4[1]-50, "症状建议书")
                    c.setFont(font_name, 12)
                    y = A4[1] - 100

                    # Limit to last 5 messages for brevity, or show all if less than 5
                    messages_to_print = st.session_state.chat_history[-5:] if len(st.session_state.chat_history) > 5 else st.session_state.chat_history

                    for msg in reversed(messages_to_print):
                        role_prefix = f"{msg['role'].capitalize()}: "
                        text_content = msg['content']
                        full_text = role_prefix + text_content

                        # Wrap text within the page width
                        lines = []
                        current_line = ""
                        max_width_chars = 60 # Approximate character limit per line for A4 at 12pt

                        # Simple word wrapping logic
                        words = full_text.split()
                        for word in words:
                            if c.stringWidth(current_line + word + " ", font_name) < max_width_chars * 7: # Approx width of char * max_width_chars
                                current_line += word + " "
                            else:
                                lines.append(current_line.strip())
                                current_line = word + " "
                        lines.append(current_line.strip())

                        # Draw lines to PDF
                        for line in reversed(lines):
                            if y < 50:  # Start new page if too close to bottom
                                c.showPage()
                                c.setFont(font_name, 12)
                                y = A4[1] - 50
                            c.drawString(50, y, line)
                            y -= 15 # Move down for the next line

                    c.save()
                    buffer.seek(0)
                    st.download_button("下载建议书", data=buffer, file_name="advice.pdf", mime="application/pdf")

        with st.expander("药物冲突警告"):
            # Ensure medication_history and disease_tags are always lists
            medication_history = user_data.get('medication_history', []) if isinstance(user_data.get('medication_history'), list) else []
            disease_tags = user_data.get('disease_tags', []) if isinstance(user_data.get('disease_tags'), list) else []
            warnings = check_medication_compatibility(medication_history, disease_tags)
            if warnings:
                for warning in warnings:
                    st.error(warning)
            else:
                st.info("未检测到药物冲突")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">数据问答</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input("用中文问数据：", placeholder="例如：上周我的平均收缩压比前一周降了多少？", key="data_question")
        with col2:
            speech_input_component("data_question")

        if st.button("提交查询"):
            if question:
                try:
                    cardio_data = user_data.get('cardio_daily', [])
                    # Ensure cardio_data is a list of dicts, or empty list if invalid
                    if not isinstance(cardio_data, list):
                        st.warning("心血管数据格式不正确，无法查询。")
                        cardio_data = []

                    sql, df, fig = nl_to_sql_cardio(question, cardio_data)

                    if fig:
                        st.plotly_chart(fig, width='stretch')

                    if not df.empty:
                        # Ensure numeric columns are processed correctly and handle potential NaNs
                        numeric_cols = df.select_dtypes(include=np.number).columns

                        # Apply styling only to numeric columns and check for positive values
                        # Using a function for applymap to handle non-numeric types gracefully
                        def style_numeric(x):
                            if isinstance(x, (int, float)) and not pd.isna(x) and x > 0:
                                return 'background-color: #f3f4f6'
                            return ''

                        styled_df = df.style.applymap(
                            style_numeric,
                            subset=pd.IndexSlice[:, numeric_cols] # Apply to numeric columns
                        ).set_properties(**{'color': '#1e3a8a'}) # Set text color for all cells

                        st.dataframe(styled_df, width='stretch', hide_index=False)
                    else:
                        st.info("无相关数据")
                except Exception as e:
                    st.error(f"查询失败：{str(e)}")
            else:
                st.warning("请输入您想查询的数据问题。")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()