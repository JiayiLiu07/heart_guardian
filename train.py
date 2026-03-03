# train.py
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import json
import os

# --- 1. 路径设置 ---
data_path = 'data/cardio_train.csv'
assets_dir = 'assets'
os.makedirs(assets_dir, exist_ok=True)
model_path = os.path.join(assets_dir, 'cv_risk_model.json')
meta_path = os.path.join(assets_dir, 'model_metadata.json')

print(f"📂 正在加载数据：{data_path} ...")

if not os.path.exists(data_path):
    raise FileNotFoundError(f"❌ 文件不存在：{data_path}")

# --- 2. 读取数据 (关键修复：指定分隔符为分号) ---
df = pd.read_csv(data_path, sep=';')

print(f"✅ 数据加载成功。形状：{df.shape}")
print(f"🏷️  列名确认：{df.columns.tolist()}")

# --- 3. 数据预处理 ---
# 清洗异常值 (根据实际列名访问)
# ap_hi: 收缩压, ap_lo: 舒张压
df = df[(df['ap_hi'] > 50) & (df['ap_hi'] < 250)]
df = df[(df['ap_lo'] > 30) & (df['ap_lo'] < 150)]
df = df[(df['height'] > 100) & (df['height'] < 250)]
df = df[(df['weight'] > 30) & (df['weight'] < 200)]

# 特征工程
# 计算 BMI
df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)
# 转换年龄为天 -> 年
df['age_years'] = (df['age'] / 365).astype(int)

# --- 4. 准备模型输入 ---
# 注意：原数据集中 alcohol 列名为 'alco'
features = ['age_years', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active', 'bmi']
target = 'cardio'

# 检查是否有缺失列
missing = [col for col in features if col not in df.columns]
if missing:
    raise ValueError(f"❌ 数据集中缺少以下列：{missing}")

X = df[features]
y = df[target]

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("🚀 开始训练 XGBoost 模型...")

# --- 5. 模型训练 ---
model = xgb.XGBClassifier(
    objective='binary:logistic',
    n_estimators=150,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='logloss',
    use_label_encoder=False,
    random_state=42
)

model.fit(X_train, y_train)

# --- 6. 模型评估 ---
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ 训练完成！测试集准确率：{accuracy:.4f}")
print(classification_report(y_test, y_pred, target_names=['No Disease', 'Disease']))

# --- 7. 保存模型 ---
model.save_model(model_path)
print(f"💾 模型已保存：{model_path}")

# 保存元数据 (包含特征重要性，用于前端展示)
metadata = {
    "features": features,
    "accuracy": float(accuracy),
    "feature_importances": dict(zip(features, model.feature_importances_.tolist())),
    "column_mapping_note": "alco corresponds to alcohol consumption"
}

with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=4, ensure_ascii=False)

print(f"📝 元数据已保存：{meta_path}")
print("🎉 一切就绪！请运行 streamlit 查看效果。")