import os
import os.path
import time

import pandas as pd
import yfinance as yf
from yfinance import exceptions


def need_get(df):
    for index, row in df.iterrows():
        mark = row["Mark"]
        if mark in (1, -1):
            continue
        stock_name = str(row["Stock_name"])
        print("now:", stock_name, " -- ", index + 1, r"/", len(df))
        df.at[index, 'Mark'] = get_price(stock_name)
        df.to_csv("lists/" + list_file_path, index=False)
        time.sleep(0.1)
        yield df


def get_price(ticker):
    # tickerStrings = ['AAPL', 'MSFT']
    attempts = 0
    while attempts < 3:
        try:
            timer = time.time()
            data = yf.download(
                ticker,
                start="2024-01-01",
                end="2026-01-31",
                progress=False,
                auto_adjust=False,
                threads=False,
            )
            if data is None or data.empty:
                raise exceptions.YFDataException("Empty data")
            os.makedirs("prices", exist_ok=True)
            data.to_csv("prices/" + ticker + ".csv")
            print("Used:", time.time() - timer)
            flag = 1
            return flag
        except (exceptions.YFDataException, exceptions.YFPricesMissingError, exceptions.YFTzMissingError):
            print("Failed to download")
            attempts += 1
            continue
        except Exception as exc:
            print("Failed to download:", exc)
            attempts += 1
            continue
    if attempts == 3:
        flag = -1
        return flag


if __name__ == "__main__":
    list_len = 0
    inits = input("from which lists:")
    # support ranges like a-z and ignore non-letters
    def expand_inits(text):
        cleaned = text.strip().lower()
        result = []
        i = 0
        while i < len(cleaned):
            ch = cleaned[i]
            if ch.isalpha():
                if i + 2 < len(cleaned) and cleaned[i + 1] in ("-", ":") and cleaned[i + 2].isalpha():
                    start = ord(ch)
                    end = ord(cleaned[i + 2])
                    step = 1 if start <= end else -1
                    result.extend([chr(c) for c in range(start, end + step, step)])
                    i += 3
                    continue
                result.append(ch)
            i += 1
        # de-duplicate while preserving order
        seen = set()
        deduped = []
        for ch in result:
            if ch not in seen:
                seen.add(ch)
                deduped.append(ch)
        return deduped

    for init in expand_inits(inits):
        list_file_path = 'list_' + init + '.csv'
        if not os.path.isfile("lists/" + list_file_path):
            print("skip missing:", list_file_path)
            continue
        list_df = pd.read_csv("lists/" + list_file_path, encoding="utf-8")
        list_len = list_len + len(list_df)
        while not list_df['Mark'].isin([1, -1]).all():
            print("need get")
            updated = False
            for updated_df in need_get(list_df):
                list_df = updated_df
                updated = True
                break
            if not updated:
                break
        print("list_", init, "completed", "len:", len(list_df))
    print("total:", list_len)
