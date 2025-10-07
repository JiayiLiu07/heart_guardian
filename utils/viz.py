# utils/viz.py

# This file is intended for helper functions related to visualization generation,
# which are called by train.py.
# The actual visualization generation logic (using matplotlib, seaborn, shap, etc.)
# is currently embedded within train.py for simplicity of this example.
# In a larger project, these functions might be moved here for better modularity.

# For now, this file can remain mostly empty or contain utility functions
# that don't involve direct plotting calls but prepare data for plotting.

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from sklearn.inspection import PartialDependenceDisplay

# --- Example: Function to prepare data for a specific plot ---
def prepare_shap_summary_plot_data(model, X_data):
    """ Prepares data for SHAP summary plot. """
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_data)
        # For binary classification, shap_values might be a list.
        # Assuming we need SHAP values for class 1 (cardio disease).
        if isinstance(shap_values, list) and len(shap_values) > 1:
            shap_values = shap_values[1]
        
        return X_data, shap_values # Return data and SHAP values for plotting
    except Exception as e:
        st.error(f"Error preparing SHAP summary plot data: {e}")
        return None, None

def plot_shap_summary_bar(X_data, shap_values, feature_names, output_path):
    """ Plots and saves SHAP summary bar plot. """
    if X_data is None or shap_values is None or not feature_names:
        st.warning("Missing data for SHAP summary bar plot.")
        return

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_data, feature_names=feature_names, plot_type="bar", show=False, color='#E94560')
    plt.title('Global Feature Importance (SHAP)')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"SHAP summary bar plot saved to {output_path}")

# --- Other potential visualization helper functions ---
# def plot_correlation_heatmap(...): ...
# def plot_partial_dependence(...): ...

# The functions in train.py are currently directly implementing the plots.
# If these functions become complex or are reused, they can be moved here.
