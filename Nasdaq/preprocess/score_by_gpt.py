import os
import time

import numpy as np
import pandas as pd
import openai
from openai import OpenAI


import os
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_sentiment(symbol, *texts):
    # Build text content
    texts = [text for text in texts if text != 0]
    num_text = len(texts)
    # print(num_text)
    text_content = " ".join([f"### News to Stock Symbol -- {symbol}: {text}" for text in texts])
    # print(text_content)

    # Define conversation
    conversation = [
        {"role": "system",
         "content": f"Forget all your previous instructions. You are a financial expert with stock recommendation experience. Based on a specific stock, score for range from 1 to 5, where 1 is negative, 2 is somewhat negative, 3 is neutral, 4 is somewhat positive, 5 is positive. {num_text} summerized news will be passed in each time, you will give score in format as shown below in the response from assistant."},
        {"role": "user",
         "content": f"News to Stock Symbol -- AAPL: Apple (AAPL) increase 22% ### News to Stock Symbol -- AAPL: Apple (AAPL) price decreased 30% ### News to Stock Symbol -- MSFT: Microsoft (MSTF) price has no change"},
        {"role": "assistant", "content": "5, 1, 3"},
        {"role": "user",
         "content": f"News to Stock Symbol -- AAPL: Apple (AAPL) announced iPhone 15 ### News to Stock Symbol -- AAPL: Apple (AAPL) will release VisonPro on Feb 2, 2024"},
        {"role": "assistant", "content": "4, 4"},
        {"role": "user", "content": text_content},
    ]
    # print(conversation)
    sentiments = []
    # Make API call
    # Originally was client
    try:
        # response = openai.ChatCompletion.create(
        #     engine="gpt-35-turbo",
        #     messages=conversation,
        #     temperature=0,
        #     max_tokens=50,
        # )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0,
            max_tokens=50,
        )

        # Print assistant's response
        content = response.choices[0].message.content
        print(content)
    except AttributeError:
        print("response error")
        sentiment_value = np.nan
        sentiments.append(sentiment_value)
        return sentiments
    except openai.error.InvalidRequestError:
        print("response error")
        sentiment_value = np.nan
        sentiments.append(sentiment_value)
        return sentiments
    except openai.error.RateLimitError:
        print("openai error")
        sentiment_value = np.nan
        sentiments.append(sentiment_value)
        return sentiments
    # Process sentiment scores
    # sentiments = [int(sentiment.strip()) for sentiment in content.split(',')]

    for sentiment in content.split(','):
        try:
            sentiment_value = int(sentiment.strip())
        except ValueError:
            print("content error")
            sentiment_value = np.nan
        sentiments.append(sentiment_value)
    return sentiments


def from_csv_get_sentiment(df, symbol, saving_path, batch_size=4):
    # Sort so unprocessed data appears at bottom
    df.sort_values(by='Sentiment_gpt', ascending=False, na_position='last', inplace=True)
    if 'New_text' in df.columns:
        # If exists, rename column
        df.rename(columns={'New_text': 'Lsa_summary'}, inplace=True)
    for i in range(0, len(df), batch_size):
        # Check if each row has been processed
        # Skip already processed rows (None)
        if df.loc[i:min(i + batch_size - 1, len(df) - 1), 'Sentiment_gpt'].notna().all():
            # print("Processed")
            continue
        print("Now row: ", i)
        texts = [df.loc[j, 'Lsa_summary'] if j < len(df) else 0 for j in range(i, i + batch_size)]
        sentiments = get_sentiment(symbol, *texts)

        for k, sentiment in enumerate(sentiments):
            if i + k < len(df):
                df.loc[i + k, 'Sentiment_gpt'] = sentiment
        df_filtered = df[["Date", "Url", "Sentiment_gpt"]].copy()
        df_filtered.sort_values(by='Sentiment_gpt', ascending=False, na_position='last', inplace=True)
        df_filtered.to_csv(saving_path, index=False)
    return df


def reproduce(folder_path, name, saving_path, batch_size):
    print(name)
    a = time.time()
    file_path = os.path.join(folder_path, name+".csv")
    print(file_path)

    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="ISO-8859-1")
    symbol = name
    df.columns = df.columns.str.capitalize()
    # Ensure sentiment_gpt column exists
    if 'Sentiment_gpt' not in df.columns:
        df['Sentiment_gpt'] = np.nan

    if df['Sentiment_gpt'].isnull().any():
        # Reset batch_size
        batch_size_process = batch_size
        while batch_size_process > 0:
            print("Now Batch_size:", batch_size_process)
            df = from_csv_get_sentiment(df, symbol, os.path.join(saving_path, name+".csv"), batch_size_process)
            batch_size_process -= 1
            print(f"Processed {name} in {time.time() - a:.2f} seconds.")
            if df['Sentiment_gpt'].isnull().any():
                print("Unfinished:", name)
            else:
                print('Finished:', name)
                break
    else:
        print("Finished:", name)


if __name__ == "__main__":
    news_folder_path = "news_data_summarized"
    news_saving_path = "news_data_sentiment_scored_by_gpt"
    #
    # # # Method 1
    # # news_files = [file for file in os.listdir(news_folder_path) if file.endswith('.csv')]
    # # for news_file in news_files:
    # #     name = news_file.split(".")[0]
    # #     reproduce(news_folder_path, name, news_saving_path, batch_size=5)
    #
    # Method 2
    name = input("input as AAPL: ")
    reproduce(news_folder_path, name, news_saving_path, batch_size=5)
