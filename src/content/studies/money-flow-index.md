---
title: Money Flow Index
aliases: [MFI, Volume-Weighted RSI]
category: volume
summary: An RSI-style oscillator built from price times volume instead of price alone. It runs from 0 to 100, and swings with the same logic as RSI, but heavier volume counts for more.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: situational
status: draft
related: [relative-strength-index, chaikin-money-flow, on-balance-volume]
overlaps:
  - with: relative-strength-index
    strength: partial
    corr: 0.73
    note: "The same shape of calculation as RSI, with money flow (typical price times volume) in place of price changes. The correlation is between the two lines."
---

> **In plain English.** Take each bar's typical price times its volume, which is roughly the money that changed hands. If the typical price rose from the previous bar, call it positive money flow, and if it fell, negative. Then ask what share of the last 14 bars' flow was positive. That share, from 0 to 100, is the MFI. It is sometimes called a volume-weighted RSI.
>
> **Good for:** an overbought and oversold gauge that also considers whether volume backed the moves.
>
> **Watch out for:** its extremes, which are rarer than RSI's here: it was above 80 on 0.8% of the sample's scored bars, though it did touch 0.0 on bar 244.

## What it measures

The share of recent money flow that went into rising bars. Heavy volume on up-bars pushes it up, and heavy volume on down-bars pushes it down.

## Calculation

With the typical price $T = (H + L + C)/3$ and the raw money flow $T \times V$:

$$
\text{MFI}_t = 100 - \frac{100}{1 + \dfrac{\sum \text{flow on bars where } T \text{ rose}}{\sum \text{flow on bars where } T \text{ fell}}}
$$

over the last $N$ bars (14 by default). Bars where the typical price did not change count for neither side.

**Worked example.** With a 3-bar window, suppose three bars have a typical price and volume of: 11 and 200 (up from 10), 10.5 and 100 (down), 11.5 and 300 (up). Their flows are 2,200, 1,050 and 3,450. Positive flow is $2200 + 3450 = 5650$ and negative flow is 1,050:

$$
100 \times \frac{5650}{5650 + 1050} = 84.3
$$

An unbroken decline gives exactly 0, and the check script confirms it.

```python
def mfi(high, low, close, volume, n=14):
    typical = (high + low + close) / 3
    flow = typical * volume
    change = typical.diff()
    positive = flow.where(change > 0, 0.0).rolling(n).sum()
    negative = flow.where(change < 0, 0.0).rolling(n).sum()
    return 100 - 100 / (1 + positive / negative)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/money-flow-index-dark.svg">
<img src="../../charts/money-flow-index-light.svg" alt="Price above, and the Money Flow Index and RSI below with lines at 20 and 80" width="840" height="590">
</picture>
<figcaption>Synthetic data. The MFI (pink) averaged 56.7 in the uptrend, 51.9 in the range, 39.7 in the selloff and 56.5 in the rebound. It touched 0.0 on bar 244 and read 13.8 at the price low (bar 249), where RSI (teal) read 17.4.</figcaption>
</figure>

- **Above 80** and **below 20** are the usual overbought and oversold levels.
- **Divergence** from price is the usual caution.
- **The 50 line**: above it means more of the recent flow was into rising bars.

What it does not tell you: whether a stretch will reverse. Strong trends keep it at the extremes.

## Best used when

- You like RSI but want **volume** to have a say.
- The market is **ranging**, where oversold and overbought readings work best.

## Avoid when

- **Volume is unreliable** or missing.
- The market is **trending hard**. It can stay at an extreme.

## Settings and tuning

- **14** is the usual length. Shorter is jumpier.
- **80 and 20** are the usual levels. Some use 90 and 10.

## Implementation variations

- **Smoothing.** A plain 14-bar sum, as here. RSI uses a smoothed average, so the MFI reacts a little differently to old data leaving the window.
- **Typical price.** The average of high, low and close, as in VWAP.
- **History.** It is usually credited to Gene Quong and Avrum Soudack. I have not confirmed the details.

## Is it useful?

**Situational.** It is a reasonable volume-aware cousin of RSI. On the sample it correlated 0.73 with RSI, so volume changed the picture meaningfully. It averaged 56.7 in the uptrend, 51.9 in the range, 39.7 in the selloff and 56.5 in the rebound. At the price low (bar 249) it read 13.8, near RSI's 17.4, and it touched 0.0 on bar 244. Where volume carries information, it is a fair second opinion on RSI. In a market where volume does not tell you much, it is RSI with extra noise.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): the same idea without volume.
- [Chaikin Money Flow](../chaikin-money-flow/): another volume-based pressure measure.
- [On-Balance Volume](../on-balance-volume/): a running total of signed volume.
