import io
import yfinance as yf
import pandas as pd
import requests


def get_sp500_tickers() -> list[str]:
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers=headers
    ).text
    return pd.read_html(io.StringIO(html))[0]["Symbol"].tolist()


def get_stock_info(tickers: list[str]) -> pd.DataFrame:
    rows = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            rows.append({
                "ticker": ticker,
                "name": info.get("shortName", "N/A"),
                "sector": info.get("sector", "N/A"),
            })
        except:
            rows.append({"ticker": ticker, "name": "N/A", "sector": "N/A"})
    return pd.DataFrame(rows)
