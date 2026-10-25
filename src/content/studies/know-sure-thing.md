---
title: Know Sure Thing
aliases: [KST, Pring's KST]
category: momentum
summary: A weighted blend of four smoothed rates of change over different time spans, from short to long, intended to show the trend of momentum across several horizons in one line.
display: panel
inputs:
  - { name: ROC lengths, default: "10, 15, 20, 30" }
  - { name: smoothing lengths, default: "10, 10, 10, 15" }
  - { name: weights, default: "1, 2, 3, 4" }
  - { name: signal length, default: 9 }
verdict: redundant
status: draft
related: [rate-of-change, macd, true-strength-index, trix]
overlaps:
  - with: macd
    strength: near
    corr: 0.95
    note: "Both are smoothed momentum lines that cross zero when the trend turns. The KST blends four time spans. The correlation is between the two lines."
  - with: true-strength-index
    strength: partial
    corr: 0.94
    note: "Both are smoothed momentum lines. The correlation is between the KST and the TSI."
---

> **In plain English.** Take the percentage change over four different lookbacks (short to long). Smooth each one. Add them up, giving longer horizons more weight. The sum is one smooth line that rises when momentum is positive across timeframes, and falls when it is negative across them. It is momentum seen from several distances at once.
>
> **Good for:** a slow, steady read of whether momentum is positive or negative across horizons.
>
> **Watch out for:** how slow it is. It reacts several weeks late, and it adds little beyond MACD.

## What it measures

A weighted sum of smoothed rates of change. Because longer lookbacks carry larger weights, it mostly reflects the longer-term momentum, with shorter-term momentum as a refinement.

## Calculation

For each of four pairs of settings (ROC length $r$, smoothing length $s$, weight $w$), take the percentage rate of change over $r$ bars, average it over $s$ bars, and weight it:

$$
\text{KST}_t = \sum_{i=1}^{4} w_i \cdot \text{SMA}_{s_i}\!\left(100 \times \left(\frac{P_t}{P_{t-r_i}} - 1\right)\right)
$$

The usual settings are $(r, s, w)$ = (10, 10, 1), (15, 10, 2), (20, 10, 3) and (30, 15, 4). The signal line is a 9-bar simple average of the KST.

**Worked example.** Suppose the four smoothed rates of change are 2, 3, 4 and 5 (in percent). Weighted by 1, 2, 3 and 4:

$$
1 \times 2 + 2 \times 3 + 3 \times 4 + 4 \times 5 = 40
$$

If price grows a steady 1% each bar, each rate of change is 1.01 raised to its lookback, minus one, and the KST equals the same weighted sum of those four growth rates. The check script confirms this.

```python
def kst(close, signal=9):
    parts = [(10, 10, 1), (15, 10, 2), (20, 10, 3), (30, 15, 4)]
    line = sum(w * (100 * (close / close.shift(r) - 1)).rolling(s).mean() for r, s, w in parts)
    return line, line.rolling(signal).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/know-sure-thing-dark.svg">
<img src="../../charts/know-sure-thing-light.svg" alt="Price above, and the Know Sure Thing with its signal line below, with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The KST was above zero on 62% of the range's bars and on none of the selloff's. Its low of -184.2 came on bar 252, three bars after the price low. It crossed its signal line 9 times in the range.</figcaption>
</figure>

- **Zero line.** Above zero means the blended momentum is positive. Below zero means it is negative.
- **Signal crossovers.** The KST crossing its 9-bar average is the usual earlier cue: 9 times in the sample's range.
- **Direction of the line.** Because it is smooth, a turn is itself informative.
- **Divergence.** The KST failing to confirm a new price high or low is the usual caution.

What it does not tell you: the size of any move in price terms. Its scale is arbitrary, and cannot be compared across instruments.

## Best used when

- You want a **slow, smooth** view of the trend of momentum.
- You prefer **weekly or monthly** perspectives, where its slow behavior suits the original design.

## Avoid when

- You use **MACD** already. The two correlated 0.95 on the sample.
- You need **timely** signals. It is slow: at the price low (bar 249) it was still falling, bottoming at bar 252.
- The market is **choppy** and has no momentum to blend.

## Settings and tuning

- **The four pairs** are fixed in the standard version, and the weights favor the long end. Changing them changes what it means.
- **Shorter versions** exist for faster markets, and longer versions for monthly charts.
- **The signal length** of 9 is the default.

## Implementation variations

- **Different parameter sets.** Several sets of lookbacks exist for daily, weekly and monthly charts, and the daily set varies between sources.
- **Signal.** Some tools omit it.
- **Rate of change.** Some use the difference in price and some the percentage. This page uses the percentage.
- **History.** It is usually credited to Martin Pring, from the 1990s. I have not confirmed the details.

## Is it useful?

**Redundant.** It is a clever idea: look at momentum over several horizons at once. In practice, the KST correlated 0.95 with MACD's line and 0.94 with the [True Strength Index](../true-strength-index/) on the sample. In the selloff it was above zero on none of its bars, and in the range it crossed zero 3 times, against 5 for MACD and for the TSI. It is slower and has an arbitrary scale. Unless you follow Pring's longer-term methods, MACD gives the same information with less machinery.

## Pairs well with / See also

- [Rate of Change](../rate-of-change/): the building block.
- [MACD](../macd/): the near twin, with simpler construction.
- [True Strength Index](../true-strength-index/): another smoothed momentum line.
- [TRIX](../trix/): another smoothed momentum line.
