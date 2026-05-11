import os
import pandas as pd
import requests


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_NOTIFY_ENABLED = os.environ.get("TELEGRAM_NOTIFY_ENABLED", "false").lower() == "true"


def _fmt(value, suffix="%", fallback="N/A") -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return fallback
    return f"{value}{suffix}"


def _fmt_mcap(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.1f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    return f"${value / 1_000_000:.0f}M"


def _rsi_emoji(rsi: float) -> str:
    return "🟢" if rsi < 30 else "🟡"


def _drawdown_emoji(drawdown) -> str:
    if not isinstance(drawdown, (int, float)):
        return ""
    if drawdown <= -20:
        return "🔻"
    if drawdown <= -10:
        return "🟠"
    return "🟡"


def _send_message(text: str, parse_mode: str = "HTML") -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode
    })
    resp.raise_for_status()


def _build_stock_message(row: dict) -> str:
    rsi_icon = _rsi_emoji(row["rsi"])
    drawdown = row.get("drawdown_52w")
    drawdown_icon = _drawdown_emoji(drawdown)

    lines = [
        f"<b>{row['ticker']}</b> — {row.get('name', '')}",
        f"Sector: {row.get('sector', 'N/A')}",
        f"",
        f"{rsi_icon} RSI (14): <b>{row['rsi']}</b>",
        f"Trend: {row['trend']} ({_fmt(row.get('pct_above_sma50'), suffix='%')} vs SMA50)",
        f"Rev Growth (3y avg): {_fmt(row.get('rev_growth_3y'), suffix='%')}",
        f"PE: {_fmt(row.get('pe'), suffix='')} vs Ind {_fmt(row.get('industry_pe'), suffix='')} ({_fmt(row.get('pe_discount'), suffix='%')} disc.)",
        f"{drawdown_icon} Off 52w High: <b>{_fmt(drawdown, suffix='%')}</b>",
        f"Net Margin: {_fmt(row.get('profit_margin'), suffix='%')}",
        f"ROE: {_fmt(row.get('roe'), suffix='%')}",
        f"Price: {_fmt(row.get('price'), suffix='')}",
        f"Mkt Cap: {_fmt_mcap(row.get('market_cap'))}",
        f"",
        f'<a href="https://finance.yahoo.com/quote/{row["ticker"]}">View on Y!Finance</a>',
    ]
    return "\n".join(lines)


def send_no_results() -> None:
    if not TELEGRAM_NOTIFY_ENABLED:
        print("TELEGRAM_NOTIFY_ENABLED is not set to 'true' — skipping Telegram notification.")
        return

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — skipping Telegram notification.")
        return

    _send_message("No buyable stocks found today.")
    print("Sent 'no results' notification to Telegram.")


def send_flex(result_df: pd.DataFrame) -> None:
    if not TELEGRAM_NOTIFY_ENABLED:
        print("TELEGRAM_NOTIFY_ENABLED is not set to 'true' — skipping Telegram notification.")
        return

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — skipping Telegram notification.")
        return

    rows = result_df.to_dict("records")

    header = "📊 <b>Low RSI Watchlist — Buyable Stocks</b>\n"
    messages = [_build_stock_message(row) for row in rows]
    full_text = header + "\n" + ("\n\n" + "—" * 20 + "\n\n").join(messages)

    # Telegram message limit is 4096 chars; split if needed
    if len(full_text) <= 4096:
        _send_message(full_text)
        print(f"Sent {len(rows)} stock(s) to Telegram.")
    else:
        # Send header + stocks individually
        _send_message(header)
        for msg in messages:
            _send_message(msg)
        print(f"Sent {len(rows)} stock(s) to Telegram (individual messages).")
