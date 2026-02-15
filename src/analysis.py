import numpy as np


def calculate_volatility(stock_series):
    """
    Calculates annualized volatility for a stock series.

    Args:
        stock_series (pd.Series): Series of stock prices (Close).

    Returns:
        float: Annualized volatility as a percentage.
    """
    if stock_series.empty or len(stock_series) < 2:
        return 0.0

    returns = stock_series.pct_change()
    # Drop the first NaN value created by pct_change
    returns = returns.dropna()

    if returns.empty:
        return 0.0

    volatility = returns.std() * np.sqrt(252)
    volatility_pct = volatility * 100
    return volatility_pct


from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def analyze_sentiment(news_df):
    """
    Analyzes the sentiment of news headlines using VaderSentiment.

    Args:
        news_df (pd.DataFrame): DataFrame containing news with 'title' column.

    Returns:
        pd.DataFrame: news_df with added 'sentiment_score' column, or original df if empty.
    """
    if news_df is None or news_df.empty or "title" not in news_df.columns:
        return news_df

    analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(text):
        if not isinstance(text, str):
            return 0.0
        return analyzer.polarity_scores(text)["compound"]

    # Operate on a copy to avoid SettingWithCopy warnings if slice passed
    result_df = news_df.copy()
    result_df["sentiment_score"] = result_df["title"].apply(get_sentiment)

    return result_df
