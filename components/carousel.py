import streamlit as st
import json
import random
import os

def render():
    tips_file = 'assets/health_tips.json'
    
    if not os.path.exists(tips_file):
        st.warning(f"健康建议文件 '{tips_file}' 未找到。")
        tips_data = ["请确保 'assets/health_tips.json' 文件存在。"]
    else:
        try:
            with open(tips_file, 'r', encoding='utf-8') as f:
                tips_data = json.load(f)
        except Exception as e:
            st.error(f"加载健康建议失败: {e}")
            tips_data = ["加载健康建议失败。"]

    carousel_items_html = ""
    for tip in tips_data:
        carousel_items_html += f"""
        <div class="carousel-card">
            {tip}
        </div>
        """

    carousel_container_html = f"""
    <div class="carousel-container">
        <div class="carousel-track">
            {carousel_items_html}
        </div>
    </div>
    <style>
        .carousel-container {{
            height: 100px;
            background: #f0f2f6;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 2rem;
            overflow: hidden;
        }}
        .carousel-track {{
            display: flex;
            width: max-content;
            animation: scrollTips 40s linear infinite;
        }}
        .carousel-card {{
            flex-shrink: 0;
            width: 380px;
            height: 100px;
            background: #fff;
            border-left: 5px solid #E94560;
            border-radius: 12px;
            padding: 16px;
            font-size: 14px;
            color: #1F2937;
            box-shadow: 0 4px 12px rgba(0,0,0,.08);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-right: 20px;
        }}
        .carousel-container:hover .carousel-track {{
            animation-play-state: paused;
        }}
        @keyframes scrollTips {{
            0% {{
                transform: translateX(0%);
            }}
            100% {{
                transform: translateX(-100%);
            }}
        }}
    </style>
    """
    st.markdown(carousel_container_html, unsafe_allow_html=True)

if __name__ == "__main__":
    render()