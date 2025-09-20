# pages/_01_dashboard.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
# Assuming CVDRiskPredictor, create_risk_gauge, create_radar_cardio are correctly imported and defined
from utils.ml_model import CVDRiskPredictor
from utils.visualization import create_risk_gauge, create_radar_cardio
from utils.database import UserManager, RedisManager
from utils.ai_utils import get_ai_symptom_advice
from utils.config import Config
import random

st.set_page_config(page_title="心守护 - 健康概览", page_icon="❤️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    .main { background-color: #f9fafb; padding: 2rem; }
    .card { background: linear-gradient(145deg, #ffffff, #f1f5f9); border-radius: 12px; padding: 18px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,30,0.1); transition: transform 0.25s; }
    .card:hover { box-shadow: 0 6px 16px rgba(0,0,30,0.15); transform: scale(1.02); }
    .btn { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 min-h-[44px] font-semibold transition-colors duration-200; }
    .suggestion-box { @apply bg-gradient-to-r from-blue-50 to-green-50 p-4 rounded-lg border border-blue-200 mt-4 flex items-center gap-4 animate-slideIn; }
    @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>
""", unsafe_allow_html=True)

def check_medication_compatibility(medication, disease_tags):
    warnings = []
    for tag in disease_tags:
        if ':' not in tag:
            continue
        main_type, subtype = tag.split(':')
        # Safely access config values
        # Correctly access DISEASE_TAGS using the class method
        disease_config = Config.get_disease_tags().get(main_type, {}).get('subtypes', {}).get(subtype, {})

        if 'HFrEF' in tag and any('NSAID' in med.upper() for med in medication): # Case-insensitive check
            warnings.append("射血分数降低型心衰患者禁用非甾体抗炎药，可能加重心衰（ESC 2021, PMID: 34447992）")
        elif 'PAD' in tag and any('NSAID' in med.upper() for med in medication):
            warnings.append("外周动脉疾病患者需谨慎使用非甾体抗炎药，请咨询医生（ADA 2021, PMID: 33298413）")
        elif 'CAD' in tag and not any('statin' in med.lower() for med in medication):
            warnings.append("冠心病患者建议使用他汀类药物控制胆固醇（ESC 2019, PMID: 31504424）")
        elif 'AF' in tag and any('caffeine' in med.lower() for med in medication):
            warnings.append("心房颤动患者避免含咖啡因药物，可能诱发心律失常（EHRA 2021, PMID: 34097040）")
        elif 'CVD' in tag and not any('antihypertensive' in med.lower() for med in medication):
            warnings.append("脑血管病患者需使用降压药控制血压（AHA 2021, PMID: 34109933）")
    return warnings

def create_body_heatmap():
    # Simplified mapping for demonstration; a real implementation might be more complex
    symptom_map = {
        "head": ["心悸", "头晕", "视力模糊"],
        "chest": ["胸痛", "呼吸困难"],
        "abdomen": ["乏力"],
        "left_leg": ["间歇性跛行", "足部麻木"]
    }
    return symptom_map

def main():
    # Initialize session state if not already done
    if 'selected_symptoms' not in st.session_state:
        st.session_state.selected_symptoms = []
    if 'severity' not in st.session_state:
        st.session_state.severity = ["中等"]

    user_manager = UserManager(RedisManager())
    # Ensure user_id is available
    if 'user_id' not in st.session_state or not st.session_state.user_id:
        st.error("请先登录！")
        st.switch_page("app.py")
        st.stop()

    user_data = user_manager.get_user_info(st.session_state.user_id) or {
        'disease_tags': ['HTN:WCHT'],
        'today_data': {'ap_hi': 120.0, 'ap_lo': 80.0, 'heart_rate': 70.0, 'sodium_intake': 0.0}, # Ensure defaults as floats
        'cardio_daily': [],
        'symptom_history': [],
        'medication_history': [],
        'risk_score': 0.0,
        'basic_info': {'age': 30.0, 'gender': '男', 'height': 170.0, 'weight': 70.0} # Ensure defaults as floats
    }
    subtype = user_data.get('disease_tags', ['HTN:WCHT'])[0].split(':')[1]

    # Safely get today_data with float defaults
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

        def save_bp():
            # Use session state if available, otherwise fallback to today_data
            bp_hi = float(st.session_state.bp_hi if 'bp_hi' in st.session_state else today_data.get('ap_hi', 120.0))
            bp_lo = float(st.session_state.bp_lo if 'bp_lo' in st.session_state else today_data.get('ap_lo', 80.0))
            heart_rate = float(st.session_state.heart_rate if 'heart_rate' in st.session_state else today_data.get('heart_rate', 70.0))

            # Validate input ranges
            if not (80 <= bp_hi <= 250 and 50 <= bp_lo <= 150 and 30 <= heart_rate <= 200):
                st.error("血压或心率值超出有效范围！")
                return

            # Ensure cardio_daily list exists
            if 'cardio_daily' not in user_data:
                user_data['cardio_daily'] = []

            user_data['cardio_daily'].append({
                'date': datetime.now().strftime("%Y-%m-%d"),
                'ap_hi': bp_hi,
                'ap_lo': bp_lo,
                'heart_rate': heart_rate
            })
            user_manager.update_user_info(st.session_state.user_id, user_data)
            st.success("血压记录成功！")
            # Update today_data in user_data for immediate display consistency
            user_data['today_data'] = {'ap_hi': bp_hi, 'ap_lo': bp_lo, 'heart_rate': heart_rate, 'sodium_intake': today_data.get('sodium_intake', 0.0)}
            user_manager.update_user_info(st.session_state.user_id, user_data) # Save updated today_data

        with st.form("quick_health_form"):
            st.markdown("### 快速健康记录")
            # Use .get() with defaults for safety, ensure float values
            bp_hi_val = float(today_data.get('ap_hi', 120.0))
            bp_lo_val = float(today_data.get('ap_lo', 80.0))
            hr_val = float(today_data.get('heart_rate', 70.0))

            bp_hi = st.number_input("收缩压 (mmHg)", min_value=80.0, max_value=250.0, step=1.0, value=bp_hi_val, key="bp_hi")
            bp_lo = st.number_input("舒张压 (mmHg)", min_value=50.0, max_value=150.0, step=1.0, value=bp_lo_val, key="bp_lo")
            heart_rate = st.number_input("心率 (bpm)", min_value=30.0, max_value=200.0, step=1.0, value=hr_val, key="heart_rate")

            if st.form_submit_button("记录", key="submit_health_record"):
                save_bp()
                st.rerun()

        # Display warning based on fetched today_data (using potentially updated values after save_bp)
        if today_data.get('ap_hi', 0.0) > 140.0:
            st.warning("⚠️ 血压偏高，请咨询医生！")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">风险评分</h3>', unsafe_allow_html=True)
        # Ensure risk_score is a float and within bounds for the gauge
        risk_score_val = float(user_data.get('risk_score', 0.0))
        risk_score_val = np.clip(risk_score_val, 0.0, 100.0) # Clamp between 0 and 100
        st.plotly_chart(create_risk_gauge(risk_score_val), width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">心血管健康维度</h3>', unsafe_allow_html=True)
        # Safely get and calculate values, ensuring they are floats and within range
        # Correctly access DISEASE_TAGS using the class method
        sodium_limit_val = float(Config.get_disease_tags().get('HTN', {}).get('subtypes', {}).get(subtype, {}).get('sodium_limit', 1500.0))
        sodium_intake_val = float(today_data.get('sodium_intake', 0.0))
        sodium_percent_val = np.clip(1.0 - (sodium_intake_val / sodium_limit_val if sodium_limit_val > 0 else 1.0), 0.0, 1.0)

        bp_hi_val = float(today_data.get('ap_hi', 120.0))
        # Normalize blood pressure score (higher is better for score, so use 1 - normalized deviation)
        bp_deviation = (bp_hi_val - 90.0) / (180.0 - 90.0) # Assuming target around 90-180 range for deviation calculation
        bp_score_val = np.clip(1.0 - bp_deviation, 0.0, 1.0)

        # Assuming Exercise_Days and Smoke_Free_Days are available in local_data
        # Add checks for 'local_data' existence and default to 0.0 if missing
        local_data = user_data.get('local_data', {})
        exercise_days_val = float(local_data.get('Exercise_Days', 0.0)) / 7.0
        smoke_free_days_val = float(local_data.get('Smoke_Free_Days', 0.0)) / 30.0 # Assuming monthly tracking

        st.plotly_chart(create_radar_cardio(sodium_percent_val, bp_score_val, exercise_days_val, smoke_free_days_val, sodium_limit_val), width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">疾病饮食建议</h3>', unsafe_allow_html=True)
        diet_tips = {
            'WCHT': "增加水果和蔬菜摄入，避免加工食品。每日钠摄入≤1500mg（ESH 2020, PMID: 33027117）。",
            'MHT': "选择低脂蛋白食物（如鱼、瘦肉），减少饱和脂肪。每日钠摄入≤1500mg（ESH 2020, PMID: 33027117）。",
            'HFrEF': "多吃富含钾的食物（如香蕉、菠菜），严格限制钠和液体摄入。每日钠摄入≤1200mg（ESC 2021, PMID: 34447992）。",
            'CAD': "遵循低脂饮食，控制胆固醇摄入（如坚果、鱼）。每日钠摄入≤1500mg（ESC 2019, PMID: 31504424）。",
            'AF': "避免刺激性食物和饮料（如咖啡、酒精）。每日钠摄入≤1500mg（EHRA 2021, PMID: 34097040）。",
            'CVD': "控制血压和血脂，选择低升糖指数食物。每日钠摄入≤1500mg（AHA 2021, PMID: 34109933）。",
            'PAD': "选择低升糖指数食物（如糙米、豆类），戒烟，控制血糖。每日钠摄入≤1500mg（ADA 2021, PMID: 33298413）。"
        }
        disease_tags = user_data.get('disease_tags', ['HTN:WCHT'])
        for tag in disease_tags:
            if ':' in tag:
                current_subtype = tag.split(':')[1]
                st.markdown(f'<div class="suggestion-box"><span class="text-2xl">🍎</span><span>{diet_tips.get(current_subtype, "遵循低钠、低脂饮食，增加水果蔬菜摄入。")}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">一键打卡</h3>', unsafe_allow_html=True)
    with st.form("daily_checkin"):
        tasks = ["步行30分钟", "低钠饮食"]
        if 'daily_checkins' not in user_data:
            user_data['daily_checkins'] = []

        today_date = datetime.now().strftime("%Y-%m-%d")
        today_checkin = next((item for item in user_data['daily_checkins'] if item.get('date') == today_date), None)

        current_tasks_status = {}
        if today_checkin:
            current_tasks_status = {task: task in today_checkin.get('tasks', []) for task in tasks}
        else:
            current_tasks_status = {task: False for task in tasks}

        checks = {task: st.checkbox(task, value=current_tasks_status.get(task, False)) for task in tasks}

        if st.form_submit_button("记录", key="submit_daily_checkin"):
            checked_tasks = [task for task, checked in checks.items() if checked]

            if today_checkin:
                today_checkin['tasks'] = checked_tasks
            else:
                user_data['daily_checkins'].append({
                    'date': today_date,
                    'tasks': checked_tasks
                })
            user_manager.update_user_info(st.session_state.user_id, user_data)
            st.success("打卡成功！")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- 新版词云 ----------
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        symptom_history = user_data.get('symptom_history', [])
        # 构造空格分隔的字符串（词频默认 1）
        text = " ".join([s.get('symptom', '') for s in symptom_history if s.get('symptom')])
        if text:
            st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">症状词云</h3>', unsafe_allow_html=True)
            wc = WordCloud(
                font_path="/System/Library/Fonts/STHeiti Medium.ttc",                background_color="white",
                width=800, height=400,
                colormap="viridis",
                max_words=200
            ).generate(text)

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("暂无症状记录，词云为空")
    except ImportError:
        st.warning("请安装 wordcloud 以启用症状词云功能")
    except Exception as e:
        st.error(f"症状词云加载失败: {str(e)}")
    # ---------- /新版词云 ----------

    cardio_daily = user_data.get('cardio_daily', [])
    if cardio_daily:
        df = pd.DataFrame(cardio_daily)
        df['date'] = pd.to_datetime(df['date'])
        st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">血压热力日历</h3>', unsafe_allow_html=True)
        st.info("血压热力日历功能暂未实现。") # Placeholder for the calendar heatmap
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">身体症状记录</h3>', unsafe_allow_html=True)
    symptom_map = create_body_heatmap()
    body_parts_display = {"head": "头部", "chest": "胸部", "abdomen": "腹部", "left_leg": "腿部"}

    # Ensure the selected key is valid for the selectbox
    current_body_part_key = st.session_state.get('body_part_selector', list(symptom_map.keys())[0])

    selected_part_key = st.selectbox(
        "选择身体部位",
        list(symptom_map.keys()),
        index=list(symptom_map.keys()).index(current_body_part_key) if current_body_part_key in symptom_map else 0,
        format_func=lambda x: body_parts_display.get(x, x),
        key="body_part_selector"
    )

    symptom_input_key = "symptom_input"
    symptom = st.text_input("输入症状", key=symptom_input_key, placeholder="例如：心悸")

    if st.button("记录症状", key="record_symptom_btn"):
        if symptom and selected_part_key:
            if 'symptom_history' not in user_data:
                user_data['symptom_history'] = []

            user_data['symptom_history'].append({
                'symptom': symptom,
                'part': selected_part_key,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'severity': '中等' # Default severity, could be made selectable
            })
            user_manager.update_user_info(st.session_state.user_id, user_data)
            st.success("症状记录成功！")
            st.rerun()
        else:
            st.warning("请选择身体部位并输入症状。")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">今日建议</h3>', unsafe_allow_html=True)
    # Fetch current session state for advice generation
    selected_symptoms = st.session_state.get('selected_symptoms', [])
    severity = st.session_state.get('severity', ["中等"])
    current_sodium_intake = today_data.get('sodium_intake', 0.0) # Default to 0.0 float

    try:
        advice = get_ai_symptom_advice(user_data, selected_symptoms, severity, current_sodium_intake)
        st.markdown(f'<div class="suggestion-box"><span class="text-2xl">💡</span><span>{advice}</span></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"获取建议失败：{str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()