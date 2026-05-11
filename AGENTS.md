# AGENTS.md

Guidance for AI coding agents working in this repository.

## Running the script

```bash
# Activate the virtual environment (Python 3.11.9)
source .venv/bin/activate

# Run the scanner
python main.py

# Run with Telegram notification enabled
TELEGRAM_NOTIFY_ENABLED=true python main.py
```

## Environment variables

Stored in `.env` (not committed). Load manually or via your shell before running:

| Variable | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token (from @BotFather) |
| `TELEGRAM_CHAT_ID` | Telegram chat/channel ID to send messages to |
| `TELEGRAM_NOTIFY_ENABLED` | Set to `true` to send Telegram notification (default: `false`) |

## Architecture

This is a single-purpose script that scans S&P 500 stocks for low-RSI buying opportunities and sends results to a Telegram chat/channel.

**Data flow:** `main.py` orchestrates four steps in sequence:
1. **`fetcher.py`** — scrapes S&P 500 tickers from Wikipedia, then fetches name + sector per ticker via `yfinance`
2. **`scanner.py`** — downloads 1 year of daily OHLCV per ticker, computes RSI-14 and 50-day SMA trend; returns tickers where `RSI < 40` and price is above SMA50
3. **`main.py`** — merges scan results with enriched stock info
4. **`notifier.py`** — sends HTML-formatted messages to Telegram via the Bot API (`sendMessage`)

## Key behaviours

- **Telegram Bot API** — uses `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to send messages; no webhook needed.
- **Message splitting** — if the combined message exceeds Telegram's 4096-char limit, stocks are sent as individual messages.
- **RSI emoji coding** — 🟢 when RSI < 30, 🟡 when 30–40.
- **Testing subset** — `main.py` currently slices `tickers[:50]` for faster iteration; remove or adjust this for a full scan.