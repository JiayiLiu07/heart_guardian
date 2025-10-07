import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import re
import ast  # 用于从 CSV 字符串转换列表

# 用户数据文件夹路径
USERS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "users"))

# 确保用户文件夹存在
os.makedirs(USERS_FOLDER, exist_ok=True)

# 心血管疾病分类表（基于 Braunwald’s Heart Disease 2023、2022 ESC/ACC 指南及 ICD-10）
CARDIO_DISEASES = {
    "无心血管疾病": {"subtypes": [], "heritable": False, "diet_guidelines": "均衡饮食，适量控制热量和钠摄入。"},
    "缺血性心脏病": {
        "subtypes": ["稳定型心绞痛", "急性冠脉综合征（STEMI/NSTEMI）"],
        "heritable": False,
        "diet_guidelines": "低饱和脂肪、低胆固醇、控制热量，增加膳食纤维（如全谷物、蔬菜）。"
    },
    "高血压性心脏病": {
        "subtypes": ["原发性高血压心脏损害", "高血压肾心病"],
        "heritable": False,
        "diet_guidelines": "低钠（<2000 mg/日）、高钾（如香蕉、菠菜）、控制体重。"
    },
    "心律失常": {
        "subtypes": ["房颤", "房扑", "室上速", "室速", "传导阻滞", "长 QT", "Brugada", "短 QT", "CPVT"],
        "heritable": True,
        "diet_guidelines": "适量电解质（钾、镁），避免刺激物（如咖啡因、酒精）。"
    },
    "心力衰竭": {
        "subtypes": ["HFrEF", "HFpEF", "HFmrEF", "右心衰竭"],
        "heritable": False,
        "diet_guidelines": "低钠（<1500 mg/日）、限制液体摄入、适量优质蛋白。"
    },
    "心肌病": {
        "subtypes": ["肥厚型（HCM）", "扩张型（DCM）", "限制型（RCM）", "ARVC", "左室致密化不全"],
        "heritable": True,
        "diet_guidelines": "均衡饮食，适量蛋白，控制热量，避免高脂肪食物。"
    },
    "心脏瓣膜病": {
        "subtypes": ["二尖瓣狭窄", "二尖瓣关闭不全", "主动脉瓣狭窄", "主动脉瓣关闭不全", "三尖瓣疾病", "肺动脉瓣疾病", "二叶式主动脉瓣"],
        "heritable": True,
        "diet_guidelines": "低钠、均衡营养，适量维生素K（如绿叶蔬菜）。"
    },
    "先天性心脏病": {
        "subtypes": ["室间隔缺损", "房间隔缺损", "动脉导管未闭", "法洛四联症", "大动脉转位", "左心发育不良"],
        "heritable": True,
        "diet_guidelines": "均衡饮食，适量热量，注意电解质平衡。"
    },
    "主动脉/大血管疾病": {
        "subtypes": ["胸主动脉瘤", "腹主动脉瘤", "主动脉夹层", "家族性胸主动脉瘤综合征"],
        "heritable": True,
        "diet_guidelines": "低钠、适量抗氧化食物（如水果、蔬菜）。"
    },
    "肺血管疾病": {
        "subtypes": ["肺动脉高压（PAH）", "慢性血栓栓塞性肺高压"],
        "heritable": True,
        "diet_guidelines": "低钠、适量蛋白，控制液体摄入。"
    },
    "心包疾病": {
        "subtypes": ["急性心包炎", "缩窄性心包炎", "心包积液"],
        "heritable": False,
        "diet_guidelines": "均衡饮食，避免高盐高脂食物。"
    },
    "周围动脉疾病": {
        "subtypes": ["下肢动脉硬化闭塞", "急性动脉栓塞", "血栓闭塞性脉管炎"],
        "heritable": False,
        "diet_guidelines": "低胆固醇、低饱和脂肪，增加膳食纤维。"
    },
    "静脉/淋巴疾病": {
        "subtypes": ["深静脉血栓", "静脉曲张", "慢性静脉功能不全"],
        "heritable": False,
        "diet_guidelines": "均衡饮食，适量维生素C和E以支持血管健康。"
    },
    "感染性/免疫性心脏病": {
        "subtypes": ["风湿热", "风湿性瓣膜病", "感染性心内膜炎", "心肌炎"],
        "heritable": False,
        "diet_guidelines": "均衡饮食，增强免疫（如富含维生素C的食物）。"
    },
    "心脏肿瘤": {
        "subtypes": ["黏液瘤", "横纹肌瘤", "纤维瘤"],
        "heritable": True,
        "diet_guidelines": "均衡饮食，适量抗氧化食物。"
    }
}

