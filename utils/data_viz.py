import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

@st.cache_data(show_spinner=False)
def load_train_csv():
    return pd.read_csv('data/cardio_train.csv', sep=';')  # Fix sep=';' for column names like 'id;age;...'

def plot_age_bp_scatter():
    df = load_train_csv()
    fig = px.scatter(df, x='age', y='ap_hi', color='cardio', title='年龄与收缩压散点图')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**解读**：高龄与高收缩压人群心血管疾病风险较高。", unsafe_allow_html=True)

def plot_disease_distribution():
    df = load_train_csv()
    fig, ax = plt.subplots()
    sns.countplot(data=df, x='cardio', ax=ax)
    ax.set_title('疾病分布柱状图')
    st.pyplot(fig)
    st.markdown("**解读**：数据集中疾病与非疾病人群分布。", unsafe_allow_html=True)

def plot_bmi_chol_heatmap():
    df = load_train_csv()
    fig, ax = plt.subplots()
    corr = df[['bmi', 'cholesterol']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title('BMI与胆固醇热力图')
    st.pyplot(fig)
    st.markdown("**解读**：BMI与胆固醇的相关性分析。", unsafe_allow_html=True)

def plot_feature_correlation():
    df = load_train_csv()
    fig, ax = plt.subplots()
    corr = df.corr().iloc[:10, :10]
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, annot=True, cmap='Blues', ax=ax, mask=mask)
    ax.set_title('特征相关性（Top 10）')
    st.pyplot(fig)
    st.markdown("**解读**：关键特征间的相关性，指导风险评估。", unsafe_allow_html=True)