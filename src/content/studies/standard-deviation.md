---
title: Standard Deviation
aliases: [StdDev, Standard Deviation Indicator, SD]
category: volatility
summary: How spread out the last N closing prices are around their average. It is the engine inside Bollinger Bands, and it rises in strong trends as well as in choppy markets.
display: panel
inputs:
  - { name: length, default: 20 }
verdict: situational
status: draft
related: [bollinger-bands, historical-volatility, average-true-range]
overlaps:
  - with: bollinger-bands
    strength: identical
    note: "Bollinger Bands are the average plus and minus two standard deviations, so the distance from the upper to the lower band is exactly four standard deviations."
---

> **In plain English.** Take the last 20 closes, find their average, and ask how far the closes typically sit from it. That typical distance is the standard deviation, in price units. It is large when the closes are widely spread, and small when they are bunched together.
>
> **Good for:** measuring spread, and understanding what Bollinger Bands are doing.
>
> **Watch out for:** a trend inflates it. A steady climb spreads the closes out just as much as chop does, even though price moved calmly. On the sample, it spiked to 9.2 in the selloff while ATR, which looks at each bar's range, peaked at 2.9.

## What it measures

The dispersion of closing prices within the window, around their own average. It mixes two things: the noise from bar to bar, and the trend across the window.

## Calculation

$$
\sigma_t = \sqrt{\frac{1}{N}\sum_{i=0}^{N-1}\left(P_{t-i} - \bar{P}_t\right)^2}
$$

where $\bar{P}_t$ is the simple average of the last $N$ closes. This uses the population form (divide by $N$), which is how Bollinger Bands define it.

**Worked example.** Take eight closes: 2, 4, 4, 4, 5, 5, 7, 9. The average is 5. The squared distances are 9, 1, 1, 1, 0, 0, 4, 16, which sum to 32. Divide by 8 to get 4, and take the square root:

$$
\sigma = \sqrt{32 / 8} = 2
$$

```python
def std_dev(close, n=20):
    return close.rolling(n).std(ddof=0)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/standard-deviation-dark.svg">
<img src="../../charts/standard-deviation-light.svg" alt="Price above, and the 20-bar standard deviation of price with ATR below, both in price units" width="840" height="590">
</picture>
<figcaption>Synthetic data. The standard deviation of price (pink) averaged 2.49 in the uptrend and 1.75 in the range, while ATR (teal) averaged 1.66 and 1.79. In the selloff the standard deviation peaked at 9.2 (bar 248), against an ATR peak of 2.91 (bar 243).</figcaption>
</figure>

- **Rising** means closes are spreading out, either through bigger swings or through a trend.
- **Falling** means closes are bunching together.
- **In price units**, so it is not comparable across instruments. Divide by price for a percentage.

What it does not tell you: whether the spread comes from noise or from a trend. To separate them, compare with ATR (in the figure), which ignores the drift across the window.

## Best used when

- You want to **understand or rebuild** Bollinger Bands.
- You want a spread measure for **statistics**, such as a z-score.

## Avoid when

- You want a clean **volatility** reading in a trending market. Use ATR or historical volatility.
- You compare **different instruments** without converting to percent.

## Settings and tuning

- **20** is common, matching Bollinger Bands.
- **A shorter window** reacts faster and is noisier.
- **Population or sample.** Dividing by $N-1$ makes it very slightly larger.

## Implementation variations

- **Divisor.** $N$ (here) or $N-1$.
- **Input.** Closing prices here. Some tools use another price, or the returns instead, which is [Historical Volatility](../historical-volatility/).
- **Naming.** Often just "StdDev" in tool menus.

## Is it useful?

**Situational.** As a tool in its own right it is mostly a building block, because it is exactly four times the width of the Bollinger Bands' channel, and the check script confirms this to rounding error. Its weakness is the trend effect: the sample's standard deviation averaged 2.49 in the uptrend, against 1.75 in the range, even though ATR was higher in the range (1.79 against 1.66). Across the whole sample it correlated only 0.63 with ATR. If you want volatility, use ATR or HV. If you want spread around an average, this is the measure.

## Pairs well with / See also

- [Bollinger Bands](../bollinger-bands/): the average plus and minus two of these.
- [Historical Volatility](../historical-volatility/): the same idea applied to returns.
- [Average True Range](../average-true-range/): volatility from the bar's range, which ignores trend.
