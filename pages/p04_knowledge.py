# pages/p04_knowledge.py
import streamlit as st
from utils.disease_dict import DISEASE_ENUM
from utils.api import client
from pages.p01_profile import load_profile_data
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import pandas as pd

df = pd.read_csv("data/cardio_train.csv", sep=";")

def generate_viz_image_and_desc(viz_type):
    buf = BytesIO()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if viz_type == "age_bp_scatter":
        sns.scatterplot(data=df, x='age', y='ap_hi', hue='cardio', ax=ax)
        ax.set_title('Age vs Blood Pressure Scatter')
        prompt = "基于 cardio_train.csv 数据集，描述年龄与血压分布散点图。图中标签用英文。提供中文关键数据洞察，使用 markdown 加粗重点。"
    elif viz_type == "disease_distribution":
        sns.countplot(data=df, x='cardio', ax=ax)
        ax.set_title('Disease Distribution')
        prompt = "基于 cardio_train.csv 数据集，描述疾病分布柱状图。图中标签用英文。提供中文关键数据洞察，使用 markdown 加粗重点。"
    elif viz_type == "bmi_chol_heatmap":
        df['bmi'] = df['weight'] / ((df['height']/100)**2)
        pivot = df.pivot_table(index='cholesterol', columns='cardio', values='bmi', aggfunc='mean')
        sns.heatmap(pivot, ax=ax, cmap='coolwarm', annot=True)
        ax.set_title('BMI vs Cholesterol Heatmap')
        prompt = "基于 cardio_train.csv 数据集，描述 BMI 与胆固醇热图。图中标签用英文。提供中文关键数据洞察，使用 markdown 加粗重点。"
    elif viz_type == "feature_correlation":
        corr = df.corr()
        sns.heatmap(corr, ax=ax, cmap='coolwarm', annot=True, fmt=".2f")
        ax.set_title('Feature Correlation')
        prompt = "基于 cardio_train.csv 数据集，描述特征相关性热图。图中标签用英文。提供中文关键数据洞察，使用 markdown 加粗重点。"
    
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    # Get description from VLLM
    resp = client.chat.completions.create(model="qwen-turbo", messages=[{"role": "user", "content": prompt}], stream=False)
    desc = resp.choices[0].message.content.strip()
    
    return img_base64, desc

def ask_vllm(question):
    try:
        resp = client.chat.completions.create(model="qwen-turbo", messages=[{"role": "user", "content": f"心脏健康知识问答: {question}"}])
        return resp.choices[0].message.content
    except Exception as e:
        return f"AI 错误: {e}"

def render_knowledge_tree(kb, user_disease):
    if user_disease:
        st.markdown(f'<div class="tree-root">{user_disease}</div>', unsafe_allow_html=True)
    for key, value in kb.items():
        with st.expander(f"{value['label']} {value.get('icon', '❤️')}", expanded=key == user_disease):
            st.markdown(value.get('content', '暂无内容'))

def render():
    st.markdown("<style>section[data-testid='stSidebar'], .stSidebar, [data-testid='collapsedControl'], #MainMenu, footer {display: none !important;}</style>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    :root{--p:#1a237e;--a:#00e5ff;--bg:#0f1629;}
    body{background:var(--bg);color:#e1f5fe;}
    .hero{background:linear-gradient(135deg,var(--p),#283593,#3949ab);padding:3rem 1rem;border-radius:15px;text-align:center;color:white;margin:2rem 0;}
    .tree-root {border:2px solid var(--a);background:rgba(255,255,255,.1);padding:1rem;border-radius:8px;}
    .viz-card {background:rgba(255,255,255,.1);backdrop-filter:blur(10px);border:1px solid rgba(0,229,255,.2);border-radius:16px;padding:1.5rem;margin:1rem 0;}
    .source-card {background:rgba(41,121,255,.2);border-radius:12px;padding:1rem;}
    .hot-chip {background:var(--a);color:var(--p);padding:0.5rem 1rem;border-radius:20px;margin:0.5rem;display:inline-block;cursor:pointer;}
    .hot-chip:hover {background:#2979ff;}
    .desc-card {background: #f0f7ff; border-left: 4px solid #00e5ff; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,229,255,0.1);}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hero"><h1>心脏健康知识库</h1><p>探索专业知识与数据洞察</p></div>', unsafe_allow_html=True)

    user_id = st.session_state.get('user_id')
    user_data = load_profile_data(user_id)
    user_disease = user_data.get('cardio_diseases', ['无'])[0]

    search_term = st.text_input("搜索知识库", placeholder="输入关键词，如'高血压'")
    if search_term:
        st.info(f"搜索结果: {search_term}")

    col1, col2 = st.columns([3,7])
    with col1:
        st.subheader("目录树")
        render_knowledge_tree({k.name: DISEASE_ENUM[k].value for k in DISEASE_ENUM if k.name != 'none'}, user_disease)

    with col2:
        st.subheader("详情 / 洞察")
        tab1, tab2 = st.tabs(["文章详情", "数据洞察"])
        with tab1:
            st.info("选择左侧目录查看详情")
        with tab2:
            viz_funcs = ["age_bp_scatter", "disease_distribution", "bmi_chol_heatmap", "feature_correlation"]
            captions = ["年龄与血压分布", "疾病分布", "BMI与胆固醇热图", "特征相关性"]
            for func, caption in zip(viz_funcs, captions):
                st.markdown('<div class="viz-card">', unsafe_allow_html=True)
                img_base64, desc = generate_viz_image_and_desc(func)
                st.image(f"data:image/png;base64,{img_base64}")
                st.markdown(f'<p>{caption}</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="desc-card">{desc}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("即时问 VLLM")
    question = st.text_input("提问", placeholder="什么是白大衣高血压？")
    if st.button("发送"):
        answer = ask_vllm(question)
        st.markdown(f'<div class="source-card">{answer}</div>', unsafe_allow_html=True)

    st.markdown('<p>热门提问：</p>', unsafe_allow_html=True)
    hot_questions = ["什么是白大衣高血压？", "HCM 可以打篮球吗？"]
    for q in hot_questions:
        if st.button(q, type="secondary", key=q):
            st.text_input("提问", value=q, disabled=True)
            st.button("发送", disabled=True)
            answer = ask_vllm(q)
            st.markdown(f'<div class="source-card">{answer}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    render()