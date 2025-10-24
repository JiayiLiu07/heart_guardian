import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.markdown("""
<style>
section[data-testid='stSidebar'] {display: none !important;}
.block-container {padding-top: 80px !important; margin-top: 0 !important;}
.cyber-title{font-size:2.4rem;font-weight:700;background:linear-gradient(90deg,#00e5ff,#2979ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 4s ease infinite;background-size:200% 200%;}
@keyframes gradientShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.neon-chart{background:radial-gradient(circle at center,rgba(0,229,255,.08) 0%,transparent 70%);border:1px solid rgba(0,229,255,.4);border-radius:16px;padding:1rem;box-shadow:0 0 20px rgba(0,229,255,.35);}
.holo-card{display:flex;align-items:center;gap:.8rem;background:linear-gradient(135deg,rgba(0,229,255,.05) 0%,rgba(41,121,255,.05) 100%);border-left:4px solid #00e5ff;border-radius:12px;padding:1rem 1.2rem;margin:.8rem 0;backdrop-filter:blur(6px);transition:all .3s ease;}
.holo-card:hover{transform:translateX(6px);box-shadow:0 0 15px rgba(0,229,255,.45)}
.holo-icon{font-size:1.6rem}
.holo-text{color:#000000;font-weight:500}
.health-tip{background:rgba(255,82,82,.08);border-left:4px solid #ff5252;border-radius:12px;padding:1rem 1.2rem;margin:.8rem 0;backdrop-filter:blur(6px);}
.health-tip-icon{font-size:1.4rem;margin-right:.6rem}
</style>
""", unsafe_allow_html=True)

df = pd.read_csv("data/cardio_train.csv", sep=";")
df["age_year"] = (df["age"] / 365.25).round().astype(int)

st.markdown('<div class="cyber-title">❤️ 心血管科普展览馆</div>', unsafe_allow_html=True)
st.markdown("**仅基于公开数据集** `cardio_train.csv` **告诉你：心血管被什么害、怎么防**")

tabs = st.tabs(["🔍 高危因素", "📈 血压迷踪", "🍏 生活方式", "⚠️ 健康警示"])

with tabs[0]:
    st.markdown("#### ① 高危因素排行榜")
    importances = df.corr()['cardio'].abs().sort_values(ascending=False)[1:11]
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0f1629'); ax.set_facecolor('#0f1629')
    sns.barplot(x=importances.values, y=importances.index, hue=importances.index, ax=ax, palette='Blues_r', legend=False)
    ax.set_title('Top 10 Risk Factors', color='#e1f5fe')
    for sp in ax.spines.values(): sp.set_color('#e1f5fe')
    ax.tick_params(colors='#e1f5fe')
    buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches='tight'); buf.seek(0)
    st.image(buf, width='stretch')
    st.markdown("""
    <div class="holo-card">
      <div class="holo-icon">⚠️</div>
      <div class="holo-text">高血压、胆固醇和年龄是心血管疾病的三大驱动因素。控制血压和胆固醇可降低 40% 风险！建议定期体检，监测收缩压（ap_hi）和舒张压（ap_lo），并保持健康饮食。</div>
    </div>
    """, unsafe_allow_html=True)

with tabs[1]:
    st.markdown("#### ② 血压迷踪")
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0f1629'); ax.set_facecolor('#0f1629')
    sns.scatterplot(data=df, x='age_year', y='ap_hi', hue='cardio', ax=ax, palette={0:'#00e5ff',1:'#ff5252'})
    ax.set_title('Age vs Systolic BP', color='#e1f5fe')
    for sp in ax.spines.values(): sp.set_color('#e1f5fe')
    ax.tick_params(colors='#e1f5fe')
    buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches='tight'); buf.seek(0)
    st.image(buf, width='stretch')
    st.markdown("""
    <div class="holo-card">
      <div class="holo-icon">📈</div>
      <div class="holo-text">收缩压（ap_hi）超过 140 mmHg 或舒张压（ap_lo）超过 90 mmHg 时，心血管风险显著增加。建议减少盐摄入，避免压力，必要时咨询医生使用降压药。</div>
    </div>
    """, unsafe_allow_html=True)

with tabs[2]:
    st.markdown("#### ③ 生活方式分析")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_facecolor('#0f1629'); ax.set_facecolor('#0f1629')
        sns.countplot(data=df, x='smoke', hue='cardio', ax=ax, palette={0:'#00e5ff',1:'#ff5252'})
        ax.set_title('Smoking vs Cardiovascular', color='#e1f5fe')
        for sp in ax.spines.values(): sp.set_color('#e1f5fe')
        ax.tick_params(colors='#e1f5fe')
        buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches='tight'); buf.seek(0)
        st.image(buf, width='stretch')
    with col2:
        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_facecolor('#0f1629'); ax.set_facecolor('#0f1629')
        sns.countplot(data=df, x='alco', hue='cardio', ax=ax, palette={0:'#00e5ff',1:'#ff5252'})
        ax.set_title('Alcohol vs Cardiovascular', color='#e1f5fe')
        for sp in ax.spines.values(): sp.set_color('#e1f5fe')
        ax.tick_params(colors='#e1f5fe')
        buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches='tight'); buf.seek(0)
        st.image(buf, width='stretch')
    with col3:
        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_facecolor('#0f1629'); ax.set_facecolor('#0f1629')
        sns.countplot(data=df, x='active', hue='cardio', ax=ax, palette={0:'#00e5ff',1:'#ff5252'})
        ax.set_title('Exercise vs Cardiovascular', color='#e1f5fe')
        for sp in ax.spines.values(): sp.set_color('#e1f5fe')
        ax.tick_params(colors='#e1f5fe')
        buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches='tight'); buf.seek(0)
        st.image(buf, width='stretch')
    st.markdown("""
    <div class="holo-card">
      <div class="holo-icon">🏃</div>
      <div class="holo-text">每周 150 min 中等强度运动，心血管事件风险降低 30%！运动能改善心肺功能，降低血压和胆固醇水平。建议从散步、游泳或骑行开始，坚持规律锻炼。同时，避免吸烟和过量饮酒，这些习惯会加速血管损伤，增加血栓风险。</div>
    </div>
    """, unsafe_allow_html=True)

with tabs[3]:
    st.markdown("#### ④ 年龄警示线")
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0f1629'); ax.set_facecolor('#0f1629')
    sns.histplot(data=df, x='age_year', hue='cardio', ax=ax, palette={0:'#00e5ff',1:'#ff5252'}, element='step', fill=True)
    ax.set_title('Age Distribution vs Cardiovascular', color='#e1f5fe')
    ax.axvline(45, color='#ff5252', linestyle='--', linewidth=2)
    ax.text(46, ax.get_ylim()[1]*0.9, 'Risk spikes at 45', color='#ff5252', fontsize=10)
    for sp in ax.spines.values(): sp.set_color('#e1f5fe')
    ax.tick_params(colors='#e1f5fe')
    buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches='tight'); buf.seek(0)
    st.image(buf, width='stretch')
    st.markdown("""
    <div class="health-tip">
      <span class="health-tip-icon">⚠️</span>
      45 岁后心血管风险陡升，建议每年做<strong>心脏彩超 + 冠脉 CT</strong>！随着年龄增长，血管弹性下降，容易积累斑块。预防包括均衡饮食、控制体重、定期筛查高血压和高脂血症，早发现早治疗可有效降低发病率。
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="height:80px"></div>', unsafe_allow_html=True)