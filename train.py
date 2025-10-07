# cardioguard/train.py

import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.inspection import PartialDependenceDisplay
import os
import json
import joblib # For saving models

# --- 数据加载与预处理 ---
def load_and_preprocess_data(csv_path='data/cardio_train.csv'):
    if not os.path.exists(csv_path):
        st.error(f"数据文件未找到: {csv_path}。请确保 'data' 目录下存在 'cardio_train.csv'。")
        return None, None, None, None

    df = pd.read_csv(csv_path, sep=';') # Assuming separator is semicolon based on common datasets

    # 数据清洗和转换
    # 1. 移除 'id' 列，因为它对模型无用
    df = df.drop('id', axis=1)

    # 2. 'age' 列单位是天，转换为年
    df['age_years'] = df['age'] / 365.25
    df = df.drop('age', axis=1)

    # 3. 'gender' 列（1: woman, 2: man）。转换为 0/1
    df['gender'] = df['gender'].apply(lambda x: 1 if x == 2 else 0) # 0 for female, 1 for male

    # 4. 'height' 和 'weight' 转换为 BMI
    # height is in cm, convert to meters
    df['height_m'] = df['height'] / 100
    df['bmi'] = df['weight'] / (df['height_m']**2)
    df = df.drop(['height', 'weight', 'height_m'], axis=1)

    # 5. 'ap_hi' (systolic blood pressure), 'ap_lo' (diastolic blood pressure)
    # Handle potential outliers or invalid entries (e.g., systolic < diastolic)
    # For simplicity, we'll filter out extreme values. A more robust approach might be needed.
    df = df[(df['ap_hi'] > 50) & (df['ap_hi'] < 250)] # Filter extreme systolic BPs
    df = df[(df['ap_lo'] > 0) & (df['ap_lo'] < 150)]  # Filter extreme diastolic BPs
    # Ensure systolic >= diastolic, if not, might indicate data entry error.
    # For this example, we'll assume valid entries are mostly correct.

    # 6. 'cholesterol' and 'gluc' are categorical: 1: normal, 2: above normal, 3: very high
    # These can be treated as ordered categories or one-hot encoded.
    # For tree models, Label Encoding or keeping as is can work if they are numerically ordered.
    # Let's treat them as ordered for now.

    # 7. 'cardio' is the target variable (1: heart disease, 0: no heart disease)

    # Define features and target
    features = [col for col in df.columns if col != 'cardio']
    target = 'cardio'

    X = df[features]
    y = df[target]

    # Ensure all feature columns are numeric
    for col in X.columns:
        if X[col].dtype == 'object':
            st.warning(f"Column '{col}' has object dtype. Attempting Label Encoding.")
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])

    return df, X, y, features

# --- 模型训练 ---
def train_risk_model(X, y, model_path='assets/xgb_risk.pkl'):
    st.write("正在训练心血管风险预测模型...")
    model = xgb.XGBClassifier(objective='binary:logistic',
                              eval_metric='auc',
                              use_label_encoder=False,
                              n_estimators=100,
                              learning_rate=0.1,
                              max_depth=3,
                              subsample=0.8,
                              colsample_bytree=0.8,
                              random_state=42)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model.fit(X_train, y_train)

    # 保存模型
    joblib.dump(model, model_path)
    st.success(f"心血管风险预测模型已训练并保存至 {model_path}")

    # 评估模型 (可选，这里主要为可视化做准备)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    cm = confusion_matrix(y_test, model.predict(X_test))

    st.write(f"模型在测试集上的 AUC: {auc:.4f}")
    st.write(f"模型在测试集上的 Accuracy: {accuracy:.4f}")
    st.write("混淆矩阵:")
    st.dataframe(pd.DataFrame(cm, index=['No Disease', 'Disease'], columns=['Predicted No Disease', 'Predicted Disease']))

    return model, X_test, y_test # Return for visualization

