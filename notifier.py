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


def _build_bubble(row: dict) -> FlexBubble:
    rsi_color = "#22c55e" if row["rsi"] < 30 else "#f59e0b"
    return FlexBubble(
        size="kilo",
        header=FlexBox(
            layout="vertical",
            background_color="#1e293b",
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
            ],
        ),
    )


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
