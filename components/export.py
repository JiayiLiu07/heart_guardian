import streamlit as st
import pandas as pd
import io

def render(data_to_export=None, default_filename="export_data"):
    st.subheader("导出数据")

    export_format = st.selectbox("选择导出格式", ["CSV", "Excel", "JSON"], key="export_format_select")

    if data_to_export is None:
        st.warning("没有数据可供导出。")
        return

    df_to_export = None
    if isinstance(data_to_export, pd.DataFrame):
        df_to_export = data_to_export
    elif isinstance(data_to_export, dict):
        try:
            df_to_export = pd.DataFrame.from_dict(data_to_export)
            st.info("字典数据已转换为 DataFrame 进行导出。")
        except Exception as e:
            st.error(f"无法将字典转换为 DataFrame: {e}")
            return
    else:
        st.error("不支持的导出数据类型。")
        return

    if export_format == "CSV":
        csv = df_to_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="下载 CSV 文件",
            data=csv,
            file_name=f"{default_filename}.csv",
            mime='text/csv',
            key="download_csv_button"
        )
    elif export_format == "Excel":
        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_to_export.to_excel(writer, index=False, sheet_name='Sheet1')
            excel_data = buffer.getvalue()
            st.download_button(
                label="下载 Excel 文件",
                data=excel_data,
                file_name=f"{default_filename}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key="download_excel_button"
            )
        except ImportError:
            st.error("请安装 'openpyxl' 库: pip install openpyxl")
        except Exception as e:
            st.error(f"导出 Excel 时发生错误: {e}")
    elif export_format == "JSON":
        json_data = df_to_export.to_json(orient='records', indent=4).encode('utf-8')
        st.download_button(
            label="下载 JSON 文件",
            data=json_data,
            file_name=f"{default_filename}.json",
            mime='application/json',
            key="download_json_button"
        )

if __name__ == "__main__":
    render()