# --- 辅助函数 ---
def calculate_bmi(weight, height):
    """计算BMI"""
    try:
        weight = float(weight)
        height = float(height)
        if height > 0 and weight > 0:
            return weight / ((height / 100) ** 2)
        return 0
    except (ValueError, TypeError):
        return 0

def get_bmi_category(bmi):
    """获取BMI分类"""
    if bmi == 0:
        return "未知"
    if bmi < 18.5:
        return "体重过轻"
    elif bmi < 24:
        return "正常体重"
    elif bmi < 28:
        return "超重"
    else:
        return "肥胖"

def save_profile_data(profile_data):
    """保存用户档案数据"""
    try:
        user_id = profile_data.get('user_id', 'default_user')
        filename = os.path.join(USERS_FOLDER, f"{user_id}_profile.csv")
        # 处理列表字段保存为字符串
        if isinstance(profile_data.get('diet_habits', []), list):
            profile_data['diet_habits'] = str(profile_data['diet_habits'])
        df = pd.DataFrame([profile_data])
        df.to_csv(filename, index=False, encoding='utf-8')
        return True
    except Exception as e:
        st.error(f"保存数据时出错: {e}")
        return False

def load_profile_data(user_id):
    """加载用户档案数据"""
    try:
        filename = os.path.join(USERS_FOLDER, f"{user_id}_profile.csv")
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            data = df.iloc[0].to_dict()
            # 处理列表字段从字符串转换回列表
            if 'diet_habits' in data and isinstance(data['diet_habits'], str):
                try:
                    data['diet_habits'] = ast.literal_eval(data['diet_habits'])
                except:
                    data['diet_habits'] = []
            return data
        return {}
    except:
        return {}

