import logging

import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_stock_data(ticker_string, period="2y"):
    """
    Downloads stock data for the given tickers.

    Args:
        ticker_string (str): Space-separated list of tickers.
        period (str): Period to download data for. Default is "2y".

    Returns:
        pd.DataFrame: DataFrame containing stock data, or None if error.
    """
    if not ticker_string or not ticker_string.strip():
        logger.error("No tickers provided to get_stock_data")
        return None

    try:
        logger.info(f"Downloading data for: {ticker_string}")
        stocks_df = yf.download(
            ticker_string, period=period, group_by="ticker", progress=False
        )

        if stocks_df is None:
            logger.error(f"yfinance returned None for tickers: {ticker_string}")
            return None

        if stocks_df.empty:
            logger.warning(
                f"yfinance returned empty DataFrame for tickers: {ticker_string}"
            )
            return None

        # Clean the data
        stocks_df.dropna(inplace=True)

        if stocks_df.empty:
            logger.warning(
                f"DataFrame is empty after dropping NaN values for: {ticker_string}"
            )
            return None

        logger.info(f"Successfully downloaded data for {ticker_string}")
        return stocks_df

    except Exception as e:
        logger.error(f"Error downloading data for {ticker_string}: {e!s}")
        return None


def get_stock_news(selected_tickers):
    """
    Fetches news for the selected tickers using yfinance.

    Args:
        selected_tickers (list): List of ticker symbols.

    Returns:
        pd.DataFrame: DataFrame containing news items, or empty DataFrame.
    """
    if not selected_tickers:
        logger.warning("No tickers provided to get_stock_news")
        return pd.DataFrame()

    news_data = []  # List to hold cleaned dicts
    failed_tickers = []

    for ticker in selected_tickers:
        try:
            logger.info(f"Fetching news for {ticker}")
            ticker_obj = yf.Ticker(ticker)

            if not hasattr(ticker_obj, "news"):
                logger.warning(f"Ticker {ticker} does not have news attribute")
                failed_tickers.append(ticker)
                continue

            ticker_news = ticker_obj.news

            if not ticker_news:
                logger.info(f"No news available for {ticker}")
                continue

            for item in ticker_news:
                # Handle nested content structure if present (new yfinance behavior)
                data = item.get("content", item)

                # Extract fields
                title = data.get("title")

                # Date handling
                published = data.get("pubDate") or data.get("providerPublishTime")

                # URL handling
                url = data.get("link")
                if not url:
                    click_through = data.get("clickThroughUrl")
                    if click_through and isinstance(click_through, dict):
                        url = click_through.get("url")
                if not url:
                    canonical = data.get("canonicalUrl")
                    if canonical and isinstance(canonical, dict):
                        url = canonical.get("url")

                if title:
                    news_data.append(
                        {
                            "symbol": ticker,
                            "title": title,
                            "publishedAt": published,
                            "url": url,
                        }
                    )

        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e!s}")
            failed_tickers.append(ticker)
            continue

    if failed_tickers:
        logger.warning(f"Failed to fetch news for: {', '.join(failed_tickers)}")

    if news_data:
        news_df = pd.DataFrame(news_data)

        # Clean timestamps
        if "publishedAt" in news_df.columns:
            # pubDate is often ISO string '2025-12-04T16:48:09Z'
            # providerPublishTime is often int timestamp
            # pd.to_datetime handles mixed reasonably well usually
            news_df["publishedAt"] = pd.to_datetime(
                news_df["publishedAt"], errors="coerce"
            )

        news_df.drop_duplicates(inplace=True)
        logger.info(f"Successfully fetched {len(news_df)} news items")
    else:
        logger.info("No news data retrieved for any ticker")
        news_df = pd.DataFrame()

    return news_df
