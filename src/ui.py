"""Page layout for the stock comparison app."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import return_correlation, score_text, tone
from src.charts import (
    correlation_figure,
    drawdown_figure,
    price_figure,
    returns_figure,
    risk_return_figure,
    rolling_volatility_figure,
    sentiment_figure,
)
from src.universe import (
    DEFAULT_TICKERS,
    SECTORS,
    display_name,
    logo_url,
    stock_options,
)

SITE_URL = "https://www.data-flakes.dev"
ROOT = Path(__file__).resolve().parent.parent

PERIODS = {
    "1M": "1mo",
    "6M": "6mo",
    "YTD": "ytd",
    "1Y": "1y",
    "2Y": "2y",
    "5Y": "5y",
    "Max": "max",
}
PERIOD_PHRASE = {
    "1mo": "over the last month",
    "6mo": "over the last 6 months",
    "ytd": "since the start of the year",
    "1y": "over the last year",
    "2y": "over the last 2 years",
    "5y": "over the last 5 years",
    "max": "over their full history",
}
MAX_TICKERS = 8


def render_config() -> None:
    """Set the page configuration and load the stylesheet."""
    st.set_page_config(
        page_title="Stock comparison",
        page_icon=str(ROOT / "assets" / "images" / "favicon.png"),
        layout="wide",
    )
    css = (ROOT / "styles" / "main.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_topbar() -> None:
    """Show a plain breadcrumb back to the Data Flakes site."""
    st.markdown(
        f"""
        <nav class="site-bar">
            <a href="{SITE_URL}/" target="_blank">Data Flakes</a>
            <span>/</span>
            <a href="{SITE_URL}/projects/" target="_blank">Projects</a>
            <span>/</span>
            <span>Stock comparison</span>
        </nav>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[list[str], str, bool, bool]:
    """Render the controls.

    Returns:
        The chosen tickers, the yfinance period code, whether to index prices
        and whether to add the S&P 500 benchmark.
    """
    with st.sidebar:
        st.header("Compare")
        sectors = st.multiselect(
            "Sector",
            SECTORS,
            placeholder="All sectors",
            key="sectors",
            help="Narrows the stock list below. Stocks you already picked stay.",
        )
        picked = st.session_state.get("stocks", DEFAULT_TICKERS)
        options = list(dict.fromkeys([*stock_options(sectors), *picked]))
        chosen = st.multiselect(
            "Stocks",
            options,
            default=DEFAULT_TICKERS,
            key="stocks",
            format_func=display_name,
            accept_new_options=True,
            max_selections=MAX_TICKERS,
            placeholder="Search by company or ticker",
            help=f"Up to {MAX_TICKERS}. Type any ticker symbol and press Enter.",
        )
        period = st.segmented_control("Period", list(PERIODS), default="2Y")
        view = st.segmented_control(
            "Chart shows",
            ["Indexed", "Price"],
            default="Indexed",
            help="Indexed starts every stock at 100 so growth is comparable.",
        )
        benchmark = st.toggle("Compare with the S&P 500", value=True)
        st.caption("Prices come from Yahoo Finance and can be delayed or incomplete.")
    tickers = [t.strip().upper() for t in chosen if t.strip()]
    return tickers, PERIODS[period or "2Y"], view != "Price", benchmark


def render_intro(last_date: pd.Timestamp, phrase: str) -> None:
    """Introduce the page.

    Args:
        last_date: Date of the most recent close in the data.
        phrase: The period as a phrase, for example ``over the last year``.
    """
    st.title("Stock comparison")
    st.write(
        f"How up to {MAX_TICKERS} stocks have moved {phrase}, how "
        f"bumpy the ride was, and what recent headlines say. Latest close: "
        f"{last_date:%d %B %Y}."
    )


def render_summary(summary: pd.DataFrame) -> None:
    """Show one row of headline statistics per stock, with company logos.

    Args:
        summary: Frame from ``analysis.summary_table``.
    """
    table = summary.copy()
    table.insert(0, "Logo", [logo_url(t) for t in table["Ticker"]])
    names = [display_name(t).split(" (")[0] for t in table["Ticker"]]
    table.insert(2, "Company", names)
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            "Logo": st.column_config.ImageColumn(" ", width="small"),
            "Company": st.column_config.TextColumn(width="medium"),
            "Price": st.column_config.NumberColumn(format="$%.2f"),
            "Day": st.column_config.NumberColumn("1 day", format="%+.2f%%"),
            "Return": st.column_config.NumberColumn(format="%+.1f%%"),
            "Volatility": st.column_config.NumberColumn(format="%.1f%%"),
            "Drawdown": st.column_config.NumberColumn(
                "Worst fall", format="%.1f%%", help="Largest peak-to-trough drop."
            ),
            "Trend": st.column_config.LineChartColumn("Recent trend"),
        },
    )


