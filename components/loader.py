import streamlit as st
import time

def render(message="🩺 正在分析…", duration=1.2):
    html = f"""
    <div class="pulse-loader-container">
        <div class="pulse-bar"></div>
        <div class="loader-message">{message}</div>
    </div>
    <style>
        .pulse-loader-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 20px 0;
        }}
        .pulse-bar {{
            width: 60px;
            height: 5px;
            background-color: #E94560;
            border-radius: 3px;
            animation: pulse {duration}s infinite ease-in-out;
            transform-origin: center;
        }}
        .loader-message {{
            margin-top: 10px;
            font-size: 14px;
            color: #1F2937;
            font-weight: 500;
        }}
        @keyframes pulse {{
            0% {{
                transform: scaleX(0.8);
                opacity: 0.8;
            }}
            50% {{
                transform: scaleX(1.2);
                opacity: 1;
            }}
            100% {{
                transform: scaleX(0.8);
                opacity: 0.8;
            }}
        }}
    </style>
    """
    st.markdown(html, unsafe_allow_html=True)

if __name__ == "__main__":
    render()