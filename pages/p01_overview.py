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

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-e200005b066942eebc8c5426df92a6d5",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

st.set_page_config(page_title="健康总览 · CardioGuard AI", page_icon="📊" ,layout="wide")

DATA_FILE = "heart_profile_data.json"
MODEL_PATH = "assets/cv_risk_model.json"
META_PATH = "assets/model_metadata.json"

# 设置 matplotlib 英文显示
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
    """加载 XGBoost 模型和元数据"""
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
    """清理 AI 生成的文本，移除 markdown 标记"""
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
    """格式化 AI 生成的文本，美化显示"""
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
            formatted_lines.append('<div style="height:0.3rem;"></div>')
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
                formatted_lines.append(f'<div style="font-size:1.1rem; font-weight:600; color:#1e293b; margin:1rem 0 0.5rem 0;">{line}</div>')
            elif '第一部分' in line or '第二部分' in line:
                formatted_lines.append(f'<div style="font-size:1.1rem; font-weight:600; color:#1e293b; margin:0.8rem 0 0.3rem 0;">{line}</div>')
            elif '已指定亚型分析' in line or '亚型推导' in line:
                formatted_lines.append(f'<div style="font-size:1rem; font-weight:600; color:#1e293b; margin:0.6rem 0 0.2rem 0; border-left:3px solid #e2e8f0; padding-left:0.6rem;">{line}</div>')
            elif ':' in line and any(disease in line for disease in ['缺血性心脏病', '高血压心脏病', '心律失常', '心肌病', '瓣膜性心脏病', '先天性心脏病', '主动脉疾病', '血管疾病']):
                formatted_lines.append(f'<div style="font-size:0.95rem; font-weight:600; color:#1e293b; margin:0.4rem 0 0.1rem 0;">{line}</div>')
            elif re.match(r'^\d+[\.、]', line):
                formatted_lines.append(f'<div style="margin:0.3rem 0 0.3rem 1.2rem; color:#1e293b; font-weight:500;">{line}</div>')
            else:
                formatted_lines.append(f'<div style="margin:0.2rem 0; color:#1e293b;">{line}</div>')
        else:
            line_with_highlights = highlight_key_points(line)
            formatted_lines.append(f'<div style="margin:0.2rem 0; color:#34495e;">{line_with_highlights}</div>')
    return ''.join(formatted_lines)

def generate_ai_subtype_analysis(profile):
    """生成 AI 亚型推导分析"""
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
3. 避免使用 markdown 标记符号
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
        return f"AI 分析生成失败：{str(e)}"

def generate_ai_lifestyle_advice(profile):
    """生成 AI 生活方式优化建议"""
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
请提供以下五个方面的专业建议，每个方面用对应 emoji 开头：
🏃 运动康复建议
🥗 饮食调整建议
😴 作息优化建议
❤️ 心理健康建议
⚠️ 需要警惕的危险信号
要求：
- 基于循证医学证据
- 建议具体、可执行
- 语气专业、严谨，保持温和关怀
- 避免使用 markdown 标记符号
- 每个方面 3-5 条建议，用数字编号
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
        return f"AI 建议生成失败：{str(e)}"

