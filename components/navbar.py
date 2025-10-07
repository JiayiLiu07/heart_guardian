import streamlit as st
import streamlit.components.v1 as components

def render():
    html = """
    <nav style="position: fixed; top: 0; width: 100%; background: white; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 1000;">
        <a href="/p00_intro" style="margin-right: 20px;">首页</a>
        <a href="/01_profile" style="margin-right: 20px;">档案</a>
        <a href="/02_nutrition" style="margin-right: 20px;">营养</a>
        <a href="/03_ai_doctor" style="margin-right: 20px;">AI医生</a>
        <a href="/04_knowledge" style="margin-right: 20px;">知识库</a>
        <a href="/05_me" style="margin-right: 20px;">个人中心</a>
    </nav>
    """
    components.html(html, height=60)

if __name__ == "__main__":
    render()