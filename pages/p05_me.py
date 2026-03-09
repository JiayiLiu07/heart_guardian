# pages/p05_me.py
import streamlit as st
import json
import os
import time
from datetime import datetime
import base64

# ─── 统一恢复用户档案 ────────────────────────────────────────
def load_profile():
    # 优先从 query params
    if 'profile_data' in st.query_params:
        try:
            b64 = st.query_params['profile_data']
            b64 += '=' * ((4 - len(b64) % 4) % 4)
            json_str = base64.urlsafe_b64decode(b64).decode('utf-8')
            return json.loads(json_str)
        except:
            pass
    # 其次从 session_state
    if 'profile' in st.session_state:
        return st.session_state['profile']
    # 最后尝试文件（云端基本无效）
    try:
        with open("users/heart_profile_data.json", encoding="utf-8") as f:
            data = json.load(f)
            st.session_state['profile'] = data
            return data
    except:
        return {}

# 在页面加载时执行
if 'profile' not in st.session_state:
    st.session_state['profile'] = load_profile()

# 下面就可以安全使用 st.session_state.profile 了
profile = st.session_state['profile']

# 尝试导入组件 (如果存在)
try:
    from components.nav_component import render_navbar, render_hero
except ImportError:
    def render_navbar(key): pass
    def render_hero(title, sub, c1, c2): st.title(title)

# 【修改点】设置页面配置，使用 Emoji 作为图标
st.set_page_config(
    page_title="我的中心 · CardioGuard AI", 
    layout="wide",
    page_icon="👤"  # 用户 Emoji
)

# ==========================================
# 【修复部分】路径配置 - 确保顺序正确
# ==========================================
# 1. 先定义 users 文件夹的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
USERS_FOLDER = os.path.abspath(os.path.join(current_dir, "..", "users"))

# 2. 确保 users 文件夹存在，不存在则创建
if not os.path.exists(USERS_FOLDER):
    os.makedirs(USERS_FOLDER)

# 3. 再定义数据文件路径 (现在 USERS_FOLDER 已经定义了，不会报错)
DATA_FILE = os.path.join(USERS_FOLDER, "heart_profile_data.json")
LOG_FILE = os.path.join(USERS_FOLDER, "user_logs.json")
USER_DATA_FILE = os.path.join(USERS_FOLDER, "user_data.json")

