# CardioGuard AI - Smart Cardiovascular Health Management Platform 💖

## Introduction 📝

CardioGuard AI is an intelligent cardiovascular health management application built with Streamlit. It aims to provide users with comprehensive cardiovascular health insights and personalized management solutions by integrating personal health data, AI-assisted analysis, nutrition advice, smart Q&A, and a professional knowledge base. This platform leverages advanced machine learning models to predict cardiovascular disease risk and utilizes large language models (DashScope Qwen) to offer professional medical consultation and lifestyle recommendations.

## Core Features ✨

1.  **Health Profile 📋**
    *   Record and manage user's basic physiological indicators (age, gender, height, weight, blood pressure, blood lipids, blood glucose).
    *   Detailed cardiovascular disease history (major categories and subtypes).
    *   Lifestyle and risk factor assessment (smoking, alcohol, late nights, exercise, dietary preferences, allergies, etc.).
    *   Data stored locally to ensure privacy and security.

2.  **Health Overview 📊**
    *   Predicts 10-year cardiovascular disease risk using an XGBoost machine learning model based on the user's health profile.
    *   Provides multi-dimensional personal risk radar charts and key indicator trend simulations.
    *   Utilizes SHAP values to explain model predictions, revealing the contribution of each factor to individual risk.
    *   AI intelligently infers unspecified disease subtypes and deeply analyzes selected subtypes.
    *   AI generates personalized lifestyle optimization suggestions (exercise, diet, routine, mental health, warning signs).

3.  **AI Nutritionist 🥗**
    *   Intelligently generates customized 7-day cardiovascular recovery meal plans based on user's health profile (diseases, allergies, dietary preferences).
    *   Provides detailed recipe information, including dish names, ingredients, cooking steps, and nutritional values.
    *   Supports a "swap recipe" feature for flexible adjustments.
    *   Automatically generates a weekly shopping list, categorized by ingredients.
    *   Offers practical dietary health tips.

4.  **AI Doctor 🩺**
    *   24/7 intelligent Q&A, allowing users to consult on cardiovascular health issues anytime.
    *   Supports multi-turn conversations, providing professional medical answers and advice.
    *   Saves chat history for easy review and management.

5.  **Knowledge Base 📚**
    *   Provides cardiovascular disease data insights, displaying relationships between age, blood pressure, risk factors through interactive charts.
    *   Detailed knowledge map of seven major cardiovascular disease categories, including causes, symptoms, subtypes, treatment, and prevention.
    *   Includes a smart Q&A module to answer professional questions about diseases.

6.  **My Center 👤**
    *   View and edit a summary of personal health records.
    *   Record and manage personal health logs.
    *   Supports password reset and account deletion functions.
    *   Emphasizes data security and privacy protection.

## Technology Stack 💻

*   **Frontend Framework**: Streamlit
*   **AI/ML**:
    *   Large Language Model (LLM): DashScope (Qwen-turbo, Qwen-max)
    *   Machine Learning: XGBoost, SHAP (for risk prediction and model interpretability)
*   **Data Processing**: Pandas, NumPy
*   **Data Visualization**: Plotly, Matplotlib
*   **Authentication & Security**: File-based user authentication and password hashing
*   **Other**: `json`, `os`, `re`, `datetime`, `uuid`

## Installation and Setup 🚀

### 1. Clone the repository
```bash
git clone https://github.com/JiayiLiu07/CardioGuard-AI.git
cd CardioGuard-AI
```

### 2. Create and activate a virtual environment (recommended)
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies 📦
```bash
pip install -r requirements.txt
```
**Note**: The `dashscope` library listed in `requirements.txt` is an SDK provided by Alibaba Cloud that is compatible with the OpenAI API. Please ensure it is installed.

### 4. Configure API Key 🔑
This project uses **DashScope (Alibaba Cloud Qwen)** as the LLM backend.
Please replace your DashScope API key in the following files:
*   `p01_profile.py`
*   `p03_ai_doctor.py`
*   `p04_knowledge.py`
  
Set the `api_key` to your actual key (please note that the example key `sk-e200005b066942eebc8c5426df92a6d5` is a placeholder):
```python
client = OpenAI(
    api_key="sk-YOUR_DASHSCOPE_API_KEY", # <-- Replace with your key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
```
If you wish to use the official OpenAI API, simply change or remove `base_url` and ensure your API key is correct.

### 5. Prepare Model Files (Train if missing) ⚙️
The project relies on `assets/cv_risk_model.json` (XGBoost model) and `assets/model_metadata.json` (model metadata) for cardiovascular risk prediction.
Please ensure these files exist in the `assets/` directory. If they are missing, you might need to run a model training script (not provided in this repository, but can be developed based on `data/cardio_train.csv`).

