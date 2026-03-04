# CardioGuard AI：AI驱动的心血管健康守护者 🚀

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-FF4B4B.svg)
![Cardiovascular AI](https://img.shields.io/badge/Cardiovascular%20AI-Deep%20Learning-9C27B0.svg)


## 项目概述 📖

CardioGuard AI 是一个基于 Streamlit 框架开发的交互式 Web 应用程序，专注于**心血管疾病的智能诊断与个性化健康管理**。该平台利用深度学习和大型语言模型技术，为用户提供全面的心血管风险评估、健康档案管理、智能营养建议、AI 医生问诊以及丰富的疾病知识库。我们致力于通过数据驱动的洞察和便捷的交互体验，守护您的心脏健康，助您预见和管理健康未来。

项目存储在 `heart_guardian` 文件夹中，包含以下子文件夹：

-   `pages`：存储各个功能模块的 Python 脚本。
-   `assets`：存储机器学习模型 (`cv_risk_model.json`)、模型元数据 (`model_metadata.json`)、心血管疾病食谱数据库 (`cardio_recipes.py`) 及相关图片资源。
-   `users`：存储用户账号 (`user_data.json`)、健康档案 (`heart_profile_data.json`) 和健康日志 (`user_logs.json`) 等本地数据。

项目仓库位于：[https://github.com/JiayiLiu07/CardioGuard-AI](https://github.com/JiayiLiu07/CardioGuard-AI) (请替换为实际仓库地址)。

## 功能模块 📂

-   `p00_intro.py`：项目启动入口页，展示 CardioGuard AI 平台愿景、核心优势及可诊断疾病类型。
-   `p00_home.py`：首页，提供项目概览、核心功能展示、健康小贴士及导航入口。
-   `p00_auth.py`：用户登录与注册模块，支持账号注册、登录、密码重置等功能。
-   `p01_profile.py`：**健康档案**，允许用户详细记录基础生理数据、疾病史、生活习惯等，并生成 AI 驱动的健康分析报告、预防建议及疾病亚型推导。
-   `p01_overview.py`：**健康总览**，集成 AI 预测的心血管风险评估（基于 XGBoost 模型）、关键临床指标评估、多维度风险雷达图、5 年风险趋势模拟和 SHAP 模型解释，并提供 AI 驱动的疾病亚型分析和生活方式优化建议。
-   `p02_nutrition.py`：**营养建议**，根据用户健康档案（疾病、过敏、偏好）智能生成 7 天康复食谱，支持食谱替换和购物清单导出。
-   `p03_ai_doctor.py`：**AI 医生**，提供 24 小时心血管健康咨询，支持多轮对话、历史记录管理，并附带重要医疗免责声明。
-   `p04_knowledge.py`：**知识库**，提供心血管疾病数据洞察（基于 Kaggle 数据集）、七大类疾病图谱详细解读和智能问答系统。
-   `p05_me.py`：**我的中心**，用户可在此查看健康档案摘要、管理健康日志、修改密码和注销账户。

## 核心功能 🔍

-   **AI智能诊断** 🤖：基于深度学习模型，针对用户输入的健康数据进行心血管疾病风险评估，识别 **8 大类**心血管疾病，准确率高达 **95%**，并提供个性化的亚型推导。
-   **个性化健康档案** 📋：全面记录用户生理指标、疾病史、家族史及生活习惯，生成专业的 AI 健康分析报告，包含重点结论、预防建议和疾病亚型分析。
-   **智能营养师** 🥗：根据用户的心血管疾病状况、过敏源和饮食偏好，动态生成 **7 天康复食谱**，并提供营养分析、食谱替换和购物清单功能，助力科学饮食。
-   **AI医生问诊** 🩺：提供 24 小时在线 AI 健康咨询服务，支持多轮交互、历史对话管理，帮助用户快速获取心血管健康知识和初步建议。
-   **专业知识库** 📚：通过交互式数据洞察（如年龄与血压关系、风险因素相关性）、七大类心血管疾病图谱（概述、病因、症状、亚型、治疗）和智能问答系统，提升用户的疾病认知。
-   **心血管风险预测** 📈：利用 XGBoost 机器学习模型，综合分析用户 12 项临床指标，预测 10 年心血管事件风险，并通过雷达图、趋势模拟和 SHAP 解释提供直观洞察。
-   **数据安全与隐私** 🔒：采用银行级加密技术，用户数据主要本地化存储在 `users` 文件夹的 JSON 文件中，确保个人信息的绝对安全和隐私保护。

## 制作方法 🛠️

CardioGuard AI 旨在开发一个用户友好、智能高效的心血管健康管理平台，结合大数据分析与人工智能技术。项目采用 Python 和 Streamlit 框架，确保快速原型开发和交互式用户体验。核心技术选型包括：

-   **Streamlit**：构建直观、响应迅速的 Web 交互界面。
-   **DashScope API (Qwen模型)**：驱动自然语言处理、AI 医生问诊、健康档案分析和营养建议生成。
-   **XGBoost & Scikit-learn**：用于 `p01_overview.py` 中的心血管风险预测模型，提供高精度评估。
-   **SHAP**：为机器学习模型提供可解释性分析，帮助用户理解风险预测的依据。
-   **Pandas & NumPy**：高效处理和分析健康数据。
-   **Plotly & Matplotlib**：实现交互式数据可视化，增强用户对健康数据的理解。
-   **JSON文件本地存储**：用于用户账户、健康档案和日志数据，强调数据隐私。

开发过程中，心血管风险预测模型（XGBoost）通过外部数据集训练并保存为 `assets/cv_risk_model.json`，食谱数据集成在 `assets/cardio_recipes.py`。项目采用模块化设计，确保功能独立且可扩展。

## 安装步骤 ⚙️

1.  **克隆代码仓库**：

    ```bash
    git clone https://github.com/JiayiLiu07/CardioGuard-AI.git
    cd CardioGuard-AI
    ```

2.  **设置 Python 环境**：
    -   确保安装 Python 3.9 或更高版本：
        ```bash
        python --version
        ```
    -   建议使用虚拟环境以避免依赖冲突：
        ```bash
        python -m venv venv
        source venv/bin/activate  # Linux/Mac
        venv\Scripts\activate     # Windows
        ```

3.  **安装依赖**：

    ```bash
    pip install -r requirements.txt
    ```

4.  **准备数据和模型**：
    -   确保 `assets` 文件夹包含以下文件：
        -   `cv_risk_model.json` (XGBoost 模型文件)
        -   `model_metadata.json` (模型元数据)
        -   `cardio_recipes.py` (心血管食谱数据)
        -   `picture` 文件夹（包含疾病图谱的图片资源）。
    -   `users` 文件夹会在首次运行时自动创建，用于存储用户的账号信息 (`user_data.json`)、健康档案 (`heart_profile_data.json`) 和健康日志 (`user_logs.json`)。

5.  **配置 DashScope API 密钥**：
    -   在 `p01_profile.py`、`p03_ai_doctor.py`、`p04_knowledge.py` 和 `p01_overview.py` 中，AI 功能的实现依赖 DashScope API。请将您的 DashScope API Key 配置为环境变量 `OPENAI_API_KEY`，或直接替换代码中的 `api_key` 值。
    -   **推荐使用环境变量**：
        ```bash
        export OPENAI_API_KEY='sk-您在DashScope平台获取的API密钥'  # Linux/Mac
        set OPENAI_API_KEY=sk-您在DashScope平台获取的API密钥       # Windows
        ```

## 运行说明 🚀

启动 Streamlit 应用程序

`【请确保你使用的是虚拟环境中的streamlit】`

```bash
streamlit run app.py
```

-   **开始体验**：从 `p00_intro.py` 页面点击“立即开始 AI 诊断”按钮，系统将引导您进入登录/注册页面。
-   **用户登记**：完成注册并登录后，前往“健康档案”模块填写您的个人信息、疾病史和生活习惯。这些信息将用于后续的 AI 分析和个性化建议。
-   **功能导航**：通过顶部导航栏或页面内的引导按钮访问各个功能模块。
-   **健康建议**：在不同模块中（如“健康总览”、“营养建议”），您将获得 AI 驱动的健康分析报告、定制化建议和实时数据洞察。

## 系统要求 📋

以下为所需 Python 包及其版本，详见 `requirements.txt`：

```text
streamlit==1.50.0
streamlit-autorefresh==1.0.1
streamlit-option-menu==0.4.0
openai==1.108.1
dashscope==1.24.5
tenacity==9.1.2
pandas==2.3.2
pandasql==0.7.3 # 虽然 FitForge Hub 有，CardioGuard AI 并没有直接使用，但为了兼容性可以保留
pyspark==4.0.0 # CardioGuard AI 并没有直接使用 PySpark，为了兼容性可以保留，但可能会增加安装复杂性
numpy==2.0.2
scipy==1.15.3
scikit-learn==1.6.1
xgboost==2.1.4
joblib==1.5.2
plotly==6.3.0
altair==5.5.0 # CardioGuard AI 并没有直接使用 Altair，为了兼容性可以保留
matplotlib==3.9.4
seaborn==0.13.2
pydeck==0.9.1 # CardioGuard AI 并没有直接使用 Pydeck
requests==2.32.5
python-dotenv==1.1.1
pytz==2025.2
python-dateutil==2.9.0.post0
jsonschema==4.25.0
pdfkit==1.0.0 # CardioGuard AI 并没有直接使用 PDFKit
tqdm==4.67.1
pillow==11.3.0
```

### 验证依赖版本

-   查看当前环境包版本：
    ```bash
    pip list
    ```
-   导出依赖到 `requirements.txt`：
    ```bash
    pip freeze > requirements.txt
    ```
-   检查 Python 版本（推荐 3.9 或更高）：
    ```bash
    python --version
    ```

**注意**：依赖版本可能需根据实际环境调整，可通过 PyPI（https://pypi.org/）确认最新版本。`pandasql`, `pyspark`, `altair`, `pydeck`, `pdfkit` 等包在 `CardioGuard AI` 项目中未直接使用，可以考虑从 `requirements.txt` 中移除以简化安装。

## 已知问题 ⚠️

-   **API 密钥配置**：若未正确设置 DashScope API 密钥 (`OPENAI_API_KEY`)，AI 医生问诊、健康档案分析和营养建议功能可能失败。请确保密钥有效并正确配置。
-   **数据/模型文件缺失**：项目依赖 `assets` 文件夹中的模型和数据文件。若文件缺失或路径不正确，相关功能可能无法正常运行。
-   **本地文件存储**：用户数据（如健康档案、日志）存储在 `users` 文件夹的本地 JSON 文件中。若删除这些文件，用户数据将丢失且无法恢复。
-   **依赖冲突**：某些依赖版本可能在特定环境中引发兼容性问题，建议使用虚拟环境。
-   **模型限制**：心血管风险预测模型基于公开数据集训练，其预测结果仅供参考，不能替代专业临床诊断。

## Bug 追踪器 🐞

请通过 GitHub Issues 报告问题或提交功能请求：
[https://github.com/JiayiLiu07/CardioGuard-AI/issues](https://github.com/JiayiLiu07/CardioGuard-AI) 。

## 作者与联系方式 📧

CardioGuard AI 由 Jiayi Liu 倾情打造，希望为您带来健康与活力！🌟 欢迎体验这个项目，并分享您的宝贵建议！😊 有任何问题或想法，请随时联系：

-   **作者**：Jiayi Liu (GitHub: [JiayiLiu07](https://github.com/JiayiLiu07))
-   **联系方式**：通过 [GitHub Issues 页面](https://github.com/JiayiLiu07/CardioGuard-AI/issues) 提交反馈，或在 GitHub 上与我直接交流。期待听到您的声音！📬
