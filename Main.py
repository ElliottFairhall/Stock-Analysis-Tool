import requests
from PIL import Image
import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
from bs4 import BeautifulSoup
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import os

PAGE_TITLE = "Data Engineer, Educator Analyst and Technology Enthusiast"

PAGE_ICON = ":chart_with_upwards_trend:"

# Set the title and icon of the application
st.set_page_config(page_title = PAGE_TITLE, page_icon = PAGE_ICON, layout="wide")

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
<p>The dropdown below allows users of this project to select multiple businesses from a list. In this project, the dropdown is used to select the stocks that will be analysed. The businesses that are provided include Apple Inc. (AAPL), Tesla Inc. (TSLA), Microsoft Corp. (MSFT), Alphabet Inc. (GOOGL), Amazon Inc. (AMZN), Facebook Inc. (FB), Alibaba Group Holding Ltd. (BABA), Wal-Mart Stores Inc. (WMT), General Electric Co. (GE), JPMorgan Chase & Co. (JPM), Taiwan Semiconductor Manufacturing Co. Ltd. (TSM), Comcast Corp. (CMCSA), Chevron Corp. (CVX), Procter & Gamble Co. (PG), Boeing Co. (BA), Intel Corp. (INTC), Cisco Systems Inc. (CSCO), and Pfizer Inc. (PFE). By selecting two or more of these stocks, users can gain a deeper understanding of the performance and see the potential of these companies.</p>
""", unsafe_allow_html=True)

# Create a multi-select box for the user to select stock tickers
selected_tickers = st.multiselect("Select stocks to analyse", ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "FB", "BABA", "WMT", "GE", "JPM", "TSM", "WMT", "CMCSA", "CVX", "PG", "WMT", "BA", "INTC", "CSCO", "PFE"], default=["MSFT","TSLA"])
if len(selected_tickers) < 2:
    st.error("Please select at least 2 stocks.")

# Concatenate the selected tickers into a single string for use in the API call
ticker_string = ','.join(selected_tickers)

@st.cache(ttl=3600) # ttl = time to live in seconds
def get_stock_data(ticker_string):
    stocks_df = yf.download(ticker_string, period='max', group_by='ticker')
    # Clean the data
    stocks_df.dropna(inplace=True)
    return stocks_df

# Create a line chart to show the historical close prices
def create_line_chart(selected_tickers, stocks_df):
    for ticker in selected_tickers:
        stock_df = stocks_df[ticker]
        plt.plot(stock_df['Close'], label=ticker)
    plt.title("Close Price of Selected Stocks")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    st.pyplot()

# Create a bar chart to show the relative returns of selected stocks
def create_bar_chart(selected_tickers, stocks_df):
        for ticker in selected_tickers:
            stock_df = stocks_df[ticker]
            stock_df["returns"] = stock_df["Close"].pct_change()
            plt.bar(stock_df.index, stock_df["returns"], label=ticker)
            plt.title("Relative Returns of Selected Stocks")
            plt.xlabel("Date")
            plt.ylabel("Relative Return (%)")
            plt.legend()
            st.pyplot()           

# Create a scatter plot to show the historical close prices of selected stocks
def create_scatter_plot(selected_tickers, stocks_df):
    for ticker in selected_tickers:
        stock_df = stocks_df[ticker]
        plt.scatter(stock_df.index, stock_df["Close"], label=ticker)
    plt.title("Historical Close Prices of Selected Stocks")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()   
    st.pyplot()

# Create a volatility analysis based on selected stocks
def create_volatility_analysis(selected_tickers, stocks_df):
    for ticker in selected_tickers:
        stock_df = stocks_df[ticker]
        stock_df.drop(stock_df.index[0], inplace=True)
        stock_df["returns"] = stock_df["Close"].pct_change()
        volatility = stock_df["returns"].std() * np.sqrt(252)
        volatility_pct = volatility * 100
        st.write("Volatility of " + ticker + ": " + "{:.2f}%".format(volatility_pct))

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
    create_line_chart(selected_tickers, stocks_df)

# create information related to line charts of historical prices 
st.markdown(
    """
    <h2>Line Chart of Historic Close Prices</h2>
    <p>A historical close price line chart is a graphical representation of a stock's historical closing price over a 
    specified period of time. The x-axis typically represents time, and the y-axis represents the closing price. 
    The closing price is the price at which a stock is traded when the market closes for the day. 
    Within the below historical close price line chart, I have maintained this principle providing the year within 
    the x-axis and the close price within the y-axis.</p>
    <p>This type of chart can provide valuable insights into a stock's historical performance, such as trends in price
    movement, volatility, and overall market sentiment. It can also be used to compare the performance of different
    stocks or sectors. Additionally, the historical close price line chart provided below can be used to compare the
    performance of multiple stocks over a period of years.</p>
    """
, unsafe_allow_html=True)

# provide an error if two stocks are not selected within the dropdown
if len(selected_tickers) < 2:
    st.error("Please select at least 2 stocks to create a Historical Close Price Line Chart.")
else:
    stocks_df = get_stock_data(selected_tickers)
    create_scatter_plot(selected_tickers, stocks_df)

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

# provide information related to related news and the extraction of news articles
st.markdown(
    """
    <h2>Recent News for the selected stock</h2>
    <p>With the help of <a href='https://newsapi.org/'>newsapi.org</a>, we can extract recent news articles 
    related to the selected stocks chosen above. These articles can give us valuable insights into the current market sentiment 
    and news surrounding the stock.</p>
    <p>It is important to note that while these articles may give a general idea of the sentiment, it is not a 
    comprehensive analysis and should be used in conjunction with other technical and fundamental analysis.</p>
    """
    , unsafe_allow_html=True)

# extract news from newapi.org
def extract_news_articles(selected_tickers):
    news_url = f"https://newsapi.org/v2/everything?q={selected_tickers}&sortBy=relevancy&apiKey={News_API}"
    news_data = requests.get(news_url).json()
    news_articles = []
    for article in news_data["articles"]:
        news_articles.append(article["title"] + " - " + article["description"])
    return news_articles

# analyse news sentiment based off of the news articles returned 
def analyze_news_sentiment(selected_tickers):
    analyzer = SentimentIntensityAnalyzer()
    news_articles = extract_news_articles(selected_tickers) # function to extract news articles related to the stock
    sentiments = []
    for article in news_articles:
        sentiment = analyzer.polarity_scores(article)
        sentiments.append(sentiment)
    return sentiments

# provide information related to sentiment analysis of stocks
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

# display extracted news articles
news_articles = extract_news_articles(selected_tickers)

# display the stocks selected related to the extracted news articles
tickers_string = ', '.join(selected_tickers)

# provide an error if two stocks are not selected within the dropdown
if len(selected_tickers) < 2:
    st.error("Please select at least 2 stocks to provide recent news articles.")
else:
    st.write("Recent news articles for " + tickers_string + ":")
    st.write("\n".join(news_articles))

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

# create sentiment bar chat
def create_sentiment_bar_chart(sentiments, selected_tickers):
    # Get the average sentiment scores
    compound_sentiments = [sentiment["compound"] for sentiment in sentiments]
    if len(compound_sentiments) > 0:
        mean_sentiment = round(sum(compound_sentiments) / len(compound_sentiments), 2)
    else:
        mean_sentiment = 0

# display sentiment bar chart
    plt.bar(["Sentiment"], [mean_sentiment])
    plt.title(f"Average Sentiment of News Articles for {selected_tickers}")
    plt.xlabel("Sentiment")
    plt.ylabel("Mean Score")
    st.pyplot()
    # provide an error if no sentiment found for a selected ticker
    if len(compound_sentiments) == 0:
        st.write("No Sentiment Found for "+ ",".join(selected_tickers))

# provide an error if two stocks are not selected within the dropdown
if len(selected_tickers) < 2:
    st.error("Please select at least 2 stocks to compare sentiment.")
else:
    sentiments = analyze_news_sentiment(selected_tickers)
    create_sentiment_bar_chart(sentiments, selected_tickers)