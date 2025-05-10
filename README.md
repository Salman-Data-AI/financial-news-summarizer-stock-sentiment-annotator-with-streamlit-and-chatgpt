# 📊 Financial News Summarizer & Stock Sentiment Annotator

A real-time **Streamlit dashboard** that scrapes the latest financial headlines from Yahoo Finance, summarizes full news articles using **ChatGPT (gpt-3.5-turbo)**, and extracts **stock-specific sentiment classifications** (bullish, bearish, or neutral). Ideal for finance professionals, NLP researchers, and anyone building explainable LLM-based tools.

## Architecture Diagram

![image](https://github.com/user-attachments/assets/b6cb42af-1440-4395-ad50-c1a1ca961de6)


## 🧠 What It Does

- 🔄 **Live news ingestion** from Yahoo Finance RSS
- 📰 **Full article parsing**, not just headlines
- ✍️ **2-line summary** of each article using ChatGPT
- 🏷 **Sentiment tagging per stock** mentioned (e.g., AAPL: bullish, TSLA: bearish)
- 📉 **Interactive bar chart** of sentiment distribution by stock
- 🎛️ **Dropdown filter** for bullish / bearish / neutral views
- 📁 **Downloadable CSV** of all processed data
- 🧮 **Token usage + cost estimator** for each API run

## ⚙️ How to Run

### 1. Clone the repo
```bash
git clone https://github.com/your-handle/financial-news-summarizer-stock-sentiment-annotator.git
cd financial-news-summarizer-stock-sentiment-annotator

streamlit run financial_news_summarizer.py


