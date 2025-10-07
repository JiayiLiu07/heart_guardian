import streamlit as st
import pandas as pd
import re
from pages.p01_profile import load_profile_data

# --- Dummy Data for Knowledge Base ---
KNOWLEDGE_BASE = {
    "高血压": {
        "简介": "高血压是指动脉血压持续升高的一种慢性疾病。",
        "诊断标准": {
            "普通高血压": "收缩压 ≥ 140 mmHg 或 舒张压 ≥ 90 mmHg。",
            "白大衣高血压": "在医疗环境中血压升高，在家中正常。",
            "隐匿性高血压": "在医疗环境中血压正常，在家中升高。",
        },
        "病因与风险因素": {
            "主要风险因素": "年龄增长、家族史、肥胖、高盐饮食、缺乏运动、吸烟、饮酒、精神压力大等。",
            "并发症": "可导致心脏病、脑卒中、肾脏损害、眼底病变等。",
        },
        "处理流程": "1. 生活方式干预（减盐、减重、戒烟限酒、规律运动）。2. 药物治疗（根据血压水平和合并症选择）。3. 定期监测。",
        "相关文章": ["如何有效控制血压", "高盐饮食的危害"]
    },
    "冠心病": {
        "简介": "冠心病是指冠状动脉血管发生动脉粥样硬化病变而引起血管腔狭窄或阻塞，造成心肌缺血、缺氧或坏死。",
        "类型": {
            "稳定型心绞痛": "由体力活动诱发，休息后缓解。",
            "急性冠脉综合征 (ACS)": "包括不稳定型心绞痛、心肌梗死，是紧急情况。",
        },
        "症状": "主要表现为胸骨后疼痛、压迫感，可放射至左肩、颈部或下颌，常伴有心悸、气短、出冷汗等。",
        "风险因素": "同高血压，并强调高血脂、糖尿病、吸烟是重要诱因。",
        "预防与管理": "控制风险因素、健康饮食、规律运动、遵医嘱服药。",
        "相关文章": ["冠心病的早期识别", "心脏支架手术"]
    },
    "心力衰竭": {
        "简介": "心力衰竭是指心脏泵血功能受损，无法满足身体对血液和氧气的需求。",
        "病因": "常见于冠心病、高血压、心肌病、瓣膜病等。",
        "症状": "活动耐力下降、呼吸困难（尤其在夜间或平卧时）、下肢水肿、乏力等。",
        "管理": "药物治疗、生活方式调整（限盐、适度活动）、监测体重。",
    },
    "心律失常": {
        "简介": "心律失常是指心脏跳动的频率、节律或传导发生异常。",
        "常见类型": {
            "房颤 (AFib)": "心房快速而不规则地颤动，增加卒中风险。",
            "早搏": "心跳提前发生，可为房性或室性。",
            "心动过速/过缓": "心率过快或过慢。",
        },
        "症状": "心悸（感觉心跳不规则、过快或过慢）、头晕、乏力、胸闷等。",
        "风险": "特别是房颤，显著增加脑卒中风险。",
        "治疗": "药物、导管消融、起搏器等。",
    }
}

# Helper function to flatten the knowledge base for searching
def flatten_kb(kb_data, parent_key="", separator=" > "):
    items = []
    for key, value in kb_data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_kb(value, new_key, separator))
        else:
            items.append({"path": new_key, "content": str(value)})
    return items

# Convert KB to searchable DataFrame
FLATTENED_KB = flatten_kb(KNOWLEDGE_BASE)
KNOWLEDGE_DF = pd.DataFrame(FLATTENED_KB)

# --- Rendering Functions ---
def render_article_content(title, content, highlight=False):
    border_style = "border: 2px solid #E94560;" if highlight else ""
    st.markdown(f"""
    <div style="background: #ffffff; border-radius: 12px; padding: 15px; margin-bottom: 15px; {border_style}">
        <h4 style='font-size: 18px;'>{title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⭐ 收藏", key=f"collect_{title}"):
        st.info("收藏功能开发中...")
    if st.button("📤 分享", key=f"share_{title}"):
        st.info("分享功能开发中...")

def render_knowledge_tree(data, parent_key="", user_disease=None):
    for key, value in data.items():
        current_path = f"{parent_key} > {key}" if parent_key else key
        highlight = user_disease == key
        
        if isinstance(value, dict):
            with st.expander(current_path, expanded=highlight):
                render_knowledge_tree(value, current_path, user_disease)
        else:
            with st.expander(current_path, expanded=highlight):
                render_article_content(current_path, value, highlight)

def render():
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("请先登录以访问知识库。")
        user_id = 'default_user'
        user_disease = None
    else:
        user_id = st.session_state.user_id
        user_data = load_profile_data(user_id)
        user_disease = user_data.get('cardio_disease', '无心血管疾病') if user_data.get('cardio_disease', '无心血管疾病') != '无心血管疾病' else None

    st.title("心脏健康知识库")

    search_term = st.text_input("搜索知识库:")
    
    col1, col2 = st.columns([0.3, 0.7])

    with col1:
        st.subheader("目录")
        # 置顶用户已患疾病
        if user_disease and user_disease in KNOWLEDGE_BASE:
            st.markdown(f"""
            <div style='background: #ffffff; border: 2px solid #E94560; border-radius: 8px; padding: 10px; margin-bottom: 10px;'>
                <h4>{user_disease}</h4>
                <p>您的已确诊疾病</p>
            </div>
            """, unsafe_allow_html=True)
        render_knowledge_tree(KNOWLEDGE_BASE, user_disease=user_disease)

    with col2:
        st.subheader("文章详情")
        if search_term:
            search_results = KNOWLEDGE_DF[
                KNOWLEDGE_DF['path'].str.contains(search_term, case=False, na=False) |
                KNOWLEDGE_DF['content'].str.contains(search_term, case=False, na=False)
            ]
            if not search_results.empty:
                st.markdown(f"### 搜索结果 ({len(search_results)} 项):")
                for index, row in search_results.iterrows():
                    highlight = user_disease is not None and user_disease in row['path']
                    render_article_content(row['path'], row['content'], highlight)
            else:
                st.info("未找到相关知识。")
        else:
            st.info("请在左侧选择目录，或在上方搜索框输入关键词查看详情。")

if __name__ == "__main__":
    render()