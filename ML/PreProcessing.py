import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer

def process_price_csv(file_path):
    """
    Reads a CSV file, imputes missing values using Random Forest, 
    and saves the result to 'price_processed.csv' in the same directory.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"\nProcessing: {file_path}")

    # Read the CSV file, skipping the first row as it contains the title
    df = pd.read_csv(file_path, header=1)

    # --- Data Cleaning ---

    # Columns to process
    # Note: The column names might vary slightly (e.g., year changes). 
    # We need to dynamically identify them or assume a consistent structure based on position if names change.
    # Based on the requirement "prices in january 25 , fill the with the help of the model", 
    # and previous file analysis, the columns are specific to the month.
    # However, for a batch script over different months, the column names will differ (e.g., "Prices February, 2025").
    # Strategy: Identify columns by index or keyword if possible, or strictly use the provided structure if it's consistent.
    # Let's inspect the column names dynamically.
    
    # Actually, the problem says "Missing data in the second column".
    # Let's verify the structure.
    # Col 0: Market
    # Col 1: Prices {Month}, {Year} (Target)
    # Col 2: Prices {PrevMonth}, {Year/PrevYear} (Feature 1)
    # Col 3: Prices {Month}, {PrevYear} (Feature 2)
    
    # We will use indices to be generic across months.
    target_col = df.columns[1]
    feature_cols = [df.columns[2], df.columns[3]]

    print(f"Target Column: {target_col}")
    print(f"Feature Columns: {feature_cols}")

    # Convert columns to numeric, coercing errors to NaN (handles '-')
    for col in [target_col] + feature_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- Imputation ---

    # 1. Prepare data for model training
    # Use SimpleImputer to fill missing values in FEATURE columns with mean
    if df[feature_cols].isnull().all().all():
         print("All feature values are missing. Cannot impute.")
         return

    imputer = SimpleImputer(strategy='mean')
    df[feature_cols] = imputer.fit_transform(df[feature_cols])

    # 2. Split data into sets with known and unknown target values
    known_target = df[df[target_col].notna()]
    unknown_target = df[df[target_col].isna()]

    if not unknown_target.empty:
        print(f"Found {len(unknown_target)} missing values in '{target_col}'. Imputing...")

        # 3. Train Random Forest model
        X_train = known_target[feature_cols]
        y_train = known_target[target_col]
        
        if X_train.empty:
             print("No training data available (all target values missing).")
             return

        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)

        # 4. Predict missing values
        X_predict = unknown_target[feature_cols]
        predicted_values = rf_model.predict(X_predict)

        # 5. Fill missing values in original dataframe
        df.loc[df[target_col].isna(), target_col] = predicted_values
        
    else:
        print(f"No missing values found in '{target_col}'.")

    # --- Save Processed Data ---
    output_dir = os.path.dirname(file_path)
    output_path = os.path.join(output_dir, "price_processed.csv")
    df.to_csv(output_path, index=False)
    print(f"Processed data saved to: {output_path}")


# --- Main Batch Execution ---

# Define the base directory relative to this script
script_dir = os.path.dirname(__file__)
base_dir = os.path.join(script_dir, "DataSet/Maharashtra/Wheat/2025")

# List of month directories (including identified typos)
months = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "Septemeber", "October", "Novemeber", "December"
]

print("Starting batch processing...")

for month in months:
    file_path = os.path.join(base_dir, month, "price.csv")
    process_price_csv(file_path)

print("\nBatch processing complete.")
