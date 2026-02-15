import pandas as pd
import yfinance as yf


def get_stock_data(ticker_string, period="2y"):
    """
    Downloads stock data for the given tickers.

    Args:
        ticker_string (str): Space-separated list of tickers.
        period (str): Period to download data for. Default is "2y".

    Returns:
        pd.DataFrame: DataFrame containing stock data, or None if error.
    """
    try:
        stocks_df = yf.download(ticker_string, period=period, group_by="ticker")
        # Clean the data
        if not stocks_df.empty:
            stocks_df.dropna(inplace=True)
        return stocks_df
    except Exception as e:
        # In a real app we might want to log this instead of printing to streamlit immediately,
        # but preserving original behavior for now or returning None to let caller handle it.
        print(f"Error downloading data: {e}")
        return None


def get_stock_news(selected_tickers):
    """
    Fetches news for the selected tickers.

    Args:
        selected_tickers (list): List of ticker symbols.

    Returns:
        pd.DataFrame: DataFrame containing news items, or empty DataFrame.
    """
    news_data = []  # List to hold cleaned dicts
    for ticker in selected_tickers:
        try:
            ticker_news = yf.Ticker(ticker).news
            if ticker_news:
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
            print(f"Error fetching news for {ticker}: {e}")
            continue

    if news_data:
        news_df = pd.DataFrame(news_data)

        # Clean timestamps
        if "publishedAt" in news_df.columns:
            # pubDate is often ISO string '2025-12-04T16:48:09Z'
            # providerPublishTime is often int timestamp
            # pd.to_datetime handles mixed reasonably well usually, or we can explicit convert
            news_df["publishedAt"] = pd.to_datetime(
                news_df["publishedAt"], errors="coerce"
            )

        news_df.drop_duplicates(inplace=True)

    else:
        news_df = pd.DataFrame()

    return news_df
