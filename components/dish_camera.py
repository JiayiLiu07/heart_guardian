import streamlit as st
import time

def render():
    st.subheader("拍照识菜")
    st.markdown("将摄像头对准您想识别的菜品，点击拍照。")

    if st.button("拍照", key="take_picture_button", use_container_width=True):
        st.info("正在拍照并识别菜品...")
        with st.spinner("正在识别..."):
            time.sleep(2)
        st.success("识别完成！")
        st.markdown("""
        <div style='margin-top: 20px; padding: 15px; background-color: #e8f5e9; border-left: 5px solid #4CAF50; border-radius: 8px;'>
            <strong>识别结果示例:</strong>
            <ul>
                <li><strong>番茄炒蛋</strong>: <span style='color: #4CAF50;'>适量食用</span> - 富含维生素C，需控制烹饪油量。</li>
                <li><strong>红烧肉</strong>: <span style='color: #F44336;'>少量或避免</span> - 高脂肪、高胆固醇，不利于心血管健康。</li>
                <li><strong>蒸蛋</strong>: <span style='color: #4CAF50;'>适量食用</span> - 优质蛋白质来源，易消化。</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top: 30px; font-size: 13px; color: #777;'>
        <strong>温馨提示：</strong> 拍照识别功能尚在完善中，结果仅供参考。请结合实际情况和营养师建议进行饮食调整。
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()