import yfinance as yf
import pandas as pd


def get_sp500_tickers() -> list[str]:    
    url = "https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax?fileType=csv&fileName=IVV_holdings&dataType=fund"
    df = pd.read_csv(url, skiprows=9)
    tickers = df[df["Asset Class"] == "Equity"]["Ticker"].dropna().tolist()
    return tickers


def get_stock_info(tickers: list[str]) -> pd.DataFrame:
    rows = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info

            # 1-year capital gain
            hist = t.history(period="1y")
            if len(hist) >= 2:
                gain_1yr = round((hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100, 1)
            else:
                gain_1yr = None

            profit_margin = info.get("profitMargins")
            roe = info.get("returnOnEquity")

            market_cap = info.get("marketCap")
            price = info.get("currentPrice") or info.get("regularMarketPrice")

            rows.append({
                "ticker": ticker,
                "name": info.get("shortName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "gain_1yr": gain_1yr,
                "profit_margin": round(profit_margin * 100, 1) if profit_margin is not None else None,
                "roe": round(roe * 100, 1) if roe is not None else None,
                "market_cap": market_cap,
                "price": round(price, 2) if price is not None else None,
            })
        except:
            rows.append({"ticker": ticker, "name": "N/A", "sector": "N/A",
                         "gain_1yr": None, "profit_margin": None, "roe": None,
                         "market_cap": None, "price": None})
    return pd.DataFrame(rows)
