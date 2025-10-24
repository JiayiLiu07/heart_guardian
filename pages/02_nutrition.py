# pages/02_nutrition.py
import streamlit as st
import pandas as pd
import os
import re
import logging
from openai import OpenAI
from pages.p01_profile import load_profile_data
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Initialize session state
if "chart_history" not in st.session_state:
    st.session_state.chart_history = []
if "chart_summary" not in st.session_state:
    st.session_state.chart_summary = ""

def initialize_client(api_key):
    """Initialize OpenAI client"""
    return OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

def load_cardio_data():
    """Load cardio dataset"""
    try:
        cardio_path = "data/cardio_train.csv"
        if os.path.exists(cardio_path):
            df = pd.read_csv(cardio_path, sep=';')
            logging.info(f"Loaded cardio data: {df.shape}")
            return df
        else:
            st.error("🚨 数据集文件未找到: cardio_train.csv")
            return None
    except Exception as e:
        st.error(f"🚨 加载数据集失败: {e}")
        return None

def generate_chart_with_vllm(question, user_profile, cardio_df):
    """Generate chart description and analysis using VLLM"""
    
    # Prepare user context
    profile_context = f"""
    用户档案信息:
    - 姓名: {user_profile.get('name', '未填写')}
    - 年龄: {user_profile.get('age', '未填写')}岁
    - 性别: {user_profile.get('gender', '未填写')}
    - 身高: {user_profile.get('height', '未填写')}cm
    - 体重: {user_profile.get('weight', '未填写')}kg
    - 健康问题: {', '.join(user_profile.get('conditions', [])) if user_profile.get('conditions') else '无'}
    - 饮食目标: {user_profile.get('diet_goal', '未填写')}
    """
    
    # Dataset description
    dataset_info = """
    心血管数据集字段说明:
    - id: 患者ID
    - age: 年龄(天)
    - gender: 性别(1-女, 2-男)
    - height: 身高(cm)
    - weight: 体重(kg)
    - ap_hi: 收缩压
    - ap_lo: 舒张压
    - cholesterol: 胆固醇水平(1-正常, 2-高于正常, 3-远高于正常)
    - gluc: 血糖水平(1-正常, 2-高于正常, 3-远高于正常)
    - smoke: 是否吸烟(0-否, 1-是)
    - alco: 是否饮酒(0-否, 1-是)
    - active: 是否积极运动(0-否, 1-是)
    - cardio: 是否有心血管疾病(0-否, 1-是)
    """
    
    prompt = f"""
    你是一个专业的数据分析师和健康顾问。请根据用户的问题和心血管数据集，生成一个详细的图表描述和数据分析。

    {profile_context}
    
    {dataset_info}
    
    数据集样本数据:
    {cardio_df.head(3).to_string()}
    
    用户问题: {question}
    
    请按照以下格式回复:
    
    📊 **图表描述:**
    [详细描述应该生成的图表类型、展示的数据维度和关键洞察]
    
    📈 **数据分析:**
    [分析图表中展示的数据模式、趋势和统计信息]
    
    💡 **健康洞察:**
    [结合用户档案，提供个性化的健康建议]
    """
    
    try:
        client = initialize_client(st.session_state.get('api_key'))
        response = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        analysis = response.choices[0].message.content.strip()
        return analysis
    except Exception as e:
        logging.error(f"Error in VLLM request: {e}")
        return None