# --- 主应用逻辑 ---
def main():
    st.set_page_config(
        page_title="个人资料 - CardioGuard AI",
        page_icon="👤",
        layout="centered"
    )

    # 自定义 CSS（调整以移除顶部空白）
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        margin-top: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        text-align: center;
        color: #555;
        margin-bottom: 1rem;
        margin-top: 0;
    }
    .card {
        background: #ffffff;
        border-radius: 12px;
        padding: 10px 20px;  /* 减少顶部 padding */
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        margin-top: 0;  /* 移除顶部 margin */
    }
    .progress-bar {
        height: 8px;
        background: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    .input-container {
        position: relative;
        margin-bottom: 1rem;
    }
    .input-icon {
        position: absolute;
        left: 10px;
        top: 50%;
        transform: translateY(-50%);
        color: #667eea;
        font-size: 1.2rem;
    }
    .stTextInput > div > div > input, .stNumberInput > div > div > input, 
    .stSelectbox > div > div > select, .stMultiselect > div > div > div, 
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1px solid #b0c4de;
        padding: 10px 10px 10px 35px;
        background: #f9f9f9;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus, 
    .stSelectbox > div > div > select:focus, .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px;
        font-size: 1.1rem;
        font-weight: bold;
        width: 100%;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    .stButton > button:disabled {
        background: #cccccc;
        color: #666666;
        cursor: not-allowed;
        box-shadow: none;
    }
    .validation-message {
        color: #ff4b4b;
        font-size: 0.85rem;
        margin-top: 5px;
    }
    .bmi-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .bmi-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .bmi-category {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .nav-card {
        background: #f0f2f6;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .nav-card:hover {
        background: #e0e7ff;
        border-color: #764ba2;
    }
    .success-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # 初始化 session_state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'default_user'
    if 'profile_data' not in st.session_state:
        st.session_state.profile_data = load_profile_data(st.session_state.user_id)

    # 主标题
    st.markdown('<h1 class="main-header">创建您的健康档案</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">请填写以下信息以生成您的个性化健康档案</p>', unsafe_allow_html=True)

    # 进度条
    progress = (st.session_state.current_step - 1) / 3
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress * 100}%"></div>
    </div>
    """, unsafe_allow_html=True)

    # 第一步：基本信息
    if st.session_state.current_step == 1:
        with st.form("profile_form_step1"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 基本信息")

            # 实时跟踪输入
            if 'name' not in st.session_state:
                st.session_state.name = st.session_state.profile_data.get('name', '')
            if 'gender' not in st.session_state:
                st.session_state.gender = st.session_state.profile_data.get('gender', '请选择')
            if 'birth_date' not in st.session_state:
                st.session_state.birth_date = st.session_state.profile_data.get('birth_date', '')
            if 'height' not in st.session_state:
                st.session_state.height = float(st.session_state.profile_data.get('height', 170.0))
            if 'weight' not in st.session_state:
                st.session_state.weight = float(st.session_state.profile_data.get('weight', 70.0))

            st.markdown('<div class="input-container"><span class="input-icon">👤</span>', unsafe_allow_html=True)
            st.session_state.name = st.text_input("姓名 *", value=st.session_state.name, key="name_input")
            if not st.session_state.name.strip():
                st.markdown('<span class="validation-message">请输入姓名</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="input-container"><span class="input-icon">⚥</span>', unsafe_allow_html=True)
            st.session_state.gender = st.selectbox("性别 *", ["请选择", "男", "女"], index=0 if st.session_state.gender == "请选择" else 1 if st.session_state.gender == "男" else 2, key="gender_input")
            if st.session_state.gender == "请选择":
                st.markdown('<span class="validation-message">请选择性别</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="input-container"><span class="input-icon">🎂</span>', unsafe_allow_html=True)
            st.session_state.birth_date = st.text_input("出生日期 *", value=st.session_state.birth_date, placeholder="YYYY-MM-DD", key="birth_date_input")
            if not st.session_state.birth_date or not re.match(r"\d{4}-\d{2}-\d{2}", st.session_state.birth_date):
                st.markdown('<span class="validation-message">请输入有效的出生日期（格式：YYYY-MM-DD）</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="input-container"><span class="input-icon">📏</span>', unsafe_allow_html=True)
                st.session_state.height = st.number_input("身高 (cm) *", min_value=50.0, max_value=250.0, value=st.session_state.height, step=0.1, key="height_input")
                if st.session_state.height <= 0:
                    st.markdown('<span class="validation-message">请输入有效身高</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="input-container"><span class="input-icon">⚖️</span>', unsafe_allow_html=True)
                st.session_state.weight = st.number_input("体重 (kg) *", min_value=20.0, max_value=200.0, value=st.session_state.weight, step=0.1, key="weight_input")
                if st.session_state.weight <= 0:
                    st.markdown('<span class="validation-message">请输入有效体重</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # 计算 BMI
            bmi = calculate_bmi(st.session_state.weight, st.session_state.height)
            bmi_category = get_bmi_category(bmi)
            if bmi > 0:
                st.markdown(f"""
                <div class="bmi-display">
                    <div>BMI 指数</div>
                    <div class="bmi-value">{bmi:.1f}</div>
                    <div class="bmi-category">{bmi_category}</div>
                </div>
                """, unsafe_allow_html=True)

            col_submit, col_next = st.columns([1, 1])
            with col_submit:
                submit_submitted = st.form_submit_button("保存", use_container_width=True)
            with col_next:
                next_submitted = st.form_submit_button("下一步 →", type="primary", use_container_width=True)

            if submit_submitted or next_submitted:
                if not st.session_state.name.strip() or st.session_state.gender == "请选择" or not re.match(r"\d{4}-\d{2}-\d{2}", st.session_state.birth_date) or st.session_state.height <= 0 or st.session_state.weight <= 0:
                    st.error("请填写所有必填的基本信息")
                else:
                    st.session_state.profile_data.update({
                        'name': st.session_state.name,
                        'gender': st.session_state.gender,
                        'birth_date': st.session_state.birth_date,
                        'height': st.session_state.height,
                        'weight': st.session_state.weight,
                        'bmi': bmi,
                        'bmi_category': bmi_category
                    })
                    if submit_submitted:
                        if save_profile_data(st.session_state.profile_data):
                            st.success("基本信息已保存")
                    if next_submitted:
                        st.session_state.current_step = 2
                        st.rerun()

    # 第二步：健康信息
    elif st.session_state.current_step == 2:
        with st.form("profile_form_step2"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 健康信息")

            if 'systolic' not in st.session_state:
                st.session_state.systolic = int(st.session_state.profile_data.get('systolic', 120))
            if 'diastolic' not in st.session_state:
                st.session_state.diastolic = int(st.session_state.profile_data.get('diastolic', 80))
            if 'has_genetic_history' not in st.session_state:
                st.session_state.has_genetic_history = st.session_state.profile_data.get('has_genetic_history', '请选择')
            if 'cardio_disease' not in st.session_state:
                st.session_state.cardio_disease = st.session_state.profile_data.get('cardio_disease', '无心血管疾病')
            if 'cardio_subtype' not in st.session_state:
                st.session_state.cardio_subtype = st.session_state.profile_data.get('cardio_subtype', '不清楚')

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="input-container"><span class="input-icon">🩺</span>', unsafe_allow_html=True)
                st.session_state.systolic = st.number_input("收缩压 (mmHg)", min_value=50, max_value=250, value=st.session_state.systolic, step=1, key="systolic_input")
                if st.session_state.systolic < 50 or st.session_state.systolic > 250:
                    st.markdown('<span class="validation-message">请输入有效收缩压 (50-250)</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="input-container"><span class="input-icon">🩺</span>', unsafe_allow_html=True)
                st.session_state.diastolic = st.number_input("舒张压 (mmHg)", min_value=30, max_value=150, value=st.session_state.diastolic, step=1, key="diastolic_input")
                if st.session_state.diastolic < 30 or st.session_state.diastolic > 150:
                    st.markdown('<span class="validation-message">请输入有效舒张压 (30-150)</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="input-container"><span class="input-icon">🧬</span>', unsafe_allow_html=True)
            st.session_state.has_genetic_history = st.selectbox("是否有家族遗传病史 *", ["请选择", "是", "否"], index=0 if st.session_state.has_genetic_history == "请选择" else 1 if st.session_state.has_genetic_history == "是" else 2, key="genetic_history_input")
            if st.session_state.has_genetic_history == "请选择":
                st.markdown('<span class="validation-message">请选择是否有家族遗传病史</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            disease_options = list(CARDIO_DISEASES.keys())
            st.markdown('<div class="input-container"><span class="input-icon">❤️</span>', unsafe_allow_html=True)
            st.session_state.cardio_disease = st.selectbox("已确认心血管疾病类型（可选）", disease_options, index=disease_options.index(st.session_state.cardio_disease) if st.session_state.cardio_disease in disease_options else 0, key="cardio_disease_input")
            st.markdown('</div>', unsafe_allow_html=True)

            subtypes = CARDIO_DISEASES[st.session_state.cardio_disease]["subtypes"]
            subtype_options = ["不清楚"] + subtypes if subtypes else ["不清楚"]
            st.markdown('<div class="input-container"><span class="input-icon">🩺</span>', unsafe_allow_html=True)
            st.session_state.cardio_subtype = st.selectbox("已确认心血管疾病亚型（可选）", subtype_options, index=subtype_options.index(st.session_state.cardio_subtype) if st.session_state.cardio_subtype in subtype_options else 0, disabled=st.session_state.cardio_disease == "无心血管疾病", key="cardio_subtype_input")
            st.markdown('</div>', unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1], gap="medium")
            with col1:
                prev_submitted = st.form_submit_button("← 上一步", use_container_width=True)
            with col2:
                submit_submitted = st.form_submit_button("保存", use_container_width=True)
            with col2:
                next_submitted = st.form_submit_button("下一步 →", type="primary", use_container_width=True)

            if prev_submitted:
                st.session_state.current_step = 1
                st.rerun()
            if submit_submitted or next_submitted:
                if st.session_state.has_genetic_history == "请选择" or st.session_state.systolic < 50 or st.session_state.systolic > 250 or st.session_state.diastolic < 30 or st.session_state.diastolic > 150:
                    st.error("请填写所有必填的健康信息")
                else:
                    st.session_state.profile_data.update({
                        'systolic': st.session_state.systolic,
                        'diastolic': st.session_state.diastolic,
                        'has_genetic_history': st.session_state.has_genetic_history,
                        'cardio_disease': st.session_state.cardio_disease,
                        'cardio_subtype': st.session_state.cardio_subtype if st.session_state.cardio_disease != "无心血管疾病" else "无"
                    })
                    if submit_submitted:
                        if save_profile_data(st.session_state.profile_data):
                            st.success("健康信息已保存")
                    if next_submitted:
                        st.session_state.current_step = 3
                        st.rerun()

    # 第三步：生活习惯
    elif st.session_state.current_step == 3:
        with st.form("profile_form_step3"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 生活习惯")

            # 初始化生活习惯，修复默认值问题
            if 'diet_habits' not in st.session_state:
                habits = st.session_state.profile_data.get('diet_habits', [])
                if isinstance(habits, str):
                    try:
                        habits = ast.literal_eval(habits)
                    except:
                        habits = ["荤素均衡"]
                elif not isinstance(habits, list):
                    habits = ["荤素均衡"]
                # 过滤无效选项
                valid_options = ["荤素均衡", "偏素", "偏荤", "高盐", "高糖", "低脂"]
                habits = [h for h in habits if h in valid_options]
                st.session_state.diet_habits = habits if habits else ["荤素均衡"]

            if 'exercise_frequency' not in st.session_state:
                st.session_state.exercise_frequency = st.session_state.profile_data.get('exercise_frequency', '请选择')
            if 'smoking' not in st.session_state:
                st.session_state.smoking = st.session_state.profile_data.get('smoking', '请选择')
            if 'alcohol' not in st.session_state:
                st.session_state.alcohol = st.session_state.profile_data.get('alcohol', '请选择')

            st.markdown('<div class="input-container"><span class="input-icon">🍽️</span>', unsafe_allow_html=True)
            st.session_state.diet_habits = st.multiselect("饮食习惯 *", ["荤素均衡", "偏素", "偏荤", "高盐", "高糖", "低脂"], default=st.session_state.diet_habits, key="diet_habits_input")
            if not st.session_state.diet_habits:
                st.markdown('<span class="validation-message">请选择至少一种饮食习惯</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="input-container"><span class="input-icon">🏃</span>', unsafe_allow_html=True)
            st.session_state.exercise_frequency = st.selectbox("运动频率 *", ["请选择", "几乎不运动", "每周1-2次", "每周3-5次", "每天"], index=0 if st.session_state.exercise_frequency == "请选择" else 1 if st.session_state.exercise_frequency == "几乎不运动" else 2 if st.session_state.exercise_frequency == "每周1-2次" else 3 if st.session_state.exercise_frequency == "每周3-5次" else 4, key="exercise_frequency_input")
            if st.session_state.exercise_frequency == "请选择":
                st.markdown('<span class="validation-message">请选择运动频率</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="input-container"><span class="input-icon">🚬</span>', unsafe_allow_html=True)
            st.session_state.smoking = st.selectbox("吸烟情况 *", ["请选择", "不吸烟", "偶尔吸烟", "经常吸烟", "已戒烟"], index=0 if st.session_state.smoking == "请选择" else 1 if st.session_state.smoking == "不吸烟" else 2 if st.session_state.smoking == "偶尔吸烟" else 3 if st.session_state.smoking == "经常吸烟" else 4, key="smoking_input")
            if st.session_state.smoking == "请选择":
                st.markdown('<span class="validation-message">请选择吸烟情况</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="input-container"><span class="input-icon">🍷</span>', unsafe_allow_html=True)
            st.session_state.alcohol = st.selectbox("饮酒情况 *", ["请选择", "不饮酒", "偶尔饮酒", "经常饮酒", "已戒酒"], index=0 if st.session_state.alcohol == "请选择" else 1 if st.session_state.alcohol == "不饮酒" else 2 if st.session_state.alcohol == "偶尔饮酒" else 3 if st.session_state.alcohol == "经常饮酒" else 4, key="alcohol_input")
            if st.session_state.alcohol == "请选择":
                st.markdown('<span class="validation-message">请选择饮酒情况</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1], gap="medium")
            with col1:
                prev_submitted = st.form_submit_button("← 上一步", use_container_width=True)
            with col2:
                is_complete_disabled = st.session_state.exercise_frequency == "请选择" or st.session_state.smoking == "请选择" or st.session_state.alcohol == "请选择" or not st.session_state.diet_habits
                complete_submitted = st.form_submit_button("完成档案 ✅", type="primary", disabled=is_complete_disabled, use_container_width=True)
                submit_submitted = st.form_submit_button("保存", use_container_width=True)

            if prev_submitted:
                st.session_state.current_step = 2
                st.rerun()
            if submit_submitted or complete_submitted:
                if is_complete_disabled:
                    st.error("请填写所有必填的生活习惯信息")
                else:
                    st.session_state.profile_data.update({
                        'diet_habits': st.session_state.diet_habits,
                        'exercise_frequency': st.session_state.exercise_frequency,
                        'smoking': st.session_state.smoking,
                        'alcohol': st.session_state.alcohol,
                        'completion_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'user_id': st.session_state.user_id
                    })
                    if save_profile_data(st.session_state.profile_data):
                        if submit_submitted:
                            st.success("生活习惯信息已保存")
                        if complete_submitted:
                            st.session_state.current_step = 4
                            st.rerun()

    # 第四步：完成
    elif st.session_state.current_step == 4:
        with st.container():
            st.markdown('<div class="success-icon">🎉</div>', unsafe_allow_html=True)
            st.markdown("### 恭喜！您的健康档案已完成")
            st.markdown("现在您可以开始使用 CardioGuard AI 的各项功能了")

            # 档案摘要
            st.markdown("### 您的档案摘要")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="health-metric">
                    <div class="metric-label">基本信息</div>
                    <div class="metric-value">{st.session_state.profile_data.get('name', '')}</div>
                    <div>{st.session_state.profile_data.get('gender', '')} | {st.session_state.profile_data.get('birth_date', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="health-metric">
                    <div class="metric-label">BMI指数</div>
                    <div class="metric-value">{st.session_state.profile_data.get('bmi', 0):.1f}</div>
                    <div>{st.session_state.profile_data.get('bmi_category', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="health-metric">
                    <div class="metric-label">血压</div>
                    <div class="metric-value">{st.session_state.profile_data.get('systolic', 0)}/{st.session_state.profile_data.get('diastolic', 0)} mmHg</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="health-metric">
                    <div class="metric-label">心血管疾病</div>
                    <div class="metric-value">{st.session_state.profile_data.get('cardio_disease', '无心血管疾病')} ({st.session_state.profile_data.get('cardio_subtype', '无')})</div>
                    <div>家族遗传病史: {st.session_state.profile_data.get('has_genetic_history', '未知')}</div>
                </div>
                """, unsafe_allow_html=True)

            # 导航菜单
            st.markdown("### 选择下一步")
            cols = st.columns(3)
            nav_items = [
                ("📊 健康总览", "查看您的健康数据概览", "pages/01_overview.py"),
                ("💊 用药管理", "管理您的药物使用", "pages/03_ai_doctor.py"),
                ("🍎 营养建议", "获取个性化饮食建议", "pages/02_nutrition.py"),
                ("📈 趋势分析", "查看健康数据变化", "pages/01_overview.py"),
                ("🤖 AI医生", "智能健康咨询", "pages/03_ai_doctor.py"),
                ("⚙️ 个人设置", "修改您的档案信息", "pages/p05_me.py")
            ]
            for i, (label, description, page) in enumerate(nav_items):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="nav-card">
                        <h4>{label}</h4>
                        <p>{description}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("进入", key=f"nav_{i}", use_container_width=True):
                        st.switch_page(page)

if __name__ == "__main__":
    main()