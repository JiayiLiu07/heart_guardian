import pandas as pd
import xgboost as xgb
import joblib
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%levelname]s] %(message)s")

def train_model():
    try:
        df = pd.read_csv('data/cardio_train.csv')
        features = ['age', 'height', 'weight', 'gender', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']
        scaler = StandardScaler()
        label_encoders = {}
        
        df['age'] = df['age'] / 365.0
        for feature in ['gender', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']:
            label_encoders[feature] = LabelEncoder()
            df[feature] = label_encoders[feature].fit_transform(df[feature])
        
        X = df[features]
        X_scaled = scaler.fit_transform(X)
        y = df['cardio']
        
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        model.fit(X_scaled, y)
        
        os.makedirs('models', exist_ok=True)
        joblib.dump(model, 'models/xgboost_model.pkl')
        joblib.dump(scaler, 'models/scaler.pkl')
        joblib.dump(label_encoders, 'models/label_encoders.pkl')
        logging.info("模型、scaler和label_encoders保存成功")
    except Exception as e:
        logging.error(f"训练失败: {str(e)}")
        raise

if __name__ == "__main__":
    train_model()