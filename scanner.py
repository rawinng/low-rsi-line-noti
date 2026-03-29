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


def is_long_term_uptrend(close_series: pd.Series) -> bool:
    ema200 = close_series.ewm(span=200, adjust=False).mean()
    return float(close_series.iloc[-1]) > float(ema200.iloc[-1])



def scan_tickers(tickers: list[str]) -> list[dict]:
    buyable = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            close = df["Close"].squeeze()
            rsi = float(compute_rsi(close).iloc[-1])
            upside = is_upside(close)
            long_term_up = is_long_term_uptrend(close)
            trend = "UP" if upside else "DOWN"
            signal = "BUY" if rsi < 40 and upside and long_term_up else "-"
            print(f"{ticker} RSI: {rsi:.2f} | Trend: {trend} | EMA200: {'UP' if long_term_up else 'DOWN'} | Signal: {signal}")

            if rsi < 40 and upside and long_term_up:
                buyable.append({"ticker": ticker, "rsi": round(rsi, 2), "trend": trend})
        except:
            pass
    return buyable
