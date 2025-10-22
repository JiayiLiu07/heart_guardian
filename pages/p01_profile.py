# pages/p01_profile.py
import streamlit as st
import pandas as pd
import os
from utils.disease_dict import DISEASE_ENUM
from utils.api import client

USERS_FOLDER = 'users'
os.makedirs(USERS_FOLDER, exist_ok=True)

def save_profile_data(user_id, data):
    pd.DataFrame([data]).to_csv(f"{USERS_FOLDER}/{user_id}_profile.csv", index=False, encoding='utf-8')

def load_profile_data(user_id):
    path = f"{USERS_FOLDER}/{user_id}_profile.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, encoding='utf-8')
        profile = df.iloc[0].to_dict()
        # 安全转换列表字段
        for k in ['cardio_diseases', 'allergens', 'habits']:
            val = profile.get(k)
            if isinstance(val, str):
                try:
                    profile[k] = eval(val)
                except:
                    profile[k] = []
            elif not isinstance(val, list):
                profile[k] = []
        # 过滤无效疾病
        profile['cardio_diseases'] = [k for k in profile.get('cardio_diseases', []) if k in DISEASE_ENUM.__members__]
        return profile
    # 默认值全部 float
    return {
        'cardio_diseases': [], 'allergens': [], 'habits': [],
        'height': 170.0, 'weight': 70.0, 'waist': 80.0,
        'age': 30, 'sleep_hours': 8.0, 'exercise_min': 150
    }

