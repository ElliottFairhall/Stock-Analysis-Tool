"""Tests for the price statistics, headline scoring and company universe."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.analysis import (
    calculate_volatility,
    close_prices,
    daily_returns,
    drawdown_series,
    max_drawdown,
    rebase,
    return_correlation,
    rolling_volatility,
    score_text,
    summary_table,
)
from src.universe import (
    COMPANIES,
    SECTORS,
    company_name,
    display_name,
    logo_url,
    monogram,
    stock_options,
)


def _closes() -> pd.DataFrame:
    index = pd.bdate_range("2025-01-01", periods=6)
    return pd.DataFrame(
        {"AAA": [100, 110, 99, 120, 108, 130], "BBB": [50, 50, 50, 50, 50, 50]},
        index=index,
        dtype="float64",
    )


def test_rebase_starts_every_series_at_100() -> None:
    """Growth of 100: the first value of each column is exactly 100."""
    rebased = rebase(_closes())
    assert rebased.iloc[0].tolist() == [100.0, 100.0]
    assert rebased["AAA"].iloc[-1] == pytest.approx(130.0)


def test_max_drawdown_finds_the_worst_peak_to_trough_fall() -> None:
    """120 down to 108 is a 10% fall; 110 to 99 is also 10%."""
    series = _closes()["AAA"]
    assert max_drawdown(series) == pytest.approx(-10.0)
    assert max_drawdown(_closes()["BBB"]) == 0.0


def test_drawdown_series_is_never_positive_and_zero_at_highs() -> None:
    """A drawdown is zero at a new high and negative below it."""
    dd = drawdown_series(_closes())["AAA"]
    assert (dd <= 0).all()
    assert dd.iloc[1] == 0.0
    assert dd.iloc[2] == pytest.approx(-10.0)


def test_flat_prices_have_zero_volatility() -> None:
    """A constant price never moves, so its risk is zero."""
    assert calculate_volatility(_closes()["BBB"]) == 0.0


def test_volatility_matches_the_textbook_formula() -> None:
    """Annualised volatility is the daily return std times root 252."""
    series = _closes()["AAA"]
    expected = series.pct_change().std() * np.sqrt(252) * 100
    assert calculate_volatility(series) == pytest.approx(expected)


def test_volatility_of_a_short_series_is_zero() -> None:
    """One price gives no returns to measure."""
    assert calculate_volatility(pd.Series([100.0])) == 0.0


def test_rolling_volatility_needs_a_full_window() -> None:
    """The first window-1 rows are empty rather than guessed."""
    rolling = rolling_volatility(_closes(), window=3)
    assert rolling["AAA"].iloc[:3].isna().all()
    assert rolling["AAA"].iloc[3:].notna().all()


def test_correlation_of_a_series_with_itself_is_one() -> None:
    """The diagonal is 1 and the matrix is symmetric."""
    closes = _closes()
    closes["CCC"] = closes["AAA"] * 2
    corr = return_correlation(closes[["AAA", "CCC"]])
    assert corr.loc["AAA", "CCC"] == pytest.approx(1.0)
    assert corr.equals(corr.T)


def test_daily_returns_are_percentages() -> None:
    """A 10% rise shows as 10, not 0.1."""
    assert daily_returns(_closes())["AAA"].iloc[0] == pytest.approx(10.0)


def test_summary_table_reports_each_ticker() -> None:
    """One row per ticker with price, return, risk and a sparkline."""
    table = summary_table(_closes())
    row = table.set_index("Ticker").loc["AAA"]
    assert row["Price"] == 130.0
    assert row["Return"] == pytest.approx(30.0)
    assert row["Drawdown"] == pytest.approx(-10.0)
    assert len(row["Trend"]) == 6


def test_close_prices_skips_tickers_without_data() -> None:
    """A ticker Yahoo returned nothing for is left out, not an error."""
    index = pd.bdate_range("2025-01-01", periods=3)
    columns = pd.MultiIndex.from_product([["AAA"], ["Close", "Open"]])
    frame = pd.DataFrame(1.0, index=index, columns=columns)
    closes = close_prices(frame, ["AAA", "ZZZ"])
    assert list(closes.columns) == ["AAA"]


@pytest.mark.parametrize(
    ("text", "sign"),
    [
        ("Record profits and a great quarter delight investors", 1),
        ("Company collapses amid fraud scandal and heavy losses", -1),
    ],
)
def test_headline_sentiment_has_the_right_sign(text: str, sign: int) -> None:
    """Clearly positive and negative headlines score on the right side of 0."""
    assert score_text(text) * sign > 0.3


@pytest.mark.parametrize("text", ["", "   ", None])
def test_blank_headlines_score_zero(text: object) -> None:
    """Nothing to read means a neutral score, never an error."""
    assert score_text(text) == 0.0  # type: ignore[arg-type]


def test_universe_has_unique_tickers_and_known_sectors() -> None:
    """The curated list is clean and every company has a website."""
    assert COMPANIES["ticker"].is_unique
    assert (COMPANIES["domain"].str.contains(r"\.")).all()
    assert len(SECTORS) >= 8


def test_sector_filter_narrows_the_options() -> None:
    """Choosing a sector keeps only its companies; none means all."""
    energy = stock_options(["Energy"])
    assert set(energy) == {"XOM", "CVX"}
    assert len(stock_options([])) == len(COMPANIES)


def test_names_and_logos_for_known_and_unknown_tickers() -> None:
    """Known tickers get names and a favicon URL; unknown get a monogram."""
    assert company_name("MSFT") == "Microsoft"
    assert display_name("MSFT") == "Microsoft (MSFT)"
    assert display_name("ZZZZ") == "ZZZZ"
    assert logo_url("MSFT").startswith("https://www.google.com/s2/favicons?domain=")
    assert logo_url("ZZZZ") == monogram("ZZZZ")
    assert monogram("ZZZZ").startswith("data:image/svg+xml;base64,")
