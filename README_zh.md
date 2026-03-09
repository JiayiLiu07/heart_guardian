# CardioGuard AI - 智能心血管健康管理平台 💖

## 简介 📝

CardioGuard AI 是一个基于 Streamlit 构建的智能心血管健康管理应用，旨在通过整合个人健康数据、AI 辅助分析、营养建议、智能问答和专业知识库，为用户提供全面的心血管健康洞察与个性化管理方案。本平台利用先进的机器学习模型预测心血管疾病风险，并通过大型语言模型（DashScope 通义千问）提供专业医学咨询和生活方式建议。

## 核心功能 ✨

1.  **健康档案 (Health Profile) 📋**
    *   记录和管理用户的基本生理指标（年龄、性别、身高、体重、血压、血脂、血糖）。
    *   详细的心血管疾病史（大类与亚型选择）。
    *   生活习惯与风险因素评估（吸烟、饮酒、熬夜、运动、饮食偏好、过敏等）。
    *   数据本地存储，确保隐私安全。

2.  **健康总览 (Health Overview) 📊**
    *   基于用户健康档案，通过 XGBoost 机器学习模型预测 10 年心血管疾病风险。
    *   提供多维度的个人风险雷达图和关键指标趋势模拟。
    *   利用 SHAP 值解释模型预测结果，揭示各项因素对个人风险的贡献。
    *   AI 智能推导未指定疾病亚型，并深入分析已选亚型。
    *   AI 生成个性化的生活方式优化建议（运动、饮食、作息、心理、危险信号）。

3.  **AI 营养师 (AI Nutritionist) 🥗**
    *   根据用户健康档案（疾病、过敏、饮食偏好），智能生成定制化的 7 日心血管康复食谱。
    *   提供详细食谱信息，包括菜品名称、食材、烹饪步骤和营养成分。
    *   支持食谱“换一道”功能，灵活调整。
    *   自动生成本周购物清单，并按食材类别进行分类。
    *   提供实用的饮食健康小贴士。

4.  **AI 医生 (AI Doctor) 🩺**
    *   24/7 智能问答，用户可随时咨询心血管相关健康问题。
    *   支持多轮对话，提供专业的医学解答和建议。
    *   保存历史对话记录，方便回顾和管理。

5.  **知识库 (Knowledge Base) 📚**
    *   提供心血管疾病数据洞察，通过交互式图表展示年龄、血压、风险因素等关系。
    *   详细的七大类心血管疾病图谱，包括病因、症状、亚型、治疗与预防。
    *   内置智能问答模块，解答用户关于疾病的专业疑问。

6.  **我的中心 (My Center) 👤**
    *   查看和编辑个人健康档案摘要。
    *   记录和管理个人健康日志。
    *   支持重置密码和注销账户功能。
    *   强调数据安全与隐私保护。

## 技术栈 💻

*   **前端框架**: Streamlit
*   **AI/ML**:
    *   大型语言模型 (LLM): DashScope (通义千问 `qwen-turbo`, `qwen-max`)
    *   机器学习: XGBoost, SHAP (用于风险预测和模型解释)
*   **数据处理**: Pandas, NumPy
*   **数据可视化**: Plotly, Matplotlib
*   **认证与安全**: 基于文件系统的用户认证与密码哈希
*   **其他**: `json`, `os`, `re`, `datetime`, `uuid`

## 安装与运行 🚀

### 1. 克隆仓库
```bash
git clone https://github.com/JiayiLiu07/CardioGuard-AI.git
cd CardioGuard-AI
```

### 2. 创建并激活虚拟环境 (推荐)
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖 📦
```bash
pip install -r requirements.txt
```
**注意**: `requirements.txt` 中列出的 `dashscope` 库是阿里云提供的兼容 OpenAI API 的 SDK，请确保安装。

### 4. 配置 API 密钥 🔑
本项目使用 **DashScope (阿里云通义千问)** 作为 LLM 后端。
请在以下文件中替换您的 DashScope API 密钥：
*   `p01_profile.py`
*   `p03_ai_doctor.py`
*   `p04_knowledge.py`
  
将 `api_key` 设置为您的实际密钥（请注意，示例密钥 `sk-e200005b066942eebc8c5426df92a6d5` 仅为占位符）：
```python
client = OpenAI(
    api_key="sk-YOUR_DASHSCOPE_API_KEY", # <-- 替换为您的密钥
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
```
如果您想使用 OpenAI 官方 API，只需更改 `base_url` 或移除，并确保 API 密钥正确。