def show_ai_charts_page():
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.warning("请先登录")
        return

    user_profile = load_profile_data(user_id)
    cardio_df = load_cardio_data()
    
    if cardio_df is None:
        return

    st.markdown('<div class="hero"><h1>🍎 AI 营养分析</h1><p>个性化饮食建议，守护心血管健康</p></div>', unsafe_allow_html=True)
    
    # Search bar
    with st.container():
        st.markdown('<div class="chip-search">', unsafe_allow_html=True)
        col1, col2 = st.columns([8, 2])
        with col1:
            question = st.text_input("输入您的问题", placeholder="例如：低盐饮食对高血压的影响？")
        with col2:
            ask_button = st.button("🔍 提问", key="ask_chart")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick questions
    st.markdown('<div class="slider-track">', unsafe_allow_html=True)
    quick_questions = [
        "低盐饮食对高血压的影响？",
        "高胆固醇推荐哪些食物？",
        "适合心脏健康的运动？",
        "如何通过饮食降低血糖？"
    ]
    cols = st.columns(4)
    for i, q in enumerate(quick_questions):
        with cols[i]:
            if st.button(q, key=f"quick_q_{i}", type="secondary"):
                st.session_state["nutrition_question"] = q
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle question
    question_to_use = st.session_state.get("nutrition_question", question)
    if (ask_button or "nutrition_question" in st.session_state) and question_to_use:
        analysis = generate_chart_with_vllm(question_to_use, user_profile, cardio_df)
        if analysis:
            # Save to history
            st.session_state.chart_history.append({
                "question": question_to_use,
                "analysis": analysis,
                "timestamp": pd.Timestamp.now()
            })
            
            # Display analysis
            st.subheader("📋 分析报告")
            st.markdown(analysis)
            
            # Add some visual separators
            st.markdown("---")
            st.success("✅ 分析完成！")
        else:
            st.error("❌ 生成分析失败，请重试")
    
    # Display history
    if st.session_state.chart_history:
        st.subheader("🕒 历史查询")
        for i, item in enumerate(reversed(st.session_state.chart_history[-5:])):
            with st.expander(f"查询 {len(st.session_state.chart_history)-i}: {item['question'][:50]}...", expanded=False):
                st.markdown(item['analysis'])
    
    # Dataset overview
    with st.sidebar:
        st.subheader("📁 数据集概览")
        st.write(f"**总记录数:** {len(cardio_df):,}")
        st.write(f"**心血管疾病患者:** {cardio_df['cardio'].sum():,}")
        st.write(f"**数据集字段:** {len(cardio_df.columns)}个")
        
        st.subheader("💡 使用提示")
        st.info("""
        - 可以询问关于年龄、性别、血压等维度的分析
        - 结合您的个人档案获得个性化建议
        - 系统会基于真实心血管数据提供洞察
        """)

if __name__ == "__main__":
    show_ai_charts_page()

st.markdown("""
<style>
.block-container {padding-top: 80px !important; margin-top: 0 !important;}
.chip-search{
  display:flex;gap:.5rem;
  background:rgba(0,229,255,.05);border:1px solid rgba(0,229,255,.3);
  border-radius:12px;padding:.5rem .8rem;
}
.chip-search input{
  background:transparent;border:none;color:#e1f5fe;
}
.chip-search button{
  box-shadow:0 0 10px rgba(0,229,255,.45) !important;
}
.slider-track{
  display:flex;gap:1rem;overflow-x:auto;
  padding:1rem 0;
}
.slider-track::-webkit-scrollbar{height:6px}
.slider-track::-webkit-scrollbar-thumb{background:#00e5ff;border-radius:3px}
.glass-dish{
  min-width:160px;background:rgba(255,255,255,.06);
  border:1px solid rgba(0,229,255,.3);border-radius:12px;
  padding:1rem;backdrop-filter:blur(8px);
  text-align:center;transition:all .3s ease;
}
.glass-dish:hover{transform:translateY(-4px);box-shadow:0 8px 20px rgba(0,229,255,.35)}
.dish-name{font-weight:600;color:#e1f5fe}
.dish-cal{font-size:.8rem;color:rgba(225,245,254,.7)}
.sub-tag{
  background:linear-gradient(90deg,#ff5252,#ff867c);
  color:#fff;font-size:.7rem;padding:.2rem .5rem;
  border-radius:10px;margin-left:.5rem;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<div style="height:80px"></div>', unsafe_allow_html=True)