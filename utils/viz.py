# 📁 utils/viz.py
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# --- Universal Styling ---
# Apply consistent font and color palette
def get_theme_styles():
    """Returns a dictionary of theme styles for plots."""
    # These colors can be linked to your global CSS variables if available
    return {
        "font": "Arial, sans-serif",
        "primary_color": "#007bff", # Example: Blue
        "accent_color": "#17a2b8",  # Example: Cyan
        "success_color": "#28a745", # Example: Green
        "warning_color": "#ffc107", # Example: Yellow
        "danger_color": "#dc3545",  # Example: Red
        "neutral_color": "#6c757d", # Example: Gray
        "figure_bg_color": "white",
        "plot_bg_color": "white",
        "axis_color": "#333",
        "title_color": "#333",
    }

# --- Plotting Functions ---

def plot_age_bp_scatter(df: pd.DataFrame, title: str = "Age vs Blood Pressure", **kwargs):
    """
    Generates a Plotly scatter plot for Age vs Blood Pressure (Systolic and Diastolic).
    Assumes df has 'age', 'ap_high', 'ap_low' columns, and 'timestamp' for coloring/hover.
    """
    if df is None or df.empty:
        st.warning("No data available for plotting Age vs BP.")
        return None

    # Ensure required columns exist
    required_cols = ['age', 'ap_high', 'ap_low']
    if not all(col in df.columns for col in required_cols):
        st.error(f"DataFrame is missing required columns for BP plot: {required_cols}")
        return None

    # Use timestamp for coloring if available, otherwise use age or a simple color
    color_col = 'timestamp' if 'timestamp' in df.columns else 'age'
    
    fig = px.scatter(df, 
                     x='age', 
                     y='ap_high', 
                     color=color_col,
                     size='ap_low', # Using size for diastolic BP
                     hover_name='age', # Display age on hover
                     hover_data={'ap_high': True, 'ap_low': True, 'timestamp': True, 'age': False}, # Customize hover info
                     title=title,
                     labels={
                         'age': '年龄', 
                         'ap_high': '收缩压 (mmHg)', 
                         'ap_low': '舒张压 (mmHg)',
                         'timestamp': '记录时间'
                     },
                     color_continuous_scale=px.colors.sequential.Viridis # Example color scale
                    )

    fig.update_layout(
        xaxis_title="年龄",
        yaxis_title="收缩压 (mmHg)",
        hovermode='closest', # Show hover info for the closest point
        plot_bgcolor=get_theme_styles()["plot_bg_color"],
        paper_bgcolor=get_theme_styles()["figure_bg_color"],
        font=dict(family=get_theme_styles()["font"]),
        title_font_color=get_theme_styles()["title_color"],
        xaxis=dict(tickfont=dict(color=get_theme_styles()["axis_color"])),
        yaxis=dict(tickfont=dict(color=get_theme_styles()["axis_color"])),
        coloraxis_colorbar=dict(title="时间" if color_col == 'timestamp' else "年龄") # Colorbar title
    )
    
    # Add a secondary y-axis if needed, or just plot them together
    # For simplicity, let's just use scatter plot for now.
    
    return fig

# Add other plotting functions as needed, e.g., for distribution, trends, etc.
# def plot_obesity_distribution(df, ...): ...
# def plot_health_trends_line(df, metric, ...): ...

# Example: Matplotlib-based plot
def plot_matplotlib_bar(data: pd.Series, title: str = "Bar Chart"):
    """Generates a simple Matplotlib bar plot."""
    styles = get_theme_styles()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=data.index, y=data.values, ax=ax, palette="viridis") # Using seaborn for better aesthetics
    
    ax.set_title(title, fontsize=16, color=styles["title_color"])
    ax.set_xlabel("Category", fontsize=12, color=styles["axis_color"])
    ax.set_ylabel("Value", fontsize=12, color=styles["axis_color"])
    ax.tick_params(axis='both', which='major', labelsize=10, colors=styles["axis_color"])
    
    plt.tight_layout()
    return fig