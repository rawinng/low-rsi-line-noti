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
            t = yf.Ticker(ticker)
            info = t.info

            # 5-year capital gain
            hist = t.history(period="5y")
            if len(hist) >= 2:
                gain_5yr = round((hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100, 1)
            else:
                gain_5yr = None

            profit_margin = info.get("profitMargins")
            roe = info.get("returnOnEquity")

            market_cap = info.get("marketCap")
            price = info.get("currentPrice") or info.get("regularMarketPrice")

            rows.append({
                "ticker": ticker,
                "name": info.get("shortName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "gain_5yr": gain_5yr,
                "profit_margin": round(profit_margin * 100, 1) if profit_margin is not None else None,
                "roe": round(roe * 100, 1) if roe is not None else None,
                "market_cap": market_cap,
                "price": round(price, 2) if price is not None else None,
            })
        except:
            rows.append({"ticker": ticker, "name": "N/A", "sector": "N/A",
                         "gain_5yr": None, "profit_margin": None, "roe": None,
                         "market_cap": None, "price": None})
    return pd.DataFrame(rows)
