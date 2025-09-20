# pages/_02_nutrition.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from utils.database import UserManager, RedisManager
from utils.config import Config
from utils.visualization import create_nutrition_chart
from utils.ai_utils import analyze_food_image, generate_dish
from datetime import datetime
from io import BytesIO
import base64

st.set_page_config(page_title="心守护 - 饮食助手", page_icon="🥗", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    .main { background-color: #f9fafb; padding: 2rem; }
    .card { background: linear-gradient(145deg, #ffffff, #f1f5f9); border-radius: 12px; padding: 18px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,30,0.1); transition: transform 0.25s; }
    .card:hover { box-shadow: 0 6px 16px rgba(0,0,30,0.15); transform: scale(1.02); }
    .btn { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 min-h-[44px] font-semibold transition-colors duration-200; }
    .food-card { clip-path: polygon(0 0, 90% 0, 100% 100%, 10% 100%); }
    .blink { animation: blink 1s infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    .suggestion-box { @apply bg-gradient-to-r from-blue-50 to-green-50 p-4 rounded-lg border border-blue-200 mt-4 flex items-center gap-4 animate-slideIn; }
    @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def create_sodium_progress(sodium_intake, sodium_limit):
    # Ensure values are floats for calculations
    sodium_intake = float(sodium_intake)
    sodium_limit = float(sodium_limit)

    progress = min(sodium_intake / sodium_limit, 1.0) if sodium_limit > 0 else 0.0
    color = "#FF4B4B" if sodium_intake > sodium_limit else "#4CAF50"

    fig = go.Figure(go.Indicator(
        mode="gauge",
        gauge={
            'shape': "bullet",
            'axis': {'range': [0, sodium_limit]},
            'bar': {'color': color, 'thickness': 0.5},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [{'range': [0, sodium_limit], 'color': "#e5e7eb"}]
        },
        value=sodium_intake
    ))

    fig.update_layout(
        height=100,
        margin=dict(t=10, b=10, l=50, r=50),
        annotations=[{
            'x': 0.5, 'y': -0.2, 'xref': "paper", 'yref': "paper",
            'text': f"今日钠摄入: {sodium_intake:.0f} mg / 限额 {sodium_limit:.0f} mg",
            'showarrow': False, 'font': {'size': 14, 'color': color}
        }]
    )
    return fig

def speech_input_component(key):
    return st.components.v1.html(
        f"""
        <button id="speech-btn-{key}" class="btn" aria-label="语音输入食物">🎤 语音</button>
        <p style="color: #555; font-size: 12px;">请使用 Chrome 或 Edge 浏览器以获得最佳语音体验</p>
        <script>
            try {{
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'zh-CN';
                recognition.maxAlternatives = 1;
                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    Streamlit.setComponentValue(transcript, '{key}');
                }};
                recognition.onend = () => {{
                    document.getElementById('speech-btn-{key}').innerText = '🎤 语音';
                }};
                recognition.onerror = (event) => {{
                    console.error('Speech recognition error: ', event.error);
                }};
                document.getElementById('speech-btn-{key}').addEventListener('click', () => {{
                    recognition.start();
                    document.getElementById('speech-btn-{key}').innerText = '🎤 录音中...';
                    setTimeout(() => {{ recognition.stop(); }}, 30000);
                }});
            }} catch (e) {{
                console.error('Speech recognition not supported: ', e);
            }}
        </script>
        """, height=80
    )

def main():
    user_manager = UserManager(RedisManager())
    if 'user_id' not in st.session_state or not st.session_state.user_id:
        st.error("请先登录！")
        st.switch_page("app.py")
        st.stop()

    user_data = user_manager.get_user_info(st.session_state.user_id) or {
        'disease_tags': ['HTN:WCHT'],
        'food_log': [],
        'weekly_menu': {},
        'today_data': {'sodium_intake': 0.0} # Ensure it's a float
    }
    subtype = user_data.get('disease_tags', ['HTN:WCHT'])[0].split(':')[1]

    # Safely get sodium_limit as float
    try:
        # Correctly access DISEASE_TAGS using the class method
        sodium_limit = float(Config.get_disease_tags().get('HTN', {}).get('subtypes', {}).get(subtype, {}).get('sodium_limit', 1500.0))
    except (ValueError, TypeError):
        sodium_limit = 1500.0 # Default if config is invalid

    food_log = user_data.get('food_log', [])
    weekly_menu = user_data.get('weekly_menu', {})
    meal_types = ['早餐', '午餐', '晚餐']
    days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    with st.sidebar:
        st.markdown('<h3 class="text-lg font-semibold text-gray-700">导航</h3>', unsafe_allow_html=True)
        if st.button("🏠 返回主页"):
            st.switch_page("app.py")
        st.markdown('<hr class="my-4">', unsafe_allow_html=True)

        def save_food():
            food_name = st.session_state.get('food_name', '').strip()
            # Use text input for sodium to allow user entry, then convert safely
            food_sodium_str = st.session_state.get('food_sodium', '0.0')

            if not food_name:
                st.error("食物名称不能为空！")
                return

            try:
                food_sodium = float(food_sodium_str)
                if food_sodium < 0:
                    st.error("钠含量不能为负！")
                    return
            except (ValueError, TypeError):
                st.error("无效的钠含量！请确保输入数字。")
                return

            if 'food_log' not in user_data:
                user_data['food_log'] = []

            user_data['food_log'].append({
                'name': food_name,
                'sodium': food_sodium,
                'date': datetime.now().strftime("%Y-%m-%d")
            })
            user_manager.update_user_info(st.session_state.user_id, user_data)
            st.success("食物记录成功！")

        with st.form("quick_food_form"):
            st.markdown("### 快速记录食物")
            food_name = st.text_input("食物名称", placeholder="例如：鸡胸肉", key="food_name")
            # Use text_input for manual entry, allowing flexible input. Conversion handled in save_food.
            sodium = st.text_input("钠含量 (mg)", value="0.0", key="food_sodium", help="请输入数字，如 120.5")

            if st.form_submit_button("记录"):
                save_food()
                # Refresh the page to show updated data immediately
                st.rerun()

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">今日钠摄入</h3>', unsafe_allow_html=True)
    today_date_str = datetime.now().strftime("%Y-%m-%d")
    # Ensure sodium is treated as float for sum
    sodium_intake = sum(float(item.get('sodium', 0.0)) for item in food_log if item.get('date') == today_date_str)

    if 'today_data' not in user_data or not isinstance(user_data['today_data'], dict):
        user_data['today_data'] = {} # Ensure it's a dict

    user_data['today_data']['sodium_intake'] = sodium_intake
    user_manager.update_user_info(st.session_state.user_id, user_data)

    st.plotly_chart(create_sodium_progress(sodium_intake, sodium_limit), width='stretch')

    if sodium_intake > sodium_limit:
        st.markdown('<p class="blink text-red-600">⚠️ 钠摄入超标，请调整饮食！</p>', unsafe_allow_html=True)
    elif sodium_intake > sodium_limit * 0.8:
        st.warning("⚠️ 钠摄入接近限额，请注意饮食！")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">食物识别</h3>', unsafe_allow_html=True)
    uploaded_image = st.file_uploader("上传食物图片", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        try:
            image = Image.open(uploaded_image)
            with st.spinner("正在识别食物..."):
                result = analyze_food_image(image)

            st.markdown('<div class="food-card">', unsafe_allow_html=True)
            st.image(image, caption=result.get('name', '未知食物'), width=200)
            st.markdown('</div>', unsafe_allow_html=True)

            food_name = result.get('name', '未知食物')
            # Ensure all nutrition values are floats, defaulting to 0.0
            food_sodium = float(result.get('sodium', 0.0))
            food_protein = float(result.get('protein', 0.0))
            food_calories = float(result.get('calories', 0.0))
            food_fat = float(result.get('fat', 0.0))
            food_carbs = float(result.get('carbs', 0.0))
            confidence = float(result.get('confidence', 0.0))

            st.write(f"识别结果: {food_name} (置信度: {confidence:.2f})")
            st.write(f"营养信息 (估算): 钠: {food_sodium:.1f} mg, 蛋白质: {food_protein:.1f} g, 热量: {food_calories:.1f} kcal, 脂肪: {food_fat:.1f} g, 碳水化合物: {food_carbs:.1f} g")

            if food_sodium > sodium_limit / 3 and confidence > 0.7:
                st.warning("⚠️ 食物钠含量较高，建议替换！")
                # Generate a low-sodium dish recommendation
                with st.spinner("正在生成低钠菜品推荐..."):
                    # Requesting dish for specific meal type
                    new_dish_info = generate_dish(subtype, ["早餐", "午餐", "晚餐"]) # Request for general meals
                    if new_dish_info:
                        # Try to pick a dish that's not the one identified or similar
                        # For simplicity, pick the first one if available
                        recommended_dish = new_dish_info[0] if new_dish_info else {}
                        st.markdown(f'<div class="suggestion-box"><span class="text-2xl">🥗</span><strong>推荐低钠菜：</strong> {recommended_dish.get("name", "无推荐")} (钠: {recommended_dish.get("sodium", 0):.1f} mg)</div>', unsafe_allow_html=True)
                    else:
                        st.warning("未能生成新的菜品，请稍后重试。")

            if st.button("记录此食物", key="record_recognized_food"):
                if 'food_log' not in user_data:
                    user_data['food_log'] = []
                user_data['food_log'].append({
                    'name': food_name,
                    'sodium': food_sodium,
                    'protein': food_protein,
                    'calories': food_calories,
                    'fat': food_fat,
                    'carbs': food_carbs,
                    'date': datetime.now().strftime("%Y-%m-%d")
                })
                user_manager.update_user_info(st.session_state.user_id, user_data)
                st.success("食物记录成功！")
                st.rerun()
        except Exception as e:
            st.error(f"图片分析失败：{str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">语音记录饮食</h3>', unsafe_allow_html=True)
    food_input = speech_input_component("food_input")
    if food_input:
        if 'food_log' not in user_data:
            user_data['food_log'] = []

        user_data['food_log'].append({
            'name': food_input,
            'sodium': 0.0, # Default sodium to 0, needs manual update or better parsing
            'date': datetime.now().strftime("%Y-%m-%d")
        })
        user_manager.update_user_info(st.session_state.user_id, user_data)
        st.success(f"饮食记录成功：'{food_input}' (钠含量待补充)")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if food_log:
        today_food_log = [item for item in food_log if item.get('date') == today_date_str]
        if today_food_log:
            st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">今日营养分析</h3>', unsafe_allow_html=True)
            st.plotly_chart(create_nutrition_chart(today_food_log), width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3 class="text-xl font-semibold text-gray-700">本周菜单</h3>', unsafe_allow_html=True)
    if not weekly_menu or not any(weekly_menu.values()):
        try:
            # Generate menu for the current week if it doesn't exist
            valid_subtypes = ['WCHT', 'MHT', 'HFrEF', 'CAD', 'AF', 'CVD', 'PAD']
            if subtype in valid_subtypes: # Example valid subtypes
                generated_menu = {}
                for day in days:
                    generated_menu[day] = {}
                    for meal in meal_types:
                        # Requesting dish for specific meal type
                        dishes = generate_dish(subtype, [meal])
                        # Ensure we are adding a dictionary, even if empty
                        generated_menu[day][meal] = dishes[0] if dishes else {'name': '暂无推荐', 'sodium': 0.0, 'protein': 0.0, 'calories': 0.0, 'liquid': 0.0}
                weekly_menu = generated_menu
                user_data['weekly_menu'] = weekly_menu
                user_manager.update_user_info(st.session_state.user_id, user_data)
            else:
                st.warning(f"无法为疾病类型 '{subtype}' 生成菜单。")
        except Exception as e:
            st.error(f"生成菜单时出错：{str(e)}")
            weekly_menu = {} # Reset if error occurs
            user_data['weekly_menu'] = weekly_menu
            user_manager.update_user_info(st.session_state.user_id, user_data)

    for day in days:
        for meal in meal_types:
            # Check if the day and meal exist in the weekly_menu before expanding
            if day in weekly_menu and meal in weekly_menu[day] and weekly_menu[day][meal]:
                menu_item = weekly_menu[day][meal]
                with st.expander(f"{day} - {meal}", expanded=False):
                    st.markdown(f'<div class="food-card"><p><strong>{menu_item.get("name", "暂无推荐")}</strong> (钠: {menu_item.get("sodium", 0.0):.1f} mg, 蛋白质: {menu_item.get("protein", 0.0):.1f} g, 热量: {menu_item.get("calories", 0.0):.1f} kcal)</p></div>', unsafe_allow_html=True)
                    if st.button(f"替换", key=f"replace_{day}_{meal}"):
                        try:
                            # Generate a new dish for the same meal type
                            new_dish_info = generate_dish(subtype, [meal])
                            if new_dish_info:
                                weekly_menu[day][meal] = new_dish_info[0]
                                user_data['weekly_menu'] = weekly_menu
                                user_manager.update_user_info(st.session_state.user_id, user_data)
                                st.rerun()
                            else:
                                st.warning("未能生成新的菜品，请稍后重试。")
                        except Exception as e:
                            st.error(f"替换菜品时出错：{str(e)}")

    daily_na_data = []
    for day in days:
        if day in weekly_menu:
            daily_sodium = sum(float(item.get('sodium', 0.0)) for meal, item in weekly_menu[day].items() if isinstance(item, dict))
            daily_na_data.append({"day": day, "sodium": daily_sodium})

    if daily_na_data:
        daily_na_df = pd.DataFrame(daily_na_data)
        fig = px.line(daily_na_df, x='day', y='sodium', title='本周每日菜单钠摄入估算 vs 亚型限额')
        fig.add_hline(y=sodium_limit, line_dash='dash', line_color='red', annotation_text=f'{subtype} 限额 {sodium_limit:.0f} mg', annotation_position="bottom right")
        fig.update_layout(
            template="plotly_white",
            height=300,
            margin=dict(t=80, b=50, l=50, r=50),
            xaxis_title="日期",
            yaxis_title="钠摄入 (mg)"
        )
        st.plotly_chart(fig, width='stretch')

    if st.button("查看本周菜单营养详情", key="view_menu_details"):
        nutrition_details = []
        for day in days:
            if day in weekly_menu:
                day_data = {'日期': day}
                for meal_type in meal_types:
                    if meal_type in weekly_menu[day] and isinstance(weekly_menu[day][meal_type], dict):
                        item = weekly_menu[day][meal_type]
                        day_data[f'{meal_type}_名称'] = item.get('name', 'N/A')
                        day_data[f'{meal_type}_钠(mg)'] = float(item.get('sodium', 0.0))
                        day_data[f'{meal_type}_蛋白(g)'] = float(item.get('protein', 0.0))
                        day_data[f'{meal_type}_热量(kcal)'] = float(item.get('calories', 0.0))
                        day_data[f'{meal_type}_液体(ml)'] = float(item.get('liquid', 0.0))
                nutrition_details.append(day_data)

        if nutrition_details:
            nutrition_df = pd.DataFrame(nutrition_details)
            st.dataframe(nutrition_df.style.applymap(
                lambda x: 'background-color: #FFCDD2; color: #B71C1C;' if isinstance(x, (int, float)) and '钠(mg)' in str(x) and x > (sodium_limit/3) else '', # Highlight high sodium
                subset=pd.IndexSlice[:, [col for col in nutrition_df.columns if '钠(mg)' in col]]
            ).set_properties(**{
                'background-color': '#f3f4f6',
                'color': '#1e3a8a',
                'font-weight': 'bold'
            }), width='stretch', hide_index=False)
        else:
            st.info("暂无菜单营养详情可显示。")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
