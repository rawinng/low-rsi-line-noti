import time
import pandas as pd
from fetcher import get_sp500_tickers, get_stock_info
from scanner import scan_tickers
from notifier import send_flex, send_no_results


def main():
    start = time.time()
    tickers = get_sp500_tickers()
    ## less tickers for testing    
    print(f"Total tickers: {len(tickers)}")

    buyable = scan_tickers(tickers)

    print(f"\n=== Buyable stocks (RSI < 40 + Uptrend) ===")
    if not buyable:
        print("No buyable stocks found.")
        send_no_results()
        print(f"\nTotal time: {time.time() - start:.1f}s")
        return

    result = pd.DataFrame(buyable).sort_values(
        ["rsi", "pe_discount", "rev_growth_3y"],
        ascending=[True, False, False],
        na_position="last",
    ).head(10).reset_index(drop=True)
    info_df = get_stock_info(result["ticker"].tolist())
    result = result.merge(info_df, on="ticker", how="left")[
        ["ticker", "name", "sector", "rsi", "trend", "pct_above_sma50",
         "rev_growth_3y", "pe", "industry_pe", "pe_discount",
         "drawdown_52w", "profit_margin", "roe", "market_cap", "price"]
    ]
    print(result)

    send_flex(result)
    print(f"\nTotal time: {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
