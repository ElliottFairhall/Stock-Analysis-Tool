"""Run the whole app against a fake Yahoo Finance, so no test touches the network."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def _run() -> AppTest:
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()


def test_default_page_renders_with_summary_and_analysis() -> None:
    """The opening state shows a summary table and the four analysis tabs."""
    at = _run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.title[0].value == "Stock comparison"
    assert len(at.dataframe) >= 1
    assert [tab.label for tab in at.tabs] == [
        "Drawdown",
        "Rolling volatility",
        "Correlation",
        "Daily returns",
    ]


def test_summary_lists_the_chosen_stocks_and_the_benchmark() -> None:
    """MSFT, TSLA and the S&P 500 appear as rows."""
    table = _run().dataframe[0].value
    assert list(table["Ticker"]) == ["MSFT", "TSLA", "S&P 500"]
    assert list(table["Company"]) == ["Microsoft", "Tesla", "S&P 500"]
    assert table["Logo"].notna().all()


def test_benchmark_can_be_switched_off() -> None:
    """With the toggle off the S&P 500 row disappears."""
    at = _run()
    at.toggle[0].set_value(False).run()
    assert not at.exception
    assert list(at.dataframe[0].value["Ticker"]) == ["MSFT", "TSLA"]


def test_adding_a_typed_ticker_works() -> None:
    """Any ticker can be typed, not just the curated ones."""
    at = _run()
    at.multiselect(key="stocks").set_value(["MSFT", "TSLA", "ZZZ"]).run()
    assert not at.exception
    assert "ZZZ" in list(at.dataframe[0].value["Ticker"])


def test_sector_filter_limits_the_stock_list() -> None:
    """Choosing Energy leaves only energy companies, plus current picks."""
    at = _run()
    at.multiselect(key="sectors").set_value(["Energy"]).run()
    options = set(at.multiselect(key="stocks").options)
    assert {"Exxon Mobil (XOM)", "Chevron (CVX)"} <= options
    assert "Apple (AAPL)" not in options
    assert {"Microsoft (MSFT)", "Tesla (TSLA)"} <= options  # current picks stay


def test_unknown_ticker_gets_a_warning_not_a_crash() -> None:
    """A symbol Yahoo has no data for is reported plainly."""
    at = _run()
    at.multiselect(key="stocks").set_value(["MSFT", "NOPE"]).run()
    assert not at.exception
    assert any("NOPE" in w.value for w in at.warning)


def test_empty_selection_prompts_the_user() -> None:
    """With nothing chosen the page asks for a stock instead of failing."""
    at = _run()
    at.multiselect(key="stocks").set_value([]).run()
    assert not at.exception
    assert any("at least one" in info.value for info in at.info)


def test_period_and_chart_view_controls_render() -> None:
    """Every period option renders without error."""
    for period in ("1M", "YTD", "Max"):
        at = _run()
        at.sidebar.get("segmented_control")[0].set_value(period).run()
        assert not at.exception, period


def test_headline_scorer_labels_sentiment() -> None:
    """Typing a positive headline shows a positive score."""
    at = _run()
    at.text_input[0].set_value("Record profits delight investors").run()
    assert not at.exception
    sentiment = next(m for m in at.metric if m.label == "Sentiment")
    assert float(sentiment.value) > 0
    assert sentiment.delta == "Positive"
