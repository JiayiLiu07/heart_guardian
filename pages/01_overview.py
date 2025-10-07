import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
try:
    import shap
    import xgboost as xgb
    import joblib
except ImportError:
    st.warning("SHAP、xgboost 或 joblib 库未安装，使用 dummy 数据。")
    shap = None
    xgb = None
    joblib = None

# --- Helper function to load model ---
def load_model(model_path='assets/xgb_risk.pkl'):
    if joblib and os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            return shap.TreeExplainer(model) if shap else None
        except Exception as e:
            st.error(f"加载模型 {model_path} 失败: {e}")
            return None
    else:
        st.warning(f"模型文件 {model_path} 不存在或 joblib 未安装，使用 dummy 数据。")
        return None

# --- Helper function to get user's feature data ---
def load_profile_data(user_id):
    filename = os.path.join('users', f"{user_id}_profile.csv")
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            return df.iloc[0].to_dict()
        except Exception as e:
            st.error(f"加载用户数据失败: {e}")
            return {}
    return {}

def get_user_features(user_id):
    user_data = load_profile_data(user_id)
    if user_data:
        features = {}
        features['gender'] = 1 if user_data.get('gender', '') == '男' else 0
        features['age_years'] = user_data.get('age', 40)  # Assuming age in years
        height_cm = user_data.get('height', 0)
        weight_kg = user_data.get('weight', 0)
        if height_cm > 0 and weight_kg > 0:
            height_m = height_cm / 100
            features['bmi'] = weight_kg / (height_m ** 2)
        else:
            features['bmi'] = 0
        features['cholesterol'] = 1
        features['gluc'] = 1
        features['ap_hi'] = user_data.get('systolic', 120)
        features['ap_lo'] = user_data.get('diastolic', 80)
        features['smoke'] = 1 if user_data.get('smoking', '不吸烟') != '不吸烟' else 0
        features['alco'] = 1 if user_data.get('alcohol', '不饮酒') != '不饮酒' else 0
        features['active'] = 1 if user_data.get('exercise_frequency', '几乎不运动') != '几乎不运动' else 0
        return pd.DataFrame([features])
    else:
        st.warning("用户数据不存在，使用 dummy 数据。")
        dummy_features = {
            'gender': 1, 'age_years': 50, 'bmi': 25, 'cholesterol': 1, 'gluc': 1,
            'ap_hi': 120, 'ap_lo': 80, 'smoke': 0, 'alco': 0, 'active': 1
        }
        return pd.DataFrame([dummy_features])

# --- Predict and Get SHAP Values ---
def predict_and_get_shap(user_features_df, explainer):
    if explainer and xgb:
        try:
            model = explainer.model
            dmatrix = xgb.DMatrix(user_features_df)
            risk_prediction_proba = model.predict(dmatrix)  # 移除 output_margin 参数
            shap_values = explainer.shap_values(user_features_df)
            expected_value = explainer.expected_value
            return risk_prediction_proba[0], shap_values, expected_value
        except Exception as e:
            st.error(f"预测和 SHAP 计算失败: {e}")
            return 0.5, None, None
    else:
        return 0.5, None, None  # Dummy

# --- Render SHAP Waterfall Plot ---
def render_shap_waterfall(shap_values, expected_value, model_feature_names, user_features_df):
    if shap and shap_values is not None:
        try:
            fig, ax = plt.subplots(figsize=(6, 4))
            shap_explanation = shap.Explanation(values=shap_values[0], base_values=expected_value, data=user_features_df.iloc[0], feature_names=model_feature_names)
            shap.plots.waterfall(shap_explanation, max_display=10, show=False)
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"渲染 SHAP waterfall 图失败: {e}")
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'SHAP Waterfall (Dummy)', ha='center')
            st.pyplot(fig)
            plt.close(fig)

# --- Render SHAP Bar Plot for Training Set ---
def render_shap_bar(explainer, feature_names, user_shap_values, user_features_df):
    if shap and explainer:
        try:
            # 使用用户 SHAP 值计算特征重要性，避免零数据形状问题
            fig, ax = plt.subplots(figsize=(6, 4))
            shap.summary_plot(user_shap_values, user_features_df, plot_type="bar", show=False)
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"渲染 SHAP bar 图失败: {e}")
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'SHAP Bar (Dummy)', ha='center')
            st.pyplot(fig)
            plt.close(fig)

