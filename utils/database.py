# utils/database.py
import os
import json
import redis
import numpy as np
import hashlib
from typing import Any, Dict, Optional, Tuple
import logging
from datetime import datetime
from streamlit.delta_generator import DeltaGenerator

class RedisManager:
    def __init__(self):
        self.r = None
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_db = int(os.getenv("REDIS_DB", 0))
            
            self.r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
            self.r.ping()
            logging.info("Redis 连接成功")
        except (redis.ConnectionError, ValueError) as e:
            logging.warning(f"Redis 连接失败 ({e})，将使用 JSON 文件存储")
            self.r = None
    
    def _convert_to_serializable(self, obj):
        """Convert non-serializable types (e.g., numpy types, datetime) to JSON-serializable types."""
        if isinstance(obj, DeltaGenerator):              
            return "[Streamlit-Widget]"                   
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    def set(self, key: str, value: Any) -> None:
        if self.r:
            try:
                serializable_value = self._convert_to_serializable(value)
                serialized_value = json.dumps(serializable_value)
                self.r.set(key, serialized_value)
                logging.debug(f"成功存储数据到 Redis，键: {key}")
            except TypeError as e:
                logging.error(f"无法序列化键 '{key}' 的数据: {e}")
                self._save_to_json(key, value)
            except Exception as e:
                logging.error(f"存储数据到 Redis 失败，键 '{key}': {e}")
                self._save_to_json(key, value)
        else:
            self._save_to_json(key, value)
    
    def get(self, key: str) -> Dict:
        if self.r:
            try:
                data = self.r.get(key)
                if data:
                    return json.loads(data)
                else:
                    logging.info(f"Redis 中未找到键 '{key}'")
                    return {}
            except json.JSONDecodeError:
                logging.error(f"无法解析 Redis 中的 JSON 数据，键 '{key}'")
                return {}
            except Exception as e:
                logging.error(f"从 Redis 获取数据失败，键 '{key}': {e}")
                return {}
        else:
            return self._load_from_json(key)
            
    def delete(self, key: str) -> None:
        if self.r:
            self.r.delete(key)
        else:
            file_path = f'data/users/{key}.json'
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    logging.error(f"删除 JSON 文件 '{file_path}' 失败: {e}")

    def _save_to_json(self, key: str, value: Any) -> None:
        """Saves data to a JSON file."""
        os.makedirs('data/users', exist_ok=True)
        file_path = f'data/users/{key}.json'
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._convert_to_serializable(value), f, indent=2, ensure_ascii=False)
            logging.debug(f"成功保存数据到 JSON 文件: {file_path}")
        except TypeError as e:
            logging.error(f"无法序列化数据到 JSON，键 '{key}': {e}")
        except Exception as e:
            logging.error(f"保存到 JSON 文件 '{file_path}' 失败: {e}")

    def _load_from_json(self, key: str) -> Dict:
        """Loads data from a JSON file."""
        file_path = f'data/users/{key}.json'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging.debug(f"成功从 JSON 文件加载数据: {file_path}")
                return data
        except FileNotFoundError:
            logging.info(f"JSON 文件未找到: {file_path}")
            return {}
        except json.JSONDecodeError:
            logging.error(f"无法解析 JSON 文件: {file_path}")
            return {}
        except Exception as e:
            logging.error(f"加载 JSON 文件 '{file_path}' 失败: {e}")
            return {}

class UserManager:
    def __init__(self, redis_manager: RedisManager):
        self.redis = redis_manager
        self.default_user_data = {
            'username': 'User',
            'password': None,
            'basic_info': {'age': 50, 'height': 170, 'weight': 70, 'gender': '男', 'cholesterol': 1, 'gluc': 1},
            'disease_tags': ['HTN:WCHT'],
            'risk_score': 0.0,
            'risk_history': [],
            'symptom_history': [],
            'medication_history': [],
            'food_log': [],
            'weekly_menu': {},
            'today_data': {'ap_hi': 120.0, 'ap_lo': 80.0, 'heart_rate': 70.0, 'sodium_intake': 0.0},
            'case_files': [],
            'chat_history': [{"role": "assistant", "content": "您好！我是您的AI健康顾问，有什么可以帮您的？"}],
            'saved_tips': [],
            'daily_checkins': [],
            'rehab_plan': []
        }
    
    def get_user_info(self, user_id: str) -> Dict:
        user_data = self.redis.get(user_id)
        if not user_data:
            logging.info(f"用户 ID {user_id[:10]}... 未找到，返回默认用户数据")
            return self.default_user_data.copy()
        return user_data
    
    def update_user_info(self, user_id: str, updates: Dict) -> None:
        current_data = self.get_user_info(user_id)
        current_data.update(updates)
        self.redis.set(user_id, current_data)
        logging.debug(f"更新用户数据，ID: {user_id[:10]}...")
    
    def delete_user(self, user_id: str) -> None:
        self.redis.delete(user_id)
        logging.info(f"删除用户，ID: {user_id[:10]}...")
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user with username and password, return user_id if successful."""
        # Normalize username to lowercase for consistency
        username_normalized = username.lower()
        user_id = hashlib.sha256(username_normalized.encode()).hexdigest()
        user_data = self.redis.get(user_id)

        if not user_data or 'password' not in user_data or not user_data['password']:
            logging.info(f"认证失败: 用户 '{username}' 未找到或密码未设置")
            return None

        stored_password_hash = user_data['password']
        input_password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if stored_password_hash == input_password_hash:
            logging.info(f"认证成功: 用户 '{username}'")
            # Update username in DB if it differs (case-insensitive)
            if user_data.get('username', '').lower() != username_normalized:
                user_data['username'] = username
                self.redis.set(user_id, user_data)
                logging.debug(f"更新用户名到数据库: {username}")
            return user_id
        else:
            logging.info(f"认证失败: 用户 '{username}' 密码错误")
            return None
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        if not username or not password:
            return False, "用户名和密码不能为空"

        # Normalize username to lowercase for user_id generation
        username_normalized = username.lower()
        user_id = hashlib.sha256(username_normalized.encode()).hexdigest()
        new_user_data = {
            **self.default_user_data,
            'username': username,  # Store original username (with case)
            'password': hashlib.sha256(password.encode()).hexdigest()
        }
        self.redis.set(user_id, new_user_data)
        logging.info(f"注册成功: 用户 '{username}' (ID: {user_id[:10]}...)")
        return True, user_id