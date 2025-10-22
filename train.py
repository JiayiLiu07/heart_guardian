# 📁 train.py
import pandas as pd
import pickle
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import os
import json

# --- Paths and Directories ---
ASSETS_DIR = "./assets/"
RISK_MODEL_PATH = os.path.join(ASSETS_DIR, "xgb_risk.pkl")
SUBTYPE_MODELS_DIR = os.path.join(ASSETS_DIR, "subtype_models/")
RECIPE_POOL_PATH = os.path.join(ASSETS_DIR, "recipe_pool.json") # Keep recipe pool if it's needed

# --- Ensure Directories Exist ---
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)
if not os.path.exists(SUBTYPE_MODELS_DIR):
    os.makedirs(SUBTYPE_MODELS_DIR)

# --- Data Path ---
DATA_PATH = "data/cardio_train.csv"

# --- Import Disease Definitions ---
try:
    from utils.disease_dict import DISEASE_ENUM
except ImportError:
    print("Error: Could not import DISEASE_ENUM from utils.disease_dict. Please ensure the file exists.")
    # Define a fallback empty enum or exit if critical
    class DISEASE_ENUM: # Mock class if import fails
        @staticmethod
        def get_all_diseases(): return []
        @staticmethod
        def get_disease_keys(): return []
        @staticmethod
        def get_disease_labels(): return {}

# --- Data Loading Function ---
def load_data(filepath):
    """Loads data and performs initial preprocessing."""
    print(f"Loading data from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found at {filepath}")
    df = pd.read_csv(filepath)
    print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
    
    # --- Preprocessing Steps ---
    # Handle missing values (e.g., imputation)
    # df.fillna(value=..., inplace=True) 
    
    # Convert categorical features if necessary (e.g., one-hot encoding)
    # df['gender'] = df['gender'].apply(lambda x: 1 if x == 'Male' else 0) # Example
    
    # Ensure target variables are correctly represented (e.g., binary 0/1)
    # Example: Assume 'cardio' is the target for the main model.
    if 'cardio' in df.columns:
        df['cardio'] = df['cardio'].astype(int)

    # NOTE: For subtype models, you need to ensure that the DataFrame contains
    # target columns for each disease (e.g., 'hypertension', 'diabetes', etc.)
    # If these columns are not directly in cardio_train.csv, they need to be generated.
    # For example, creating binary flags based on thresholds or combinations of features.
    # Example: Generate a dummy 'hypertension' column if it doesn't exist
    # if 'hypertension' not in df.columns:
    #     print("Generating dummy 'hypertension' column...")
    #     # Replace with actual logic based on your data or definitions
    #     df['hypertension'] = ((df['ap_high'] > 140) | (df['ap_low'] > 90)).astype(int)

    return df

# --- Feature Engineering ---
def feature_engineering(df):
    """Performs feature engineering steps."""
    print("Performing feature engineering...")
    df['bmi'] = df['weight'] / ((df['height'] / 100)**2)
    df['gender'] = df['gender'].apply(lambda x: 1 if x == 'Male' else 0) # Assuming 'Male' is 1, 'Female' is 0
    # Add other engineered features here
    print("Feature engineering complete.")
    return df