### 6. Run the Streamlit Application ▶️
```bash
streamlit run app.py
```
This will open the application in your web browser.

## Usage Guide 📖

1.  **Homepage (p00_intro.py) / Login & Registration (p00_auth.py)**: If you're a first-time user, please register an account and log in. Upon successful login, you will be automatically redirected to the Health Profile page.
2.  **Health Profile (p01_profile.py)**: It is crucial to fill in your personal health information in detail, including physiological indicators, disease history (with subtypes), and lifestyle habits. This forms the foundation for all AI analyses and recommendations.
3.  **Health Overview (p01_overview.py)**: Once your profile is complete, this section will display your cardiovascular risk predictions, AI subtype analysis, and lifestyle recommendations.
4.  **AI Nutritionist (p02_nutrition.py)**: Generates personalized meal plans based on your health data.
5.  **AI Doctor (p03_ai_doctor.py)**: Ask questions anytime to receive health consultations.
6.  **Knowledge Base (p04_knowledge.py)**: Explore cardiovascular disease knowledge and data insights.
7.  **My Center (p05_me.py)**: Manage your personal information, view health logs, and account settings.

## File Structure 📂

```bash
streamlit run app.py
```
| Path                                        | Description                                                 |
| ------------------------------------------- | ----------------------------------------------------------- |
| `CardioGuard-AI/assets/cardio_recipes.py`   | Recipe database                                             |
| `CardioGuard-AI/assets/cv_risk_model.json`  | Cardiovascular risk prediction model                        |
| `CardioGuard-AI/assets/model_metadata.json` | Model metadata (feature importance, etc.)                   |
| `CardioGuard-AI/data/cardio_train.csv`      | Cardiovascular disease training data (Kaggle)               |
| `CardioGuard-AI/pages/p00_auth.py`          | User authentication (login/register/reset password)         |
| `CardioGuard-AI/pages/p00_home.py`          | Homepage (with animations and info display)                 |
| `CardioGuard-AI/pages/p00_intro.py`         | Landing page (redirects to auth or home)                    |
| `CardioGuard-AI/pages/p01_overview.py`      | Health Overview (risk prediction, SHAP, AI recommendations) |
| `CardioGuard-AI/pages/p01_profile.py`       | Health Profile (user data input)                            |
| `CardioGuard-AI/pages/p02_nutrition.py`     | AI Nutritionist (meal plan generation)                      |
| `CardioGuard-AI/pages/p03_ai_doctor.py`     | AI Doctor (chatbot)                                         |
| `CardioGuard-AI/pages/p04_knowledge.py`     | Knowledge Base (data insights, disease map, smart Q\&A)     |
| `CardioGuard-AI/pages/p05_me.py`            | My Center (personal info, health logs, account management)  |
| `CardioGuard-AI/picture/血管堵塞动图.gif`         | Vessel blockage animation                                   |
| `CardioGuard-AI/picture/心脏电击动过程动图.gif`      | Cardiac defibrillation animation                            |
| `CardioGuard-AI/picture/胸痛主要原因.jpg`         | Main causes of chest pain                                   |
| `CardioGuard-AI/picture/超声下的心脏跳动图.gif`      | Heartbeat under ultrasound                                  |
| `CardioGuard-AI/requirements.txt`           | Project dependencies                                        |
| `CardioGuard-AI/README.md`                  | Project description                                         |


## Important Notes & Disclaimer ⚠️

*   **Data Security**: User health profiles and log data are stored locally by default (`users/heart_profile_data.json`, `users/user_logs.json`) to ensure personal privacy.
*   **Model Limitations**: The AI risk prediction model is trained on public datasets, and its results are for reference only, not a substitute for professional medical diagnosis.
*   **AI Advice**: Advice provided by the AI Doctor and Nutritionist is generated based on general medical knowledge and your input data, and does not constitute a formal medical prescription or treatment plan.
*   **Always**: Consult a professional doctor or medical institution before making any health decisions.

---

## Bug Tracker 🐞

Please report issues or submit feature requests via GitHub Issues:
[https://github.com/JiayiLiu07/CardioGuard-AI/issues](https://github.com/JiayiLiu07/CardioGuard-AI/issues)

## Author & Contact 📧

CardioGuard AI is passionately crafted by Jiayi Liu, aiming to bring health and vitality to you! 🌟 We welcome you to experience this project and share your valuable suggestions! 😊 For any questions or ideas, feel free to contact:

-   **Author**: Jiayi Liu (GitHub: [JiayiLiu07](https://github.com/JiayiLiu07))
-   **Contact**: Provide feedback via the [GitHub Issues page](https://github.com/JiayiLiu07/CardioGuard-AI/issues) or connect with me directly on GitHub. I look forward to hearing from you! 📬
