# pages/p04_knowledge.py
import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import re

# ─── 配置 ────────────────────────────────────────────────
client = OpenAI(
    api_key="sk-e200005b066942eebc8c5426df92a6d5",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 【关键修改】同时设置 page_title (带 emoji) 和 page_icon (单独 emoji)
# 这样浏览器标签页会显示 📚，页面标题也会显示 📚
st.set_page_config(
    page_title="知识库 · CardioGuard AI", 
    page_icon="📚",  # 这里单独设置标签页图标
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ==========================================
# CSS 样式 - 完全同步 p02_nutrition.py 的导航栏和布局风格
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #F97316;       /* 知识库主题色：橙色 */
        --primary-dark: #C2410C;
        --primary-light: #FFEDD5;
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
    
    /* 移除默认 padding-top */
    .main > div { 
        padding-top: 0 !important; 
    }
    
    /* 调整主内容区域 */
    .block-container { 
        padding: 0 2rem 1rem !important; 
        max-width: 1400px; 
        margin: 0 auto; 
    }
    
    #MainMenu, footer, section[data-testid="stSidebar"] { display: none !important; }
    
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
    
    /* Hero 区域 - 同步 nutrition 的紧凑风格，但使用知识库主题色 */
    .hero-box { 
        background: linear-gradient(135deg, #F97316 0%, #C2410C 100%); 
        padding: 1.8rem 1.5rem;      /* 同步：更紧凑的内边距 */
        border-radius: 24px; 
        text-align: center; 
        color: white; 
        margin: 0.5rem 0 1rem 0;     /* 同步：更紧凑的外边距 */
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
    
    /* ===== 以下是功能代码区域样式，保持原有逻辑，微调字体 ===== */
    
    /* Tabs 样式 */
    .stTabs {
        margin-top: 0.2rem;
        margin-bottom: -0.5rem !important;
        position: relative;
        z-index: 5;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px !important;
        background: #f8fafc;
        padding: 4px;
        border-radius: 40px;
        border: 1px solid #eef2f6;
        margin-bottom: 0rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        padding: 0.3rem 1rem !important;
        border-radius: 40px !important;
        background: transparent !important;
        color: #64748b !important;
        border: none !important;
        transition: all 0.2s;
        margin: 0 !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 0.2rem !important;
        margin-top: 0 !important;
    }
    
    /* 页面主标题 */
    .section-title {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: var(--gray-800) !important;
        margin: 1.2rem 0 0.8rem 0 !important;
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
    
    /* 子标题 */
    .sub-desc {
        font-size: 0.9rem !important;
        color: #64748b;
        margin-bottom: 1rem;
    }
    
    /* Radio 按钮样式 */
    .stRadio {
        margin: 0 0 0.8rem 0 !important;
        padding: 0 !important;
    }
    .stRadio > div {
        flex-direction: row !important;
        justify-content: center !important;
        gap: 6px !important;
        background: #f1f5f9;
        padding: 4px !important;
        border-radius: 40px !important;
    }
    .stRadio [role="radiogroup"] {
        gap: 2px !important;
    }
    .stRadio [data-testid="stWidgetLabel"] {
        display: none !important;
    }
    .stRadio label {
        background: transparent !important;
        padding: 6px 16px !important;
        border-radius: 30px !important;
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        border: none !important;
        transition: all 0.2s !important;
        margin: 0 !important;
    }
    .stRadio label:hover {
        background: rgba(249,115,22,0.1) !important;
        color: var(--primary) !important;
    }
    .stRadio label[data-baseweb="radio"]:has(input:checked) {
        background: var(--primary) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(249,115,22,0.2) !important;
    }
    
    /* 折叠框样式 */
    .stExpander {
        border: none !important;
        background: transparent !important;
        margin: 0 0 1rem 0 !important;
        padding: 0 !important;
    }
    
    .stExpander > div:first-child {
        border: 1px solid #f1f5f9 !important;
        border-radius: 16px !important;
        background: white !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
        transition: all 0.2s ease;
    }
    
    .stExpander summary {
        padding: 0.8rem 1.5rem 0.8rem 3rem !important;
        list-style: none !important;
        cursor: pointer !important;
        position: relative !important;
        background: white !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        color: #1e293b !important;
        border: none !important;
        outline: none !important;
        user-select: none !important;
        transition: all 0.2s;
        display: block !important;
    }
    
    .stExpander summary::-webkit-details-marker {
        display: none !important;
    }
    
    .stExpander summary::marker {
        display: none !important;
        content: "" !important;
    }
    
    .stExpander summary::before {
        content: "▼" !important;
        position: absolute !important;
        left: 1.2rem !important;
        top: 50% !important;
        transform: translateY(-50%) rotate(0deg) !important;
        font-size: 0.9rem !important;
        color: var(--primary) !important;
        transition: transform 0.2s ease !important;
        display: inline-block !important;
        width: 20px !important;
        text-align: center !important;
        font-weight: 400 !important;
        z-index: 10 !important;
    }
    
    .stExpander[open] summary::before {
        transform: translateY(-50%) rotate(180deg) !important;
    }
    
    .stExpander summary svg,
    .stExpander summary [data-testid="stExpanderToggleIcon"] {
        display: none !important;
    }
    
    .stExpander > div[data-testid="stExpanderDetails"] {
        padding: 1rem 1.5rem !important;
        border-top: 1px solid rgba(249,115,22,0.1) !important;
        background: #ffffff;
        border-radius: 0 0 16px 16px;
    }
    
    .stExpander p, .stExpander li, .stExpander div {
        font-size: 0.9rem !important;
    }
    
    .stExpander h4 {
        font-size: 1.2rem !important;
        margin: 0.5rem 0 0.8rem 0 !important;
    }
    
    .stExpander h5 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin: 0.8rem 0 0.3rem 0 !important;
        color: var(--gray-800);
    }
    
    .stImage {
        margin-bottom: 0.5rem;
    }
    
    .stImage img {
        border-radius: 12px;
        border: 1px solid #f1f5f9;
    }
    
    .insight-card {
        background: #FFF7ED;
        padding: 0.7rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        border-left: 4px solid var(--primary);
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        transition: all 0.2s;
        font-size: 0.85rem !important;
        color: #334155;
        line-height: 1.5;
    }
    .insight-card:hover {
        transform: translateX(2px);
        box-shadow: 0 4px 12px rgba(249,115,22,0.08);
    }
    
    .insight-card + h3, .stMarkdown h3 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin: 0 0 0.5rem 0 !important;
        color: var(--gray-800);
    }
    
    .stButton button {
        background: white !important;
        border: 1px solid var(--primary) !important;
        color: var(--primary) !important;
        border-radius: 30px !important;
        padding: 0.3rem 0.6rem !important;
        font-size: 0.8rem !important;
        transition: all 0.2s !important;
        white-space: normal !important;
        height: auto !important;
        min-height: 50px !important;
        word-break: break-word !important;
        line-height: 1.3 !important;
    }
    .stButton button:hover {
        background: var(--primary) !important;
        color: white !important;
        border-color: var(--primary) !important;
        box-shadow: 0 2px 8px rgba(249,115,22,0.15) !important;
    }
    
    .info-box {
        background: var(--primary-light);
        padding: 0.6rem 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary);
        font-size: 0.9rem !important;
        color: #334155;
        margin: 0.5rem 0;
    }
    
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 1.5rem !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: min(700px, 90%) !important;
        z-index: 9999 !important;
        background: white !important;
        border: 2px solid rgba(249,115,22,0.15) !important;
        border-radius: 40px !important;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05) !important;
        padding: 0.2rem 0.8rem !important;
    }
    
    .stChatMessage {
        font-size: 0.9rem !important;
    }
    
    .js-plotly-plot .gtitle {
        font-size: 14px !important;
    }
    
    .legendtext {
        font-size: 11px !important;
    }
    
    .xtitle, .ytitle {
        font-size: 11px !important;
    }
    
    p, li, .stMarkdown, .stText {
        font-size: 0.9rem !important;
        line-height: 1.5;
    }
    
    .stTabs h4 {
        font-size: 1.1rem !important;
        margin: 0.5rem 0 !important;
    }
    
    .stTabs h5 {
        font-size: 1rem !important;
        margin: 0.5rem 0 0.2rem 0 !important;
    }
    
    .stPlotlyChart {
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── 后面的 main 函数 ──────────────────────────────────────────
def main():
    # 渲染顶部导航栏 - 完全同步 nutrition.py 的结构
    st.markdown("""
    <div class="top-navbar">
        <div class="nav-logo">❤️ CardioGuard AI</div>
        <div class="nav-links">
             <a href="/p00_home">🏠 首页</a>
            <a href="/p01_profile">📋 健康档案</a>
            <a href="/p01_overview">📊 健康总览</a>
            <a href="/p02_nutrition">🥗 营养建议</a>
            <a href="/p03_ai_doctor">🩺 AI 医生</a>
            <a href="/p04_knowledge" class="active">📚 知识库</a>
            <a href="/p05_me">👤 我的中心</a>
        </div>
    </div>
    
    <!-- Hero 区域 -->
    <div class="hero-box">
        <h1 class="hero-title">📚 知识库</h1>
        <p class="hero-sub">心血管疾病科学解读 · 数据驱动洞察</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 为 Tab 添加 Icon
    tab_data, tab_disease, tab_chat = st.tabs(["📊 数据洞察", "🫀 疾病图谱", "💬 智能问答"])
    
    # ── Tab 1：数据洞察 ───────────────────────────────────────────────
    with tab_data:
        st.markdown('<div class="section-title">核心风险指标交互分析</div>', unsafe_allow_html=True)
        try:
            df = pd.read_csv("data/cardio_train.csv", sep=";")
            df["age_year"] = (df["age"] / 365.25).round().astype(int)
        except:
            st.error("数据文件加载失败")
            st.stop()
        
        st.markdown('<p class="sub-desc">选择以下视图探索数据洞察（数据来源于 Kaggle Cardiovascular Disease dataset，包含约 70,000 个样本，用于预测心血管风险因素）</p>', unsafe_allow_html=True)
        
        view = st.radio("", 
                        ["年龄与血压关系", "风险因素相关性", "生活习惯对比", "年龄分布预警"],
                        horizontal=True, label_visibility="collapsed")
        
        c1, c2 = st.columns([7,3])
        with c1:
            if view == "年龄与血压关系":
                fig = px.scatter(df.sample(2500, random_state=42), x="age_year", y="ap_hi",
                                 color="cardio", color_discrete_map={0:"#00e5ff",1:"#ff5252"},
                                 hover_data=["ap_lo","cholesterol","gluc"],
                                 title="年龄 vs 收缩压（点越大代表舒张压越高）",
                                 size="ap_lo", size_max=40, opacity=0.7)
                fig.update_traces(marker=dict(sizemin=10))
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                  font_size=11, title_font_size=14,
                                  yaxis_range=[60, 220], margin=dict(t=30, b=20, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)
            elif view == "风险因素相关性":
                corr = df.corr(numeric_only=True)['cardio'].abs().sort_values(ascending=False)[1:12]
                fig = px.bar(x=corr.values, y=corr.index, orientation='h',
                             color=corr.values, color_continuous_scale="Oranges",
                             title="心血管疾病相关性 Top 因素")
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                  font_size=11, title_font_size=14,
                                  margin=dict(t=30, b=20, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)
            elif view == "生活习惯对比":
                melted = pd.melt(df, id_vars=["cardio"], value_vars=["smoke","alco","active"])
                fig = px.sunburst(melted, path=["variable","value","cardio"],
                                  title="生活方式与疾病关系的层级分布",
                                  color_discrete_sequence=["#F97316", "#fb923c", "#ff5252"])
                fig.update_layout(margin=dict(t=30, b=20, l=20, r=20),
                                  font_size=11, title_font_size=14)
                st.plotly_chart(fig, use_container_width=True)
            elif view == "年龄分布预警":
                fig = px.histogram(df[df['age_year'] >= 35], x="age_year", color="cardio",
                                   barmode="overlay", nbins=50,
                                   color_discrete_map={0:"#fb923c",1:"#C2410C"},
                                   title="年龄分布与心血管疾病风险（数据集低龄样本较少，30-35 岁数据有限）")
                fig.add_vline(x=50, line_dash="dash", line_color="#C2410C", annotation_text="50 岁风险快速上升")
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                  font_size=11, title_font_size=14,
                                  margin=dict(t=30, b=20, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("### 关键发现速览")
            if view == "年龄与血压关系":
                avg_hi_cardio = df[df['cardio']==1]['ap_hi'].mean()
                avg_hi_no = df[df['cardio']==0]['ap_hi'].mean()
                st.markdown(f'<div class="insight-card">• 患者平均收缩压 {avg_hi_cardio:.1f} mmHg，高于非患者 {avg_hi_no:.1f} mmHg</div>', unsafe_allow_html=True)
                st.markdown('<div class="insight-card">• 45 岁后高压点明显增多，需警惕隐性风险</div>', unsafe_allow_html=True)
                st.markdown('<div class="insight-card">• 血糖/胆固醇异常常伴随血压升高</div>', unsafe_allow_html=True)
            elif view == "风险因素相关性":
                top_corr = df.corr(numeric_only=True)['cardio'].abs().sort_values(ascending=False)[1:3]
                st.markdown(f'<div class="insight-card">• 顶级因素：年龄 (相关性 {top_corr.iloc[0]:.2f}) 和体重指数</div>', unsafe_allow_html=True)
                st.markdown('<div class="insight-card">• 血压指标主导风险，需优先控制</div>', unsafe_allow_html=True)
                st.markdown('<div class="insight-card">• 生活因素如吸烟相关性较低但可干预</div>', unsafe_allow_html=True)
            elif view == "生活习惯对比":
                smoke_rate = df[df['smoke']==1]['cardio'].mean() * 100
                active_rate = df[df['active']==0]['cardio'].mean() * 100
                st.markdown(f'<div class="insight-card">• 吸烟者患病率 {smoke_rate:.1f}%，高于整体水平</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="insight-card">• 不运动人群风险升至 {active_rate:.1f}%，运动可显著降低</div>', unsafe_allow_html=True)
                st.markdown('<div class="insight-card">• 饮酒影响中性，但与吸烟叠加风险放大</div>', unsafe_allow_html=True)
            elif view == "年龄分布预警":
                over_50_rate = df[df['age_year'] > 50]['cardio'].mean() * 100
                under_50_rate = df[df['age_year'] <= 50]['cardio'].mean() * 100
                st.markdown(f'<div class="insight-card">• 50 岁后患病率 {over_50_rate:.1f}%，远高于 50 岁前 {under_50_rate:.1f}%</div>', unsafe_allow_html=True)
                st.markdown('<div class="insight-card">• 年龄峰值在 55-60 岁，建议中年筛查</div>', unsafe_allow_html=True)
                st.markdown('<div class="insight-card">• 早发病例多伴随其他风险因素</div>', unsafe_allow_html=True)
    
    # ── Tab 2：疾病图谱 ───────────────────────────────────────────────
    with tab_disease:
        st.markdown('<div class="section-title">七大类心血管疾病图谱</div>', unsafe_allow_html=True)
        
        st.markdown('<p class="sub-desc">点击下方疾病分类，深入了解各类心血管疾病的病因、症状、亚型及治疗方案</p>', unsafe_allow_html=True)
        
        diseases = {
            "缺血性心脏病": { 
                "emoji": "❤️‍🔥",
                "file": "缺血性心脏病.avif", 
                "color":"#ff5252", 
                "overview": "缺血性心脏病（IHD）是最常见的心血管疾病类型，全球导致数百万死亡，主要涉及冠状动脉血流减少导致心肌缺氧。临床上常称为冠心病，包括心绞痛和心肌梗死。",
                "causes": "主要由冠状动脉粥样硬化引起，风险因素包括高血压、糖尿病、高脂血症、吸烟、肥胖、缺乏运动、遗传等。长期高胆固醇沉积导致动脉狭窄，减少心脏血流供应。",
                "symptoms": "胸痛（典型心绞痛）、气短、疲劳、心律不齐，严重时突发心肌梗死伴随剧痛、出汗、恶心。症状常在活动时加重。",
                "subtypes": "- 慢性冠脉综合征：稳定型心绞痛、缺血性心肌病、无症状心肌缺血。\n- 急性冠脉综合征：不稳定心绞痛、ST 段抬高型心肌梗死（STEMI）、非 ST 段抬高型心肌梗死（NSTEMI）。",
                "treatment": "紧急情况下需立即 PCI 或溶栓。常规治疗包括抗血小板药（如阿司匹林）、他汀类降脂药、生活方式干预（DASH 饮食、每周 150 分钟中等强度运动、戒烟限酒）。预防强调定期筛查血脂血压，控制体重，遗传高危者需早干预。"
            },
            "高血压心脏病": { 
                "emoji": "🩸",
                "file":"高血压心脏病.avif", 
                "color":"#f59e0b", 
                "overview": "高血压心脏病是指长期高血压导致的心脏结构和功能变化，是全球主要死亡原因之一，常发展为心力衰竭或缺血事件。影响约 10 亿人。",
                "causes": "慢性高血压导致心脏重构和左心室肥厚，风险包括遗传倾向、肥胖、高盐饮食（每日盐摄入>5g）、慢性压力、缺乏运动、过度饮酒、吸烟。肾素 - 血管紧张素系统异常常见。",
                "symptoms": "头痛、头晕、胸痛、气短、心悸、疲劳、下肢水肿。晚期可出现心力衰竭症状如夜间喘息。",
                "subtypes": "- 高血压性左心室肥厚：心脏壁增厚，影响泵血功能。\n- 高血压性心力衰竭：心脏泵血不足，导致体液潴留。\n- 高血压性肾功能损害：伴随肾动脉硬化。",
                "treatment": "目标血压<130/80 mmHg。使用 ACE 抑制剂、β阻滞剂、钙通道阻滞剂、利尿剂等药物组合。生活方式包括低盐饮食（每日<5g 盐）、减重、每周运动、压力管理。预防需每年监测血压，高危人群（如家族史）从年轻开始控制。"
            },
            "心律失常": { 
                "emoji": "⚡",
                "file":"心率失常.webp", 
                "color":"#8b5cf6", 
                "overview": "心律失常是心脏电活动异常，导致心跳不规律，可为良性或危及生命。常见于老年或心脏病患者，年发病率约 2%。",
                "causes": "电解质失衡（如低钾）、心脏基础疾病（缺血、心肌病）、高血压、甲状腺功能异常、慢性压力、过量咖啡因/酒精、某些药物、先天性离子通道缺陷。手术后或放射治疗也可诱发。",
                "symptoms": "心悸、头晕、胸痛、气短、昏厥、疲劳、心跳过快（>100 次/分）或过慢（<60 次/分）。严重时导致血栓或心衰。",
                "subtypes": "- 快速性心律失常：房颤/房扑、阵发性室上性心动过速、室性心动过速/室颤、早搏（房性/室性）。\n- 缓慢性心律失常：病态窦房结综合征、房室传导阻滞（I/II/III 度）。",
                "treatment": "急性发作需电复律或抗心律失常药。长期管理包括β阻滞剂、钙通道阻滞剂、射频消融、植入起搏器/ICD。预防避免诱因、保持电解质平衡、定期心电图检查、管理基础心脏病。"
            },
            "心肌病": { 
                "emoji": "🫀",
                "file":"扩张型心肌病.webp", 
                "color":"#ec4899", 
                "overview": "心肌病是心肌结构和功能异常的疾病群，常导致心衰或猝死。发病率约 1/2500，遗传型占 40%。",
                "causes": "遗传突变（如肌钙蛋白基因）、病毒感染（柯萨奇病毒）、慢性酒精滥用、化疗药物毒性、妊娠相关、长期高血压或缺血性心脏病。特发性病例占一定比例。",
                "symptoms": "进行性气短、疲劳、下肢水肿、心悸、心律失常、咳嗽（肺水肿）、胸痛。晚期发展为心力衰竭或猝死。",
                "subtypes": "- 扩张型心肌病 (DCM)：心脏扩大、泵血功能减弱，最常见。\n- 肥厚型心肌病 (HCM)：心室壁肥厚，常遗传，易致梗阻。\n- 限制型心肌病 (RCM)：心室僵硬，舒张功能障碍。\n- 致心律失常性右室心肌病 (ARVC)：右室脂肪取代，易室颤。\n- 代谢性心肌病：如淀粉样变性或法布雷病。",
                "treatment": "严重时需心脏移植。药物包括β阻滞剂、ACE 抑制剂、利尿剂、抗凝药；装置如 ICD/CRT。预防筛查家族史、避免酒精/毒物、控制基础疾病、遗传咨询。",
                "extra_img": "肥厚型心肌病.webp"
            },
            "瓣膜性心脏病": { 
                "emoji": "🚪",
                "file":"瓣膜性心脏病.webp", 
                "color":"#06b6d4", 
                "overview": "瓣膜性心脏病涉及心脏瓣膜结构异常，导致血流逆流或梗阻。全球影响 2.5% 人口，老年多见。",
                "causes": "先天缺陷、衰老性钙化、感染性（风湿热或感染性心内膜炎）、高血压、动脉粥样硬化、结缔组织疾病（如马凡综合征）。创伤或放射也可损伤瓣膜。",
                "symptoms": "气短、胸痛、心悸、下肢水肿、疲劳、咳血、昏厥。听诊闻及杂音。",
                "subtypes": "- 二尖瓣病变：狭窄、关闭不全、脱垂。\n- 主动脉瓣病变：狭窄、关闭不全、二叶瓣畸形。\n- 三尖瓣/肺动脉瓣病变：多继发于右心疾病。\n- 风湿性心脏病：多瓣膜受累，常狭窄。",
                "treatment": "重症需外科瓣膜置换或修复。药物控制症状（利尿剂、抗凝）；球囊扩张用于狭窄。预防风湿热（链球菌感染及时抗生素）、口腔卫生防内膜炎、定期超声筛查。"
            },
            "先天性心脏病": { 
                "emoji": "👶",
                "file":"先天性心脏病.webp", 
                "color":"#10b981", 
                "overview": "先天性心脏病是出生时心脏结构缺陷，最常见先天畸形，影响约 1% 新生儿，许多可手术矫正。",
                "causes": "遗传因素、染色体异常（如 21 三体）、母体糖尿病/感染（风疹病毒）、妊娠期药物/辐射暴露、环境毒素。约 8/1000 新生儿发病。",
                "symptoms": "紫绀、气短、喂养困难、生长迟缓、反复肺炎、心律异常。成人残留可致心衰。",
                "subtypes": "- 左向右分流型：房间隔缺损 (ASD)、室间隔缺损 (VSD)、动脉导管未闭 (PDA)。\n- 复杂紫绀型：法洛四联症、大动脉转位。\n- 梗阻型：主动脉缩窄、肺动脉瓣狭窄。",
                "treatment": "手术矫正或导管闭合，终身随访。药物控制症状。预防孕期避免感染、控制血糖、叶酸补充、遗传咨询。"
            },
            "主动脉疾病": { 
                "emoji": "🩹",
                "file":"主动脉疾病.avif", 
                "color":"#F97316", 
                "overview": "主动脉疾病涉及主干血管异常，如瘤或夹层，潜在致命，需紧急干预。发病率随年龄增加。",
                "causes": "动脉粥样硬化、高血压、遗传疾病（如马凡综合征）、创伤、感染、衰老、二叶主动脉瓣畸形。吸烟和脂质异常加速进展。",
                "symptoms": "突发撕裂样胸/背痛、血压不对称、脉搏弱、昏厥、休克。瘤破裂致大出血。",
                "subtypes": "- 主动脉瘤：胸/腹主动脉瘤，常无症状直至破裂。\n- 主动脉夹层：A 型（升主动脉）、B 型（降主动脉）。\n- 主动脉缩窄：先天狭窄，常伴高血压。\n- 主动脉炎：炎症性，如大动脉炎。",
                "treatment": "急性夹层需紧急手术。药物控制血压（β阻滞剂）；血管内支架或外科置换。预防严格控压、戒烟、定期影像筛查高危者、遗传咨询。"
            },
        }
        
        for name, info in diseases.items():
            expander_title = f"{info['emoji']} {name}"
            
            with st.expander(expander_title, expanded=False):
                st.markdown(f"<h4 style='color:{info['color']}; margin-top:0;'>{name}</h4>", unsafe_allow_html=True)
                
                col_img, col_text = st.columns([1, 2])
                with col_img:
                    if info.get("file"):
                        try:
                            st.image(f"picture/{info['file']}", use_container_width=True,
                                     caption=f"{name} 典型影像示意")
                        except Exception as e:
                            st.caption("📷 (图片加载失败，请检查路径)")
                    
                    if "extra_img" in info:
                        try:
                            st.image(f"picture/{info['extra_img']}", use_container_width=True,
                                     caption="肥厚型心肌病 典型影像示意")
                        except Exception as e:
                            st.caption("📷 (肥厚型心肌病图片未找到)")
                
                with col_text:
                    # 为子 Tab 也加上 Icon
                    sub_tabs = st.tabs(["📋 概述与因素", "🔍 症状与亚型", "💊 治疗与预防"])
                    
                    with sub_tabs[0]:
                        st.markdown("##### 📝 概述")
                        st.write(info.get("overview", ""))
                        
                        st.markdown("##### ⚠️ 引起因素")
                        st.write(info.get("causes", ""))
                        
                    with sub_tabs[1]:
                        st.markdown("##### 🚨 症状")
                        st.write(info.get("symptoms", "暂无症状信息"))
                        
                        st.markdown("##### 🔬 亚型")
                        st.write(info.get("subtypes", ""))
                        
                    with sub_tabs[2]:
                        st.markdown("##### 💉 治疗与预防")
                        st.write(info.get("treatment", "暂无治疗与预防信息"))
    
    # ── Tab 3：智能问答 ───────────────────────────────────────────────
    with tab_chat:
        st.markdown('<div class="section-title">向我提问</div>', unsafe_allow_html=True)
        st.markdown('<p class="sub-desc">咨询心血管相关疑问，获取专业解答</p>', unsafe_allow_html=True)
        
        st.markdown("**💡 示例问题**：")
        examples = [
            "房颤的抗凝治疗指征是什么？",
            "高血压 3 级应该首选哪类降压药？",
            "急性心肌梗死溶栓的黄金时间窗口？",
            "扩张型心肌病最常见的基因突变是？",
            "主动脉夹层 Stanford 分型怎么选手术方式？"
        ]
        cols = st.columns(5)
        for i, q in enumerate(examples):
            if cols[i].button(q, key=f"q_{i}", use_container_width=True):
                st.session_state["chat_input"] = q
                st.rerun()
        
        if "knowledge_chat" not in st.session_state:
            st.session_state.knowledge_chat = [{"role":"assistant", "content":"我是心血管知识助手，请问您的问题？"}]
        
        for msg in st.session_state.knowledge_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        default = st.session_state.get("chat_input", "")
        prompt = st.chat_input("请输入您的问题...", key="knowledge_prompt")
        if default:
            prompt = default
            if "chat_input" in st.session_state:
                del st.session_state["chat_input"]
        
        if prompt:
            st.session_state.knowledge_chat.append({"role":"user", "content":prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("思考中..."):
                try:
                    resp = client.chat.completions.create(
                        model="qwen-max",
                        messages=st.session_state.knowledge_chat,
                        temperature=0.6,
                        max_tokens=1200
                    )
                    answer = resp.choices[0].message.content
                    st.session_state.knowledge_chat.append({"role":"assistant", "content":answer})
                    with st.chat_message("assistant"):
                        st.markdown(answer)
                except Exception as e:
                    st.error(f"抱歉，回答失败：{str(e)}")

if __name__ == "__main__":
    main()