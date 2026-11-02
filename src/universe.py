"""A curated list of large companies: name, sector and website for logos."""

from __future__ import annotations

import base64

import pandas as pd

BENCHMARK_SYMBOL = "^GSPC"
BENCHMARK_NAME = "S&P 500"

# (ticker, company, sector, website domain)
_COMPANIES = [
    ("AAPL", "Apple", "Technology", "apple.com"),
    ("MSFT", "Microsoft", "Technology", "microsoft.com"),
    ("NVDA", "NVIDIA", "Technology", "nvidia.com"),
    ("AVGO", "Broadcom", "Technology", "broadcom.com"),
    ("ORCL", "Oracle", "Technology", "oracle.com"),
    ("CRM", "Salesforce", "Technology", "salesforce.com"),
    ("ADBE", "Adobe", "Technology", "adobe.com"),
    ("AMD", "AMD", "Technology", "amd.com"),
    ("INTC", "Intel", "Technology", "intel.com"),
    ("CSCO", "Cisco", "Technology", "cisco.com"),
    ("TSM", "TSMC", "Technology", "tsmc.com"),
    ("GOOGL", "Alphabet", "Communication Services", "google.com"),
    ("META", "Meta Platforms", "Communication Services", "meta.com"),
    ("NFLX", "Netflix", "Communication Services", "netflix.com"),
    ("DIS", "Disney", "Communication Services", "disney.com"),
    ("CMCSA", "Comcast", "Communication Services", "comcast.com"),
    ("AMZN", "Amazon", "Consumer Discretionary", "amazon.com"),
    ("TSLA", "Tesla", "Consumer Discretionary", "tesla.com"),
    ("HD", "Home Depot", "Consumer Discretionary", "homedepot.com"),
    ("MCD", "McDonald's", "Consumer Discretionary", "mcdonalds.com"),
    ("NKE", "Nike", "Consumer Discretionary", "nike.com"),
    ("BABA", "Alibaba", "Consumer Discretionary", "alibabagroup.com"),
    ("WMT", "Walmart", "Consumer Staples", "walmart.com"),
    ("COST", "Costco", "Consumer Staples", "costco.com"),
    ("PG", "Procter & Gamble", "Consumer Staples", "pg.com"),
    ("KO", "Coca-Cola", "Consumer Staples", "coca-colacompany.com"),
    ("PEP", "PepsiCo", "Consumer Staples", "pepsico.com"),
    ("JPM", "JPMorgan Chase", "Financials", "jpmorganchase.com"),
    ("BAC", "Bank of America", "Financials", "bankofamerica.com"),
    ("GS", "Goldman Sachs", "Financials", "goldmansachs.com"),
    ("V", "Visa", "Financials", "visa.com"),
    ("MA", "Mastercard", "Financials", "mastercard.com"),
    ("BRK-B", "Berkshire Hathaway", "Financials", "berkshirehathaway.com"),
    ("JNJ", "Johnson & Johnson", "Health Care", "jnj.com"),
    ("LLY", "Eli Lilly", "Health Care", "lilly.com"),
    ("UNH", "UnitedHealth", "Health Care", "unitedhealthgroup.com"),
    ("PFE", "Pfizer", "Health Care", "pfizer.com"),
    ("MRK", "Merck", "Health Care", "merck.com"),
    ("ABBV", "AbbVie", "Health Care", "abbvie.com"),
    ("XOM", "Exxon Mobil", "Energy", "exxonmobil.com"),
    ("CVX", "Chevron", "Energy", "chevron.com"),
    ("BA", "Boeing", "Industrials", "boeing.com"),
    ("GE", "GE Aerospace", "Industrials", "geaerospace.com"),
    ("CAT", "Caterpillar", "Industrials", "caterpillar.com"),
    ("UPS", "UPS", "Industrials", "ups.com"),
]

COMPANIES = pd.DataFrame(_COMPANIES, columns=["ticker", "name", "sector", "domain"])
SECTORS = sorted(COMPANIES["sector"].unique())
DEFAULT_TICKERS = ["MSFT", "TSLA"]
_BY_TICKER = COMPANIES.set_index("ticker")
LOGO_SIZE = 64


def stock_options(sectors: list[str] | None = None) -> list[str]:
    """List the tickers to offer, optionally limited to some sectors.

    Args:
        sectors: Sectors to keep. An empty list or None keeps everything.

    Returns:
        Tickers in alphabetical order of company name.
    """
    frame = COMPANIES
    if sectors:
        frame = frame[frame["sector"].isin(sectors)]
    return [str(ticker) for ticker in frame.sort_values("name")["ticker"]]


def company_name(ticker: str) -> str:
    """Return the company name for a ticker, or the ticker if it is unknown."""
    if ticker == BENCHMARK_NAME:
        return BENCHMARK_NAME
    return str(_BY_TICKER["name"].get(ticker, ticker))


def display_name(ticker: str) -> str:
    """Return ``"Microsoft (MSFT)"`` style text for pickers and tables."""
    name = company_name(ticker)
    return ticker if name == ticker else f"{name} ({ticker})"


def monogram(ticker: str) -> str:
    """Build a small rounded-square icon with a ticker's initials.

    Used when no company logo is known, so a table never shows a blank or
    broken image.

    Args:
        ticker: A ticker symbol or index name.

    Returns:
        An SVG data URI.
    """
    letters = "".join(ch for ch in ticker if ch.isalnum())[:2].upper() or "?"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">'
        '<rect width="64" height="64" rx="12" fill="#355C7D"/>'
        '<text x="32" y="41" font-family="Arial,sans-serif" font-size="26" '
        f'font-weight="700" text-anchor="middle" fill="#F9FAFB">{letters}</text>'
        "</svg>"
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def logo_url(ticker: str) -> str:
    """Return a logo image for a ticker.

    Known companies get the site icon served by Google's favicon service from
    the company's own domain (no API key needed). Anything else gets a
    monogram of its initials.

    Args:
        ticker: A stock ticker symbol or index name.

    Returns:
        An https URL, or an SVG data URI for unknown tickers.
    """
    if ticker not in _BY_TICKER.index:
        return monogram(ticker)
    domain = _BY_TICKER.loc[ticker, "domain"]
    return f"https://www.google.com/s2/favicons?domain={domain}&sz={LOGO_SIZE}"
