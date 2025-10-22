import streamlit as st
import random
from utils.disease_dict import DISEASE_ENUM

def render_menu_card(day_data):
    meals = ["早餐", "午餐", "晚餐", "加餐"]
    meal_icons = {"早餐": "🌞", "午餐": "🍱", "晚餐": "🌙", "加餐": "🍪"}
    html = f'<div class="menu-card"><h4>{day_data["day_name"]}</h4>'
    for meal in meals:
        if meal in day_data:
            d = day_data[meal]
            html += f'<div>{meal_icons[meal]} {meal}: {d["dish"]} (卡路里: {d["calories"]} kcal)</div>'
    html += '</div>'
    return html

def render(cardio_disease='none'):
    guidelines = DISEASE_ENUM.get(cardio_disease, {}).get('diet_guidelines', '均衡饮食')
    dishes = {
        "低钠": ["燕麦粥", "蒸蛋", "凉拌黄瓜", "清蒸鱼", "白灼菜心", "西兰花", "苹果", "酸奶"],
        "低脂": ["燕麦粥", "蒸蛋", "凉拌黄瓜", "清蒸鱼", "白灼菜心", "西兰花", "苹果", "酸奶", "杂粮馒头"],
        "高钾": ["香蕉", "菠菜", "土豆", "西兰花", "苹果"],
        "高纤维": ["燕麦粥", "杂粮馒头", "西兰花", "凉拌黄瓜", "苹果"],
        "常规": ["燕麦粥", "杂粮馒头", "蒸蛋", "凉拌黄瓜", "番茄炒蛋", "宫保鸡丁", "清蒸鱼", "白灼菜心", "西兰花", "苹果", "酸奶", "坚果"]
    }
    is_low_sodium = "低钠" in guidelines
    is_low_fat = "低饱和脂肪" in guidelines or "低胆固醇" in guidelines
    is_high_potassium = "高钾" in guidelines
    is_high_fiber = "膳食纤维" in guidelines
    suitable_dishes = list(set(dishes["常规"]))
    if is_low_sodium:
        suitable_dishes = list(set(suitable_dishes) & set(dishes["低钠"]))
    if is_low_fat:
        suitable_dishes = list(set(suitable_dishes) & set(dishes["低脂"]))
    if is_high_potassium:
        suitable_dishes = list(set(suitable_dishes) | set(dishes["高钾"]))
    if is_high_fiber:
        suitable_dishes = list(set(suitable_dishes) | set(dishes["高纤维"]))
    if not suitable_dishes:
        suitable_dishes = dishes["常规"]
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    menu_data_for_component = {}
    for day in days:
        day_card_data = {"day_name": day}
        day_total_calories = 0
        day_total_sodium = 0
        day_total_potassium = 0
        day_total_fiber = 0
        meals = ["早餐", "午餐", "晚餐", "加餐"]
        for meal in meals:
            dish_name = random.choice(suitable_dishes)
            calories = random.randint(100, 600) if is_low_fat else random.randint(100, 800)
            sodium = random.randint(50, 400) if is_low_sodium else random.randint(50, 800)
            potassium = random.randint(200, 600) if is_high_potassium else random.randint(50, 500)
            fiber = random.randint(5, 15) if is_high_fiber else random.randint(1, 10)
            day_card_data[meal] = {
                "dish": dish_name,
                "calories": calories,
                "sodium": sodium,
                "potassium": potassium,
                "fiber": fiber
            }
            day_total_calories += calories
            day_total_sodium += sodium
            day_total_potassium += potassium
            day_total_fiber += fiber
        day_card_data["daily_totals"] = {
            "calories": day_total_calories,
            "sodium": day_total_sodium,
            "potassium": day_total_potassium,
            "fiber": day_total_fiber
        }
        menu_data_for_component[day] = day_card_data
    all_menu_cards_html = ""
    for day_name in days:
        all_menu_cards_html += render_menu_card(menu_data_for_component[day_name])
    st.markdown(f"""
    <div style="display: flex; overflow-x: auto; scrollbar-width: none; -ms-overflow-style: none; padding-bottom: 20px; margin-top: 30px;">
        {all_menu_cards_html}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()