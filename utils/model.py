# 📁 utils/model.py
import streamlit as st
import pickle
import pandas as pd
import os
# Assuming necessary ML libraries are installed, e.g., xgboost, scikit-learn
# import xgboost as xgb
# from sklearn.ensemble import RandomForestClassifier

MODEL_DIR = "./assets/"
RISK_MODEL_PATH = os.path.join(MODEL_DIR, "xgb_risk.pkl")
SUBTYPE_MODELS_DIR = os.path.join(MODEL_DIR, "subtype_models/") # Assuming subtype models are in a sub-directory

# --- Utility Functions for Model Loading and Prediction ---

@st.cache_resource # Use Streamlit's resource caching to avoid reloading models
def load_risk_model():
    """Loads the overall risk prediction model."""
    if os.path.exists(RISK_MODEL_PATH):
        try:
            with open(RISK_MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            st.error(f"Failed to load risk model from {RISK_MODEL_PATH}: {e}")
            return None
    else:
        st.error(f"Risk model file not found: {RISK_MODEL_PATH}")
        return None

@st.cache_resource
def load_subtype_models():
    """Loads all disease-specific subtype models."""
    models = {}
    if os.path.exists(SUBTYPE_MODELS_DIR) and os.path.isdir(SUBTYPE_MODELS_DIR):
        for filename in os.listdir(SUBTYPE_MODELS_DIR):
            if filename.endswith(".pkl"):
                disease_key = filename.replace(".pkl", "").upper() # e.g., "HYPERTENSION"
                model_path = os.path.join(SUBTYPE_MODELS_DIR, filename)
                try:
                    with open(model_path, 'rb') as f:
                        models[disease_key] = pickle.load(f)
                except Exception as e:
                    st.error(f"Failed to load subtype model {filename}: {e}")
        if not models:
            st.warning(f"No subtype models found in {SUBTYPE_MODELS_DIR}.")
        return models
    else:
        st.error(f"Subtype models directory not found or is not a directory: {SUBTYPE_MODELS_DIR}")
        return {}

def preprocess_user_data(user_profile_dict: dict) -> pd.DataFrame:
    """
    Preprocesses user profile data into a DataFrame suitable for model prediction.
    This function should align with the preprocessing steps used during model training.
    """
    # Ensure user_profile_dict contains all necessary features for the models.
    # Example features (adjust based on your model's requirements):
    # 'age', 'gender', 'height', 'weight', 'ap_high', 'ap_low', 'cholesterol', 'gluc', 'smoke', 'alco', 'active', 'bmi', 'family_history', 'diseases' etc.

    # Convert dictionary to DataFrame
    user_df = pd.DataFrame([user_profile_dict])

    # Perform feature engineering (e.g., calculate BMI, encode categorical features)
    # NOTE: This MUST match the preprocessing done during training.
    if 'height' in user_df.columns and 'weight' in user_df.columns:
        user_df['bmi'] = user_df['weight'] / ((user_df['height'] / 100)**2)
    
    # Example: Encode gender (assuming 'Male' -> 1, 'Female' -> 0, 'Other'/'Select' -> 0 or specific value)
    if 'gender' in user_df.columns:
        user_df['gender'] = user_df['gender'].apply(lambda x: 1 if x == '男' else 0) # Adjust based on your gender labels

    # Example: One-hot encode categorical features if your model requires it
    # categorical_features = ['family_history', 'smoking_status', 'alcohol_consumption', ...]
    # for col in categorical_features:
    #     if col in user_df.columns:
    #         user_df = pd.get_dummies(user_df, columns=[col], prefix=col)
    
    # Example: Map diseases to numerical features if your model uses them
    # This might be complex if diseases are multi-select and impact multiple models.
    # For simplicity, assuming 'diseases' list is not directly used as a feature here,
    # but models are trained on specific disease flags.

    # Ensure the order of columns matches the model's expected feature order
    # If models have `feature_names_in_` attribute, you can use that:
    # model_features = model.feature_names_in_
    # user_df = user_df.reindex(columns=model_features, fill_value=0)

    return user_df

def predict_risk(model, user_profile_dict: dict):
    """Predicts overall cardiovascular risk."""
    if model is None:
        st.error("Risk prediction model is not loaded.")
        return 0.5 # Return a neutral default or raise error

    try:
        user_df = preprocess_user_data(user_profile_dict)
        # Make prediction (e.g., probability of positive class)
        # The index [:, 1] assumes binary classification and returns the probability of the positive class.
        # Adjust if your model returns probabilities differently.
        prediction = model.predict_proba(user_df)[:, 1] 
        return prediction[0]
    except Exception as e:
        st.error(f"Error during risk prediction: {e}")
        return 0.5 # Return default on error

def predict_subtype(models: dict, user_profile_dict: dict):
    """Predicts risk for each subtype disease."""
    subtype_predictions = {}
    if not models:
        st.warning("No subtype models loaded.")
        return subtype_predictions

    try:
        user_df = preprocess_user_data(user_profile_dict)
        
        for disease_key, model in models.items():
            try:
                prediction = model.predict_proba(user_df)[:, 1]
                subtype_predictions[disease_key] = prediction[0]
            except Exception as e:
                st.warning(f"Error predicting subtype '{disease_key}': {e}")
                subtype_predictions[disease_key] = 0.0 # Default to 0 on error
        return subtype_predictions
    except Exception as e:
        st.error(f"Overall subtype prediction failed: {e}")
        return subtype_predictions

# --- Example Usage (for testing utils/model.py directly) ---
if __name__ == "__main__":
    st.write("Testing model loading and prediction...")
    
    # Create dummy profile data for testing
    dummy_profile = {
        'name': 'Test User', 'age': 55, 'gender': '男', 'height': 170, 'weight': 75,
        'bmi': 25.95, 'diseases': ['HTN', 'DM'], 'family_history': '有',
        'smoking_status': '偶尔吸烟', 'alcohol_consumption': '适量饮酒',
        'allergies': ['花生'], 'cuisine_preference': ['中餐'],
        'sleep_hours': 7.5, 'exercise_minutes': 150
    }
    
    # Load models
    risk_model_test = load_risk_model()
    subtype_models_test = load_subtype_models()
    
    if risk_model_test:
        risk_pred = predict_risk(risk_model_test, dummy_profile)
        st.write(f"Dummy profile overall risk prediction: {risk_pred:.4f}")
    
    if subtype_models_test:
        subtype_preds = predict_subtype(subtype_models_test, dummy_profile)
        st.write("Dummy profile subtype predictions:")
        for disease, pred in subtype_preds.items():
            st.write(f"- {disease}: {pred:.4f}")