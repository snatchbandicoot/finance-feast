---
title: Double Smoothed Stochastic
aliases: [DSS, DSS Bressert, Bressert DSS]
category: momentum
summary: A Stochastic Oscillator that is smoothed, re-measured against its own range, and smoothed again. The result is much smoother than a plain stochastic and turns a little later.
display: panel
inputs:
  - { name: window, default: 13 }
  - { name: smoothing, default: 8 }
verdict: situational
status: draft
related: [stochastic-oscillator, schaff-trend-cycle, stochastic-momentum-index]
overlaps:
  - with: stochastic-oscillator
    strength: partial
    corr: 0.77
    note: "Both place the close inside a recent high-low range. The Double Smoothed Stochastic then smooths and repeats the step. The correlation is with the Stochastic's smoothed %K."
---

> **In plain English.** The Stochastic Oscillator shows where the close sits in its recent range, but it is jumpy. This version smooths the answer, measures that smoothed line against its own recent high and low, then smooths again. Every pass removes a little noise and adds a little delay. The reward is a calm line from 0 to 100.
>
> **Good for:** a smooth overbought and oversold gauge with few false flickers.
>
> **Watch out for:** the delay. Two passes of smoothing mean it turns after the market has.

## What it measures

Where a smoothed stochastic sits within its own recent range. It is a smoothed second-generation stochastic, and it is not a new measurement of price.

## Calculation

1. The raw stochastic over $N$ bars (13): $100 \times (C - LL) / (HH - LL)$.
2. Smooth it with an EMA of length $s$ (8).
3. Take the stochastic of the smoothed series over the same $N$ bars.
4. Smooth that with another EMA of length $s$. This is the DSS.

**Worked example.** If the smoothed stochastic is 55, and over the last 13 bars it has ranged from 40 to 60, the second stochastic is:

$$
100 \times \frac{55 - 40}{60 - 40} = 75
$$

The final EMA with length 8 then moves $2/(8+1) = 22\%$ of the way from its previous value to 75.

```python
def double_smoothed_stochastic(high, low, close, n=13, smooth=8):
    raw = 100 * (close - low.rolling(n).min()) / (high.rolling(n).max() - low.rolling(n).min())
    first = raw.ewm(span=smooth, adjust=False).mean()
    low2, high2 = first.rolling(n).min(), first.rolling(n).max()
    second = 100 * (first - low2) / (high2 - low2).replace(0, np.nan)
    return second.ewm(span=smooth, adjust=False).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/double-smoothed-stochastic-dark.svg">
<img src="../../charts/double-smoothed-stochastic-light.svg" alt="Price above, and the Double Smoothed Stochastic and the ordinary Stochastic below with lines at 20 and 80" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Double Smoothed Stochastic (pink) was above 80 on 26% of scored bars and below 20 on 24%. It crossed 50 19 times, against 22 for the Stochastic's smoothed %K (teal). It read 3.1 at the price low (bar 249).</figcaption>
</figure>

- **Above 80** is overbought and **below 20** is oversold, as in a plain stochastic. In the sample it was above 80 on 26% of scored bars and below 20 on 24%.
- **Crossing 50** is read as a change of bias. It crossed 50 19 times, against 22 for the plain Stochastic, and 26 for the Schaff Trend Cycle.
- **Turns** from the extremes are the main signal.

What it does not tell you: how strong a trend is. In a strong trend it sits at an extreme for a long time.

## Best used when

- The market is **ranging** and you want a smooth swing indicator.
- You find the ordinary stochastic **too jumpy**.

## Avoid when

- The market is **trending hard**.
- You want **early** signals. It is slow.

## Settings and tuning

- **13 and 8** are the usual values.
- **Shorter smoothing** brings it closer to a plain stochastic.

## Implementation variations

- **The second stage.** The second stochastic uses the smoothed line's own high and low, as here. Some versions differ in detail.
- **Smoothing type.** Exponential here. Some tools use other averages.
- **History.** It is usually credited to Walter Bressert. I have not confirmed the details.

## Is it useful?

**Situational.** It does what it says: smoother than the plain stochastic, with fewer reversals, at the cost of lag. On the sample it correlated 0.77 with the Stochastic's smoothed %K, so related but clearly different. It read 3.1 at the price low (bar 249), a clear oversold reading. But it is built from the same ingredients as the [Stochastic](../stochastic-oscillator/) and the [Stochastic Momentum Index](../stochastic-momentum-index/), so you rarely need more than one. Choose it if smoothness matters more than speed.

## Pairs well with / See also

- [Stochastic Oscillator](../stochastic-oscillator/): the single-pass version.
- [Schaff Trend Cycle](../schaff-trend-cycle/): the same two-pass idea applied to MACD.
- [Stochastic Momentum Index](../stochastic-momentum-index/): another smoother stochastic.
