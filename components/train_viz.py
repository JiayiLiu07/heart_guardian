import streamlit as st

def render():
    st.markdown("<h3 style='font-size: 20px; font-weight: 500; margin-bottom: 20px; color: #1F2937;'>大数据告诉你：心血管危险因子长什么样</h3>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["特征重要性", "相关性", "单因子 PDP", "交互 PDP"])

    with tab1:
        st.image('assets/global_shap.png', use_column_width=True, caption="全球特征重要性 (SHAP)")
        st.markdown("""
        <p style="font-size: 14px; color: #333; line-height: 1.6;">
        行业大数据显示：收缩压（ap_hi）、年龄（age_years）、BMI 是影响心血管风险的前三杀手 ℹ️
        </p>
        """, unsafe_allow_html=True)

    with tab2:
        st.image('assets/corr_heatmap.png', use_column_width=True, caption="特征相关性热力图")
        st.markdown("""
        <p style="font-size: 14px; color: #333; line-height: 1.6;">
        图中红色表示正相关，绿色表示负相关。例如，收缩压 (ap_hi) 与心血管疾病 (cardio) 呈正相关 ℹ️
        </p>
        """, unsafe_allow_html=True)

    with tab3:
        st.image('assets/partial_dependence.png', use_column_width=True, caption="单因子部分依赖图 (PDP)")
        st.markdown("""
        <p style="font-size: 14px; color: #333; line-height: 1.6;">
        当收缩压 (ap_hi) 每升高 20 mmHg，心血管风险概率平均上升约 3.2% ℹ️
        </p>
        """, unsafe_allow_html=True)

    with tab4:
        st.image('assets/interact_pdp.png', use_column_width=True, caption="交互部分依赖图 (SBP × Age)")
        st.markdown("""
        <p style="font-size: 14px; color: #333; line-height: 1.6;">
        数据显示：50 岁以上且收缩压超过 140 mmHg 的人群，心血管疾病风险显著陡增 ℹ️
        </p>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()