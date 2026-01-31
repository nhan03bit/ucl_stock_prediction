import os
import pandas as pd
from tqdm import tqdm

script_dir = os.path.dirname(os.path.abspath(__file__))
contents_dir = os.path.join(script_dir, "contents")

def clean_csv_file(file_path):
    """Remove empty rows from CSV file."""
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="ISO-8859-1")
    
    original_rows = len(df)
    
    # Remove rows where all values are NaN or empty strings
    df = df.dropna(how='all')
    df = df[~(df.astype(str).apply(lambda x: x.str.strip() == '').all(axis=1))]
    
    cleaned_rows = len(df)
    removed_rows = original_rows - cleaned_rows
    
    if removed_rows > 0:
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return removed_rows
    return 0

def clean_all_csv_files():
    """Clean all CSV files in contents directory."""
    if not os.path.exists(contents_dir):
        print(f"Directory not found: {contents_dir}")
        return
    
    csv_files = [f for f in os.listdir(contents_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in contents directory")
        return
    
    print(f"Found {len(csv_files)} CSV files to clean...")
    
    total_removed = 0
    files_cleaned = 0
    
    for csv_file in tqdm(csv_files, desc="Cleaning CSV files"):
        file_path = os.path.join(contents_dir, csv_file)
        removed = clean_csv_file(file_path)
        if removed > 0:
            total_removed += removed
            files_cleaned += 1
    
    print(f"\nCleaning complete:")
    print(f"  Files processed: {len(csv_files)}")
    print(f"  Files cleaned: {files_cleaned}")
    print(f"  Total empty rows removed: {total_removed}")

if __name__ == "__main__":
    clean_all_csv_files()