def render_prices(closes: pd.DataFrame, indexed: bool) -> None:
    """Draw the price comparison chart.

    Args:
        closes: One column of closing prices per stock.
        indexed: Whether to rebase every line to 100.
    """
    st.subheader("Prices")
    st.plotly_chart(price_figure(closes, indexed), width="stretch")


def render_risk(summary: pd.DataFrame) -> None:
    """Draw the risk and return scatter with a short explanation.

    Args:
        summary: Frame from ``analysis.summary_table``.
    """
    st.subheader("Risk and return")
    st.write(
        "Volatility is how much the daily price swings, scaled to a year. Further "
        "right is a bumpier ride and higher up is a bigger return, so the best "
        "outcomes sit towards the top left."
    )
    st.plotly_chart(risk_return_figure(summary), width="stretch")


def render_analysis(closes: pd.DataFrame) -> None:
    """Show deeper views of the same prices, one per tab.

    Args:
        closes: One column of closing prices per stock.
    """
    st.subheader("Analysis")
    drawdown, volatility, correlation, returns = st.tabs(
        ["Drawdown", "Rolling volatility", "Correlation", "Daily returns"]
    )
    with drawdown:
        st.caption(
            "How far each stock sat below its previous high. Deep, long dips "
            "show how much pain an investor had to sit through."
        )
        st.plotly_chart(drawdown_figure(closes), width="stretch")
    with volatility:
        window = st.select_slider("Window (trading days)", [10, 20, 30, 60, 90], 30)
        st.caption("Risk changes over time; the average in the table hides that.")
        st.plotly_chart(rolling_volatility_figure(closes, window), width="stretch")
    with correlation:
        if closes.shape[1] < 2:
            st.info("Pick at least two stocks to compare how they move together.")
        else:
            st.caption(
                "Values near +1 mean the stocks rise and fall together, so owning "
                "both adds little diversification. Near 0 or below diversifies more."
            )
            st.plotly_chart(
                correlation_figure(return_correlation(closes)), width="stretch"
            )
    with returns:
        st.caption(
            "How often each stock had a quiet day versus a big one. Wider, "
            "heavier tails mean larger surprises."
        )
        st.plotly_chart(returns_figure(closes), width="stretch")


def render_headlines(news: pd.DataFrame) -> None:
    """Show recent headlines with filters, a tone chart and a scorer.

    Args:
        news: Headlines with ``sentiment_score`` and ``tone`` columns; may be empty.
    """
    st.subheader("Headlines")
    if news is None or news.empty:
        st.info(
            "No recent headlines were found for these stocks. "
            "You can still score any headline below."
        )
        render_scorer()
        return

    symbols = sorted(news["symbol"].unique())
    pick_col, tone_col = st.columns([3, 2])
    chosen = pick_col.multiselect("Stocks", symbols, default=symbols, key="news_stocks")
    tone_filter = tone_col.segmented_control(
        "Tone", ["All", "Positive", "Neutral", "Negative"], default="All"
    )
    view = news[news["symbol"].isin(chosen)]
    if tone_filter and tone_filter != "All":
        view = view[view["tone"] == tone_filter]

    figure = sentiment_figure(news[news["symbol"].isin(chosen)])
    if figure is not None:
        st.plotly_chart(figure, width="stretch")
    st.caption(
        f"{len(view)} of {len(news)} headlines. Scores come from a general-language "
        "model with finance terms added, so treat them as a rough guide."
    )
    st.dataframe(
        view[
            [
                "publishedAt",
                "symbol",
                "title",
                "tone",
                "sentiment_score",
                "source",
                "url",
            ]
        ],
        hide_index=True,
        width="stretch",
        height=min(420, 40 + 35 * max(len(view), 1)),
        column_config={
            "publishedAt": st.column_config.DatetimeColumn(
                "Published", format="distance"
            ),
            "symbol": "Stock",
            "title": st.column_config.TextColumn("Headline", width="medium"),
            "tone": "Tone",
            "sentiment_score": st.column_config.NumberColumn("Score", format="%+.2f"),
            "source": st.column_config.TextColumn("Source", width="small"),
            "url": st.column_config.LinkColumn(
                "Link", display_text="Open", width="small"
            ),
        },
    )
    render_scorer()


def render_scorer() -> None:
    """Score a headline typed by the user."""
    text = st.text_input(
        "Score a headline",
        placeholder="Chipmaker beats earnings forecasts as demand surges",
    )
    if text.strip():
        score = score_text(text)
        st.metric("Sentiment", f"{score:+.2f}", tone(score), delta_color="off")


def render_footer() -> None:
    """Show the disclaimer and a link back to the Data Flakes site."""
    st.markdown(
        f"""
        <footer class="site-foot">
            For information only, not investment advice. Past performance does not
            predict future results. Built by Elliott Fairhall; more at
            <a href="{SITE_URL}/" target="_blank">data-flakes.dev</a>.
        </footer>
        """,
        unsafe_allow_html=True,
    )
