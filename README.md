
# Financial Analysis Techniques with Python

**This project is currently in development**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](elliottfairhall-stock-analysis-tool-main-pgogm7)

In this project, I will be showcasing various financial analysis techniques using Python. For this project I have utilized Python modules such as yfinance, matplotlib, streamlit and VaderSentiment to analyse stocks and extract news articles.

To visualise this information I have create a range of visualizations of historical stock data including visualisations relatd to calculated returns, analysed news article sentiment to gain a better understanding of the performance of stocks and historical close prices.

## Business Stock Dropdown

The dropdown within the application allows users of this project to select multiple businesses from a list. This project's dropdown is used to select the stocks that  will analysed and ultimately visualised. 

The businesses that are provided include:

-   Apple Inc. (AAPL)
-   Tesla Inc. (TSLA)
-   Microsoft Corp. (MSFT)
-   Alphabet Inc. (GOOGL)
-   Amazon Inc. (AMZN)
-   Facebook Inc. (FB)
-   Alibaba Group Holding Ltd. (BABA)
-   Wal-Mart Stores Inc. (WMT)
-   General Electric Co. (GE)
-   JPMorgan Chase & Co. (JPM)
-   Taiwan Semiconductor Manufacturing Co. Ltd. (TSM)
-   Comcast Corp. (CMCSA)
-   Chevron Corp. (CVX)
-   Procter & Gamble Co. (PG)
-   Boeing Co. (BA)
-   Intel Corp. (INTC)
-   Cisco Systems Inc. (CSCO)
-   Pfizer Inc. (PFE)

By selecting two or more of these stocks, users can gain a deeper understanding of their performance and potential.

## Data and Analysis

The script analyses the stocks in a variety of ways. Some of the methods are:

### Historical Close Prices Line Chart

A line chart showing the historical close prices of the selected stocks.

### Relative Returns Bar Chart

A bar chart that shows the relative returns of the selected stocks.

### Historical Close Prices Scatter Plot

A scatter plot that shows the historical close prices of the selected stocks.

### Volatility Analysis

A volatility analysis based on the selected stocks.

### Sentiment Analysis of Articles

We use the `yfinance` module to retrieve data and the `pandas` module to clean and prepare data for analysis. The `vaderSentiment` module is used for sentiment analysis of news articles.

## Requirements

To run this project locally, you will need to install the following modules:

-   requests
-   PIL
-   yfinance
-   matplotlib
-   streamlit
-   numpy
-   bs4
-   pathlib
-   vaderSentiment
-   dotenv

## Credits

This project was created by Elliott Fairhall
