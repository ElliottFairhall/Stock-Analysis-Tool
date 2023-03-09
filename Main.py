import requests
from nltk.sentiment import SentimentIntensityAnalyzer
from PIL import Image
import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objs as go
import numpy as np
from bs4 import BeautifulSoup
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import os

PAGE_TITLE = "Data Engineer, Educator Analyst and Technology Enthusiast"

PAGE_ICON = ":chart_with_upwards_trend:"

# Set the title and icon of the application
st.set_page_config(page_title = PAGE_TITLE, page_icon = PAGE_ICON, layout="centered")

# Get the current directory and open the css file
current_dir = Path(__file__).parent if "_file_" in locals() else Path.cwd()
home_page = current_dir / "Home_Page.py"
finance_image = current_dir / "assets"/ "images" / "Finance.jpg"
css_file = current_dir / "styles" / "main.css"
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

load_dotenv()
News_API = os.environ["NEWS_API"]

# provide title for page
st.markdown("<h1>Introduction to Financial Analysis with Python</h1>", unsafe_allow_html=True)

st.markdown("---")

#open finance_image for page
image = Image.open(finance_image)
st.image(image)

# create information related project outline 
st.markdown("""
<p>In this project, I will be showcasing various financial analysis techniques using Python. I will be utilising modules such as yfinance, matplotlib, streamlit and VaderSentiment to analyse stocks and extract news articles. These modules will assist me in creating charts and visualisations of historical stock data, calculating returns and analysing sentiments of news articles. By using these modules and similar modules to this, analysts can gain a better understanding of the performance of stocks.</p>
<hr>
<h1>Business Stock Dropdown</h1>
<p>The dropdown below allows users of this project to select multiple businesses from a list. In this project, the dropdown is used to select the stocks that will be analysed. The businesses that are provided include Apple Inc. (AAPL), Tesla Inc. (TSLA), Microsoft Corp. (MSFT), Alphabet Inc. (GOOGL), Amazon Inc. (AMZN), Facebook Inc. (META), Alibaba Group Holding Ltd. (BABA), Wal-Mart Stores Inc. (WMT), General Electric Co. (GE), JPMorgan Chase & Co. (JPM), Taiwan Semiconductor Manufacturing Co. Ltd. (TSM), Comcast Corp. (CMCSA), Chevron Corp. (CVX), Procter & Gamble Co. (PG), Boeing Co. (BA), Intel Corp. (INTC), Cisco Systems Inc. (CSCO), and Pfizer Inc. (PFE). By selecting two or more of these stocks, users can gain a deeper understanding of the performance and see the potential of these companies.</p>
""", unsafe_allow_html=True)

# Create a multi-select box for the user to select stock tickers
selected_tickers = st.multiselect("Select stocks to analyse", ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "BABA", "WMT", "GE", "JPM", "TSM", "WMT", "CMCSA", "CVX", "PG", "WMT", "BA", "INTC", "CSCO", "PFE"], default=["MSFT","TSLA"])
if len(selected_tickers) < 2:
    st.error("Please select at least 2 stocks.")

# Concatenate the selected tickers into a single string for use in the API call
ticker_string = ','.join(selected_tickers)

def get_stock_data(ticker_string):
    stocks_df = yf.download(ticker_string, period='max', group_by='ticker')
    # Clean the data
    stocks_df.dropna(inplace=True)
    return stocks_df
    
    # Get the news for each selected ticker
    news_df = pd.DataFrame()
    for ticker in selected_tickers:
        ticker_news = yf.Ticker(ticker).news(articles=50)
        ticker_news_df = pd.DataFrame(ticker_news)
        ticker_news_df['symbol'] = ticker
        news_df = pd.concat([news_df, ticker_news_df], axis=0)
    
    # Clean the news data
    if not news_df.empty:
        news_df['publishedAt'] = pd.to_datetime(news_df['publishedAt'])
        news_df.set_index('publishedAt', inplace=True)
        news_df = news_df[['symbol', 'title', 'url']]
        news_df.drop_duplicates(inplace=True)
    
    return stocks_df, news_df

