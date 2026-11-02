"""Tests for the headline pipeline: feed, relevance, scoring, fallback and filters."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import requests
from streamlit.testing.v1 import AppTest

from src.analysis import analyze_sentiment, score_text, tone
from src.data import get_stock_news
from src.news import (
    COLUMNS,
    fetch_headlines,
    fetch_rss,
    is_relevant,
    parse_rss,
    source_from_url,
)

from .conftest import sample_rss

ROOT = Path(__file__).resolve().parent.parent


def test_parse_rss_reads_every_item() -> None:
    """All four sample items are parsed with a publisher name."""
    records = parse_rss(sample_rss("MSFT"), "MSFT")
    assert len(records) == 4
    assert records[0]["source"] == "Yahoo Finance"
    assert records[1]["source"] == "reuters.com"
    assert set(COLUMNS) == set(records[0])


def test_parse_rss_survives_garbage() -> None:
    """A broken feed gives no headlines rather than an exception."""
    assert parse_rss("<rss><not closed", "MSFT") == []


def test_parse_rss_rejects_entity_bombs() -> None:
    """XML entity expansion is refused instead of expanded into memory."""
    bomb = (
        '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">'
        '<!ENTITY b "&a;&a;&a;&a;">]><rss><channel><item>'
        "<title>&b;</title></item></channel></rss>"
    )
    assert parse_rss(bomb, "MSFT") == []


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://finance.yahoo.com/x", "Yahoo Finance"),
        ("https://www.reuters.com/y", "reuters.com"),
        ("", "Unknown"),
        (None, "Unknown"),
    ],
)
def test_source_names(url: str | None, expected: str) -> None:
    """Publishers are named from the link's host."""
    assert source_from_url(url) == expected


def test_relevance_filter_keeps_company_news_and_drops_the_rest() -> None:
    """Name in the headline or ticker as a word counts; passing mentions do not."""
    by_title = {r["title"]: r for r in parse_rss(sample_rss("MSFT"), "MSFT")}
    assert is_relevant(
        by_title["Microsoft beats earnings forecasts as demand surges"], "MSFT"
    )
    assert is_relevant(by_title["Analysts downgrade MSFT after weak quarter"], "MSFT")
    assert not is_relevant(by_title["Crypto token prices rally again"], "MSFT")


def test_ticker_must_be_a_whole_word() -> None:
    """GE must not match inside another word such as 'GEnerally'."""
    record: dict[str, object] = {
        "title": "Generally speaking, markets rose",
        "summary": "",
    }
    assert not is_relevant(record, "GE")


def test_fetch_headlines_filters_dedupes_and_sorts() -> None:
    """Two relevant, unique headlines come back newest first."""
    frame = fetch_headlines(["MSFT"])
    assert list(frame.columns) == COLUMNS
    assert len(frame) == 2
    assert frame["publishedAt"].is_monotonic_decreasing
    assert frame["symbol"].eq("MSFT").all()


def test_fetch_rss_returns_empty_when_the_request_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A network error is logged and yields nothing, never a crash."""

    def boom(*_args: object, **_kwargs: object) -> None:
        raise requests.ConnectionError("offline")

    monkeypatch.setattr("src.news.requests.get", boom)
    assert fetch_rss("MSFT") == []
    assert fetch_headlines(["MSFT"]).empty


def test_get_stock_news_falls_back_to_yfinance_when_rss_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If the feed gives nothing, the old yfinance route is still tried."""
    monkeypatch.setattr("src.data.fetch_headlines", lambda _s: pd.DataFrame())
    frame = get_stock_news(["MSFT"])
    assert len(frame) == 2
    assert "MSFT posts record profits" in set(frame["title"])


@pytest.mark.parametrize(
    ("headline", "expected"),
    [
        ("Chipmaker beats forecasts as shares surge", "Positive"),
        ("Shares plunge after analysts downgrade outlook", "Negative"),
        ("Company announces date of annual meeting", "Neutral"),
    ],
)
def test_finance_terms_are_scored_sensibly(headline: str, expected: str) -> None:
    """Market vocabulary moves the score the way a reader expects."""
    assert tone(score_text(headline)) == expected


def test_analyze_sentiment_adds_score_and_tone() -> None:
    """Scored frames carry a numeric score and a matching label."""
    scored = analyze_sentiment(fetch_headlines(["MSFT"]))
    assert {"sentiment_score", "tone"} <= set(scored.columns)
    assert scored["tone"].tolist() == [tone(s) for s in scored["sentiment_score"]]


def _run() -> AppTest:
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()


def test_page_shows_a_headlines_table_with_sources() -> None:
    """The headlines section lists relevant items, not an empty-state message."""
    at = _run()
    assert not at.exception, [e.value for e in at.exception]
    table = at.dataframe[1].value
    assert set(table["symbol"]) == {"MSFT", "TSLA"}
    assert len(table) == 4
    assert {"Yahoo Finance", "reuters.com"} == set(table["source"])


def test_tone_filter_limits_the_rows() -> None:
    """Choosing Negative leaves only negative headlines."""
    at = _run()
    tone_control = next(
        c for c in at.get("segmented_control") if getattr(c, "label", "") == "Tone"
    )
    tone_control.set_value("Negative").run()
    assert not at.exception
    table = at.dataframe[1].value
    assert len(table) >= 1
    assert set(table["tone"]) == {"Negative"}


def test_stock_filter_limits_the_rows() -> None:
    """Choosing one stock hides the other's headlines."""
    at = _run()
    at.multiselect(key="news_stocks").set_value(["TSLA"]).run()
    assert not at.exception
    assert set(at.dataframe[1].value["symbol"]) == {"TSLA"}
