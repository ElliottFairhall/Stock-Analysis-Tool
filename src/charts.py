import plotly.graph_objs as go
import matplotlib.pyplot as plt
import pandas as pd

def create_line_chart_figure(selected_tickers, stocks_df):
    """
    Creates a plotly figure for historical close prices.
    """
    if stocks_df is None or stocks_df.empty:
        return None

    colors = ['#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845']
    fig = go.Figure()

    for i, ticker in enumerate(selected_tickers):
        # yfinance with group_by='ticker' returns a MultiIndex columns if multiple tickers
        # If single ticker, it might be different, but assuming multiple for now based on original code usage
        try:
            if ticker in stocks_df.columns:
                 # Access the 'Close' column for the specific ticker
                 close_data = stocks_df[ticker]['Close']
            else:
                 # Fallback/Check if flat structure (unlikely with group_by='ticker' and multiple tickers)
                 continue
                 
            fig.add_trace(
                go.Scatter(
                    x=close_data.index,
                    y=close_data,
                    mode='lines',
                    name=ticker,
                    line=dict(color=colors[i % len(colors)])
                )
            )
        except KeyError:
            continue

    fig.update_layout(
        title="Close Price of Selected Stocks",
        xaxis_title="Date",
        yaxis_title="Close Price",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    return fig

def create_relative_returns_figure(selected_tickers, stocks_df):
    """
    Creates a plotly figure for relative returns.
    """
    if stocks_df is None or stocks_df.empty:
        return None

    bar_colors = ['#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845']
    traces = []

    for i, ticker in enumerate(selected_tickers):
        if ticker not in stocks_df.columns:
            continue
            
        stock_df = stocks_df[ticker].copy()
        if stock_df.empty:
            continue
            
        stock_df.loc[:, "returns"] = stock_df["Close"].pct_change()
        traces.append(
            go.Bar(
                x=stock_df.index,
                y=stock_df["returns"],
                name=ticker,
                marker=dict(color=bar_colors[i % len(bar_colors)])
            )
        )

    layout = go.Layout(
        title="Relative Returns of Selected Stocks",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Relative Return (%)"),
        barmode="group",
        plot_bgcolor='#0D5943',
        paper_bgcolor='#0D5943',
        font=dict(color='#FFFFFF')
    )

    return go.Figure(data=traces, layout=layout)

def create_scatter_plot_figure(selected_tickers, stocks_df):
    """
    Creates a matplotlib figure for historical close prices scatter plot.
    """
    colors = ['#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845']
    fig, ax = plt.subplots()

    for i, ticker in enumerate(selected_tickers):
        if ticker not in stocks_df.columns:
            continue

        stock_df = stocks_df[ticker]
        if stock_df.empty:
            continue
            
        ax.scatter(stock_df.index, stock_df["Close"], label=ticker, color=colors[i % len(colors)])

    ax.set_title("Historical Close Prices of Selected Stocks")
    ax.set_xlabel("Date")
    ax.set_ylabel("Close Price")
    ax.legend()
    
    return fig

def create_sentiment_chart_figure(news_df):
    """
    Creates a bar chart of average sentiment scores by stock.
    (Aggregating by symbol since we don't have enough data for a time series in a single run usually,
     but user requested x-axis as time periods. However, typically we just get recent news.
     Let's attempt time-based aggregation if datetime is present, otherwise simple bar per article or average per stock?
     The requirement: "bar chart of average sentiment scores. x-axis ... time periods".
     Given fetch is snapshot, let's group by Date if possible, or just by Symbol if data is sparse.
     Let's try grouping by Symbol for now as "Average Sentiment of News Articles chart" usually implies comparing stocks or simple daily avg.
     Wait, user said "x-axis ... different time periods". 
     Let's try resampling by day if 'publishedAt' exists.
    """
    if news_df is None or news_df.empty or 'sentiment_score' not in news_df.columns:
        return None
        
    # Ensure date column
    if 'publishedAt' in news_df.columns:
        # Group by Date and perhaps Symbol? 
        # If multiple stocks selected, maybe color by stock.
        # "Average sentiment of News Articles"
        
        # Let's create a bar chart: X=Date, Y=Avg Sentiment, Color=Symbol
        df_grouped = news_df.groupby([pd.Grouper(key='publishedAt', freq='D'), 'symbol'])['sentiment_score'].mean().reset_index()
        
        # If we have only 1 day of data, it might look sparse.
        
        fig = go.Figure()
        symbols = df_grouped['symbol'].unique()
        colors = ['#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845']
        
        for i, symbol in enumerate(symbols):
            subset = df_grouped[df_grouped['symbol'] == symbol]
            fig.add_trace(go.Bar(
                x=subset['publishedAt'],
                y=subset['sentiment_score'],
                name=symbol,
                marker=dict(color=colors[i % len(colors)])
            ))
            
        fig.update_layout(
            title="Average Sentiment of News Articles",
            xaxis_title="Date",
            yaxis_title="Average Sentiment Score",
            barmode='group'
        )
        return fig
    else:
        # Fallback if no date
        return None

