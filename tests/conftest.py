"""Shared fixtures: a fake Yahoo Finance so no test touches the network."""

from __future__ import annotations

import zlib
from collections.abc import Iterator

import numpy as np
import pandas as pd
import pytest
import streamlit as st

from src.universe import company_name

UNKNOWN = {"NOPE"}


def fake_download(tickers: str, period: str = "2y", **_: object) -> pd.DataFrame:
    """Return a deterministic ``(ticker, field)`` frame like yfinance does."""
    index = pd.bdate_range(end="2026-10-30", periods=260)
    frames = {}
    for ticker in tickers.split():
        if ticker in UNKNOWN:
            continue
        rng = np.random.default_rng(zlib.crc32(ticker.encode()))
        close = 100 * np.cumprod(1 + rng.normal(0.0004, 0.015, len(index)))
        for field in ("Open", "High", "Low", "Close", "Volume"):
            frames[(ticker, field)] = close if field == "Close" else close * 0.99
    return pd.DataFrame(frames, index=index)


class FakeTicker:
    """Stand-in for ``yfinance.Ticker`` with two deterministic headlines."""

    def __init__(self, symbol: str) -> None:
        """Create the fake with one good and one bad headline."""
        self.news = [
            {
                "content": {
                    "title": f"{symbol} posts record profits",
                    "link": "https://a",
                }
            },
            {"content": {"title": f"{symbol} faces heavy losses", "link": "https://b"}},
        ]


def sample_rss(symbol: str) -> str:
    """A small Yahoo-style RSS feed: two relevant, one duplicate, one off-topic."""
    name = company_name(symbol)
    item = (
        "<item><title>{title}</title><description>{summary}</description>"
        "<link>{link}</link><pubDate>{date}</pubDate></item>"
    )
    items = [
        item.format(
            title=f"{name} beats earnings forecasts as demand surges",
            summary="Strong quarter.",
            link="https://finance.yahoo.com/news/a.html",
            date="Mon, 02 Nov 2026 19:00:00 +0000",
        ),
        item.format(
            title=f"Analysts downgrade {symbol} after weak quarter",
            summary="Shares plunge.",
            link="https://www.reuters.com/b",
            date="Mon, 02 Nov 2026 20:00:00 +0000",
        ),
        item.format(
            title="Crypto token prices rally again",
            summary="Nothing to do with the company.",
            link="https://99bitcoins.com/c",
            date="Mon, 02 Nov 2026 21:00:00 +0000",
        ),
        item.format(
            title=f"{name} beats earnings forecasts as demand surges",
            summary="Duplicate of the first.",
            link="https://finance.yahoo.com/news/a.html",
            date="Mon, 02 Nov 2026 19:00:00 +0000",
        ),
    ]
    return '<?xml version="1.0"?><rss><channel>' + "".join(items) + "</channel></rss>"


class FakeResponse:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, text: str) -> None:
        """Hold the body text."""
        self.text = text

    def raise_for_status(self) -> None:
        """Pretend the request succeeded."""


def fake_get(url: str, params: dict | None = None, **_: object) -> FakeResponse:
    """Return the sample feed for the requested symbol."""
    return FakeResponse(sample_rss((params or {})["s"]))


@pytest.fixture(scope="module", autouse=True)
def offline() -> Iterator[None]:
    """Replace Yahoo Finance with fakes for every test module.

    Module scope matters: module-scoped fixtures such as the smoke test's
    shared app run are built before any function-scoped patch would apply.
    """
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("src.data.yf.download", fake_download)
        patch.setattr("src.data.yf.Ticker", FakeTicker)
        patch.setattr("src.news.requests.get", fake_get)
        st.cache_data.clear()
        yield


@pytest.fixture(autouse=True)
def fresh_cache() -> None:
    """Start each test with empty Streamlit caches."""
    st.cache_data.clear()
