import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from openai import OpenAI
import re

# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-e200005b066942eebc8c5426df92a6d5",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

st.set_page_config(page_title="健康总览 · CardioGuard AI", layout="wide")

DATA_FILE = "heart_profile_data.json"
MODEL_PATH = "assets/cv_risk_model.json"
META_PATH = "assets/model_metadata.json"

# 设置matplotlib英文显示
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False

def load_data_from_file():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def load_model():
    """加载XGBoost模型和元数据"""
    if os.path.exists(MODEL_PATH) and os.path.exists(META_PATH):
        try:
            model = xgb.XGBClassifier()
            model.load_model(MODEL_PATH)
            with open(META_PATH, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return model, metadata
        except Exception as e:
            st.warning(f"模型加载失败：{e}")
            return None, None
    return None, None

def prepare_features(profile):
    """将用户档案转换为模型特征向量"""
    bp_sys_map = {
        "-- 请选择 --": 120,
        "未测量": 120,
        "90-119": 105,
        "120-129": 125,
        "130-139": 135,
        "140-159": 150,
        "≥160": 165
    }
    
    bp_dia_map = {
        "-- 请选择 --": 80,
        "未测量": 80,
        "60-79": 70,
        "80-89": 85,
        "90-99": 95,
        "≥100": 105
    }
    
    chol_map = {
        "-- 请选择 --": 4.5,
        "未测量": 4.5,
        "<4.0": 3.5,
        "4.0-5.2": 4.6,
        "5.2-6.2": 5.7,
        ">6.2": 6.8
    }
    
    gluc_map = {
        "-- 请选择 --": 5.0,
        "未测量": 5.0,
        "<5.6": 5.0,
        "5.6-6.9": 6.2,
        "7.0-11.0": 9.0,
        ">11.0": 12.0
    }
    
    age = profile.get('age', 45)
    gender = 1 if profile.get('gender') == '男' else 2
    height = profile.get('height', 170)
    weight = profile.get('weight', 65)
    
    ap_hi = bp_sys_map.get(profile.get('systolic_bp', "-- 请选择 --"), 120)
    ap_lo = bp_dia_map.get(profile.get('diastolic_bp', "-- 请选择 --"), 80)
    
    cholesterol_val = chol_map.get(profile.get('total_cholesterol', "-- 请选择 --"), 4.5)
    gluc_val = gluc_map.get(profile.get('blood_glucose', "-- 请选择 --"), 5.0)
    
    if cholesterol_val < 4.0:
        cholesterol = 1
    elif cholesterol_val <= 5.2:
        cholesterol = 2
    else:
        cholesterol = 3
        
    if gluc_val < 5.6:
        gluc = 1
    elif gluc_val <= 6.9:
        gluc = 2
    else:
        gluc = 3
    
    smoke = 1 if profile.get('smoking', False) else 0
    alco = 1 if profile.get('drinking', False) else 0
    active = 1 if profile.get('ex_freq', 0) >= 3 else 0
    
    bmi = weight / ((height / 100) ** 2)
    age_years = age
    
    features = [age_years, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active, bmi]
    
    derived = {
        'bmi': bmi,
        'age_years': age_years,
        'ap_hi': ap_hi,
        'ap_lo': ap_lo,
        'cholesterol_val': cholesterol_val,
        'gluc_val': gluc_val,
        'cholesterol_grade': cholesterol,
        'gluc_grade': gluc
    }
    
    return features, derived

def get_risk_level(probability):
    """根据概率返回风险等级"""
    if probability < 0.3:
        return "低风险", "#2e7d32"
    elif probability < 0.6:
        return "中风险", "#ed6c02"
    else:
        return "高风险", "#c62828"

def clean_ai_text(text):
    """清理AI生成的文本，移除markdown标记"""
    if not text:
        return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    return text

def highlight_key_points(text):
    """标记关键要点为红色"""
    if not text:
        return text
    key_phrases = [
        "主要风险因素", "关键危险信号", "需要警惕", "立即就医",
        "高血压", "糖尿病", "冠心病", "心力衰竭", "心律失常",
        "动脉粥样硬化", "心肌缺血", "心绞痛", "心肌梗死",
        "遗传因素", "家族史", "并发症", "高危人群",
        "生活方式干预", "药物治疗", "定期复查", "紧急情况"
    ]
    for phrase in key_phrases:
        if phrase in text:
            text = text.replace(phrase, f'<span style="color:#c62828; font-weight:500;">{phrase}</span>')
    return text

def format_ai_text(text, is_lifestyle=False):
    """格式化AI生成的文本，美化显示"""
    if not text:
        return ""
    text = clean_ai_text(text)
    lines = text.split('\n')
    formatted_lines = []
    heading_patterns = [
        r'^第一部分', r'^第二部分', r'^已指定亚型分析', r'^亚型推导',
        r'^🏃', r'^🥗', r'^😴', r'^❤️', r'^⚠️',
        r'^\d+[\.、]',
    ]
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append('<div style="height:0.5rem;"></div>')
            continue
        is_heading = False
        for pattern in heading_patterns:
            if re.match(pattern, line):
                is_heading = True
                break
        if ':' in line and any(disease in line for disease in ['缺血性心脏病', '高血压心脏病', '心律失常', '心肌病', '瓣膜性心脏病', '先天性心脏病', '主动脉疾病', '血管疾病']):
            is_heading = True
        if is_heading:
            if '🏃' in line or '🥗' in line or '😴' in line or '❤️' in line or '⚠️' in line:
                formatted_lines.append(f'<div style="font-size:1.2rem; font-weight:600; color:#1e293b; margin:1.2rem 0 0.8rem 0;">{line}</div>')
            elif '第一部分' in line or '第二部分' in line:
                formatted_lines.append(f'<div style="font-size:1.2rem; font-weight:600; color:#1e293b; margin:1rem 0 0.5rem 0;">{line}</div>')
            elif '已指定亚型分析' in line or '亚型推导' in line:
                formatted_lines.append(f'<div style="font-size:1.1rem; font-weight:600; color:#1e293b; margin:0.8rem 0 0.3rem 0; border-left:3px solid #e2e8f0; padding-left:0.8rem;">{line}</div>')
            elif ':' in line and any(disease in line for disease in ['缺血性心脏病', '高血压心脏病', '心律失常', '心肌病', '瓣膜性心脏病', '先天性心脏病', '主动脉疾病', '血管疾病']):
                formatted_lines.append(f'<div style="font-size:1rem; font-weight:600; color:#1e293b; margin:0.5rem 0 0.2rem 0;">{line}</div>')
            elif re.match(r'^\d+[\.、]', line):
                formatted_lines.append(f'<div style="margin:0.4rem 0 0.4rem 1.5rem; color:#1e293b; font-weight:500;">{line}</div>')
            else:
                formatted_lines.append(f'<div style="margin:0.3rem 0; color:#1e293b;">{line}</div>')
        else:
            line_with_highlights = highlight_key_points(line)
            formatted_lines.append(f'<div style="margin:0.3rem 0; color:#34495e;">{line_with_highlights}</div>')
    return ''.join(formatted_lines)

def generate_ai_subtype_analysis(profile):
    """生成AI亚型推导分析"""
    diseases = profile.get('diseases', [])
    specified_subtypes = []
    unknown_subtypes = []
    for disease in diseases:
        subtype = profile.get(f"subtype_{disease}", "未知")
        if subtype == "未知":
            unknown_subtypes.append(disease)
        else:
            specified_subtypes.append(f"{disease}: {subtype}")
    prompt = f"""你是一位资深心血管专科医生。请根据以下患者数据，对疾病亚型进行专业分析。
患者数据：
- 年龄：{profile.get('age')}岁
- 性别：{profile.get('gender')}
- BMI：{profile.get('weight', 65) / ((profile.get('height', 170)/100) ** 2):.1f}
- 血压：收缩压 {profile.get('systolic_bp', '未测量')}，舒张压 {profile.get('diastolic_bp', '未测量')}
- 已确诊疾病：{', '.join(diseases)}
- 已指定的亚型：{', '.join(specified_subtypes) if specified_subtypes else '无'}
- 需要推导的亚型：{', '.join(unknown_subtypes) if unknown_subtypes else '无'}
- 生活方式：{'吸烟' if profile.get('smoking') else '不吸烟'}，{'饮酒' if profile.get('drinking') else '不饮酒'}，熬夜{profile.get('late_night', 0)}次/周
- 家族史：{profile.get('family_history', '无')}
请提供以下两部分分析：
第一部分：已指定亚型分析
- 对用户已选择的亚型进行解读，解释该亚型的临床意义和注意事项
第二部分：亚型推导（如果有需要推导的疾病）
- 为每个需要推导的疾病分析最可能的亚型
- 结合患者数据说明推导依据
要求：
1. 语气专业严谨，体现医学专业性
2. 每个疾病单独分析，用数字编号
3. 避免使用markdown标记符号
4. 重要的医学结论可以用普通文字表达，不需要特殊标记
请开始分析："""
    try:
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1200
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"AI分析生成失败：{str(e)}"

def generate_ai_lifestyle_advice(profile):
    """生成AI生活方式优化建议"""
    smoking_status = "吸烟" if profile.get('smoking') else "不吸烟"
    drinking_status = "饮酒" if profile.get('drinking') else "不饮酒"
    salt_status = "高盐饮食" if profile.get('high_salt') else "盐摄入适中"
    sugar_status = "高糖饮食" if profile.get('high_sugar') else "糖摄入适中"
    prompt = f"""你是一位资深心血管健康管理专家。请根据以下患者数据，生成一份专业、科学的生活方式优化建议。
患者数据：
- 年龄：{profile.get('age')}岁
- 性别：{profile.get('gender')}
- BMI：{profile.get('weight', 65) / ((profile.get('height', 170)/100) ** 2):.1f}
- 已确诊疾病：{', '.join(profile.get('diseases', ['无']))}
- 生活习惯：
  * {smoking_status}
  * {drinking_status}
  * 熬夜：{profile.get('late_night', 0)}次/周
  * 运动：{profile.get('ex_freq', 0)}次/周，每次{profile.get('ex_dur', 0)}分钟
  * {salt_status}
  * {sugar_status}
  * 压力水平：{profile.get('stress', '中')}
  * 睡眠时间：{profile.get('sleep', 7)}小时/天
- 饮食偏好：{', '.join(profile.get('diet_pref', ['无']))}
- 食物过敏：{', '.join(profile.get('allergies', ['无']))}
请提供以下五个方面的专业建议，每个方面用对应emoji开头：
🏃 运动康复建议
🥗 饮食调整建议
😴 作息优化建议
❤️ 心理健康建议
⚠️ 需要警惕的危险信号
要求：
- 基于循证医学证据
- 建议具体、可执行
- 语气专业、严谨，保持温和关怀
- 避免使用markdown标记符号
- 每个方面3-5条建议，用数字编号
请开始生成："""
    try:
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1500
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"AI建议生成失败：{str(e)}"

# ==========================================
# CSS 样式 - 更新版（已按您的要求优化）
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #2563EB;
        --primary-dark: #1E40AF;
        --primary-light: #DBEAFE;
        --success: #059669;
        --warning: #D97706;
        --danger: #DC2626;
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
    
    /* 导航栏：间距稍微增大（原为2px，现改为8px） */
    .top-navbar {
        background: white;
        padding: 0 2.5rem;
        height: 70px;
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
        color: var(--primary);
        cursor: default; 
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .nav-links { 
        display: flex; 
        gap: 8px;  /* 原为2px，现增大到8px，适中 */
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
        background: var(--primary);
        color: white; 
    }
    
    .hero-box { 
        background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%); 
        padding: 2.5rem 2rem; 
        border-radius: 30px; 
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
    .hero-title { font-size: 2.5rem; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .hero-sub { font-size: 1.1rem; opacity: 0.95; margin-top: 0.5rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--gray-800);
        margin: 2rem 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
    }
    .section-title::after {
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, var(--primary), transparent);
        margin-left: 20px;
    }
    
    .subsection-title-center {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--gray-800);
        margin: 2rem 0 1.5rem 0;
        text-align: center;
        position: relative;
        padding-bottom: 0.8rem;
    }
    .subsection-title-center::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 3px;
        background: var(--primary);
        border-radius: 2px;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: var(--shadow-md);
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        border: 1px solid var(--gray-200);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-light);
    }
    .metric-label { color: var(--gray-600); font-weight: 500; font-size: 0.95rem; margin-bottom: 0.5rem; }
    .metric-value { font-size: 2.5rem; font-weight: 600; color: var(--primary); line-height: 1.2; margin: 0.3rem 0; }
    
    .risk-bar-container {
        width: 100%;
        height: 8px;
        background: var(--gray-200);
        border-radius: 4px;
        margin: 0.5rem 0;
        position: relative;
    }
    .risk-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
    .risk-markers { display: flex; justify-content: space-between; margin-top: 0.3rem; font-size: 0.9rem; color: var(--gray-600); }
    
    .model-explanation {
        margin-top: 0.8rem;
        padding: 0.8rem;
        background: var(--gray-50);
        border-radius: 8px;
        font-size: 1.05rem;
        color: var(--gray-800);
        text-align: left;
        border-left: 4px solid var(--primary);
        line-height: 1.6;
    }
    
    .analysis-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .analysis-card-content { flex: 1; display: flex; flex-direction: column; }
    .analysis-card-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--gray-800);
        margin-bottom: 1rem;
        text-align: center;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--gray-200);
    }
    
    .clinical-metrics-container { display: flex; flex-direction: column; gap: 0.8rem; flex: 1; }
    
    .clinical-metric-row {
        display: flex;
        align-items: center;
        background: white;
        border-radius: 12px;
        padding: 0.6rem;
        border: 1px solid var(--gray-200);
        transition: all 0.2s ease;
    }
    .clinical-metric-row:hover { border-color: var(--primary); background: var(--gray-50); }
    
    .metric-icon-box {
        width: 40px;
        height: 40px;
        background: var(--gray-100);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        margin-right: 0.8rem;
    }
    
    .metric-info { flex: 1; display: flex; flex-direction: column; }
    .metric-name { font-size: 0.85rem; color: var(--gray-600); margin-bottom: 0.2rem; }
    .metric-value-unit { font-size: 1.1rem; font-weight: 600; color: var(--gray-800); }
    
    .metric-status-box { display: flex; flex-direction: column; align-items: flex-end; min-width: 80px; }
    .metric-status-badge { font-size: 0.9rem; font-weight: 500; padding: 0.2rem 0.8rem; border-radius: 20px; text-align: center; }
    .metric-range { font-size: 0.7rem; color: var(--gray-600); margin-top: 0.2rem; }
    
    .info-box {
        background: var(--primary-light);
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary);
    }
    
    .ai-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        margin: 1.5rem 0;
        border: 1px solid var(--gray-200);
    }
    .ai-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; }
    .ai-card-title { font-size: 1.3rem; font-weight: 600; color: var(--gray-800); }
    
    /* ===== 图表解读框 - 高度减小，更紧凑 ===== */
    .chart-interpretation {
        background: linear-gradient(135deg, #f0f7ff 0%, #e6f0fa 100%);
        padding: 0.7rem 1.2rem;          /* 上下内边距从1.2rem减小到0.7rem */
        border-radius: 12px;
        margin-bottom: 1rem;               /* 下边距减小 */
        border: 1px solid #d4e2f0;
        font-size: 0.95rem;                /* 字体稍微调小但保持可读 */
        color: var(--gray-700);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        line-height: 1.5;
    }
    
    .chart-interpretation strong {
        font-size: 1.2rem;                  /* 标题保持醒目 */
        color: var(--primary-dark);
        display: block;
        margin-bottom: 0.3rem;
    }
    
    /* 内部段落边距减小 */
    .chart-interpretation p {
        margin: 0.2rem 0;
    }
    
    .chart-interpretation ul {
        margin: 0.2rem 0 0.2rem 1.2rem;
    }
    
    .chart-interpretation li {
        margin: 0.1rem 0;
    }
    
    /* 雷达图旁边的解读框 - 让Age等不换行，使用flex列表 */
    .chart-interpretation .risk-dimensions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem 1.5rem;
        list-style: none;
        padding-left: 0;
        margin: 0.3rem 0;
    }
    
    .chart-interpretation .risk-dimensions li {
        white-space: nowrap;        /* 强制不换行 */
        margin: 0;
    }
    
    .chart-annotation-content {
        padding: 1.2rem;
        background: white;
        border-radius: 8px;
        line-height: 1.7;
        border: 1px solid var(--gray-200);
        font-family: 'Inter', sans-serif;
        margin-top: 1rem;
    }
    
    .chart-annotation-content h4 { color: var(--primary); margin-top: 0; margin-bottom: 1rem; font-size: 1.2rem; font-weight: 600; }
    .chart-annotation-content p { margin: 0.8rem 0; color: var(--gray-700); }
    .chart-annotation-content ul { margin: 0.5rem 0 1rem 0; padding-left: 1.5rem; }
    .chart-annotation-content li { margin: 0.3rem 0; color: var(--gray-700); }
    
    .term-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.8rem 1.5rem;
        margin: 1rem 0;
        background: var(--gray-50);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--gray-200);
    }
    .term-label { color: var(--primary); font-weight: 600; min-width: 100px; }
    .term-desc { color: var(--gray-600); }
    
    .stButton > button {
        background: white !important;
        color: var(--primary) !important;
        border: 1px solid var(--primary) !important;
        border-radius: 30px !important;
        font-weight: 500 !important;
        padding: 0.4rem 1.2rem !important;
        font-size: 0.9rem !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        background: var(--primary) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md) !important;
    }
    
    .shap-plot-container { max-width: 600px; margin: 0 auto; }
    
    .flex-row { display: flex; gap: 1.5rem; align-items: stretch; }
    .flex-1 { flex: 1; }
    
    @media (max-width: 768px) { .flex-row { flex-direction: column; } }
