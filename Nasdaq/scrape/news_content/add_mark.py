import os

import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
lists_folder = os.path.join(script_dir, "lists")
lists_saving_folder = os.path.join(script_dir, "lists")
news_contents_folder = os.path.join(script_dir, "contents")
news_contents_saving_folder = os.path.join(script_dir, "contents")


# process lists
print("---Lists---")
list_files = [file for file in os.listdir(lists_folder) if file.endswith('.csv')]
for list_file in list_files:
    print(list_file)
    list_file_path = os.path.join(lists_folder, list_file)
    list_saving_path = os.path.join(lists_saving_folder, list_file)

    list_df = pd.read_csv(list_file_path, encoding="utf-8", on_bad_lines="skip")

    list_df.columns = list_df.columns.str.capitalize()
    list_df_filtered = list_df[["Stock_name"]]
    list_df_filtered["Mark"] = 0

    list_df_filtered.to_csv(list_saving_path, index=False)

# process new_content files
print("---News---")
news_content_files = [file for file in os.listdir(news_contents_folder) if file.endswith('.csv') and not file.startswith('list_')]
for news_content_file in news_content_files:
    print(news_content_file)
    news_content_file_path = os.path.join(news_contents_folder, news_content_file)
    news_content_saving_path = os.path.join(news_contents_saving_folder, news_content_file)
    try:
        news_content_df = pd.read_csv(news_content_file_path, encoding="utf-8", on_bad_lines="skip")
    except UnicodeDecodeError:
        news_content_df = pd.read_csv(news_content_file_path, encoding="ISO-8859-1", on_bad_lines="skip")

    print(f"  Columns: {news_content_df.columns.tolist()}")
    
    news_content_df.columns = news_content_df.columns.str.capitalize()
    news_content_df["Mark"] = 0
    news_content_df["Text"] = "0"
    
    # Find the URL column (case-insensitive)
    url_col = None
    date_col = None
    for col in news_content_df.columns:
        if col.lower() == 'url':
            url_col = col
        elif col.lower() == 'date':
            date_col = col
    
    print(f"  Found URL col: {url_col}, Date col: {date_col}")
    
    # Drop duplicates if URL column exists
    if url_col:
        news_content_df = news_content_df.drop_duplicates(subset=url_col)
    
    # Select only columns that exist
    cols_to_select = []
    if date_col:
        cols_to_select.append(date_col)
    if url_col:
        cols_to_select.append(url_col)
    cols_to_select.extend(["Text", "Mark"])
    
    news_content_df_filtered = news_content_df[cols_to_select]

    news_content_df_filtered.to_csv(news_content_saving_path, index=False)
