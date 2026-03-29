import os
import pandas as pd
import requests

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    BroadcastRequest,
    FlexMessage,
    FlexCarousel,
    FlexBubble,
    FlexBox,
    FlexText,
    FlexSeparator,
    FlexButton,
    URIAction,
)

LINE_CHANNEL_ID     = os.environ.get("LINE_CHANNEL_ID", "")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_NOTIFY_ENABLED = os.environ.get("LINE_NOTIFY_ENABLED", "false").lower() == "true"


def _get_token() -> str:
    resp = requests.post(
        "https://api.line.me/v2/oauth/accessToken",
        data={
            "grant_type": "client_credentials",
            "client_id": LINE_CHANNEL_ID,
            "client_secret": LINE_CHANNEL_SECRET,
        }
    )
    return resp.json()["access_token"]


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


_SECTOR_COLORS = {
    "Technology":             "#1d4ed8",  # blue
    "Health Care":            "#0f766e",  # teal
    "Financial Services":       "#1e3a5f",  # navy
    "Consumer Defensive":       "#b45309",  # amber-brown
    "Consumer Staples":       "#4d7c0f",  # olive green
    "Industrials":            "#374151",  # steel grey
    "Energy":                 "#92400e",  # dark orange
    "Utilities":              "#5b21b6",  # purple
    "Real Estate":            "#be185d",  # pink
    "Materials":              "#065f46",  # dark green
    "Communication Services": "#1e40af",  # indigo
}
_DEFAULT_SECTOR_COLOR = "#1e293b"


def _build_bubble(row: dict) -> FlexBubble:
    rsi_color = "#22c55e" if row["rsi"] < 30 else "#f59e0b"
    header_color = _SECTOR_COLORS.get(row.get("sector", ""), _DEFAULT_SECTOR_COLOR)
    gain = row.get("gain_1yr")
    gain_color = "#22c55e" if isinstance(gain, (int, float)) and gain >= 0 else "#ef4444"
    return FlexBubble(
        size="kilo",
        header=FlexBox(
            layout="vertical",
            background_color=header_color,
            contents=[
                FlexText(text=row["ticker"], weight="bold", size="xl", color="#ffffff"),
                FlexText(text=row["name"], size="xs", color="#94a3b8", wrap=True),
            ],
        ),
        body=FlexBox(
            layout="vertical",
            spacing="sm",
            contents=[
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(text="Sector", size="sm", color="#64748b", flex=2),
                        FlexText(text=row["sector"], size="sm", color="#0f172a", flex=3, wrap=True),
                    ],
                ),
                FlexSeparator(),
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(text="RSI (14)", size="sm", color="#64748b", flex=2),
                        FlexText(text=str(row["rsi"]), size="sm", color=rsi_color, weight="bold", flex=3),
                    ],
                ),
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(text="Trend", size="sm", color="#64748b", flex=2),
                        FlexText(text=row["trend"], size="sm", color="#0f172a", flex=3),
                    ],
                ),
                FlexSeparator(),
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(text="1yr Gain", size="sm", color="#64748b", flex=2),
                        FlexText(
                            text=_fmt(gain, suffix="%"),
                            size="sm", color=gain_color, weight="bold", flex=3,
                        ),
                    ],
                ),
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(text="Net Margin", size="sm", color="#64748b", flex=2),
                        FlexText(text=_fmt(row.get("profit_margin"), suffix="%"), size="sm", color="#0f172a", flex=3),
                    ],
                ),
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(text="ROE", size="sm", color="#64748b", flex=2),
                        FlexText(text=_fmt(row.get("roe"), suffix="%"), size="sm", color="#0f172a", flex=3),
                    ],
                ),
                FlexSeparator(),
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(text="Price", size="sm", color="#64748b", flex=2),
                        FlexText(text=_fmt(row.get("price"), suffix=""), size="sm", color="#0f172a", flex=3),
                    ],
                ),
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(text="Mkt Cap", size="sm", color="#64748b", flex=2),
                        FlexText(text=_fmt_mcap(row.get("market_cap")), size="sm", color="#0f172a", flex=3),
                    ],
                ),
            ],
        ),
        footer=FlexBox(
            layout="vertical",
            contents=[
                FlexButton(
                    action=URIAction(
                        label="View on Y!Finance",
                        uri=f"https://finance.yahoo.com/quote/{row['ticker']}",
                    ),
                    style="primary",
                    color="#1e293b",
                    height="sm",
                ),
            ],
        ),
    )


def send_no_results() -> None:
    if not LINE_NOTIFY_ENABLED:
        print("LINE_NOTIFY_ENABLED is not set to 'true' — skipping LINE notification.")
        return

    if not LINE_CHANNEL_ID or not LINE_CHANNEL_SECRET:
        print("LINE_CHANNEL_ID / LINE_CHANNEL_SECRET not set — skipping LINE notification.")
        return

    token = _get_token()
    bubble = FlexBubble(
        size="kilo",
        header=FlexBox(
            layout="vertical",
            background_color="#1e293b",
            contents=[
                FlexText(text="Low RSI Scanner", weight="bold", size="xl", color="#ffffff"),
                FlexText(text="Daily Scan Result", size="xs", color="#94a3b8"),
            ],
        ),
        body=FlexBox(
            layout="vertical",
            spacing="sm",
            contents=[
                FlexText(
                    text="No buyable stocks found today.",
                    size="sm",
                    color="#64748b",
                    wrap=True,
                ),
                FlexText(
                    text="No S&P 500 stocks currently meet the RSI < 40 + uptrend criteria.",
                    size="xs",
                    color="#94a3b8",
                    wrap=True,
                ),
            ],
        ),
    )
    flex_msg = FlexMessage(
        alt_text="Low RSI Scanner — No buyable stocks today",
        contents=FlexCarousel(type="carousel", contents=[bubble]),
    )
    with ApiClient(Configuration(access_token=token)) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.broadcast(BroadcastRequest(messages=[flex_msg]))
        print("Sent 'no results' notification to LINE OA.")


def send_flex(result_df: pd.DataFrame) -> None:
    if not LINE_NOTIFY_ENABLED:
        print("LINE_NOTIFY_ENABLED is not set to 'true' — skipping LINE notification.")
        return

    if not LINE_CHANNEL_ID or not LINE_CHANNEL_SECRET:
        print("LINE_CHANNEL_ID / LINE_CHANNEL_SECRET not set — skipping LINE notification.")
        return

    token = _get_token()
    rows = result_df.to_dict("records")
    chunks = [rows[i:i + 12] for i in range(0, len(rows), 12)]

    with ApiClient(Configuration(access_token=token)) as api_client:
        line_bot_api = MessagingApi(api_client)
        for chunk in chunks:
            bubbles = [_build_bubble(row) for row in chunk]
            flex_msg = FlexMessage(
                alt_text="Low RSI Watchlist — Buyable Stocks",
                contents=FlexCarousel(type="carousel", contents=bubbles),
            )
            line_bot_api.broadcast(BroadcastRequest(messages=[flex_msg]))
            print(f"Sent {len(bubbles)} bubble(s) to LINE OA.")
