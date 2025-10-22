# pages/01_overview.py
import streamlit as st
import pandas as pd
from pages.p01_profile import load_profile_data
from utils.disease_dict import DISEASE_ENUM
from utils.api import client
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import base64

# 统一风格，与p00_intro.py匹配
st.markdown("""
<style>
:root {{ --primary: #1a237e; --accent: #00e5ff; --danger: #ff5252; --bg: #0f1629; --text: #e1f5fe; --shadow: rgba(0,229,255,.3); }}
body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; }}
.hero-section {{
    background: linear-gradient(135deg, var(--primary) 0%, #283593 50%, #3949ab 100%);
    padding: 4rem 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px var(--shadow);
    backdrop-filter: blur(10px);
}}
.hero-section::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.3;
}}
.hero-title {{
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
    text-shadow: 0 0 10px var(--shadow);
}}
.hero-subtitle {{
    font-size: 1.5rem;
    margin-bottom: 2rem;
    opacity: 0.9;
    font-weight: 300;
    text-shadow: 0 0 5px var(--shadow);
}}
@keyframes gradientAnimation {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
.feature-card {{
    background: rgba(255, 255, 255, 0.05);
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
    border: 1px solid var(--shadow);
    transition: all 0.3s ease;
    cursor: pointer;
    backdrop-filter: blur(10px);
}}
.feature-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 15px 35px var(--shadow);
}}
.skeleton {{height:300px;background:linear-gradient(90deg, #333 25%, #444 50%, #333 75%);background-size:200% 100%;animation:skeleton-pulse 1.5s infinite;border-radius:12px;}}
@keyframes skeleton-pulse {{0%{background-position:200% 0}100%{background-position:-200% 0}}}
.desc-card {{background: rgba(41,121,255,.1); border-left: 4px solid var(--accent); padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px var(--shadow); margin-top: 1rem;}}
</style>
""", unsafe_allow_html=True)

df = pd.read_csv("data/cardio_train.csv", sep=";")

def generate_plot_image(prompt, key):
    place = st.empty()
    place.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)
    try:
        # Use VLLM to get description in Chinese
        resp = client.chat.completions.create(model="qwen-turbo", messages=[{"role": "user", "content": prompt + " Provide a Chinese description with key data insights. Use markdown for formatting, bold key points. Do not mention access to files or generating visualizations."}], stream=False)
        desc = resp.choices[0].message.content.strip()

        # Generate plot using matplotlib based on type
        buf = BytesIO()
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor('#0f1629')
        ax.patch.set_facecolor('#0f1629')
        ax.spines['top'].set_color('#e1f5fe')
        ax.spines['bottom'].set_color('#e1f5fe')
        ax.spines['left'].set_color('#e1f5fe')
        ax.spines['right'].set_color('#e1f5fe')
        ax.tick_params(colors='#e1f5fe')
        ax.title.set_color('#e1f5fe')
        ax.xaxis.label.set_color('#e1f5fe')
        ax.yaxis.label.set_color('#e1f5fe')
        
        if "feature importance" in prompt.lower():
            importances = df.corr()['cardio'].abs().sort_values(ascending=False)[1:16]
            sns.barplot(x=importances.values, y=importances.index, ax=ax, palette='Blues_r')
            ax.set_title('Top 15 Feature Importance', color='#e1f5fe')
            ax.set_xlabel('Importance', color='#e1f5fe')
            ax.set_ylabel('Features', color='#e1f5fe')
            ax.grid(color='rgba(0,229,255,.3)')
        elif "correlation heatmap" in prompt.lower():
            corr = df.corr()
            sns.heatmap(corr, ax=ax, cmap='coolwarm', annot=True, fmt=".2f", annot_kws={"color": "black"})
            ax.set_title('Correlation Heatmap', color='#e1f5fe')
        elif "partial dependence" in prompt.lower():
            ap_hi_range = range(80, 200, 10)
            risk = [df[(df['ap_hi'] >= v-5) & (df['ap_hi'] < v+5)]['cardio'].mean() for v in ap_hi_range]
            sns.lineplot(x=ap_hi_range, y=risk, ax=ax, color='#00e5ff', marker='o')
            ax.set_title('Partial Dependence of ap_hi on Risk', color='#e1f5fe')
            ax.set_xlabel('ap_hi', color='#e1f5fe')
            ax.set_ylabel('Risk', color='#e1f5fe')
            ax.grid(color='rgba(0,229,255,.3)')
        elif "feature distribution" in prompt.lower():
            sns.violinplot(data=df, x='cardio', y='age', ax=ax, palette='Blues', inner='quartile')
            ax.set_title('Feature Distribution (Age by Cardio)', color='#e1f5fe')
            ax.set_xlabel('Cardio', color='#e1f5fe')
            ax.set_ylabel('Age', color='#e1f5fe')
        
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        place.empty()
        st.image(f"data:image/png;base64,{img_base64}", use_container_width=True)
        st.markdown(f'<div class="desc-card">{desc}</div>', unsafe_allow_html=True)
    except Exception as e:
        place.error(f"生成失败: {e}")
    if st.button("🔁 重新生成", key=key):
        generate_plot_image(prompt, key)

def render():
    st.markdown("<style>section[data-testid='stSidebar'], .stSidebar, [data-testid='collapsedControl'], #MainMenu, footer {display: none !important;}</style>", unsafe_allow_html=True)

    st.markdown('<div class="hero-section"><h1 class="hero-title">AI 风险总览</h1><p class="hero-subtitle">基于大数据 + 您的档案</p></div>', unsafe_allow_html=True)

    tabs = st.tabs(["特征重要性", "相关性热图", "血压依赖", "特征分布"])
    prompts = [
        "基于 cardio_train.csv 数据集，描述前 15 个平均 SHAP 值的水平条形图。图中标签用英文。提供中文关键数据洞察，使用 markdown 加粗重点。",
        "基于 cardio_train.csv 数据集，描述数值特征的相关性热图。图中标签用英文。提供中文关键数据洞察，使用 markdown 加粗重点。",
        "基于 cardio_train.csv 数据集，描述 ap_hi 对风险的部分依赖关系。图中标签用英文。提供中文关键数据洞察，使用 markdown 加粗重点。",
        "基于 cardio_train.csv 数据集，描述前几个特征的 SHAP 蜂群图。图中标签用英文。提供中文关键数据洞察，使用 markdown 加粗重点。"
    ]
    titles = ["特征重要性", "相关性热图", "血压依赖", "特征分布"]
    for tab, prompt, title in zip(tabs, prompts, titles):
        with tab:
            generate_plot_image(prompt, title)

if __name__ == "__main__":
    render()