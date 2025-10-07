# utils/model.py

import streamlit as st
import pandas as pd
import joblib
import os
import numpy as np

# --- Model Loading ---
def load_risk_model(model_path='assets/xgb_risk.pkl'):
    """Loads the trained XGBoost risk prediction model."""
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            return model
        except Exception as e:
            st.error(f"加载心血管风险模型失败: {e}")
            return None
    else:
        st.warning(f"心血管风险模型文件 '{model_path}' 不存在。请先运行 train.py。")
        return None

def load_subtype_model(model_path='assets/xgb_subtype.pkl'):
    """Loads the trained XGBoost subtype prediction model (if available)."""
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            return model
        except Exception as e:
            st.error(f"加载疾病亚型模型失败: {e}")
            return None
    else:
        # It's okay if subtype model doesn't exist, it's optional.
        st.info(f"疾病亚型模型文件 '{model_path}' 不存在。")
        return None

# --- Prediction Function ---
def predict_risk(model, features_df):
    """
    Predicts the risk probability of cardiovascular disease.
    
    Args:
        model: The loaded XGBoost model.
        features_df (pd.DataFrame): DataFrame containing input features.
                                    Must match the features used during training.
                                    
    Returns:
        float: Probability of cardiovascular disease (0 to 1).
    """
    if model is None:
        return None
    
    try:
        # Ensure the input DataFrame has the correct columns in the correct order
        # This is crucial for accurate prediction.
        # You might need to reorder or add missing columns with default values.
        # For example, if model.feature_names_in_ is available:
        if hasattr(model, 'feature_names_in_'):
            expected_features = model.feature_names_in_
            # Reindex df to match expected features, filling missing with 0 or mean if appropriate.
            # Here, assuming 'features_df' already has the correct columns derived from user profile.
            # A more robust check might be needed.
            features_df = features_df.reindex(columns=expected_features, fill_value=0) # Fill missing features if any
        
        # Predict probabilities for the positive class (cardiovascular disease = 1)
        prediction_proba = model.predict_proba(features_df)[:, 1]
        return prediction_proba[0] if len(prediction_proba) > 0 else None
        
    except Exception as e:
        st.error(f"预测心血管风险时发生错误: {e}")
        return None

def predict_subtype(model, features_df):
    """
    Predicts the subtype of cardiovascular disease.
    
    Args:
        model: The loaded XGBoost subtype model.
        features_df (pd.DataFrame): DataFrame containing input features.
                                    
    Returns:
        int or str: The predicted subtype label or None if prediction fails.
    """
    if model is None:
        return None
        
    try:
        # Similar feature alignment as predict_risk
        if hasattr(model, 'feature_names_in_'):
            expected_features = model.feature_names_in_
            features_df = features_df.reindex(columns=expected_features, fill_value=0)
        
        # Predict the class label for subtype
        prediction = model.predict(features_df)
        return prediction[0] if len(prediction) > 0 else None
        
    except Exception as e:
        st.error(f"预测疾病亚型时发生错误: {e}")
        return None

# --- SHAP Calculation (using loaded model) ---
def get_shap_explainer(model):
    """Creates a SHAP explainer for a given XGBoost model."""
    if model is None:
        return None
    try:
        # TreeExplainer is suitable for tree-based models like XGBoost
        explainer = shap.TreeExplainer(model)
        return explainer
    except Exception as e:
        st.error(f"创建 SHAP Explainer 失败: {e}")
        return None

def calculate_user_shap_values(explainer, user_features_df):
    """
    Calculates SHAP values for a single user's input features.
    
    Args:
        explainer: The SHAP TreeExplainer object.
        user_features_df (pd.DataFrame): DataFrame of the user's features.
                                         
    Returns:
        np.ndarray: SHAP values for the user's prediction (for the positive class).
        float: The expected value (base value) of the model's predictions.
    """
    if explainer is None or user_features_df is None or user_features_df.empty:
        return None, None
    
    try:
        # Ensure features are aligned with the explainer's expectations
        # If explainer has `expected_value` and can handle data alignment:
        
        # SHAP explainer's `shap_values` method might return a list for binary classification.
        # We usually want SHAP values for the positive class (class 1).
        shap_values_output = explainer.shap_values(user_features_df)
        
        # For binary classification, `shap_values_output` is typically a list of two arrays: [shap_for_class_0, shap_for_class_1]
        # We are interested in the prediction of cardiovascular disease (class 1).
        if isinstance(shap_values_output, list) and len(shap_values_output) > 1:
            user_shap = shap_values_output[1] # SHAP values for class 1
        else:
            user_shap = shap_values_output # Assuming it's already for the relevant class or single output

        # The expected_value attribute of the explainer is the base rate.
        # For binary classification, it might also be a list.
        expected_value = explainer.expected_value
        if isinstance(expected_value, list) and len(expected_value) > 1:
            expected_value = expected_value[1] # Expected value for class 1

        return user_shap, expected_value
        
    except Exception as e:
        st.error(f"计算用户 SHAP 值时发生错误: {e}")
        return None, None

