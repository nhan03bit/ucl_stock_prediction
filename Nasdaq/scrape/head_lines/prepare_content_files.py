import os
import pandas as pd
from tqdm import tqdm

def prepare_content_files():
    """
    Read headlines/*.csv files, extract Date and URL columns,
    add Text and Mark columns, and save to news_content/contents/
    """
    
    # Create output directory if it doesn't exist
    os.makedirs('news_content/contents', exist_ok=True)
    
    # Get all CSV files in headlines directory
    headlines_dir = 'headlines'
    if not os.path.exists(headlines_dir):
        print(f"Error: {headlines_dir} directory not found")
        return
    
    csv_files = [f for f in os.listdir(headlines_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {headlines_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    
    processed = 0
    skipped = 0
    
    for csv_file in tqdm(csv_files, desc="Processing files"):
        try:
            # Read the headline CSV file
            input_path = os.path.join(headlines_dir, csv_file)
            df = pd.read_csv(input_path, encoding='utf-8-sig')
            
            # Check if required columns exist
            if 'Date' not in df.columns or 'URL' not in df.columns:
                print(f"Skipping {csv_file}: missing Date or URL column")
                skipped += 1
                continue
            
            # Create new dataframe with required columns
            content_df = pd.DataFrame({
                'Date': df['Date'],
                'URL': df['URL'],
                'Text': '',  # Empty text column to be filled by scraper
                'Mark': 0    # Mark as not processed (0)
            })
            
            # Save to news_content/contents directory
            output_path = os.path.join('contents', csv_file)
            content_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            processed += 1
            
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
            skipped += 1
            continue
    
    print(f"\nProcessing complete:")
    print(f"  Processed: {processed} files")
    print(f"  Skipped: {skipped} files")
    print(f"  Output directory: news_content/contents/")


if __name__ == "__main__":
    prepare_content_files()
