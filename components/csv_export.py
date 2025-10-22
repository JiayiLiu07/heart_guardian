import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
from pages.p01_profile import load_profile_data

def render_export():
    user_id = st.session_state.get('user_id', 'demo')
    profile_data = load_profile_data(user_id)
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("profile_data.csv", pd.DataFrame([profile_data]).to_csv(index=False))
    zip_buffer.seek(0)
    
    st.download_button(
        label="下载 CSV (ZIP)",
        data=zip_buffer,
        file_name="profile_export.zip",
        mime="application/zip"
    )