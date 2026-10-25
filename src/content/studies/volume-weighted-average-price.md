---
title: Volume Weighted Average Price
aliases: [VWAP, Anchored VWAP, Session VWAP]
category: volume
summary: The average price paid during a session, with each price counted in proportion to the volume traded at it.
display: overlay
inputs:
  - { name: session reset, default: each trading day }
verdict: situational
status: draft
related: [simple-moving-average, on-balance-volume, average-true-range]
---

> **In plain English.** The average price of everything traded so far today, where prices that saw more trading count for more. If a lot of volume traded around 50 and only a little at 52, the VWAP sits close to 50. It starts fresh at the open of each session and is a running figure throughout the day.
>
> **Good for:** judging whether you bought or sold better or worse than the day's average price, and as a reference line for the day.
>
> **Watch out for:** using it on daily charts, where it makes little sense unless you pick a starting point on purpose. Also, late in the day it barely moves, so it stops being a useful signal.

## What it measures

The volume-weighted average of price since the session began. It answers a plain question: *what has the average share cost so far today?*

Price above VWAP means the latest trade is above what the average participant has paid today. Price below means below. Because it is weighted by volume, it reflects where most of the trading happened, not just where price spent time.

Fund managers and execution desks commonly use it as a benchmark: an order filled below VWAP (for a buy) is regarded as having done better than the day's average.

## Calculation

For each bar, take the typical price (the average of high, low and close) and multiply it by the bar's volume. Add these up from the start of the session, and divide by the total volume so far:

$$ \text{VWAP}_t = \frac{\sum_{i \le t} TP_i \cdot V_i}{\sum_{i \le t} V_i}, \qquad TP = \frac{H + L + C}{3} $$

The sums restart at the beginning of every session.

**Worked example.** One bar with a typical price of 10 on a volume of 100, then another with a typical price of 11 on a volume of 300. VWAP is $(10 \times 100 + 11 \times 300)/(100 + 300) = 4300/400 = 10.75$. A plain average of the two prices would be 10.5. The heavier second bar pulls VWAP toward 11.

```python
def vwap(high, low, close, volume, session):
    typical = (high + low + close) / 3
    cum_pv = (typical * volume).groupby(session).cumsum()
    cum_v = volume.groupby(session).cumsum()
    return cum_pv / cum_v
```

Here `session` labels which session each bar belongs to, for example the calendar date. Grouping by it makes the sums restart.

## How to read it

- **Price above or below the line.** Above VWAP means buyers have been paying more than the day's average recently, and below means sellers have accepted less. It describes the day so far. It does not say what comes next.
- **As a reference.** Traders often watch for price returning to VWAP after moving away from it, because it marks the average cost. Whether price respects it as a "level" is a matter of habit and attention, not a mathematical property.
- **Distance from VWAP.** Price far above or below VWAP is stretched relative to the day's average. This is context, not a signal on its own.

What it does not tell you: direction for the next bar, or whether the day is trending.

## Best used when

- You trade **intraday** on bars of a few minutes up to an hour. This is its home use.
- You want to **measure execution**: whether your fills were better or worse than the day's average.
- The instrument has **reliable, centralised volume**, such as listed stocks and futures.

## Avoid when

- You use **daily or longer bars** and a session reset. With one bar per session there is no average to compute. Some people anchor a VWAP to a chosen date instead (see below), which is a different tool.
- The **market has no central volume**, such as spot currencies. Platforms substitute tick counts, which approximate activity but are not traded volume.
- It is **late in the session**. By the afternoon, the running sums are large, so new bars barely change VWAP. The line goes flat and lags.
- You treat it as a **support level** with certainty. It is an average. Price crosses it all the time.

## Settings and tuning

There are almost no settings. The one real choice is **when the sums restart**.

- **Each session** (the standard): a fresh VWAP every day.
- **Longer resets** (weekly, monthly): a VWAP that covers more history and moves more slowly.

The typical price formula is a convention. Some tools use only the close, or $(H + L)/2$.

## Implementation variations

- **Anchored VWAP.** Instead of restarting each day, the sums start at a bar you choose, such as an earnings date or a major low, and run from there. It then shows the average price paid since that event. It is a deliberate analytical tool, and the result depends entirely on where you anchor.
- **Bands.** Many platforms draw lines above and below VWAP at standard-deviation distances. These are an added layer. They are not part of VWAP itself.
- **Bar-based approximation.** True VWAP weights every individual trade. Computing it from bars, as above, is an approximation, and it is closer when bars are shorter.
- **Typical price.** As above.

## Is it useful?

**Situational.** It is the right tool for a specific job: intraday reference and measuring execution quality. For that job it is hard to replace, and it is widely watched. Outside that job, it has little to offer. It is not a trend indicator, and on its own it is not a trading signal. It overlaps in spirit with moving averages, but the volume weighting and the daily reset make it a different thing.

## Pairs well with / See also

- [Simple Moving Average](../simple-moving-average/): an equal-weight average over a fixed window, instead of a running volume-weighted one.
- [On-Balance Volume](../on-balance-volume/): another way of using volume, focused on direction.
- [Average True Range](../average-true-range/): a way to judge whether a distance from VWAP is large or small for the instrument.