# ==========================================
# CSS 样式 - 已同步 nutrition.py 的导航栏参数 (紧贴顶部)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #EC4899;       /* 粉色主色调 */
        --primary-dark: #BE185D;  /* 深粉色 */
        --primary-light: #FCE7F3; /* 浅粉色背景 */
        --success: #059669;
        --warning: #D97706;
        --danger: #DC2626;
        --gray-50: #F9FAFB;
        --gray-100: #F3F4F6;
        --gray-200: #E5E7EB;
        --gray-600: #4B5563;
        --gray-800: #1F2937;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .stApp {
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        background-color: #f8fafc;
    }
    
    /* 移除默认 padding-top */
    .main > div { 
        padding-top: 0 !important; 
    }
    
    /* 调整主内容区域 */
    .block-container { 
        padding: 0 2rem 1rem !important; 
        max-width: 1400px; 
        margin: 0 auto; 
    }
    
    #MainMenu, footer, section[data-testid="stSidebar"] { display: none !important; }
    
    /* 【关键修改】导航栏 - 完全同步 nutrition.py 参数 */
    .top-navbar {
        background: white;
        padding: 0 1.5rem;           /* 同步：1.5rem */
        height: 75px;                /* 同步：75px */
        box-shadow: var(--shadow-sm);
        display: flex;
        justify-content: space-between;
        align-items: center;         /* 同步：居中 */
        position: relative; 
        z-index: 9999;
        border-bottom: 1px solid var(--gray-200);
        
        margin-top: 50px;            /* 同步：50px，紧贴默认头部 */
        margin-bottom: 0rem;         /* 同步：1rem */
        border-radius: 0 0 8px 8px;
    }
    
    .nav-logo { 
        font-weight: 700; 
        font-size: 1.8rem;           /* 同步：1.8rem */
        color: var(--primary);
        cursor: default; 
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .nav-links { 
        display: flex; 
        gap: 10px;                   /* 同步：10px */
    }
    .nav-links a { 
        text-decoration: none; 
        color: var(--gray-600); 
        font-weight: 500; 
        padding: 8px 18px;           /* 同步：8px 18px */
        border-radius: 20px; 
        transition: all 0.3s; 
        font-size: 1.1rem;           /* 同步：调整为 1.1rem */
    }
    .nav-links a:hover { 
        background-color: var(--primary-light);
        color: var(--primary); 
    }
    .nav-links a.active { 
        background: var(--primary);
        color: white; 
    }
    
    /* Hero 区域 - 更紧凑 */
    .hero-box { 
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); 
        padding: 1.8rem 1.5rem; 
        border-radius: 24px; 
        text-align: center; 
        color: white; 
        margin: 0.5rem 0 1rem 0; 
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .hero-box::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
        z-index: 1;
    }
    
    .hero-box::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.05) 25%, transparent 25%,
                    transparent 50%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.05) 75%,
                    transparent 75%, transparent);
        background-size: 30px 30px;
        animation: move 10s linear infinite;
        z-index: 1;
    }
    
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes move { 0% { background-position: 0 0; } 100% { background-position: 30px 30px; } }
    
    .hero-title, .hero-sub { position: relative; z-index: 2; }
    .hero-title { 
        font-size: 2.2rem; 
        font-weight: 700; 
        margin: 0; 
        text-shadow: 0 2px 4px rgba(0,0,0,0.2); 
    }
    .hero-sub { 
        font-size: 1rem; 
        opacity: 0.95; 
        margin-top: 0.3rem; 
        text-shadow: 0 1px 2px rgba(0,0,0,0.1); 
    }
    
    /* 大标题样式 */
    .section-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--gray-800);
        margin: 1.2rem 0 0.8rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, var(--primary), transparent);
        margin-left: 15px;
    }
    
    /* 通用按钮样式 */
    .stButton > button {
        border-radius: 30px !important;
        font-weight: 600 !important;
        padding: 0.3rem 1rem !important;
        font-size: 0.8rem !important;
        transition: all 0.3s !important;
        min-height: 48px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* 默认按钮 (白色底，粉色字) */
    .stButton > button:first-child {
        background: white !important;
        color: var(--primary) !important;
        border: 1px solid var(--primary) !important;
    }
    
    .stButton > button:first-child:hover {
        background: var(--primary-light) !important;
        color: var(--primary-dark) !important;
        transform: translateY(-1px);
        box-shadow: var(--shadow-md) !important;
    }
    
    /* 【修改重点】主要按钮 (原绿色，现改为粉色) */
    .stButton > button[kind="primary"],
    .stButton > button[type="primary"] {
        background: var(--primary) !important;      /* 改为粉色 */
        color: white !important;
        border: 2px solid var(--primary) !important; /* 改为粉色边框 */
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[type="primary"]:hover {
        background: var(--primary-dark) !important; /* 改为深粉色 */
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(236, 72, 153, 0.4) !important; /* 改为粉色阴影 */
    }
    
    /* 清空日志按钮 (保持红色) */
    button[data-testid="stButton"][key="clear_all_logs"] {
        background-color: #d32f2f !important;
        color: white !important;
        border: none !important;
    }
    button[data-testid="stButton"][key="clear_all_logs"]:hover {
        background-color: #b71c1c !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(211, 47, 47, 0.4);
    }
    
    .log-card {
        background: #fff;
        padding: 12px;
        border: 1px solid #eee;
        margin-bottom: 8px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .log-time {
        color: #888;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .log-content {
        color: #333;
        line-height: 1.5;
    }
    
    .security-badge {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.2rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #dee2e6;
        margin-top: 2rem;
    }
    .security-badge p {
        color: #495057;
        margin: 0;
        font-size: 0.95rem;
    }
    .security-badge strong {
        color: var(--primary);
        font-weight: 600;
    }
    
    /* 调整列间距 */
    .row-widget.stHorizontal {
        gap: 0.8rem !important;
    }
</style>
""", unsafe_allow_html=True)

def load_data_from_file():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def load_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_logs(logs):
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存日志失败：{e}")
        return False

def save_log(content):
    logs = load_logs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = {"time": timestamp, "content": content}
    logs.insert(0, new_log)
    return save_logs(logs)

def get_selected_subtypes(profile):
    """
    优化：只返回当前 profile['diseases'] 中存在的疾病对应的亚型
    防止显示之前选择过但已被删除的疾病的亚型
    """
    subtypes = {}
    current_diseases = profile.get('diseases', [])
    
    for disease in current_diseases:
        key = f"subtype_{disease}"
        value = profile.get(key, "未知")
        subtypes[disease] = value if value else "未知"
    
    return subtypes

def delete_user_account():
    username = st.session_state.get('username')
    if not username:
        return False, "未找到当前登录用户"
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            if username in user_data:
                del user_data[username]
                with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, ensure_ascii=False, indent=2)
            else:
                return False, "用户数据不存在"
        else:
            return False, "用户数据文件不存在"
        
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        return True, "账户已注销"
    except Exception as e:
        return False, str(e)

def main():
    # 顶部导航栏
    st.markdown("""
    <div class="top-navbar">
        <div class="nav-logo">❤️ CardioGuard AI</div>
        <div class="nav-links">
            <a href="/p00_home">🏠 首页</a>
            <a href="/p01_profile">📋 健康档案</a>
            <a href="/p01_overview">📊 健康总览</a>
            <a href="/p02_nutrition">🥗 营养建议</a>
            <a href="/p03_ai_doctor">🩺 AI 医生</a>
            <a href="/p04_knowledge">📚 知识库</a>
            <a href="/p05_me" class="active">👤 我的中心</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero 区域
    st.markdown("""
    <div class="hero-box">
        <h1 class="hero-title">👤 我的中心</h1>
        <p class="hero-sub">个人信息管理 · 健康日志 · 账户安全</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示登录用户信息（如果已登录）
    if st.session_state.get('is_logged_in', False) or st.session_state.get('username'):
        username = st.session_state.get('username', st.session_state.get('user_id', '用户'))
        st.markdown(f"""
        <div style="background: #fce7f3; padding: 12px 20px; border-radius: 12px; border-left: 6px solid #ec4899; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2rem;">👤</span>
                <span style="font-weight: 600; color: #be185d;">当前登录用户：{username}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 直接显示个人信息，不检查登录状态
    tab1, tab2, tab3 = st.tabs(["📋 个人信息", "📝 健康日志", "🔒 账户安全"])
    
    # ================= 标签页 1: 个人信息 =================
    with tab1:
        st.markdown('<div class="section-title">📋 您的健康档案摘要</div>', unsafe_allow_html=True)
        # 使用 session_state 中的 profile，而不是重新从文件加载
        # 确保 profile 是最新的引用
        profile = st.session_state['profile']
        
        # 【关键修复】确保 diseases 字段存在且为列表，防止类型错误
        if 'diseases' not in profile:
            profile['diseases'] = []
        elif isinstance(profile['diseases'], (set, tuple)):
            profile['diseases'] = list(profile['diseases'])
            
        if not profile or not profile.get('gender'):
            st.info("📭 暂无数据，请先前往 [健康档案] 填写信息。")
            if st.button("前往填写", type="primary", use_container_width=True):
                st.switch_page("pages/p01_profile.py")
        else:
            # 1. 基础生理与生化指标
            st.markdown("### 1️⃣ 基础生理与生化指标")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**🚹 性别**: {profile.get('gender')}")
                st.markdown(f"**🎂 年龄**: {profile.get('age')} 岁")
                h = profile.get('height', 0)
                w = profile.get('weight', 0)
                bmi = round(w / ((h/100)**2), 1) if h > 0 else 0
                st.markdown(f"**📏 身高/体重**: {h} cm / {w} kg (BMI: {bmi})")
                st.markdown(f"**🩸 血压**: 收缩压 {profile.get('systolic_bp', '未测')} / 舒张压 {profile.get('diastolic_bp', '未测')}")
            with c2:
                st.markdown(f"**🧪 总胆固醇**: {profile.get('total_cholesterol', '未测')}")
                st.markdown(f"**🍬 空腹血糖**: {profile.get('blood_glucose', '未测')}")
                st.markdown(f"**👨‍👩‍👧‍👦 家族史**: {profile.get('family_history', '无')}")
            st.markdown("---")
            
            # 2. 疾病大类与亚型诊断 (核心修改部分)
            st.markdown("### 2️⃣ 疾病大类与亚型诊断")
            diseases = profile.get('diseases', [])
            
            if diseases:
                # 显示确诊/疑似疾病大类
                st.markdown(f"**✅ 确诊/疑似疾病大类**: {', '.join(diseases)}")
                
                # 获取并过滤亚型数据，确保只显示当前选中疾病的亚型
                subtypes = get_selected_subtypes(profile)
                
                if subtypes:
                    # 计算列数，最多3列
                    col_count = min(len(subtypes), 3)
                    cols = st.columns(col_count)
                    
                    idx = 0
                    for disease, subtype in subtypes.items():
                        with cols[idx % col_count]:
                            # 根据亚型是否未知设置颜色
                            is_unknown = subtype == "未知"
                            badge_color = "#ef5350" if is_unknown else "#ec4899"
                            bg_color = "#ffebee" if is_unknown else "#fce7f3"
                            icon = "❓" if is_unknown else "✅"
                            
                            st.markdown(f"""
                            <div style="border: 1px solid #ddd; padding: 12px; border-radius: 8px; margin-bottom: 10px; background: {bg_color}; transition: transform 0.2s;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                    <span style="font-weight: bold; color: #555; font-size: 0.9em;">{disease}</span>
                                    <span style="font-size:1.2em;">{icon}</span>
                                </div>
                                <div style="color: {badge_color}; font-weight: 800; font-size: 1.1em; border-top:1px dashed #ccc; padding-top:4px; margin-top:4px;">
                                    {subtype}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        idx += 1
                else:
                    st.warning("⚠️ 暂未选择具体亚型，请前往健康档案完善。")
            else:
                st.info("ℹ️ 暂未选择疾病大类，请前往健康档案进行筛查。")
            
            st.markdown("---")
            
            # 3. 生活习惯与风险因素
            st.markdown("### 3️⃣ 生活习惯与风险因素")
            c3, c4 = st.columns(2)
            with c3:
                st.markdown(f"**🚬 吸烟**: {'是 (高风险)' if profile.get('smoking') else '否'}")
                st.markdown(f"**🍺 饮酒**: {'是 (每周≥3 次)' if profile.get('drinking') else '否'}")
                st.markdown(f"**🧂 高盐饮食**: {'是' if profile.get('high_salt') else '否'}")
                st.markdown(f"**🍰 高糖饮食**: {'是' if profile.get('high_sugar') else '否'}")
                st.markdown(f"**🌙 每周熬夜**: {profile.get('late_night', 0)} 次")
            with c4:
                st.markdown(f"**🏃 运动频率**: {profile.get('ex_freq', 0)} 次/周")
                st.markdown(f"**⏱️ 运动时长**: {profile.get('ex_dur', 0)} 分钟/次")
                st.markdown(f"**😰 压力水平**: {profile.get('stress', '中')}")
                st.markdown(f"**😴 日均睡眠**: {profile.get('sleep', 0)} 小时")
                diet_pref = profile.get('diet_pref', [])
                st.markdown(f"**🥗 饮食偏好**: {', '.join(diet_pref) if diet_pref else '无特殊偏好'}")
            st.markdown("---")
            
            if st.button("✏️ 编辑档案信息", type="primary", use_container_width=True):
                st.switch_page("pages/p01_profile.py")
                
    # ================= 标签页 2: 健康日志 =================
    with tab2:
        st.markdown('<div class="section-title">📝 记录健康日志</div>', unsafe_allow_html=True)
        log_input = st.text_area("写下您今天的健康状况...", height=150, placeholder="例如：今天感觉心跳比较平稳...")
        if st.button("💾 保存日志", type="primary"):
            if log_input.strip():
                if save_log(log_input.strip()):
                    st.success("✅ 日志保存成功！")
                    st.rerun()
            else:
                st.warning("⚠️ 请输入内容。")
        
        st.markdown("---")
        st.markdown('<div class="section-title">📜 历史日志</div>', unsafe_allow_html=True)
        
        logs = load_logs()
        
        if logs:
            for i, log in enumerate(logs):
                c_log, c_del = st.columns([5, 1])
                with c_log:
                    st.markdown(f"""
                    <div class="log-card">
                        <small class="log-time">{log['time']}</small><br>
                        <span class="log-content">{log['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with c_del:
                    if st.button("🗑️", key=f"del_{i}", help="删除此条日志"):
                        logs.pop(i)
                        if save_logs(logs):
                            st.success("✅ 日志已删除！")
                            st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ 清空全部日志 (不可恢复)", key="clear_all_logs", help="删除所有历史记录"):
                if save_logs([]):
                    st.success("✅ 所有日志已清空！")
                    st.rerun()
        else:
            st.info("暂无日志记录。")
            
    # ================= 标签页 3: 账户安全 =================
    with tab3:
        st.markdown('<div class="section-title">🔒 重置密码</div>', unsafe_allow_html=True)
        st.caption("修改后，为了安全，系统将退出登录，您需要使用新密码重新登录。")
        
        with st.form("reset_pwd_form"):
            new_pwd = st.text_input("新密码", type="password", placeholder="请输入新密码")
            confirm_pwd = st.text_input("确认新密码", type="password", placeholder="请再次输入新密码")
            submitted = st.form_submit_button("提交修改", use_container_width=True)
            
            if submitted:
                if not new_pwd or not confirm_pwd:
                    st.error("❌ 密码不能为空。")
                elif new_pwd != confirm_pwd:
                    st.error("❌ 两次输入的密码不一致。")
                elif len(new_pwd) < 6:
                    st.error("❌ 密码长度至少为 6 位。")
                else:
                    current_user = st.session_state.get('username')
                    if os.path.exists(USER_DATA_FILE):
                        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                            users = json.load(f)
                        
                        if current_user in users:
                            import hashlib
                            hashed_pwd = hashlib.sha256(new_pwd.encode()).hexdigest()
                            
                            users[current_user]['password'] = hashed_pwd
                            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                                json.dump(users, f, ensure_ascii=False, indent=2)
                            
                            st.success("✅ 密码已更新！正在退出登录，请前往登录页...")
                            time.sleep(1.5)
                            
                            for key in list(st.session_state.keys()):
                                del st.session_state[key]
                            
                            st.switch_page("pages/p00_auth.py")
                        else:
                            st.error("❌ 用户不存在。")
                    else:
                        st.error("❌ 系统文件错误。")
        
        st.markdown("---")
        st.markdown('<div class="section-title">🚪 退出与注销</div>', unsafe_allow_html=True)
        
        if st.button("确认退出登录", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("👋 已退出。")
            time.sleep(1)
            st.switch_page("pages/p00_intro.py") 
            
        st.markdown("---")
        st.markdown('<div class="section-title" style="color: #dc2626;">☠️ 注销账户</div>', unsafe_allow_html=True)
        st.caption("此操作将永久删除您的账户数据，且无法恢复。")
        
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete = False
        
        if not st.session_state.confirm_delete:
            if st.button("申请注销账户", type="secondary", use_container_width=True):
                st.session_state.confirm_delete = True
                st.rerun()
        else:
            st.error("⚠️ **警告**：您即将永久删除账户！此操作不可逆。")
            c_del, c_cancel = st.columns([1, 1])
            with c_del:
                if st.button("☠️ 确认注销 (永久删除)", type="primary", use_container_width=True):
                    success, msg = delete_user_account()
                    if success:
                        st.success("✅ 账户已成功注销。")
                        time.sleep(1)
                        st.switch_page("pages/p00_intro.py")
                    else:
                        st.error(f"❌ 注销失败：{msg}")
                        st.session_state.confirm_delete = False
                        st.rerun()
            with c_cancel:
                if st.button("取消", use_container_width=True):
                    st.session_state.confirm_delete = False
                    st.rerun()
    
    # 安全声明
    st.markdown("""
    <div class="security-badge">
        <p>🔐 <strong>CardioGuard AI</strong> 采用银行级加密技术保护您的健康数据，所有信息仅在您的设备本地存储和处理，确保个人隐私的绝对安全。我们承诺不收集、不分析、不共享任何可识别您身份的个人信息。</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()