# components/loader.py
import streamlit as st

def render_loader(text="正在分析..."):
    st.markdown(f"<div style='text-align:center; color:#E94560;'>{text}</div>", unsafe_allow_html=True)
    st.markdown("""
    <svg style='display:block;margin:0 auto;width:50px;height:50px;'>
        <circle cx='25' cy='25' r='20' stroke='#E94560' stroke-width='5' fill='none'>
            <animate attributeName='stroke-dasharray' from='0 100' to='100 0' dur='1.5s' repeatCount='indefinite'/>
        </circle>
    </svg>
    """, unsafe_allow_html=True)