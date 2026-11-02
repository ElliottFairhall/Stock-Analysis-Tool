"""Price statistics and headline sentiment for the stock comparison."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

TRADING_DAYS = 252
NEUTRAL_BAND = 0.05

# VADER is trained on general text. These words mean something specific in
# market news, so they are added to its lexicon (scale -4 to +4).
FINANCE_LEXICON = {
    "beats": 1.8,
    "beat": 1.5,
    "surge": 2.0,
    "surges": 2.0,
    "soar": 2.2,
    "soars": 2.2,
    "rally": 1.8,
    "upgrade": 1.8,
    "upgraded": 1.8,
    "outperform": 1.8,
    "strong": 1.5,
    "growth": 1.2,
    "profit": 1.2,
    "profits": 1.2,
    "misses": -1.8,
    "miss": -1.5,
    "plunge": -2.2,
    "plunges": -2.2,
    "tumble": -2.0,
    "slump": -2.0,
    "downgrade": -1.8,
    "downgraded": -1.8,
    "underperform": -1.8,
    "lawsuit": -1.8,
    "probe": -1.5,
    "recall": -1.6,
    "bankruptcy": -3.0,
    "layoffs": -1.8,
    "fraud": -3.0,
    "weak": -1.5,
    "losses": -1.8,
}
SPARKLINE_POINTS = 60


def close_prices(stocks_df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """Pull the closing price of each ticker into one frame.

    Args:
        stocks_df: Frame from yfinance with ``(ticker, field)`` columns.
        tickers: Tickers to include, in display order.

    Returns:
        One column per ticker that has data. Tickers with no data are left out.
    """
    columns = {}
    for ticker in tickers:
        if ticker in stocks_df.columns.get_level_values(0):
            series = stocks_df[ticker]["Close"].dropna()
            if not series.empty:
                columns[ticker] = series
    return pd.DataFrame(columns)


def rebase(closes: pd.DataFrame) -> pd.DataFrame:
    """Rescale each column so its first price is 100.

    Args:
        closes: Frame from :func:`close_prices`.

    Returns:
        The same shape, with every series starting at 100.
    """
    first = closes.apply(lambda col: col.dropna().iloc[0])
    return closes / first * 100


def calculate_volatility(stock_series: pd.Series) -> float:
    """Annualised volatility of daily returns, as a percentage.

    Args:
        stock_series: Closing prices.

    Returns:
        Volatility in percent, or 0.0 when there are fewer than two prices.
    """
    returns = stock_series.pct_change().dropna()
    if len(returns) < 1:
        return 0.0
    return float(returns.std() * np.sqrt(TRADING_DAYS) * 100)


def max_drawdown(stock_series: pd.Series) -> float:
    """Largest peak-to-trough fall, as a negative percentage.

    Args:
        stock_series: Closing prices.

    Returns:
        The worst fall from a previous high, for example ``-32.5``.
    """
    if stock_series.empty:
        return 0.0
    running_peak = stock_series.cummax()
    return float(((stock_series / running_peak) - 1).min() * 100)


def summary_table(closes: pd.DataFrame) -> pd.DataFrame:
    """Build one row of headline statistics per ticker.

    Args:
        closes: Frame from :func:`close_prices`.

    Returns:
        Columns: Ticker, Price, Day, Return, Volatility, Drawdown and Trend
        (the recent prices, for a sparkline).
    """
    rows = []
    for ticker in closes.columns:
        series = closes[ticker].dropna()
        day = series.pct_change().iloc[-1] * 100 if len(series) > 1 else 0.0
        rows.append(
            {
                "Ticker": ticker,
                "Price": float(series.iloc[-1]),
                "Day": float(day),
                "Return": float((series.iloc[-1] / series.iloc[0] - 1) * 100),
                "Volatility": calculate_volatility(series),
                "Drawdown": max_drawdown(series),
                "Trend": series.tail(SPARKLINE_POINTS).tolist(),
            }
        )
    return pd.DataFrame(rows)


@lru_cache(maxsize=1)
def _analyzer() -> SentimentIntensityAnalyzer:
    """Build the VADER analyser once, with the finance words added."""
    analyzer = SentimentIntensityAnalyzer()
    analyzer.lexicon.update(FINANCE_LEXICON)
    return analyzer


def tone(score: float) -> str:
    """Label a sentiment score as Positive, Neutral or Negative.

    Args:
        score: A compound score between -1 and 1.

    Returns:
        ``"Positive"`` above the neutral band, ``"Negative"`` below it,
        otherwise ``"Neutral"``.
    """
    if score > NEUTRAL_BAND:
        return "Positive"
    if score < -NEUTRAL_BAND:
        return "Negative"
    return "Neutral"


def score_text(text: str) -> float:
    """Score one piece of text from -1 (negative) to +1 (positive).

    Args:
        text: A headline or sentence.

    Returns:
        VADER's compound sentiment score.
    """
    if not isinstance(text, str) or not text.strip():
        return 0.0
    return float(_analyzer().polarity_scores(text)["compound"])


def analyze_sentiment(news_df: pd.DataFrame) -> pd.DataFrame:
    """Add a ``sentiment_score`` column to a frame of headlines.

    Args:
        news_df: Frame with a ``title`` column.

    Returns:
        A copy with the score added, or the input unchanged if it has no titles.
    """
    if news_df is None or news_df.empty or "title" not in news_df.columns:
        return news_df
    analyzer = _analyzer()
    result = news_df.copy()
    result["sentiment_score"] = [
        analyzer.polarity_scores(t)["compound"] if isinstance(t, str) else 0.0
        for t in result["title"]
    ]
    result["tone"] = result["sentiment_score"].map(tone)
    return result


def daily_returns(closes: pd.DataFrame) -> pd.DataFrame:
    """Day-on-day percentage change of each ticker.

    Args:
        closes: Frame from :func:`close_prices`.

    Returns:
        Daily returns in percent, with the first (empty) row dropped.
    """
    return closes.pct_change().dropna(how="all") * 100


def drawdown_series(closes: pd.DataFrame) -> pd.DataFrame:
    """How far each ticker sits below its previous high, in percent.

    Args:
        closes: Frame from :func:`close_prices`.

    Returns:
        Values of zero or below; zero means a new high.
    """
    return (closes / closes.cummax() - 1) * 100


def rolling_volatility(closes: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """Annualised volatility over a moving window of trading days.

    Args:
        closes: Frame from :func:`close_prices`.
        window: Number of trading days in each window.

    Returns:
        Volatility in percent; the first ``window`` rows are empty.
    """
    returns = closes.pct_change()
    return returns.rolling(window).std() * np.sqrt(TRADING_DAYS) * 100


def return_correlation(closes: pd.DataFrame) -> pd.DataFrame:
    """Correlation of daily returns between every pair of tickers.

    Args:
        closes: Frame from :func:`close_prices`.

    Returns:
        A square frame of values between -1 and 1.
    """
    return closes.pct_change().dropna(how="all").corr()
