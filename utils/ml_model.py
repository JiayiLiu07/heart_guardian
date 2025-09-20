import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from utils.config import Config
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class CVDRiskPredictor:
    def __init__(self, model_path='models/xgboost_model.pkl', scaler_path='models/scaler.pkl', encoder_path='models/label_encoders.pkl'):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.encoder_path = encoder_path
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.features = ['age', 'height', 'weight', 'gender', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']
        self.model = self._load_or_train_model()
    
    def _load_or_train_model(self):
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path) and os.path.exists(self.encoder_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.label_encoders = joblib.load(self.encoder_path)
                logging.info("成功加载现有模型、scaler和label_encoders")
                return self.model
            else:
                logging.info("模型文件缺失，训练新模型")
                return self._train_new_model()
        except Exception as e:
            logging.error(f"加载模型失败: {str(e)}，训练新模型")
            return self._train_new_model()
    
    def _train_new_model(self):
        try:
            df = pd.read_csv('data/cardio_train.csv')
            self.scaler = StandardScaler()
            self.label_encoders = {}
            model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
            
            X = self._preprocess_data(df)
            y = df['cardio']
            
            model.fit(X, y)
            
            os.makedirs('models', exist_ok=True)
            joblib.dump(model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.label_encoders, self.encoder_path)
            logging.info("新模型训练并保存成功")
            return model
        except Exception as e:
            logging.error(f"训练模型失败: {str(e)}")
            raise
    
    def _preprocess_data(self, df):
        df = df.copy()
        if 'age' in df.columns:
            df['age'] = df['age'] / 365.0
        
        for feature in ['gender', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']:
            if feature in df.columns and feature not in self.label_encoders:
                self.label_encoders[feature] = LabelEncoder()
                df[feature] = self.label_encoders[feature].fit_transform(df[feature])
        
        X = df[self.features]
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled
    
    def predict_risk(self, user_data):
        try:
            df = pd.DataFrame([user_data], columns=self.features)
            if 'age' in df:
                df['age'] = df['age'] / 365.0
            
            for feature in ['gender', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']:
                if feature in self.label_encoders:
                    df[feature] = self.label_encoders[feature].transform([df[feature].iloc[0]])[0]
            
            X_scaled = self.scaler.transform(df)
            risk_score = float(self.model.predict_proba(X_scaled)[:, 1][0] * 100)
            return risk_score
        except Exception as e:
            logging.error(f"预测风险失败: {str(e)}")
            return 0.0