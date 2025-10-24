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
import json

df = pd.read_csv("data/cardio_train.csv", sep=";")

def generate_viz_image_and_desc(viz_type):
    buf = BytesIO()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if viz_type == "age_bp_scatter":
        sns.scatterplot(data=df, x='age', y='ap_hi', hue='cardio', ax=ax)
        ax.set_title('Age vs Blood Pressure Scatter')
        prompt = "基于 cardio_train.csv 数据集，描述年龄与血压分布散点图。图中标签用英文。提供中文关键数据洞察，使用 markdown 加粗重点。"
    elif viz_type == "disease_distribution":
        sns.countplot(data=df, x='cardio', hue='cardio', ax=ax, palette={0:'#00e5ff',1:'#ff5252'}, legend=False)
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
    subtype_map = json.load(open("assets/subtype_dict.json"))
    for key, value in kb.items():
        if key == user_disease:
            st.markdown(f'<div class="neon-tree-content">{value}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="neon-tree-content">{key}: {value}</div>', unsafe_allow_html=True)

def render():
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
        render_knowledge_tree({member.name: member.value for member in DISEASE_ENUM if member.name != 'none'}, user_disease)

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
                st.image(f"data:image/png;base64,{img_base64}", width='stretch')
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

st.markdown("""
<style>
.block-container {padding-top: 80px !important; margin-top: 0 !important;}
.neon-tree-content{
  border-left:2px solid #00e5ff;
  padding-left:1rem;margin-top:.5rem;
  background:rgba(0,229,255,.05);
  border-radius:0 8px 8px 0;
}
.glass-viz{
  background:rgba(255,255,255,.06);
  border:1px solid rgba(0,229,255,.3);
  border-radius:12px;padding:1rem;
  backdrop-filter:blur(8px);margin:1rem 0;
}
.viz-desc{
  margin-top:.5rem;font-size:.9rem;color:rgba(225,245,254,.8)
}
</style>
""", unsafe_allow_html=True)
st.markdown('<div style="height:80px"></div>', unsafe_allow_html=True)