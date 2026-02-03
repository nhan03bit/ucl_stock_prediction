

# 📈 UCL Hackathon – NASDAQ News-Driven Stock Prediction
[![image.png](https://i.postimg.cc/50tkvp28/image.png)](https://postimg.cc/zL9jYCWf)

## 🧠 Project Overview

Financial markets are increasingly driven by *information flow* as much as historical price dynamics. News, macroeconomic announcements, and corporate disclosures can rapidly shift investor sentiment and market direction. This project was developed for the **UCL Hackathon** under the **UCL Data Science Society**, with the goal of building an **end-to-end, research-inspired stock prediction pipeline** that integrates:

* **NASDAQ market data**
* **Automated news scraping**
* **GPT-based sentiment analysis**
* **Deep learning models (CNN + LSTM)** for time-series forecasting

Our approach is motivated by recent academic work showing that **hybrid models combining sentiment features with historical price data consistently outperform pure price-based models**, particularly in volatile or news-driven markets.

---

## 🏗️ System Architecture

The full pipeline consists of four main stages:

1. **Market & News Data Collection**
2. **LLM-based Sentiment Extraction**
3. **Feature Engineering & Data Fusion**
4. **CNN-LSTM Prediction & Evaluation**

The following sections describe each stage in detail, with visual results integrated from our experiments.

---

## 📊 Market Data & News Collection

### 🔹 NASDAQ Market Activity
[![image.png](https://i.postimg.cc/Mpd7RwM4/image.png)](https://postimg.cc/pm55bgBY)


We collect historical price data for multiple NASDAQ-listed stocks and indices (e.g., COMP, NDX), including open, close, volume, and intraday trends. This provides the **core numerical time-series signal** used by the prediction models.

*Figure 1: NASDAQ market activity view used as reference for price movement alignment.*

### 🔹 News Scraping

Relevant financial news articles are scraped from NASDAQ-related sources and market news providers. For each article, we store:

* Headline
* Publication timestamp
* Source
* Full article text

This produces a continuously updating stream of **unstructured textual data**, which captures real-time market narratives not reflected immediately in price movements.

---

## 🧠 GPT-Based News Sentiment Analysis
[![image.png](https://i.postimg.cc/nrhkNLDY/image.png)](https://postimg.cc/0MhDwPZb)
To transform raw news text into actionable signals, we apply a **GPT-based large language model (LLM)** to each article. Unlike traditional lexicon-based sentiment methods, GPT allows:

* Context-aware sentiment interpretation
* Detection of implicit market signals (e.g., earnings surprise, regulatory risk)
* Reduction of noise from ambiguous financial language

Each article is mapped to a **numerical sentiment score**, which is later aggregated daily and aligned with price data.

---

## 🔧 Feature Engineering & Data Fusion

We merge sentiment features with historical price data using a shared daily timeline. Key steps include:

* Normalization and scaling of price features
* Rolling averages of sentiment scores
* Lagged sentiment variables (t-1, t-2, …)
* Sliding window construction for sequence models

This results in a unified multivariate time-series input suitable for deep learning.

---

## 🧠 Model Architecture: CNN + LSTM

### 🔹 Convolutional Neural Network (CNN)

The CNN layers extract **local temporal patterns** from short windows of price and sentiment data. This helps capture immediate market reactions to news events.

### 🔹 Long Short-Term Memory (LSTM)

The LSTM layers model **long-term dependencies** and trends in stock prices, enabling the network to learn broader market dynamics beyond short-term noise.

### 🔹 Hybrid Fusion

By combining CNN and LSTM, the model benefits from both:

* Short-term pattern detection (CNN)
* Long-term temporal reasoning (LSTM)

This design follows findings from recent studies showing improved robustness and predictive accuracy when CNN and LSTM are used together with external sentiment signals.

---

## 📈 Prediction Results & Visualisations

### 🔹 Stock Price Predictions

The plots below compare **actual vs. predicted prices** across multiple NASDAQ stocks. The close alignment demonstrates the model’s ability to track both trend and short-term fluctuations.



*Figure 2–4: Actual vs. predicted stock prices using the CNN-LSTM + GPT sentiment model.*
[![image.png](https://i.postimg.cc/9F1RgpmM/image.png)](https://postimg.cc/zVbGVTRZ)


---

### 🔹 Quantitative Evaluation Metrics

We evaluate performance using standard regression metrics across five stocks:

* **Mean Absolute Error (MAE)**
* **Mean Squared Error (MSE)**
* **R² Score**

[![image.png](https://i.postimg.cc/HLF74kpr/image.png)](https://postimg.cc/FfgRhmkv)

*Figure 5: MAE, MSE, and R² scores across five NASDAQ stocks.*

Results show consistently **low prediction error and strong explanatory power**, particularly when sentiment features are included.

---

## 🧪 Key Findings

* Integrating **GPT-based sentiment** improves prediction stability during volatile periods.
* CNN-LSTM hybrid models outperform standalone LSTM models on multi-stock datasets.
* News sentiment is especially effective at capturing **short-term market reactions**.

These findings align closely with recent academic research in financial deep learning, including studies published in *Nature Humanities and Social Sciences Communications*.

---

## 🎓 Hackathon Context

This project was built for the **UCL Hackathon**, organised in collaboration with the **UCL Data Science Society**. The aim was to demonstrate how **state-of-the-art AI methods** can be applied to real-world financial prediction problems under time and resource constraints.

---

## 🔗 References

* Nature Humanities & Social Sciences Communications (2025): Hybrid deep learning for stock prediction
* NASDAQ Market Activity Data
* GPT-based Large Language Models for Financial Sentiment Analysis

---

## 📜 License

MIT License
