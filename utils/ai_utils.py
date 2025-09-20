# utils/ai_utils.py
import yaml
import os
import json
import logging
import base64
from io import BytesIO
import pandas as pd
import plotly.express as px
from openai import OpenAI # Assuming openai library is installed
from utils.config import Config # Assuming config.py is in utils directory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def initialize_client():
    """Initializes and returns an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not api_key or not base_url:
        logging.error("OPENAI_API_KEY and OPENAI_BASE_URL environment variables are not set.")
        # Raise an error or return None/an indicator of failure
        return None # Indicate failure to initialize

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        # Optional: Ping the server to check connection health if supported by the client/API
        # Example: if hasattr(client, 'ping'): client.ping()
        return client
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")
        return None

def analyze_food_image(image):
    """Analyzes a food image to extract nutrition information."""
    client = initialize_client()
    if not client:
        return {"name": "未知", "sodium": 0.0, "protein": 0.0, "calories": 0.0, "fat": 0.0, "carbs": 0.0, "confidence": 0.0}

    try:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="qwen-vl-max", # Ensure this model is accessible and suitable
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "识别图片中的食物，并提供营养信息（钠(mg)、蛋白质(g)、热量(kcal)、脂肪(g)、碳水化合物(g)）及置信度。请严格按照JSON格式返回，键名分别为'name', 'sodium', 'protein', 'calories', 'fat', 'carbs', 'confidence'。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                    ]
                }
            ],
            temperature=0.1 # Lower temperature for more factual answers
        )
        
        content = response.choices[0].message.content
        if not content:
            logging.warning("Received empty content from AI for food image analysis.")
            return {"name": "未知", "sodium": 0.0, "protein": 0.0, "calories": 0.0, "fat": 0.0, "carbs": 0.0, "confidence": 0.0}
            
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON from AI response: {content}")
            return {"name": "未知", "sodium": 0.0, "protein": 0.0, "calories": 0.0, "fat": 0.0, "carbs": 0.0, "confidence": 0.0}

        # Validate keys and types, providing defaults and ensuring float types
        nutrition_data = {
            "name": result.get('name', '未知'),
            "sodium": float(result.get('sodium', 0.0)),
            "protein": float(result.get('protein', 0.0)),
            "calories": float(result.get('calories', 0.0)),
            "fat": float(result.get('fat', 0.0)),
            "carbs": float(result.get('carbs', 0.0)),
            "confidence": float(result.get('confidence', 0.0))
        }

        if nutrition_data["name"] == "未知" or nutrition_data['confidence'] < 0.7:
            logging.warning(f"Food recognition confidence is low: {nutrition_data['confidence']} for {nutrition_data['name']}")
            # Return default values if confidence is too low or name is unknown
            return {"name": "未知", "sodium": 0.0, "protein": 0.0, "calories": 0.0, "fat": 0.0, "carbs": 0.0, "confidence": nutrition_data['confidence']}
        
        return nutrition_data
        
    except Exception as e:
        logging.error(f"食物识别失败: {str(e)}")
        return {"name": "未知", "sodium": 0.0, "protein": 0.0, "calories": 0.0, "fat": 0.0, "carbs": 0.0, "confidence": 0.0}

def generate_dish(subtype, meal_types):
    """Generates a recipe for a specific cardiovascular subtype and meal types."""
    client = initialize_client()
    if not client:
        return []

    try:
        # Get sodium limit for the specific subtype safely
        disease_config = Config.DISEASE_TAGS.get('HTN', {}).get('subtypes', {}).get(subtype, {})
        try:
            sodium_limit = float(disease_config.get('sodium_limit', 1500.0))
        except (ValueError, TypeError):
            logging.warning(f"Invalid sodium_limit found for subtype {subtype}, defaulting to 1500mg.")
            sodium_limit = 1500.0

        prompt = f"""
        为患有 {subtype} 心血管亚型的患者生成适合的菜谱。
        请提供 {', '.join(meal_types)} 的菜品，并为每道菜指定：
        - 名称 (name)
        - 钠含量 (mg, sodium)
        - 蛋白质 (g, protein)
        - 热量 (kcal, calories)
        - 液体量 (ml, liquid) - 如果适用，例如汤类
        - 脂肪 (g, fat)
        - 碳水化合物 (g, carbs)

        要求：
        1. 每道菜的钠含量必须严格低于 {sodium_limit} mg。
        2. 菜谱应体现低钠、低脂、均衡营养的原则。
        3. 输出必须是JSON格式的列表，每个菜品是一个JSON对象。
        4. 不要包含任何解释性文字，只返回JSON列表。
        """
        
        response = client.chat.completions.create(
            model="qwen-max", # Ensure this model is accessible
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7 # Moderate temperature for creative recipes
        )
        
        content = response.choices[0].message.content
        if not content:
            logging.warning("Received empty content from AI for dish generation.")
            return []

        try:
            dishes = json.loads(content)
            # Ensure all required keys are present, provide defaults, and ensure float types
            formatted_dishes = []
            for dish in dishes:
                formatted_dish = {
                    "name": dish.get("name", "未知菜品"),
                    "sodium": float(dish.get("sodium", 0.0)),
                    "protein": float(dish.get("protein", 0.0)),
                    "calories": float(dish.get("calories", 0.0)),
                    "liquid": float(dish.get("liquid", 0.0)),
                    "fat": float(dish.get("fat", 0.0)),
                    "carbs": float(dish.get("carbs", 0.0)),
                }
                formatted_dishes.append(formatted_dish)
            # Filter out any "unknown" dishes that might have slipped through
            return [dish for dish in formatted_dishes if dish.get('name') != "未知菜品"]
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON from AI response for dish generation: {content}")
            return []
            
    except Exception as e:
        logging.error(f"菜谱生成失败: {str(e)}")
        return []

def get_ai_symptom_advice(user_data, symptoms, severity, sodium_intake):
    """Provides AI-driven health advice based on user's condition and input."""
    client = initialize_client()
    if not client:
        return "AI服务暂时不可用，请稍后重试。"

    try:
        # Safely get subtype
        subtype = user_data.get('disease_tags', ['HTN:WCHT'])[0].split(':')[1] if user_data.get('disease_tags') else 'WCHT'
        
        prompt = f"""
        患者信息：
        - 疾病亚型: {subtype}
        - 当前症状: {', '.join(symptoms) if symptoms else '无'}
        - 症状严重程度: {', '.join(severity) if severity else '无'}
        - 今日钠摄入量: {sodium_intake:.1f} mg

        请根据以上信息，提供简洁、易懂的健康建议（中文，50字以内）。
        建议应侧重于管理当前状况、调整生活方式或饮食，并强调何时应咨询医生。
        """
        
        response = client.chat.completions.create(
            model="qwen-max", # Ensure this model is accessible
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5 # Moderate temperature for helpful advice
        )
        
        advice = response.choices[0].message.content.strip()
        if not advice:
            return "请注意休息，控制钠摄入，并按时服药。如有不适，请及时就医。"
        return advice

    except Exception as e:
        logging.error(f"健康建议生成失败: {str(e)}")
        return "获取健康建议时发生错误，请咨询您的医生。"

