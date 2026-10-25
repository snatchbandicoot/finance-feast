---
title: Ulcer Index
aliases: [UI, Martin Ulcer Index]
category: volatility
summary: Measures the depth and duration of recent drawdowns, from the highest close in the window. It only counts price falling away from its peak, so rising prices do not add to it.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: situational
status: draft
related: [historical-volatility, standard-deviation, average-true-range]
overlaps:
  - with: historical-volatility
    strength: partial
    corr: 0.74
    note: "Both rise when the market is moving a lot. The Ulcer Index counts only the falls from a peak, and historical volatility counts moves in both directions. The correlation is between the two lines."
---

> **In plain English.** Most volatility measures treat a 5% rise and a 5% fall the same. Investors do not. The Ulcer Index counts only the pain: how far price has sunk below its recent peak, and for how long. A smooth climb scores zero. A long, deep slide scores high.
>
> **Good for:** judging how uncomfortable holding an asset has been, or comparing the downside experience of two assets.
>
> **Watch out for:** its window. Because the peak is the highest close in the last N bars, the reading fades once the old peak drops out of the window, even if price is still far below an older high.

## What it measures

The root mean square of percentage drawdowns over the window, where each drawdown is measured from the highest close in the N bars up to that point.

## Calculation

For each bar in the window, find the percentage drawdown from the highest close in the preceding $N$ bars (including that bar):

$$
D_t = 100 \times \left(\frac{P_t}{\max_N(P)_t} - 1\right) \qquad \text{UI}_t = \sqrt{\frac{1}{N}\sum_{i=0}^{N-1} D_{t-i}^{\,2}}
$$

Squaring means deep drawdowns count far more than shallow ones.

**Worked example.** With $N = 3$ and closes of 100, 98, 97, the drawdowns are 0%, -2% and -3%:

$$
\sqrt{\frac{0^2 + 2^2 + 3^2}{3}} = \sqrt{4.33} = 2.08
$$

A market that only rises has no drawdowns and scores exactly zero. The check script confirms this.

```python
def ulcer(close, n=14):
    drawdown = 100 * (close / close.rolling(n, min_periods=1).max() - 1)
    return np.sqrt((drawdown ** 2).rolling(n).mean())
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/ulcer-index-dark.svg">
<img src="../../charts/ulcer-index-light.svg" alt="Price above, and the Ulcer Index below" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Ulcer Index averaged 1.73 in the uptrend, 2.33 in the range, 5.97 in the selloff and 3.92 in the rebound. It peaked at 16.49 on bar 251, two bars after the price low.</figcaption>
</figure>

- **Level.** A higher number means deeper or longer recent declines. Compare it with the same asset's history, or across assets.
- **Rising** during a slide. **Falling** as the market recovers, or as the old peak leaves the window.
- **Zero** means price is at new highs on every bar of the window.

What it does not tell you: how likely the next fall is.

## Best used when

- You compare **investments** by the downside they delivered.
- You want a volatility figure that **ignores upward moves**.

## Avoid when

- You want a **trading signal**. It is a risk description.
- You need a **forward-looking** figure. It looks back.

## Settings and tuning

- **14** is the usual default. Longer windows suit investment comparisons, and 14 suits short-term views.
- **Percentages** make it comparable across assets.

## Implementation variations

- **Peak.** The highest close in the window (here), or the highest high, or the all-time high.
- **Window.** The peak and the averaging window use the same length here. Some tools use two different lengths.
- **Ratio form.** The Martin Ratio divides return by the Ulcer Index. This page covers only the index.
- **History.** It is usually credited to Peter Martin and Byron McCann, from the 1980s. I have not confirmed the details.

## Is it useful?

**Situational.** It has an appealing idea: risk is the part that hurts. On the sample it averaged 1.73 in the uptrend, 2.33 in the range, 5.97 in the selloff and 3.92 in the rebound, and peaked at 16.49 on bar 251, two bars after the price low, then dropped back within about 14 bars as the peak left the window. It correlated 0.74 with historical volatility. For comparing downside across assets it is a good measure. As a signal, it just tells you the market has already fallen.

## Pairs well with / See also

- [Historical Volatility](../historical-volatility/): volatility in both directions.
- [Standard Deviation](../standard-deviation/): the spread of prices.
- [Average True Range](../average-true-range/): volatility from the bar's range.
