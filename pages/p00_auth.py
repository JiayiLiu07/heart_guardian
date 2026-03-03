import streamlit as st
import os
import hashlib
import re
import time
import json

def render():
    # 【新增】状态同步检查：如果已经登录，提示用户并允许跳转
    if st.session_state.get('is_logged_in', False):
        username = st.session_state.get('username', '用户')
        st.warning(f"✅ 您已作为 **{username}** 登录。")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("前往健康档案", type="primary", use_container_width=True):
                st.switch_page("pages/p01_profile.py")
        with col2:
            if st.button("退出登录", type="secondary", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        st.markdown("---")
        # 即使已登录，也允许用户查看登录页（比如想切换账号），但默认引导去健康档案

    st.set_page_config(
        page_title="登录注册 - CardioGuard AI",
        page_icon="🔑",
        layout="centered"
    )

    # ================= 配置区域开始 =================
    # 定义 users 文件夹路径 (指向根目录 heart_guardian/users)
    USERS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "users"))
    
    # 统一所有数据文件到 users 文件夹
    USER_DATA_FILE = os.path.join(USERS_FOLDER, "user_data.json")       # 用户账号信息
    DATA_FILE = os.path.join(USERS_FOLDER, "heart_profile_data.json")   # 心脏健康档案摘要 (我的中心展示用)
    LOG_FILE = os.path.join(USERS_FOLDER, "user_logs.json")             # 健康日志
    
    def ensure_users_folder():
        """确保 users 文件夹存在"""
        if not os.path.exists(USERS_FOLDER):
            os.makedirs(USERS_FOLDER)
    # ================= 配置区域结束 =================

    def load_user_data():
        """加载用户账号数据"""
        ensure_users_folder()
        if os.path.exists(USER_DATA_FILE):
            try:
                with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"加载用户数据失败：{e}")
                return {}
        return {}

    def save_user_data(data):
        """保存用户账号数据"""
        ensure_users_folder()
        try:
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"保存用户数据失败：{e}")

    def load_heart_profile():
        """加载心脏健康档案摘要数据 (我的中心用)"""
        ensure_users_folder()
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                return {}
        return {}

    def save_heart_profile(data):
        """保存心脏健康档案摘要数据"""
        ensure_users_folder()
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"保存健康档案失败：{e}")

    def load_user_logs():
        """加载用户健康日志"""
        ensure_users_folder()
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                return []
        return []

    def save_user_logs(logs):
        """保存用户健康日志"""
        ensure_users_folder()
        try:
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"保存日志失败：{e}")

    def hash_password(password):
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_account(account):
        """验证帐号格式"""
        if len(account) < 6:
            return False, "帐号长度不能少于 6 位"
        
        # 检查是否为手机号
        if re.match(r'^1[3-9]\d{9}$', account):
            return True, "手机号格式正确"
        
        # 检查是否为 QQ 号
        if re.match(r'^[1-9]\d{4,11}$', account):
            return True, "QQ 号格式正确"
        
        # 检查是否为邮箱
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', account):
            return True, "邮箱格式正确"
        
        return False, "请输入有效的手机号、QQ 号或邮箱"

    def validate_username(username):
        """验证用户名格式"""
        if len(username) < 2:
            return False, "用户名至少 2 个字符"
        if len(username) > 20:
            return False, "用户名不能超过 20 个字符"
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$', username):
            return False, "用户名只能包含中文、英文、数字和下划线"
        return True, "用户名格式正确"

    def validate_password(password):
        """验证密码强度"""
        if len(password) < 6:
            return False, "密码至少 6 个字符"
        if len(password) > 20:
            return False, "密码不能超过 20 个字符"
        return True, "密码格式正确"

    def verify_user(account, password):
        """验证用户凭据"""
        user_data = load_user_data()
        for username, data in user_data.items():
            if data.get('account') == account:
                stored_password = data.get('password')
                if stored_password == hash_password(password):
                    return True, username
                return False, "密码错误"
        return False, "帐号不存在"

    # 自定义 CSS 样式（与 p00_intro.py 风格一致）
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    .stSidebar {
        display: none !important;
    }
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(45deg, #00e5ff, #2979ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientAnimation 5s ease infinite;
        background-size: 200% 200%;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #2979ff, #00e5ff);
        color: white;
        box-shadow: 0 4px 10px rgba(41, 121, 255, 0.3);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(45deg, #5c6bc0, #4fc3f7);
        color: white;
    }
    .button-right {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #b0c4de;
        padding: 10px;
        background: rgba(255, 255, 255, 0.8);
    }
    .stButton > button {
        background: linear-gradient(45deg, #2979ff, #00e5ff);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        font-size: 1.2rem;
        font-weight: bold;
        width: 100%;
        box-shadow: 0 4px 15px rgba(41, 121, 255, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(41, 121, 255, 0.4);
    }
    /* 自定义“忘记密码”按钮样式 */
    button[kind="secondary"][data-testid="baseButton-secondary"] {
        background: none !important;
        color: #003087 !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        font-size: 0.9rem;
        font-weight: normal;
        text-align: right;
        padding: 5px 0;
        width: auto;
    }
    button[kind="secondary"][data-testid="baseButton-secondary"]:hover {
        color: #0053b3 !important;
        text-decoration: underline;
        transform: none !important;
        box-shadow: none !important;
    }
    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    """, unsafe_allow_html=True)

    # 主界面
    st.markdown('<div class="main-header">🔑 CardioGuard AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">心脏健康守护者 - 专业 AI 分析平台</div>', unsafe_allow_html=True)

    # 使用标签页
    tab1, tab2 = st.tabs(["🚪 登录", "📝 注册"])

    with tab1:
        st.subheader("用户登录")
        
        with st.form("login_form"):
            login_account = st.text_input(
                "帐号",
                placeholder="请输入帐号（手机号/QQ 号/邮箱）",
                key="login_account"
            )
            
            login_password = st.text_input(
                "密码",
                type="password",
                placeholder="请输入密码",
                key="login_password"
            )
            
            if st.form_submit_button("登录", type="primary", use_container_width=True):
                if not login_account or not login_password:
                    st.error("请输入帐号和密码")
                else:
                    valid, message = verify_user(login_account, login_password)
                    if valid:
                        # 设置登录状态 - 确保所有必要字段都设置
                        st.session_state.is_logged_in = True
                        st.session_state.username = message
                        st.session_state.user_id = message
                        st.session_state.login_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 设置额外的会话状态以确保登录信息持久化
                        st.session_state['auth_status'] = 'authenticated'
                        st.session_state['user'] = {
                            'username': message,
                            'account': login_account,
                            'login_time': st.session_state.login_time
                        }
                        
                        # 调试信息 - 可以在控制台查看
                        print("="*50)
                        print("登录成功！Session State 已设置：")
                        print(f"is_logged_in: {st.session_state.is_logged_in}")
                        print(f"username: {st.session_state.username}")
                        print(f"user_id: {st.session_state.user_id}")
                        print(f"login_time: {st.session_state.login_time}")
                        print("="*50)
                        
                        st.success(f"欢迎回来，{message}！")
                        st.balloons()
                        time.sleep(1.5)
                        # 跳转到健康档案页面
                        st.switch_page("pages/p01_profile.py")
                    else:
                        st.error(message)
        
        # “忘记密码”按钮移到表单下方右侧
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("忘记密码", key="forgot_password_button", type="secondary"):
                st.session_state.show_forgot_password = True
                st.rerun()

    with tab2:
        st.subheader("用户注册")
        
        with st.form("register_form"):
            reg_username = st.text_input(
                "用户名",
                placeholder="请输入用户名（2-20 个字符）",
                key="reg_username"
            )
            
            reg_account = st.text_input(
                "帐号",
                placeholder="请输入帐号（手机号/QQ 号/邮箱）",
                key="reg_account"
            )
            
            reg_password1 = st.text_input(
                "密码",
                type="password",
                placeholder="请输入密码（6-20 个字符）",
                key="reg_password1"
            )
            
            reg_password2 = st.text_input(
                "确认密码",
                type="password",
                placeholder="请再次输入密码",
                key="reg_confirm_password",
                label_visibility="collapsed"
            )
            
            if st.form_submit_button("注册", type="primary", use_container_width=True):
                if not all([reg_username, reg_account, reg_password1, reg_password2]):
                    st.error("请填写所有字段")
                else:
                    # 验证用户名
                    username_valid, username_msg = validate_username(reg_username)
                    if not username_valid:
                        st.error(username_msg)
                    
                    # 验证帐号
                    account_valid, account_msg = validate_account(reg_account)
                    if not account_valid:
                        st.error(account_msg)
                    
                    # 验证密码
                    password_valid, password_msg = validate_password(reg_password1)
                    if not password_valid:
                        st.error(password_msg)
                    
                    # 检查密码一致性
                    if reg_password1 != reg_password2:
                        st.error("两次输入的密码不一致")
                    
                    # 如果所有验证都通过
                    if username_valid and account_valid and password_valid and reg_password1 == reg_password2:
                        user_data = load_user_data()
                        
                        # 检查用户名是否已存在
                        if reg_username in user_data:
                            st.error("用户名已存在！")
                        else:
                            # 检查帐号是否已注册
                            account_exists = any(data.get('account') == reg_account for data in user_data.values())
                            if account_exists:
                                st.error("该帐号已被注册")
                            else:
                                # 保存用户数据
                                user_data[reg_username] = {
                                    'account': reg_account,
                                    'password': hash_password(reg_password1),
                                    'register_time': time.strftime("%Y-%m-%d %H:%M:%S")
                                }
                                save_user_data(user_data)
                                st.success("注册成功！请返回登录页面登录")
                                time.sleep(2)
                                st.rerun()

    # 忘记密码页面
    if st.session_state.get('show_forgot_password', False):
        st.markdown("---")
        st.subheader("🔐 重置密码")
        
        with st.form("reset_password_form"):
            reset_account = st.text_input(
                "原帐号",
                placeholder="请输入您的帐号（手机号/QQ 号/邮箱）",
                key="reset_account"
            )
            
            new_password1 = st.text_input(
                "新密码",
                type="password",
                placeholder="请输入新密码（6-20 个字符）",
                key="new_password1"
            )
            
            new_password2 = st.text_input(
                "确认新密码",
                type="password",
                placeholder="请再次输入新密码",
                key="new_password2",
                label_visibility="collapsed"
            )
            
            # 按钮布局 - 返回在左，确认在右
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                if st.form_submit_button("🔙 返回登录页面", use_container_width=True):
                    st.session_state.show_forgot_password = False
                    st.rerun()
            with col3:
                if st.form_submit_button("✅ 确认修改", type="primary", use_container_width=True):
                    if not reset_account or not new_password1 or not new_password2:
                        st.error("请填写所有字段")
                    else:
                        user_data = load_user_data()
                        
                        # 查找用户
                        user_found = None
                        for username, data in user_data.items():
                            if data.get('account') == reset_account:
                                user_found = username
                                break
                        
                        if not user_found:
                            st.error("帐号不存在")
                        else:
                            # 验证新密码
                            password_valid, password_msg = validate_password(new_password1)
                            if not password_valid:
                                st.error(password_msg)
                            elif new_password1 != new_password2:
                                st.error("两次输入的密码不一致")
                            else:
                                # 更新密码 (哈希)
                                user_data[user_found]['password'] = hash_password(new_password1)
                                save_user_data(user_data)
                                st.success("密码已修改！")
                                time.sleep(2)
                                st.session_state.show_forgot_password = False
                                st.rerun()

if __name__ == "__main__":
    render()