# utils/visualization.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def create_risk_gauge(risk_score):
    """Creates a Plotly gauge chart for risk score."""
    # Ensure risk_score is a valid number
    try:
        risk_score = float(risk_score)
    except (ValueError, TypeError):
        risk_score = 0.0 # Default to 0 if invalid

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#FF4B4B"},
            'steps': [
                {'range': [0, 30], 'color': "#4CAF50"}, # Green
                {'range': [30, 70], 'color': "#FFC107"}, # Yellow
                {'range': [70, 100], 'color': "#FF4B4B"} # Red
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70 # Threshold line
            }
        }
    ))
    fig.update_layout(
        height=200,
        margin=dict(t=10, b=10),
        annotations=[{
            'x': 0.5, 'y': -0.2, 'xref': "paper", 'yref': "paper",
            'text': "0-30: 低风险, 30-70: 中等风险, 70-100: 高风险",
            'showarrow': False, 'font': {'size': 12}
        }]
    )
    return fig

def create_radar_cardio(sodium_percent, bp_score, exercise_days, smoke_free_days, sodium_limit):
    """Creates a radar chart for cardiovascular health metrics."""
    categories = ['钠摄入控制', '血压达标', '运动频率', '戒烟天数']
    
    # Ensure all values are within the 0-1 range for the radar chart
    values = [
        np.clip(1 - float(sodium_percent), 0, 1),
        np.clip(float(bp_score), 0, 1),
        np.clip(float(exercise_days), 0, 1),
        np.clip(float(smoke_free_days), 0, 1)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], # Close the loop
        theta=categories + [categories[0]], # Close the loop
        fill='toself',
        line_color='#3b82f6', # Blue
        name='健康维度'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),
            angularaxis=dict(rotation=90, direction="clockwise", tickfont=dict(size=12)) # Adjust tick font size
        ),
        showlegend=False,
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        title="心血管健康维度"
    )
    return fig

def create_3d_scatter(risk_history_data):
    """Creates a 3D scatter plot for risk history."""
    # Ensure risk_history_data is a list of dictionaries with expected keys
    if not isinstance(risk_history_data, list) or not risk_history_data:
        logging.warning("Risk history data is empty or invalid, cannot create 3D scatter plot.")
        return go.Figure() # Return an empty figure

    # Extract data, ensuring keys exist and values are numeric
    x = [float(item.get('ap_hi', 0)) for item in risk_history_data] # Systolic BP
    y = [float(item.get('social_support', 0)) for item in risk_history_data] # Social Support
    z = [float(item.get('relaxation_time', 0)) for item in risk_history_data] # Relaxation Time
    color = [float(item.get('risk_score', 0)) for item in risk_history_data] # Risk Score

    fig = go.Figure(data=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=8,
            color=color,
            colorscale='Viridis', # A perceptually uniform colormap
            opacity=0.8,
            showscale=True,
            colorbar=dict(
                title='风险评分 (%)'
            )
        )
    )])
    
    fig.update_layout(
        title='心血管风险因素三维关系',
        scene=dict(
            xaxis_title='收缩压 (mmHg)',
            yaxis_title='社会支持',
            zaxis_title='放松时间 (小时)'
        ),
        height=500,
        margin=dict(t=80, b=50, l=50, r=50)
    )
    return fig

def create_nutrition_chart(food_log):
    """Creates a grouped bar chart for daily nutrition analysis."""
    if not food_log:
        logging.warning("Food log is empty, cannot create nutrition chart.")
        return go.Figure() # Return empty figure if no data

    df = pd.DataFrame(food_log)
    
    # Ensure numeric columns are actually numeric
    for col in ['sodium', 'protein', 'calories', 'fat', 'carbs']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Filter out items with no name or negative values if necessary
    df = df[(df['name'].notna()) & (df['name'] != '')]

    fig = go.Figure(data=[
        go.Bar(name="钠含量 (mg)", x=df["name"], y=df["sodium"], marker_color="#4CAF50"), # Green
        go.Bar(name="蛋白质 (g)", x=df["name"], y=df["protein"], marker_color="#3F51B5")  # Blue
    ])
    
    fig.update_layout(
        barmode='group',
        height=300,
        margin=dict(t=10, b=10, l=10, r=10), # Reduced margins
        xaxis_title="食物",
        yaxis_title="含量",
        legend_title="营养素"
    )
    return fig