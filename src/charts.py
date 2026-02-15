import plotly.graph_objs as go

# Premium Color Palette
COLORS = ["#fda4af", "#7dd3fc", "#f0abfc", "#fb7185", "#38bdf8"]


def create_line_chart_figure(selected_tickers, stocks_df):
    """
    Creates a plotly figure for historical close prices.
    """
    if stocks_df is None or stocks_df.empty:
        return None

    fig = go.Figure()

    for i, ticker in enumerate(selected_tickers):
        try:
            if ticker in stocks_df.columns:
                close_data = stocks_df[ticker]["Close"]
            else:
                continue

            fig.add_trace(
                go.Scatter(
                    x=close_data.index,
                    y=close_data,
                    mode="lines",
                    name=ticker,
                    line=dict(color=COLORS[i % len(COLORS)], width=2.5),
                )
            )
        except (KeyError, ValueError):
            continue

    fig.update_layout(
        title="Historical Market Performance",
        xaxis_title="Timeline",
        yaxis_title="Close Price (USD)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=14, color="#f8fafc"),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def create_relative_returns_figure(selected_tickers, stocks_df):
    """
    Creates a plotly figure for relative returns.
    """
    if stocks_df is None or stocks_df.empty:
        return None

    traces = []

    for i, ticker in enumerate(selected_tickers):
        if ticker not in stocks_df.columns:
            continue

        stock_df = stocks_df[ticker].copy()
        if stock_df.empty:
            continue

        stock_df.loc[:, "returns"] = stock_df["Close"].pct_change() * 100
        traces.append(
            go.Bar(
                x=stock_df.index,
                y=stock_df["returns"],
                name=ticker,
                marker=dict(color=COLORS[i % len(COLORS)]),
            )
        )

    layout = go.Layout(
        title="Dynamic Growth Engine (Relative Returns %)",
        xaxis=dict(title="Timeline"),
        yaxis=dict(title="Return Velocity (%)"),
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=14, color="#f8fafc"),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return go.Figure(data=traces, layout=layout)


def create_sentiment_chart_figure(news_df):
    """
    Creates a bar chart of average sentiment scores by stock.
    """
    if news_df is None or news_df.empty or "sentiment_score" not in news_df.columns:
        return None

    if "publishedAt" in news_df.columns:
        # Group by Symbol for a comparative summary
        df_grouped = news_df.groupby("symbol")["sentiment_score"].mean().reset_index()

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df_grouped["symbol"],
                y=df_grouped["sentiment_score"],
                marker=dict(
                    color=df_grouped["sentiment_score"],
                    colorscale="RdYlGn",
                    showscale=True,
                    colorbar=dict(title="Sentiment Intensity"),
                ),
                text=df_grouped["sentiment_score"].round(2),
                textposition="auto",
            )
        )

        fig.update_layout(
            title="Market Resonance Indicator (Sentiment Analysis)",
            xaxis_title="Ticker Symbol",
            yaxis_title="Mean Resonance Score",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", size=14, color="#f8fafc"),
            margin=dict(l=20, r=20, t=60, b=20),
        )
        return fig
    else:
        return None
