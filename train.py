# train.py
import pandas as pd
import pickle
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler   # 新增
import joblib                                      # 替换 pickle
import os
import json

# --- Paths and Directories ---
ASSETS_DIR = "./assets/"
RISK_MODEL_PATH = os.path.join(ASSETS_DIR, "xgb_risk.pkl")
SUBTYPE_MODELS_DIR = os.path.join(ASSETS_DIR, "subtype_models/")
RECIPE_POOL_PATH = os.path.join(ASSETS_DIR, "recipe_pool.json")

# --- Ensure Directories Exist ---
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(SUBTYPE_MODELS_DIR, exist_ok=True)

# --- Data Path ---
DATA_PATH = "data/cardio_train.csv"

# --- Import Disease Definitions ---
try:
    from utils.disease_dict import DISEASE_ENUM
except ImportError:
    print("Error: Could not import DISEASE_ENUM from utils.disease_dict. Using fallback.")
    class DISEASE_ENUM:
        @staticmethod
        def get_all_diseases(): return []
        @staticmethod
        def get_disease_keys(): return []
        @staticmethod
        def get_disease_labels(): return {}

# --- Data Loading Function ---
def load_data(filepath):
    print(f"Loading data from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found at {filepath}")
    df = pd.read_csv(filepath, sep=";")
    print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df

# --- Feature Engineering ---
def feature_engineering(df):
    print("Performing feature engineering...")
    df['age_year'] = (df['age'] / 365.25).round().astype(int)
    df['bmi'] = df['weight'] / ((df['height'] / 100)**2)
    df['gender'] = df['gender'].map({1: 0, 2: 1})  # 1=Male→0, 2=Female→1 (or adjust)
    print("Feature engineering complete.")
    return df

# --- Train Risk Model ---
def train_risk_model(df):
    """Trains and saves the overall cardiovascular risk model with scaler."""
    print("\n--- Training Overall Risk Model ---")
    if 'cardio' not in df.columns:
        raise ValueError("Target column 'cardio' not found in DataFrame.")

    # 选择用于风险小测的极简特征（仅用于 demo）
    feature_cols = ['age_year', 'ap_hi']
    X = df[feature_cols]
    y = df['cardio']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")

    # 标准化（必须！否则模型泛化差）
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # XGBoost 模型
    model = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        n_estimators=150,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        verbosity=0
    )
    model.fit(X_train_scaled, y_train)

    # 评估
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    print(f"Accuracy: {acc:.4f}, AUC: {auc:.4f}")

    # 保存 model + scaler
    pipeline = {'model': model, 'scaler': scaler, 'features': feature_cols}
    joblib.dump(pipeline, RISK_MODEL_PATH)
    print(f"Risk model + scaler saved to: {RISK_MODEL_PATH}")

    return model, scaler, X_test, y_test

# --- Train Subtype Models (保持原逻辑，仅跳过无关部分) ---
def train_subtype_models(df):
    trained_models = {}
    diseases = DISEASE_ENUM.get_all_diseases()
    if not diseases:
        print("No diseases defined in DISEASE_ENUM. Skipping subtype training.")
        return trained_models

    print(f"\n--- Training {len(diseases)} Subtype Models ---")
    for disease_key in diseases:
        target_column_name = DISEASE_ENUM.get_disease_labels().get(disease_key, {}).get('target_col')
        if not target_column_name or target_column_name not in df.columns:
            print(f"Warning: Target '{target_column_name}' not found for {disease_key}. Skipping.")
            continue

        X = df.drop(columns=[target_column_name])
        y = df[target_column_name]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            random_state=42,
            verbosity=0
        )
        model.fit(X_train, y_train)

        model_path = os.path.join(SUBTYPE_MODELS_DIR, f"{disease_key}.pkl")
        joblib.dump(model, model_path)
        trained_models[disease_key] = model
        print(f"  → {disease_key} model saved.")

    return trained_models

# --- Visualizations (保持空实现) ---
def generate_visualizations(X_test, y_test, model, subtype_models, data):
    print("\n--- Skipping visualization generation as requested ---")

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting model training process...")

    try:
        df_raw = load_data(DATA_PATH)
        df = feature_engineering(df_raw.copy())
        print("Data preprocessing complete.")
    except Exception as e:
        print(f"ERROR in data loading: {e}")
        exit(1)

    # 训练主风险模型（用于 30 秒小测）
    try:
        risk_model, scaler, X_test_risk, y_test_risk = train_risk_model(df.copy())
    except Exception as e:
        print(f"ERROR training risk model: {e}")
        risk_model, scaler = None, None

    # 训练亚型模型
    subtype_models = {}
    if DISEASE_ENUM.get_all_diseases():
        try:
            subtype_models = train_subtype_models(df.copy())
        except Exception as e:
            print(f"ERROR training subtype models: {e}")

    # 可选：生成可视化
    generate_visualizations(X_test_risk, y_test_risk, risk_model, subtype_models, df)

    print("\nModel training process finished.")