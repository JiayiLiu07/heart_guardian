import streamlit as st
import base64

def render():
    # 页面配置
    st.set_page_config(
        page_title="CardioGuard AI - 心脏健康守护者",
        page_icon="❤️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 隐藏侧边栏和任何潜在的登录按钮
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    .stSidebar {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {
        visibility: visible !important;
    }
    .block-container {
        padding-top: 0rem !important;
    }
    .stAlert, .stSpinner, .stException {
        padding-top: 0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 医疗高科技风格CSS样式
    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
        padding: 4rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
        margin-top: -2rem !important;
    }
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #00e5ff, #2979ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        animation: gradientAnimation 5s ease infinite;
        background-size: 200% 200%;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #2979ff;
        transition: all 0.3s ease;
        cursor: pointer;
        backdrop-filter: blur(10px);
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(41, 121, 255, 0.2);
    }
    .tech-card {
        background: linear-gradient(135deg, #f8fdff 0%, #e3f2fd 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e1f5fe;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .tech-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #2979ff, #00e5ff);
    }
    .tech-card:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 25px rgba(41, 121, 255, 0.15);
    }
    .step-card {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem;
        text-align: center;
        transition: all 0.3s ease;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .step-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(41, 121, 255, 0.3);
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        margin: 2rem 0;
        background: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    .stat-item {
        text-align: center;
        padding: 1rem;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #2979ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        font-weight: 500;
    }
    .cta-button {
        background: linear-gradient(45deg, #2979ff, #00e5ff);
        color: white;
        padding: 15px 30px;
        border: none;
        border-radius: 25px;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        margin: 1rem;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(41, 121, 255, 0.3);
    }
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(41, 121, 255, 0.4);
        color: white;
        text-decoration: none;
    }
    .video-disease-container {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
        align-items: stretch;
    }
    .bilibili-container {
        width: 100%;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        height: 450px;
    }
    .disease-card {
        background: linear-gradient(135deg, #f5faff 0%, #e8f0fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0, 100, 200, 0.2);
        border: 1px solid #b0c4de;
        height: 450px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
    .disease-card h4 {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1a237e;
        background: linear-gradient(45deg, #2979ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .disease-card p {
        font-size: 1rem;
        color: #333;
        margin: 0.3rem 0;
    }
    .carousel-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem;
        border-left: 4px solid #00e5ff;
        animation: fadeIn 1s ease-in;
        backdrop-filter: blur(10px);
        min-width: 300px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stButton button {
        background: linear-gradient(45deg, #2979ff, #00e5ff);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-size: 1.4rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(41, 121, 255, 0.3);
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(41, 121, 255, 0.4);
    }
    .nav-buttons {
        display: flex;
        gap: 15px;
        justify-content: center;
        margin: 2rem 0;
    }
    .step-container {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
    }
    .step-number {
        background: linear-gradient(45deg, #2979ff, #00e5ff);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
        flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(41, 121, 255, 0.3);
    }
    .step-content {
        flex: 1;
    }
    .faq-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 2rem 0;
    }
    .faq-card {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f0fa 100%);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 100, 200, 0.2);
        margin: 1rem 0;
        border: 1px solid #b0c4de;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        min-height: 150px;
    }
    .faq-card:hover {
        box-shadow: 0 0 25px rgba(0, 100, 200, 0.3);
        transform: scale(1.02);
    }
    .faq-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at top left, rgba(255, 255, 255, 0.3), transparent);
        opacity: 0.5;
    }
    .health-tips-container {
        width: 100%;
        overflow: hidden;
        padding: 1rem 0;
    }
    .health-tips-carousel {
        display: flex;
        gap: 1rem;
        animation: scroll 120s linear infinite;
        width: max-content;
    }
    @keyframes scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(calc(-296px * 14)); }
    }
    .health-tips-carousel:hover {
        animation-play-state: paused;
    }
    .tip-card {
        background: linear-gradient(135deg, #f5faff 0%, #e8f0fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        min-width: 280px;
        border-left: 4px solid #00e5ff;
        box-shadow: 0 8px 20px rgba(0, 100, 200, 0.2);
        flex-shrink: 0;
        transition: all 0.3s ease;
    }
    .tip-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(0, 100, 200, 0.3);
    }
    .tip-card h4 {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1a237e;
        background: linear-gradient(45deg, #2979ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .tip-card p {
        font-size: 0.95rem;
        color: #333;
        margin: 0.2rem 0;
    }
    .centered {
        text-align: center;
    }
    .section-title {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(45deg, #00e5ff, #2979ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientAnimation 5s ease infinite;
        background-size: 200% 200%;
    }
    .dynamic-title {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(45deg, #00e5ff, #2979ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientAnimation 5s ease infinite, scaleAnimation 2s ease-in-out infinite;
        background-size: 200% 200%;
    }
    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes scaleAnimation {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)

    # 英雄区域
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">❤️ CardioGuard AI</h1>
        <p class="hero-subtitle">「管理心脏健康，从每一次跳动开始」</p>
    </div>
    """, unsafe_allow_html=True)

    # 视频和疾病分类模块
    st.markdown("---")
    st.markdown('<div class="centered"><h3 class="section-title">心血管健康概览</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="video-disease-container">', unsafe_allow_html=True)
    video_col, disease_col = st.columns([1, 1])
    
    with video_col:
        st.markdown("""
        <div class="bilibili-container">
            <iframe 
                src="//player.bilibili.com/player.html?bvid=BV1xZ4y1Z7Xw&page=1&high_quality=1&autoplay=1" 
                scrolling="no" 
                border="0" 
                frameborder="no" 
                framespacing="0" 
                allowfullscreen="true" 
                width="100%" 
                height="450">
            </iframe>
        </div>
        """, unsafe_allow_html=True)
    
    with disease_col:
        st.markdown("""
        <div class="disease-card">
            <h4>心血管疾病分类</h4>
            <p><strong>缺血性心脏病</strong>: 稳定型心绞痛、急性冠脉综合征（心梗等）</p>
            <p><strong>高血压性心脏病</strong>: 原发性高血压损害、高血压肾心病</p>
            <p><strong>心律失常</strong>: 房颤、室速、长 QT、Brugada 综合征等</p>
            <p><strong>心力衰竭</strong>: HFrEF、HFpEF、右心衰竭</p>
            <p><strong>心肌病</strong>: 肥厚型（HCM）、扩张型（DCM）、ARVC</p>
            <p><strong>心脏瓣膜病</strong>: 二尖瓣/主动脉瓣狭窄或关闭不全、二叶式主动脉瓣</p>
            <p><strong>先天性心脏病</strong>: 房缺、室缺、法洛四联症等</p>
            <p><strong>主动脉/大血管疾病</strong>: 主动脉瘤、夹层、马凡综合征</p>
            <p><strong>肺血管疾病</strong>: 肺动脉高压、慢性血栓栓塞</p>
            <p><strong>心包疾病</strong>: 心包炎、缩窄性心包炎</p>
            <p><strong>周围动脉疾病</strong>: 下肢动脉闭塞、动脉栓塞</p>
            <p><strong>静脉/淋巴疾病</strong>: 深静脉血栓、静脉曲张</p>
            <p><strong>感染性/免疫性心脏病</strong>: 风湿性瓣膜病、心肌炎</p>
            <p><strong>心脏肿瘤</strong>: 黏液瘤、横纹肌瘤</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 主要行动号召按钮
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h2 class="dynamic-title">🚀 立即开始您的心脏健康管理之旅</h2>
        <p style="font-size: 1.2rem; margin-bottom: 2rem;">加入数万名用户，体验专业的AI心脏健康分析服务</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 立即开始免费分析", use_container_width=True, type="primary"):
            # 直接跳转到登录页面
            st.switch_page("pages/p00_auth.py")



    # 统计数据 - 移动到按钮下面
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">99.2%</div>
            <div class="stat-label">预测准确率</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">50,000+</div>
            <div class="stat-label">已分析病例</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">24/7</div>
            <div class="stat-label">实时监测</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">95%</div>
            <div class="stat-label">用户满意度</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 功能介绍
    st.markdown("---")
    st.markdown('<div class="centered"><h3 class="section-title">🎯 核心功能</h3></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 智能分析</h3>
            <p>基于XGBoost机器学习算法，精准分析心脏健康数据，提供专业风险评估。</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📈 数据可视化</h3>
            <p>直观的数据图表展示，帮助您更好地理解心脏健康状况和趋势变化。</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🛡️ 风险预警</h3>
            <p>实时监测异常指标，及时发出健康预警，为您的健康保驾护航。</p>
        </div>
        """, unsafe_allow_html=True)

    # 技术特性
    st.markdown("---")
    st.markdown('<div class="centered"><h3 class="section-title">🔬 技术特性</h3></div>', unsafe_allow_html=True)

    tech_col1, tech_col2 = st.columns(2)

    with tech_col1:
        st.markdown("""
        <div class="tech-card">
            <h4>🤖 机器学习模型</h4>
            <ul>
            <li><strong>XGBoost算法</strong>：业界领先的梯度提升框架</li>
            <li><strong>特征工程</strong>：自动提取关键健康指标</li>
            <li><strong>模型优化</strong>：持续学习和性能提升</li>
            <li><strong>交叉验证</strong>：确保模型稳定性和可靠性</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="tech-card">
            <h4>📊 数据分析能力</h4>
            <ul>
            <li><strong>多维度分析</strong>：年龄、血压、胆固醇等综合评估</li>
            <li><strong>趋势预测</strong>：基于历史数据的健康趋势分析</li>
            <li><strong>异常检测</strong>：自动识别异常波动和风险信号</li>
            <li><strong>个性化报告</strong>：定制化的健康建议和改善方案</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with tech_col2:
        st.markdown("""
        <div class="tech-card">
            <h4>🎨 可视化展示</h4>
            <ul>
            <li><strong>交互式图表</strong>：支持缩放、筛选和详细查看</li>
            <li><strong>实时仪表盘</strong>：关键指标一目了然</li>
            <li><strong>健康报告</strong>：专业美观的PDF报告生成</li>
            <li><strong>移动适配</strong>：完美支持各种设备访问</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="tech-card">
            <h4>🔒 数据安全</h4>
            <ul>
            <li><strong>隐私保护</strong>：严格的数据加密和访问控制</li>
            <li><strong>本地处理</strong>：敏感数据可在本地完成分析</li>
            <li><strong>合规性</strong>：符合医疗数据安全标准</li>
            <li><strong>备份恢复</strong>：完善的数据备份和恢复机制</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # FAQ 模块
    st.markdown("---")
    st.markdown('<div class="centered"><h3 class="section-title">❓ 常见问题</h3></div>', unsafe_allow_html=True)

    faq_col1, faq_col2 = st.columns(2)

    with faq_col1:
        st.markdown("""
        <div class="faq-card">
            <h4>🔒 我的数据安全吗？</h4>
            <p>您的安全是我们的首要任务！我们采用银行级加密技术，严格遵循隐私法规，确保您的健康数据仅用于分析，绝不外泄。</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="faq-card">
            <h4>💰 这项服务是免费的吗？</h4>
            <p>当然！基础分析完全免费，助您轻松开启健康之旅。高级功能需订阅，但物超所值，欢迎随时体验！</p>
        </div>
        """, unsafe_allow_html=True)

    with faq_col2:
        st.markdown("""
        <div class="faq-card">
            <h4>📱 支持移动设备吗？</h4>
            <p>是的！我们的平台采用响应式设计，支持手机、平板和电脑，让您随时随地管理心脏健康，方便又贴心！</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="faq-card">
            <h4>🩺 分析结果准确吗？</h4>
            <p>我们的算法基于海量临床数据，准确率高！但结果仅供参考，建议结合专业医生意见，守护您的健康更安心！</p>
        </div>
        """, unsafe_allow_html=True)

    # 心血管健康小贴士
    st.markdown("---")
    st.markdown('<div class="centered"><h3 class="section-title">💡 心血管健康小贴士</h3></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="health-tips-container">
        <div class="health-tips-carousel">
            <div class="tip-card">
                <h4>缺血性心脏病预防</h4>
                <p>• 定期检查血脂</p>
                <p>• 低脂饮食，控制体重</p>
                <p>• 适度有氧运动</p>
                <p>• 戒烟限酒</p>
            </div>
            <div class="tip-card">
                <h4>高血压性心脏病管理</h4>
                <p>• 每日监测血压</p>
                <p>• 减少盐分摄入</p>
                <p>• 规律运动，减压</p>
                <p>• 遵医嘱服药</p>
            </div>
            <div class="tip-card">
                <h4>心律失常预防</h4>
                <p>• 避免过度咖啡因</p>
                <p>• 保持电解质平衡</p>
                <p>• 规律作息，减压</p>
                <p>• 定期心电图检查</p>
            </div>
            <div class="tip-card">
                <h4>心力衰竭护理</h4>
                <p>• 限制液体摄入</p>
                <p>• 低盐饮食控制</p>
                <p>• 监测体重变化</p>
                <p>• 遵医嘱用药</p>
            </div>
            <div class="tip-card">
                <h4>心肌病管理</h4>
                <p>• 定期心脏超声</p>
                <p>• 避免过度运动</p>
                <p>• 控制基础疾病</p>
                <p>• 遗传咨询（HCM/DCM）</p>
            </div>
            <div class="tip-card">
                <h4>心脏瓣膜病护理</h4>
                <p>• 定期超声检查</p>
                <p>• 预防感染性心内膜炎</p>
                <p>• 适度活动</p>
                <p>• 遵医嘱服药</p>
            </div>
            <div class="tip-card">
                <h4>先天性心脏病关注</h4>
                <p>• 定期随访医生</p>
                <p>• 注意感染预防</p>
                <p>• 适度运动规划</p>
                <p>• 心理支持</p>
            </div>
            <div class="tip-card">
                <h4>主动脉疾病预防</h4>
                <p>• 控制血压、血脂</p>
                <p>• 戒烟，健康饮食</p>
                <p>• 定期影像学检查</p>
                <p>• 遗传咨询（马凡等）</p>
            </div>
            <div class="tip-card">
                <h4>肺血管疾病管理</h4>
                <p>• 定期肺功能检查</p>
                <p>• 遵医嘱用药</p>
                <p>• 避免高海拔活动</p>
                <p>• 遗传咨询（PAH）</p>
            </div>
            <div class="tip-card">
                <h4>心包疾病护理</h4>
                <p>• 及时治疗感染</p>
                <p>• 定期影像学检查</p>
                <p>• 注意休息</p>
                <p>• 遵医嘱用药</p>
            </div>
            <div class="tip-card">
                <h4>周围动脉疾病预防</h4>
                <p>• 控制血糖、血脂</p>
                <p>• 戒烟，适度运动</p>
                <p>• 定期血管检查</p>
                <p>• 避免久坐</p>
            </div>
            <div class="tip-card">
                <h4>静脉疾病管理</h4>
                <p>• 避免长时间站立</p>
                <p>• 穿弹力袜</p>
                <p>• 定期运动，促进循环</p>
                <p>• 监测血栓风险</p>
            </div>
            <div class="tip-card">
                <h4>感染性心脏病预防</h4>
                <p>• 及时治疗感染</p>
                <p>• 预防风湿热</p>
                <p>• 定期口腔检查</p>
                <p>• 遵医嘱用抗生素</p>
            </div>
            <div class="tip-card">
                <h4>心脏肿瘤关注</h4>
                <p>• 定期影像学检查</p>
                <p>• 关注家族史</p>
                <p>• 遗传咨询（黏液瘤等）</p>
                <p>• 遵医嘱随访</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>© 2024 CardioGuard AI - 心脏健康守护者 | 专业医疗级AI分析平台</p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">本产品仅供健康监测参考，不能替代专业医疗诊断</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()