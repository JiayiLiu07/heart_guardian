import streamlit as st

def render():
    """首页渲染函数 - 医疗专业化版本 (已移除实时数据条)"""
    # 自定义CSS样式 - 医疗专业版
    st.markdown("""
    <style>
        /* 隐藏默认元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 强制隐藏顶部导航栏 */
        .top-navbar { display: none !important; }
        div[class*="top-navbar"] { display: none !important; }
        .stApp header { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        
        /* 隐藏Streamlit默认元素 - 增强版 */
        .stApp footer { display: none !important; }
        .stApp [data-testid="stFooter"] { display: none !important; }
        .st-emotion-cache-1jicfl2 { display: none !important; }
        .st-emotion-cache-15zws58 { display: none !important; }
        .st-emotion-cache-1aehpvj { display: none !important; }
        .st-emotion-cache-1dp5vir { display: none !important; }
        .st-emotion-cache-1r6slb0 { display: none !important; }
        .st-emotion-cache-1wmy9hl { display: none !important; }
        
        /* 隐藏所有可能的Streamlit生成的底部元素 */
        [data-testid="stBottom"] { display: none !important; }
        [data-testid="stBottomBlock"] { display: none !important; }
        
        /* ===== 医疗专业色彩系统 ===== */
        :root {
            --medical-blue-dark: #0D47A1;
            --medical-blue: #1976D2;
            --medical-blue-light: #E3F2FD;
            --medical-green: #00897B;
            --medical-red: #E53935;
            --medical-accent: #FF6F00;
            --text-primary: #1A237E;
            --text-secondary: #546E7A;
            --bg-white: #FAFBFC;
            --bg-soft: #F0F4F8;
            --border-light: #ECEFF1;
        }
        
        /* 全局样式 - 医疗渐变背景 */
        .stApp {
            background: linear-gradient(180deg, #FAFBFC 0%, #F0F4F8 100%) !important;
        }
        
        .main {
            background: transparent;
            padding: 2rem;
        }
        
        /* 所有文字颜色 */
        body, p, h1, h2, h3, h4, h5, h6, div, span, label {
            color: var(--text-primary) !important;
        }
        
        /* ===== 自定义滚动条 ===== */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-soft);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb {
            background: var(--medical-blue);
            border-radius: 10px;
            transition: all 0.2s ease;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--medical-blue-dark);
        }
        
        /* ===== 标题区域增强 ===== */
        .hero-section {
            text-align: center;
            padding: 1.5rem 0 0.5rem 0;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        /* 背景网格渐变 */
        .hero-bg-grid {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(var(--medical-blue-light) 1px, transparent 1px),
                linear-gradient(90deg, var(--medical-blue-light) 1px, transparent 1px);
            background-size: 40px 40px;
            opacity: 0.3;
            z-index: 0;
            mask-image: radial-gradient(circle at center, black 40%, transparent 80%);
            -webkit-mask-image: radial-gradient(circle at center, black 40%, transparent 80%);
        }
        /* 主标题 - 打字机效果 */
        .main-title {
            font-size: 4.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #0D47A1, #1976D2, #00897B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 auto;
            padding: 0 140px;
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            letter-spacing: 2px;
            display: inline-block;
            position: relative;
            text-align: center;
            left: 50%;
            transform: translateX(-50%);
            animation: titleGlow 3s ease-in-out infinite;
            white-space: nowrap;
            z-index: 1;
            border-right: 2px solid var(--medical-blue);
            width: 0;
            overflow: hidden;
            animation: 
                typing 3.5s steps(30, end) forwards,
                blink-caret 0.75s step-end infinite,
                titleGlow 3s ease-in-out infinite 3.5s;
        }
        @keyframes typing {
            from { width: 0; }
            to { width: 100%; }
        }
        @keyframes blink-caret {
            from, to { border-color: transparent; }
            50% { border-color: var(--medical-blue); }
        }
        @keyframes titleGlow {
            0%, 100% { text-shadow: 0 0 20px rgba(13, 71, 161, 0.3); }
            50% { text-shadow: 0 0 30px rgba(25, 118, 210, 0.6); }
        }
        .main-title::before {
            content: "❤️";
            font-size: 4.5rem;
            position: absolute;
            left: -60px;
            top: 50%;
            transform: translateY(-50%);
            animation: heartbeat 1.8s ease-in-out infinite;
            z-index: 2;
        }
        .main-title::after {
            content: "🩺";
            font-size: 3.8rem;
            position: absolute;
            right: -60px;
            top: 45%;
            animation: float 3s ease-in-out infinite;
            z-index: 2;
        }
        @keyframes heartbeat {
            0%, 100% { transform: translateY(-50%) scale(1); }
            25% { transform: translateY(-50%) scale(1.1); }
            35% { transform: translateY(-50%) scale(1); }
            45% { transform: translateY(-50%) scale(1.05); }
            55% { transform: translateY(-50%) scale(1); }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        /* 心电图装饰线 - 实时绘制动画 */
        .ecg-line {
            width: 160px;
            height: 30px;
            margin: 0.2rem auto 1rem;
            position: relative;
            z-index: 1;
        }
        
        .ecg-line svg {
            width: 100%;
            height: 100%;
            animation: ecgBeat 1.5s ease-in-out infinite;
        }
        
        @keyframes ecgBeat {
            0%, 100% { transform: scaleX(1); }
            50% { transform: scaleX(1.05); }
        }
        
        .ecg-path {
            stroke: var(--medical-red);
            stroke-width: 2;
            fill: none;
            stroke-dasharray: 1000;
            stroke-dashoffset: 1000;
            animation: ecgDraw 3s ease-in-out infinite;
        }
        
        @keyframes ecgDraw {
            0% { stroke-dashoffset: 1000; }
            50% { stroke-dashoffset: 0; }
            100% { stroke-dashoffset: 1000; }
        }
        /* ===== 平台定位容器增强 ===== */
        .platform-container {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 2px solid var(--medical-blue-light);
            border-radius: 30px;
            padding: 1rem 2.5rem;
            margin: 0.5rem auto 1.5rem;
            max-width: 850px;
            box-shadow: 0 8px 25px rgba(13, 71, 161, 0.08);
            transition: all 0.3s ease;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            z-index: 1;
            overflow: hidden;
            animation: borderPulse 3s infinite;
        }
        @keyframes borderPulse {
            0% { border-color: rgba(227, 242, 253, 0.8); box-shadow: 0 8px 25px rgba(13, 71, 161, 0.08); }
            50% { border-color: rgba(25, 118, 210, 0.6); box-shadow: 0 8px 35px rgba(13, 71, 161, 0.15); }
            100% { border-color: rgba(227, 242, 253, 0.8); box-shadow: 0 8px 25px rgba(13, 71, 161, 0.08); }
        }
        /* 3D 倾斜效果 */
        .platform-container-inner {
            transition: transform 0.3s ease;
            transform-style: preserve-3d;
            perspective: 1000px;
        }
        
        .platform-container:hover .platform-container-inner {
            transform: rotateX(5deg) rotateY(5deg) scale(1.02);
        }
        /* 浮动小图标 */
        .floating-icon {
            position: absolute;
            font-size: 1.2rem;
            opacity: 0.6;
            animation: floatIcon 4s ease-in-out infinite;
            color: var(--medical-blue);
        }
        .fi-1 { top: 10%; left: 10%; animation-delay: 0s; }
        .fi-2 { bottom: 15%; right: 15%; animation-delay: 1s; }
        .fi-3 { top: 20%; right: 10%; animation-delay: 2s; }
        .fi-4 { bottom: 10%; left: 20%; animation-delay: 1.5s; }
        @keyframes floatIcon {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-15px) rotate(10deg); }
        }
        .platform-sub {
            font-size: 1.4rem;
            font-weight: 600;
            background: linear-gradient(135deg, var(--medical-blue-dark), var(--medical-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            letter-spacing: 1.2px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.8rem;
            flex-wrap: nowrap;
            text-align: center;
            position: relative;
            z-index: 2;
        }
        .platform-sub-icon {
            font-size: 1.6rem;
            color: var(--medical-accent) !important;
            -webkit-text-fill-color: var(--medical-accent);
        }
        /* ===== 按钮区域增强 ===== */
        .start-button-wrapper {
            text-align: center;
            margin: 1.5rem auto 3rem;
            width: 100%;
            display: flex;
            justify-content: center;
            position: relative;
            z-index: 10;
        }
        .stButton {
            display: flex;
            justify-content: center;
            width: 100%;
            position: relative;
        }
        .btn-magnetic-area {
            position: relative;
            display: inline-block;
        }
        .stButton > button {
            background: linear-gradient(145deg, #0D47A1, #1976D2) !important;
            color: #FFFFFF !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            padding: 1.2rem 8.5rem !important;
            border: 3px solid rgba(255, 255, 255, 0.5) !important;
            border-radius: 70px !important;
            cursor: pointer !important;
            box-shadow: 0 4px 20px rgba(13, 71, 161, 0.4), 0 0 0 2px rgba(255, 255, 255, 0.2) !important;
            width: auto !important;
            min-width: 580px !important;
            margin: 0 auto !important;
            transition: transform 0.1s ease-out !important;
            letter-spacing: 2px;
            position: relative;
            overflow: visible !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }
        .stButton > button::before {
            content: "✚";
            font-size: 2.5rem;
            margin-right: 18px;
            display: inline-block;
            filter: drop-shadow(0 2px 2px rgba(0,0,0,0.2));
        }
        /* 涟漪动画 */
        .stButton > button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 100%;
            height: 100%;
            border-radius: 70px;
            border: 2px solid white;
            transform: translate(-50%, -50%) scale(1);
            opacity: 0;
            animation: pulse-ring 2s infinite;
            pointer-events: none;
        }
        @keyframes pulse-ring {
            0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
            100% { transform: translate(-50%, -50%) scale(1.3); opacity: 0; }
        }
        .stButton > button:hover {
            background: linear-gradient(145deg, #1565C0, #1E88E5) !important;
            box-shadow: 0 8px 30px rgba(13, 71, 161, 0.6), 0 0 0 4px rgba(255, 255, 255, 0.3) !important;
            color: #FFFFFF !important;
            border-color: white !important;
        }
        /* 悬浮提示 Tooltip */
        .btn-tooltip {
            position: absolute;
            bottom: -40px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--medical-blue-dark);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            z-index: 20;
        }
        .btn-tooltip::before {
            content: '';
            position: absolute;
            top: -4px;
            left: 50%;
            transform: translateX(-50%);
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 5px solid var(--medical-blue-dark);
        }
        .btn-magnetic-area:hover .btn-tooltip {
            opacity: 1;
            visibility: visible;
            bottom: -50px;
        }
        
        /* ===== 专业分隔线 ===== */
        .section-divider {
            width: 120px;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--medical-blue), var(--medical-green), var(--medical-blue), transparent);
            margin: 1.5rem auto;
            border-radius: 2px;
        }
        
        /* ===== 区块标题 ===== */
        .section-title {
            text-align: center;
            color: var(--text-primary) !important;
            font-size: 2.2rem;
            font-weight: 700;
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            margin: 2.5rem auto 1.5rem;
            position: relative;
            padding-bottom: 1rem;
            max-width: 1200px;
            z-index: 1;
        }
        .section-title::after {
            content: "";
            display: block;
            width: 70px;
            height: 3px;
            background: linear-gradient(to right, var(--medical-red), var(--medical-blue), var(--medical-green));
            margin: 0.6rem auto 0;
            border-radius: 3px;
            animation: lineWidth 2s ease-in-out infinite;
        }
        @keyframes lineWidth {
            0%, 100% { width: 70px; }
            50% { width: 110px; }
        }
        
        /* ===== 视频容器 ===== */
        .video-container {
            max-width: 900px;
            margin: 1.5rem auto 2rem;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(13, 71, 161, 0.1);
            background: white;
            padding: 1rem;
            border: 1px solid var(--border-light);
            transition: all 0.3s ease;
            position: relative;
            z-index: 1;
        }
        .video-container:hover {
            transform: scale(1.02);
            box-shadow: 0 15px 40px rgba(13, 71, 161, 0.2);
            border-color: var(--medical-blue);
        }
        .video-wrapper {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 16px;
            background: #000;
        }
        .video-wrapper iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }
        
        /* ===== 数据标签 ===== */
        .data-label {
            background: var(--medical-blue-light);
            color: var(--medical-blue-dark) !important;
            padding: 0.2rem 0.8rem;
            border-radius: 30px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
            margin: 0.2rem;
            border: 1px solid var(--medical-blue);
        }
        
        /* ===== 疾病卡片 ===== */
        .disease-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.2rem;
            margin: 1.5rem auto 2rem;
            max-width: 1200px;
            position: relative;
            z-index: 1;
        }
        .disease-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem 1rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
            border: 1px solid var(--border-light);
            animation: cardFloat 5s ease-in-out infinite;
            position: relative;
            overflow: hidden;
        }
        .disease-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            width: 4px;
            height: 100%;
            background: var(--medical-blue);
            transition: all 0.3s ease;
        }
        .disease-card:hover::before {
            width: 6px;
            background: var(--medical-green);
        }
        .disease-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 30px rgba(13, 71, 161, 0.15);
            border-color: var(--medical-blue);
        }
        .disease-icon {
            font-size: 2.5rem;
            margin-bottom: 0.8rem;
            background: linear-gradient(135deg, var(--medical-blue-light), white);
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.8rem;
            transition: all 0.3s ease;
        }
        .disease-card:hover .disease-icon {
            background: var(--medical-blue);
            transform: scale(1.1);
            color: white !important;
        }
        .disease-name {
            color: var(--text-primary) !important;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }
        .disease-desc {
            color: var(--text-secondary) !important;
            font-size: 0.85rem;
            line-height: 1.4;
            margin-bottom: 0.6rem;
        }
        .accuracy-badge {
            background: var(--medical-green);
            color: white !important;
            padding: 0.15rem 0.6rem;
            border-radius: 30px;
            font-size: 0.7rem;
            font-weight: 600;
            display: inline-block;
            position: absolute;
            top: 8px;
            right: 8px;
        }
        
        /* ===== 核心功能卡片 ===== */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin: 1.5rem auto 2.5rem;
            max-width: 1200px;
            position: relative;
            z-index: 1;
        }
        .feature-card {
            background: white;
            border-radius: 20px;
            padding: 2rem 1.2rem;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
            border: 1px solid var(--border-light);
            animation: featureFloat 6s ease-in-out infinite;
            position: relative;
            overflow: hidden;
        }
        .feature-card::before {
            content: "✚";
            font-size: 6rem;
            position: absolute;
            right: -15px;
            bottom: -15px;
            opacity: 0.03;
            color: var(--medical-blue);
            transform: rotate(15deg);
        }
        .feature-card:nth-child(2) { animation-delay: 0.3s; }
        .feature-card:nth-child(3) { animation-delay: 0.6s; }
        @keyframes featureFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-4px); }
        }
        .feature-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 25px 35px rgba(13, 71, 161, 0.15);
            border-color: var(--medical-blue);
        }
        .feature-icon {
            font-size: 2.8rem;
            margin-bottom: 1.2rem;
            background: linear-gradient(135deg, var(--medical-blue-light), white);
            width: 70px;
            height: 70px;
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.2rem;
            transition: all 0.3s ease;
        }
        .feature-card:hover .feature-icon {
            background: var(--medical-blue);
            transform: rotate(5deg) scale(1.1);
            color: white !important;
        }
        .feature-title {
            color: var(--text-primary) !important;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }
        .feature-desc {
            color: var(--text-secondary) !important;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .stat-highlight {
            color: var(--medical-blue-dark) !important;
            font-weight: 700;
            font-size: 1.05em;
        }
        
        /* ===== 优势卡片 ===== */
        .advantage-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            margin: 1.5rem auto 2rem;
            max-width: 1200px;
            position: relative;
            z-index: 1;
        }
        .advantage-card {
            background: white;
            border-radius: 18px;
            padding: 1.8rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
            display: flex;
            align-items: flex-start;
            gap: 1.2rem;
            border: 1px solid var(--border-light);
            animation: advantageSlide 5s ease-in-out infinite;
            position: relative;
            overflow: hidden;
        }
        .advantage-card::before {
            content: "🏥";
            font-size: 5rem;
            position: absolute;
            right: -5px;
            bottom: -5px;
            opacity: 0.05;
            transform: rotate(10deg);
        }
        .advantage-card:nth-child(2) { animation-delay: 0.2s; }
        .advantage-card:nth-child(3) { animation-delay: 0.4s; }
        .advantage-card:nth-child(4) { animation-delay: 0.6s; }
        @keyframes advantageSlide {
            0%, 100% { transform: translateX(0); }
            50% { transform: translateX(4px); }
        }
        .advantage-card:hover {
            transform: translateX(6px) scale(1.01);
            box-shadow: 0 20px 30px rgba(13, 71, 161, 0.15);
            border-color: var(--medical-blue);
        }
        .advantage-icon {
            font-size: 2.2rem;
            flex-shrink: 0;
            background: linear-gradient(135deg, var(--medical-blue), var(--medical-blue-dark));
            width: 55px;
            height: 55px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white !important;
            transition: all 0.3s ease;
        }
        .advantage-card:hover .advantage-icon {
            transform: scale(1.1) rotate(5deg);
            box-shadow: 0 10px 20px rgba(13, 71, 161, 0.3);
        }
        .advantage-content {
            flex: 1;
        }
        .advantage-title {
            color: var(--text-primary) !important;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }
        .advantage-desc {
            color: var(--text-secondary) !important;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 0.5rem;
        }
        
        /* ===== 健康小贴士 ===== */
        .tips-section {
            background: white;
            border-radius: 30px;
            padding: 1.8rem;
            margin: 1.2rem auto 2.5rem;
            border: 1px solid var(--border-light);
            overflow: hidden;
            max-width: 1200px;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.02);
            z-index: 1;
        }
        .tips-scroll {
            display: flex;
            gap: 1.2rem;
            animation: scroll 60s linear infinite;
            width: max-content;
            padding: 0.5rem 0;
        }
        .tips-section:hover .tips-scroll {
            animation-play-state: paused;
        }
        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        .tip-card {
            min-width: 280px;
            background: linear-gradient(145deg, white, var(--bg-soft));
            border-radius: 18px;
            padding: 1.8rem 1.2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.02);
            border: 1px solid var(--border-light);
            flex-shrink: 0;
            transition: all 0.3s ease;
            position: relative;
        }
        .tip-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--medical-blue), var(--medical-green));
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        .tip-card:hover::before {
            transform: scaleX(1);
        }
        .tip-card:hover {
            transform: scale(1.05) translateY(-6px);
            box-shadow: 0 25px 35px rgba(13, 71, 161, 0.15);
            border-color: var(--medical-blue);
        }
        .tip-icon {
            font-size: 2.2rem;
            margin-bottom: 0.6rem;
            transition: transform 0.3s ease;
        }
        .tip-card:hover .tip-icon {
            transform: scale(1.2) rotate(5deg);
        }
        .tip-title {
            color: var(--medical-blue-dark) !important;
            font-size: 1.2rem;
            font-weight: 700;
            margin: 0.4rem 0 0.8rem;
            transition: color 0.3s ease;
        }
        .tip-item {
            color: var(--text-secondary) !important;
            font-size: 0.9rem;
            padding: 0.3rem 0;
            border-bottom: 1px dashed var(--border-light);
            transition: all 0.3s ease;
        }
        .tip-card:hover .tip-item {
            color: var(--text-primary) !important;
            padding-left: 8px;
        }
        .tip-item:last-child {
            border-bottom: none;
        }
        
        /* ===== 页脚 - 医疗资质展示 ===== */
        .footer-section {
            margin-top: 3rem;
            padding: 2.5rem 0 1.5rem 0;
            background: linear-gradient(145deg, #1A237E, #0D47A1);
            width: 100%;
            position: relative;
            overflow: hidden;
            border-top-left-radius: 40px;
            border-top-right-radius: 40px;
            z-index: 1;
        }
        .footer-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(45deg, transparent, transparent 20px, rgba(255,255,255,0.02) 20px, rgba(255,255,255,0.02) 40px);
            pointer-events: none;
        }
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            z-index: 2;
        }
        .footer-grid {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1.5fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        .footer-col {
            color: white;
        }
        .footer-logo {
            font-size: 1.8rem;
            font-weight: 800;
            margin-bottom: 1rem;
            color: white !important;
        }
        .footer-desc {
            color: rgba(255,255,255,0.8);
            line-height: 1.5;
            margin-bottom: 1.2rem;
            font-size: 0.9rem;
        }
        .footer-social {
            display: flex;
            gap: 0.8rem;
        }
        .social-icon {
            width: 36px;
            height: 36px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            border: 1px solid rgba(255,255,255,0.2);
            color: white;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .social-icon:hover {
            background: var(--medical-green);
            transform: translateY(-4px);
            border-color: white;
        }
        .footer-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: white !important;
            margin-bottom: 1.2rem;
            position: relative;
            padding-bottom: 0.4rem;
        }
        .footer-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 25px;
            height: 2px;
            background: var(--medical-green);
            border-radius: 2px;
        }
        .footer-links {
            list-style: none;
            padding: 0;
        }
        .footer-links li {
            margin-bottom: 0.6rem;
        }
        .footer-links a {
            color: rgba(255,255,255,0.8) !important;
            text-decoration: none;
            transition: all 0.3s ease;
            display: inline-block;
            font-size: 0.9rem;
        }
        .footer-links a:hover {
            color: white !important;
            transform: translateX(6px);
        }
        .footer-contact {
            color: rgba(255,255,255,0.8) !important;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-size: 0.9rem;
        }
        .certification-badges {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin: 1.5rem 0;
            justify-content: center;
        }
        .cert-badge {
            background: rgba(255,255,255,0.12);
            border-radius: 40px;
            padding: 0.3rem 1rem;
            border: 1px solid rgba(255,255,255,0.2);
            font-size: 0.8rem;
            color: white !important;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        .cert-badge:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
            border-color: var(--medical-green);
        }
        .footer-bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: rgba(255,255,255,0.7) !important;
            font-size: 0.85rem;
            flex-wrap: wrap;
            gap: 1rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 0.5rem;
        }
        .copyright {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: rgba(255,255,255,0.7) !important;
        }
        .legal-links {
            display: flex;
            gap: 1.5rem;
        }
        .legal-links a {
            color: rgba(255,255,255,0.7) !important;
            text-decoration: none;
            transition: color 0.3s ease;
            font-size: 0.85rem;
        }
        .legal-links a:hover {
            color: white !important;
        }
        .disclaimer-badge {
            background: rgba(229, 57, 53, 0.2);
            border-radius: 40px;
            padding: 0.4rem 1.2rem;
            border: 1px solid var(--medical-red);
            font-size: 0.8rem;
            color: white !important;
            display: inline-block;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        .disclaimer-badge:hover {
            background: rgba(229, 57, 53, 0.3);
            transform: translateY(-2px);
        }
        
        /* 响应式设计 */
        @media (max-width: 1200px) {
            .disease-grid { grid-template-columns: repeat(3, 1fr); padding: 0 1rem; }
            .footer-grid { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 900px) {
            .disease-grid { grid-template-columns: repeat(2,1fr); }
            .feature-grid { grid-template-columns: 1fr; padding: 0 1rem; }
            .advantage-grid { grid-template-columns: 1fr; padding: 0 1rem; }
            .platform-sub { font-size: 1rem; }
            .platform-container { padding: 0.8rem 1.5rem; margin: 0.5rem 1rem; }
            .main-title { font-size: 3.5rem; padding: 0 100px; }
        }
        @media (max-width: 768px) {
            .main-title { font-size: 2.8rem; padding: 0 90px; }
            .main-title::before { font-size: 2.5rem; left: -10px; }
            .main-title::after { font-size: 2.2rem; right: -10px; }
            .platform-sub { font-size: 0.95rem; flex-direction: column; gap: 0.2rem; }
            .stButton > button { font-size: 2rem !important; padding: 1rem 5rem !important; min-width: 420px !important; }
            .section-title { font-size: 1.6rem; padding: 0 1rem; }
            .footer-bottom { flex-direction: column; text-align: center; }
            .legal-links { justify-content: center; flex-wrap: wrap; gap: 1rem; }
            .footer-grid { grid-template-columns: 1fr; text-align: center; }
            .footer-title::after { left: 50%; transform: translateX(-50%); }
            .certification-badges { justify-content: center; }
        }
        @media (max-width: 550px) {
            .main-title { font-size: 2.2rem; padding: 0 70px; }
            .main-title::before { font-size: 2rem; left: -5px; }
            .main-title::after { font-size: 1.8rem; right: -5px; }
        }
        
        /* 强制主容器居中 */
        .block-container {
            max-width: 1400px !important;
            padding: 0 1.5rem !important;
            margin: 0 auto !important;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .block-container > * {
            width: 100%;
            max-width: 1200px;
            margin-left: auto !important;
            margin-right: auto !important;
        }
    </style>
    
    <!-- JavaScript 交互增强 -->
    <script>
        // 等待 DOM 加载完成
        document.addEventListener('DOMContentLoaded', function() {
            // 1. 按钮磁吸效果
            const btnArea = document.querySelector('.btn-magnetic-area');
            const btn = document.querySelector('.stButton > button');
            
            if (btnArea && btn) {
                btnArea.addEventListener('mousemove', function(e) {
                    const rect = btnArea.getBoundingClientRect();
                    const x = e.clientX - rect.left - rect.width / 2;
                    const y = e.clientY - rect.top - rect.height / 2;
                    
                    // 限制移动范围
                    const moveX = x * 0.15;
                    const moveY = y * 0.15;
                    
                    btn.style.transform = `translate(${moveX}px, ${moveY}px)`;
                });
                
                btnArea.addEventListener('mouseleave', function() {
                    btn.style.transform = 'translate(0, 0)';
                });
            }
            
            // 2. 平台容器 3D 倾斜效果
            const platform = document.querySelector('.platform-container');
            if (platform) {
                platform.addEventListener('mousemove', (e) => {
                    const rect = platform.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    const centerX = rect.width / 2;
                    const centerY = rect.height / 2;
                    
                    const rotateX = ((y - centerY) / centerY) * -5;
                    const rotateY = ((x - centerX) / centerX) * 5;
                    
                    platform.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
                });
                
                platform.addEventListener('mouseleave', () => {
                    platform.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
                });
            }
        });
    </script>
    """, unsafe_allow_html=True)
    
    # 主标题区域
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    # 背景网格
    st.markdown('<div class="hero-bg-grid"></div>', unsafe_allow_html=True)
    
    # 主标题
    st.markdown('<h1 class="main-title">CardioGuard AI</h1>', unsafe_allow_html=True)
    
    # 心电图装饰线
    st.markdown("""
    <div class="ecg-line">
        <svg viewBox="0 0 200 40">
            <path class="ecg-path" d="M10,20 L30,20 L40,10 L50,30 L60,15 L70,25 L80,20 L100,20 L110,15 L120,25 L130,20 L150,20 L160,10 L170,30 L180,20 L190,20" />
        </svg>
    </div>
    """, unsafe_allow_html=True)
    
    # 平台定位
    st.markdown("""
    <div class="platform-container" id="platform-container">
        <div class="floating-icon fi-1">🫀</div>
        <div class="floating-icon fi-2">🩺</div>
        <div class="floating-icon fi-3">💊</div>
        <div class="floating-icon fi-4">⚡</div>
        <div class="platform-container-inner">
            <div class="platform-sub">
                <span class="platform-sub-icon">🔬</span> 基于深度学习的智能心血管疾病诊断平台 守护您的心脏健康
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 了解心血管疾病（视频）
    st.markdown('<h2 class="section-title">📺 了解心血管疾病</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="video-container">
        <div class="video-wrapper">
            <iframe 
                src="//player.bilibili.com/player.html?bvid=BV1xZ4y1Z7Xw&page=1&high_quality=1&danmaku=0" 
                scrolling="no" 
                border="0" 
                frameborder="no" 
                framespacing="0" 
                allowfullscreen="true">
            </iframe>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 开始诊断按钮
    st.markdown('<div class="start-button-wrapper">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="btn-magnetic-area">', unsafe_allow_html=True)
        if st.button("立即开始 AI 诊断", use_container_width=True):
            st.switch_page("pages/p00_auth.py")
        st.markdown('<div class="btn-tooltip">已有 10,000+ 用户使用</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 专业分隔线
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # 为什么选择 CardioGuard AI
    st.markdown('<h2 class="section-title">🎯 为什么选择 CardioGuard AI？</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="advantage-grid">
        <div class="advantage-card">
            <div class="advantage-icon">🎓</div>
            <div class="advantage-content">
                <div class="advantage-title">专业医学背景</div>
                <div class="advantage-desc">基于<span class="stat-highlight">数十万份</span>真实心电图数据训练，融合心脏病学专家的临床经验</div>
                <span class="data-label">三甲医院合作</span>
            </div>
        </div>
        <div class="advantage-card">
            <div class="advantage-icon">⚡</div>
            <div class="advantage-content">
                <div class="advantage-title">快速精准诊断</div>
                <div class="advantage-desc">采用先进深度学习算法，仅需<span class="stat-highlight">3秒</span>完成分析，准确率高达<span class="stat-highlight">95%</span></div>
                <span class="data-label">实时分析</span>
            </div>
        </div>
        <div class="advantage-card">
            <div class="advantage-icon">📱</div>
            <div class="advantage-content">
                <div class="advantage-title">便捷易用</div>
                <div class="advantage-desc">无需复杂操作，上传心电图数据即可自动分析并生成详细报告</div>
                <span class="data-label">一键上传</span>
            </div>
        </div>
        <div class="advantage-card">
            <div class="advantage-icon">🔒</div>
            <div class="advantage-content">
                <div class="advantage-title">隐私安全保障</div>
                <div class="advantage-desc">银行级加密技术，严格遵守医疗数据保护规范，信息绝对安全</div>
                <span class="data-label">ISO 认证</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 可诊断疾病类型
    st.markdown('<h2 class="section-title">🏥 可诊断疾病类型</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="disease-grid">
        <div class="disease-card">
            <span class="accuracy-badge">96%</span>
            <div class="disease-icon">🫀</div>
            <div class="disease-name">缺血性心脏病</div>
            <div class="disease-desc">冠状动脉供血不足</div>
        </div>
        <div class="disease-card">
            <span class="accuracy-badge">94%</span>
            <div class="disease-icon">💉</div>
            <div class="disease-name">高血压心脏病</div>
            <div class="disease-desc">长期高血压导致</div>
        </div>
        <div class="disease-card">
            <span class="accuracy-badge">95%</span>
            <div class="disease-icon">⚡</div>
            <div class="disease-name">心律失常</div>
            <div class="disease-desc">心脏电活动异常</div>
        </div>
        <div class="disease-card">
            <span class="accuracy-badge">93%</span>
            <div class="disease-icon">💔</div>
            <div class="disease-name">心力衰竭</div>
            <div class="disease-desc">泵血功能减退</div>
        </div>
        <div class="disease-card">
            <span class="accuracy-badge">92%</span>
            <div class="disease-icon">🩸</div>
            <div class="disease-name">心肌病</div>
            <div class="disease-desc">心肌结构异常</div>
        </div>
        <div class="disease-card">
            <span class="accuracy-badge">91%</span>
            <div class="disease-icon">🚪</div>
            <div class="disease-name">瓣膜性心脏病</div>
            <div class="disease-desc">瓣膜结构异常</div>
        </div>
        <div class="disease-card">
            <span class="accuracy-badge">90%</span>
            <div class="disease-icon">👶</div>
            <div class="disease-name">先天性心脏病</div>
            <div class="disease-desc">出生即存在异常</div>
        </div>
        <div class="disease-card">
            <span class="accuracy-badge">92%</span>
            <div class="disease-icon">🌊</div>
            <div class="disease-name">主动脉疾病</div>
            <div class="disease-desc">主动脉结构异常</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心功能
    st.markdown('<h2 class="section-title">✨ 核心功能</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI 智能诊断</div>
            <div class="feature-desc">识别<span class="stat-highlight">8 大类</span>心血管疾病，准确率<span class="stat-highlight">95%</span></div>
            <span class="data-label">人工智能</span>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">数据可视化</div>
            <div class="feature-desc">直观展示<span class="stat-highlight">12 项</span>心电图指标</div>
            <span class="data-label">可视化分析</span>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <div class="feature-title">专业建议</div>
            <div class="feature-desc">提供<span class="stat-highlight">5 项</span>个性化预防措施</div>
            <span class="data-label">智能建议</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 心血管健康小贴士
    st.markdown('<h2 class="section-title">💊 心血管健康小贴士</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="tips-section">
        <div class="tips-scroll">
            <div class="tip-card">
                <span class="tip-icon">🫀</span>
                <div class="tip-title">缺血性心脏病预防</div>
                <div class="tip-item">✓ 定期检查血脂</div>
                <div class="tip-item">✓ 低脂饮食，控制体重</div>
                <div class="tip-item">✓ 适度有氧运动</div>
            </div>
            <div class="tip-card">
                <span class="tip-icon">💉</span>
                <div class="tip-title">高血压管理</div>
                <div class="tip-item">✓ 每日监测血压</div>
                <div class="tip-item">✓ 减少盐分摄入</div>
                <div class="tip-item">✓ 规律运动，减压</div>
            </div>
            <div class="tip-card">
                <span class="tip-icon">⚡</span>
                <div class="tip-title">心律失常预防</div>
                <div class="tip-item">✓ 避免过度咖啡因</div>
                <div class="tip-item">✓ 保持电解质平衡</div>
                <div class="tip-item">✓ 规律作息，减压</div>
            </div>
            <div class="tip-card">
                <span class="tip-icon">💔</span>
                <div class="tip-title">心力衰竭护理</div>
                <div class="tip-item">✓ 限制液体摄入</div>
                <div class="tip-item">✓ 低盐饮食控制</div>
                <div class="tip-item">✓ 监测体重变化</div>
            </div>
            <!-- 复制用于无缝轮播 -->
            <div class="tip-card">
                <span class="tip-icon">🫀</span>
                <div class="tip-title">缺血性心脏病预防</div>
                <div class="tip-item">✓ 定期检查血脂</div>
                <div class="tip-item">✓ 低脂饮食，控制体重</div>
                <div class="tip-item">✓ 适度有氧运动</div>
            </div>
            <div class="tip-card">
                <span class="tip-icon">💉</span>
                <div class="tip-title">高血压管理</div>
                <div class="tip-item">✓ 每日监测血压</div>
                <div class="tip-item">✓ 减少盐分摄入</div>
                <div class="tip-item">✓ 规律运动，减压</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 页脚
    st.markdown("""
    <div class="footer-section">
        <div class="footer-content">
            <div class="footer-grid">
                <div class="footer-col">
                    <div class="footer-logo">CardioGuard AI</div>
                    <div class="footer-desc">让每一次心跳都被守护<br>用 AI 技术预见健康未来</div>
                    <div class="footer-social">
                        <div class="social-icon">📱</div>
                        <div class="social-icon">💬</div>
                        <div class="social-icon">📧</div>
                    </div>
                </div>
                <div class="footer-col">
                    <div class="footer-title">产品服务</div>
                    <ul class="footer-links">
                        <li><a href="#">AI 智能诊断</a></li>
                        <li><a href="#">健康档案</a></li>
                        <li><a href="#">数据分析</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <div class="footer-title">关于我们</div>
                    <ul class="footer-links">
                        <li><a href="#">团队介绍</a></li>
                        <li><a href="#">技术优势</a></li>
                        <li><a href="#">合作机构</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <div class="footer-title">联系方式</div>
                    <div class="footer-contact">📞 JIayi07</div>
                    <div class="footer-contact">✉️ 877942636@qq.com</div>
                    <div class="footer-contact">📍 https://github.com/JiayiLiu07</div>
                </div>
            </div>
            <div class="certification-badges">
                <div class="cert-badge">🏥 三甲医院临床认证</div>
                <div class="cert-badge">🔬 医疗器械注册证：2024 第 001 号</div>
                <div class="cert-badge">⭐ ISO 13485 认证</div>
                <div class="cert-badge">🏆 国家高新技术企业</div>
            </div>
            <div class="footer-bottom">
                <div class="copyright">
                    © 2024 CardioGuard AI - 心脏健康守护者 | 专业医疗级 AI 分析平台
                </div>
                <div class="legal-links">
                    <a href="#">隐私政策</a>
                    <a href="#">免责声明</a>
                    <a href="#">医疗资质</a>
                </div>
                <div class="disclaimer-badge">
                    ⚕️ 本产品仅供健康监测参考，不能替代专业医疗诊断。❤️
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()