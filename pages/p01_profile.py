# pages/p01_profile.py
import streamlit as st
import re
import json
import os
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    api_key="sk-e200005b066942eebc8c5426df92a6d5",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

st.set_page_config(page_title="健康档案 · CardioGuard AI", 
                   page_icon="📋" ,
                   layout="wide")


USERS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "users"))
DATA_FILE = os.path.join(USERS_FOLDER, "heart_profile_data.json")
USER_DATA_FILE = os.path.join(USERS_FOLDER, "user_data.json")

def save_data_to_file(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"保存数据失败：{e}")

def load_data_from_file():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# ==========================================
# CSS 样式 - 全新设计：疾病大类框住亚型选择
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #10B981;
        --primary-dark: #047857;
        --primary-light: #D1FAE5;
        --gray-50: #F9FAFB;
        --gray-100: #F3F4F6;
        --gray-200: #E5E7EB;
        --gray-600: #4B5563;
        --gray-800: #1F2937;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        
        /* 亚型卡片新配色 */
        --card-border: #E5E7EB;
        --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        --hint-bg: #F3E8FF;
        --hint-border: #D8B4FE;
        --hint-text: #6D28D9;
        --confirm-bg: #E8F5E9;
        --confirm-border: #A5D6A7;
        --confirm-text: #1B5E20;
        --select-bg: #FFFFFF;
    }
    
    .stApp {
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        background-color: #f8fafc;
        font-size: 16px;
    }
    
    .main > div { padding-top: 0 !important; }
    .block-container { padding: 0 2rem 1rem !important; max-width: 1400px; margin: 0 auto; }
    
    /* 隐藏默认元素 */
    #MainMenu, footer, section[data-testid="stSidebar"] { display: none !important; }
    
    /* ========== 导航栏 ========== */
    .top-navbar {
        background: white;
        padding: 0 1.5rem;
        height: 75px;
        box-shadow: var(--shadow-sm);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative; 
        z-index: 9999;
        border-bottom: 1px solid var(--gray-200);
        margin-top: 50px;
        margin-bottom: 0rem;
        border-radius: 0 0 8px 8px;
    }
    
    .nav-logo { 
        font-weight: 700; 
        font-size: 1.8rem;
        color: var(--primary);
        cursor: default; 
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .nav-links { 
        display: flex; 
        gap: 10px;
    }
    .nav-links a { 
        text-decoration: none; 
        color: var(--gray-600); 
        font-weight: 500; 
        padding: 8px 18px;
        border-radius: 20px; 
        transition: all 0.3s; 
        font-size: 1.1rem;
    }
    .nav-links a:hover { 
        background-color: var(--primary-light);
        color: var(--primary); 
    }
    .nav-links a.active { 
        background: var(--primary);
        color: white; 
    }
    
    /* ========== Hero 区域 ========== */
    .hero-box { 
        background: linear-gradient(135deg, #10B981 0%, #047857 100%); 
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
    .hero-sub { font-size: 1.1rem; opacity: 0.95; margin-top: 0.3rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    
    /* ========== 大标题样式 ========== */
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--gray-800);
        margin: 1.0rem 0 0.6rem 0;
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
    
    .subsection-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--gray-800);
        margin: 0.8rem 0 0.4rem 0;
        padding-left: 0.6rem;
        border-left: 4px solid var(--primary);
    }
    
    /* ========== 进度条 ========== */
    .progress-container { 
        margin: 0 0 1.5rem 0 !important;
        background: white; 
        padding: 1.2rem 1.5rem; 
        border-radius: 16px; 
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
    }
    .progress-text { display: flex; justify-content: space-between; font-size: 1rem; color: var(--gray-600); margin-bottom: 8px; font-weight: 500; }
    .progress-bar-bg { background: var(--gray-200); height: 10px; border-radius: 5px; overflow: hidden; }
    .progress-bar-fill { background: var(--primary); height: 100%; border-radius: 5px; transition: width 0.8s ease; }
    
    /* ========== 表单标签 ========== */
    .field-label { 
        font-size: 1.1rem;
        font-weight: 600; 
        display: flex; 
        align-items: center; 
        margin-bottom: 0.6rem;
        color: var(--gray-800); 
    }
    .field-label.required {
        color: var(--primary) !important;
    }
    .field-label .field-icon { margin-right: 8px; color: var(--primary); font-size: 1.2rem; }
    
    /* ========== 高级 BMI 卡片 ========== */
    .bmi-premium {
        background: linear-gradient(145deg, #ffffff 0%, #f9fdfc 100%);
        border-radius: 20px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 4px 15px -5px rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 1rem 0 1.5rem 0;
        transition: all 0.3s ease;
    }
    .bmi-premium-left { display: flex; flex-direction: column; }
    .bmi-premium-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        color: var(--primary-dark);
        background: var(--primary-light);
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        margin-bottom: 0.5rem;
        align-self: flex-start;
    }
    .bmi-premium-value {
        font-size: 2.8rem;
        font-weight: 800;
        color: var(--primary);
        line-height: 1;
        margin-bottom: 0.2rem;
    }
    .bmi-premium-status-badge.normal { background: #D1FAE5; color: #065F46; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 1rem; font-weight: 600; display: inline-block; }
    .bmi-premium-status-badge.underweight { background: #FEF3C7; color: #92400E; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 1rem; font-weight: 600; display: inline-block; }
    .bmi-premium-status-badge.overweight { background: #FEE2E2; color: #991B1B; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 1rem; font-weight: 600; display: inline-block; }
    
    /* ========== 【全新设计】疾病大类卡片 ========== */
    .disease-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 1.8rem;
        margin: 1.5rem 0;
    }
    
    .disease-card {
        background: white;
        border-radius: 24px;
        border: 2px solid var(--card-border);
        box-shadow: var(--card-shadow);
        overflow: hidden;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .disease-card:hover {
        box-shadow: 0 12px 28px rgba(16, 185, 129, 0.15);
        transform: translateY(-3px);
        border-color: var(--primary);
    }
    
    /* 疾病大类头部 - 醒目设计 */
    .disease-header {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        padding: 1.2rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 3px solid var(--primary-dark);
        position: relative;
    }
    
    .disease-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, white, transparent);
    }
    
    .disease-icon {
        width: 52px;
        height: 52px;
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(4px);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.5);
    }
    
    .disease-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        flex: 1;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        letter-spacing: 0.5px;
    }
    
    /* 亚型选择区域 - 被疾病大类框住 */
    .subtype-section {
        padding: 1.5rem;
        background: white;
        border-top: 1px solid var(--gray-100);
    }
    
    .subtype-label {
        font-size: 1rem;
        font-weight: 600;
        color: var(--gray-600);
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .subtype-label span {
        background: var(--gray-100);
        padding: 0.2rem 0.8rem;
        border-radius: 30px;
        font-size: 0.85rem;
        color: var(--gray-600);
    }
    
    /* 自定义 Selectbox 样式 - 与卡片完美融合 */
    .subtype-section .stSelectbox {
        margin: 0 0 1rem 0 !important;
    }
    
    .subtype-section .stSelectbox > div {
        margin: 0 !important;
    }
    
    .subtype-section .stSelectbox > div > div {
        background: var(--gray-50) !important;
        border: 2px solid var(--gray-200) !important;
        border-radius: 16px !important;
        padding: 0.5rem 1rem !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        min-height: 56px !important;
    }
    
    .subtype-section .stSelectbox > div > div:hover {
        border-color: var(--primary) !important;
        background: white !important;
    }
    
    .subtype-section .stSelectbox > div > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1) !important;
    }
    
    /* 状态提示区域 - 在卡片内部 */
    .subtype-status {
        border-radius: 16px;
        padding: 1rem 1.2rem;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-top: 0.5rem;
    }
    
    /* 未确认状态 */
    .subtype-status.hint {
        background: var(--hint-bg);
        color: var(--hint-text);
        border: 2px solid var(--hint-border);
        animation: softGlow 2s infinite;
    }
    
    @keyframes softGlow {
        0% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.2); }
        50% { box-shadow: 0 0 0 8px rgba(139, 92, 246, 0); }
        100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0); }
    }
    
    /* 已确认状态 */
    .subtype-status.confirmed {
        background: var(--confirm-bg);
        color: var(--confirm-text);
        border: 2px solid var(--confirm-border);
    }
    
    .subtype-status-icon {
        font-size: 1.5rem;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .subtype-status-text {
        flex: 1;
    }
    
    .subtype-status-subtext {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* 已选中的亚型标签 */
    .selected-subtype-badge {
        background: rgba(76, 175, 80, 0.2);
        padding: 0.4rem 1rem;
        border-radius: 30px;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--confirm-text);
        border: 1px solid var(--confirm-border);
    }
    
    /* ========== 组合按钮 ========== */
    .combo-buttons {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
        margin: 0.5rem 0 1rem 0;
    }
    
    .combo-buttons .stButton > button {
        padding: 0.5rem 0.6rem !important;
        font-size: 0.95rem !important;
        min-height: 48px !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-weight: 600 !important;
        border-radius: 16px !important;
        background: white !important;
        border: 2px solid var(--gray-200) !important;
        color: var(--gray-800) !important;
    }
    
    .combo-buttons .stButton > button:hover {
        border-color: var(--primary) !important;
        background: var(--primary-light) !important;
        color: var(--primary-dark) !important;
    }

    /* ========== AI 报告卡片 ========== */
    .ai-report {
        background: white;
        border-radius: 24px;
        padding: 2rem;
        box-shadow: var(--shadow-lg);
        margin: 2rem 0;
        border: 1px solid var(--gray-200);
    }
    
    .ai-report-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid var(--primary-light);
        position: relative;
    }
    
    .ai-report-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 100px;
        height: 3px;
        background: var(--primary);
        border-radius: 3px;
    }
    
    .ai-report-icon {
        width: 64px;
        height: 64px;
        background: var(--primary-light);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: var(--primary-dark);
    }
    
    .ai-report-title-wrapper {
        flex: 1;
    }
    
    .ai-report-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--gray-800);
        line-height: 1.2;
        margin-bottom: 0.2rem;
    }
    
    .ai-report-subtitle {
        color: var(--gray-600);
        font-size: 1rem;
    }
    
    .ai-report-badge {
        background: var(--primary-light);
        color: var(--primary-dark);
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        font-size: 0.9rem;
        font-weight: 600;
        border: 1px solid var(--primary);
    }
    
    .analysis-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .analysis-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .analysis-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary);
    }
    
    .analysis-card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid var(--primary-light);
    }
    
    .analysis-card-icon {
        width: 40px;
        height: 40px;
        background: var(--primary-light);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        color: var(--primary-dark);
    }
    
    .analysis-card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--gray-800);
        flex: 1;
    }
    
    .analysis-card-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .analysis-item {
        background: var(--gray-50);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid var(--primary);
        font-size: 1rem;
        color: var(--gray-700);
        line-height: 1.6;
    }
    
    .analysis-item strong {
        color: var(--primary-dark);
        display: block;
        margin-bottom: 0.3rem;
        font-size: 1.05rem;
    }
    
    .prevent-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .prevent-item {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        background: var(--gray-50);
        padding: 1rem 1.2rem;
        border-radius: 16px;
        border: 1px solid var(--gray-200);
        transition: all 0.2s;
    }
    
    .prevent-item:hover {
        border-color: var(--primary);
        background: white;
        transform: translateX(5px);
    }
    
    .prevent-check {
        width: 28px;
        height: 28px;
        background: var(--primary);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        flex-shrink: 0;
        font-weight: bold;
    }
    
    .prevent-text {
        color: var(--gray-700);
        line-height: 1.5;
        font-size: 1rem;
        flex: 1;
    }
    
    .logic-flow, .analysis-flow {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .logic-step, .analysis-step {
        background: var(--gray-50);
        padding: 1.2rem 1.2rem 1.2rem 3rem;
        border-radius: 16px;
        border: 1px solid var(--gray-200);
        position: relative;
        color: var(--gray-700);
        line-height: 1.6;
        font-size: 1rem;
        transition: all 0.2s;
    }
    
    .logic-step:hover, .analysis-step:hover {
        border-color: var(--primary);
        background: white;
        transform: translateX(5px);
    }
    
    .logic-step::before {
        content: '→';
        position: absolute;
        left: 1.2rem;
        top: 1.2rem;
        color: var(--primary);
        font-weight: bold;
        font-size: 1.2rem;
    }
    .analysis-step::before {
        content: '🔍';
        position: absolute;
        left: 1rem;
        top: 1.2rem;
        font-size: 1.2rem;
    }
    
    .diet-details {
        background: white;
        border-radius: 20px;
        border: 1px solid var(--gray-200);
        margin: 1.5rem 0;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    
    .diet-details summary {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary);
        padding: 1.2rem 1.5rem;
        cursor: pointer;
        background: var(--gray-50);
        list-style: none;
        transition: background 0.2s;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .diet-details summary:hover {
        background: var(--primary-light);
    }
    
    .diet-details summary::-webkit-details-marker { display: none; }
    
    .diet-details[open] summary {
        border-bottom: 1px solid var(--gray-200);
    }
    
    .diet-guide {
        padding: 1.5rem;
        background: white;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .diet-guide::-webkit-scrollbar {
        width: 6px;
    }
    
    .diet-guide::-webkit-scrollbar-track {
        background: var(--gray-100);
        border-radius: 3px;
    }
    
    .diet-guide::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 3px;
    }
    
    .diet-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    
    .diet-item {
        background: var(--gray-50);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--gray-200);
    }
    
    .diet-name {
        font-size: 1rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .diet-desc {
        font-size: 0.95rem;
        color: var(--gray-600);
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    .diet-suit {
        font-size: 0.85rem;
        color: var(--primary-dark);
        background: var(--primary-light);
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 500;
    }
    
    /* 按钮样式 */
    .stButton > button {
        border-radius: 30px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s !important;
        min-height: 48px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    div.stButton > button:first-child {
        background: white !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
    }
    div.stButton > button:first-child:hover {
        background: var(--primary-light) !important;
        color: var(--primary-dark) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md) !important;
    }
    
    .stButton > button[kind="primary"],
    .stButton > button[type="primary"] {
        background: #059669 !important;
        color: white !important;
        border: 2px solid #059669 !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[type="primary"]:hover {
        background: #047857 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3) !important;
    }
    
    .info-box {
        background: var(--primary-light);
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border-left: 4px solid var(--primary);
        margin: 0.8rem 0;
        color: var(--primary-dark);
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    .warning-box {
        background: #FEF3C7;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #F59E0B;
        color: #92400E;
        font-size: 1rem;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .disclaimer {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid var(--gray-200);
        color: var(--gray-600);
        font-size: 0.95rem;
        margin: 2rem 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid var(--gray-200);
    }
    
    .stSelectbox {
        width: 100%;
    }
    
    .stSelectbox > div {
        width: 100%;
    }
    
    .stSelectbox > div > div {
        width: 100%;
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

def clean_ai_text(text):
    if not text: return ""
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'```\w*\n?', '', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'_+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def generate_structured_prompt(profile):
    diseases_text = ",".join(profile.get('diseases', [])) if profile.get('diseases') else "无"
    
    known_subtypes = []
    unknown_subtypes = []
    for d in profile.get('diseases', []):
        subtype = profile.get(f"subtype_{d}", "未知")
        if subtype == "未知":
            unknown_subtypes.append(f"{d}")
        else:
            known_subtypes.append(f"{d}: {subtype}")
    
    known_text = ",".join(known_subtypes) if known_subtypes else "无"
    unknown_text = ",".join(unknown_subtypes) if unknown_subtypes else "无"
    
    return f"""你是一位资深心血管专科医生，请基于以下患者数据生成一份专业的健康分析报告。
【患者数据】
- 基本信息：{profile.get('gender', '未知')}，{profile.get('age', '未知')}岁，身高{profile.get('height', '未知')}cm，体重{profile.get('weight', '未知')}kg
- 血压：收缩压{profile.get('systolic_bp', '未知')} mmHg，舒张压{profile.get('diastolic_bp', '未知')} mmHg
- 血脂：总胆固醇{profile.get('total_cholesterol', '未知')} mmol/L
- 血糖：空腹血糖{profile.get('blood_glucose', '未知')} mmol/L
- 家族史：{profile.get('family_history', '无')}
- 疾病史：{diseases_text}
- 已确认亚型：{known_text}
- 未确认亚型：{unknown_text}
- 生活方式：吸烟{'是' if profile.get('smoking') else '否'}，每周熬夜{profile.get('late_night', 0)}次
- 其他：运动{profile.get('ex_freq', 0)}次/周，每次{profile.get('ex_dur', 0)}分钟，压力水平{profile.get('stress', '中')}
【输出要求】
你必须且只能输出一个有效的 JSON 对象，不要包含任何其他文字、Markdown、HTML 标签或代码块。
【JSON 结构】
{{
    "analysis": [
        "重点结论 1：对疾病状态的核心分析，约 30-50 字",
        "重点结论 2：对风险因素的核心分析，约 30-50 字",
        "重点结论 3：对预后的核心分析，约 30-50 字"
    ],
    "prevent": [
        "建议 1：针对具体情况的可行建议，约 20-30 字",
        "建议 2：针对具体情况的可行建议，约 20-30 字",
        "建议 3：针对具体情况的可行建议，约 20-30 字",
        "建议 4：针对具体情况的可行建议，约 20-30 字"
    ],
    "subtype": [
        "对于已确认亚型：分析该亚型的病理特点、常见诱因、潜在并发症风险",
        "对于未确认亚型：基于患者数据推导最可能的亚型，并说明依据",
        "根据疾病数量，可包含多条分析，每条 30-50 字"
    ]
}}
请严格只输出 JSON：
"""

def parse_ai_json_response(ai_text):
    if not ai_text or ai_text.startswith("Error"): return None, None, None
    
    clean_text = re.sub(r'```json\s*', '', ai_text)
    clean_text = re.sub(r'```\s*', '', clean_text)
    clean_text = clean_text.strip()
    
    json_match = re.search(r'(\{[\s\S]*\})', clean_text)
    if json_match:
        clean_text = json_match.group(1).strip()
    
    try:
        data = json.loads(clean_text)
        analysis = [clean_ai_text(item) for item in data.get('analysis', [])]
        prevent = [clean_ai_text(item) for item in data.get('prevent', [])]
        subtype = [clean_ai_text(item) for item in data.get('subtype', [])]
        return analysis, prevent, subtype
    except json.JSONDecodeError:
        try:
            clean_text = clean_text.replace("'", '"')
            clean_text = re.sub(r'([{,])\s*([a-zA-Z_]+)\s*:', r'\1"\2":', clean_text)
            data = json.loads(clean_text)
            analysis = [clean_ai_text(item) for item in data.get('analysis', [])]
            prevent = [clean_ai_text(item) for item in data.get('prevent', [])]
            subtype = [clean_ai_text(item) for item in data.get('subtype', [])]
            return analysis, prevent, subtype
        except:
            st.warning("AI 返回格式有误，请重试")
            return None, None, None

def main():
    # 顶部导航栏
    st.markdown("""
    <div class="top-navbar">
        <div class="nav-logo">❤️ CardioGuard AI</div>
        <div class="nav-links">
             <a href="/p00_home">🏠 首页</a>
            <a href="/p01_profile" class="active">📋 健康档案</a>
            <a href="/p01_overview">📊 健康总览</a>
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
        <h1 class="hero-title">📋 个人健康档案</h1>
        <p class="hero-sub">精准数据驱动 · AI 智能推导 · 专属心血管风险管理</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('is_logged_in', False) or st.session_state.get('username'):
        username = st.session_state.get('username', st.session_state.get('user_id', '用户'))
        st.markdown(f"""
        <div style="background: #e8f5e9; padding: 12px 20px; border-radius: 12px; border-left: 6px solid #2e7d32; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2rem;">👤</span>
                <span style="font-weight: 600; color: #2e7d32;">当前登录用户：{username}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if 'step' not in st.session_state: st.session_state.step = 1
    if 'profile' not in st.session_state: 
        saved_data = load_data_from_file()
        st.session_state.profile = saved_data if saved_data else {}
    
    profile = st.session_state.profile
    if isinstance(profile.get('diseases'), (set, tuple)): profile['diseases'] = list(profile['diseases'])
    if 'diseases' not in profile: profile['diseases'] = []
    
    defaults = {
        'gender': '男', 'age': 45, 'height': 170, 'weight': 65.0,
        'family_history': '无', 'late_night': 2, 'smoking': False,
        'drinking': False, 'high_salt': False, 'high_sugar': False,
        'ex_freq': 3, 'ex_dur': 45, 'stress': '中', 'sleep': 7.0,
        'allergies': [], 'diet_pref': []
    }
    for k, v in defaults.items():
        if k not in profile: profile[k] = v
    
    required_fields_map = {
        'gender': '性别', 'age': '年龄', 'height': '身高', 'weight': '体重',
        'systolic_bp': '收缩压', 'diastolic_bp': '舒张压',
        'family_history': '心血管家族史', 'total_cholesterol': '总胆固醇',
        'blood_glucose': '空腹血糖', 'late_night': '每周熬夜次数', 'smoking': '吸烟情况'
    }
    
    filled_count = sum(1 for key in required_fields_map if profile.get(key) not in (None, "", "-- 请选择 --"))
    if profile.get('diseases'): filled_count += 1
    total_required = len(required_fields_map) + 1
    progress_pct = min(100, int((filled_count / total_required) * 100))
    
    st.markdown(f'''
    <div class="progress-container">
        <div class="progress-text">
            <span>✅ 已完成 {filled_count}/{total_required} 项核心信息</span>
            <span>进度：{progress_pct}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {progress_pct}%"></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # ====================== 步骤 1 ======================
    if st.session_state.step == 1:
        st.markdown('<div class="section-title" style="margin: 0.5rem 0 0.8rem 0;">📊 基础生理与生化指标</div>', unsafe_allow_html=True)
        
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.markdown('<div class="field-label required"><span class="field-icon">🚹</span>性别 (必填)</div>', unsafe_allow_html=True)
            g_idx = 0 if profile.get('gender') == '男' else 1
            profile['gender'] = st.selectbox("请选择", ["男", "女"], index=g_idx, key="sel_gender", label_visibility="collapsed")
        with r1_c2:
            st.markdown('<div class="field-label required"><span class="field-icon">📏</span>身高 (必填)</div>', unsafe_allow_html=True)
            profile['height'] = st.number_input("cm", 140, 220, profile.get('height'), key="inp_h", label_visibility="collapsed")
        
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.markdown('<div class="field-label required"><span class="field-icon">🎂</span>年龄 (必填)</div>', unsafe_allow_html=True)
            profile['age'] = st.number_input("岁", 18, 120, profile.get('age'), key="inp_age", label_visibility="collapsed")
        with r2_c2:
            st.markdown('<div class="field-label required"><span class="field-icon">⚖️</span>体重 (必填)</div>', unsafe_allow_html=True)
            profile['weight'] = st.number_input("kg", 30.0, 200.0, float(profile.get('weight', 65)), step=0.5, key="inp_weight", label_visibility="collapsed")
        
        if profile.get('height') and profile.get('weight') and profile['height'] > 0:
            h_m = profile['height'] / 100
            bmi = profile['weight'] / (h_m ** 2)
            if bmi < 18.5:
                status = "偏轻"
                badge_class = "underweight"
            elif 18.5 <= bmi <= 24.9:
                status = "正常"
                badge_class = "normal"
            else:
                status = "超重/肥胖"
                badge_class = "overweight"
            
            st.markdown(f'''
            <div class="bmi-premium">
                <div class="bmi-premium-left">
                    <span class="bmi-premium-label">⚖️ 身体质量指数</span>
                    <div class="bmi-premium-value">{bmi:.1f}</div>
                    <div>
                        <span class="bmi-premium-status-badge {badge_class}">{status}</span>
                        <span style="font-size:0.9rem; color:var(--gray-600); margin-left:8px;">根据身高体重计算</span>
                    </div>
                </div>
                <div class="bmi-premium-right" style="text-align:right; background:var(--gray-50); padding:0.8rem 1.2rem; border-radius:16px; border:1px dashed var(--primary);">
                    <div style="font-size:0.8rem; color:var(--gray-600); font-weight:500;">健康参考范围</div>
                    <div><span style="font-size:1.4rem; font-weight:700; color:var(--primary-dark);">18.5 - 24.9</span><span style="font-size:0.9rem; color:var(--gray-600);">kg/m²</span></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
        PLACEHOLDER = "-- 请选择 --"
        bp_sys_opts = [PLACEHOLDER, "未测量", "90-119", "120-129", "130-139", "140-159", "≥160"]
        bp_dia_opts = [PLACEHOLDER, "未测量", "60-79", "80-89", "90-99", "≥100"]
        chol_opts = [PLACEHOLDER, "未测量", "<4.0", "4.0-5.2", "5.2-6.2", ">6.2"]
        glu_opts = [PLACEHOLDER, "未测量", "<5.6", "5.6-6.9", "7.0-11.0", ">11.0"]
        
        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            st.markdown('<div class="field-label required"><span class="field-icon">🩸</span>收缩压 (必填)</div>', unsafe_allow_html=True)
            cur = profile.get('systolic_bp', PLACEHOLDER)
            if cur not in bp_sys_opts: cur = PLACEHOLDER
            profile['systolic_bp'] = st.selectbox("mmHg", bp_sys_opts, index=bp_sys_opts.index(cur), key="sel_sys", label_visibility="collapsed")
        with r3_c2:
            st.markdown('<div class="field-label required"><span class="field-icon">🧪</span>总胆固醇 (必填)</div>', unsafe_allow_html=True)
            cur = profile.get('total_cholesterol', PLACEHOLDER)
            if cur not in chol_opts: cur = PLACEHOLDER
            profile['total_cholesterol'] = st.selectbox("mmol/L", chol_opts, index=chol_opts.index(cur), key="sel_chol", label_visibility="collapsed")
            
        r4_c1, r4_c2 = st.columns(2)
        with r4_c1:
            st.markdown('<div class="field-label required"><span class="field-icon">🩸</span>舒张压 (必填)</div>', unsafe_allow_html=True)
            cur = profile.get('diastolic_bp', PLACEHOLDER)
            if cur not in bp_dia_opts: cur = PLACEHOLDER
            profile['diastolic_bp'] = st.selectbox("mmHg", bp_dia_opts, index=bp_dia_opts.index(cur), key="sel_dia", label_visibility="collapsed")
        with r4_c2:
            st.markdown('<div class="field-label required"><span class="field-icon">🍬</span>空腹血糖 (必填)</div>', unsafe_allow_html=True)
            cur = profile.get('blood_glucose', PLACEHOLDER)
            if cur not in glu_opts: cur = PLACEHOLDER
            profile['blood_glucose'] = st.selectbox("mmol/L", glu_opts, index=glu_opts.index(cur), key="sel_glu", label_visibility="collapsed")
        
        fam_opts = ["无", "一级亲属", "二级亲属", "不清楚"]
        cur_fam = profile.get('family_history', "无")
        if cur_fam not in fam_opts: cur_fam = "无"
        st.markdown('<div class="field-label required"><span class="field-icon">👨‍👩‍👧‍👦</span>心血管家族史 (必填)</div>', unsafe_allow_html=True)
        profile['family_history'] = st.selectbox("请选择", fam_opts, index=fam_opts.index(cur_fam), key="sel_fam", label_visibility="collapsed")
        
        if st.button("下一步 → 疾病史", type="primary", use_container_width=True, key="btn_step1"):
            st.session_state.step = 2
            st.rerun()
            
    # ====================== 步骤 2 (疾病大类框住亚型选择) ======================
    elif st.session_state.step == 2:
        st.markdown('<div class="section-title" style="margin: 0.5rem 0 0.5rem 0;">❤️ 疾病史与共病选择</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box" style="margin-top:0.5rem; margin-bottom:0.8rem;">📊 心血管疾病共病率 >60%，请选择所有符合情况的大类</div>', unsafe_allow_html=True)
        
        if 'diseases_multiselect' not in st.session_state or set(st.session_state['diseases_multiselect']) != set(profile.get('diseases', [])):
            st.session_state['diseases_multiselect'] = profile.get('diseases', []).copy()
        
        st.markdown('<div class="combo-buttons">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🫀 高血压 + 冠心病", use_container_width=True):
                st.session_state['diseases_multiselect'] = ["高血压心脏病", "缺血性心脏病"]
                profile['diseases'] = ["高血压心脏病", "缺血性心脏病"]
                st.rerun()
        with col2:
            if st.button("⚡ 冠心病 + 心律失常", use_container_width=True):
                st.session_state['diseases_multiselect'] = ["缺血性心脏病", "心律失常"]
                profile['diseases'] = ["缺血性心脏病", "心律失常"]
                st.rerun()
        with col3:
            if st.button("❤️ 高血压 + 瓣膜病", use_container_width=True):
                st.session_state['diseases_multiselect'] = ["高血压心脏病", "瓣膜性心脏病"]
                profile['diseases'] = ["高血压心脏病", "瓣膜性心脏病"]
                st.rerun()
        with col4:
            if st.button("⚠️ 多重高危组合", use_container_width=True):
                st.session_state['diseases_multiselect'] = ["缺血性心脏病", "高血压心脏病", "心律失常"]
                profile['diseases'] = ["缺血性心脏病", "高血压心脏病", "心律失常"]
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="subsection-title" style="margin-top:0.8rem;">📋 或手动选择疾病大类</div>', unsafe_allow_html=True)
        
        all_diseases = ["缺血性心脏病", "高血压心脏病", "心律失常", "心肌病", "瓣膜性心脏病", "先天性心脏病", "主动脉疾病", "血管疾病"]
        selected = st.multiselect("选择", all_diseases, key="diseases_multiselect", label_visibility="collapsed")
        profile['diseases'] = list(st.session_state['diseases_multiselect'])
        
        subtypes_map = {
            "心肌病": ["未知", "扩张型心肌病", "肥厚型心肌病", "限制型心肌病", "致心律失常性右室心肌病"],
            "缺血性心脏病": ["未知", "慢性冠脉综合征", "急性冠脉综合征"],
            "高血压心脏病": ["未知", "高血压性左心室肥厚", "高血压性心力衰竭"],
            "心律失常": ["未知", "快速性心律失常", "缓慢性心律失常"],
            "瓣膜性心脏病": ["未知", "二尖瓣病变", "主动脉瓣病变"],
            "先天性心脏病": ["未知", "左向右分流", "复杂紫绀型"],
            "主动脉疾病": ["未知", "主动脉瘤", "主动脉夹层"],
            "血管疾病": ["未知", "脑血管疾病", "外周动脉疾病"]
        }
        
        disease_icons = {
            "心肌病": "💪",
            "缺血性心脏病": "❤️‍🔥",
            "高血压心脏病": "📈",
            "心律失常": "⚡",
            "瓣膜性心脏病": "🚪",
            "先天性心脏病": "👶",
            "主动脉疾病": "🔄",
            "血管疾病": "🩸"
        }
        
        if profile['diseases']:
            st.markdown('<div class="section-title" style="font-size:1.8rem; margin:1rem 0 0.6rem 0;">🔬 亚型确认</div>', unsafe_allow_html=True)
            
            # 使用grid布局包裹所有疾病卡片
            st.markdown('<div class="disease-grid">', unsafe_allow_html=True)
            
            for d in profile['diseases']:
                opts = subtypes_map.get(d, ["未知"])
                key = f"subtype_{d}"
                if key not in profile or profile[key] not in opts: 
                    profile[key] = "未知"
                
                # 创建唯一的选择框key
                select_key = f"sel_{d}_{abs(hash(d)) % 10000}"
                
                # 疾病卡片开始
                st.markdown(f'''
                <div class="disease-card">
                    <div class="disease-header">
                        <div class="disease-icon">{disease_icons.get(d, "🔬")}</div>
                        <div class="disease-name">{d}</div>
                    </div>
                    <div class="subtype-section">
                        <div class="subtype-label">
                            📌 选择亚型
                            <span>必填</span>
                        </div>
                ''', unsafe_allow_html=True)
                
                # Streamlit选择框
                selected_subtype = st.selectbox(
                    f"选择{d}的亚型", 
                    opts, 
                    index=opts.index(profile[key]) if profile[key] in opts else 0,
                    key=select_key,
                    label_visibility="collapsed"
                )
                profile[key] = selected_subtype
                
                # 根据选择状态显示不同的提示区域
                if profile[key] == "未知":
                    st.markdown(f'''
                        <div class="subtype-status hint">
                            <div class="subtype-status-icon">💡</div>
                            <div class="subtype-status-text">
                                AI 智能推导
                                <div class="subtype-status-subtext">根据您的健康数据，AI将自动分析最可能的亚型</div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                        <div class="subtype-status confirmed">
                            <div class="subtype-status-icon">✅</div>
                            <div class="subtype-status-text">
                                已确认：{profile[key]}
                                <div class="subtype-status-subtext">AI将在报告中深入分析该亚型特征</div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                
                # 关闭subtype-section和disease-card
                st.markdown('</div></div>', unsafe_allow_html=True)
            
            # 关闭disease-grid
            st.markdown('</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 3])
        with c1:
            if st.button("← 上一步", use_container_width=True, key="btn_back2"): 
                st.session_state.step = 1
                st.rerun()
        with c2:
            if st.button("下一步 → 生活方式", type="primary", use_container_width=True, key="btn_next2"):
                if not profile['diseases']: 
                    st.markdown('<div class="warning-box">⚠️ 请至少选择一项疾病大类。</div>', unsafe_allow_html=True)
                else: 
                    st.session_state.step = 3
                    st.rerun()
                    
    # ====================== 步骤 3 ======================
    elif st.session_state.step == 3:
        st.markdown('<div class="section-title" style="margin: 0.5rem 0 0.8rem 0;">🌟 生活方式与风险因素</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">✨ 填写这些有助于 AI 给出更精准的个性化生活干预建议</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="field-label required"><span class="field-icon">🚬</span>吸烟 (必填)</div>', unsafe_allow_html=True)
            profile['smoking'] = st.checkbox("是否吸烟", value=profile.get('smoking', False), key="cb_smoke")
            
            st.markdown('<div class="field-label"><span class="field-icon">🍺</span>饮酒 (选填)</div>', unsafe_allow_html=True)
            profile['drinking'] = st.checkbox("每周≥3 次", value=profile.get('drinking', False), key="cb_drink")
            
            st.markdown('<div class="field-label"><span class="field-icon">🧂</span>高盐饮食 (选填)</div>', unsafe_allow_html=True)
            profile['high_salt'] = st.checkbox("口味偏重", value=profile.get('high_salt', False), key="cb_salt")
            
            st.markdown('<div class="field-label"><span class="field-icon">🍰</span>高糖饮食 (选填)</div>', unsafe_allow_html=True)
            profile['high_sugar'] = st.checkbox("喜爱甜食", value=profile.get('high_sugar', False), key="cb_sugar")
            
        with c2:
            st.markdown('<div class="field-label required"><span class="field-icon">🌙</span>每周熬夜次数 (必填)</div>', unsafe_allow_html=True)
            profile['late_night'] = st.number_input("次/周", 0, 7, profile.get('late_night'), key="inp_late", label_visibility="collapsed")
            st.markdown('<div class="field-label"><span class="field-icon">🏃</span>每周运动次数 (选填)</div>', unsafe_allow_html=True)
            profile['ex_freq'] = st.number_input("次", 0, 7, profile.get('ex_freq'), key="inp_ex_f", label_visibility="collapsed")
            st.markdown('<div class="field-label"><span class="field-icon">⏱️</span>每次运动时长 (选填)</div>', unsafe_allow_html=True)
            profile['ex_dur'] = st.number_input("分钟", 0, 180, profile.get('ex_dur'), key="inp_ex_d", label_visibility="collapsed")
            st.markdown('<div class="field-label"><span class="field-icon">😰</span>压力水平 (选填)</div>', unsafe_allow_html=True)
            profile['stress'] = st.selectbox("请选择", ["低", "中", "高"], index=["低","中","高"].index(profile.get('stress', '中')), key="sel_stress", label_visibility="collapsed")
        
        st.markdown('<div class="field-label"><span class="field-icon">😴</span>日均睡眠 (选填)</div>', unsafe_allow_html=True)
        profile['sleep'] = st.slider("小时", 3.0, 12.0, float(profile.get('sleep', 7.0)), 0.5, key="sl_sleep", label_visibility="collapsed")
        
        allergy_opts = ["花生", "坚果", "海鲜", "乳制品", "大豆", "鸡蛋", "麸质", "芝麻", "无"]
        st.markdown('<div class="field-label"><span class="field-icon">🥜</span>食物过敏 (选填)</div>', unsafe_allow_html=True)
        profile['allergies'] = st.multiselect("请选择", allergy_opts, default=profile.get('allergies', []), key="ms_allergy", label_visibility="collapsed")
        
        diet_options = ["中式清淡", "严格低钠", "无酒精/无酒酿", "低嘌呤", "低组胺/无发酵", "无亚硫酸盐", "高蛋白", "低脂饮食", "糖尿病友好", "软食易消化", "高纤维通便", "地中海/DASH 风格"]
        st.markdown('<div class="field-label"><span class="field-icon">🥗</span>饮食偏好 (选填)</div>', unsafe_allow_html=True)
        profile['diet_pref'] = st.multiselect("请选择", diet_options, default=profile.get('diet_pref', []), key="ms_diet", label_visibility="collapsed")
        
        st.markdown('''
        <details class="diet-details">
            <summary>📚 查看饮食风格与忌口指南</summary>
            <div class="diet-guide">
                <div class="diet-grid">
                    <div class="diet-item"><div class="diet-name">🥗 中式清淡</div><div class="diet-desc">少油少盐，以蒸、煮、炖为主。</div><div class="diet-suit">适合大多数康复期患者</div></div>
                    <div class="diet-item"><div class="diet-name">🧂 严格低钠</div><div class="diet-desc">完全无添加盐，排除酱油/咸菜。</div><div class="diet-suit">适合高血压、心衰患者</div></div>
                    <div class="diet-item"><div class="diet-name">🚫 无酒精/无酒酿</div><div class="diet-desc">排除所有含酒精菜肴。</div><div class="diet-suit">适合心律失常患者</div></div>
                    <div class="diet-item"><div class="diet-name">🍄 低嘌呤</div><div class="diet-desc">避开内脏、浓肉汤。</div><div class="diet-suit">适合合并痛风患者</div></div>
                    <div class="diet-item"><div class="diet-name">🌿 低组胺/无发酵</div><div class="diet-desc">避开腌制食品、陈年奶酪。</div><div class="diet-suit">适合易心悸、过敏体质</div></div>
                    <div class="diet-item"><div class="diet-name">🍷 无亚硫酸盐</div><div class="diet-desc">避开干果、葡萄酒。</div><div class="diet-suit">适合合并哮喘患者</div></div>
                    <div class="diet-item"><div class="diet-name">🥩 高蛋白</div><div class="diet-desc">增加鱼禽蛋豆。</div><div class="diet-suit">适合术后恢复患者</div></div>
                    <div class="diet-item"><div class="diet-name">🧈 低脂饮食</div><div class="diet-desc">限制肥肉/油炸。</div><div class="diet-suit">适合高血脂、冠心病</div></div>
                    <div class="diet-item"><div class="diet-name">📉 糖尿病友好</div><div class="diet-desc">低 GI 食物。</div><div class="diet-suit">适合合并糖尿病患者</div></div>
                    <div class="diet-item"><div class="diet-name">🥣 软食易消化</div><div class="diet-desc">食物切碎煮烂。</div><div class="diet-suit">适合高龄、术后患者</div></div>
                    <div class="diet-item"><div class="diet-name">🌾 高纤维通便</div><div class="diet-desc">预防便秘。</div><div class="diet-suit">适合卧床、活动量少</div></div>
                    <div class="diet-item"><div class="diet-name">🌍 地中海/DASH</div><div class="diet-desc">橄榄油、全谷物。</div><div class="diet-suit">适合所有心血管高危人群</div></div>
                </div>
            </div>
        </details>
        ''', unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 3])
        with c1:
            if st.button("← 上一步", use_container_width=True, key="btn_back3"): 
                st.session_state.step = 2
                st.rerun()
        with c2:
            if st.button("💾 保存并生成 AI 报告", type="primary", use_container_width=True, key="btn_gen_ai"):
                missing_cn = []
                PLACEHOLDER = "-- 请选择 --"
                for key, label in required_fields_map.items():
                    val = profile.get(key)
                    if key == 'smoking': continue
                    if key in ['systolic_bp', 'diastolic_bp', 'total_cholesterol', 'blood_glucose']:
                        if val in (PLACEHOLDER, None, ""): missing_cn.append(label)
                        continue
                    if val is None or val == "": missing_cn.append(label)
                if not profile.get('diseases'): missing_cn.append("疾病史选择")
                
                if missing_cn:
                    st.markdown(f'<div class="warning-box">⚠️ 请填写所有核心必填项：{", ".join(missing_cn)}</div>', unsafe_allow_html=True)
                else:
                    save_data_to_file(profile)
                    
                    with st.spinner("🧠 AI 正在深度分析您的健康档案..."):
                        prompt_text = generate_structured_prompt(profile)
                        try:
                            resp = client.chat.completions.create(
                                model="qwen-turbo", 
                                messages=[{"role": "user", "content": prompt_text}], 
                                temperature=0.3, 
                                max_tokens=2000,
                                response_format={"type": "json_object"}
                            )
                            ai_raw = resp.choices[0].message.content
                            st.session_state.ai_result = ai_raw
                        except Exception as e:
                            st.session_state.ai_result = f"Error: {str(e)}"
                    st.rerun()
        
        if st.session_state.get('ai_result'):
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">📋 AI 健康分析报告</div>', unsafe_allow_html=True)
            
            analysis_list, prevent_list, subtype_list = parse_ai_json_response(st.session_state.ai_result)
            
            if analysis_list or prevent_list or subtype_list:
                if analysis_list:
                    st.markdown("""
                    <div class="ai-report">
                        <div class="ai-report-header">
                            <div class="ai-report-icon">🫀</div>
                            <div class="ai-report-title-wrapper">
                                <div class="ai-report-title">身体健康分析</div>
                                <div class="ai-report-subtitle">基于您健康数据的专业解读</div>
                            </div>
                            <div class="ai-report-badge">AI 智能分析</div>
                        </div>
                        <div class="analysis-grid">
                    """, unsafe_allow_html=True)
                    
                    for item in analysis_list:
                        if ':' in item or ':' in item:
                            sep = ':' if ':' in item else ':'
                            parts = item.split(sep, 1)
                            title = parts[0].strip()
                            desc = parts[1].strip()
                            st.markdown(f'''
                            <div class="analysis-card">
                                <div class="analysis-card-header">
                                    <div class="analysis-card-icon">📊</div>
                                    <div class="analysis-card-title">{title}</div>
                                </div>
                                <div class="analysis-card-content">
                                    <div class="analysis-item">{desc}</div>
                                </div>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'''
                            <div class="analysis-card">
                                <div class="analysis-card-content">
                                    <div class="analysis-item">{item}</div>
                                </div>
                            </div>
                            ''', unsafe_allow_html=True)
                    
                    st.markdown('</div></div>', unsafe_allow_html=True)
                
                if prevent_list:
                    st.markdown("""
                    <div class="ai-report">
                        <div class="ai-report-header">
                            <div class="ai-report-icon">🛡️</div>
                            <div class="ai-report-title-wrapper">
                                <div class="ai-report-title">预防与控制建议</div>
                                <div class="ai-report-subtitle">个性化心血管风险管理方案</div>
                            </div>
                            <div class="ai-report-badge">4 项关键建议</div>
                        </div>
                        <div class="prevent-list">
                    """, unsafe_allow_html=True)
                    
                    for item in prevent_list:
                        st.markdown(f'''
                        <div class="prevent-item">
                            <div class="prevent-check">✓</div>
                            <div class="prevent-text">{item}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown('</div></div>', unsafe_allow_html=True)
                
                if subtype_list:
                    has_unknown = any(profile.get(f"subtype_{d}") == "未知" for d in profile.get('diseases', []))
                    icon = "🔬" if has_unknown else "📋"
                    title = "亚型智能推导" if has_unknown else "亚型分析"
                    badge = f"{len(subtype_list)} 条分析"
                    
                    st.markdown(f"""
                    <div class="ai-report">
                        <div class="ai-report-header">
                            <div class="ai-report-icon">{icon}</div>
                            <div class="ai-report-title-wrapper">
                                <div class="ai-report-title">{title}</div>
                                <div class="ai-report-subtitle">{'基于临床表现的逻辑推导' if has_unknown else '已确认亚型深入分析'}</div>
                            </div>
                            <div class="ai-report-badge">{badge}</div>
                        </div>
                        <div class="{'logic-flow' if has_unknown else 'analysis-flow'}">
                    """, unsafe_allow_html=True)
                    
                    for item in subtype_list:
                        if has_unknown:
                            st.markdown(f'<div class="logic-step">{item}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="analysis-step">{item}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-report"><div>{st.session_state.ai_result}</div></div>', unsafe_allow_html=True)
            
            st.markdown('''
            <div class="disclaimer">
                <span>⚠️</span>
                <span>重要提示：以上报告基于您提供的数据进行逻辑推导，仅供健康管理参考，不能替代线下医院的专业诊断与治疗。如有不适，请及时就医。</span>
            </div>
            ''', unsafe_allow_html=True)
            st.balloons()

if __name__ == "__main__":
    main()