# Create a line chart to show the historical close prices
def create_line_chart(selected_tickers, stocks_df):
    # Define a list of colors for the line traces
    colors = ['#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845']

    # Create a new figure object
    fig = go.Figure()

    # Add a line trace for each selected ticker
    for i, ticker in enumerate(selected_tickers):
        stock_df = stocks_df[ticker]
        fig.add_trace(
            go.Scatter(
                x=stock_df.index,
                y=stock_df['Close'],
                mode='lines',
                name=ticker,
                line=dict(color=colors[i])
            )
        )

    # Set the chart title and axis labels
    fig.update_layout(
        title="Close Price of Selected Stocks",
        xaxis_title="Date",
        yaxis_title="Close Price"
    )

    # Show the chart
    st.plotly_chart(fig)

# Create a chart to show the relative returns of selected stocks
def relative_returns(selected_tickers, stocks_df):
    # Define colors
    bar_colors = ['#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845']

    # Create a list to hold the traces
    traces = []

    # Loop through the selected tickers
    for i, ticker in enumerate(selected_tickers):
        stock_df = stocks_df[ticker].copy()
        stock_df.loc[:, "returns"] = stock_df["Close"].pct_change()
        traces.append(
            go.Bar(
                x=stock_df.index,
                y=stock_df["returns"],
                name=ticker,
                marker=dict(color=bar_colors[i % len(bar_colors)])
            )
        )

    # Create the layout
    layout = go.Layout(
        title="Relative Returns of Selected Stocks",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Relative Return (%)"),
        barmode="group",
        plot_bgcolor='#0D5943',
        paper_bgcolor='#0D5943',
        font=dict(color='#FFFFFF')
    )

    # Create the figure
    fig = go.Figure(data=traces, layout=layout)

    # Pass the figure object to st.plotly_chart
    st.plotly_chart(fig)

    # Create the figure
    fig = go.Figure(data=traces, layout=layout)

# Create a scatter plot to show the historical close prices of selected stocks
def create_scatter_plot(selected_tickers, stocks_df):
    # Create new figure object
    fig, ax = plt.subplots()
    for ticker in selected_tickers:
        stock_df = stocks_df[ticker]
        plt.scatter(stock_df.index, stock_df["Close"], label=ticker)
    plt.title("Historical Close Prices of Selected Stocks")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()   
    # Pass the figure object to st.pyplot
    st.pyplot(fig)

# Create a volatility analysis based on selected stocks
def create_volatility_analysis(selected_tickers, stocks_df):
    for ticker in selected_tickers:
        stock_df = stocks_df[ticker]
        stock_df.drop(stock_df.index[0], inplace=True)
        stock_df["returns"] = stock_df["Close"].pct_change()
        volatility = stock_df["returns"].std() * np.sqrt(252)
        volatility_pct = volatility * 100
        st.write("Volatility of " + ticker + ": " + "{:.2f}%".format(volatility_pct))

st.markdown("---")

# create information related to line charts of historical prices 
st.markdown(
    """
    <h2>Line Chart of Historic Close Prices</h2>
    <p>A line chart of historical close prices is a useful tool for finance analysts when analysing stocks. 
    It allows for the visualisation of the stock's performance over a period of time. This can provide insight 
    into trends and patterns in the stock's performance, helping analysts to make informed decisions about 
    whether to buy, hold, or sell the stock.</p>
    <p>For example, an upward trend in the line chart may indicate that the stock's value is increasing and may 
    be a good time to buy, while a downward trend may indicate the opposite. Additionally, the line chart provided
    below can be used to compare the performance of multiple stocks.</p>
    """
, unsafe_allow_html=True)

# provide an error if two stocks are not selected within the dropdown
if len(selected_tickers) < 2:
    st.error("Please select at least 2 stocks to create a line chart.")
else:
    stocks_df = get_stock_data(selected_tickers)
    # Call the create_line_chart function
    if selected_tickers:
        create_line_chart(selected_tickers, stocks_df)

st.markdown("---")

