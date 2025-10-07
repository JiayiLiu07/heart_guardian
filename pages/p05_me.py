import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Helper Functions ---
def load_user_base_info(user_id):
    user_data_path = os.path.join('users', f"{user_id}.parquet")
    if os.path.exists(user_data_path):
        try:
            df = pd.read_parquet(user_data_path)
            return df.iloc[0].to_dict()
        except Exception as e:
            st.error(f"加载基础用户信息失败: {e}")
            return {}
    return {}

def save_user_base_info(user_id, data_dict):
    user_data_path = os.path.join('users', f"{user_id}.parquet")
    try:
        existing_data = load_user_base_info(user_id)
        existing_data.update(data_dict)
        df_to_save = pd.DataFrame([existing_data])
        df_to_save.to_parquet(user_data_path, index=False)
        st.success("个人信息已更新。")
        return True
    except Exception as e:
        st.error(f"保存基础用户信息失败: {e}")
        return False

def render():
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("请先登录以访问个人中心。")
        user_id = 'default_user'
        user_info = {}  # Dummy
    else:
        user_id = st.session_state.user_id
        user_info = load_user_base_info(user_id)

    st.title("个人中心")

    tab_personal, tab_notes, tab_export, tab_account = st.tabs([
        "个人信息", "我的笔记", "导出数据", "账号安全"
    ])

    with tab_personal:
        st.image("https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/350/red-heart_2764.png", width=100)
        current_nickname = user_info.get('nickname', '未知')
        new_nickname = st.text_input("昵称", value=current_nickname)
        if st.button("保存昵称"):
            save_user_base_info(user_id, {'nickname': new_nickname})
            st.rerun()

    with tab_notes:
        st.subheader("健康笔记")
        notes_content = user_info.get('health_notes', "")
        edited_notes = st.text_area("您的健康笔记", value=notes_content, height=300)
        if st.button("保存笔记"):
            save_user_base_info(user_id, {'health_notes': edited_notes})
            st.rerun()

    with tab_export:
        st.subheader("导出您的健康数据")
        export_format = st.selectbox("选择导出格式", ["CSV", "PDF"])
        if st.button(f"导出为 {export_format}"):
            st.info(f"导出 {export_format} 功能开发中...")

    with tab_account:
        st.subheader("账号安全")
        st.info("关联账号功能开发中...")
        if st.button("退出登录"):
            st.session_state.user_id = None
            st.rerun()
        st.warning("注销账号将永久删除数据。")
        if st.button("注销账号"):
            user_data_path = os.path.join('users', f"{user_id}.parquet")
            if os.path.exists(user_data_path):
                os.remove(user_data_path)
            st.session_state.user_id = None
            st.success("账号已注销。")
            st.rerun()

if __name__ == "__main__":
    render()