import yfinance as yf
import pandas as pd


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def is_upside(close_series: pd.Series) -> bool:
    sma50 = close_series.rolling(50).mean()
    return float(close_series.iloc[-1]) > float(sma50.iloc[-1])


def scan_tickers(tickers: list[str]) -> list[dict]:
    buyable = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            close = df["Close"].squeeze()
            rsi = float(compute_rsi(close).iloc[-1])
            upside = is_upside(close)
            trend = "UP" if upside else "DOWN"
            signal = "BUY" if rsi < 40 and upside else "-"
            print(f"{ticker} RSI: {rsi:.2f} | Trend: {trend} | Signal: {signal}")

            if rsi < 40 and upside:
                buyable.append({"ticker": ticker, "rsi": round(rsi, 2), "trend": trend})
        except:
            pass
    return buyable
