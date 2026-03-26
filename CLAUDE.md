# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the script

```bash
# Activate the virtual environment (Python 3.11.9)
source .venv/bin/activate

# Run the scanner
python main.py

# Run with LINE notification enabled
LINE_NOTIFY_ENABLED=true python main.py
```

## Environment variables

Stored in `.env` (not committed). Load manually or via your shell before running:

| Variable | Purpose |
|---|---|
| `LINE_CHANNEL_ID` | LINE OA Channel ID |
| `LINE_CHANNEL_SECRET` | LINE OA Channel Secret |
| `LINE_NOTIFY_ENABLED` | Set to `true` to send LINE broadcast (default: `false`) |

## Architecture

This is a single-purpose script that scans S&P 500 stocks for low-RSI buying opportunities and broadcasts results to a LINE OA channel as a Flex Message carousel.

**Data flow:** `main.py` orchestrates four steps in sequence:
1. **`fetcher.py`** — scrapes S&P 500 tickers from Wikipedia, then fetches name + sector per ticker via `yfinance`
2. **`scanner.py`** — downloads 6 months of daily OHLCV per ticker, computes RSI-14 and 50-day SMA trend; returns tickers where `RSI < 40` and price is above SMA50
3. **`main.py`** — merges scan results with enriched stock info
4. **`notifier.py`** — obtains a short-lived LINE access token via `POST /v2/oauth/accessToken`, builds a `FlexCarousel` (max 12 bubbles per message), and broadcasts via `linebot.v3.messaging`

## Key behaviours

- **Token is fetched at runtime** — `notifier._get_token()` exchanges Channel ID + Secret for a token on every run; no token is stored.
- **LINE carousel limit** — `send_flex` chunks results into groups of 12 (LINE's max per carousel).
- **RSI colour coding** — green (`#22c55e`) when RSI < 30, amber (`#f59e0b`) when 30–40.
- **Testing subset** — `main.py` currently slices `tickers[:50]` for faster iteration; remove or adjust this for a full scan.
