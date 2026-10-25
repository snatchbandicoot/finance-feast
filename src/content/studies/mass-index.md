---
title: Mass Index
aliases: [MI, Reversal Bulge]
category: volatility
summary: Adds up how much the daily range has been widening compared with its own average, and looks for a "bulge" that is meant to warn of a reversal. It ignores direction entirely.
display: panel
inputs:
  - { name: EMA length, default: 9 }
  - { name: sum length, default: 25 }
verdict: skip
status: draft
related: [average-true-range, chaikin-volatility, bollinger-bands]
---

> **In plain English.** Smooth the daily high-low range. Smooth that smoothed range again. Divide one by the other: when ranges are widening, the first is larger than the second, and the ratio rises above 1. Add up 25 of those ratios. The total hovers around 25, and the idea is that a rise above 27 followed by a drop below 26.5 (a "reversal bulge") warns that a trend may be about to reverse.
>
> **Good for:** nothing proven here. It is a curiosity.
>
> **Watch out for:** the signal, which is rare. On the sample, it never rose above 27 at all.

## What it measures

Whether the daily range has been expanding relative to its own recent average, summed over 25 bars. It is blind to direction.

## Calculation

$$
\text{ratio}_t = \frac{\text{EMA}_9(H - L)_t}{\text{EMA}_9\big(\text{EMA}_9(H - L)\big)_t} \qquad \text{MI}_t = \sum_{i=0}^{24}\text{ratio}_{t-i}
$$

**Why 25?** If the range never changes, the two averages are equal, each ratio is exactly 1, and the sum of 25 is exactly 25. The check script confirms this. So the line sits near 25 in a steady market, above it when ranges have been widening, and below it when they have been narrowing.

**Worked example.** If the single-smoothed range is 2.1 and the double-smoothed one is 2.0, the ratio is 1.05. If it stays 1.05 for 25 bars the index is $25 \times 1.05 = 26.25$.

```python
def mass_index(high, low, n=9, total=25):
    spread = (high - low).ewm(span=n, adjust=False).mean()
    ratio = spread / spread.ewm(span=n, adjust=False).mean()
    return ratio.rolling(total).sum()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/mass-index-dark.svg">
<img src="../../charts/mass-index-light.svg" alt="Price above, and the Mass Index below with lines at 26.5 and 27" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Mass Index stayed between 22.7 and 26.7 and never crossed 27. Its highest reading, 26.66, came on bar 223, during the selloff.</figcaption>
</figure>

- **The reversal bulge.** The index rises above 27, then falls back below 26.5. The author's claim is that a reversal in price is likely to follow. It does not say which direction.
- **Near 25** means ranges are steady.
- **Below 25** means ranges are narrowing.

What it does not tell you: the direction of any reversal. It needs another indicator for that.

## Best used when

- You study **range expansion** over weeks, and want a single running total of it.

## Avoid when

- You want a **timely** signal. The bulge is rare and slow.
- You want a **direction**. It has none.

## Settings and tuning

- **9 and 25** are the standard values, and the 27 and 26.5 thresholds belong to them.
- **Changing the lengths** changes the baseline, which is the sum length. A 25-bar sum sits at 25 and a 20-bar sum at 20, so the thresholds must move too.

## Implementation variations

- **Seeding.** The two exponential averages start from the first range, so the early values are not reliable. The chart hides the first 60 bars.
- **Range.** The high-low range is standard, not the true range.
- **History.** It is usually credited to Donald Dorsey, from the 1990s. I have not confirmed the details.

## Is it useful?

**Skip.** The idea, that a widening range foreshadows a turn, is easy to state and hard to use. On the sample the index stayed between 22.7 and 26.7 and never rose above 27, so the bulge signal never appeared, even though the sample contains a sharp reversal (the selloff turning into a rebound). Its highest reading, 26.66, came on bar 223 in the middle of the selloff, well before the price low at bar 249. With so rare a trigger, and no direction, there is little to act on. Look at ATR or Bollinger Band width if you want to watch ranges widen.

## Pairs well with / See also

- [Average True Range](../average-true-range/): a direct level of the range.
- [Chaikin Volatility](../chaikin-volatility/): another measure of widening ranges.
- [Bollinger Bands](../bollinger-bands/): their width shows expansion and contraction.
