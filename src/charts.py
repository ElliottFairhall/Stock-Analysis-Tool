"""Plotly figures for the stock comparison."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.analysis import daily_returns, drawdown_series, rebase, rolling_volatility
from src.universe import BENCHMARK_NAME

# Data Flakes palette, one colour per ticker (the app allows five).
COLOURS = [
    "#5E8FBA",
    "#C06C84",
    "#F8B195",
    "#6C5B7B",
    "#F67280",
    "#355C7D",
    "#E8A0AF",
    "#9BB5CE",
]
BENCHMARK_COLOUR = "#94A3B8"
POSITIVE = "#5E8FBA"
NEGATIVE = "#F67280"
FONT = {"family": "Inter, sans-serif", "size": 13}
GRID = "rgba(128,128,128,0.18)"


def _colour(ticker: str, position: int) -> str:
    """Pick a colour: grey for the benchmark, otherwise by position."""
    if ticker == BENCHMARK_NAME:
        return BENCHMARK_COLOUR
    return COLOURS[position % len(COLOURS)]


def _dash(ticker: str) -> str:
    return "dot" if ticker == BENCHMARK_NAME else "solid"


def _style(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        margin={"t": 8, "b": 8, "l": 8, "r": 8},
        font=FONT,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


def price_figure(closes: pd.DataFrame, indexed: bool) -> go.Figure:
    """Line chart of closing prices.

    Args:
        closes: One column per ticker.
        indexed: If true, every line starts at 100 so growth is comparable.

    Returns:
        The figure.
    """
    data = rebase(closes) if indexed else closes
    fig = go.Figure()
    for position, ticker in enumerate(data.columns):
        fig.add_scatter(
            x=data.index,
            y=data[ticker],
            name=ticker,
            mode="lines",
            line={
                "color": _colour(ticker, position),
                "width": 2,
                "dash": _dash(ticker),
            },
            hovertemplate="%{y:.1f}" if indexed else "$%{y:.2f}",
        )
    _style(fig, 400)
    fig.update_layout(
        hovermode="x unified", legend={"orientation": "h", "y": 1.1, "x": 0}
    )
    fig.update_yaxes(title="Index (start = 100)" if indexed else "Close (USD)")
    return fig


def risk_return_figure(summary: pd.DataFrame) -> go.Figure:
    """Scatter of period return against volatility, one point per ticker.

    Args:
        summary: Frame from ``analysis.summary_table``.

    Returns:
        The figure.
    """
    fig = go.Figure()
    for position, row in summary.reset_index(drop=True).iterrows():
        fig.add_scatter(
            x=[row["Volatility"]],
            y=[row["Return"]],
            mode="markers+text",
            text=[row["Ticker"]],
            textposition="top center",
            name=row["Ticker"],
            showlegend=False,
            marker={"size": 14, "color": _colour(row["Ticker"], int(position))},
            hovertemplate="Volatility %{x:.1f}%<br>Return %{y:.1f}%",
        )
    _style(fig, 340)
    fig.update_layout(margin={"t": 28, "b": 8, "l": 8, "r": 24})
    fig.update_xaxes(title="Volatility (annualised, %)")
    fig.update_yaxes(title="Return over the period (%)")
    return fig


def sentiment_figure(news_df: pd.DataFrame) -> go.Figure | None:
    """Stacked bars of positive, neutral and negative headlines per stock.

    Args:
        news_df: Frame with ``symbol`` and ``tone`` columns.

    Returns:
        The figure, or None if there is nothing to plot.
    """
    if news_df is None or news_df.empty or "tone" not in news_df:
        return None
    counts = pd.crosstab(news_df["symbol"], news_df["tone"])
    colours = {"Positive": POSITIVE, "Neutral": "#CBD5E1", "Negative": NEGATIVE}
    fig = go.Figure()
    for label, colour in colours.items():
        if label in counts:
            fig.add_bar(
                y=counts.index,
                x=counts[label],
                name=label,
                orientation="h",
                marker_color=colour,
                hovertemplate="%{x} " + label.lower() + " headlines<extra></extra>",
            )
    _style(fig, 90 + 46 * len(counts))
    fig.update_layout(barmode="stack", legend={"orientation": "h", "y": 1.2, "x": 0})
    fig.update_xaxes(title="Headlines", dtick=1)
    fig.update_yaxes(autorange="reversed")
    return fig


def _lines(data: pd.DataFrame, unit: str) -> go.Figure:
    fig = go.Figure()
    for position, ticker in enumerate(data.columns):
        fig.add_scatter(
            x=data.index,
            y=data[ticker],
            name=ticker,
            mode="lines",
            line={
                "color": _colour(ticker, position),
                "width": 2,
                "dash": _dash(ticker),
            },
            hovertemplate="%{y:.1f}" + unit,
        )
    _style(fig, 340)
    fig.update_layout(
        hovermode="x unified", legend={"orientation": "h", "y": 1.12, "x": 0}
    )
    return fig


def drawdown_figure(closes: pd.DataFrame) -> go.Figure:
    """Line chart of each stock's distance below its previous high.

    Args:
        closes: One column per ticker.

    Returns:
        The figure.
    """
    fig = _lines(drawdown_series(closes), "%")
    fig.update_yaxes(title="Below previous high (%)", ticksuffix="%")
    return fig


def rolling_volatility_figure(closes: pd.DataFrame, window: int) -> go.Figure:
    """Line chart of rolling annualised volatility.

    Args:
        closes: One column per ticker.
        window: Trading days in each rolling window.

    Returns:
        The figure.
    """
    fig = _lines(rolling_volatility(closes, window).dropna(how="all"), "%")
    fig.update_yaxes(title=f"{window}-day volatility (annualised)", ticksuffix="%")
    return fig


def correlation_figure(corr: pd.DataFrame) -> go.Figure:
    """Heatmap of daily-return correlation between stocks.

    Args:
        corr: Square correlation frame.

    Returns:
        The figure.
    """
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.index),
            zmin=-1,
            zmax=1,
            colorscale=[[0, NEGATIVE], [0.5, "#F1F5F9"], [1, POSITIVE]],
            text=corr.round(2).values,
            texttemplate="%{text}",
            hovertemplate="%{x} vs %{y}: %{z:.2f}<extra></extra>",
            colorbar={"title": "Correlation"},
        )
    )
    _style(fig, 90 + 70 * len(corr))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False)
    return fig


def returns_figure(closes: pd.DataFrame) -> go.Figure:
    """Overlaid histograms of daily returns.

    Args:
        closes: One column per ticker.

    Returns:
        The figure.
    """
    returns = daily_returns(closes)
    fig = go.Figure()
    for position, ticker in enumerate(returns.columns):
        fig.add_histogram(
            x=returns[ticker].dropna(),
            name=ticker,
            opacity=0.65,
            nbinsx=50,
            marker_color=_colour(ticker, position),
        )
    _style(fig, 340)
    fig.update_layout(barmode="overlay", legend={"orientation": "h", "y": 1.12})
    fig.update_xaxes(title="Daily return (%)", ticksuffix="%")
    fig.update_yaxes(title="Days")
    return fig
