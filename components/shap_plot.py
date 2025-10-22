import streamlit as st
import shap
import matplotlib.pyplot as plt

def render_shap(model, features, disease_key):
    if model:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features)
        st.subheader(f"{disease_key} SHAP 值")
        fig, ax = plt.subplots()
        shap.summary_plot(shap_values, features, plot_type="bar")
        st.pyplot(fig)
    else:
        st.warning("模型未加载，使用 dummy 图表")
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Dummy SHAP Plot', ha='center')
        st.pyplot(fig)

if __name__ == "__main__":
    # Test dummy
    render_shap(None, None, "test")