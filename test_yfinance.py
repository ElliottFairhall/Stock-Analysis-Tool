"""
Test script to debug yfinance data download issues.

Run this to verify yfinance is working correctly:
    python test_yfinance.py
"""

import logging

import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_single_ticker():
    """Test downloading a single ticker."""
    logger.info("Testing single ticker download...")
    try:
        ticker = "MSFT"
        data = yf.download(ticker, period="5d", progress=False)
        logger.info(f"Single ticker result type: {type(data)}")
        logger.info(
            f"Single ticker shape: {data.shape if data is not None else 'None'}"
        )
        cols = data.columns.tolist() if data is not None else "None"
        logger.info(f"Single ticker columns: {cols}")
        if data is not None and not data.empty:
            logger.info("✓ Single ticker download successful")
            return True
        else:
            logger.error("✗ Single ticker download failed")
            return False
    except Exception as e:
        logger.error(f"✗ Single ticker download error: {e}")
        return False


def test_multiple_tickers():
    """Test downloading multiple tickers."""
    logger.info("\nTesting multiple ticker download...")
    try:
        tickers = "MSFT TSLA"
        data = yf.download(tickers, period="5d", group_by="ticker", progress=False)
        logger.info(f"Multiple ticker result type: {type(data)}")
        logger.info(
            f"Multiple ticker shape: {data.shape if data is not None else 'None'}"
        )
        cols = data.columns.tolist()[:10] if data is not None else "None"
        logger.info(f"Multiple ticker columns (first level): {cols}")

        if data is not None and not data.empty:
            logger.info("✓ Multiple ticker download successful")

            # Test accessing individual ticker data
            try:
                if "MSFT" in data.columns:
                    msft_data = data["MSFT"]
                    logger.info(f"  MSFT data shape: {msft_data.shape}")
                    logger.info(f"  MSFT columns: {msft_data.columns.tolist()}")
                    if "Close" in msft_data.columns:
                        logger.info(
                            f"  MSFT latest close: ${msft_data['Close'].iloc[-1]:.2f}"
                        )
                        logger.info("✓ Can access MSFT ticker data")
                    else:
                        logger.error("✗ 'Close' column not found in MSFT data")
                else:
                    logger.error("✗ 'MSFT' not found in columns")
                    logger.info(f"Available columns: {data.columns.tolist()}")
            except Exception as e:
                logger.error(f"✗ Error accessing ticker data: {e}")
                return False

            return True
        else:
            logger.error("✗ Multiple ticker download failed")
            return False
    except Exception as e:
        logger.error(f"✗ Multiple ticker download error: {e}")
        return False


def test_news_api():
    """Test fetching news for a ticker."""
    logger.info("\nTesting news API...")
    try:
        ticker = yf.Ticker("MSFT")
        news = ticker.news
        logger.info(f"News result type: {type(news)}")
        logger.info(f"Number of news items: {len(news) if news else 0}")

        if news:
            logger.info("✓ News API working")
            logger.info(f"  Sample news item keys: {list(news[0].keys())[:5]}")
            return True
        else:
            logger.warning("⚠ News API returned no results (might be normal)")
            return True
    except Exception as e:
        logger.error(f"✗ News API error: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("YFinance Diagnostic Test")
    logger.info("=" * 60)

    results = {
        "Single Ticker": test_single_ticker(),
        "Multiple Tickers": test_multiple_tickers(),
        "News API": test_news_api(),
    }

    logger.info("\n" + "=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{test_name}: {status}")

    all_passed = all(results.values())
    if all_passed:
        logger.info("\n🎉 All tests passed!")
    else:
        logger.error("\n❌ Some tests failed. Check the logs above for details.")
