import pandas as pd
import os

def create_main_csv():
    # Define the dataset directory relative to this script
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "DataSet")
    
    print(f"\nAggregating data from {dataset_dir}...")
    
    data_rows = []

    # Walk through the directory structure
    for root, dirs, files in os.walk(dataset_dir):
        if "price_processed.csv" in files:
            file_path = os.path.join(root, "price_processed.csv")
            
            # Extract metadata from path
            # Structure: .../DataSet/{State}/{Commodity}/{Year}/{Month}/price_processed.csv
            try:
                # Get relative path from dataset_dir to handle varying absolute paths
                rel_path = os.path.relpath(root, dataset_dir)
                path_parts = rel_path.split(os.sep)
                
                # We expect at least 4 parts: State, Commodity, Year, Month
                # Example: Maharashtra/Wheat/2025/January
                if len(path_parts) >= 4:
                    state = path_parts[0]
                    commodity = path_parts[1] 
                    year = path_parts[2]
                    month = path_parts[3]

                    # Filter out placeholder directories
                    if commodity.lower().startswith("commodity"):
                        continue
                    
                    df = pd.read_csv(file_path)
                    
                    # Ensure expected columns exist (Market is col 0, Current is 1, Previous is 2)
                    if len(df.columns) >= 3:
                         market_col = df.columns[0]
                         current_price_col = df.columns[1]
                         prev_price_col = df.columns[2]
                         
                         for _, row in df.iterrows():
                             data_rows.append({
                                 "Commodity": commodity,
                                 "State": state,
                                 "Market": row[market_col],
                                 "Year": year,
                                 "Month": month,
                                 "Current Month Price": row[current_price_col],
                                 "Previous Month Price": row[prev_price_col]
                             })
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    # Create DataFrame and save
    if data_rows:
        # Define column order with Commodity first
        columns = ["Commodity", "State", "Market", "Year", "Month", "Current Month Price", "Previous Month Price"]
        main_df = pd.DataFrame(data_rows, columns=columns)
        
        output_path = os.path.join(dataset_dir, "main.csv")
        main_df.to_csv(output_path, index=False)
        print(f"\nSuccessfully created main.csv at {output_path}")
        print("First 5 rows:")
        print(main_df.head())
        print(f"\nTotal rows: {len(main_df)}")
    else:
        print("\nNo data found to aggregate.")

if __name__ == "__main__":
    create_main_csv()
