# utils/api.py
import os
import streamlit as st
import time
import logging
import re
import threading
from openai import OpenAI
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format="{asctime} [{levelname}] {message}", style='{')
logger = logging.getLogger(__name__)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# SVG 清理函数
def clean_svg(svg: str) -> str:
    """清理 SVG 内容，确保格式正确"""
    svg = svg.strip()
    if not svg.startswith('<svg'):
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="240">{svg}</svg>'
    if not svg.endswith('</svg>'):
        svg = svg + '</svg>'
    # 移除非法字符
    svg = re.sub(r'[^\x00-\x7F<>/="\'\s-:#]+', '', svg)
    return svg

# 超时装饰器
def timeout(seconds):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            if thread.is_alive():
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            if exception[0]:
                raise exception[0]
            return result[0]
        return wrapper
    return decorator

# AI 图生成
def ai_plot(prompt: str, key: str, timeout_duration: int = 8, max_retries: int = 3):
    """VLLM 生成 SVG + 中文解读；失败→兜底"""
    logger.info(f"生成 AI 图，prompt: {prompt[:50]}...")
    place = st.empty()
    place.markdown(skeleton, unsafe_allow_html=True)

    @timeout(timeout_duration)
    def try_api_call(prompt):
        full_prompt = f"""
        根据以下要求生成内容：
        1. 基于 cardio_train.csv 数据集，生成 {prompt}，返回标准 SVG 格式（必须以 <svg> 开头，以 </svg> 结尾）。
        2. 提供中文解读，格式为：
           【中文解读】
           **关键指标分析**：
           1. [指标1]：[指标描述]
           2. [指标2]：[指标描述]
           3. [指标3]：[指标描述]
           **建议**：[具体建议]
        确保 SVG 代码完整，解读清晰，使用简洁中文。
        """
        logger.info(f"完整 prompt: {full_prompt[:100]}...")
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            stream=False
        )
        return resp.choices[0].message.content

    for attempt in range(max_retries):
        try:
            raw = try_api_call(prompt)
            logger.info(f"API 响应成功，内容长度: {len(raw)}")
            # 解析响应
            if "【中文解读】" in raw:
                svg, desc = raw.split("【中文解读】", 1)
                svg = clean_svg(svg.strip())
            else:
                svg = ""
                desc = raw or "⚠️ AI 未返回详细解读，建议稍后重试。"
            desc = emojify(desc.strip())
            place.empty()
            # 上下排版
            if svg.strip() and '<svg' in svg and '</svg>' in svg:
                st.markdown(svg, unsafe_allow_html=True)
                logger.info("SVG 图显示成功")
            else:
                st.markdown(fallback_svg, unsafe_allow_html=True)
                logger.warning("无有效 SVG，使用兜底图")
            st.markdown(f'<div class="desc-card">{desc}</div>', unsafe_allow_html=True)
            logger.info("文字显示成功")
            return
        except TimeoutError:
            logger.warning(f"尝试 {attempt + 1}/{max_retries} 超时")
            if attempt < max_retries - 1:
                time.sleep(2)  # 重试间隔
        except Exception as e:
            logger.error(f"尝试 {attempt + 1}/{max_retries} 失败：{str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
    # 兜底
    place.empty()
    st.info("AI 作图超时或失败，先给您看示意图 ⏱️")
    st.markdown(fallback_svg, unsafe_allow_html=True)
    st.markdown("""
    <div class="desc-card">
        💡 <strong>建议</strong>：检查网络或稍后重试。以下是关键指标分析：
        <ol>
            <li><strong>🩺 血压</strong>：高血压显著增加心血管风险。</li>
            <li><strong>🧪 胆固醇</strong>：高胆固醇可能导致血管堵塞。</li>
            <li><strong>🎂 年龄</strong>：年龄越大，患病风险越高。</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    logger.warning("进入兜底逻辑")
    if st.button("🔁 重新生成", key=key):
        ai_plot(prompt, key, timeout_duration, max_retries)

skeleton = '''
<div class="skeleton"></div>
<style>
.skeleton{height:240px;background:linear-gradient(90deg,rgba(0,229,255,.1) 25%,rgba(0,229,255,.3) 50%,rgba(0,229,255,.1) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:12px;}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
</style>
'''

fallback_svg = '''
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="240">
  <rect width="600" height="240" fill="#1a237e"/>
  <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#000000" font-size="20">
    AI Chart Placeholder
  </text>
</svg>
'''

def emojify(text: str) -> str:
    """给常见健康关键词自动加 emoji & 高亮，清理排版"""
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'\s+', ' ', text.strip())
    emoji_map = {
        r"\b风险\b": "🚨 风险",
        r"\b建议\b": "💡 建议",
        r"\b运动\b": "🏃 运动",
        r"\b饮食\b": "🥗 饮食",
        r"\b血压\b": "🩺 血压",
        r"\b吸烟\b": "🚭 吸烟",
        r"\b睡眠\b": "🌙 睡眠",
        r"\b胆固醇\b": "🧪 胆固醇",
        r"\bBMI\b": "⚖️ BMI",
        r"\b年龄\b": "🎂 年龄",
        r"\b血糖\b": "🩺 血糖",
        r"\b心脏\b": "❤️ 心脏",
    }
    for pattern, repl in emoji_map.items():
        text = re.sub(pattern, repl, text, flags=re.I)
    text = re.sub(r"(\d+\.?\d*)", r"**`\1`**", text)
    text = re.sub(r'(\d+\.\s*\[.*?\]\s*:\s*\[.*?\])', r'<li>\1</li>', text)
    if '<li>' in text:
        text = f'<ol>{text}</ol>'
    return text