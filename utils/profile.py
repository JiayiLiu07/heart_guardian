# utils/profile.py
import json
import os
from typing import Dict, Any

def load_profile_data(user_id: str) -> Dict[str, Any]:
    """加载用户档案"""
    profile_path = f"data/profiles/{user_id}.json"
    if not os.path.exists(profile_path):
        return {}
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载档案失败: {e}")
        return {}

def save_profile_data(user_id: str, data: Dict[str, Any]):
    """保存用户档案"""
    os.makedirs("data/profiles", exist_ok=True)
    profile_path = f"data/profiles/{user_id}.json"
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)