### 5. 准备模型文件 (若无则训练) ⚙️
项目依赖 `assets/cv_risk_model.json` (XGBoost 模型) 和 `assets/model_metadata.json` (模型元数据) 进行心血管风险预测。
请确保这些文件存在于 `assets/` 目录下。如果缺失，您可能需要运行一个模型训练脚本（本仓库未提供，但可基于 `data/cardio_train.csv` 自行训练并保存）。

### 6. 运行 Streamlit 应用 ▶️
```bash
streamlit run app.py
```
这将在您的浏览器中打开应用程序。

## 使用指南 📖

1.  **首页 (p00_intro.py) / 登录注册 (p00_auth.py)**: 初次访问请先注册账号并登录。登录成功后将自动跳转至健康档案页面。
2.  **健康档案 (p01_profile.py)**: 务必详细填写您的个人健康信息，包括生理指标、疾病史（含亚型）和生活习惯。这是所有 AI 分析和建议的基础。
3.  **健康总览 (p01_overview.py)**: 在档案完善后，此处会展示您的心血管风险预测、AI 亚型分析和生活方式建议。
4.  **AI 营养师 (p02_nutrition.py)**: 根据您的健康数据生成个性化食谱。
5.  **AI 医生 (p03_ai_doctor.py)**: 随时提问，获取健康咨询。
6.  **知识库 (p04_knowledge.py)**: 探索心血管疾病知识和数据洞察。
7.  **我的中心 (p05_me.py)**: 管理您的个人信息、查看健康日志和账户设置。

## 文件结构 📂

```
CardioGuard-AI/
├── assets/
│   ├── cardio_recipes.py         # 食谱数据库
│   ├── cv_risk_model.json        # 心血管风险预测模型
│   └── model_metadata.json       # 模型元数据 (特征重要性等)
├── data/
│   └── cardio_train.csv          # 心血管疾病训练数据 (Kaggle)
├── pages/
│   ├── p00_auth.py               # 用户认证 (登录/注册/重置密码)
│   ├── p00_home.py               # 首页 (带动画和信息展示)
│   ├── p00_intro.py              # 引导页 (重定向到 auth 或 home)
│   ├── p01_overview.py           # 健康总览 (风险预测、SHAP、AI 建议)
│   ├── p01_profile.py            # 健康档案 (用户数据输入)
│   ├── p02_nutrition.py          # AI 营养师 (食谱生成)
│   ├── p03_ai_doctor.py          # AI 医生 (聊天机器人)
│   ├── p04_knowledge.py          # 知识库 (数据洞察、疾病图谱、智能问答)
│   └── p05_me.py                 # 我的中心 (个人信息、健康日志、账户管理)
├── picture/                      # 存放图片资源 (如动图、示意图)
│   ├── 血管堵塞动图.gif
│   ├── 心脏电击动过程动图.gif
│   ├── 胸痛主要原因.jpg
│   └── 超声下的心脏跳动图.gif
├── requirements.txt              # 项目依赖
└── README.md                     # 项目说明 (您正在阅读的这份文件)
```

## 注意事项与免责声明 ⚠️

*   **数据安全**: 用户的健康档案和日志数据默认存储在本地文件 (`users/heart_profile_data.json`, `users/user_logs.json`)，确保个人隐私。
*   **模型局限**: AI 风险预测模型基于公开数据集训练，其结果仅供参考，不能替代专业的医疗诊断。
*   **AI 建议**: AI 医生和营养师提供的建议是基于通用医学知识和您的输入数据生成，不构成正式的医疗处方或治疗方案。
*   **请务必**: 在做出任何健康决策前，咨询专业的医生或医疗机构。

---

## Bug 追踪器 🐞

请通过 GitHub Issues 报告问题或提交功能请求：
[https://github.com/JiayiLiu07/CardioGuard-AI/issues](https://github.com/JiayiLiu07/CardioGuard-AI/issues)

## 作者与联系方式 📧

CardioGuard AI 由 Jiayi Liu 倾情打造，希望为您带来健康与活力！🌟 欢迎体验这个项目，并分享您的宝贵建议！😊 有任何问题或想法，请随时联系：

-   **作者**：Jiayi Liu (GitHub: [JiayiLiu07](https://github.com/JiayiLiu07))
-   **联系方式**：通过 [GitHub Issues 页面](https://github.com/JiayiLiu07/CardioGuard-AI/issues) 提交反馈，或在 GitHub 上与我直接交流。期待听到您的声音！📬

