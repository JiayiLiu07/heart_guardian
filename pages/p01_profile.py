# pages/p01_profile.py
import streamlit as st
import pandas as pd
import os
import base64
import io
from utils.api import client
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

st.markdown("""
<style>
section[data-testid='stSidebar'] {display: none !important;}
.block-container {padding-top: 80px !important; margin-top: 0 !important;}
.cyber-title{font-size:2.4rem;font-weight:700;background:linear-gradient(90deg,#00e5ff,#2979ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 4s ease infinite;background-size:200% 200%;}
@keyframes gradientShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.step-bar{height:6px;background:rgba(0,229,255,.15);border-radius:3px;margin:1rem 0}
.step-active{height:100%;width:33%;background:#00e5ff;border-radius:3px;box-shadow:0 0 10px #00e5ff}
.bmi-gauge{width:140px;height:140px;margin:auto;border:8px solid rgba(0,229,255,.2);border-top:8px solid #00e5ff;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;animation:spin 2s linear infinite;}
@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
.gauge-value{font-size:2rem;font-weight:700;color:#e1f5fe}
.gauge-label{font-size:.9rem;color:rgba(225,245,254,.8)}
.holo-report{background:linear-gradient(135deg,rgba(0,229,255,.05) 0%,rgba(41,121,255,.05) 100%);border:1px solid rgba(0,229,255,.4);border-radius:16px;padding:1.5rem;backdrop-filter:blur(10px);margin:1rem 0;}
.download-btn{background:linear-gradient(90deg,#ff5252,#ff867c);color:#fff;border:none;padding:.8rem 1.2rem;border-radius:20px;font-weight:600;box-shadow:0 0 15px rgba(255,82,82,.4);transition:all .3s ease;}
.download-btn:hover{transform:translateY(-2px);box-shadow:0 0 25px rgba(255,82,82,.6)}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="cyber-title">🧬 私人健康舱</div>', unsafe_allow_html=True)
st.markdown("3 步完成档案，AI 生成专属心血管亚型报告")

user_id = st.session_state.get('user_id')
if not user_id:
    st.warning("请先登录")
    st.stop()

USERS_FOLDER = 'users'
os.makedirs(USERS_FOLDER, exist_ok=True)

def load_profile_data(uid):
    path = f"{USERS_FOLDER}/{uid}_profile.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, encoding='utf-8')
        return df.iloc[0].to_dict()
    return {'cardio_subtypes':[],'gender':'男','age':30,'height':170.0,'weight':70.0,'waist':80.0,'sleep_hours':8.0}

def save_profile_data(uid, profile):
    path = f"{USERS_FOLDER}/{uid}_profile.csv"
    df = pd.DataFrame([profile])
    df.to_csv(path, index=False, encoding='utf-8')

if 'step' not in st.session_state:
    st.session_state.step = 1

profile = load_profile_data(user_id)
if not profile:
    profile = {'cardio_subtypes':[],'gender':'男','age':30,'height':170.0,'weight':70.0,'waist':80.0,'sleep_hours':8.0}

if st.session_state.step == 1:
    st.subheader("① 基本信息")
    profile['name'] = st.text_input("姓名", value=profile.get('name', ''))
    profile['gender'] = st.selectbox("性别", ["男", "女"], index=0 if profile.get('gender') == '男' else 1)
    profile['age'] = st.number_input("年龄", min_value=18, max_value=120, value=profile.get('age', 30))
    if st.button("下一步 ➡️"):
        st.session_state.step = 2
        st.rerun()

if st.session_state.step == 2:
    st.subheader("② 健康数据")
    profile['height'] = st.number_input("身高 (cm)", min_value=100.0, max_value=250.0, value=profile.get('height', 170.0))
    profile['weight'] = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0, value=profile.get('weight', 70.0))
    profile['waist'] = st.number_input("腰围 (cm)", min_value=50.0, max_value=150.0, value=profile.get('waist', 80.0))
    profile['sleep_hours'] = st.number_input("平均睡眠时间 (小时)", min_value=0.0, max_value=24.0, value=profile.get('sleep_hours', 8.0))
    subtype_map = json.load(open("assets/subtype_dict.json"))
    selected_sub = profile.get('cardio_subtypes', [])
    for k, v in subtype_map.items():
        if st.checkbox(f"{v['icon']} {v['label']}", key=k):
            if k not in selected_sub:
                selected_sub.append(k)
        else:
            if k in selected_sub:
                selected_sub.remove(k)
    profile["cardio_subtypes"] = selected_sub
    col1, col2 = st.columns(2)
    with col1:
        if st.button("上一步 ⬅️"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("完成建档 ✅", type="primary"):
            save_profile_data(user_id, profile)
            st.session_state.step = 3
            st.rerun()

if st.session_state.step == 3:
    st.success("档案已保存！🎉")
    st.subheader("③ AI 亚型报告")
    if st.button("🔍 生成报告", type="primary"):
        with st.spinner("AI 分析中..."):
            prompt = f"基于用户档案{profile}，分析亚型风险，给出 200 字通俗建议，加 emoji，引用《2023 Braunwald’s Heart Disease》。"
            resp = client.chat.completions.create(model="qwen-turbo", messages=[{"role": "user", "content": prompt}])
            report_txt = resp.choices[0].message.content
        st.markdown(f'<div class="holo-report">{report_txt}</div>', unsafe_allow_html=True)

        # 生成 PDF（内存 base64）
        pdf_buf = io.BytesIO()
        with PdfPages(pdf_buf) as pdf:
            fig = plt.figure(figsize=(8, 11))
            fig.patch.set_facecolor('#0f1629')
            plt.text(0.5, 0.9, "CardioGuard AI 亚型报告", color='#00e5ff', fontsize=20, ha='center', transform=fig.transFigure)
            plt.text(0.5, 0.8, f"用户：{profile.get('name','匿名')}", color='#e1f5fe', fontsize=14, ha='center', transform=fig.transFigure)
            plt.text(0.5, 0.7, f"亚型：{', '.join([subtype_map[s]['label'] for s in profile['cardio_subtypes']])}", color='#e1f5fe', fontsize=12, ha='center', transform=fig.transFigure)
            plt.text(0.5, 0.6, "AI 建议：", color='#00e5ff', fontsize=12, ha='center', transform=fig.transFigure)
            plt.text(0.5, 0.5, report_txt, color='#e1f5fe', fontsize=10, ha='center', va='top', wrap=True, transform=fig.transFigure)
            plt.axis('off')
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
        pdf_buf.seek(0)
        b64_pdf = base64.b64encode(pdf_buf.read()).decode()
        st.download_button(
            label="📥 下载 PDF 报告",
            data=base64.b64decode(b64_pdf),
            file_name=f"cardio_report_{user_id}.pdf",
            mime="application/pdf",
            help="内含亚型分析及 AI 建议",
            key="download_pdf",
            type="primary",
            width='stretch'
        )

st.markdown('<div style="height:80px"></div>', unsafe_allow_html=True)