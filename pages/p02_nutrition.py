# pages/p02_nutrition.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import sys
import os
import json
import base64  # ★★★ 新增导入
import time
from collections import Counter

# --- 路径配置 ---
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
try:
    from assets.cardio_recipes import MAIN_RECIPE_DB, FALLBACK_POOL, get_fallback_recipe
    DATA_LOADED = True
except ImportError as e:
    st.error(f"❌ 无法加载食谱数据库：{e}")
    DATA_LOADED = False

st.set_page_config(page_title="AI 营养师 · CardioGuard AI", page_icon="🥗", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# ★★★ 核心改动：跨页面数据恢复逻辑 ★★★
# ==============================================================================
def load_profile():
    """
    优先级：query_params > session_state > 本地文件
    用于解决 Streamlit 云端部署后 Session 断开导致数据丢失的问题
    """
    # 1. 优先从 URL query params 恢复
    if 'profile_data' in st.query_params:
        try:
            b64_str = st.query_params['profile_data']
            # 补齐 padding
            b64_str += '=' * ((4 - len(b64_str) % 4) % 4)
            json_str = base64.urlsafe_b64decode(b64_str).decode('utf-8')
            data = json.loads(json_str)
            st.session_state['profile'] = data
            return data
        except Exception:
            pass

    # 2. 其次从 session_state 取
    if 'profile' in st.session_state:
        return st.session_state['profile']

    # 3. 最后尝试从本地文件读 (云端环境通常无效，但本地开发有用)
    try:
        # 假设文件在同级 users 文件夹或根目录，根据实际情况调整路径
        possible_paths = [
            "users/heart_profile_data.json",
            "heart_profile_data.json",
            os.path.join(os.path.dirname(__file__), "..", "users", "heart_profile_data.json")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                    st.session_state['profile'] = data
                    return data
    except Exception:
        pass
    
    return {}

# 在页面加载时执行恢复
if 'profile' not in st.session_state:
    st.session_state['profile'] = load_profile()

# 全局快捷访问
profile = st.session_state['profile']

# ==============================================================================
# 原有常量与逻辑定义
# ==============================================================================
DATA_FILE = "heart_profile_data.json" # 保留变量以防旧逻辑引用，但主要逻辑已切换

CARDIO_DISEASES = {
    "缺血性心脏病 🫀": ["慢性冠脉综合征", "稳定型心绞痛", "缺血性心肌病", "无症状心肌缺血", "急性冠脉综合征", "不稳定性心绞痛", "STEMI", "NSTEMI"],
    "高血压心脏病 🩸": ["高血压性左心室肥厚", "高血压性心力衰竭", "高血压性肾功能损害"],
    "心律失常 ⚡": ["房颤/房扑", "阵发性室上性心动过速", "室性心动过速/室颤", "早搏（房性/室性）", "病态窦房结综合征", "房室传导阻滞"],
    "心肌病 💓": ["扩张型心肌病 (DCM)", "肥厚型心肌病 (HCM)", "限制型心肌病 (RCM)", "致心律失常性右室心肌病 (ARVC)", "代谢性心肌病"],
    "瓣膜性心脏病 🫁": ["二尖瓣病变", "主动脉瓣病变", "三尖瓣/肺动脉瓣病变", "风湿性心脏病"],
    "先天性心脏病 👶": ["房间隔缺损 (ASD)", "室间隔缺损 (VSD)", "动脉导管未闭 (PDA)", "法洛四联症", "大动脉转位", "主动脉缩窄", "肺动脉瓣狭窄"],
    "主动脉疾病 🩺": ["主动脉瘤", "主动脉夹层", "主动脉缩窄", "主动脉炎"]
}

ALLERGENS_LIST = ["花生 🥜", "树坚果 🌰", "海鲜 🦐", "乳制品 🥛", "大豆 🫘", "鸡蛋 🥚", "麸质 🍞", "芝麻 🌾"]
DIET_PREFERENCES_LIST = ["中式清淡 🥢", "严格低钠 🧂", "无酒精/无酒酿 🚫🍷", "低嘌呤 🍗", "低组胺/无发酵 🍇", "无亚硫酸盐 🍷", "高蛋白 🥩", "低脂饮食 🥗", "糖尿病友好 🩸", "软食易消化 🥣", "高纤维通便 🌽", "地中海/DASH风格 🫒"]
MEAL_NAMES = {"Breakfast": "早餐 🌅", "Lunch": "午餐 ☀️", "Dinner": "晚餐 🌙"}

DIET_TIPS = [
    {"title": "🧂【控盐减钠篇】", "items": ["🕵️‍♂️ 隐形盐警惕", "🌿 巧用香料", "⏱️ 出锅前放盐", "⚠️ 警惕低钠盐", "🏷️ 阅读标签"]},
    {"title": "🛢️【油脂选择篇】", "items": ["✅ 好油坏油分清", "🥄 每日限量", "🚫 远离反式脂肪", "🥜 坚果适量", "🐟 吃鱼有讲究"]},
    {"title": "🥦【蔬果粗粮篇】", "items": ["🌈 彩虹饮食", "🥣 燕麦早餐", "🌾 全谷替代", "🫘 豆类优质蛋白", "🍎 水果不过量"]},
    {"title": "🥩【肉类选择篇】", "items": ["📉 少吃红肉", "🍗 去皮禽肉", "🥘 内脏限量"]},
    {"title": "🍵【饮品习惯篇】", "items": ["🍷 限酒护心", "🍃 淡茶为宜", "💧 足量饮水", "🥤 远离甜饮料"]},
    {"title": "🍳【烹饪方式篇】", "items": ["🥘 蒸煮炖拌", "🥡 警惕外卖", "🥢 细嚼慢咽"]}
]

# ==============================================================================
# 逻辑函数 (适配新的 profile 获取方式)
# ==============================================================================
def get_tag_color(tag_name):
    tag_colors = {
        "严格低钠": "orange", "无酒精/无酒酿": "red", "低嘌呤": "blue",
        "低组胺/无发酵": "purple", "无亚硫酸盐": "purple", "高蛋白": "green",
        "低脂饮食": "green", "糖尿病友好": "gray", "软食易消化": "purple",
        "高纤维通便": "green", "地中海/DASH风格": "pink", "中式清淡": "gray"
    }
    return tag_colors.get(tag_name, "gray")

def check_profile_sync():
    """
    检查 profile 是否完整。
    现在直接使用全局 profile 变量 (来自 session_state)
    """
    # 如果 profile 为空字典，视为未同步
    if not profile: 
        return False, {}, [], [], []
    
    current_dis = profile.get('diseases', [])
    current_allergens = profile.get('allergies', [])
    current_prefs = profile.get('diet_pref', [])
    
    if not current_dis or not current_prefs: 
        return False, profile, current_dis, current_allergens, current_prefs
    
    return True, profile, current_dis, current_allergens, current_prefs

def filter_candidates(meal_type, allergens, prefs, exclude_names=None):
    if not DATA_LOADED: return []
    if exclude_names is None: exclude_names = set()
    candidates = MAIN_RECIPE_DB.get(meal_type, [])
    hard_tags = ["严格低钠", "无酒精/无酒酿", "低嘌呤", "低组胺/无发酵", "无亚硫酸盐", "糖尿病友好", "软食易消化"]
    active_hard = [p for p in prefs if p in hard_tags]
    valid = []
    for r in candidates:
        if r['name'] in exclude_names: continue
        if any(a in r.get('allergens', []) for a in allergens): continue
        if active_hard and not all(t in r.get('tags', []) for t in active_hard): continue
        valid.append(r)
    if not valid:
        for r in candidates:
            if r['name'] in exclude_names: continue
            if any(a in r.get('allergens', []) for a in allergens): continue
            valid.append(r)
    if not valid:
        fb = get_fallback_recipe(meal_type, allergens)
        if fb and fb['name'] not in exclude_names: valid.append(fb)
    return valid

def generate_7day_plan(allergens, prefs):
    days_count = 7
    meal_types = ["Breakfast", "Lunch", "Dinner"]
    days = [(datetime.now() + timedelta(days=i)).strftime("%m月%d日 (%A)") for i in range(days_count)]
    plan = []
    used_names_global = set()
    for day_idx, day_str in enumerate(days):
        day_plan = {"date": day_str, "meals": []}
        for meal in meal_types:
            candidates = filter_candidates(meal, allergens, prefs, used_names_global)
            if candidates:
                chosen = random.choice(candidates)
                used_names_global.add(chosen['name'])
                item = chosen.copy()
                item['meal_type_cn'] = MEAL_NAMES[meal]
                item['day_idx'] = day_idx
                item['meal_type_key'] = meal
                day_plan['meals'].append(item)
            else:
                fb = get_fallback_recipe(meal, allergens)
                if fb:
                    item = fb.copy()
                    if item['name'] not in used_names_global: used_names_global.add(item['name'])
                else:
                    item = {"name": "清淡饮食", "ingredients": "时令蔬菜", "steps": "清炒或水煮。", "nutrition": {"cal": 200, "pro": 5, "carb": 30, "fat": 2}, "tags": ["中式清淡"], "allergens": []}
                item['meal_type_cn'] = MEAL_NAMES[meal]
                item['day_idx'] = day_idx
                item['meal_type_key'] = meal
                day_plan['meals'].append(item)
        plan.append(day_plan)
    return plan

def swap_recipe(day_idx, meal_type_key, current_plan, allergens, prefs):
    used_names = set()
    target_recipe_name = None
    for d in current_plan:
        for m in d['meals']:
            if m['day_idx'] == day_idx and m['meal_type_key'] == meal_type_key: target_recipe_name = m['name']
            else: used_names.add(m['name'])
    candidates = filter_candidates(meal_type_key, allergens, prefs, used_names)
    if candidates:
        candidates = [c for c in candidates if c['name'] != target_recipe_name]
        if candidates:
            new_recipe = random.choice(candidates)
            for d in current_plan:
                for i, m in enumerate(d['meals']):
                    if m['day_idx'] == day_idx and m['meal_type_key'] == meal_type_key:
                        updated = new_recipe.copy()
                        updated['meal_type_cn'] = MEAL_NAMES[meal_type_key]
                        updated['day_idx'] = day_idx
                        updated['meal_type_key'] = meal_type_key
                        d['meals'][i] = updated
                        return current_plan
    return current_plan

def get_disease_subtype(profile_data, disease_name):
    """注意：这里传入的是 profile 字典"""
    for key, value in profile_data.items():
        if key.startswith('subtype_') and disease_name in key:
            return value if value and value != "未知" else "待确认"
    return "待确认"

def extract_ingredients_from_plan(plan):
    all_ingredients = []
    for day in plan:
        for meal in day['meals']:
            ingredients = meal.get('ingredients', '')
            if ingredients:
                if ':' in ingredients: ingredients = ingredients.split(':')[-1]
                if ':' in ingredients: ingredients = ingredients.split(':')[-1]
                for sep in ['、', '，', ',', ' ', '；']:
                    if sep in ingredients:
                        all_ingredients.extend([item.strip() for item in ingredients.split(sep) if item.strip()])
                        break
                else:
                    all_ingredients.append(ingredients.strip())
    return sorted(list(set(all_ingredients))), Counter(all_ingredients)

def categorize_ingredients(ingredients):
    categories = {"🥬 蔬菜菌菇": [], "🥩 肉禽蛋类": [], "🍚 主食五谷": [], "🧂 调味品及其它": []}
    veg_keywords = ["菜", "瓜", "豆", "菇", "葱", "姜", "蒜", "萝卜", "茄", "椒", "笋", "芹", "菠菜", "生菜", "白菜", "西兰花", "豆腐", "木耳", "蘑菇", "青菜", "空心菜", "韭菜", "香菜", "芹菜", "胡萝卜", "土豆", "山药", "芋头", "莲藕", "玉米", "豌豆"]
    meat_keywords = ["肉", "鸡", "鸭", "鱼", "虾", "蛋", "牛", "羊", "猪", "排骨", "腿", "翅", "肝", "肚", "蟹", "贝", "三文鱼", "鳕鱼", "鲈鱼"]
    grain_keywords = ["饭", "米", "粥", "面", "馒头", "包", "饼", "麦", "红薯", "燕麦", "荞麦", "小米", "糯米", "糙米"]
    for ingredient in ingredients:
        categorized = False
        for kw in veg_keywords:
            if kw in ingredient: categories["🥬 蔬菜菌菇"].append(ingredient); categorized = True; break
        if not categorized:
            for kw in meat_keywords:
                if kw in ingredient: categories["🥩 肉禽蛋类"].append(ingredient); categorized = True; break
        if not categorized:
            for kw in grain_keywords:
                if kw in ingredient: categories["🍚 主食五谷"].append(ingredient); categorized = True; break
        if not categorized:
            categories["🧂 调味品及其它"].append(ingredient)
    for k in categories: categories[k] = sorted(list(set(categories[k])))
    return categories

# ==============================================================================
# 主界面
# ==============================================================================
def main():
    # ========== 1. 处理原生动态效果 ==========
    if st.session_state.get('trigger_celebration', False):
        st.session_state['trigger_celebration'] = False
        st.session_state['is_generating'] = False
        st.balloons()
        st.toast("🎉 生成成功！您的专属 7 天食谱已就绪", icon="🥗")
    
    # ========== 2. CSS 样式 ==========
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        :root { --primary: #10B981; --primary-dark: #047857; --primary-light: #D1FAE5; --gray-200: #E5E7EB; --gray-600: #4B5563; --gray-800: #1F2937; --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05); --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1); --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
        .stApp { font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif; background-color: #f8fafc; font-size: 18px; }
        .main > div { padding-top: 0 !important; }
        .block-container { padding: 0 2rem 1rem !important; max-width: 1400px; margin: 0 auto; }
        #MainMenu, footer, section[data-testid="stSidebar"] { display: none !important; }
        .top-navbar { background: white; padding: 0 1.5rem; height: 75px; box-shadow: var(--shadow-sm); display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 9999; border-bottom: 1px solid var(--gray-200); margin-top: 50px; margin-bottom: 0rem; border-radius: 0 0 8px 8px; }
        .nav-logo { font-weight: 700; font-size: 2.0rem; color: var(--primary); cursor: default; display: flex; align-items: center; gap: 8px; }
        .nav-links { display: flex; gap: 10px; }
        .nav-links a { text-decoration: none; color: var(--gray-600); font-weight: 500; padding: 8px 18px; border-radius: 20px; transition: all 0.3s; font-size: 1.2rem; }
        .nav-links a:hover { background-color: var(--primary-light); color: var(--primary); }
        .nav-links a.active { background: var(--primary); color: white; }
        .hero-box { background: linear-gradient(135deg, #10B981 0%, #047857 100%); padding: 1.8rem 1.5rem; border-radius: 24px; text-align: center; color: white; margin: 0.5rem 0 1rem 0; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; }
        .hero-box::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); animation: rotate 20s linear infinite; z-index: 1; }
        .hero-box::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(45deg, rgba(255,255,255,0.05) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.05) 75%, transparent 75%, transparent); background-size: 30px 30px; animation: move 10s linear infinite; z-index: 1; }
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes move { 0% { background-position: 0 0; } 100% { background-position: 30px 30px; } }
        .hero-title, .hero-sub { position: relative; z-index: 2; }
        .hero-title { font-size: 2.5rem; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .hero-sub { font-size: 1.2rem; opacity: 0.95; margin-top: 0.3rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1); }
        .section-title { font-size: 2.0rem; font-weight: 700; color: var(--gray-800); margin: 1.5rem 0 1rem 0; display: flex; align-items: center; gap: 8px; position: relative; }
        .section-title::after { content: ''; flex: 1; height: 2px; background: linear-gradient(90deg, var(--primary), transparent); margin-left: 15px; }
        .subsection-title { font-size: 1.6rem; font-weight: 600; color: var(--gray-800); margin: 1.2rem 0 0.8rem 0; padding-left: 0.6rem; border-left: 4px solid var(--primary); }
        .profile-compact { background: transparent; margin: 0.5rem 0 1.5rem 0; }
        .profile-compact-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; }
        .profile-compact-header .icon { font-size: 2.2rem; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background: var(--primary-light); border-radius: 8px; color: var(--primary-dark); }
        .profile-compact-header .title { font-size: 2.0rem; font-weight: 600; color: var(--gray-800); }
        .profile-compact-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
        .profile-compact-section { background: white; border-radius: 10px; padding: 1rem; border: 1px solid var(--gray-200); box-shadow: var(--shadow-sm); }
        .profile-compact-section-title { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem; font-size: 1.3rem; font-weight: 600; color: var(--gray-700); }
        .profile-compact-section-title .count { background: var(--gray-100); color: var(--gray-600); padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 1.0rem; font-weight: 500; }
        .profile-compact-tags { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .tag-profile { display: inline-flex; align-items: center; padding: 0.4rem 0.8rem; border-radius: 9999px; font-size: 1.1rem; font-weight: 500; line-height: 1.2; border: 1px solid transparent; }
        .tag-profile.disease { background: #FEF3C7; color: #92400e; border-color: #FCD34D; }
        .tag-profile.allergen { background: #FEE2E2; color: #B91C1C; border-color: #FCA5A5; }
        .tag-profile.diet { background: var(--primary-light); color: var(--primary-dark); border-color: #A7F3D0; }
        .tag-profile.subtype { background: #E0E7FF; color: #3730A3; border-color: #A5B4FC; font-size: 1.0rem; padding: 0.2rem 0.6rem; margin-left: 0.2rem; }
        .tag-profile.empty { background: var(--gray-100); color: var(--gray-600); border-color: var(--gray-200); }
        .recipe-card { background: white; border-radius: 14px; padding: 1.2rem; box-shadow: var(--shadow-sm); height: 100%; border: 1px solid var(--gray-200); transition: all 0.3s; }
        .recipe-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--primary); }
        .recipe-title { font-weight: 700; color: var(--primary-dark); font-size: 1.4rem; margin-bottom: 0.5rem; }
        .recipe-meal-type { font-size: 1.5rem; font-weight: 700; color: var(--primary-dark); margin-bottom: 0.5rem; }
        .tag { display: inline-block; padding: 0.3rem 0.6rem; border-radius: 9999px; font-size: 0.9rem; font-weight: 500; margin-right: 0.3rem; margin-bottom: 0.3rem; }
        .tag-green { background-color: var(--primary-light); color: var(--primary-dark); }
        .tag-orange { background-color: #FEF3C7; color: #92400e; }
        .tag-red { background-color: #FEE2E2; color: #b91c1c; }
        .tag-blue { background-color: #E0E7FF; color: #3730a3; }
        .tag-purple { background-color: #F3E8FF; color: #6b21a8; }
        .tag-gray { background-color: #F3F4F6; color: #1F2937; }
        .tag-pink { background-color: #FFE4E6; color: #9f1239; }
        .nutrition-box { display: flex; justify-content: space-around; background: var(--primary-light); padding: 0.8rem; border-radius: 10px; margin: 0.8rem 0; }
        .nutri-item { text-align: center; }
        .nutri-item b { display: block; color: var(--primary-dark); font-size: 1.3rem; }
        .nutri-item span { font-size: 1.0rem; color: var(--gray-600); }
        .stButton > button { border-radius: 30px !important; font-weight: 500 !important; transition: all 0.3s !important; background: white !important; color: var(--primary) !important; border: 1px solid var(--primary) !important; padding: 0.4rem 1rem !important; font-size: 1.0rem !important; }
        div.stButton > button:first-child:hover { background: var(--primary) !important; color: white !important; transform: translateY(-1px); box-shadow: var(--shadow-md) !important; }
        .shopping-category { background: white; border-radius: 14px; padding: 1.2rem; margin-bottom: 1rem; border: 1px solid var(--gray-200); box-shadow: var(--shadow-sm); }
        .shopping-category-title { display: flex; align-items: center; gap: 6px; font-size: 1.4rem; font-weight: 600; color: var(--primary-dark); margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--primary-light); }
        .shopping-category-title span { background: var(--primary-light); color: var(--primary-dark); padding: 0.3rem 0.8rem; border-radius: 9999px; font-size: 1.0rem; font-weight: 500; margin-left: auto; }
        .shopping-items { display: flex; flex-wrap: wrap; gap: 8px; }
        .shopping-item { background: var(--gray-50); border: 1px solid var(--gray-200); border-radius: 9999px; padding: 0.5rem 1rem; font-size: 1.0rem; transition: all 0.2s; cursor: default; }
        .shopping-item:hover { background: var(--primary); color: white; border-color: var(--primary); transform: scale(1.02); }
        .carousel-container { background: white; border-radius: 16px; padding: 1.2rem; margin: 0.5rem 0; border: 1px solid var(--gray-200); box-shadow: var(--shadow-sm); min-height: 200px; }
        .carousel-title { font-size: 1.4rem; font-weight: 600; color: var(--primary-dark); margin-bottom: 0.8rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--primary-light); }
        .carousel-list { list-style: none; padding: 0; margin: 0; }
        .carousel-list li { padding: 8px 0 8px 1.5rem; position: relative; color: var(--gray-600); font-size: 1.1rem; border-bottom: 1px dashed var(--gray-200); line-height: 1.6; }
        .carousel-list li:last-child { border-bottom: none; }
        .carousel-list li::before { content: "•"; color: var(--primary); font-size: 1.2rem; position: absolute; left: 0; top: 6px; }
        .carousel-indicator { text-align: center; font-size: 1.1rem; color: var(--gray-600); font-weight: 500; margin: 0.8rem 0; }
        .carousel-indicator span { color: var(--primary); font-weight: 700; font-size: 1.2rem; }
        .tip-badge { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid var(--gray-200); margin: 1.5rem 0; }
        .tip-badge p { color: var(--gray-600); margin: 0; font-size: 1.1rem; line-height: 1.6; }
        .tip-badge strong { color: var(--primary); font-weight: 600; }
        .day-divider { margin: 2rem 0; border: none; border-top: 2px solid var(--gray-200); }
        .info-box { background: var(--primary-light); padding: 0.8rem 1.2rem; border-radius: 8px; border-left: 3px solid var(--primary); margin: 0.8rem 0; font-size: 1.1rem; line-height: 1.6; }
        .regenerate-container { margin: 1.5rem 0 1rem 0; }
        .row-widget.stHorizontal { gap: 1rem !important; }
        .recipe-card div[style*="font-size:0.8rem"] { font-size: 1.0rem !important; line-height: 1.6; }
    </style>
    
    <!-- 导航栏 -->
    <div class="top-navbar">
        <div class="nav-logo">❤️ CardioGuard AI</div>
        <div class="nav-links">
             <a href="/p00_home">🏠 首页</a>
            <a href="/p01_profile">📋 健康档案</a>
            <a href="/p01_overview">📊 健康总览</a>
            <a href="/p02_nutrition" class="active">🥗 营养建议</a>
            <a href="/p03_ai_doctor">🩺 AI 医生</a>
            <a href="/p04_knowledge">📚 知识库</a>
            <a href="/p05_me">👤 我的中心</a>
        </div>
    </div>
    
    <!-- Hero 区域 -->
    <div class="hero-box">
        <h1 class="hero-title">🥗 AI 营养师</h1>
        <p class="hero-sub">🫀 专为心血管疾病患者设计的智能康复食谱 · 📊 精准数据驱动 · 🤖 AI 智能推导</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not DATA_LOADED:
        st.error("数据库加载失败。")
        return
    
    # 使用更新后的检查逻辑
    is_ready, profile_data, default_dis, default_allergens, default_prefs = check_profile_sync()
    
    if not is_ready:
        missing_parts = []
        if not default_dis: missing_parts.append("疾病信息")
        if not default_prefs: missing_parts.append("饮食偏好")
        missing_text = "、".join(missing_parts) if missing_parts else "相关信息"
        st.warning(f"⚠️ **信息尚未完善**\n\n为了给您生成精准的康复食谱，我们需要您的健康数据。检测到您尚未在 **个人健康档案** 中填写完整的 {missing_text}。")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📝 前往完善档案", use_container_width=True):
                st.switch_page("pages/p01_profile.py")
        # 移除旧的文件同步按钮，因为现在主要依赖 session_state/query_params
        st.stop()
    
    # ========== 健康档案展示 ==========
    st.markdown("""
    <div class="profile-compact">
        <div class="profile-compact-header">
            <span class="icon">🩺</span>
            <span class="title">健康档案</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="profile-compact-grid">', unsafe_allow_html=True)
    
    disease_icons = {"缺血性心脏病": "🫀", "高血压心脏病": "🩸", "心律失常": "⚡", "心肌病": "💓", "瓣膜性心脏病": "🫁", "先天性心脏病": "👶", "主动脉疾病": "🩺"}
    disease_html = """<div class="profile-compact-section"><div class="profile-compact-section-title"><span>🫀 疾病诊断</span><span class="count">{}</span></div><div class="profile-compact-tags">""".format(len(default_dis))
    if default_dis:
        for disease in default_dis:
            icon = disease_icons.get(disease, "❤️")
            # 传入 profile_data 而不是全局 profile 变量，虽然它们是一样的，但保持函数签名一致
            subtype = get_disease_subtype(profile_data, disease)
            disease_html += f'<span class="tag-profile disease">{icon} {disease} <span class="tag-profile subtype">🔹 {subtype}</span></span>'
    else:
        disease_html += '<span class="tag-profile empty">暂无疾病记录</span>'
    disease_html += '</div></div>'
    st.markdown(disease_html, unsafe_allow_html=True)
    
    allergen_html = """<div class="profile-compact-section"><div class="profile-compact-section-title"><span>🚫 过敏源</span><span class="count">{}</span></div><div class="profile-compact-tags">""".format(len(default_allergens) if default_allergens else 0)
    if default_allergens:
        for allergen in default_allergens: allergen_html += f'<span class="tag-profile allergen">🚫 {allergen}</span>'
    else:
        allergen_html += '<span class="tag-profile empty">无过敏源</span>'
    allergen_html += '</div></div>'
    st.markdown(allergen_html, unsafe_allow_html=True)
    
    pref_html = """<div class="profile-compact-section"><div class="profile-compact-section-title"><span>🥗 饮食偏好</span><span class="count">{}</span></div><div class="profile-compact-tags">""".format(len(default_prefs) if default_prefs else 0)
    if default_prefs:
        for pref in default_prefs: pref_html += f'<span class="tag-profile diet">🏷️ {pref}</span>'
    else:
        pref_html += '<span class="tag-profile empty">未设置偏好</span>'
    pref_html += '</div></div>'
    st.markdown(pref_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 智能生成/重新生成按钮 ==========
    st.markdown('<div class="regenerate-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        is_generating = st.session_state.get('is_generating', False)
        has_plan = 'plan' in st.session_state and st.session_state['plan']
        
        if is_generating:
            btn_label = "⏳ 正在生成..."
        elif has_plan:
            btn_label = "🔄 重新生成 7 天食谱"
        else:
            btn_label = "🚀 生成 7 天食谱"
        
        if st.button(
            btn_label, 
            use_container_width=True, 
            type="primary",
            key="unique_regenerate_btn", 
            disabled=is_generating
        ):
            st.session_state['trigger_celebration'] = True
            st.session_state['is_generating'] = True 
            
            with st.spinner("🤖 AI 正在从 500+ 道菜品中为您定制不重复食谱..."):
                time.sleep(0.5) 
                plan = generate_7day_plan(default_allergens, default_prefs)
                st.session_state['plan'] = plan
                st.session_state['params'] = {'all': default_allergens, 'pref': default_prefs}
            
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 结果显示 ==========
    if 'plan' in st.session_state:
        plan = st.session_state['plan']
        params = st.session_state.get('params', {})
        
        st.markdown('<div class="section-title">📅 您的 7 天康复食谱</div>', unsafe_allow_html=True)
        
        for day_idx, day_data in enumerate(plan):
            st.markdown(f'<div class="subsection-title">🗓️ {day_data["date"]}</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            for c_idx, meal in enumerate(day_data['meals']):
                with cols[c_idx]:
                    meal_type_cn = meal.get('meal_type_cn', '餐')
                    meal_name = meal.get('name', '未知菜品')
                    tags = meal.get('tags', [])
                    tag_html = ""
                    for tag in tags:
                        color = get_tag_color(tag)
                        tag_html += f'<span class="tag tag-{color}">{tag}</span>'
                    nutrition = meal.get('nutrition', {})
                    cal = nutrition.get('cal', 0); pro = nutrition.get('pro', 0); fat = nutrition.get('fat', 0)
                    ingredients = meal.get('ingredients', '暂无食材信息')
                    if ':' in ingredients: ingredients = ingredients.split(':')[-1]
                    if ':' in ingredients: ingredients = ingredients.split(':')[-1]
                    steps = meal.get('steps', '暂无步骤信息')
                    if len(steps) > 80: steps = steps[:80] + "..."
                    
                    st.markdown(f"""
                    <div class="recipe-card">
                        <div class="recipe-meal-type">{meal_type_cn}</div>
                        <div class="recipe-title">{meal_name}</div>
                        <div>{tag_html}</div>
                        <div class="nutrition-box">
                            <div class="nutri-item"><b>{cal}</b><span>千卡</span></div>
                            <div class="nutri-item"><b>{pro}g</b><span>蛋白</span></div>
                            <div class="nutri-item"><b>{fat}g</b><span>脂肪</span></div>
                        </div>
                        <div style="margin-bottom:5px;"><b>🛒 食材:</b> {ingredients}</div>
                        <div style="line-height:1.6;"><b>👨‍🍳 做法:</b> {steps}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    btn_key = f"swap_{day_idx}_{meal.get('meal_type_key', 'Breakfast')}_{c_idx}"
                    if st.button("🔄 换一道", key=btn_key, use_container_width=True):
                        new_plan = swap_recipe(day_idx, meal.get('meal_type_key', 'Breakfast'), plan, params.get('all', default_allergens), params.get('pref', default_prefs))
                        st.session_state['plan'] = new_plan
                        st.rerun()
            if day_idx < len(plan) - 1:
                st.markdown('<hr class="day-divider">', unsafe_allow_html=True)
        
        # 购物清单
        ingredients_list, ingredient_counts = extract_ingredients_from_plan(plan)
        categorized = categorize_ingredients(ingredients_list)
        st.markdown('<div class="section-title">🛍️ 本周购物清单</div>', unsafe_allow_html=True)
        total_items = 0
        for category_name, items in categorized.items():
            if items:
                total_items += len(items)
                items_html = "".join([f'<span class="shopping-item">{item}</span>' for item in items])
                st.markdown(f"""
                <div class="shopping-category">
                    <div class="shopping-category-title">{category_name} <span>{len(items)}种</span></div>
                    <div class="shopping-items">{items_html}</div>
                </div>
                """, unsafe_allow_html=True)
        if total_items > 0:
            st.markdown(f"""<div class="info-box">📝 根据您的食谱，本周共需要 <strong>{total_items}</strong> 种食材，已按类别整理如上。</div>""", unsafe_allow_html=True)
        
        # 饮食提示
        st.markdown('<div class="section-title">💡 饮食温馨提示</div>', unsafe_allow_html=True)
        if 'tip_index' not in st.session_state: st.session_state.tip_index = 0
        current_tip = DIET_TIPS[st.session_state.tip_index]
        list_items = "".join([f'<li>{item}</li>' for item in current_tip["items"]])
        st.markdown(f"""
        <div class="carousel-container">
            <div class="carousel-title">{current_tip["title"]}</div>
            <ul class="carousel-list">{list_items}</ul>
        </div>
        <div class="carousel-indicator"><span>{st.session_state.tip_index + 1}</span> / {len(DIET_TIPS)}</div>
        """, unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        with col2:
            if st.button("◀ 上一篇", key="prev_tip", use_container_width=True):
                st.session_state.tip_index = (st.session_state.tip_index - 1) % len(DIET_TIPS)
                st.rerun()
        with col4:
            if st.button("下一篇 ▶", key="next_tip", use_container_width=True):
                st.session_state.tip_index = (st.session_state.tip_index + 1) % len(DIET_TIPS)
                st.rerun()
        st.markdown("""<div class="tip-badge"><p>🍽️ <strong>CardioGuard AI 提示</strong> 饮食调整需循序渐进，建议配合营养师制定个性化食谱。如有肾功能不全、心衰等并发症，请严格遵医嘱调整饮食方案。</p></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()