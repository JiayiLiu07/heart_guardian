# app.py
import streamlit as st
import logging
import sys
from pathlib import Path

# 添加日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 页面配置
st.set_page_config(
    page_title="CardioGuard AI 健康管理平台",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 页面映射表 ====================
# key: URL 参数值, value: 模块文件名 (用于导入)
page_mapping = {
    "intro": "p00_intro",
    "auth": "p00_auth",
    "overview": "p01_overview",
    "profile": "p01_profile",
    "nutrition": "p02_nutrition",
    "ai_doctor": "p03_ai_doctor",
    "knowledge": "p04_knowledge",
    "me": "p05_me"
}

def load_page_module(module_name):
    """安全动态加载页面模块"""
    try:
        # 假设所有页面文件都在 pages 目录
        module = __import__(f"pages.{module_name}", fromlist=["main", "render"])
        return module
    except ModuleNotFoundError as e:
        logger.error(f"模块未找到：{e}")
        return None
    except Exception as e:
        logger.error(f"导入失败：{e}")
        return None

def execute_page_module(module):
    """
    执行页面模块，兼容两种入口函数：main() 或 render()
    """
    if hasattr(module, "main"):
        module.main()
    elif hasattr(module, "render"):
        module.render()
    else:
        st.error(f"模块缺少 main 或 render 入口函数")

def main():
    # 从 query_params 获取当前页面，默认为 'intro'
    query_params = st.query_params
    active_page = query_params.get("page", "intro")
    
    # 校验页面合法性
    if active_page not in page_mapping:
        active_page = "intro"
        st.query_params["page"] = "intro"
    
    # 同步到 session_state (可选，用于某些状态保持)
    st.session_state.active_page = active_page
    current_page_param = active_page
    
    logger.info(f"当前页面：{current_page_param}")
    
    # 移除所有对 nav_component 的调用
    # 不再注入通用CSS，因为每个页面都有自己的CSS
    
    # ==================== 加载当前页面内容 ====================
    target_module_name = page_mapping.get(current_page_param)
    
    if target_module_name:
        module = load_page_module(target_module_name)
        if module:
            try:
                # 使用兼容函数执行页面
                execute_page_module(module)
            except Exception as e:
                logger.error(f"执行页面失败：{e}")
                st.error(f"页面执行出错：{e}")
        else:
            st.error(f"无法加载模块：{target_module_name}")
    else:
        st.error("⛔ 无效页面配置")

if __name__ == "__main__":
    main()