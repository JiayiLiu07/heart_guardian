# utils/profile.py
import pandas as pd
import os

USERS_FOLDER = 'users'
os.makedirs(USERS_FOLDER, exist_ok=True)

def load_profile_data(user_id):
    path = os.path.join(USERS_FOLDER, f"{user_id}_profile.csv")
    if os.path.exists(path):
        df = pd.read_csv(path, encoding='utf-8')
        profile = df.iloc[0].to_dict()
        # 修复所有列表字段
        for key in ['cardio_diseases', 'allergens', 'habits']:
            val = profile.get(key)
            if isinstance(val, str) and val.strip():
                try:
                    profile[key] = eval(val)
                except:
                    profile[key] = []
            elif not isinstance(val, list):
                profile[key] = []
        return profile
    return {'cardio_diseases': [], 'allergens': [], 'habits': []}