</style>
""", unsafe_allow_html=True)

def main():
    # 顶部导航栏
    st.markdown("""
    <div class="top-navbar">
        <div class="nav-logo">❤️ CardioGuard AI</div>
        <div class="nav-links">
            <a href="/">🏠 首页</a>
            <a href="/p01_profile">📋 健康档案</a>
            <a href="/p01_overview" class="active">📊 健康总览</a>
            <a href="/p02_nutrition">🥗 营养建议</a>
            <a href="/p03_ai_doctor">🩺 AI 医生</a>
            <a href="/p04_knowledge">📚 知识库</a>
            <a href="/p05_me">👤 我的中心</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero 区域
    st.markdown("""
    <div class="hero-box">
        <h1 class="hero-title">📊 健康总览</h1>
        <p class="hero-sub">基于您的健康数据，AI为您生成全面的健康分析和个性化建议</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    profile = load_data_from_file()
    
    required_fields = ['gender', 'age', 'height', 'weight', 'diseases', 'diet_pref']
    is_complete = all(profile.get(field) for field in required_fields)
    
    if not is_complete or not profile.get('diseases') or not profile.get('diet_pref'):
        st.markdown("""
        <div style="background:#FEF3C7; padding:2rem; border-radius:20px; text-align:center; max-width:600px; margin:2rem auto;">
            <div style="font-size:3rem; margin-bottom:1rem;">⚠️</div>
            <h3 style="margin:0 0 0.5rem 0; color:#92400E;">信息尚未完善</h3>
            <p style="margin:0.5rem 0; color:#92400E;">请先在个人健康档案中填写完整的疾病信息和饮食偏好</p>
            <a href="/p01_profile" style="display:inline-block; margin-top:1rem; padding:0.8rem 2rem; background:#2563EB; color:white; text-decoration:none; border-radius:30px; font-weight:500;">前往完善档案</a>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    features, derived = prepare_features(profile)
    model_feature_names = ['age_years', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 
                          'cholesterol', 'gluc', 'smoke', 'alco', 'active', 'bmi']
    
    # ==================== 第一部分：核心健康指标 ====================
    st.markdown('<div class="section-title">📈 核心健康指标</div>', unsafe_allow_html=True)
    
    bmi = derived['bmi']
    bmi_status = "需关注" if bmi < 18.5 or bmi > 24.9 else "正常"
    bmi_color = '#059669' if bmi_status == "正常" else '#DC2626'
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">身体质量指数 (BMI)</div>
            <div class="metric-value">{bmi:.1f}</div>
            <div style="color: {bmi_color}; font-weight:500;">{bmi_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        disease_count = len(profile.get('diseases', []))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">心血管疾病</div>
            <div class="metric-value">{disease_count}</div>
            <div style="color: var(--primary);">种已记录</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        age = profile.get('age', 45)
        age_status = "需关注" if age > 60 else "正常"
        age_color = '#059669' if age <= 60 else '#DC2626'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">年龄</div>
            <div class="metric-value">{age}岁</div>
            <div style="color: {age_color};">{age_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if derived['ap_hi'] >= 140 or derived['ap_lo'] >= 90:
            bp_status = "偏高"
            bp_color = "#DC2626"
        elif derived['ap_hi'] >= 130 or derived['ap_lo'] >= 80:
            bp_status = "临界"
            bp_color = "#D97706"
        else:
            bp_status = "正常"
            bp_color = "#059669"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">血压</div>
            <div class="metric-value">{derived['ap_hi']:.0f}/{derived['ap_lo']:.0f}</div>
            <div style="color: {bp_color};">{bp_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== 第二部分：个性化风险评估 ====================
    st.markdown('<div class="section-title">🧬 个性化风险评估</div>', unsafe_allow_html=True)
    
    model, metadata = load_model()
    
    if model is not None:
        try:
            feature_df = pd.DataFrame([features], columns=model_feature_names)
            proba = model.predict_proba(feature_df)[0][1]
            risk_level, risk_color = get_risk_level(proba)
            risk_position = proba * 100
            
            left_col, right_col = st.columns(2)
            
            with left_col:
                risk_html = f"""
                <div class="analysis-card">
                    <div class="analysis-card-header">🤖 预测结果</div>
                    <div class="analysis-card-content">
                        <div style="text-align:center;">
                            <div style="color:var(--gray-600); margin-bottom:0.5rem;">10年心血管病风险</div>
                            <div style="font-size:3rem; font-weight:600; color:{risk_color};">{proba:.1%}</div>
                            <div style="margin:1rem 0;">
                                <span style="background:{risk_color}15; color:{risk_color}; padding:6px 28px; border-radius:30px; font-weight:500;">{risk_level}</span>
                            </div>
                            <div style="margin-top:1.5rem;">
                                <div class="risk-bar-container">
                                    <div class="risk-bar-fill" style="width:{risk_position}%; background:{risk_color};"></div>
                                </div>
                                <div class="risk-markers">
                                    <span>低风险</span>
                                    <span>中风险</span>
                                    <span>高风险</span>
                                </div>
                            </div>
                            <div class="model-explanation">
                                <strong>📊 预测模型说明：</strong><br>
                                基于XGBoost机器学习算法，综合考虑12项临床指标，通过分析大规模人群数据训练得出。
                                预测概率表示在相似特征人群中，10年内发生心血管事件的可能性。
                            </div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(risk_html, unsafe_allow_html=True)
            
            with right_col:
                clinical_html = """
                <div class="analysis-card">
                    <div class="analysis-card-header">📊 临床指标评估</div>
                    <div class="clinical-metrics-container">
                """
                st.markdown(clinical_html, unsafe_allow_html=True)
                
                # 血压
                if derived['ap_hi'] >= 140 or derived['ap_lo'] >= 90:
                    bp_status, bp_color, bp_range = "偏高", "#DC2626", "≥140/90"
                elif derived['ap_hi'] >= 130 or derived['ap_lo'] >= 80:
                    bp_status, bp_color, bp_range = "临界", "#D97706", "130-139/80-89"
                else:
                    bp_status, bp_color, bp_range = "正常", "#059669", "<130/80"
                
                st.markdown(f"""
                <div class="clinical-metric-row">
                    <div class="metric-icon-box">❤️</div>
                    <div class="metric-info">
                        <div class="metric-name">血压</div>
                        <div class="metric-value-unit">{derived['ap_hi']:.0f}/{derived['ap_lo']:.0f} mmHg</div>
                    </div>
                    <div class="metric-status-box">
                        <div class="metric-status-badge" style="background:{bp_color}15; color:{bp_color};">{bp_status}</div>
                        <div class="metric-range">正常值 {bp_range}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 胆固醇
                cholesterol_val = derived['cholesterol_val']
                if cholesterol_val > 6.2:
                    chol_status, chol_color, chol_range = "过高", "#DC2626", ">6.2"
                elif cholesterol_val > 5.2:
                    chol_status, chol_color, chol_range = "偏高", "#D97706", "5.2-6.2"
                else:
                    chol_status, chol_color, chol_range = "正常", "#059669", "<5.2"
                
                st.markdown(f"""
                <div class="clinical-metric-row">
                    <div class="metric-icon-box">🧪</div>
                    <div class="metric-info">
                        <div class="metric-name">总胆固醇</div>
                        <div class="metric-value-unit">{cholesterol_val:.1f} mmol/L</div>
                    </div>
                    <div class="metric-status-box">
                        <div class="metric-status-badge" style="background:{chol_color}15; color:{chol_color};">{chol_status}</div>
                        <div class="metric-range">正常值 {chol_range}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 血糖
                gluc_val = derived['gluc_val']
                if gluc_val > 7.0:
                    gluc_status, gluc_color, gluc_range = "过高", "#DC2626", ">7.0"
                elif gluc_val > 6.1:
                    gluc_status, gluc_color, gluc_range = "偏高", "#D97706", "6.1-7.0"
                else:
                    gluc_status, gluc_color, gluc_range = "正常", "#059669", "<6.1"
                
                st.markdown(f"""
                <div class="clinical-metric-row">
                    <div class="metric-icon-box">🍬</div>
                    <div class="metric-info">
                        <div class="metric-name">空腹血糖</div>
                        <div class="metric-value-unit">{gluc_val:.1f} mmol/L</div>
                    </div>
                    <div class="metric-status-box">
                        <div class="metric-status-badge" style="background:{gluc_color}15; color:{gluc_color};">{gluc_status}</div>
                        <div class="metric-range">正常值 {gluc_range}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # BMI
                if bmi >= 28:
                    bmi_status_text, bmi_color, bmi_range = "肥胖", "#DC2626", "≥28"
                elif bmi >= 24:
                    bmi_status_text, bmi_color, bmi_range = "超重", "#D97706", "24-27.9"
                elif bmi < 18.5:
                    bmi_status_text, bmi_color, bmi_range = "偏瘦", "#D97706", "<18.5"
                else:
                    bmi_status_text, bmi_color, bmi_range = "正常", "#059669", "18.5-24"
                
                st.markdown(f"""
                <div class="clinical-metric-row">
                    <div class="metric-icon-box">⚖️</div>
                    <div class="metric-info">
                        <div class="metric-name">BMI</div>
                        <div class="metric-value-unit">{bmi:.1f} kg/m²</div>
                    </div>
                    <div class="metric-status-box">
                        <div class="metric-status-badge" style="background:{bmi_color}15; color:{bmi_color};">{bmi_status_text}</div>
                        <div class="metric-range">正常值 {bmi_range}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div></div>', unsafe_allow_html=True)
            
            # ==================== 新增：高级动态可视化图 (Plotly) ====================
            st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
            
            # 图表1：个人风险雷达图
            st.markdown("""
            <div style="margin-top:2rem;">
                <div class="subsection-title-center">🕸️ 个人风险雷达</div>
            </div>
            """, unsafe_allow_html=True)
            
            radar_labels = ['Age', 'BP', 'Cholesterol', 'Glucose', 'BMI', 'Lifestyle']
            age_norm = min(1.0, derived['age_years'] / 80.0)
            bp_norm = min(1.0, max(0, (derived['ap_hi'] - 90) / 100.0))
            chol_norm = min(1.0, derived['cholesterol_val'] / 8.0)
            gluc_norm = min(1.0, derived['gluc_val'] / 15.0)
            bmi_norm = min(1.0, bmi / 35.0)
            lifestyle_score = (1 if profile.get('smoking') else 0) + (1 if profile.get('drinking') else 0) + (1 if profile.get('ex_freq', 0) < 3 else 0)
            lifestyle_norm = lifestyle_score / 3.0
            
            radar_values = [age_norm, bp_norm, chol_norm, gluc_norm, bmi_norm, lifestyle_norm]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_values + [radar_values[0]],
                theta=radar_labels + [radar_labels[0]],
                fill='toself',
                name='Your Profile',
                line_color='#2563EB',
                fillcolor='rgba(37, 99, 235, 0.25)',
                hovertemplate='<b>%{theta}</b><br>Score: %{r:.2f}<extra></extra>'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=10, color='#4B5563')),
                    angularaxis=dict(tickfont=dict(size=11, weight='bold', color='#1F2937'), direction="clockwise", period=6)
                ),
                showlegend=False,
                height=400,
                margin=dict(t=30, b=30, l=30, r=30),
                title=dict(text='Multidimensional Risk Assessment', x=0.5, font=dict(size=14, weight='bold'))
            )
            
            col_chart1, col_note1 = st.columns([2, 1])
            with col_chart1:
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
            
            with col_note1:
                # 修改：使用flex列表让维度不换行，且整体框更紧凑
                st.markdown("""
                <div class="chart-interpretation" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <strong>📊 图表解读</strong>
                    <p style="margin-top:0.3rem;">雷达图展示了您在六个关键维度的风险分布。图形覆盖面积越大，表示该维度偏离理想健康状态越远。</p>
                    <ul class="risk-dimensions" style="display: flex; flex-wrap: wrap; gap: 0.5rem 1.5rem; list-style: none; padding-left: 0; margin: 0.2rem 0;">
                        <li style="white-space: nowrap;"><strong>Age:</strong> 年龄因素（不可控）</li>
                        <li style="white-space: nowrap;"><strong>BP:</strong> 血压水平</li>
                        <li style="white-space: nowrap;"><strong>Cholesterol:</strong> 胆固醇水平</li>
                        <li style="white-space: nowrap;"><strong>Glucose:</strong> 血糖水平</li>
                        <li style="white-space: nowrap;"><strong>BMI:</strong> 体重指数</li>
                        <li style="white-space: nowrap;"><strong>Lifestyle:</strong> 生活方式风险（吸烟/饮酒/缺乏运动）</li>
                    </ul>
                    <p style="margin:0.2rem 0 0;"><strong>建议：</strong> 重点关注图形突出的顶点，这些是您需要优先干预的领域。</p>
                </div>
                """, unsafe_allow_html=True)

            # 图表2：关键指标趋势模拟
            st.markdown("""
            <div style="margin-top:2rem;">
                <div class="subsection-title-center">📈 关键指标趋势模拟</div>
            </div>
            """, unsafe_allow_html=True)
            
            years = list(range(0, 6))
            risk_no_action = [proba * (1 + 0.05 * y) for y in years]
            risk_with_action = [max(0, proba * (1 - 0.08 * y)) for y in years]
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=years, y=risk_no_action, mode='lines+markers', name='Without Intervention',
                line=dict(color='#DC2626', width=2, dash='dash'), marker=dict(size=8),
                hovertemplate='<b>No Action</b><br>Year: %{x}<br>Risk: %{y:.2%}<extra></extra>'
            ))
            fig_trend.add_trace(go.Scatter(
                x=years, y=risk_with_action, mode='lines+markers', name='With Intervention',
                line=dict(color='#059669', width=3), marker=dict(size=8),
                hovertemplate='<b>With Action</b><br>Year: %{x}<br>Risk: %{y:.2%}<extra></extra>'
            ))
            fig_trend.add_trace(go.Scatter(
                x=years + years[::-1], y=risk_no_action + risk_with_action[::-1],
                fill='toself', fillcolor='rgba(229, 231, 235, 0.6)', line=dict(color='rgba(255,255,255,0)'),
                hoverinfo='skip', showlegend=False, name='Avoidable Risk'
            ))
            
            fig_trend.update_layout(
                xaxis=dict(title='Years', tickmode='linear', tick0=0, dtick=1),
                yaxis=dict(title='Risk Probability', tickformat='.0%'),
                legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)'),
                height=400, margin=dict(t=40, b=40, l=40, r=20),
                title=dict(text='Projected 5-Year Risk Trajectory', x=0.5, font=dict(size=14, weight='bold')),
                hovermode='x unified', plot_bgcolor='rgba(243, 244, 246, 0.5)'
            )
            
            col_chart2, col_note2 = st.columns([2, 1])
            with col_chart2:
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
            
            with col_note2:
                st.markdown("""
                <div class="chart-interpretation" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <strong>📊 图表解读</strong>
                    <p style="margin:0.2rem 0;">此图模拟了未来5年内您的心血管风险变化趋势。</p>
                    <ul style="margin:0.2rem 0; padding-left:1.2rem;">
                        <li><span style="color:#DC2626;">🔴 红色虚线</span>：若不改变现有生活习惯，风险可能随年龄增长而上升。</li>
                        <li><span style="color:#059669;">🟢 绿色实线</span>：若采取积极干预措施，风险可显著降低。</li>
                    </ul>
                    <p style="margin:0.2rem 0 0;"><strong>启示：</strong> 早期干预对长期预后至关重要，阴影区域代表通过努力可避免的风险增量。</p>
                </div>
                """, unsafe_allow_html=True)

            # ==================== 第三部分：SHAP模型解释 ====================
            st.markdown('<div class="section-title">🌍 人群大数据洞察</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div style="margin-top:1rem;">
                <div class="subsection-title-center">🔍 风险因素分析</div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(feature_df)
                display_feature_names = ['Age', 'Gender', 'Height', 'Weight', 'Systolic BP', 'Diastolic BP', 
                                        'Cholesterol', 'Glucose', 'Smoking', 'Alcohol', 'Active', 'BMI']
                
                # SHAP解读框 - 更紧凑
                st.markdown("""
                <div class="chart-interpretation" style="margin-bottom:1rem;">
                    <strong>📊 图表解读</strong>
                    <p style="margin:0.2rem 0;">红色箭头表示增加风险的因素，蓝色箭头表示降低风险的因素。箭头越长，影响越大。基准值表示人群平均风险，最终值是您的个人风险。</p>
                </div>
                """, unsafe_allow_html=True)
                
                fig1, ax1 = plt.subplots(figsize=(7, 3.5))
                plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
                plt.rcParams['axes.unicode_minus'] = False
                
                shap.waterfall_plot(
                    shap.Explanation(values=shap_values[0], base_values=explainer.expected_value, data=features, feature_names=display_feature_names),
                    show=False, max_display=12
                )
                plt.title("Factors Affecting Your Cardiovascular Risk", fontsize=10, fontweight='bold', pad=10)
                plt.tight_layout()
                
                st.markdown('<div class="shap-plot-container">', unsafe_allow_html=True)
                st.pyplot(fig1)
                st.markdown('</div>', unsafe_allow_html=True)
                plt.close()
                
                # 特征重要性图表
                if metadata and 'feature_importances' in metadata:
                    st.markdown("""
                    <div style="margin-top:2rem;">
                        <div class="subsection-title-center">⭐ 特征重要性排名</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 特征重要性解读框 - 紧凑
                    st.markdown("""
                    <div class="chart-interpretation" style="margin-bottom:1rem;">
                        <strong>📊 图表解读</strong>
                        <p style="margin:0.2rem 0;">基于大规模人群数据分析，展示各因素对心血管疾病预测的总体重要性。条形越长，该特征在模型中的权重越大。</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    importances = metadata['feature_importances']
                    importance_dict = {}
                    for eng_name, chn_name in zip(model_feature_names, display_feature_names):
                        if eng_name in importances:
                            importance_dict[chn_name] = importances[eng_name]
                    
                    imp_df = pd.DataFrame({
                        'Feature': list(importance_dict.keys()),
                        'Importance': list(importance_dict.values())
                    }).sort_values('Importance', ascending=True)
                    
                    fig2, ax2 = plt.subplots(figsize=(7, 3.5))
                    colors = ['#2563EB' for _ in range(len(imp_df))]
                    bars = ax2.barh(imp_df['Feature'], imp_df['Importance'], color=colors)
                    ax2.set_xlabel('Importance Score', fontsize=9)
                    ax2.set_title('Global Feature Importance', fontsize=10, fontweight='bold', pad=10)
                    ax2.tick_params(axis='both', which='major', labelsize=8)
                    
                    for bar in bars:
                        width = bar.get_width()
                        ax2.text(width + 0.01, bar.get_y() + bar.get_height()/2, f'{width:.3f}', ha='left', va='center', fontsize=7)
                    
                    plt.tight_layout()
                    st.pyplot(fig2)
                    plt.close()
                
            except Exception as e:
                st.warning(f"SHAP分析生成失败：{e}")
                
        except Exception as e:
            st.error(f"模型预测失败：{e}")
    else:
        st.info("💡 提示：运行 train.py 训练模型后，可查看AI风险预测分析")
    
    # ==================== 第四部分：AI疾病亚型分析 ====================
    if profile.get('diseases'):
        st.markdown('<div class="section-title">🧬 疾病亚型分析</div>', unsafe_allow_html=True)
        
        unknown_subtypes = [d for d in profile.get('diseases', []) if profile.get(f"subtype_{d}") == "未知"]
        
        col_text, col_button = st.columns([5, 1])
        with col_text:
            if unknown_subtypes:
                st.markdown(f"""
                <div class="info-box">
                    🔍 检测到 <strong>{len(unknown_subtypes)}</strong> 种疾病亚型未指定，AI正在为您推导最可能的亚型
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-box">
                    ✅ 所有疾病亚型已明确，AI为您解读已指定亚型的临床意义
                </div>
                """, unsafe_allow_html=True)
        
        with col_button:
            if st.button("🔄 重新生成", key="regenerate_subtype", use_container_width=True):
                if 'subtype_analysis' in st.session_state:
                    del st.session_state.subtype_analysis
                st.rerun()
        
        with st.spinner("🧠 AI正在分析您的疾病数据..."):
            if 'subtype_analysis' not in st.session_state:
                st.session_state.subtype_analysis = generate_ai_subtype_analysis(profile)
            
            if st.session_state.subtype_analysis:
                formatted_text = format_ai_text(st.session_state.subtype_analysis, is_lifestyle=False)
                st.markdown(f"""
                <div class="ai-card">
                    <div class="ai-card-header">
                        <div class="ai-card-title">📋 AI亚型分析报告</div>
                    </div>
                    <div style="line-height:1.7;">
                        {formatted_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ==================== 第五部分：AI生活方式优化建议 ====================
    st.markdown('<div class="section-title">💪 生活方式优化建议</div>', unsafe_allow_html=True)
    
    col_text, col_button = st.columns([5, 1])
    with col_text:
        st.markdown("""
        <div class="info-box">
            🤖 基于您的健康档案，AI为您生成了专属的生活方式优化建议
        </div>
        """, unsafe_allow_html=True)
    
    with col_button:
        if st.button("🔄 重新生成", key="regenerate_lifestyle", use_container_width=True):
            if 'lifestyle_advice' in st.session_state:
                del st.session_state.lifestyle_advice
            st.rerun()
    
    if 'lifestyle_advice' not in st.session_state:
        with st.spinner("🧠 AI正在为您定制生活方式优化方案..."):
            st.session_state.lifestyle_advice = generate_ai_lifestyle_advice(profile)
    
    if st.session_state.lifestyle_advice:
        formatted_advice = format_ai_text(st.session_state.lifestyle_advice, is_lifestyle=True)
        st.markdown(f"""
        <div class="ai-card">
            <div class="ai-card-header">
                <div class="ai-card-title">📋 健康改善计划</div>
            </div>
            <div style="line-height:1.7;">
                {formatted_advice}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 免责声明
    st.markdown("---")
    st.markdown("""
    <div style="background:white; padding:1rem; border-radius:12px; text-align:center; border:1px solid #E5E7EB;">
        <p style="color:#6B7280; margin:0; font-size:0.9rem;">
            ⚠️ 重要提示：以上分析基于AI模型推导，仅供健康管理参考，不能替代专业医疗诊断
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()