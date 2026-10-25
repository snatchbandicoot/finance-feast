---
title: Commodity Channel Index
aliases: [CCI, Lambert's CCI]
category: momentum
summary: How far the typical price is from its recent average, measured in units of how far prices usually stray from that average.
display: panel
inputs:
  - { name: length, default: 20 }
verdict: redundant
status: draft
related: [bollinger-bands, relative-strength-index, simple-moving-average]
overlaps:
  - with: bollinger-bands
    strength: near
    corr: 0.98
    note: "Both measure how far price is from its 20-bar average in units of how spread out prices have been. CCI uses the typical price and mean deviation, and Bollinger %B uses the close and standard deviation."
  - with: relative-strength-index
    strength: partial
    corr: 0.82
    note: "Both are oscillators of where price sits compared with its recent past, so they often agree, but they are built differently."
---

> **In plain English.** CCI measures how far the latest typical price (the average of the high, low and close) is from its recent average, in units of how much prices typically stray from that average. Zero means right at the average. Plus or minus 100 means unusually far above or below it. It was designed for commodity markets, hence the name, but it can be used on anything.
>
> **Good for:** spotting moves that are stretched compared with recent behavior.
>
> **Watch out for:** assuming it adds something new. On the sample data it moved almost in lockstep with Bollinger %B (correlation 0.98).

## What it measures

The distance between the typical price and its simple average over the last $N$ bars, scaled by the average size of the typical price's deviations in that window. It is a *normalised* distance: a reading of +100 means the same thing, roughly, whether the instrument costs 5 or 5,000, and whether the market is quiet or wild.

## Calculation

Let $TP = (H + L + C)/3$, the typical price. Over the last $N$ bars, find its average and its mean deviation, which is the average distance of each typical price from that average:

$$
\overline{TP} = \frac{1}{N}\sum_{i=0}^{N-1} TP_{t-i} \qquad MD = \frac{1}{N}\sum_{i=0}^{N-1} \left| TP_{t-i} - \overline{TP} \right|
$$

$$
CCI_t = \frac{TP_t - \overline{TP}}{0.015 \cdot MD}
$$

The constant 0.015 is Lambert's. It was chosen so that a good share of readings fall between −100 and +100.

**Worked example.** Five typical prices of 10, 11, 12, 13, 14 with $N = 5$. The average is 12. The deviations are 2, 1, 0, 1, 2, so $MD = 6/5 = 1.2$. Then $CCI = (14 - 12)/(0.015 \times 1.2) = 2/0.018 \approx 111$.

```python
def cci(high, low, close, n=20):
    typical = (high + low + close) / 3
    mean = typical.rolling(n).mean()
    mean_dev = typical.rolling(n).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    return (typical - mean) / (0.015 * mean_dev)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/commodity-channel-index-dark.svg">
<img src="../../charts/commodity-channel-index-light.svg" alt="Price above, and 20-bar CCI below with lines at plus and minus 100" width="840" height="590">
</picture>
<figcaption>Synthetic data. In this sample 61% of CCI readings stayed within plus or minus 100 (44% in the selloff), and the readings ran from -253 to +279. The 100 lines are a convention, not a boundary.</figcaption>
</figure>

- **Zero line.** Above zero, the typical price is above its recent average, and below zero it is below.
- **Plus and minus 100.** A reading beyond either line means price is unusually far from its average. What that *means* is disputed. Lambert's original reading, as it is usually described, treats a move above +100 as the start of a strong uptrend, so you go with it. Many traders read it the opposite way, as overbought, and fade it. The two readings give opposite trades from the same signal.
- **Divergence.** As with other oscillators, price making a new extreme while CCI does not is often described as a warning. It is common and fails often.

What it does not tell you: which of the two readings of the 100 lines is right for the market in front of you.

## Best used when

- You want a **scale-free** measure of how far price is from its recent average.
- You prefer the **typical price** (which includes the high and low) to the close alone.

## Avoid when

- You already use **Bollinger Bands** or %B. They say almost the same thing.
- Price is **trending strongly**. CCI can stay beyond +100 or −100 for a long time, so fading every extreme loses to the trend.
- You treat the **100 lines** as fixed truths. They are conventions.

## Settings and tuning

- **Length 20** is the usual default.
- **Shorter** (such as 10): more sensitive, and it spends more time beyond the 100 lines.
- **Longer** (such as 40): smoother, and it rarely reaches the lines.

## Implementation variations

- **Mean deviation, not standard deviation.** CCI divides by the mean absolute deviation. Substituting the standard deviation changes the scale. A tool that does so is plotting something closer to Bollinger %B.
- **Typical price.** Some tools allow the close or another price in place of $(H + L + C)/3$.
- **The constant.** 0.015 is standard, but a few tools expose it.

## Is it useful?

**Redundant.** CCI and Bollinger %B both measure the distance of price from its 20-bar average in units of how spread out prices have been. They differ in two small details (typical price and mean deviation, against the close and the standard deviation). On the sample data the two correlated at 0.98, and CCI also correlated at 0.82 with RSI. If you already use Bollinger Bands, CCI is very unlikely to tell you something they do not. Its one real advantage is the typical price, which includes the bar's range, and that is a small one.

## Pairs well with / See also

- [Bollinger Bands](../bollinger-bands/): the closest relative. %B is the same idea with the standard deviation.
- [Relative Strength Index](../relative-strength-index/): another bounded-ish momentum gauge, with its own conventions at 70 and 30.
- [Simple Moving Average](../simple-moving-average/): CCI measures distance from one.
