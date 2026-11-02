# Stock comparison

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://elliottfairhall-stock-analysis-tool-main-pgogm7.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Compare up to eight stocks over a period of your choice: how they moved, how bumpy the ride was, how they relate to each
other and what recent headlines say. Built with Streamlit, yfinance and Plotly.

## What it does

- A list of 45 large companies with logos, sector filter and search by name; any other ticker can be typed in
- Summary table with price, one-day change, period return, volatility, worst fall and a trend sparkline
- Growth-of-100 or price chart, with the S&P 500 as an optional benchmark and periods from 1 month to the full history
- Risk and return scatter, plus Drawdown, Rolling volatility, Correlation and Daily returns tabs
- Headlines from Yahoo Finance's RSS feed, filtered for relevance and scored with VADER plus a finance word list; filter
  by stock and tone

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Needs Python 3.11 or newer. The theme follows your system's light or dark setting and is defined in
`.streamlit/config.toml`.

## Test it

```bash
pip install -e ".[dev]"
pytest
```

The tests cover the analysis code, the page itself (run headlessly with Streamlit's `AppTest`) and the dependency pins:
`tests/test_pillow_security_*.py` fails if Pillow is capped below 13 or Python 3.10 is allowed, because older Pillow
releases carry known security advisories.

## Notes

Prices come from Yahoo Finance through `yfinance` and can be delayed or incomplete. yfinance's own news endpoint
currently returns nothing, so headlines are read from Yahoo's public RSS feed instead. Company logos are site icons
fetched by your browser from Google's favicon service. This is not investment advice.

`check_yfinance.py` is a manual script that tests the live connection; the automated tests never touch the network.

Part of [Data Flakes](https://www.data-flakes.dev/).
