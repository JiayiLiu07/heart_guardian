# pages/p05_me.py
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import logging

# Import utility functions
# Ensure the path to api.py is correct in your project structure
try:
    from utils.api import initialize_client, get_image_and_explanation_from_vllm
    # Assume p01_profile.py is in the same 'pages' directory
    from pages.p01_profile import load_profile_data
except ImportError:
    st.error("Error importing modules. Make sure 'utils' and 'pages' directories are structured correctly.")
    st.stop()

from components.top_nav import render_nav
st.session_state.current_page = "me"
render_nav()

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Ensure API client is initialized
def ensure_client_initialized():
    if "client" not in st.session_state or st.session_state.client is None:
        if "api_key" in st.session_state and st.session_state.api_key:
            st.session_state.client = initialize_client(st.session_state.api_key)
            if not st.session_state.client:
                st.warning("AI client not initialized. Please set up your API key on the main page.")
                return False
        else:
            st.warning("Please set up your API key on the main page to use AI features.")
            return False
    return True

# --- Styling for this page ---
st.markdown("""
<style>
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
    st.markdown("<h1 class='section-title'>👤 My Profile & AI Insights</h1>", unsafe_allow_html=True)

    user_id = st.session_state.get("user_id")

    if not user_id:
        st.warning("Please log in or create an account to view your profile and insights.")
        # Adjust path if your login/auth page is elsewhere
        st.markdown("[Go to Login/Signup](/pages/p00_auth.py)")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- Load User Profile Data ---
    try:
        profile_data = load_profile_data(user_id)
        if not profile_data:
            st.error("Could not load your profile data. Please try again.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        st.subheader("Your Personal Information Summary")
        st.markdown(f"<div class='profile-info'><strong>Name:</strong> {profile_data.get('name', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>Age:</strong> {profile_data.get('age', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>Health Goals:</strong> {profile_data.get('health_goals', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>Dietary Preferences:</strong> {profile_data.get('dietary_preferences', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><strong>Activity Level:</strong> {profile_data.get('activity_level', 'N/A')}</div>", unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error loading profile data: {e}", exc_info=True)
        st.error(f"Error loading profile: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

    # --- AI Generated Insight Section ---
    st.subheader("🤖 AI Analysis of Your Profile")

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

    if st.button("Generate AI Health Insights ✨", key="ai_insight_button"):
        with st.spinner("AI is analyzing your profile... 🧠"):
            image_base64, explanation = get_image_and_explanation_from_vllm(
                st.session_state.client,
                profile_summary_text,
                st.session_state.image_model,
                [] # Profile data is not structured like a CSV, pass empty or specific keys
            )

            if image_base64 and explanation:
                try:
                    image_bytes = base64.b64decode(image_base64)
                    image_stream = BytesIO(image_bytes)

                    st.markdown("<div class='insight-card'>", unsafe_allow_html=True)
                    st.markdown("<div class='insight-title'>AI Health Visualization</div>", unsafe_allow_html=True)
                    st.image(image_stream, caption="Your Personalized Health Insights", use_column_width=True)
                    
                    st.markdown("<div class='explanation-text'>", unsafe_allow_html=True)
                    st.markdown(explanation, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.success("AI insights generated successfully! ✅")

                except Exception as e:
                    logger.error(f"Error displaying AI image for profile: {e}", exc_info=True)
                    st.error(f"Could not display your AI health insights. Error: {e}")
            else:
                st.error("Failed to generate AI health insights. Please try again. 😔")

    st.markdown("</div>", unsafe_allow_html=True) # Close main-content-area

# This function is called when the script is run directly
if __name__ == "__main__":
    render_p05_me()

st.markdown("""
<style>
.export-dock{display:flex;justify-content:center}
.download-pulse{
  width:60px;height:60px;margin:auto;
  border:4px solid #00e5ff;border-radius:50%;
  animation:pulse 1s infinite;
}
</style>
""", unsafe_allow_html=True)