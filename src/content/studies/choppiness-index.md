---
title: Choppiness Index
aliases: [CHOP, Choppiness]
category: trend
summary: A 0 to 100 reading of whether the market has been trending or going nowhere, by comparing how far price travelled bar by bar with the distance it actually covered. It says nothing about direction.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: situational
status: draft
related: [average-directional-index, average-true-range, aroon]
---

> **In plain English.** Imagine walking 14 steps. If you walked in a straight line, the total of your steps is about the distance from start to finish: not choppy. If you wandered back and forth, your steps add up to far more than the distance covered: choppy. The Choppiness Index puts that ratio on a 0 to 100 scale. High means wandering, low means going somewhere.
>
> **Good for:** a quick "is this market trending or churning" filter before using a trend or range tool.
>
> **Watch out for:** its lag and its muddy middle. On the sample, the sideways range averaged 50.0 and the rebound 51.3, so the two kinds of market were not separated by much.

## What it measures

The ratio of the sum of the true ranges over $N$ bars to the whole span from the highest high to the lowest low in those bars. A trending market covers a large span for its bar-to-bar travel. A choppy one covers a small span for the same travel.

## Calculation

$$
\text{CHOP}_t = 100 \times \frac{\log_{10}\!\left(\dfrac{\sum_{i=0}^{N-1} TR_{t-i}}{\max H - \min L}\right)}{\log_{10} N}
$$

where $TR$ is the true range (see [Average True Range](../average-true-range/)), and the max and min are over the same $N$ bars. The logarithm scales the result so that it tops out at 100.

**Worked example.** With $N = 14$, suppose the true ranges add up to 28, and the highest high minus the lowest low over the same 14 bars is 4:

$$
100 \times \frac{\log_{10}(28 / 4)}{\log_{10}(14)} = 100 \times \frac{0.845}{1.146} = 73.7
$$

If every bar's range equalled the whole window's span, the ratio would be 14 and the result exactly 100. The closer the travel is to the span, the lower the reading.

```python
def choppiness(high, low, close, n=14):
    prev_close = close.shift()
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    span = high.rolling(n).max() - low.rolling(n).min()
    return 100 * np.log10(tr.rolling(n).sum() / span) / np.log10(n)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/choppiness-index-dark.svg">
<img src="../../charts/choppiness-index-light.svg" alt="Price above, and the Choppiness Index below with lines at 38.2 and 61.8" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Choppiness Index averaged 41.9 in the uptrend, 50.0 in the range, 41.5 in the selloff and 51.3 in the rebound. It was below 38.2 on 47% of the uptrend's scored bars, 0% of the range's, 28% of the selloff's and 9% of the rebound's.</figcaption>
</figure>

- **Above 61.8** is the usual "choppy" line, and **below 38.2** the usual "trending" line. Those are Fibonacci ratios, picked by convention, not derived.
- **Falling through 38.2** is read as a trend starting. **Rising through 61.8** is read as a trend ending or a consolidation starting.
- **Direction.** It is blind to it. A strong fall and a strong rise both read low.

What it does not tell you: whether the trend is up or down, or whether it will continue.

## Best used when

- You want a **filter**: use trend tools when it is low, and range tools when it is high.
- You want a **second opinion** next to ADX.

## Avoid when

- You want to **pick tops and bottoms**. It describes the past.
- The window is **very short**. It becomes jumpy.

## Settings and tuning

- **14** is the usual length. A longer window is steadier.
- **38.2 and 61.8** are conventional. Some use 40 and 60.

## Implementation variations

- **True range or high-low range.** This page uses the true range, which includes gaps.
- **Log base.** The base cancels out, so any base gives the same result.
- **History.** It is usually credited to E.W. Dreiss. I have not confirmed the details.

## Is it useful?

**Situational.** The picture is intuitive, and it is cheap to compute. But the reading is only loosely tied to what the market was doing. In the sample it averaged 41.9 in the uptrend, 50.0 in the range, 41.5 in the selloff and 51.3 in the rebound. It was below 38.2 on 47% of the uptrend's scored bars and 28% of the selloff's, and on none of the range's, which is right, but it was above 61.8 on only 4% of the range's bars. It correlated -0.58 with ADX on the sample, so ADX gives much of the same information. Use it as a coarse filter, and do not trust the exact thresholds.

## Pairs well with / See also

- [Average Directional Index](../average-directional-index/): the more common trend-strength reading.
- [Average True Range](../average-true-range/): the source of the true range.
- [Aroon](../aroon/): another way to see whether a trend is present.
