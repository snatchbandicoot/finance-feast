---
title: Schaff Trend Cycle
aliases: [STC, Schaff Trend]
category: momentum
summary: Runs a stochastic oscillator on MACD, twice, with smoothing in between. The result swings between 0 and 100 faster than MACD, and spends much of its time pinned at the ends.
display: panel
inputs:
  - { name: cycle, default: 10 }
  - { name: fast, default: 23 }
  - { name: slow, default: 50 }
  - { name: smoothing factor, default: 0.5 }
verdict: situational
status: draft
related: [macd, stochastic-oscillator, double-smoothed-stochastic]
overlaps:
  - with: stochastic-oscillator
    strength: partial
    corr: 0.84
    note: "The Schaff Trend Cycle applies the Stochastic formula to MACD instead of to price. The correlation is with the Stochastic's smoothed %K, and with MACD itself it is only 0.38."
---

> **In plain English.** MACD tells you the trend's direction, but its scale is arbitrary and it moves slowly. The Schaff Trend Cycle runs a stochastic oscillator over the MACD line to ask where MACD is within its own recent range, then does it a second time to sharpen the answer. The result runs from 0 to 100 and turns sooner than MACD does.
>
> **Good for:** a bounded, quick-turning trend signal that is easy to read at a glance.
>
> **Watch out for:** the edges. It sat at 95 or above on 30% of the sample's scored bars and at 5 or below on 24%, so readings at the extremes say little.

## What it measures

Where the MACD line sits within its own recent range, smoothed and re-measured. It is a rescaling of MACD's recent swings, so it inherits MACD's direction and loses its size.

## Calculation

1. Compute the MACD line: $\text{EMA}_{23}(P) - \text{EMA}_{50}(P)$.
2. Take the stochastic of that line over the last $N$ bars (10): $100 \times (x - \min) / (\max - \min)$.
3. Smooth it with the recursive rule $s_t = s_{t-1} + 0.5\,(x_t - s_{t-1})$, starting from the first value.
4. Take the stochastic of the smoothed series over the same window.
5. Smooth that the same way. The result is the Schaff Trend Cycle.

**Worked example.** If the MACD line is 0.8, and over the last 10 bars it has ranged from 0.2 to 1.0, the first stochastic is $100 \times (0.8 - 0.2)/(1.0 - 0.2) = 75$. If the previous smoothed value was 40, the smoothing gives $40 + 0.5 \times (75 - 40) = 57.5$.

```python
def schaff_trend_cycle(close, cycle=10, fast=23, slow=50, factor=0.5):
    line = close.ewm(span=fast, adjust=False).mean() - close.ewm(span=slow, adjust=False).mean()

    def stochastic_of(x):
        low, high = x.rolling(cycle).min(), x.rolling(cycle).max()
        return 100 * (x - low) / (high - low).replace(0, np.nan)

    def smooth(x):
        out, prev = [], np.nan
        for value in x:
            if not np.isnan(value):
                prev = value if np.isnan(prev) else prev + factor * (value - prev)
            out.append(prev if not np.isnan(value) else np.nan)
        return pd.Series(out, index=x.index)

    return smooth(stochastic_of(smooth(stochastic_of(line))))
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/schaff-trend-cycle-dark.svg">
<img src="../../charts/schaff-trend-cycle-light.svg" alt="Price above, and the Schaff Trend Cycle below with lines at 25 and 75" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Schaff Trend Cycle was at 95 or above on 30% of scored bars and at 5 or below on 24%. It read 0.0 at the price low (bar 249) and crossed the 50 line 26 times.</figcaption>
</figure>

- **Above 75** is read as an uptrend, and **below 25** as a downtrend. A cross up through 25 is a buy cue, and a cross down through 75 is a sell cue.
- **At the extremes** it means little, since it saturates. In the sample it crossed the 50 line 26 times.
- **Direction** matters more than level: a turn up from near 0 is the signal people watch.

What it does not tell you: the strength of the trend. A tiny MACD wobble within a flat market can drive the oscillator across its whole range.

## Best used when

- You want a **fast, bounded** trend indicator.
- You like the stochastic format but want a trend base.

## Avoid when

- The market is **flat**. MACD's range is tiny but the stochastic stretches it to 0 to 100 anyway.
- You want **amplitude**. The size of the trend is lost.

## Settings and tuning

- **10, 23 and 50** are the usual values. The 23 and 50 form the MACD, and the 10 is the cycle length.
- **A smaller smoothing factor** gives a smoother line, with more lag.

## Implementation variations

- **The smoothing step.** The recursion with factor 0.5 is common, but some versions differ in how the first value is seeded.
- **Cycle length.** Some tools tie it to the market's dominant cycle instead of fixing it.
- **History.** It is usually credited to Doug Schaff. I have not confirmed the details.

## Is it useful?

**Situational.** The idea of making MACD bounded and quick is attractive, and the line turns earlier than MACD. But it is a rescaling, and it pays for speed with noise and with time pinned at the ends. On the sample it was above 75 on 65% of the uptrend's scored bars and 73% of the rebound's, and below 25 on 56% of the selloff's, which fits the story, and it read 0.0 at the price low (bar 249). It correlated 0.84 with the Stochastic and only 0.38 with MACD, which shows how much the rescaling changes the line. Use it as a trend filter, not as a precise timing tool.

## Pairs well with / See also

- [MACD](../macd/): the line it rescales.
- [Stochastic Oscillator](../stochastic-oscillator/): the formula it applies.
- [Double Smoothed Stochastic](../double-smoothed-stochastic/): another doubly processed stochastic, applied to price.
