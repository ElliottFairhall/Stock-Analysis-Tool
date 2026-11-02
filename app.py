"""Stock comparison: entry point."""

import logging

import streamlit as st
from dotenv import load_dotenv

from src.analysis import analyze_sentiment, close_prices, summary_table
from src.data import get_stock_data, get_stock_news
from src.ui import (
    PERIOD_PHRASE,
    render_analysis,
    render_config,
    render_footer,
    render_headlines,
    render_intro,
    render_prices,
    render_risk,
    render_sidebar,
    render_summary,
    render_topbar,
)
from src.universe import BENCHMARK_NAME, BENCHMARK_SYMBOL

logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Render the page. Everything updates as the controls change."""
    load_dotenv()
    render_config()
    render_topbar()

    tickers, period, indexed, benchmark = render_sidebar()
    if not tickers:
        st.title("Stock comparison")
        st.info("Choose at least one stock in the sidebar to begin.")
        render_footer()
        return

    wanted = [*tickers, BENCHMARK_SYMBOL] if benchmark else tickers
    stocks = get_stock_data(" ".join(wanted), period)
    closes = close_prices(stocks, wanted) if stocks is not None else None
    if closes is not None and BENCHMARK_SYMBOL in closes:
        closes = closes.rename(columns={BENCHMARK_SYMBOL: BENCHMARK_NAME})
    if closes is None or closes.empty:
        st.title("Stock comparison")
        st.error(
            "No price data came back for "
            + ", ".join(tickers)
            + ". Check the ticker symbols and your connection, then try again."
        )
        render_footer()
        return

    missing = [t for t in tickers if t not in closes.columns]
    render_intro(closes.index.max(), PERIOD_PHRASE[period])
    if missing:
        st.warning("No data found for: " + ", ".join(missing))

    summary = summary_table(closes)
    render_summary(summary)
    render_prices(closes, indexed)
    render_risk(summary)
    render_analysis(closes)
    news_for = [t for t in closes.columns if t != BENCHMARK_NAME]
    render_headlines(analyze_sentiment(get_stock_news(news_for)))
    render_footer()


if __name__ == "__main__":
    main()
