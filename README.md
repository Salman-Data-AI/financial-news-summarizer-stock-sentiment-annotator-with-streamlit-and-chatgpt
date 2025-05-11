# 📊 Financial News Summarizer & Stock Sentiment Annotator

A real-time **Streamlit dashboard** that scrapes the latest financial headlines from Yahoo Finance, summarizes full news articles using **ChatGPT (gpt-3.5-turbo)**, and extracts **stock-specific sentiment classifications** (bullish, bearish, or neutral). Ideal for finance professionals, NLP researchers, and anyone building explainable LLM-based tools.

## Architecture Diagram

![image](https://github.com/user-attachments/assets/b6cb42af-1440-4395-ad50-c1a1ca961de6)

## 🧠 What It Does

- 🏭 **Sector-level filter**: We can select which sector news we need to ingest before running the program
- 🧭 **Dashboard-based run**: Ability to trigger the program from the dashboard.
- 🔄 **Live news ingestion** from Yahoo Finance RSS and using BeautifulSoup
- 🌐 **Control number of Articles** we can pick the number of articles to be scraped
- 📰 **Full article parsing**, not just headlines
- ✍️ **2-line summary** of each article using ChatGPT
- 🏷 **Sentiment tagging per stock** mentioned (e.g., AAPL: bullish, TSLA: bearish). A single article can have mixed sentiment since it can mention multiple stocks. Thus, there will be separate records per stock.
- 📉 **Interactive bar chart** of sentiment distribution by stock
- 🎛️ **Dropdown filter** for bullish / bearish / neutral views
- 📁 **Downloadable CSV** of all processed data. Columns are date, headline, summary, stock, sentiment, url
- 🧮 **Token usage + cost estimator** for each API run

## 📊 Dashboard Sample

![image](https://github.com/user-attachments/assets/870b522f-3b9f-4d94-87cc-e5e57fdfe4e4)

## ⚙️ How to Run

### 1. Clone the repo
```bash
git clone https://github.com/your-handle/financial-news-summarizer-stock-sentiment-annotator.git

cd financial-news-summarizer-stock-sentiment-annotator

streamlit run financial_news_summarizer.py


