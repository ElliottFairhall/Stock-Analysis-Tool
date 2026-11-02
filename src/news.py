"""Fetch and filter stock headlines from Yahoo Finance's public RSS feed.

yfinance's ``Ticker.news`` currently returns nothing, but Yahoo still publishes
an RSS feed per symbol that needs no key. Feeds also include articles that
merely mention a symbol, so headlines are filtered for relevance.
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

import pandas as pd
import requests
from defusedxml import DefusedXmlException, ElementTree

from src.universe import company_name

logger = logging.getLogger(__name__)

RSS_URL = "https://feeds.finance.yahoo.com/rss/2.0/headline"
TIMEOUT_SECONDS = 10
USER_AGENT = "Mozilla/5.0 (compatible; data-flakes-stock-comparison)"
COLUMNS = ["symbol", "title", "summary", "publishedAt", "url", "source"]


def source_from_url(url: str | None) -> str:
    """Name the publisher from an article URL.

    Args:
        url: Article link.

    Returns:
        A readable name, for example ``Yahoo Finance`` or ``reuters.com``.
    """
    host = urlparse(url or "").netloc.lower().removeprefix("www.")
    if not host:
        return "Unknown"
    return "Yahoo Finance" if host.endswith("finance.yahoo.com") else host


def parse_rss(xml_text: str, symbol: str) -> list[dict[str, object]]:
    """Turn an RSS document into headline records.

    Args:
        xml_text: The raw feed.
        symbol: The ticker the feed was requested for.

    Returns:
        One dict per item with the keys in ``COLUMNS``. A malformed feed gives
        an empty list.
    """
    try:
        root = ElementTree.fromstring(xml_text)
    except (ElementTree.ParseError, DefusedXmlException):
        logger.warning("Could not parse the RSS feed for %s", symbol)
        return []
    records = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        link = (item.findtext("link") or "").strip()
        records.append(
            {
                "symbol": symbol,
                "title": title,
                "summary": (item.findtext("description") or "").strip(),
                "publishedAt": item.findtext("pubDate"),
                "url": link,
                "source": source_from_url(link),
            }
        )
    return records


def is_relevant(record: dict[str, object], symbol: str) -> bool:
    """Say whether an article is actually about the company.

    An article counts if the company name appears in its headline or summary,
    or the ticker appears as a whole word in the headline.

    Args:
        record: A headline record.
        symbol: The ticker the article was fetched for.

    Returns:
        True if the article looks to be about the company.
    """
    title = str(record["title"])
    text = f"{title} {record['summary']}".lower()
    name = company_name(symbol).lower()
    if name != symbol.lower() and name in text:
        return True
    return re.search(rf"\b{re.escape(symbol)}\b", title) is not None


def fetch_rss(symbol: str) -> list[dict[str, object]]:
    """Download the RSS feed for one symbol.

    Args:
        symbol: A ticker symbol.

    Returns:
        Headline records, or an empty list if the request fails.
    """
    try:
        response = requests.get(
            RSS_URL,
            params={"s": symbol, "region": "US", "lang": "en-US"},
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        logger.warning("RSS request for %s failed: %s", symbol, error)
        return []
    return parse_rss(response.text, symbol)


def fetch_headlines(symbols: list[str]) -> pd.DataFrame:
    """Fetch relevant, de-duplicated headlines for several symbols.

    Args:
        symbols: Ticker symbols.

    Returns:
        A frame with the ``COLUMNS``, newest first; empty if nothing was found.
    """
    records = [
        record
        for symbol in symbols
        for record in fetch_rss(symbol)
        if is_relevant(record, symbol)
    ]
    if not records:
        return pd.DataFrame(columns=COLUMNS)
    frame = pd.DataFrame(records, columns=COLUMNS)
    frame["publishedAt"] = pd.to_datetime(
        frame["publishedAt"], errors="coerce", utc=True
    )
    frame = frame.drop_duplicates(subset=["symbol", "title"])
    return frame.sort_values("publishedAt", ascending=False).reset_index(drop=True)
