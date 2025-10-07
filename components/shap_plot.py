import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap  # For SHAP plots
import os

def render(user_shap_values, expected_value, feature_names, user_features_values, title="你的风险因子贡献 (SHAP)"):
    if user_shap_values is None or expected_value is None or not feature_names:
        st.warning("SHAP 值数据不完整，无法渲染瀑布图。")
        return

    try:
        fig, ax = plt.subplots(figsize=(10, 7))
        explanation = shap.Explanation(
            values=user_shap_values,
            base_values=expected_value,
            data=user_features_values,
            feature_names=feature_names
        )
        shap.plots.waterfall(
            explanation,
            max_display=10,
            show=False
        )
        plt.title(title, fontsize=16)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    except Exception as e:
        st.error(f"渲染 SHAP 瀑布图时出错: {e}")
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'SHAP Waterfall (Dummy)', ha='center')
        st.pyplot(fig)
        plt.close(fig)

if __name__ == "__main__":
    render(None, None, [], None)