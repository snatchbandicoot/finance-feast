---
title: Anchored VWAP
aliases: [AVWAP, Event VWAP]
category: volume
summary: The volume-weighted average price from a bar you choose, such as an earnings day or a major low, carried forward indefinitely. It shows the average price paid by everyone who traded since that event.
display: overlay
inputs:
  - { name: anchor bar, default: "chosen by you" }
verdict: situational
status: draft
related: [volume-weighted-average-price, simple-moving-average, linear-regression]
overlaps:
  - with: volume-weighted-average-price
    strength: identical
    note: "Anchored at the start of a session, it is exactly the session VWAP. The only difference is that it does not restart, and the anchor is yours to pick."
---

> **In plain English.** Everyone who traded after some event paid, on average, a certain price. That average, weighted by how much traded at each price, is the anchored VWAP. If price is above it, most buyers since the event are ahead. If below, most are behind. You pick the event, and the line grows from there.
>
> **Good for:** judging who is in profit since a significant date, and as a reference line that has a reason behind it.
>
> **Watch out for:** the anchor. The choice is yours, and the best-looking anchor is usually the one picked with hindsight.

## What it measures

The average price, weighted by volume, of all trading from the anchor bar to now. It is the VWAP without the daily reset.

## Calculation

With $T_i = (H_i + L_i + C_i)/3$ and volume $V_i$, and anchor bar $a$:

$$
\text{AVWAP}_t = \frac{\sum_{i=a}^{t} T_i\, V_i}{\sum_{i=a}^{t} V_i}
$$

**Worked example.** Suppose the anchor bar has a typical price of 10 with volume 100, and the next bar has a typical price of 12 with volume 300:

$$
\frac{10 \times 100 + 12 \times 300}{100 + 300} = \frac{4600}{400} = 11.5
$$

The line is pulled toward 12, because more traded there. A plain average would have been 11.

**An exact identity.** Anchored at the first bar of one session, it equals the session [VWAP](../volume-weighted-average-price/), to the last digit. The check script confirms it.

```python
def anchored_vwap(high, low, close, volume, anchor):
    typical = ((high + low + close) / 3).iloc[anchor:]
    vol = volume.iloc[anchor:]
    out = pd.Series(np.nan, index=close.index)
    out.iloc[anchor:] = (typical * vol).cumsum() / vol.cumsum()
    return out
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/anchored-vwap-dark.svg">
<img src="../../charts/anchored-vwap-light.svg" alt="Price with the volume-weighted average price anchored at bar 200 and at bar 249" width="840" height="440">
</picture>
<figcaption>Synthetic data. Anchored at bar 200 (the start of the selloff), the line ended at 102.62 and price closed above it on 6 of 120 bars. Anchored at bar 249 (the price low), it ended at 97.50 and price closed above it on 69 of 71 bars. The second anchor was only known to be the low afterwards.</figcaption>
</figure>

- **Price above the line**: the average buyer since the anchor is in profit. **Below**: not.
- **The line as support or resistance.** Many traders watch for a bounce or a rejection at it. This site's data cannot test that.
- **Slope.** It flattens as time passes, since each new bar has less effect on a growing total.

What it does not tell you: which anchor is the right one. That is the whole difficulty.

## Best used when

- There is a **clear event**: earnings, a major low or high, a breakout, a policy decision.
- You want a **cost-basis** reference since that date.

## Avoid when

- You pick the anchor **after** seeing the chart and then trust it. In the figure, the anchor at the price low (bar 249) looks perfect only because the low was known in advance.
- The data has **no real volume**, such as many currency markets.
- The anchor is **very old**. The line moves so little that it adds nothing.

## Settings and tuning

- **The anchor** is the only setting. Use a bar with a reason.
- **Several anchors** on one chart is common, and each should have a stated reason.

## Implementation variations

- **Typical price or close.** This page uses the average of high, low and close. Some tools use the close or the average of the open, high, low and close.
- **Bands.** Some tools add standard-deviation bands around the line.
- **Starting the sum.** Some start with the anchor bar's own price and volume, and some with its next bar.
- **History.** I do not know who first used it. It has become common on charting platforms since about the late 2010s.

## Is it useful?

**Situational.** The idea is sound, because it ties a line to a reason and a price level to the money behind it. In the sample, price closed above the line anchored at the low (bar 249) on 69 of the 71 bars since, ending at 102.44 against an AVWAP of 97.50. Anchored at the start of the selloff (bar 200), price closed above it on only 6 of 120 bars. Both lines are accurate, and they tell opposite stories, which shows that the anchor is the whole signal. Without a reason for the anchor, the line is decoration. With one, it is a reasonable reference for who is ahead.

## Pairs well with / See also

- [Volume Weighted Average Price](../volume-weighted-average-price/): the same line, restarted every session.
- [Simple Moving Average](../simple-moving-average/): an average with a fixed window, instead of a fixed start.
- [Linear Regression](../linear-regression/): another line fitted to a stretch of history.
