---
title: Vortex Indicator
aliases: [VI, Vortex, VI+ and VI-]
category: trend
summary: Two lines that measure upward and downward movement against the true range, crossing when the balance between up-moves and down-moves changes.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: situational
status: draft
related: [average-directional-index, aroon, average-true-range]
overlaps:
  - with: average-directional-index
    strength: partial
    corr: 0.86
    note: "Both split movement into an upward and a downward part, relative to the true range, and compare them. The correlation is between VI+ minus VI- and +DI minus -DI."
---

> **In plain English.** Two lines. The first (VI+) measures how far each bar's high has reached above the previous bar's low, which is a measure of upward movement. The second (VI−) measures how far each bar's low has fallen below the previous bar's high, which is downward movement. Both are added over the last 14 bars and compared with the total true range. When VI+ is above VI−, upward movement is stronger, and the reverse. They cross when the balance changes.
>
> **Good for:** a direct read on which side, up or down, has been stronger, with crossovers as a trend-change signal.
>
> **Watch out for:** a lot of crossovers in a sideways market. In this site's sample they crossed 12 times in the 100-bar range, against 8 in the uptrend.

## What it measures

The balance between upward and downward movement. It works much like the +DI and −DI lines of the [Average Directional Index](../average-directional-index/), but it measures movement a different way, from each bar's high to the previous low and from each bar's low to the previous high.

## Calculation

Over the last $N$ bars, with $TR$ the true range (see [Average True Range](../average-true-range/)):

$$
VM^{+}_t = \lvert H_t - L_{t-1} \rvert \qquad VM^{-}_t = \lvert L_t - H_{t-1} \rvert
$$

$$
VI^{+} = \frac{\sum_{N} VM^{+}}{\sum_{N} TR} \qquad VI^{-} = \frac{\sum_{N} VM^{-}}{\sum_{N} TR}
$$

**Worked example.** Four bars with highs 10, 12, 13, 14, lows 9, 10, 11, 12 and closes 9.5, 11.5, 12.5, 13.5, and $N = 3$ (the last three bars):

- $VM^{+}$ is $\lvert 12 - 9 \rvert + \lvert 13 - 10 \rvert + \lvert 14 - 11 \rvert = 9$.
- $VM^{-}$ is $\lvert 10 - 10 \rvert + \lvert 11 - 12 \rvert + \lvert 12 - 13 \rvert = 2$.
- The true ranges of the three bars are 2.5, 2 and 2, which total 6.5.
- So $VI^{+} = 9/6.5 \approx 1.38$ and $VI^{-} = 2/6.5 \approx 0.31$. Upward movement dominates.

```python
def vortex(high, low, close, n=14):
    prev_close = close.shift()
    true_range = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    plus = (high - low.shift()).abs()
    minus = (low - high.shift()).abs()
    total = true_range.rolling(n).sum()
    return plus.rolling(n).sum() / total, minus.rolling(n).sum() / total
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/vortex-indicator-dark.svg">
<img src="../../charts/vortex-indicator-light.svg" alt="Price above, and the Vortex lines VI+ and VI- below with a line at 1.0" width="840" height="590">
</picture>
<figcaption>Synthetic data. VI+ was above VI- on 79% of the uptrend's bars, 56% of the range's, 18% of the selloff's and 79% of the rebound's. The lines crossed 8 times in the uptrend, 12 times in the range, 5 in the selloff and 9 in the rebound.</figcaption>
</figure>

- **VI+ above VI−** means upward movement has been the stronger one, and the reverse for a downtrend.
- **A crossover** is the trend-change signal. VI+ crossing above VI− suggests an uptrend is starting.
- **The 1.0 level.** Both lines hover around 1.0. A line well above 1 means that side's movement is large compared with the bars' ranges.
- In the sample, VI+ was above VI− on 79% of the uptrend's bars and 18% of the selloff's.

What it does not tell you: how strong the trend is overall, or whether a crossover will last.

## Best used when

- You want a **second opinion** on trend direction, alongside the directional lines of ADX.
- Price is **trending**, so that crossovers are not constant.

## Avoid when

- Price is **sideways**. The lines cross repeatedly.
- You want a **strength** measure. It has no equivalent of the ADX line, which says how strong a trend is.
- You use it **alone**. A crossover is a late and noisy signal.

## Settings and tuning

- **Length 14** is the usual default, and 21 is also common.
- **Shorter:** faster and more crossovers. **Longer:** smoother and later.

## Implementation variations

- **Sums or averages.** The ratio uses sums over the window. Using averages gives the same result.
- **Naming.** Some platforms label the lines "+VI" and "−VI".
- **History.** It is usually credited to Etienne Botes and Douglas Siepman, around 2010. I have not confirmed the details.

## Is it useful?

**Situational.** It is a clean, easily explained pair of lines. But it overlaps heavily with the directional lines of ADX: the difference between VI+ and VI− correlated 0.86 with the difference between +DI and −DI on the sample. It adds a different construction of the same idea more than a different idea. If you already use ADX with its directional lines, the Vortex is mainly a cross-check. It does not replace the strength reading ADX gives.

## Pairs well with / See also

- [Average Directional Index](../average-directional-index/): the closest relative, which also tells you how strong the trend is.
- [Aroon](../aroon/): another trend reading, from the timing of the extremes.
- [Average True Range](../average-true-range/): the denominator of both lines.
