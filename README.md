
# Financial Analysis Techniques with Python

In this project, we are showcasing various financial analysis techniques using Python. We utilize the yfinance, matplotlib, streamlit and VaderSentiment modules to analyse stocks and extract news articles.

We create visualizations of historical stock data, calculate returns, and analyse news article sentiment to gain a better understanding of the performance of stocks.

## Business Stock Dropdown

The dropdown below allows users of this project to select multiple businesses from a list. This project's dropdown is used to select the stocks that we will analyse. The businesses that are provided include:

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

We use the `yfinance` module to retrieve data and the `pandas` module to clean and prepare data for analysis. The `vaderSentiment` module is used for sentiment analysis of news articles.

## Requirements

To run the project, you will need to install the following modules:

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