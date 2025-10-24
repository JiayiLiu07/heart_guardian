import pickle
import os
import pandas as pd
from xgboost import XGBClassifier

def load_model(model_path):
    """
    加载预训练的 XGBoost 模型

    参数:
        model_path (str): 模型文件的路径（如 'assets/xgb_risk.pkl'）

    返回:
        XGBClassifier: 加载的 XGBoost 模型
    """
    try:
        model_file = os.path.join(os.path.dirname(__file__), "..", model_path)
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        raise Exception(f"加载模型失败: {e}")

def predict_risk(model, data):
    """
    使用 XGBoost 模型预测心血管疾病风险

    参数:
        model (XGBClassifier): 加载的 XGBoost 模型
        data (pd.DataFrame): 输入数据，包含特征列

    返回:
        np.array: 预测概率
    """
    return model.predict_proba(data)[:, 1]

def predict_subtype(model, data):
    """
    使用 XGBoost 模型预测心血管疾病亚型

    参数:
        model (XGBClassifier): 加载的 XGBoost 模型
        data (pd.DataFrame): 输入数据，包含特征列

    返回:
        np.array: 预测的亚型标签
    """
    return model.predict(data)