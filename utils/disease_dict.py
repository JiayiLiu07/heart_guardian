# utils/disease_dict.py
from enum import Enum

class DISEASE_ENUM(Enum):
    ischemic = {"label": "缺血性心脏病", "icon": "❤️‍🩹", "diet_tip": "低脂低盐"}
    hypertension = {"label": "高血压", "icon": "🩺", "diet_tip": "低盐饮食"}
    heart_failure = {"label": "心力衰竭", "icon": "❤️", "diet_tip": "低钠饮食"}
    arrhythmia = {"label": "心律失常", "icon": "📈", "diet_tip": "均衡饮食，避免刺激物"}
    coronary_artery = {"label": "冠状动脉疾病", "icon": "🩺", "diet_tip": "低胆固醇饮食"}
    cardiomyopathy = {"label": "心肌病", "icon": "❤️", "diet_tip": "低盐低脂"}
    valve_disease = {"label": "心瓣膜病", "icon": "🩺", "diet_tip": "均衡饮食"}
    pericarditis = {"label": "心包炎", "icon": "❤️", "diet_tip": "低盐饮食"}
    congenital_heart = {"label": "先天性心脏病", "icon": "👶", "diet_tip": "均衡饮食"}
    aortic_disease = {"label": "主动脉疾病", "icon": "🩺", "diet_tip": "低盐饮食"}
    myocarditis = {"label": "心肌炎", "icon": "❤️", "diet_tip": "低脂饮食"}
    endocarditis = {"label": "心内膜炎", "icon": "🩺", "diet_tip": "均衡饮食"}
    peripheral_artery = {"label": "外周动脉疾病", "icon": "🩺", "diet_tip": "低胆固醇饮食"}
    rheumatic_heart = {"label": "风湿性心脏病", "icon": "❤️", "diet_tip": "低盐饮食"}
    atrial_fibrillation = {"label": "心房颤动", "icon": "📈", "diet_tip": "避免咖啡因"}
    none = {"label": "无", "icon": "✅", "diet_tip": "均衡饮食"}