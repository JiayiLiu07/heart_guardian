# pages/p01_profile.py
import streamlit as st, pandas as pd, os, base64, io
from components.top_nav import render_nav
st.session_state.current_page = "profile"
render_nav()
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from utils.api import client

st.markdown("<style>section[data-testid='stSidebar'] {display: none !important;}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
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
    return {'cardio_subtypes':[],'gender':'男','age':30,'height':170.0,'weight':70.0,'waist':80.0,'sleep_hours':8.0,'exercise_min':150}
def save_profile_data(uid, data):
    pd.DataFrame([data]).to_csv(f"{USERS_FOLDER}/{uid}_profile.csv", index=False, encoding='utf-8')

if 'profile_data' not in st.session_state:
    st.session_state.profile_data = load_profile_data(user_id)
profile = st.session_state.profile_data

# ----- Step 条 -----
cols = st.columns(3)
for i, txt in enumerate(["基本信息", "亚型档案", "AI 报告"]):
    cls = ""
    if 'step' in st.session_state and st.session_state.step == i+1:
        cls = " step-active"
    cols[i].markdown(f'<div class="step-bar{cls}"></div><div style="text-align:center;color:#e1f5fe;">{txt}</div>', unsafe_allow_html=True)

if 'step' not in st.session_state:
    st.session_state.step = 1
step = st.session_state.step

if step == 1:
    st.subheader("① 基本信息")
    c1, c2 = st.columns(2)
    with c1:
        profile['gender'] = st.selectbox("性别", ["男", "女"], index=0 if profile.get('gender')=='男' else 1)
        profile['age'] = st.number_input("年龄（岁）", 18, 120, int(profile.get('age', 30)))
        profile['height'] = st.number_input("身高（cm）", 100.0, 250.0, float(profile.get('height', 170.0)), step=0.5)
        profile['weight'] = st.number_input("体重（kg）", 30.0, 200.0, float(profile.get('weight', 70.0)), step=0.5)
    with c2:
        profile['waist'] = st.number_input("腰围（cm）", 50.0, 200.0, float(profile.get('waist', 80.0)), step=0.5)
        profile['sleep_hours'] = st.slider("平均睡眠（小时）", 4.0, 12.0, float(profile.get('sleep_hours', 8.0)), step=0.5)
        profile['exercise_min'] = st.number_input("每周运动（分钟）", 0, 840, int(profile.get('exercise_min', 150)), step=30)
    # BMI 仪表盘
    if profile['height'] and profile['weight']:
        bmi = profile['weight'] / ((profile['height'] / 100) ** 2)
        status = "偏瘦" if bmi < 18.5 else "正常" if bmi < 25 else "超重" if bmi < 30 else "肥胖"
        st.markdown(f'<div class="bmi-gauge"><div class="gauge-value">{bmi:.1f}</div><div class="gauge-label">{status}</div></div>', unsafe_allow_html=True)
    if st.button("下一步 ➡️", type="primary"):
        st.session_state.step = 2
        save_profile_data(user_id, profile)
        st.rerun()

if step == 2:
    st.subheader("② 亚型档案")
    subtype_map = json.load(open("assets/subtype_dict.json")) if os.path.exists("assets/subtype_dict.json") else {}
    selected_sub = profile.get("cardio_subtypes", [])
    cols = st.columns(4)
    for i, (k, v) in enumerate(subtype_map.items()):
        with cols[i % 4]:
            if st.checkbox(f"{v['icon']} {v['label']}", value=k in selected_sub, key=k):
                if k not in selected_sub: selected_sub.append(k)
            else:
                if k in selected_sub: selected_sub.remove(k)
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

if step == 3:
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
            on_click=None,
            type="primary",
            disabled=False,
            use_container_width=True
        )

st.markdown('<div style="height:70px"></div>', unsafe_allow_html=True)