# --- 模型训练 (心血管疾病亚型预测 - 这是一个简化的示例) ---
# 假设我们有一个独立的模型来预测疾病亚型
# 在实际应用中，这可能需要更复杂的模型或多标签分类
def train_subtype_model(X, y_subtype, model_path='assets/xgb_subtype.pkl'):
    st.write("正在训练疾病亚型预测模型 (简化示例)...")
    # 这是一个占位符，实际亚型预测可能需要不同的数据集和目标变量
    # 假设 y_subtype 是一个代表亚型的 Series
    if y_subtype is None or y_subtype.empty:
        st.warning("无疾病亚型数据，跳过亚型模型训练。")
        return None

    # 假设我们只训练一个分类器，预测几种常见的亚型
    # 对于真实场景，可能需要多输出模型或为每种亚型训练一个二分类器
    # 这里我们假定 y_subtype 已经是数字编码的亚型标签
    # 如果是文本，需要 LabelEncoder
    # For demonstration, we will use the same X but assume y_subtype is available
    # A more realistic scenario might involve filtering data for specific diseases

    # Dummy data for demonstration if no real subtype data is available
    if y_subtype.nunique() < 2: # Not enough classes to train a classifier
        st.warning("疾病亚型数据不足（少于2类），跳过亚型模型训练。")
        return None

    model = xgb.XGBClassifier(objective='multi:softmax', # Or 'binary:logistic' for binary sub-classification
                              num_class=y_subtype.nunique(), # Number of unique subtypes
                              eval_metric='mlogloss',
                              use_label_encoder=False,
                              n_estimators=100,
                              learning_rate=0.1,
                              max_depth=3,
                              subsample=0.8,
                              colsample_bytree=0.8,
                              random_state=42)

    X_train, X_test, y_train, y_test = train_test_split(X, y_subtype, test_size=0.2, random_state=42, stratify=y_subtype)

    model.fit(X_train, y_train)
    joblib.dump(model, model_path)
    st.success(f"疾病亚型预测模型已训练并保存至 {model_path}")
    return model

