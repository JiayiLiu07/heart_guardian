import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import logging
from utils.api import initialize_client, get_image_and_explanation_from_vllm
from pages.p01_profile import load_profile_data

logger = logging.getLogger(__name__)

def ensure_client_initialized():
    if "client" not in st.session_state or st.session_state.client is None:
        if "api_key" in st.session_state and st.session_state.api_key:
            st.session_state.client = initialize_client(st.session_state.api_key)
            if not st.session_state.client:
                st.warning("AI 客户端未初始化。请在主页设置 API 密钥。")
                return False
        else:
            st.warning("请在主页设置 API 密钥以使用 AI 功能。")
            return False
    return True

st.markdown("""
<style>
.block-container {padding-top: 80px !important; margin-top: 0 !important;}
.main-content-area { padding: 2rem; background-color: #ffffff; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.section-title { color: #1f2937; font-size: 1.8rem; margin-bottom: 1rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 0.5rem;}
.insight-card { background-color: #f3f4f6; border-radius: 0.5rem; padding: 1.5rem; margin-top: 1.5rem; box-shadow: 0 2px 5px rgba(0,0,0,0.08); }
.insight-title { color: #3b82f6; font-weight: 600; font-size: 1.3rem; margin-bottom: 0.8rem; }
.explanation-text { color: #4b5563; line-height: 1.6; font-size: 1.05rem; }
.emoji { font-size: 1.1rem; margin-left: 0.3rem; }
.profile-info { margin-bottom: 1rem; font-size: 1.05rem; }
.profile-info strong { color: #1f2937; }
</style>
""", unsafe_allow_html=True)

def render_p05_me():
    if not ensure_client_initialized():
        st.stop()
    st.markdown("<div class='main-content-area'>", unsafe_allow_html=True)
    st.markdown("<h1 class='section-title'>👤 我的档案与 AI 洞察</h1>", unsafe_allow_html=True)
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("请登录或创建账户以查看您的档案和洞察。")
        st.markdown("[转到登录/注册](/pages/p00_auth.py)")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    try:
        profile_data = load_profile_data(user_id)
        if not profile_data:
            st.error("无法加载您的档案数据。请重试。")
            st.markdown("</div>", unsafe_allow_html=True)
            return
        st.subheader("您的个人信息摘要")
        st.markdown(f"<div class='profile-info'><strong>姓名:</strong> {profile_data.get('name', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>年龄:</strong> {profile_data.get('age', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>性别:</strong> {profile_data.get('gender', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>身高:</strong> {profile_data.get('height', 'N/A')} cm</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>体重:</strong> {profile_data.get('weight', 'N/A')} kg</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>腰围:</strong> {profile_data.get('waist', 'N/A')} cm</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>睡眠时间:</strong> {profile_data.get('sleep_hours', 'N/A')} 小时</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>心血管亚型:</strong> {', '.join(profile_data.get('cardio_subtypes', ['无']))}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>活动水平:</strong> {profile_data.get('activity_level', 'N/A')}</div>", unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"加载档案数据错误: {e}")
        st.error(f"加载档案失败: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    st.subheader("🤖 AI 对您的档案分析")
    profile_summary_text = f"""
    Based on my profile:
    Name: {profile_data.get('name', 'N/A')}
    Age: {profile_data.get('age', 'N/A')}
    Health Goals: {profile_data.get('health_goals', 'N/A')}
    Dietary Preferences: {profile_data.get('dietary_preferences', 'N/A')}
    Activity Level: {profile_data.get('activity_level', 'N/A')}
    Please provide a visual summary and actionable insights about my health status and goals.
    Include relevant emojis in your explanation.
    """
    if st.button("生成 AI 健康洞察 ✨", key="ai_insight_button"):
        with st.spinner("AI 正在分析您的档案... 🤖"):
            image_base64, explanation = get_image_and_explanation_from_vllm(
                st.session_state.client,
                profile_summary_text,
                st.session_state.image_model,
                []
            )
            if image_base64 and explanation:
                try:
                    image_bytes = base64.b64decode(image_base64)
                    image_stream = BytesIO(image_bytes)
                    st.markdown("<div class='insight-card'>", unsafe_allow_html=True)
                    st.markdown("<div class='insight-title'>AI 健康可视化</div>", unsafe_allow_html=True)
                    st.image(image_stream, caption="您的个性化健康洞察", width='stretch')
                    st.markdown("<div class='explanation-text'>", unsafe_allow_html=True)
                    st.markdown(explanation, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.success("AI 洞察生成成功！ ✔️")
                except Exception as e:
                    logger.error(f"显示 AI 图像错误: {e}")
                    st.error(f"无法显示 AI 健康洞察。错误: {e}")
            else:
                st.error("生成 AI 健康洞察失败。请重试。 😔")
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_p05_me()