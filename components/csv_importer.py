import streamlit as st
import pandas as pd
import io

def render():
    st.subheader("导入 CSV 数据")
    st.markdown("请上传您的健康数据 CSV 文件。")

    uploaded_file = st.file_uploader("选择一个 CSV 文件", type="csv", key="csv_uploader")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("文件上传成功！")
            st.markdown("##### 文件预览:")
            st.dataframe(df.head())
            st.session_state.uploaded_data = df
        except Exception as e:
            st.error(f"读取 CSV 文件时出错: {e}")

if __name__ == "__main__":
    render()