# --- 可视化生成 ---
def generate_visualizations(df, X, y, features, risk_model, model_test_data_path='assets/xgb_risk.pkl'):
    st.write("正在生成可视化图表...")

    # 确保 assets 目录存在
    if not os.path.exists('assets'):
        os.makedirs('assets')

    # 加载训练好的模型，如果 train.py 被单独运行
    if risk_model is None:
        if os.path.exists(model_test_data_path):
            try:
                risk_model = joblib.load(model_test_data_path)
                st.info(f"已加载模型 {model_test_data_path} 用于可视化生成。")
                # We need X_test and y_test to generate visualizations.
                # If models were saved without them, we need to reload or re-split.
                # For simplicity, let's re-split. In a real pipeline, you'd save/load X_test, y_test too.
                _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            except Exception as e:
                st.error(f"加载模型 {model_test_data_path} 失败: {e}")
                return
        else:
            st.error(f"模型文件 {model_test_data_path} 不存在，无法生成可视化。")
            return

    # 1. 全局特征重要性 (SHAP Bar Plot)
    st.write("1/4: 生成特征重要性图...")
    try:
        # Use explainer for the trained model
        # Ensure X is clean and has the same features as the training data
        explainer = shap.TreeExplainer(risk_model)
        # Calculate SHAP values on the full dataset X for a global view
        # Using a sample for performance if X is very large
        shap_values = explainer.shap_values(X) # shap_values for binary classification has two elements: [shap_for_class_0, shap_for_class_1]
                                             # We are interested in predicting cardio (class 1), so we use shap_values[1] or mean over all.
        
        # For binary classification, shap_values is a list of arrays.
        # explainer.shap_values(X) returns shap_values[0] for class 0 and shap_values[1] for class 1.
        # We are usually interested in predicting class 1 (cardio).
        # summary_plot uses the expected_value and shap_values for the positive class by default if not specified.
        
        # For TreeExplainer on XGBoost, shap_values is often a single numpy array if predicting single output, or list of arrays for multi-class/multi-output.
        # Let's use the standard approach for binary classification:
        shap_values_for_class_1 = explainer.shap_values(X)[1] if isinstance(explainer.shap_values(X), list) else explainer.shap_values(X)
        
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values_for_class_1, X, plot_type="bar", show=False, color='#E94560')
        plt.title('Global Feature Importance (SHAP)')
        plt.savefig('assets/global_shap.png', bbox_inches='tight', dpi=300)
        plt.close()
        st.write("特征重要性图已保存至 assets/global_shap.png")
    except Exception as e:
        st.error(f"生成特征重要性图失败: {e}")

    # 2. 相关性热力图
    st.write("2/4: 生成相关性热力图...")
    try:
        plt.figure(figsize=(12, 10))
        # Use the full dataframe including target for correlation
        correlation_df = df.copy()
        # Ensure all columns are numeric before calculating correlation
        for col in correlation_df.columns:
            if correlation_df[col].dtype == 'object':
                st.warning(f"Skipping correlation for non-numeric column '{col}'")
                correlation_df = correlation_df.drop(col, axis=1)

        sns.heatmap(correlation_df.corr(), cmap='RdYlGn', center=0, square=True, linewidths=.5)
        plt.title('Feature Correlation Heatmap')
        plt.savefig('assets/corr_heatmap.png', dpi=300)
        plt.close()
        st.write("相关性热力图已保存至 assets/corr_heatmap.png")
    except Exception as e:
        st.error(f"生成相关性热力图失败: {e}")

    # 3. 单因子 PDP (Partial Dependence Plots)
    st.write("3/4: 生成单因子 PDP...")
    try:
        # Select key features for PDP
        pdp_features = ['ap_hi', 'age_years', 'bmi', 'cholesterol', 'gluc'] # Example features
        # Ensure features exist in X
        pdp_features = [f for f in pdp_features if f in X.columns]

        if not pdp_features:
            st.warning("No valid features found for PDP.")
        else:
            # Create a figure to hold subplots
            n_features = len(pdp_features)
            # Adjust grid based on number of features. Let's make it a 2xN grid.
            n_cols = 2
            n_rows = (n_features + n_cols - 1) // n_cols
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5, n_rows * 4), squeeze=False)
            axes = axes.flatten() # Flatten for easy iteration

            # Generate PDP for each feature
            for i, feature in enumerate(pdp_features):
                if i < len(axes): # Ensure we don't exceed the number of axes
                    PartialDependenceDisplay.from_estimator(
                        risk_model, X, features=[feature],
                        target=1, # For class 1 (heart disease)
                        ax=axes[i],
                        grid_resolution=30, # Increased resolution
                        kind='average' # 'average' shows average PDP, 'individual' shows individual PDPs
                    )
                    axes[i].set_title(f'Partial Dependence of {feature}')
                    axes[i].set_xlabel(feature)
                    axes[i].set_ylabel('Risk Probability')
                else:
                    st.warning(f"Not enough axes for feature: {feature}")

            # Hide any unused subplots
            for j in range(i + 1, len(axes)):
                fig.delaxes(axes[j])

            plt.tight_layout()
            plt.savefig('assets/partial_dependence.png', dpi=300)
            plt.close()
            st.write("单因子 PDP 图已保存至 assets/partial_dependence.png")
    except Exception as e:
        st.error(f"生成单因子 PDP 图失败: {e}")

    # 4. 交互 PDP (Interaction PDP) - e.g., Systolic BP vs Age
    st.write("4/4: 生成交互 PDP...")
    try:
        # Define interaction features
        interaction_features = ['ap_hi', 'age_years'] # Example interaction: Systolic BP and Age
        
        if all(f in X.columns for f in interaction_features):
            # Using sns.heatmap to visualize the 2D grid of partial dependence
            # For more complex interactions or more features, a dedicated plotting function might be needed
            # Using `kind='grid'` for more direct visualization of the interaction grid
            
            # Let's use the specific example from the design: Systolic BP vs Age
            # We'll plot the interaction of ap_hi and age_years
            fig, ax = plt.subplots(figsize=(7, 5))
            
            # Calculate partial dependence for the interaction
            # grid_resolution determines the number of points sampled for each feature.
            # Higher resolution gives a smoother plot but takes longer.
            pd_results = partial_dependence(
                risk_model, X, features=interaction_features,
                grid_resolution=20, # Number of points along each axis
                kind='grid' # Returns a grid of values
            )

            # pd_results['grid'] contains the grid points for each feature
            # pd_results['average'][0] contains the partial dependence values (shape depends on features)
            
            # The output structure of partial_dependence for two features is:
            # grid: list of arrays, each array is the grid points for a feature
            # average: array of average partial dependence values, shape (n_features, n_grid_points) for 1D,
            #          or shape (n_grid_points_feature1, n_grid_points_feature2) for 2D
            
            # For two features, pd_results['average'] is a 2D array
            XX, YY = np.meshgrid(pd_results['grid'][0], pd_results['grid'][1])
            ZZ = pd_results['average'][0].T # Transpose to match heatmap expectation

            # Use seaborn heatmap for visualization
            sns.heatmap(ZZ, xticklabels=False, yticklabels=False, cmap='Reds', ax=ax, cbar_kws={'label': 'Risk Probability'})
            ax.set_xlabel('Systolic Blood Pressure (ap_hi)')
            ax.set_ylabel('Age (years)')
            ax.set_title('Interaction PDP: Systolic BP × Age')
            
            plt.tight_layout()
            plt.savefig('assets/interact_pdp.png', dpi=300)
            plt.close()
            st.write("交互 PDP 图已保存至 assets/interact_pdp.png")
        else:
            st.warning("Interaction features 'ap_hi' or 'age_years' not found in dataset.")
    except Exception as e:
        st.error(f"生成交互 PDP 图失败: {e}")

    st.success("所有可视化图表已生成并保存到 'assets' 目录。")

