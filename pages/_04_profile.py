# pages/_04_profile.py
import streamlit as st
import pandas as pd
from utils.database import UserManager, RedisManager
from utils.config import Config
from utils.visualization import create_3d_scatter
import hashlib
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
import qrcode
import random
import plotly.express as px
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

st.set_page_config(page_title="心守护 - 我的档案", page_icon="📋", layout="wide", initial_sidebar_state="expanded")

try:
    pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
except Exception:
    st.warning("未找到 SimSun 字体，将使用默认字体")

st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    .main { background-color: #f9fafb; padding: 2rem; }
    .card { background: linear-gradient(145deg, #ffffff, #f1f5f9); border-radius: 12px; padding: 18px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,30,0.1); transition: transform 0.25s; }
    .card:hover { box-shadow: 0 6px 16px rgba(0,0,30,0.15); transform: scale(1.02); }
    .task-card { display: flex; align-items: center; justify-content: between; padding: 10px; border-bottom: 1px solid #e5e7eb; }
    .progress-circle { position: relative; width: 32px; height: 32px; }
    .glass-card { backdrop-filter: blur(10px); background: rgba(255,255,255,0.7); border: 1px solid rgba(255,255,255,0.3); }
    .btn { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 min-h-[44px] font-semibold transition-colors duration-200; }
</style>
""", unsafe_allow_html=True)

def generate_cardio_rehab_plan(subtype, workload, support):
    tasks = {
        'WCHT': ["每日步行30分钟", "每周3次有氧运动", "低钠饮食"],
        'MHT': ["每周5次中等强度运动", "控制体重", "低钠饮食"],
        'HFrEF': ["每日步行15分钟", "每周2次轻度有氧运动", "严格低钠低液体饮食"],
        'CAD': ["每周4次有氧运动", "戒烟", "低脂饮食"],
        'AF': ["每日步行20分钟", "避免咖啡因", "低钠饮食"],
        'CVD': ["每周3次有氧运动", "控制血压", "低升糖指数饮食"],
        'PAD': ["每日步行15分钟", "戒烟", "低升糖指数饮食"]
    }
    return tasks.get(subtype, ["每日步行30分钟", "低钠饮食"])

@st.cache_data
def generate_health_card(user_data):
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("SimSun.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    username = user_data.get('username', '用户')
    # Safely get disease subtype
    subtype_tag = user_data.get('disease_tags', ['HTN:WCHT'])[0] if user_data.get('disease_tags') else 'HTN:WCHT'
    subtype = subtype_tag.split(':')[1] if ':' in subtype_tag else 'WCHT'
    risk_score = float(user_data.get('risk_score', 0.0))

    draw.text((20, 20), f"心守护健康卡", font=font, fill="#1e3a8a")
    draw.text((20, 60), f"用户名: {username}", font=font, fill="#1e3a8a")
    draw.text((20, 100), f"疾病类型: {subtype}", font=font, fill="#1e3a8a")
    draw.text((20, 140), f"风险评分: {risk_score:.1f}%", font=font, fill="#1e3a8a")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

@st.cache_data
def generate_pdf_report(user_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    font_name = 'SimSun' if 'SimSun' in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    c.setFont(font_name, 16)
    c.drawString(50, A4[1]-50, "心守护健康报告")
    c.setFont(font_name, 12)
    y = A4[1] - 100

    basic_info = user_data.get('basic_info', {})
    if basic_info:
        c.drawString(50, y, "基本信息:")
        y -= 15
        for key, value in basic_info.items():
            c.drawString(60, y, f"- {key}: {value}")
            y -= 15
        y -= 5 # Add a little space

    cardio_daily = user_data.get('cardio_daily', [])[-5:] # Take last 5 entries
    if cardio_daily:
        c.drawString(50, y, "近期血压记录:")
        y -= 15
        for entry in cardio_daily:
            c.drawString(60, y, f"- {entry.get('date', '')}: 收缩压 {entry.get('ap_hi', '-')} mmHg, 舒张压 {entry.get('ap_lo', '-')} mmHg")
            y -= 15
        y -= 5

    c.showPage()
    c.save()
    return buffer.getvalue()

def main():
    user_manager = UserManager(RedisManager())
    if 'user_id' not in st.session_state or not st.session_state.user_id:
        st.error("请先登录！")
        st.switch_page("app.py")
        st.stop()

    user_data = user_manager.get_user_info(st.session_state.user_id) or {
        'username': '用户',
        'disease_tags': ['HTN:WCHT'],
        'basic_info': {},
        'cardio_daily': [],
        'risk_score': 0.0, # Ensure float default
        'rehab_plan': []
    }
    # Safely get subtype
    subtype_tag = user_data.get('disease_tags', ['HTN:WCHT'])[0] if user_data.get('disease_tags') else 'HTN:WCHT'
    subtype = subtype_tag.split(':')[1] if ':' in subtype_tag else 'WCHT'

    with st.sidebar:
        st.markdown('<h3 class="text-lg font-semibold text-gray-700">导航</h3>', unsafe_allow_html=True)
        if st.button("🏠 返回主页"):
            st.switch_page("app.py")
        st.markdown('<hr class="my-4">', unsafe_allow_html=True)
        with st.form("basic_info_form"):
            st.markdown("### 基本信息")
            # Provide default values from user_data if available, ensure floats
            age = float(user_data.get('basic_info', {}).get('age', 30.0))
            gender_options = ["男", "女", "其他"]
            current_gender = user_data.get('basic_info', {}).get('gender', "男")
            # Find index, default to 0 if not found
            gender_index = gender_options.index(current_gender) if current_gender in gender_options else 0

            height = float(user_data.get('basic_info', {}).get('height', 170.0))
            weight = float(user_data.get('basic_info', {}).get('weight', 70.0))

            age_input = st.number_input("年龄", min_value=18.0, max_value=120.0, value=age)
            gender_input = st.selectbox("性别", gender_options, index=gender_index)
            height_input = st.number_input("身高 (cm)", min_value=100.0, max_value=250.0, value=height)
            weight_input = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0, value=weight)

            if st.form_submit_button("保存信息"):
                user_data['basic_info'] = {'age': age_input, 'gender': gender_input, 'height': height_input, 'weight': weight_input}
                user_manager.update_user_info(st.session_state.user_id, user_data)
                st.success("信息保存成功！")
                st.rerun()

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">个人信息</h3>', unsafe_allow_html=True)
    basic_info = user_data.get('basic_info', {})
    st.markdown(f"""
    - 用户名: {user_data.get('username', '用户')}
    - 年龄: {basic_info.get('age', '-')} 岁
    - 性别: {basic_info.get('gender', '-')}
    - 身高: {basic_info.get('height', '-')} cm
    - 体重: {basic_info.get('weight', '-')} kg
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">心血管康复计划</h3>', unsafe_allow_html=True)
    rehab_plan = user_data.get('rehab_plan', generate_cardio_rehab_plan(subtype, workload="moderate", support="family"))
    user_data['rehab_plan'] = rehab_plan # Update if generated
    user_manager.update_user_info(st.session_state.user_id, user_data)
    for task in rehab_plan:
        st.markdown(f'<div class="task-card"><span>{task}</span><span class="progress-circle">✅</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">历史数据</h3>', unsafe_allow_html=True)
    cardio_daily = user_data.get('cardio_daily', [])
    if cardio_daily:
        df = pd.DataFrame(cardio_daily)
        df['date'] = pd.to_datetime(df['date'])
        # Ensure 'ap_hi' and 'ap_lo' are numeric, convert errors to NaN and then fill with 0.0 for plotting
        df['ap_hi'] = pd.to_numeric(df['ap_hi'], errors='coerce').fillna(0.0)
        df['ap_lo'] = pd.to_numeric(df['ap_lo'], errors='coerce').fillna(0.0)

        fig = px.line(df, x='date', y=['ap_hi', 'ap_lo'], title='血压趋势')
        fig.update_layout(
            template="plotly_white",
            height=300,
            margin=dict(t=80, b=50, l=50, r=50),
            xaxis_title="日期",
            yaxis_title="血压 (mmHg)"
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("暂无血压数据")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card glass-card"><h3 class="text-xl font-semibold text-gray-700">风险趋势</h3>', unsafe_allow_html=True)
    risk_history = user_data.get('risk_history', [])
    if risk_history:
        st.plotly_chart(create_3d_scatter(risk_history), width='stretch')
    else:
        st.info("暂无风险历史数据")
    if st.button("导出为GIF", key="export_risk_gif"):
        try:
            import plotly.io as pio
            buffer = BytesIO()
            fig = create_3d_scatter(risk_history)
            fig.write_gif(buffer, format="gif")
            st.download_button("下载GIF", data=buffer, file_name="risk_trend.gif", mime="image/gif")
        except Exception as e:
            st.error(f"导出GIF失败：{str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">分享健康卡</h3>', unsafe_allow_html=True)
    if st.button("生成健康卡", key="generate_health_card"):
        with st.spinner("正在生成健康卡..."):
            buffer = generate_health_card(user_data)
            st.download_button("下载健康卡", data=buffer, file_name="health_card.png", mime="image/png")
            st.image(buffer, caption="您的健康卡", width=400)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">分享健康报告</h3>', unsafe_allow_html=True)
    qr = qrcode.QRCode()
    qr.add_data("https://xinguardian.com/report") # Example report link
    qr.make()
    qr_img = qr.make_image(fill_color="#1e3a8a", back_color="white")
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    st.image(buffer, caption="扫描二维码分享健康报告", width=200)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">健康报告</h3>', unsafe_allow_html=True)
    if st.button("生成 PDF 报告", key="generate_pdf_report"):
        with st.spinner("正在生成PDF报告..."):
            pdf_buffer = generate_pdf_report(user_data)
            st.download_button("下载 PDF 报告", data=pdf_buffer, file_name="health_report.pdf", mime="application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()