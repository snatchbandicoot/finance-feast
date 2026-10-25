---
title: Triangular Moving Average
aliases: [TMA, Triangular MA, Double Smoothed SMA]
category: trend
summary: A simple moving average of a simple moving average. The result weights the middle of the window most and the ends least, so it is smoother than a plain average, at the same lag.
display: overlay
inputs:
  - { name: length, default: 20 }
verdict: situational
status: draft
related: [simple-moving-average, weighted-moving-average, exponential-moving-average]
overlaps:
  - with: simple-moving-average
    strength: near
    corr: 0.99
    note: "The Triangular Moving Average is an average of simple averages, so it follows the same path as the SMA with less jitter. The correlation is with the distance of price from a same-length SMA, which is 0.993 on the sample."
---

> **In plain English.** Average the last 20 closes, then average the last 10 or so of those averages. That second step smooths the line a second time. The effect is that closes in the middle of the window count most, and the newest and oldest closes count least. The line looks calmer than a simple average, and it turns at about the same time.
>
> **Good for:** a smooth trend line that is slow to be shaken by single odd bars.
>
> **Watch out for:** its slowness at turns. The newest bar has the smallest weight of all, so it is the last to show a change.

## What it measures

A smoothed price level, built by averaging an average. The weights form a triangle: lowest at both ends of the window, highest in the middle.

## Calculation

For a length $N$, take a simple average of the closes over $\lfloor N/2 \rfloor + 1$ bars, then a simple average of that over $\lfloor (N+1)/2 \rfloor$ bars. For $N = 20$ that is an 11-bar average of closes followed by a 10-bar average of the result. The window the two steps cover together is exactly $N$ bars.

**Worked example.** For $N = 4$, the steps are a 3-bar average followed by a 2-bar average, which together give weights of 1, 2, 2, 1 (divided by 6) on the last four closes. With closes of 2, 3, 4 and 5:

$$
\frac{1 \times 2 + 2 \times 3 + 2 \times 4 + 1 \times 5}{6} = \frac{21}{6} = 3.5
$$

```python
def triangular_ma(close, n=20):
    return close.rolling(n // 2 + 1).mean().rolling((n + 1) // 2).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/triangular-moving-average-dark.svg">
<img src="../../charts/triangular-moving-average-light.svg" alt="Price with a 20-bar triangular moving average and a 20-bar simple moving average through a selloff and rebound" width="840" height="430">
</picture>
<figcaption>Synthetic data, zoomed to the end of the range, the selloff and the rebound. The triangular average (pink) and the simple average (teal) follow almost the same path. The triangular line is smoother, and on a straight climb both trail by 9.5 bars. Both crossed price 12 times in the 100-bar range.</figcaption>
</figure>

- **Slope** gives the direction, as for any average.
- **Price against the line**: above is bullish, below bearish.
- **Crossovers** with price or a faster average are the usual signals.

What it does not tell you: anything a simple average does not. It is the same idea, with the ends of the window tapered.

## Best used when

- You want a **smooth** trend line and do not mind a late turn.
- The data is **noisy**, and the jitter of a simple average irritates you.

## Avoid when

- You need **quick** reactions. It is as slow as an SMA of the same length, and its newest bar counts least.
- You use it as a **crossover** system in a flat market: it still whipsaws.

## Settings and tuning

- **20** is a common length. The two internal windows are set by it.
- **Longer** is smoother and later.

## Implementation variations

- **Odd and even lengths.** The rule used here makes the two windows add up to exactly the length. Some tools round differently.
- **Names.** It is also called a "double smoothed SMA", which is a loose description.
- **History.** I do not know who devised it.

## Is it useful?

**Situational.** It does what it says: on the sample the triangular average was smoother than the simple average (smoother again than the EMA), and on a straight climb it trailed price by 9.5 bars, exactly as an SMA of the same length does. It crossed price 12 times in the range, the same as the SMA, and the distance of price from it correlated 0.993 with the SMA's. So it is a prettier version of a simple average, not a different one. If the jitter in a simple average bothers you, it is a fair choice.

## Pairs well with / See also

- [Simple Moving Average](../simple-moving-average/): the same average, with equal weights.
- [Weighted Moving Average](../weighted-moving-average/): weights that favor the newest bars.
- [Exponential Moving Average](../exponential-moving-average/): the most common alternative.