# Create information related to relative returns chart
st.markdown(
    """
<h2>Relative Returns Chart</h2>
<p>A relative returns chart is a graphical representation of the performance of multiple stocks over a specified 
period of time relative to a benchmark or reference point. The x-axis typically represents time, and the y-axis 
represents the percentage change in price relative to the benchmark or reference point.</p>
<p>The chart below shows the relative performance of the selected stocks over the past year. Positive values 
indicate that the stock has generated a positive return, while negative values indicate that the stock has generated 
a negative return.</p>
<p>This type of chart can provide valuable insights into how a particular stock or sector has performed 
relative to a benchmark or reference point over time. It can also be used to identify trends in outperformance 
or underperformance, and to help make informed investment decisions.</p>
    """
, unsafe_allow_html=True)

# provide an error if two stocks are not selected within the dropdown
if len(selected_tickers) < 2:
    st.error("Please select at least 2 stocks to create a Historical Close Price Line Chart.")
else:
    # Call the relative_returns function
    if selected_tickers:
        relative_returns(selected_tickers, stocks_df)

st.markdown("---")

# provide information related to volatitly analysis
st.markdown(
    """
    <h2>Volatility Analysis</h2>
    <p>Volatility analysis, also known as a Volatility Indicator, is a useful tool for finance professionals
    to assess the risk of a stock. It is a measure of the dispersion of returns for a given stock over a 
    period of time. The higher the volatility, the greater the risk and potential for large returns. 
    Understanding volatility can help analysts make informed investment decisions and manage portfolio risk.</p>
    <p>A lower volatility percentage generally indicates a more stable stock, while a higher volatility percentage 
    suggests a stock with more potential for high returns but also a greater potential for losses. Analysts can use 
    this information to construct a diversified portfolio that balances risk and return.</p>
    <p>In this project, we use the standard deviation of daily returns to calculate the volatility of a stock. 
    This value is then annualised by multiplying by the square root of the number of trading days in a year (252). 
    The resulting number is presented as a percentage, making it easy to compare the volatility of different stocks.</p>
    """
, unsafe_allow_html=True)

st.markdown("---")

# provide an error if two stocks are not selected within the dropdown
if len(selected_tickers) < 2:
    st.error("Please select at least 2 stocks to create a volatility analysis.")
else:
    stocks_df = get_stock_data(selected_tickers)
    create_volatility_analysis(selected_tickers, stocks_df)

st.markdown("---")

st.markdown(
    """
    <h2>Sentiment Analysis of Stocks</h2>
    <p>Sentiment analysis of stocks is a technique used to identify and extract subjective information from financial
    news and social media sources and this can be used in conjunction with examples provided above to understand the
    risk and opportunities a given stock may have. </p>
    <p>The key benefits of sentiment analysis on businesses and their respective stock from a technical standpoint
    include the ability to quickly and efficiently process large amounts of data, identify patterns and trends, and 
    make data-driven decisions. However, it is important to note that sentiment analysis is not a perfect technique 
    and has limitations such as subjectivity, language nuances, and the possibility of biassed or unreliable data 
    sources.</p>
    """
, unsafe_allow_html=True)

st.markdown("<p><strong>This element is in development</strong></p>", unsafe_allow_html=True)

st.markdown("---")

# provide information related to interpretin analysis of stocks
st.markdown("""
<h2>Interpreting Average Sentiment Scores for Stocks</h2>
<p>By understanding how people feel about a stock, investors and analysts can make more informed decisions about 
whether to buy or sell shares.</p>
<p>Within this project we visualise sentiment data by creating a bar chart of average sentiment scores. 
The x-axis of the chart represents different time periods (e.g. days, weeks, months) and the y-axis represents the
average sentiment score for that period. A score of 0 represents neutral sentiment, while a score above 0 indicates 
positive sentiment and a score below 0 indicates negative sentiment, which can be seen within the below Average 
Sentiment of News Articles chart.</p>
""", unsafe_allow_html=True)

st.markdown("<p><strong>This element is in development</strong></p>", unsafe_allow_html=True)

st.markdown("---")