# --- Train Risk Model ---
def train_risk_model(df):
    """Trains and saves the overall cardiovascular risk prediction model."""
    print("\n--- Training Overall Risk Model ---")
    if 'cardio' not in df.columns:
        raise ValueError("Target column 'cardio' not found in DataFrame.")
        
    X = df.drop('cardio', axis=1)
    y = df['cardio']

    # --- Feature Alignment ---
    # Ensure feature names and order are consistent.
    # You might need to load feature names from a saved file if they vary.
    # For now, assume X.columns is sufficient.
    print(f"Features used for risk model ({len(X.columns)}): {list(X.columns)}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Train set shape: {X_train.shape}, Test set shape: {X_test.shape}")

    # Initialize and train XGBoost model
    model = xgb.XGBClassifier(objective='binary:logistic',
                              eval_metric='logloss',
                              use_label_encoder=False, # Recommended for newer XGBoost versions
                              n_estimators=150,      # Example parameter
                              learning_rate=0.1,     # Example parameter
                              max_depth=4,           # Example parameter
                              random_state=42)
    print("Fitting risk model...")
    model.fit(X_train, y_train, early_stopping_rounds=10, eval_set=[(X_test, y_test)], verbose=False)
    print("Risk model trained.")

    # Save the trained model
    try:
        with open(RISK_MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        print(f"Overall risk model saved to: {RISK_MODEL_PATH}")
    except Exception as e:
        print(f"Error saving risk model: {e}")

    return model, X_test, y_test

# --- Train Subtype Models ---
def train_subtype_models(df):
    """Trains and saves 15 disease-specific subtype models."""
    print("\n--- Training Subtype Models ---")
    trained_models = {}

    # Iterate through all defined diseases in DISEASE_ENUM
    all_disease_enums = DISEASE_ENUM.get_all_diseases() # Assuming DISEASE_ENUM is an Enum-like structure
    if not all_disease_enums:
        print("No diseases defined in DISEASE_ENUM to train models for.")
        return {}

    for disease_enum in all_disease_enums:
        disease_key = disease_enum.name # e.g., "HYPERTENSION"
        # Assume your DataFrame has columns named after the lowercase disease keys
        # e.g., 'hypertension', 'diabetes' for the target variables.
        target_column_name = disease_enum.name.lower() 

        if target_column_name in df.columns:
            print(f"Training model for: {disease_key} ({target_column_name})")
            
            # Features (X) should exclude all target columns (including 'cardio' and all disease flags)
            # Ensure all disease flags are accounted for when defining features
            feature_columns = [col for col in df.columns if col not in [d.name.lower() for d in DISEASE_ENUM] and col != 'cardio']
            X = df[feature_columns]
            y = df[target_column_name].astype(int) # Ensure target is binary int

            # Align features for the subtype model (should ideally be the same as risk model)
            # If feature sets differ significantly, this needs careful handling.
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            print(f"  Train set shape: {X_train.shape}, Test set shape: {X_test.shape}")

            # Initialize and train XGBoost model
            model = xgb.XGBClassifier(objective='binary:logistic',
                                      eval_metric='logloss',
                                      use_label_encoder=False,
                                      n_estimators=100, # Potentially fewer estimators for subtype models
                                      learning_rate=0.05,
                                      max_depth=3,
                                      random_state=42)
            print(f"  Fitting model for {disease_key}...")
            model.fit(X_train, y_train, eval_set=[(X_test, y_test)], early_stopping_rounds=10, verbose=False)
            print(f"  Model for {disease_key} trained.")

            # Save the subtype model
            model_filename = f"{disease_key.lower()}.pkl"
            model_path = os.path.join(SUBTYPE_MODELS_DIR, model_filename)
            try:
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                print(f"  Subtype model saved to: {model_path}")
                trained_models[disease_key] = model # Add to returned dict
            except Exception as e:
                print(f"  Error saving subtype model {model_filename}: {e}")
        else:
            print(f"Warning: Target column '{target_column_name}' for disease '{disease_key}' not found in DataFrame. Skipping training.")
            
    if not trained_models:
        print("No subtype models were successfully trained or saved.")
    else:
        print(f"{len(trained_models)} subtype models trained and saved.")
    
    return trained_models

# --- Remove or Modify Visualization Generation ---
# The previous request was to remove specific PNGs. If any other visualizations
# are generated here (e.g., for model evaluation plots), they should be reviewed.
# We are NOT generating `corr_heatmap.png`, `global_shap.png`, etc.

def generate_visualizations(X_test, y_test, model, subtype_models, data):
    """
    Placeholder for any remaining visualization generation.
    If needed, add functions to save plots or return figure objects.
    This function is called from the main execution block.
    """
    print("\n--- Generating Visualizations ---")
    
    # Any new visualization tasks (e.g., plotting feature importance for the main model)
    # should be added here. For now, we are not generating any specific output files
    # as per the previous requirements.
    
    # Example: Save feature importances if desired
    # try:
    #     feature_importances = pd.Series(model.feature_importances_, index=X_test.columns)
    #     feature_importances.nlargest(10).plot(kind='barh')
    #     plt.title("Top 10 Features for Risk Model")
    #     plt.savefig(os.path.join(ASSETS_DIR, "risk_model_feature_importance.png"))
    #     print("Saved risk model feature importance plot.")
    # except Exception as e:
    #     print(f"Could not generate or save feature importance plot: {e}")
    
    # Load and save recipe pool (if it's part of training assets)
    if RECIPE_POOL_PATH:
        if os.path.exists(RECIPE_POOL_PATH):
            try:
                with open(RECIPE_POOL_PATH, 'r', encoding='utf-8') as f:
                    json.load(f) # Just load to check if valid
                print(f"Recipe pool file found and appears valid: {RECIPE_POOL_PATH}")
            except FileNotFoundError:
                print(f"Warning: Recipe pool file not found at {RECIPE_POOL_PATH}")
            except json.JSONDecodeError:
                print(f"Warning: Recipe pool file is not valid JSON: {RECIPE_POOL_PATH}")
            except Exception as e:
                print(f"Error checking recipe pool file: {e}")
        else:
            print(f"Warning: Recipe pool file does not exist: {RECIPE_POOL_PATH}")


# --- Main Execution Block ---
if __name__ == "__main__":
    print("Starting model training process...")

    # 1. Load and preprocess data
    try:
        df_processed = load_data(DATA_PATH)
        df_processed = feature_engineering(df_processed.copy()) # Work on a copy
        print("Data loaded and preprocessed.")
    except FileNotFoundError as e:
        print(f"ERROR: {e}. Please ensure '{DATA_PATH}' exists.")
        exit()
    except ValueError as e:
        print(f"ERROR: Data preprocessing failed: {e}")
        exit()
    except Exception as e:
        print(f"An unexpected error occurred during data loading/preprocessing: {e}")
        exit()

    # 2. Train Overall Risk Model
    risk_model = None
    X_test_risk, y_test_risk = None, None
    try:
        risk_model, X_test_risk, y_test_risk = train_risk_model(df_processed.copy()) # Use a copy
        print("Overall risk model training completed.")
    except Exception as e:
        print(f"ERROR: Failed to train risk model: {e}")

    # 3. Train Subtype Models
    subtype_models = {}
    if DISEASE_ENUM.get_all_diseases(): # Only proceed if diseases are defined
        try:
            subtype_models = train_subtype_models(df_processed.copy()) # Use a copy
            print(f"Subtype models training completed ({len(subtype_models)} models trained).")
        except Exception as e:
            print(f"ERROR: Failed to train subtype models: {e}")
    else:
        print("Skipping subtype model training as DISEASE_ENUM is empty or not properly defined.")

    # 4. Generate Visualizations (if any are needed)
    # We are intentionally NOT generating the specific PNGs mentioned earlier.
    # If other visualizations are desired, add calls here.
    generate_visualizations(X_test_risk, y_test_risk, risk_model, subtype_models, df_processed)

    print("\nModel training process finished.")