def nl_to_sql_cardio(question, cardio_daily):
    """
    Parses natural language questions about cardiovascular data and returns SQL query, DataFrame, and Plotly figure.
    This is a simplified implementation using rule-based parsing. For more complex queries, an LLM or dedicated NLU system would be needed.
    """
    df = pd.DataFrame(cardio_daily)
    
    if df.empty:
        return "", df, None

    # Ensure 'date' column is in datetime format for comparisons
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        logging.error(f"Failed to convert 'date' column to datetime: {str(e)}")
        return "", pd.DataFrame(), None # Return empty if date conversion fails

    fig = None # Initialize fig to None

    try:
        if "平均收缩压" in question and ("上周" in question or "最近一周" in question):
            max_date = df['date'].max()
            # Ensure max_date is not NaT before calculations
            if pd.isnat(max_date):
                 return "", pd.DataFrame(), None
            
            last_week_start = max_date - pd.Timedelta(days=7)
            prev_week_start = max_date - pd.Timedelta(days=14)
            
            last_week_df = df[(df['date'] > last_week_start) & (df['date'] <= max_date)]
            prev_week_df = df[(df['date'] > prev_week_start) & (df['date'] <= last_week_start)]

            avg_last = last_week_df['ap_hi'].mean() if not last_week_df.empty else 0.0
            avg_prev = prev_week_df['ap_hi'].mean() if not prev_week_df.empty else 0.0
            
            result_df = pd.DataFrame({
                '周期': ['上周', '前一周'],
                '平均收缩压 (mmHg)': [avg_last, avg_prev]
            })
            
            fig = px.bar(
                result_df,
                x='周期',
                y='平均收缩压 (mmHg)',
                title='上周与前一周平均收缩压对比',
                color_discrete_sequence=['#3b82f6']
            )
            fig.update_layout(height=300, margin=dict(t=80, b=50, l=50, r=50))
            
            sql_query = "SELECT AVG(ap_hi) FROM cardio_daily WHERE date BETWEEN DATE('now', '-14 days') AND DATE('now', '-7 days') OR date BETWEEN DATE('now', '-7 days') AND DATE('now');"
            return sql_query, result_df, fig

        elif "心率" in question and ("趋势" in question or "变化" in question):
            fig = px.line(
                df,
                x='date',
                y='heart_rate',
                title='心率趋势',
                labels={'date': '日期', 'heart_rate': '心率 (bpm)'},
                color_discrete_sequence=['#3b82f6']
            )
            fig.update_layout(height=300, margin=dict(t=80, b=50, l=50, r=50))
            
            sql_query = "SELECT date, heart_rate FROM cardio_daily ORDER BY date;"
            return sql_query, df[['date', 'heart_rate']], fig

        elif "最高心率" in question:
            # Ensure 'heart_rate' column exists and is numeric
            if 'heart_rate' in df.columns and pd.api.types.is_numeric_dtype(df['heart_rate']):
                max_hr = df['heart_rate'].max() if not df.empty else 0.0
            else:
                max_hr = 0.0 # Default if column is missing or not numeric
            result_df = pd.DataFrame({'最高心率 (bpm)': [max_hr]})
            sql_query = "SELECT MAX(heart_rate) FROM cardio_daily;"
            return sql_query, result_df, None

        else:
            # For unhandled questions, return the whole dataframe with basic styling
            # Ensure all columns are displayed appropriately
            return "", df, None
            
    except Exception as e:
        logging.error(f"NL to SQL processing failed for question '{question}': {str(e)}")
        return "", pd.DataFrame(), None