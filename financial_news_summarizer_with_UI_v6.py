import os
import feedparser
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from datetime import datetime
import pandas as pd
import time
import openai
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch
from matplotlib import style

# Set up OpenAI ChatGPT client
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-3.5-turbo"
COST_PER_1K_TOKENS = 0.0015

SECTOR_FEEDS = {
    "All": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US",
    "Technology": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,MSFT,NVDA,GOOG,AMZN&region=US&lang=en-US",
    "Healthcare": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=JNJ,MRK,PFE,UNH,ABBV&region=US&lang=en-US",
    "Finance": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=JPM,BAC,WFC,C,GS&region=US&lang=en-US",
    "Energy": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=XOM,CVX,SLB,BKR,HES&region=US&lang=en-US",
    "Consumer Goods": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=PG,KO,PEP,NKE,MCD&region=US&lang=en-US",
    "Industrial": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=HON,GE,MMM,CAT,BA&region=US&lang=en-US",
    "Utilities": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=NEE,DUK,SO,D,EXC&region=US&lang=en-US"
}

plt.style.use('dark_background')

# Utility Functions
def fetch_rss_entries(feed_url):
    feed = feedparser.parse(feed_url)
    entries = [(entry.title, entry.link) for entry in feed.entries]
    return entries

def fetch_article_content(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as response:
            soup = BeautifulSoup(response.read(), 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join(p.get_text() for p in paragraphs)
        return text.strip()[:3000]
    except Exception as e:
        return f"Error fetching article: {e}"

def analyze_article_with_chatgpt(headline, article):
    prompt = (
        f"""
        Headline: {headline}

        Article:
        {article}

        Summarize the article in 3 or 4 lines. 
        The summary must include what the article is about, what its conclusion is and how it arrived at the conclusion.
        Then list the sentiment (bullish, bearish, or neutral) for each stock or company mentioned in the article.

        Respond in this format exactly:
        Summary: <summary>
        Sentiments:
        <Stock1>: <sentiment>
        <Stock2>: <sentiment>
        (If no specific stock is mentioned, just write 'general: <sentiment>')
        """
    )
    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300
        )
        return response.choices[0].message.content.strip(), len(prompt) / 4 + 300
    except Exception as e:
        return f"Error: {e}", 0

def parse_response(response_text):
    summary = ""
    sentiments = []
    lines = response_text.splitlines()
    for line in lines:
        if 'summary:' in line.lower():
            summary = line.split(":", 1)[-1].strip()
        elif ':' in line and not line.lower().startswith('summary'):
            parts = line.split(":", 1)
            stock = parts[0].strip()
            sentiment = parts[1].strip().lower()
            sentiments.append((stock, sentiment))
    return summary, sentiments

# Streamlit UI
st.set_page_config(page_title="Financial News Analyzer", layout="wide")
st.title("📊 Financial News Summarizer with ChatGPT")

# Session state to persist data
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

sector_choice = st.selectbox("Choose Sector", list(SECTOR_FEEDS.keys()))
article_limit = st.slider("Limit number of articles", min_value=1, max_value=40, value=5)

if st.button("Fetch and Analyze News"):
    with st.spinner("Fetching and summarizing news articles..."):
        entries = fetch_rss_entries(SECTOR_FEEDS[sector_choice])[:article_limit]
        results = []
        total_tokens = 0

        for i, (headline, link) in enumerate(entries):
            article = fetch_article_content(link)
            gpt_response, tokens_used = analyze_article_with_chatgpt(headline, article)
            summary, sentiment_pairs = parse_response(gpt_response)
            total_tokens += tokens_used

            for stock, sentiment in sentiment_pairs:
                results.append({
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "headline": headline,
                    "summary": summary,
                    "instrument": stock,
                    "sentiment": sentiment,
                    "url": link
                })
            time.sleep(1.5)

        df = pd.DataFrame(results)
        df = df[df["instrument"].str.lower() != "sentiments"]
        df.to_csv("financial_news_summary_ChatGPT_with_UI.csv", index=False)
        st.session_state.df = df

        estimated_cost = (total_tokens / 1000) * COST_PER_1K_TOKENS
        st.success("Analysis complete! CSV saved as 'financial_news_summary_ChatGPT_with_UI.csv'")
        st.info(f"🧮 Estimated tokens used: {int(total_tokens)} | 💵 Prompting cost: ${estimated_cost:.4f}")

if not st.session_state.df.empty:
    df = st.session_state.df

    st.subheader("📈 Sentiment Filter and Summary Table")
    selected_sentiment = st.selectbox("Filter by Sentiment", ["all", "bullish", "bearish", "neutral"])

    if selected_sentiment != "all":
        filtered_df = df[df['sentiment'] == selected_sentiment]
    else:
        filtered_df = df

    selected_instrument = st.selectbox("Filter by Instrument", ["all"] + sorted(df['instrument'].unique()))
    if selected_instrument != "all":
        filtered_df = filtered_df[filtered_df['instrument'] == selected_instrument]

    st.dataframe(filtered_df)

    st.subheader("📈 Sentiment Distribution by Instrument")
    if not df.empty:
        sentiment_counts = df.groupby(['instrument', 'sentiment']).size().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#1a1a1a')

        color_map = {'bullish': '#2ca02c', 'neutral': '#ff7f0e', 'bearish': '#d62728'}
        bar_containers = []

        for i, sentiment in enumerate(sentiment_counts.columns):
            values = sentiment_counts[sentiment].values
            bars = ax.bar(
                sentiment_counts.index,
                values,
                width=0.6,
                label=sentiment,
                color=color_map.get(sentiment, 'gray'),
                edgecolor='black'
            )
            bar_containers.append(bars)
            for bar in bars:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    f'{int(bar.get_height())}',
                    ha='center', va='bottom',
                    color='white', fontsize=8, fontweight='bold'
                )

        ax.set_xlabel("Instrument", fontsize=10, fontweight='bold', color='white')
        ax.set_ylabel("Number of Articles", fontsize=10, fontweight='bold', color='white')
        ax.set_title("Sentiment Breakdown by Instrument", fontsize=12, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.grid(True, linestyle='--', linewidth=0.4, color='#444', axis='y')
        ax.legend(title="Sentiment", title_fontsize=9, fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)


