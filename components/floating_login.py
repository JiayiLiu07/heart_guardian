import streamlit as st
import streamlit.components.v1 as components

def render():
    html = """
    <div style="position:fixed;top:20px;right:20px;z-index:9999;">
      <a href="/00_auth" target="_self"
         style="display:inline-block;background:#E94560;color:#fff;
                padding:10px 24px;border-radius:30px;font-size:14px;
                box-shadow:0 4px 12px rgba(0,0,0,.15);text-decoration:none;
                transition: all 0.3s ease;">
         登录 / 注册
      </a>
    </style>
    <script>
        const loginLink = document.querySelector('a[href="/00_auth"]');
        if (loginLink) {
            loginLink.classList.add('floating-login-button');
        }
    </script>
    """
    components.html(html, height=0)

if __name__ == "__main__":
    render()