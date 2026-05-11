import datetime

import yfinance as yf
import pandas as pd


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def sma50_distance(close_series: pd.Series) -> float:
    sma50 = close_series.rolling(50).mean()
    return float((close_series.iloc[-1] / sma50.iloc[-1] - 1) * 100)


def is_active(df: pd.DataFrame, max_days_stale: int = 14) -> bool:
    if df is None or df.empty:
        return False
    last_date = df.index[-1].date()
    return (datetime.date.today() - last_date).days <= max_days_stale


def revenue_growth_3y(ticker_obj: yf.Ticker, years: int = 3) -> float | None:
    income = ticker_obj.income_stmt
    if income is None or income.empty or "Total Revenue" not in income.index:
        return None
    revenue = income.loc["Total Revenue"].dropna().sort_index()
    if len(revenue) < years + 1:
        return None
    growth = revenue.iloc[-(years + 1):].pct_change().dropna()
    return float(growth.mean())


_industry_pe_cache: dict[str, float | None] = {}


def industry_average_pe(industry_key: str, max_peers: int = 10) -> float | None:
    if industry_key in _industry_pe_cache:
        return _industry_pe_cache[industry_key]
    try:
        peers = yf.Industry(industry_key).top_companies
    except Exception:
        peers = None
    avg: float | None = None
    if peers is not None and len(peers) > 0:
        pes: list[float] = []
        for sym in list(peers.index[:max_peers]):
            try:
                pe = yf.Ticker(sym).info.get("trailingPE")
                if pe and pe > 0:
                    pes.append(float(pe))
            except Exception:
                pass
        if pes:
            avg = sum(pes) / len(pes)
    _industry_pe_cache[industry_key] = avg
    return avg


def pe_vs_industry(ticker_obj: yf.Ticker) -> tuple[float | None, float | None]:
    info = ticker_obj.info
    pe = info.get("trailingPE")
    industry_key = info.get("industryKey")
    if not pe or pe <= 0 or not industry_key:
        return (float(pe) if pe else None, None)
    return (float(pe), industry_average_pe(industry_key))


PE_OVERPRICED_MULTIPLIER = 1.2
MIN_REVENUE_GROWTH = 0.05


def scan_tickers(tickers: list[str]) -> list[dict]:
    buyable = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if not is_active(df):
                print(f"{ticker} DELISTED or no recent data | Signal: -")
                continue
            close = df["Close"].squeeze()
            rsi = float(compute_rsi(close).iloc[-1])
            if rsi >= 40:
                print(f"{ticker} RSI: {rsi:.2f} | Signal: - (RSI not oversold)")
                continue
            sma_dist = sma50_distance(close)
            if sma_dist <= 0:
                print(f"{ticker} RSI: {rsi:.2f} | Trend: DOWN | Signal: - (below SMA50)")
                continue
            ticker_obj = yf.Ticker(ticker)
            rev_growth = revenue_growth_3y(ticker_obj)
            if rev_growth is None or rev_growth < MIN_REVENUE_GROWTH:
                rg_str = f"{rev_growth * 100:.1f}%" if rev_growth is not None else "N/A"
                print(f"{ticker} RSI: {rsi:.2f} | Trend: UP | RevGrow3y: {rg_str} | Signal: - (revenue not growing)")
                continue
            pe, industry_pe = pe_vs_industry(ticker_obj)
            if pe and industry_pe and pe > industry_pe * PE_OVERPRICED_MULTIPLIER:
                print(f"{ticker} RSI: {rsi:.2f} | PE: {pe:.1f} vs Ind {industry_pe:.1f} | Signal: - (overpriced)")
                continue
            pe_discount = ((industry_pe - pe) / industry_pe * 100) if (pe and industry_pe) else None
            pe_str = f"{pe:.1f}" if pe else "N/A"
            ind_pe_str = f"{industry_pe:.1f}" if industry_pe else "N/A"
            print(f"{ticker} RSI: {rsi:.2f} | Trend: UP +{sma_dist:.1f}% | RevGrow3y: {rev_growth * 100:.1f}% | PE: {pe_str} vs Ind {ind_pe_str} | Signal: BUY")
            buyable.append({
                "ticker": ticker,
                "rsi": round(rsi, 2),
                "trend": "UP",
                "pct_above_sma50": round(sma_dist, 2),
                "rev_growth_3y": round(rev_growth * 100, 1),
                "pe": round(pe, 2) if pe else None,
                "industry_pe": round(industry_pe, 2) if industry_pe else None,
                "pe_discount": round(pe_discount, 1) if pe_discount is not None else None,
            })
        except:
            pass
    return buyable