# --- Feature Preparation for Prediction ---
def prepare_features_for_prediction(profile_data):
    """
    Prepares a DataFrame of features from user profile data, matching
    the structure expected by the trained models.

    Args:
        profile_data (dict): Dictionary containing user's profile information.

    Returns:
        pd.DataFrame: DataFrame ready for model prediction, or None if essential data is missing.
    """
    # This function needs to mirror the feature engineering done in train.py
    # It's a critical step to ensure feature consistency.
    
    # Example feature engineering based on typical Cardio dataset features:
    # Features likely used in training:
    # 'gender', 'age_years', 'bmi', 'cholesterol', 'gluc',
    # 'ap_hi', 'ap_lo', 'smoke', 'alco', 'active'
    
    features = {}

    # 1. Gender: 0 for female, 1 for male
    features['gender'] = 1 if profile_data.get('gender') == '男' else 0

    # 2. Age in years
    features['age_years'] = profile_data.get('age')
    if features['age_years'] is None: features['age_years'] = 40 # Default if missing

    # 3. BMI
    height_cm = profile_data.get('height')
    weight_kg = profile.get('weight')
    if height_cm and weight_kg:
        height_m = height_cm / 100
        features['bmi'] = weight_kg / (height_m ** 2)
    else:
        features['bmi'] = 22.5 # Default BMI if missing

    # 4. Cholesterol & Gluc (assuming they are coded 1: normal, 2: above, 3: very high)
    # These might be directly collected or inferred. Here, assuming they are NOT collected directly in profile.
    # We'll infer based on risk factors or set defaults.
    # In a real scenario, these would be collected or estimated.
    features['cholesterol'] = 1 # Default to normal
    features['gluc'] = 1        # Default to normal
    
    # Infer cholesterol and gluc based on diseases and habits (example inference)
    diseases = profile_data.get('diseases', [])
    habits = profile_data.get('smoking', False) or profile_data.get('alcohol', False) or profile_data.get('lack_exercise', False)

    if "冠心病" in diseases or "高血压" in diseases or "心力衰竭" in diseases:
        features['cholesterol'] = 2 # Higher risk profile

    # If diabetes is present (not explicitly in profile, but could be inferred or a separate field)
    # For now, let's assume it's not explicitly collected.
    # if "diabetes" in diseases: features['gluc'] = 2

    # 5. Blood Pressure (ap_hi, ap_lo)
    # These might be collected via daily logs or specific profile fields.
    # If not collected, use defaults or infer from profile data if possible.
    # For this example, we'll use typical values or derived ones if available.
    # Let's assume they are NOT directly collected in the basic profile.
    # A more complete profile would include these.
    
    # Inferring BP is complex without actual measurements.
    # We'll use default values that might reflect a moderate risk.
    # This is a significant simplification. Ideally, BP should be a direct input.
    features['ap_hi'] = 130 # Default systolic BP
    features['ap_lo'] = 85  # Default diastolic BP
    
    # If hypertension is in diseases, slightly increase defaults or set to typical hypertensive range
    if "高血压" in diseases:
        features['ap_hi'] = 145
        features['ap_lo'] = 92

    # 6. Smoking (smoke): 0=no, 1=yes
    features['smoke'] = 1 if profile_data.get('smoking') else 0

    # 7. Alcohol (alco): 0=no, 1=yes
    features['alco'] = 1 if profile_data.get('alcohol') else 0

    # 8. Active (active): 1=yes, 0=no (opposite of lack_exercise)
    features['active'] = 1 if profile_data.get('lack_exercise') is False else 0

    # Convert to DataFrame, ensuring column order and names match the trained model
    # This requires knowing the exact feature order from train.py
    # Let's assume the trained model expects these features in this order.
    # The `prepare_features_for_prediction` in train.py should be the source of truth.
    
    # Example based on common features:
    # Check what features `train.py` actually uses and create this DataFrame accordingly.
    # Assuming the model used features: ['gender', 'age_years', 'bmi', 'cholesterol', 'gluc', 'ap_hi', 'ap_lo', 'smoke', 'alco', 'active']
    
    model_features_df = pd.DataFrame([features])
    
    # Ensure correct column names and order if model expects it explicitly
    # If using sklearn-compatible models (like XGBoost wrapped by sklearn), they often have feature_names_in_
    
    return model_features_df
