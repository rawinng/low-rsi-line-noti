import pandas as pd
from fetcher import get_sp500_tickers, get_stock_info
from scanner import scan_tickers
from notifier import send_flex


def main():
    tickers = get_sp500_tickers()
    ## less tickers for testing    
    print(f"Total tickers: {len(tickers)}")

    buyable = scan_tickers(tickers)

    print(f"\n=== Buyable stocks (RSI < 40 + Uptrend) ===")
    if not buyable:
        print("No buyable stocks found.")
        return

    result = pd.DataFrame(buyable).sort_values("rsi").head(10).reset_index(drop=True)
    info_df = get_stock_info(result["ticker"].tolist())
    result = result.merge(info_df, on="ticker", how="left")[
        ["ticker", "name", "sector", "rsi", "trend", "gain_1yr", "profit_margin", "roe", "market_cap", "price"]
    ]
    print(result)

    send_flex(result)


if __name__ == "__main__":
    main()
