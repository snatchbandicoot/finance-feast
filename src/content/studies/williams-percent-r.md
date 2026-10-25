---
title: Williams %R
aliases: ["Williams %R", "%R", Williams Percent Range, WPR]
category: momentum
summary: Where the latest close sits within the recent high-to-low range, on a scale from minus 100 at the bottom to 0 at the top.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: redundant
status: draft
related: [stochastic-oscillator, relative-strength-index]
overlaps:
  - with: stochastic-oscillator
    strength: identical
    note: "Williams %R is the stochastic's raw reading minus 100, so the two always agree. The usual stochastic adds smoothing on top."
---

> **In plain English.** Williams %R shows where the latest close sits between the recent highest high and lowest low, from −100 (at the lowest low) to 0 (at the highest high). That is exactly the stochastic oscillator's raw reading, moved onto a negative scale. If you understand the stochastic, you already understand %R.
>
> **Good for:** a quick view of how near price is to the top or bottom of its recent range.
>
> **Watch out for:** treating it as a separate tool. It is the unsmoothed stochastic minus 100, so it has the same weaknesses: it is noisy, and "overbought" in a strong trend means little.

## What it measures

Position within a range, just as the [stochastic oscillator](../stochastic-oscillator/) does. Over the last $N$ bars, where did the close land between the lowest low and the highest high?

## Calculation

$$
\%R_t = -100 \times \frac{HH_t - C_t}{HH_t - LL_t}
$$

Here $HH_t$ and $LL_t$ are the highest high and lowest low over the last $N$ bars.

The relation to the stochastic is exact:

$$
\%R = \text{raw stochastic }\%K - 100
$$

**Worked example.** The same numbers as on the stochastic page: highest high 20, lowest low 10, latest close 16. Then $\%R = -100 \times (20 - 16)/(20 - 10) = -40$. The stochastic's raw reading for those numbers is 60, and $60 - 100 = -40$.

```python
def williams_r(high, low, close, n=14):
    highest = high.rolling(n).max()
    lowest = low.rolling(n).min()
    return -100 * (highest - close) / (highest - lowest)
```

The check script confirms the identity numerically: over hundreds of bars, %R and the raw stochastic minus 100 agree to within $10^{-14}$.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/williams-percent-r-dark.svg">
<img src="../../charts/williams-percent-r-light.svg" alt="Price above, and Williams %R below with lines at -20 and -80" width="840" height="590">
</picture>
<figcaption>Synthetic data. In the selloff %R was below -80 on 60% of bars and above -20 on only 4%. In the uptrend it was above -20 on 39% of bars and below -80 on only 11%. It followed the direction of the move more than any turning point.</figcaption>
</figure>

- **Near 0** means the close is at the top of its recent range. **Near −100** means the bottom.
- **The −20 and −80 lines.** Above −20 is the top fifth of the range, below −80 the bottom fifth. These are the same conventions as the stochastic's 80 and 20, and carry the same caution: an extreme reading says price is *at the edge of its range*, not that it must turn.
- **In a trend** the reading can sit near 0 or near −100 for a long time.

What it does not tell you: when the move will end.

## Best used when

- Price is **ranging**, and you want to see closes pushing toward the top or bottom of the range.
- Your platform offers %R but **not** the stochastic, and you want that reading.

## Avoid when

- Price is **trending strongly**. Selling every reading above −20 in an uptrend fights the trend.
- You want a **smoother** line. The raw reading is jumpy. The slow stochastic smooths it.
- You already use the **stochastic**. They carry the same information.

## Settings and tuning

- **Length 14** is the common default.
- **Shorter:** more sensitive and more false extremes.
- **Longer:** smoother, rarely reaching −20 or −80.

## Implementation variations

- **Sign.** Williams' scale runs from −100 to 0. Some tools plot it inverted, as 0 to 100, which makes it identical to the raw stochastic.
- **Smoothing.** Standard %R is not smoothed. A smoothed version is the slow stochastic by another name.

## Is it useful?

**Redundant.** It is exactly the raw stochastic with 100 subtracted, so it adds no information to a chart that already has the stochastic. In practice the stochastic is usually preferable, because its smoothed lines are less jumpy and its crossovers are a conventional signal. Choose one of them and skip the other.

## Pairs well with / See also

- [Stochastic Oscillator](../stochastic-oscillator/): the same measurement, on a 0 to 100 scale and usually smoothed.
- [Relative Strength Index](../relative-strength-index/): a different measurement of momentum, from gains and losses rather than position in the range.