# --- health_tips.json 生成 ---
def generate_health_tips_json():
    tips = [
        "每日减盐 1 g → 收缩压降 2 mmHg",
        "每周 150 min 快走 → 心血管事件降 30 %",
        "保持健康体重：BMI 维持在 18.5 - 24 之间。",
        "戒烟限酒，低脂低盐饮食是心脏健康的基石。",
        "规律作息，保证充足睡眠，有助于心血管系统休息和恢复。",
        "定期监测血压、血糖、血脂，及时发现和管理风险。",
        "适度运动：每周至少进行 150 分钟中等强度有氧运动。",
        "增加蔬菜水果摄入，每餐至少占盘子的一半。",
        "学习压力管理技巧，如冥想、瑜伽，缓解心血管压力。",
        "与家人分享健康饮食，共同营造健康生活方式。",
        "关注心率变化，异常时及时就医。",
        "高血压患者需遵医嘱服药，切勿自行停药或减量。",
        "糖尿病患者需严格控制血糖，定期复查。",
        "了解冠心病症状：胸痛、胸闷、心悸等。",
        "心力衰竭早期识别很重要，留意呼吸困难、水肿等。",
        "房颤患者需警惕脑卒中风险，遵医嘱抗凝治疗。",
        "多吃富含Omega-3脂肪酸的鱼类（如三文鱼、鲭鱼）。",
        "少吃加工食品和红肉，多选择全谷物、豆类和坚果。",
        "保持积极心态，乐观面对生活中的挑战。",
        "与医生建立良好的沟通，及时反馈身体状况。",
    ]
    
    # Shuffle tips for daily random order
    np.random.shuffle(tips)

    with open('assets/health_tips.json', 'w', encoding='utf-8') as f:
        json.dump(tips, f, ensure_ascii=False, indent=4)
    st.info("健康建议 'assets/health_tips.json' 已生成。")

