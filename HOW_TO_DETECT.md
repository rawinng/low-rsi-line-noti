# How We Detect a Good Stock

A stock is flagged as a **BUY** only when all four conditions are true simultaneously. Each condition serves a distinct purpose.

## Buy Conditions

```
BUY = RSI < 40  AND  price > SMA50  AND  price > EMA100  AND  MACD crossover
```

---

### 1. RSI-14 < 40 — Oversold momentum

**Relative Strength Index** measures how fast price has moved over the last 14 days.

- Scale: 0–100
- `< 30` → strongly oversold (green in notification)
- `< 40` → mildly oversold, still qualifies
- Signals the stock has pulled back and may be due for a bounce

### 2. Price > SMA-50 — Short-term uptrend

**50-day Simple Moving Average** of closing price.

- Price above SMA50 means the stock is still in a short-term uptrend
- Filters out stocks that are in a freefall — we want a dip, not a collapse

### 3. Price > EMA-200 — Long-term uptrend intact

**200-day Exponential Moving Average** of closing price.

- EMA weights recent prices more than older ones (more responsive than SMA)
- Price above EMA200 confirms the stock is structurally healthy over the long term
- Prevents buying into a stock that is recovering short-term but broken long-term

### 4. MACD Bullish Crossover — Momentum turning up

**MACD** = EMA12 − EMA26. **Signal line** = EMA9 of MACD.

- A bullish crossover occurs when the MACD line crosses **above** the signal line
- We only trigger on the exact crossover bar (not just when MACD is above signal)
- Confirms that short-term momentum has just shifted from bearish to bullish

---

## RSI Colour Coding (in LINE notification)

| RSI Value | Colour | Meaning |
|---|---|---|
| < 30 | Green `#22c55e` | Strongly oversold |
| 30 – 40 | Amber `#f59e0b` | Mildly oversold |

---

## Summary

| Indicator | Type | Purpose |
|---|---|---|
| RSI-14 < 40 | Momentum | Stock is oversold / pulled back |
| Price > SMA-50 | Short-term trend | Dip within an uptrend, not a collapse |
| Price > EMA-200 | Long-term trend | Structurally healthy stock |
| MACD crossover | Momentum shift | Confirms reversal is starting |

The combination targets a specific setup: **a temporary dip in an otherwise healthy uptrending stock, with momentum just beginning to reverse upward.**
