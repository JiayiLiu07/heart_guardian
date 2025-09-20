# utils/database.py
import logging
import redis
import json
import hashlib
import os

class RedisManager:
    def __init__(self):
        try:
            # 连接到 Redis，使用环境变量或默认配置
            self.client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True  # 自动解码字符串
            )
            # 测试连接
            self.client.ping()
            logging.info("Redis 连接成功")
        except Exception as e:
            logging.error(f"Redis 连接失败: {str(e)}")
            raise

    def exists(self, key):
        """检查键是否存在"""
        try:
            return self.client.exists(key)
        except Exception as e:
            logging.error(f"Redis exists 错误: {str(e)}")
            return False

    def get(self, key):
        """获取键的值"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)  # 解析 JSON 字符串为字典
            return None
        except Exception as e:
            logging.error(f"Redis get 错误: {str(e)}")
            return None

    def set(self, key, value):
        """设置键值对"""
        try:
            self.client.set(key, json.dumps(value))  # 将字典转换为 JSON 字符串
            return True
        except Exception as e:
            logging.error(f"Redis set 错误: {str(e)}")
            return False

class UserManager:
    def __init__(self, redis_manager):
        self.redis = redis_manager

    def login_user(self, username, hashed_password):
        """
        Authenticate a user by checking username and hashed password.
        Returns user_id if successful, None otherwise.
        """
        try:
            user_data = self.redis.get(f"user:{username}")
            if user_data and user_data.get('password') == hashed_password:
                return user_data.get('user_id', username)
            return None
        except Exception as e:
            logging.error(f"Login error for {username}: {str(e)}")
            return None

    def register_user(self, username, password):
        """
        Register a new user with username and hashed password.
        Returns (success, message).
        """
        try:
            if self.redis.exists(f"user:{username}"):
                return False, "用户名已存在"
            user_id = hashlib.sha256(username.encode()).hexdigest()[:10]
            user_data = {
                'user_id': user_id,
                'password': hashlib.sha256(password.encode()).hexdigest(),
                'username': username
            }
            self.redis.set(f"user:{username}", user_data)
            return True, "注册成功"
        except Exception as e:
            logging.error(f"Registration error for {username}: {str(e)}")
            return False, str(e)

    def get_user_info(self, user_id):
        """
        Retrieve user info by user_id.
        """
        try:
            # Placeholder: Fetch user data from Redis
            return {
                'disease_tags': ['HTN:WCHT'],
                'today_data': {'ap_hi': 120.0, 'ap_lo': 80.0, 'heart_rate': 70.0},
                'cardio_daily': [],
                'symptom_history': [],
                'medication_history': [],
                'risk_score': 0.0,
                'basic_info': {'age': 30.0, 'gender': '男', 'height': 170.0, 'weight': 70.0}
            }
        except Exception as e:
            logging.error(f"Error fetching user info for {user_id}: {str(e)}")
            return {}