# --- 主执行逻辑 ---
if __name__ == "__main__":
    st.title("CardioGuard AI - 模型训练与可视化")
    st.markdown("---")

    # 检查数据集是否存在
    if not os.path.exists('data/cardio_train.csv'):
        st.error("请将 'cardio_train.csv' 放入 'data/' 目录。")
    else:
        # 1. 加载和预处理数据
        df, X, y, features = load_and_preprocess_data()

        if df is not None and X is not None and y is not None:
            # 2. 训练风险模型
            # 第一次运行时，可能需要训练模型并保存
            # 可以添加一个按钮来触发训练
            if st.button("开始训练心血管风险模型"):
                # 确保 assets 目录存在
                if not os.path.exists('assets'):
                    os.makedirs('assets')
                
                # Re-split data for training if not already done implicitly
                # For training, we need to split the data.
                # The generation of visualizations might need the test set, or the whole dataset depending on the method.
                # Let's retrain on the whole dataset for generating global visualizations
                # Or train on train_test_split and use X_test, y_test for SHAP etc.
                
                # Train on the entire dataset for more representative global features.
                # For actual model performance evaluation, we should use train_test_split.
                # Here, for simplicity and to ensure SHAP/PDP are based on the model that `train.py` would deploy,
                # we'll train on the whole X, y and then generate visualizations.
                # In a real scenario, you'd train on training set and evaluate on test set.
                
                # Let's do a train/test split within this script for visualization purposes
                X_train_viz, X_test_viz, y_train_viz, y_test_viz = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

                # Train the model
                trained_risk_model, _, _ = train_risk_model(X_train_viz, y_train_viz, model_path='assets/xgb_risk.pkl')
                
                # Train subtype model (if subtype data exists)
                # For this demo, let's assume 'ap_hi' can be a proxy for some "subtype" for illustration
                # In a real case, you'd need a dedicated 'subtype' column.
                # Here, we'll skip it unless a proper 'subtype' column is provided in the dataset.
                # If 'ap_hi' is used, it should be categorized.
                # Example:
                # if 'ap_hi' in X.columns:
                #     X['ap_hi_cat'] = pd.cut(X['ap_hi'], bins=[0, 120, 140, 160, np.inf], labels=[0, 1, 2, 3], right=False)
                #     # Ensure X_train_viz and X_test_viz are updated with this new column
                #     # ... and then train subtype model
                # For now, we assume no subtype data is readily available.

                # Generate visualizations using the trained model and test data
                generate_visualizations(df, X_test_viz, y_test_viz, features, trained_risk_model, model_path='assets/xgb_risk.pkl') # Pass X_test_viz and y_test_viz for evaluation metrics if needed

                # Generate health tips JSON
                generate_health_tips_json()
                
                st.balloons()
                st.success("模型训练和可视化生成完成！")

            else:
                st.write("点击上方按钮开始训练模型并生成可视化。")
                st.markdown("---")
                st.subheader("已生成的可视化图表 (assets/):")
                if os.path.exists('assets/global_shap.png'):
                    st.image('assets/global_shap.png', caption='特征重要性 (SHAP)', use_column_width=True)
                if os.path.exists('assets/corr_heatmap.png'):
                    st.image('assets/corr_heatmap.png', caption='特征相关性热力图', use_column_width=True)
                if os.path.exists('assets/partial_dependence.png'):
                    st.image('assets/partial_dependence.png', caption='单因子部分依赖图 (PDP)', use_column_width=True)
                if os.path.exists('assets/interact_pdp.png'):
                    st.image('assets/interact_pdp.png', caption='交互部分依赖图 (SBP × Age)', use_column_width=True)

                st.markdown("---")
                st.subheader("健康建议 (assets/health_tips.json):")
                if os.path.exists('assets/health_tips.json'):
                    with open('assets/health_tips.json', 'r', encoding='utf-8') as f:
                        tips_data = json.load(f)
                    st.json(tips_data)
                else:
                    st.warning("健康建议 JSON 文件未找到。")
