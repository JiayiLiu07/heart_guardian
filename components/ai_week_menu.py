import streamlit as st
import pandas as pd
import numpy as np
import random
from pages.p01_profile import CARDIO_DISEASES

def render_menu_card(day_data):
    meals = ["早餐", "午餐", "晚餐", "加餐"]
    
    menu_html = f"""
    <div style="flex-shrink: 0; width: 200px; height: 160px; margin-right: 20px; background-color: #fff; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,.08);">
        <h4 style="font-size: 16px; font-weight: 500; color: #1F2937; margin-bottom: 10px;">{day_data['day_name']}</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
    """
    
    day_totals = day_data.get("daily_totals", {})
    
    for meal in meals:
        meal_data = day_data.get(meal)
        if meal_data:
            dish = meal_data.get("dish")
            calories = meal_data.get("calories")
            sodium = meal_data.get("sodium")
            potassium = meal_data.get("potassium")
            fiber = meal_data.get("fiber")
            
            sodium_style = "color: #E94560; font-weight: 500;" if sodium > 800 else ""
            
            menu_html += f"""
            <div style="font-size: 12px; color: #555; margin-bottom: 8px;">
                <div style="font-weight: 500; color: #1F2937;">{meal}</div>
                <div>{dish}</div>
                <div style="font-size: 10px; color: #777;">
                    卡路里: {calories} kcal | 钠: <span style="{sodium_style}">{sodium} mg</span><br>
                    钾: {potassium} mg | 纤维: {fiber} g
                </div>
            </div>
            """
    
    sodium_style = "color: #E94560; font-weight: 500;" if day_totals.get('sodium', 0) > 2000 else ""
    menu_html += f"""
        </div>
        <div style="width: 100%; border-top: 1px dashed #ccc; margin-top: 10px; padding-top: 8px;">
            <div style="font-weight: 500; color: #1F2937; font-size: 12px;">今日总量</div>
            <div style="font-size: 10px; color: #777;">
                总卡路里: {day_totals.get('calories', 0)} kcal |
                总钠: <span style="{sodium_style}">{day_totals.get('sodium', 0)} mg</span> |
                总钾: {day_totals.get('potassium', 0)} mg |
                总纤维: {day_totals.get('fiber', 0)} g
            </div>
        </div>
    </div>
    """
    return menu_html

def render(cardio_disease='无心血管疾病'):
    disease_info = CARDIO_DISEASES.get(cardio_disease, {})
    is_low_sodium = "低钠" in disease_info.get('diet_guidelines', '')
    is_low_fat = "低饱和脂肪" in disease_info.get('diet_guidelines', '') or "低胆固醇" in disease_info.get('diet_guidelines', '')
    is_high_potassium = "高钾" in disease_info.get('diet_guidelines', '')
    is_high_fiber = "膳食纤维" in disease_info.get('diet_guidelines', '')
    
    dishes = {
        "低钠": ["燕麦粥", "蒸蛋", "凉拌黄瓜", "清蒸鱼", "白灼菜心", "西兰花", "苹果", "酸奶"],
        "低脂": ["燕麦粥", "蒸蛋", "凉拌黄瓜", "清蒸鱼", "白灼菜心", "西兰花", "苹果", "酸奶", "杂粮馒头"],
        "高钾": ["香蕉", "菠菜", "土豆", "西兰花", "苹果"],
        "高纤维": ["燕麦粥", "杂粮馒头", "西兰花", "凉拌黄瓜", "苹果"],
        "常规": ["燕麦粥", "杂粮馒头", "蒸蛋", "凉拌黄瓜", "番茄炒蛋", "宫保鸡丁", "清蒸鱼", "白灼菜心", "西兰花", "苹果", "酸奶", "坚果"]
    }
    
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
        suitable_dishes = dishes["常规"]  # fallback
    
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