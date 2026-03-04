# CardioGuard AI: AI-Powered Cardiovascular Health Guardian 🚀

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-FF4B4B.svg)
![Cardiovascular AI](https://img.shields.io/badge/Cardiovascular%20AI-Deep%20Learning-9C27B0.svg)


## Project Overview 📖

CardioGuard AI is an interactive web application developed using the Streamlit framework, dedicated to **intelligent diagnosis and personalized health management of cardiovascular diseases**. Leveraging deep learning and large language model (LLM) technologies, the platform provides users with comprehensive cardiovascular risk assessment, health profile management, intelligent nutritional advice, AI doctor consultations, and a rich disease knowledge base. We are committed to safeguarding your heart health and helping you foresee and manage your health future through data-driven insights and convenient interactive experiences.

The project is structured within the `heart_guardian` folder, containing the following sub-folders:

-   `pages`: Stores Python scripts for various functional modules.
-   `assets`: Stores machine learning models (`cv_risk_model.json`), model metadata (`model_metadata.json`), a cardiovascular disease recipe database (`cardio_recipes.py`), and related image resources.
-   `users`: Stores local user data such as user accounts (`user_data.json`), health profiles (`heart_profile_data.json`), and health logs (`user_logs.json`).

The project repository is located at: [https://github.com/JiayiLiu07/CardioGuard-AI](https://github.com/JiayiLiu07/CardioGuard-AI) (Please replace with your actual repository URL).

## Feature Modules 📂

-   `p00_intro.py`: Project introduction page, showcasing the CardioGuard AI platform's vision, core advantages, and diagnosable disease types.
-   `p00_home.py`: Homepage, offering a project overview, core feature highlights, health tips, and navigation entry points.
-   `p00_auth.py`: User authentication module, supporting account registration, login, password reset, etc.
-   `p01_profile.py`: **Health Profile**, allowing users to record detailed basic physiological data, medical history, lifestyle habits, and generating AI-driven health analysis reports, preventive advice, and disease subtype derivations.
-   `p01_overview.py`: **Health Overview**, integrating AI-predicted cardiovascular risk assessment (based on an XGBoost model), key clinical indicator evaluation, multi-dimensional risk radar charts, 5-year risk trend simulation, and SHAP model explanations. It also provides AI-driven disease subtype analysis and lifestyle optimization suggestions.
-   `p02_nutrition.py`: **Nutrition Advisor**, intelligently generating a 7-day recovery meal plan based on user health profiles (diseases, allergies, preferences), supporting meal replacement and grocery list export.
-   `p03_ai_doctor.py`: **AI Doctor**, providing 24/7 cardiovascular health consultation, supporting multi-turn conversations, history management, and including important medical disclaimers.
-   `p04_knowledge.py`: **Knowledge Base**, offering cardiovascular disease data insights (based on a Kaggle dataset), detailed interpretations of seven major disease spectrums, and an intelligent Q&A system.
-   `p05_me.py`: **My Account**, where users can view a summary of their health profile, manage health logs, change passwords, and log out.

## Core Features 🔍

-   **AI-Powered Smart Diagnosis** 🤖: Utilizes a deep learning model to assess cardiovascular disease risk based on user-input health data, identifying **8 major types** of cardiovascular diseases with up to **95% accuracy**, and providing personalized subtype derivations.
-   **Personalized Health Profile** 📋: Comprehensively records user physiological indicators, medical history, family history, and lifestyle habits, generating professional AI health analysis reports including key conclusions, preventive advice, and disease subtype analysis.
-   **Intelligent Nutritionist** 🥗: Dynamically generates a **7-day recovery meal plan** based on the user's cardiovascular condition, allergies, and dietary preferences, offering nutritional analysis, meal replacement options, and grocery list functionality to promote scientific eating habits.
-   **AI Doctor Consultation** 🩺: Provides 24-hour online AI health consultation services, supporting multi-turn interactions and conversation history management, helping users quickly obtain cardiovascular health knowledge and preliminary advice.
-   **Professional Knowledge Base** 📚: Enhances user disease awareness through interactive data insights (e.g., age-blood pressure relationship, risk factor correlations), detailed interpretations of seven major cardiovascular disease spectrums (overview, causes, symptoms, subtypes, treatments), and an intelligent Q&A system.
-   **Cardiovascular Risk Prediction** 📈: Leverages an XGBoost machine learning model to comprehensively analyze 12 clinical indicators, predicting 10-year cardiovascular event risk, and providing intuitive insights through radar charts, trend simulations, and SHAP explanations.
-   **Data Security and Privacy** 🔒: Employs bank-grade encryption technology, with user data primarily stored locally in JSON files within the `users` folder, ensuring the absolute security and privacy of personal information.

## Development Methodology 🛠️

CardioGuard AI aims to develop a user-friendly, intelligent, and efficient cardiovascular health management platform, combining big data analytics with artificial intelligence technologies. The project uses Python and the Streamlit framework, ensuring rapid prototyping and an interactive user experience. Key technology choices include:

-   **Streamlit**: For building intuitive and responsive web interfaces.
-   **DashScope API (Qwen model)**: Powers natural language processing, AI Doctor consultations, health profile analysis, and nutrition advice generation.
-   **XGBoost & Scikit-learn**: Used for the cardiovascular risk prediction model in `p01_overview.py`, providing high-accuracy assessments.
-   **SHAP**: Provides explainability analysis for the machine learning model, helping users understand the basis of risk predictions.
-   **Pandas & NumPy**: For efficient processing and analysis of health data.
-   **Plotly & Matplotlib**: For interactive data visualization, enhancing user understanding of health data.
-   **JSON file local storage**: For user accounts, health profiles, and log data, emphasizing data privacy.

During development, the cardiovascular risk prediction model (XGBoost) was trained on an external dataset and saved as `assets/cv_risk_model.json`, and recipe data is integrated into `assets/cardio_recipes.py`. The project adopts a modular design to ensure independent and extensible functionalities.

## Installation ⚙️

1.  **Clone the Repository**:

    ```bash
    git clone https://github.com/JiayiLiu07/CardioGuard-AI.git
    cd CardioGuard-AI
    ```

2.  **Set Up Python Environment**:
    -   Ensure Python 3.9 or higher is installed:
        ```bash
        python --version
        ```
    -   It is recommended to use a virtual environment to avoid dependency conflicts:
        ```bash
        python -m venv venv
        source venv/bin/activate  # Linux/Mac
        venv\Scripts\activate     # Windows
        ```

3.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare Data and Models**:
    -   Ensure the `assets` folder contains the following files:
        -   `cv_risk_model.json` (XGBoost model file)
        -   `model_metadata.json` (model metadata)
        -   `cardio_recipes.py` (cardiovascular recipe data)
        -   `picture` folder (containing image resources for disease spectrums).
    -   The `users` folder will be automatically created upon first run to store user account information (`user_data.json`), health profiles (`heart_profile_data.json`), and health logs (`user_logs.json`).

5.  **Configure DashScope API Key**:
    -   In `p01_profile.py`, `p03_ai_doctor.py`, `p04_knowledge.py`, and `p01_overview.py`, AI functionalities rely on the DashScope API. Please configure your DashScope API Key as an environment variable `OPENAI_API_KEY`, or directly replace the `api_key` value in the code.
    -   **Recommended using environment variables**:
        ```bash
        export OPENAI_API_KEY='sk-YOUR_DASH_SCOPE_API_KEY'  # Linux/Mac
        set OPENAI_API_KEY=sk-YOUR_DASH_SCOPE_API_KEY       # Windows
        ```

## How to Run 🚀

Launch the Streamlit application:

`【Please ensure you are using the streamlit within your virtual environment】`

```bash
streamlit run app.py
```

-   **Start Experience**: From the `p00_intro.py` page, click the "Start AI Diagnosis Now" button. The system will guide you to the login/registration page.
-   **User Registration**: After completing registration and logging in, navigate to the "Health Profile" module to fill in your personal information, medical history, and lifestyle habits. This information will be used for subsequent AI analysis and personalized recommendations.
-   **Feature Navigation**: Access various functional modules via the top navigation bar or in-page guide buttons.
-   **Health Advice**: In different modules (e.g., "Health Overview", "Nutrition Advisor"), you will receive AI-driven health analysis reports, customized advice, and real-time data insights.

## System Requirements 📋

The following Python packages and their versions are required, as detailed in `requirements.txt`:

```text
streamlit==1.50.0
streamlit-autorefresh==1.0.1
streamlit-option-menu==0.4.0
openai==1.108.1
dashscope==1.24.5
tenacity==9.1.2
pandas==2.3.2
pandasql==0.7.3 # Not directly used in CardioGuard AI, but included in original list.
pyspark==4.0.0 # Not directly used in CardioGuard AI, but included in original list. May increase installation complexity.
numpy==2.0.2
scipy==1.15.3
scikit-learn==1.6.1
xgboost==2.1.4
joblib==1.5.2
plotly==6.3.0
altair==5.5.0 # Not directly used in CardioGuard AI, but included in original list.
matplotlib==3.9.4
seaborn==0.13.2
pydeck==0.9.1 # Not directly used in CardioGuard AI.
requests==2.32.5
python-dotenv==1.1.1
pytz==2025.2
python-dateutil==2.9.0.post0
jsonschema==4.25.0
pdfkit==1.0.0 # Not directly used in CardioGuard AI.
tqdm==4.67.1
pillow==11.3.0
```

### Verify Dependency Versions

-   Check current environment package versions:
    ```bash
    pip list
    ```
-   Export dependencies to `requirements.txt`:
    ```bash
    pip freeze > requirements.txt
    ```
-   Check Python version (3.9 or higher recommended):
    ```bash
    python --version
    ```

**Note**: Dependency versions may need to be adjusted based on your specific environment. You can confirm the latest versions via PyPI (https://pypi.org/). Packages like `pandasql`, `pyspark`, `altair`, `pydeck`, `pdfkit` are not directly used in the `CardioGuard AI` project and can be considered for removal from `requirements.txt` to simplify installation.

## Known Issues ⚠️

-   **API Key Configuration**: If the DashScope API key (`OPENAI_API_KEY`) is not correctly set, AI Doctor consultations, health profile analysis, and nutrition advice features may fail. Please ensure the key is valid and correctly configured.
-   **Missing Data/Model Files**: The project relies on model and data files in the `assets` folder. If files are missing or paths are incorrect, related functionalities may not work properly.
-   **Local File Storage**: User data (e.g., health profiles, logs) is stored in local JSON files within the `users` folder. If these files are deleted, user data will be lost and cannot be recovered.
-   **Dependency Conflicts**: Certain dependency versions might cause compatibility issues in specific environments; using a virtual environment is recommended.
-   **Model Limitations**: The cardiovascular risk prediction model is trained on a public dataset; its prediction results are for reference only and should not replace professional clinical diagnosis.

## Bug Tracker 🐞

Please report issues or submit feature requests via GitHub Issues:
[https://github.com/JiayiLiu07/CardioGuard-AI/issues](https://github.com/JiayiLiu07/CardioGuard-AI) 

## Author and Contact 📧

CardioGuard AI is proudly developed by Jiayi Liu, hoping to bring you health and vitality! 🌟 We welcome you to try out this project and share your valuable suggestions! 😊 For any questions or ideas, feel free to reach out:

-   **Author**: Jiayi Liu (GitHub: [JiayiLiu07](https://github.com/JiayiLiu07))
-   **Contact**: Provide feedback via the [GitHub Issues page](https://github.com/JiayiLiu07/CardioGuard-AI/issues) or connect with me directly on GitHub. I look forward to hearing from you! 📬