def render():
    # 隐藏左侧栏
    st.markdown("<style>section[data-testid='stSidebar'], .stSidebar, [data-testid='collapsedControl'], #MainMenu, footer {display: none !important;}</style>", unsafe_allow_html=True)

    # 与p00_intro.py统一风格
    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
        padding: 4rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #00e5ff, #2979ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        animation: gradientAnimation 5s ease infinite;
        background-size: 200% 200%;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #2979ff;
        transition: all 0.3s ease;
        cursor: pointer;
        backdrop-filter: blur(10px);
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(41, 121, 255, 0.2);
    }
    .bmi-card {
        background: linear-gradient(135deg, #00e676, #00c853);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hero-section"><h1 class="hero-title">个人健康档案</h1><p class="hero-subtitle">3步完成，AI守护心脏</p></div>', unsafe_allow_html=True)

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.warning("请先登录")
        return

    if 'profile_data' not in st.session_state:
        st.session_state.profile_data = load_profile_data(user_id)
    if 'step' not in st.session_state:
        st.session_state.step = 1

    profile = st.session_state.profile_data

    # 步骤条
    cols = st.columns(3)
    steps = ["基本信息", "健康信息", "AI解读"]
    for i, txt in enumerate(steps):
        cls = "feature-card" if st.session_state.step == i+1 else "feature-card"
        cols[i].markdown(f'<div class="{cls}"><h3>{txt}</h3></div>', unsafe_allow_html=True)

    # === 步骤 1：基本信息 ===
    if st.session_state.step == 1:
        c1, c2 = st.columns(2)
        with c1:
            profile['gender'] = st.selectbox("性别 👤", ["男", "女"], index=0 if profile.get('gender') == '男' else 1)
            profile['age'] = st.number_input("年龄 🎂", min_value=18, max_value=120, value=int(profile.get('age', 30)), step=1)
            profile['height'] = st.number_input("身高 (cm) 📏", min_value=100.0, max_value=250.0, value=float(profile.get('height', 170.0)), step=0.1, format="%.1f")
            profile['weight'] = st.number_input("体重 (kg) ⚖️", min_value=30.0, max_value=200.0, value=float(profile.get('weight', 70.0)), step=0.1, format="%.1f")
        with c2:
            profile['waist'] = st.number_input("腰围 (cm) 🧍", min_value=50.0, max_value=200.0, value=float(profile.get('waist', 80.0)), step=0.1, format="%.1f")
            profile['family_history'] = st.selectbox("家族史 🏠", ["无", "一级亲属", "二级亲属", "不清楚"])

            # BMI 实时计算
            if profile.get('height') and profile.get('weight'):
                bmi = profile['weight'] / ((profile['height'] / 100) ** 2)
                status = "偏瘦 😔" if bmi < 18.5 else "正常 ✅" if bmi < 25 else "超重 ⚠️" if bmi < 30 else "肥胖 ❗"
                color = "#00e676" if "正常" in status else "#ff9800" if "超重" in status else "#f44336"
                st.markdown(f'<div class="bmi-card"><h3>BMI: {bmi:.1f}</h3><p style="color:{color}">{status}</p></div>', unsafe_allow_html=True)

        if st.button("下一步 ➡️", type="primary"):
            st.session_state.step = 2
            st.rerun()

    # === 步骤 2：健康信息 ===
    elif st.session_state.step == 2:
        diseases = [k.name for k in DISEASE_ENUM if k.name != 'none']
        selected = profile.get('cardio_diseases', [])
        cols = st.columns(3)
        for i, k in enumerate(diseases):
            with cols[i % 3]:
                enum_member = DISEASE_ENUM[k]
                label = enum_member.value['label']
                icon = enum_member.value['icon']
                checked = k in selected
                if st.checkbox(f"{icon} {label}", value=checked, key=f"d_{k}"):
                    if k not in selected:
                        selected.append(k)
                else:
                    if k in selected:
                        selected.remove(k)
        profile['cardio_diseases'] = selected

        profile['allergens'] = st.multiselect("过敏食材 🚫", ["豆类", "麸质", "坚果", "海鲜", "其他"], default=profile.get('allergens', []))
        profile['cuisine'] = st.selectbox("菜系偏好 🍲", ["中餐", "西餐", "日韩", "东南亚", "无偏好"], index=["中餐", "西餐", "日韩", "东南亚", "无偏好"].index(profile.get('cuisine', "无偏好")))
        
        habits_options = ["吸烟 🚬", "饮酒 🍷", "熬夜 🌙", "运动不足 🛋️", "高盐饮食 🧂", "家族史阳性 👪"]
        current_habits = [h for h in profile.get('habits', []) if h in [opt.split()[0] for opt in habits_options]]
        profile['habits'] = st.multiselect("症状与习惯 ⚕️", habits_options, default=current_habits)

        profile['sleep_hours'] = st.slider("平均睡眠小时 😴", 4.0, 12.0, float(profile.get('sleep_hours', 8.0)), step=0.5)
        profile['exercise_min'] = st.number_input("每周运动分钟 🏃", min_value=0, max_value=840, value=int(profile.get('exercise_min', 150)), step=30)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("上一步 ⬅️"):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button("完成建档 ✅", type="primary"):
                st.session_state.step = 3
                save_profile_data(user_id, profile)
                st.rerun()

    # === 步骤 3：AI 解读 ===
    else:
        st.success("档案已保存！ 🎉")
        diseases_str = ', '.join([DISEASE_ENUM[k].value['label'] for k in profile.get('cardio_diseases', []) if k in DISEASE_ENUM.__members__]) or '无'
        st.markdown(f"**心血管疾病**: {diseases_str} ❤️")

        with st.expander("AI 解读我的档案 📊", expanded=True):
            if st.button("生成解读报告 🔍"):
                prompt = f"基于用户档案{profile}，分析高危因素，提供预防建议。加入合适emoji，引用《2023 Braunwald’s Heart Disease》。200字通俗语言。"
                with st.spinner("AI 分析中... ⏳"):
                    try:
                        resp = client.chat.completions.create(
                            model="qwen-turbo",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        st.markdown(resp.choices[0].message.content)
                    except Exception as e:
                        st.error(f"AI 错误: {e} ❌")

        if st.button("去健康总览 📈"):
            st.switch_page("pages/01_overview.py")

if __name__ == "__main__":
    render()