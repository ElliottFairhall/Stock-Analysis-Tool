from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from src.analysis import analyze_sentiment, calculate_volatility
from src.charts import (
    create_line_chart_figure,
    create_relative_returns_figure,
    create_sentiment_chart_figure,
)

# Import custom modules
from src.data import get_stock_data, get_stock_news

# Configuration
PAGE_TITLE = "Intelligence Flux: Finance Edition"
PAGE_ICON = ":chart_with_upwards_trend:"

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
)

# Project paths
CURRENT_DIR = Path(__file__).parent
CSS_FILE = CURRENT_DIR / "styles" / "main.css"
IMAGE_FILE = CURRENT_DIR / "assets" / "images" / "Finance.jpg"


def load_css(file_path: Path) -> None:
    if file_path.exists():
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        """
        <div class='header-container'>
            <h1 class='main-title'>Stock Intelligence Flux</h1>
            <p class='sub-title'>TRANSFORMING MARKET COMPLEXITY INTO CLARITY</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<h2 style='font-family:Outfit; margin-bottom:0;'>Data Engine</h2>",
            unsafe_allow_html=True,
        )
        st.caption("Configuring high-fidelity signals.")
        st.markdown("---")

        tickers = [
            "AAPL",
            "TSLA",
            "MSFT",
            "GOOGL",
            "AMZN",
            "META",
            "BABA",
            "WMT",
            "GE",
            "JPM",
            "TSM",
            "CMCSA",
            "CVX",
            "PG",
            "BA",
            "INTC",
            "CSCO",
            "PFE",
        ]
        selected = st.multiselect("Select Assets", tickers, default=["MSFT", "TSLA"])

        st.markdown("---")
        st.caption("Environment: Intelligence Flux V3.0")
        st.caption("Aesthetic: Soft Rose / Sky")
    return selected


def render_metrics(selected_tickers, stocks_df):
    if stocks_df is not None and not stocks_df.empty:
        cols = st.columns(len(selected_tickers))
        for i, ticker in enumerate(selected_tickers):
            if ticker in stocks_df.columns:
                latest_price = stocks_df[ticker]["Close"].iloc[-1]
                prev_price = stocks_df[ticker]["Close"].iloc[-2]
                delta = (latest_price - prev_price) / prev_price * 100
                cols[i % len(cols)].metric(
                    ticker, f"${latest_price:.2f}", f"{delta:.2f}%"
                )


def main():
    load_dotenv()
    load_css(CSS_FILE)
    render_header()

    selected_tickers = render_sidebar()

    if len(selected_tickers) < 2:
        st.warning("Please select at least 2 assets to initiate analysis.")
        return

    # Load data
    ticker_string = " ".join(selected_tickers)
    stocks_df = get_stock_data(ticker_string)

    if stocks_df is None or stocks_df.empty:
        st.error("Terminal Error: Could not synchronize with market data stream.")
        return

    # Layout
    tab1, tab2, tab3 = st.tabs(
        ["Project Overview", "Market Dynamics", "Sentiment Intelligence"]
    )

    with tab2:
        render_metrics(selected_tickers, stocks_df)
        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns([2, 1])

        fig_line = create_line_chart_figure(selected_tickers, stocks_df)
        if fig_line:
            st.plotly_chart(fig_line, width="stretch")

        st.markdown("---")

        st.markdown("### Risk Velocity (Volatility Analysis)")
        v_cols = st.columns(len(selected_tickers))
        for i, ticker in enumerate(selected_tickers):
            if ticker in stocks_df.columns:
                vol = calculate_volatility(stocks_df[ticker]["Close"])
                v_cols[i % len(v_cols)].metric(f"{ticker} Volatility", f"{vol:.2f}%")

        st.markdown("---")

        fig_returns = create_relative_returns_figure(selected_tickers, stocks_df)
        if fig_returns:
            st.plotly_chart(fig_returns, width="stretch")

    with tab3:
        st.markdown("### Neural Sentiment Stream")
        news_df = get_stock_news(selected_tickers)
        if not news_df.empty:
            sentiment_df = analyze_sentiment(news_df)

            fig_sentiment = create_sentiment_chart_figure(sentiment_df)
            if fig_sentiment:
                st.plotly_chart(fig_sentiment, width="stretch")

            st.markdown("#### Signal Intelligence Preview")
            st.dataframe(
                sentiment_df[["symbol", "title", "sentiment_score", "url"]].head(15),
                width="stretch",
            )
        else:
            st.info("Digital Silence: No recent signals found for selected assets.")

    with tab1:
        if IMAGE_FILE.exists():
            image = Image.open(IMAGE_FILE)
            st.image(image, width="stretch")

        st.markdown(
            """
        ### Strategic Overview
        This project showcases high-fidelity financial analysis techniques using Python.
        Utilizing `yfinance`, `Plotly`, `Streamlit`, and `VaderSentiment` to deconstruct market data and news cycles.

        ### Methodology
        - **Market Dynamics:** Historical price trends and realized volatility metrics.
        - **Sentiment Flux:** Natural Language Processing (NLP) applied to live news feeds for ticker-specific resonance.
        - **Aesthetic:** Driven by the Intelligence Flux design system (Soft Rose/Sky).
        """
        )


if __name__ == "__main__":
    main()
