import streamlit as st
import pandas as pd
import numpy as np
import random
from components.dish_camera import render as render_dish_camera
from components.export import render as render_export
from components.ai_week_menu import render as render_ai_week_menu
from pages.p01_profile import CARDIO_DISEASES, load_profile_data

def render():
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)  # Top padding from app.py

    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("请先登录以查看营养建议。")
        user_id = 'default_user'
        user_data = {}
    else:
        user_id = st.session_state.user_id
        user_data = load_profile_data(user_id)

    st.title("饮食助手")

    # 获取用户心血管疾病信息
    cardio_disease = user_data.get('cardio_disease', '无心血管疾病')
    diet_guidelines = CARDIO_DISEASES.get(cardio_disease, {}).get('diet_guidelines', '均衡饮食，适量控制热量和钠摄入。')

    # --- Top action buttons ---
    col_camera, col_export = st.columns([1, 5])

    with col_camera:
        if st.button("拍照识菜 📸", use_container_width=True):
            render_dish_camera()

    with col_export:
        if st.button("一键导出食谱 (CSV)", use_container_width=True):
            render_export()

    # --- AI Generated Week Menu ---
    st.markdown("<h2 style='font-size: 24px; font-weight: 500; color: #1F2937; margin-top: 40px; margin-bottom: 20px;'>7 天 AI 营养食谱</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; color: #333; line-height: 1.6;'>根据您的健康档案（{cardio_disease}），推荐以下饮食方案：<br>{diet_guidelines}</p>", unsafe_allow_html=True)
    
    try:
        render_ai_week_menu(cardio_disease=cardio_disease)
    except Exception as e:
        st.error(f"加载或生成食谱时出错: {e}")

    # --- Guidance Text ---
    st.markdown("""
    <div style="margin-top: 40px; padding: 20px; background-color: #e3f2fd; border-left: 5px solid #2196f3; border-radius: 8px; font-size: 13px; color: #0d47a1;">
        <strong>营养小贴士：</strong>
        <ul>
            <li>优先选择蒸、煮、炖、凉拌等低油烹饪方式。</li>
            <li>控制钠摄入：每日建议成人钠摄入量不超过 2000 mg。</li>
            <li>保证膳食纤维：每日建议摄入 30g 左右，多吃蔬菜、全谷物。</li>
            <li>适量摄入优质蛋白，如鱼、禽、豆制品。</li>
            <li>减少饱和脂肪和反式脂肪酸的摄入，如肥肉、油炸食品。</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()