# utils/api.py
from openai import OpenAI
import os
import logging

logger = logging.getLogger(__name__)

def initialize_client(api_key):
    """初始化 OpenAI 或 DashScope 客户端"""
    try:
        base_url = "https://api.dashscope.com" if "DASHSCOPE" in os.environ and os.getenv("DASHSCOPE_API_KEY") == api_key else None
        client = OpenAI(api_key=api_key, base_url=base_url)
        logger.info("Client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        return None

def get_image_and_explanation_from_vllm(client, prompt, image_model, additional_params):
    """从 VLLM 获取图像和解释"""
    try:
        response = client.chat.completions.create(
            model=image_model,
            messages=[{"role": "user", "content": prompt}],
            **additional_params
        )
        explanation = response.choices[0].message.content
        image_base64 = None  # 替换为实际 VLLM 图像生成逻辑（目前占位）
        logger.info("Successfully generated image and explanation")
        return image_base64, explanation
    except Exception as e:
        logger.error(f"VLLM request failed: {e}")
        return None, f"生成失败: {e}"