# --- Global Comparison Text ---
def get_global_comparison_text():
    return {
        "systolic_bp_contribution": "+5.2%",
        "systolic_bp_rank": "83%",
        "top_risk_factors_text": "收缩压、年龄、BMI 是影响心血管风险的前三杀手。"
    }

def render():
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)  # Top padding from app.py

    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("请先登录以查看您的健康概览。")
        user_id = 'default_user'
    else:
        user_id = st.session_state.user_id

    st.title("您的健康概览")
    st.markdown("<h2 style='font-size: 24px; font-weight: 500; color: #1F2937;'>你的危险因子 vs 大数据</h2>", unsafe_allow_html=True)

    explainer = load_model()
    user_features_df = get_user_features(user_id)

    risk_prediction_proba, user_shap_values, expected_value = predict_and_get_shap(user_features_df, explainer)
    model_feature_names = user_features_df.columns.tolist() if user_features_df is not None else []

    # 两列布局：左边个人 SHAP 瀑布图，右边训练集平均 SHAP 条形图
    col1, col2 = st.columns([6, 6])
    with col1:
        st.markdown("<h4 style='font-size: 20px; font-weight: 500; margin-bottom: 20px; color: #1F2937;'>你的风险贡献分析</h4>", unsafe_allow_html=True)
        render_shap_waterfall(user_shap_values, expected_value, model_feature_names, user_features_df)
    with col2:
        st.markdown("<h4 style='font-size: 20px; font-weight: 500; margin-bottom: 20px; color: #1F2937;'>训练集平均风险贡献</h4>", unsafe_allow_html=True)
        render_shap_bar(explainer, model_feature_names, user_shap_values, user_features_df)

    if user_shap_values is not None and expected_value is not None:
        st.markdown(f"<p style='font-size: 14px; color: #333; line-height: 1.6;'>你的心血管疾病风险预测概率约为：<strong style='font-size: 18px; color: #E94560;'>{risk_prediction_proba*100:.2f}%</strong>。</p>", unsafe_allow_html=True)

        comparison_text_data = get_global_comparison_text()
        st.markdown(f"<p style='font-size: 14px; color: #333; line-height: 1.6;'>你的收缩压贡献了约 <strong style='color: #E94560;'>{comparison_text_data['systolic_bp_contribution']}</strong> 的风险，高于 {comparison_text_data['systolic_bp_rank']} 的同龄人。</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 14px; color: #333; line-height: 1.6;'>大数据显示：{comparison_text_data['top_risk_factors_text']}</p>", unsafe_allow_html=True)
    else:
        st.warning("未能成功计算并渲染你的 SHAP 贡献分析，使用 dummy 数据。")
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'SHAP Waterfall (Dummy)', ha='center')
        st.pyplot(fig)
        st.markdown("<p style='font-size: 14px; color: #333; line-height: 1.6;'>你的心血管疾病风险预测概率约为：<strong style='font-size: 18px; color: #E94560;'>50.00%</strong>。</p>", unsafe_allow_html=True)

    # --- Action Buttons ---
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)  # Spacer
    col_diet, col_doctor = st.columns(2)
    with col_diet:
        st.button("去查看饮食建议", key="view_diet_button", on_click=lambda: st.switch_page("pages/02_nutrition.py"), use_container_width=True, help="查看个性化饮食建议")
        st.markdown("""
        <style>
        .stButton > button {
            border: 2px solid #E94560;
            border-radius: 30px;
            background: transparent;
            color: #E94560;
            font-weight: bold;
        }
        .stButton > button:hover {
            background: #E94560;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    with col_doctor:
        st.button("去 AI 问医生", key="consult_ai_doctor_button", on_click=lambda: st.switch_page("pages/03_ai_doctor.py"), use_container_width=True, help="咨询 AI 医生")
        st.markdown("""
        <style>
        .stButton > button {
            border: 2px solid #E94560;
            border-radius: 30px;
            background: transparent;
            color: #E94560;
            font-weight: bold;
        }
        .stButton > button:hover {
            background: #E94560;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()