# ==========================================
# CSS 样式 - 已同步 nutrition.py 的导航栏样式
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
        --shadow-hover: 0 10px 20px -5px rgba(37, 99, 235, 0.15);
    }
    
    .stApp {
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        background-color: #f8fafc;
    }
    
    /* 隐藏左侧默认侧边栏 */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    .block-container { 
        padding: 0 2rem 1rem !important; 
        max-width: 1400px; 
        margin: 0 auto; 
    }
    
    /* 隐藏默认菜单和页脚 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* 【关键修改】导航栏 - 完全同步 nutrition.py 参数 */
    .top-navbar {
        background: white;
        padding: 0 1.5rem;           /* 同步：1.5rem */
        height: 75px;                /* 同步：75px */
        box-shadow: var(--shadow-sm);
        display: flex;
        justify-content: space-between;
        align-items: center;         /* 同步：居中 */
        position: relative; 
        z-index: 9999;
        border-bottom: 1px solid var(--gray-200);
        
        margin-top: 50px;            /* 同步：50px，紧贴默认头部 */
        margin-bottom: 0rem;
        border-radius: 0 0 8px 8px;
    }
    
    .nav-logo { 
        font-weight: 700; 
        font-size: 1.8rem;           /* 同步：1.8rem */
        color: var(--primary);
        cursor: default; 
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .nav-links { 
        display: flex; 
        gap: 10px;                   /* 同步：10px */
    }
    .nav-links a { 
        text-decoration: none; 
        color: var(--gray-600); 
        font-weight: 500; 
        padding: 8px 18px;           /* 同步：8px 18px */
        border-radius: 20px; 
        transition: all 0.3s; 
        font-size: 1.1rem;           /* 同步：调整为 1.1rem */
    }
    .nav-links a:hover { 
        background-color: var(--primary-light);
        color: var(--primary); 
    }
    .nav-links a.active { 
        background: var(--primary);
        color: white; 
    }
    
    /* Hero 区域 - 更紧凑 */
    .hero-box { 
        background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%); 
        padding: 1.8rem 1.5rem; 
        border-radius: 24px; 
        text-align: center; 
        color: white; 
        margin: 0.5rem 0 1rem 0; 
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
    .hero-title { font-size: 2.2rem; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .hero-sub { font-size: 1rem; opacity: 0.95; margin-top: 0.3rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    
    /* 各部分标题 */
    .section-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--gray-800);
        margin: 1.2rem 0 0.8rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
        position: relative;
    }
    .section-title::after {
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, var(--primary), transparent);
        margin-left: 15px;
    }
    
    .subsection-title-center {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--gray-800);
        margin: 1.2rem 0 0.8rem 0;
        text-align: center;
        position: relative;
        padding-bottom: 0.5rem;
    }
    .subsection-title-center::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 50px;
        height: 3px;
        background: var(--primary);
        border-radius: 2px;
    }
    
    /* 指标卡片 - 添加悬浮效果 */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: var(--shadow-md);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        border: 1px solid var(--gray-200);
        cursor: default;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-hover);
        border-color: var(--primary-light);
    }
    .metric-label { color: var(--gray-600); font-weight: 500; font-size: 0.85rem; margin-bottom: 0.3rem; }
    .metric-value { font-size: 2rem; font-weight: 600; color: var(--primary); line-height: 1.2; margin: 0.2rem 0; }
    
    .risk-bar-container {
        width: 100%;
        height: 6px;
        background: var(--gray-200);
        border-radius: 3px;
        margin: 0.3rem 0;
        position: relative;
    }
    .risk-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
    .risk-markers { display: flex; justify-content: space-between; margin-top: 0.2rem; font-size: 0.8rem; color: var(--gray-600); }
    
    .model-explanation {
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: var(--gray-50);
        border-radius: 6px;
        font-size: 0.9rem;
        color: var(--gray-800);
        text-align: left;
        border-left: 3px solid var(--primary);
        line-height: 1.4;
    }
    
    /* 分析卡片 - 添加悬浮效果 */
    .analysis-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
        height: 100%;
        display: flex;
        flex-direction: column;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .analysis-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-hover);
        border-color: var(--primary-light);
    }
    
    .analysis-card-content { flex: 1; display: flex; flex-direction: column; }
    .analysis-card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--gray-800);
        margin-bottom: 0.5rem;
        text-align: center;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid var(--gray-200);
    }
    
    .clinical-metrics-container { display: flex; flex-direction: column; gap: 0.5rem; flex: 1; }
    
    .clinical-metric-row {
        display: flex;
        align-items: center;
        background: white;
        border-radius: 10px;
        padding: 0.4rem;
        border: 1px solid var(--gray-200);
        transition: all 0.2s ease;
    }
    .clinical-metric-row:hover { border-color: var(--primary); background: var(--gray-50); }
    
    .metric-icon-box {
        width: 32px;
        height: 32px;
        background: var(--gray-100);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        margin-right: 0.5rem;
    }
    
    .metric-info { flex: 1; display: flex; flex-direction: column; }
    .metric-name { font-size: 0.75rem; color: var(--gray-600); margin-bottom: 0.1rem; }
    .metric-value-unit { font-size: 0.95rem; font-weight: 600; color: var(--gray-800); }
    
    .metric-status-box { display: flex; flex-direction: column; align-items: flex-end; min-width: 70px; }
    .metric-status-badge { font-size: 0.8rem; font-weight: 500; padding: 0.15rem 0.6rem; border-radius: 16px; text-align: center; }
    .metric-range { font-size: 0.65rem; color: var(--gray-600); margin-top: 0.1rem; }
    
    .info-box {
        background: var(--primary-light);
        padding: 0.5rem 0.8rem;
        border-radius: 6px;
        border-left: 3px solid var(--primary);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .ai-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: var(--shadow-md);
        margin: 0.8rem 0;
        border: 1px solid var(--gray-200);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .ai-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-hover);
        border-color: var(--primary-light);
    }
    .ai-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; }
    .ai-card-title { font-size: 1.1rem; font-weight: 600; color: var(--gray-800); }
    
    /* 图表解读框 - 优化版 (添加悬浮效果) */
    .chart-interpretation {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        border: 1px solid #e2e8f0;
        font-size: 0.9rem;
        color: #334155;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        line-height: 1.6;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .chart-interpretation:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
        border-color: #bfdbfe;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    }
    
    .chart-interpretation strong {
        font-size: 1.05rem;
        color: #1e293b;
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .chart-interpretation p {
        margin: 0.4rem 0;
    }
    
    .chart-interpretation ul {
        margin: 0.4rem 0 0.4rem 1.2rem;
        padding-left: 0.5rem;
    }
    
    .chart-interpretation li {
        margin: 0.25rem 0;
    }
    
    .chart-interpretation .insight-box {
        background: #eff6ff;
        border-left: 3px solid #2563eb;
        padding: 0.6rem 0.8rem;
        border-radius: 6px;
        margin-top: 0.6rem;
        font-size: 0.85rem;
    }
    
    .chart-interpretation .insight-box strong {
        color: #1e40af;
        margin-bottom: 0.2rem;
    }
    .chart-interpretation .reference-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 0.6rem;
        font-size: 0.8rem;
    }
    
    .chart-interpretation .reference-table th,
    .chart-interpretation .reference-table td {
        border: 1px solid #cbd5e1;
        padding: 0.3rem 0.5rem;
        text-align: left;
    }
    
    .chart-interpretation .reference-table th {
        background-color: #f1f5f9;
        font-weight: 600;
        color: #475569;
    }
    
    .chart-interpretation .reference-table tr:nth-child(even) {
        background-color: #f8fafc;
    }
    
    .chart-interpretation .risk-dimensions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.3rem 1rem;
        list-style: none;
        padding-left: 0;
        margin: 0.2rem 0;
    }
    
    .chart-interpretation .risk-dimensions li {
        white-space: nowrap;
        margin: 0;
    }
    
    .shap-plot-container { max-width: 500px; margin: 0 auto; }
    
    .flex-row { display: flex; gap: 1rem; align-items: stretch; }
    .flex-1 { flex: 1; }
    
    @media (max-width: 768px) { .flex-row { flex-direction: column; } }
    
    /* 按钮 */
    .stButton > button {
        background: white !important;
        color: var(--primary) !important;
        border: 1px solid var(--primary) !important;
        border-radius: 30px !important;
        font-weight: 500 !important;
        padding: 0.3rem 1rem !important;
        font-size: 0.8rem !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        background: var(--primary) !important;
        color: white !important;
        transform: translateY(-1px);
        box-shadow: var(--shadow-md) !important;
    }
    
    /* 调整列间距 */
    .row-widget.stHorizontal {
        gap: 0.8rem !important;
    }
    
    /* Plotly 图表容器 */
    .js-plotly-plot .plotly {
        margin: 0 !important;
    }
    /* 【修改重点】底部安全/声明徽章 - 同步 me.py 风格 (白灰渐变) */
    .security-badge {
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%); /* 白灰渐变背景 */
        padding: 1.2rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #e5e7eb; /* 中性灰色边框 */
        margin-top: 2rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .security-badge p {
        color: #374151;
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .security-badge strong {
        font-weight: 700;
    }
    .security-badge .warning-icon {
        font-size: 1.2rem;
        margin-right: 6px;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # 顶部导航栏 - 已同步 nutrition.py 结构
    st.markdown("""
    <div class="top-navbar">
        <div class="nav-logo">❤️ CardioGuard AI</div>
        <div class="nav-links">
             <a href="/p00_home">🏠 首页</a>
            <a href="/p01_profile">📋 健康档案</a>
            <a href="/p01_overview" class="active">📊 健康总览</a>
            <a href="/p02_nutrition">🥗 营养建议</a>
            <a href="/p03_ai_doctor">🩺 AI 医生</a>
            <a href="/p04_knowledge">📚 知识库</a>
            <a href="/p05_me">👤 我的中心</a>
        </div>
    </div>
    
    <!-- Hero 区域 -->
    <div class="hero-box">
        <h1 class="hero-title">📊 健康总览</h1>
        <p class="hero-sub">基于您的健康数据，AI 为您生成全面的健康分析和个性化建议</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    profile = load_data_from_file()
    
    required_fields = ['gender', 'age', 'height', 'weight', 'diseases', 'diet_pref']
    is_complete = all(profile.get(field) for field in required_fields)
    
    if not is_complete or not profile.get('diseases') or not profile.get('diet_pref'):
        st.markdown("""
        <div style="background:#FEF3C7; padding:1.5rem; border-radius:16px; text-align:center; max-width:500px; margin:1rem auto;">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">⚠️</div>
            <h3 style="margin:0 0 0.3rem 0; color:#92400E;">信息尚未完善</h3>
            <p style="margin:0.3rem 0; color:#92400E;">请先在个人健康档案中填写完整的疾病信息和饮食偏好</p>
            <a href="/p01_profile" style="display:inline-block; margin-top:0.8rem; padding:0.6rem 1.5rem; background:#2563EB; color:white; text-decoration:none; border-radius:30px; font-weight:500;">前往完善档案</a>
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
            <div style="color: {bmi_color}; font-weight:500; font-size:0.9rem;">{bmi_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        disease_count = len(profile.get('diseases', []))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">心血管疾病</div>
            <div class="metric-value">{disease_count}</div>
            <div style="color: var(--primary); font-size:0.9rem;">种已记录</div>
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
            <div style="color: {age_color}; font-size:0.9rem;">{age_status}</div>
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
            <div style="color: {bp_color}; font-size:0.9rem;">{bp_status}</div>
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
                            <div style="color:var(--gray-600); margin-bottom:0.3rem; font-size:0.9rem;">10 年心血管病风险</div>
                            <div style="font-size:2.5rem; font-weight:600; color:{risk_color};">{proba:.1%}</div>
                            <div style="margin:0.5rem 0;">
                                <span style="background:{risk_color}15; color:{risk_color}; padding:4px 24px; border-radius:30px; font-weight:500; font-size:0.9rem;">{risk_level}</span>
                            </div>
                            <div style="margin-top:0.8rem;">
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
                                基于 XGBoost 机器学习算法，综合考虑 12 项临床指标，通过分析大规模人群数据训练得出。
                                预测概率表示在相似特征人群中，10 年内发生心血管事件的可能性。
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
            
            # ==================== 高级动态可视化图 (Plotly) ====================
            st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
            
            # 图表 1：个人风险雷达图
            st.markdown("""
            <div style="margin-top:1rem;">
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
                    radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9, color='#4B5563')),
                    angularaxis=dict(tickfont=dict(size=10, weight='bold', color='#1F2937'), direction="clockwise", period=6)
                ),
                showlegend=False,
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                title=dict(text='Multidimensional Risk Assessment', x=0.5, font=dict(size=12, weight='bold'))
            )
            
            col_chart1, col_note1 = st.columns([2, 1])
            with col_chart1:
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
            
            with col_note1:
                st.markdown("""
                <div class="chart-interpretation" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <strong>📊 图表解读</strong>
                    <p style="margin-top:0.2rem;">雷达图展示了您在六个关键维度的风险分布。图形覆盖面积越大，表示该维度偏离理想健康状态越远。</p>
                    <ul class="risk-dimensions" style="display: flex; flex-wrap: wrap; gap: 0.3rem 1rem; list-style: none; padding-left: 0; margin: 0.2rem 0;">
                        <li style="white-space: nowrap;"><strong>Age:</strong> 年龄因素</li>
                        <li style="white-space: nowrap;"><strong>BP:</strong> 血压水平</li>
                        <li style="white-space: nowrap;"><strong>Cholesterol:</strong> 胆固醇</li>
                        <li style="white-space: nowrap;"><strong>Glucose:</strong> 血糖水平</li>
                        <li style="white-space: nowrap;"><strong>BMI:</strong> 体重指数</li>
                        <li style="white-space: nowrap;"><strong>Lifestyle:</strong> 生活方式风险</li>
                    </ul>
                    <p style="margin:0.1rem 0 0;"><strong>建议：</strong> 重点关注图形突出的顶点。</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 图表 2：关键指标趋势模拟
            st.markdown("""
            <div style="margin-top:1rem;">
                <div class="subsection-title-center">📈 关键指标趋势模拟</div>
            </div>
            """, unsafe_allow_html=True)
            
            years = list(range(0, 6))
            risk_no_action = [proba * (1 + 0.05 * y) for y in years]
            risk_with_action = [max(0, proba * (1 - 0.08 * y)) for y in years]
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=years, y=risk_no_action, mode='lines+markers', name='Without Intervention',
                line=dict(color='#DC2626', width=2, dash='dash'), marker=dict(size=6),
                hovertemplate='<b>No Action</b><br>Year: %{x}<br>Risk: %{y:.2%}<extra></extra>'
            ))
            fig_trend.add_trace(go.Scatter(
                x=years, y=risk_with_action, mode='lines+markers', name='With Intervention',
                line=dict(color='#059669', width=2.5), marker=dict(size=6),
                hovertemplate='<b>With Action</b><br>Year: %{x}<br>Risk: %{y:.2%}<extra></extra>'
            ))
            fig_trend.add_trace(go.Scatter(
                x=years + years[::-1], y=risk_no_action + risk_with_action[::-1],
                fill='toself', fillcolor='rgba(229, 231, 235, 0.6)', line=dict(color='rgba(255,255,255,0)'),
                hoverinfo='skip', showlegend=False, name='Avoidable Risk'
            ))
            
            fig_trend.update_layout(
                xaxis=dict(title='Years', tickmode='linear', tick0=0, dtick=1, title_font=dict(size=10)),
                yaxis=dict(title='Risk Probability', tickformat='.0%', title_font=dict(size=10)),
                legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)', font=dict(size=9)),
                height=350,
                margin=dict(t=30, b=30, l=40, r=20),
                title=dict(text='Projected 5-Year Risk Trajectory', x=0.5, font=dict(size=12, weight='bold')),
                hovermode='x unified', plot_bgcolor='rgba(243, 244, 246, 0.5)'
            )
            
            col_chart2, col_note2 = st.columns([2, 1])
            with col_chart2:
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
            
            with col_note2:
                st.markdown("""
                <div class="chart-interpretation" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <strong>📊 图表解读</strong>
                    <p style="margin:0.1rem 0;">此图模拟了未来 5 年内您的心血管风险变化趋势。</p>
                    <ul style="margin:0.1rem 0; padding-left:1rem;">
                        <li><span style="color:#DC2626;">🔴 红色虚线</span>：若不改变现有生活习惯</li>
                        <li><span style="color:#059669;">🟢 绿色实线</span>：若采取积极干预措施</li>
                    </ul>
                    <p style="margin:0.1rem 0 0;"><strong>启示：</strong> 早期干预至关重要。</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ==================== 第三部分：SHAP 模型解释 ====================
            st.markdown('<div class="section-title">🌍 人群大数据洞察</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div style="margin-top:0.5rem;">
                <div class="subsection-title-center">🔍 风险因素分析</div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(feature_df)
                display_feature_names = ['Age', 'Gender', 'Height', 'Weight', 'Systolic BP', 'Diastolic BP', 
                                        'Cholesterol', 'Glucose', 'Smoking', 'Alcohol', 'Active', 'BMI']
                
                # SHAP 解读框 - 优化版
                st.markdown("""
                <div class="chart-interpretation">
                    <strong>📊 图表一：个人风险因素分解 (SHAP 瀑布图)</strong>
                    <p>此图揭示了<strong>您个人</strong>的健康数据如何影响最终的风险预测结果。它展示了每个指标相对于“平均人”是增加还是降低了您的风险。</p>
                    <ul>
                        <li><span style="color:#DC2626;">🔴 红色条形</span>：该指标使您的风险<strong>高于</strong>基准（推高风险）。例如，较高的血压或年龄。</li>
                        <li><span style="color:#2563EB;">🔵 蓝色条形</span>：该指标使您的风险<strong>低于</strong>基准（降低风险）。例如，良好的生活习惯或正常的血糖。</li>
                        <li><strong>条形长度</strong>：代表影响的大小。条形越长，该因素对最终风险的贡献（无论正向或负向）就越大。</li>
                        <li><strong>Base Value</strong>：人群的平均风险基线。所有红蓝条形的效应从此基线开始累加。</li>
                        <li><strong>f(x)</strong>：您的最终预测风险值。它等于基线值加上所有个人因素的贡献之和。</li>
                    </ul>
                    <div class="insight-box">
                        <strong>💡 核心发现与建议</strong>
                        <p>请重点关注图中<strong>最长的红色条形</strong>，这些是您个人最主要的风险驱动因素。优先改善这些因素（如通过饮食、运动或遵医嘱服药）能最有效地降低您的整体风险。</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 【修改点】缩小 SHAP 图尺寸
                fig1, ax1 = plt.subplots(figsize=(3, 0.5))
                plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
                plt.rcParams['axes.unicode_minus'] = False
                
                # 1. 先正常生成 SHAP 瀑布图
                shap.waterfall_plot(
                    shap.Explanation(values=shap_values[0], base_values=explainer.expected_value, data=features, feature_names=display_feature_names),
                    show=False, max_display=12
                )
                
                # 2. 【关键步骤】获取当前坐标轴
                ax = plt.gca()
                
                # 3. 遍历图中所有的条形容器 (BarContainer)
                for container in ax.containers:
                    bars = container.get_children()
                    for bar in bars:
                        if hasattr(bar, 'set_height'):
                            bar.set_height(0.3) 
                            
                # 4. 设置标题和字体
                plt.title("Factors Affecting Your Cardiovascular Risk", fontsize=8, fontweight='bold', pad=5)
                ax.tick_params(labelsize=7) 
                plt.tight_layout()
                st.markdown('<div class="shap-plot-container">', unsafe_allow_html=True)
                st.pyplot(fig1)
                st.markdown('</div>', unsafe_allow_html=True)
                plt.close()
                
                # 特征重要性图表
                if metadata and 'feature_importances' in metadata:
                    st.markdown("""
                    <div style="margin-top:1.5rem;">
                        <div class="subsection-title-center">⭐ 特征重要性排名</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 特征重要性解读框 - 优化版
                    st.markdown("""
                    <div class="chart-interpretation">
                        <strong>📊 图表二：全局特征重要性排名</strong>
                        <p>此图反映了在<strong>整体人群</strong>中，哪些健康指标对于预测心血管疾病最为关键。它是模型从大量数据中学习到的普遍规律。</p>
                        <ul>
                            <li><strong>横轴数值 (重要性得分)</strong>：范围从 0 到 1，分数越高，表示该指标在模型做出预测时的整体影响力越大。</li>
                            <li><strong>排名意义</strong>：排名靠前的因素（如年龄、血压）通常是心血管疾病的公认主要风险因子。</li>
                            <li><strong>与上图的区别</strong>：上图（SHAP）展示的是<strong>您个人</strong>的特殊情况；而本图展示的是<strong>大众群体</strong>的普遍规律。即使某个因素在全局很重要，但在您个人身上可能影响不大（反之亦然）。</li>
                        </ul>
                        <div class="insight-box">
                            <strong>💡 核心发现</strong>
                            <p>通常情况下，<strong>年龄、血压、胆固醇</strong>是人群中最关键的风险预测因子。了解这些有助于我们关注普遍的健康原则。</p>
                        </div>
                        <table class="reference-table">
                            <thead>
                                <tr>
                                    <th>指标</th>
                                    <th>理想参考范围</th>
                                    <th>风险提示</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>收缩压 (Systolic BP)</td><td>&lt; 120 mmHg</td><td>≥140 mmHg 为高血压</td></tr>
                                <tr><td>舒张压 (Diastolic BP)</td><td>&lt; 80 mmHg</td><td>≥90 mmHg 为高血压</td></tr>
                                <tr><td>总胆固醇 (Cholesterol)</td><td>&lt; 5.2 mmol/L</td><td>&gt;6.2 mmol/L 为过高</td></tr>
                                <tr><td>空腹血糖 (Glucose)</td><td>&lt; 6.1 mmol/L</td><td>≥7.0 mmol/L 提示糖尿病</td></tr>
                                <tr><td>BMI</td><td>18.5 - 24 kg/m²</td><td>≥28 kg/m² 为肥胖</td></tr>
                            </tbody>
                        </table>
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
                    
                    # 同样缩小特征重要性图的尺寸以匹配
                    fig2, ax2 = plt.subplots(figsize=(5, 2.2))
                    colors = ['#2563EB' for _ in range(len(imp_df))]
                    bars = ax2.barh(imp_df['Feature'], imp_df['Importance'], color=colors)
                    ax2.set_xlabel('Importance Score', fontsize=8)
                    ax2.set_title('Global Feature Importance', fontsize=8, fontweight='bold', pad=5)
                    ax2.tick_params(axis='both', which='major', labelsize=7)
                    
                    for bar in bars:
                        width = bar.get_width()
                        ax2.text(width + 0.01, bar.get_y() + bar.get_height()/2, f'{width:.3f}', ha='left', va='center', fontsize=6)
                    
                    plt.tight_layout()
                    st.pyplot(fig2)
                    plt.close()
                
            except Exception as e:
                st.warning(f"SHAP 分析生成失败：{e}")
                
        except Exception as e:
            st.error(f"模型预测失败：{e}")
    else:
        st.info("💡 提示：运行 train.py 训练模型后，可查看 AI 风险预测分析")
    
    # ==================== 第四部分：AI 疾病亚型分析 ====================
    if profile.get('diseases'):
        st.markdown('<div class="section-title">🧬 疾病亚型分析</div>', unsafe_allow_html=True)
        
        unknown_subtypes = [d for d in profile.get('diseases', []) if profile.get(f"subtype_{d}") == "未知"]
        
        col_text, col_button = st.columns([5, 1])
        with col_text:
            if unknown_subtypes:
                st.markdown(f"""
                <div class="info-box">
                    🔍 检测到 <strong>{len(unknown_subtypes)}</strong> 种疾病亚型未指定，AI 正在为您推导最可能的亚型
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-box">
                    ✅ 所有疾病亚型已明确，AI 为您解读已指定亚型的临床意义
                </div>
                """, unsafe_allow_html=True)
        
        with col_button:
            if st.button("🔄 重新生成", key="regenerate_subtype", use_container_width=True):
                if 'subtype_analysis' in st.session_state:
                    del st.session_state.subtype_analysis
                st.rerun()
        
        with st.spinner("🧠 AI 正在分析您的疾病数据..."):
            if 'subtype_analysis' not in st.session_state:
                st.session_state.subtype_analysis = generate_ai_subtype_analysis(profile)
            
            if st.session_state.subtype_analysis:
                formatted_text = format_ai_text(st.session_state.subtype_analysis, is_lifestyle=False)
                st.markdown(f"""
                <div class="ai-card">
                    <div class="ai-card-header">
                        <div class="ai-card-title">📋 AI 亚型分析报告</div>
                    </div>
                    <div style="line-height:1.5;">
                        {formatted_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ==================== 第五部分：AI 生活方式优化建议 ====================
    st.markdown('<div class="section-title">💪 生活方式优化建议</div>', unsafe_allow_html=True)
    
    col_text, col_button = st.columns([5, 1])
    with col_text:
        st.markdown("""
        <div class="info-box">
            🤖 基于您的健康档案，AI 为您生成了专属的生活方式优化建议
        </div>
        """, unsafe_allow_html=True)
    
    with col_button:
        if st.button("🔄 重新生成", key="regenerate_lifestyle", use_container_width=True):
            if 'lifestyle_advice' in st.session_state:
                del st.session_state.lifestyle_advice
            st.rerun()
    
    if 'lifestyle_advice' not in st.session_state:
        with st.spinner("🧠 AI 正在为您定制生活方式优化方案..."):
            st.session_state.lifestyle_advice = generate_ai_lifestyle_advice(profile)
    
    if st.session_state.lifestyle_advice:
        formatted_advice = format_ai_text(st.session_state.lifestyle_advice, is_lifestyle=True)
        st.markdown(f"""
        <div class="ai-card">
            <div class="ai-card-header">
                <div class="ai-card-title">📋 健康改善计划</div>
            </div>
            <div style="line-height:1.5;">
                {formatted_advice}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 【修改重点】免责声明 - 同步 me.py 风格 (白灰渐变) 并修改文案颜色
    st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div class="security-badge">
        <p>
            <span class="warning-icon">⚠️</span>
            <strong style="color: #2563EB;">CardioGuard AI</strong> <strong style="color: #1F2937;">强调</strong>以上分析基于 AI 模型推导，仅供健康管理参考，不能替代专业医疗诊断。
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()