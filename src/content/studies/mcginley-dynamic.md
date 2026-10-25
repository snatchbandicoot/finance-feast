---
title: McGinley Dynamic
aliases: [McGinley, MD, McGinley Dynamic Indicator]
category: trend
summary: A moving average that adjusts its own speed according to how far price has moved from it, speeding up when price falls below it and slowing down when price runs above.
display: overlay
inputs:
  - { name: length, default: 14 }
  - { name: constant, default: 0.6 }
verdict: redundant
status: draft
related: [exponential-moving-average, kaufman-adaptive-moving-average, simple-moving-average]
overlaps:
  - with: exponential-moving-average
    strength: near
    corr: 0.99
    note: "The McGinley Dynamic is an exponential-style average whose speed depends on where price is. In practice it is nearly a 14-bar EMA. The correlation is measured on how far price sits from each line."
---

> **In plain English.** A moving average that changes its own speed. When price drops well below the line, the line speeds up to catch it. When price runs well above the line, the line slows down. The aim is to track price more closely than a fixed-speed average, without extra whipsaws. In practice, on this site's sample data it behaved almost exactly like a 14-bar exponential average.
>
> **Good for:** a self-adjusting average that is easy to use and has no extra settings to tune.
>
> **Watch out for:** its lopsidedness. It is slower to follow price up than down, so in a steady climb it trails further than an EMA of the same length.

## What it measures

A smoothed price whose speed depends on price's distance from the line itself. Where an exponential average moves a fixed fraction of the gap each bar, the McGinley Dynamic moves a fraction that gets smaller when price is above the line and larger when price is below it.

## Calculation

$$
MD_t = MD_{t-1} + \frac{P_t - MD_{t-1}}{k\,N\,\left(P_t / MD_{t-1}\right)^{4}}
$$

$N$ is the length (default 14), $k$ is a constant (usually 0.6), and $MD_0$ is the first price. When price equals the line, the divisor is $kN = 8.4$, so the line moves 1/8.4 (about 12%) of the gap, like an EMA of roughly 16 bars.

**Worked example.** With $MD = 100$ and $N = 14$, $k = 0.6$:

- If price jumps to 110, the divisor is $8.4 \times 1.1^4 = 12.30$, so the line moves $10/12.30 = 0.81$, to 100.81. It moves *slowly*.
- If price drops to 90, the divisor is $8.4 \times 0.9^4 = 5.51$, so the line moves $-10/5.51 = -1.81$, to 98.19. It moves more than twice as fast, in the same distance.

**What this means in practice.** On a steady climb, the McGinley Dynamic trails by 7.7 bars, where a 14-bar EMA trails by 6.5. After a 10-point jump up, it takes 7 bars to cover half the gap. After a 10-point jump down, it takes 3. An EMA takes 4 in both directions. The check script confirms these numbers.

```python
def mcginley(close, n=14, k=0.6):
    values = close.to_numpy(dtype=float)
    out = np.empty(len(values))
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = out[i - 1] + (values[i] - out[i - 1]) / (k * n * (values[i] / out[i - 1]) ** 4)
    return pd.Series(out, index=close.index)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/mcginley-dynamic-dark.svg">
<img src="../../charts/mcginley-dynamic-light.svg" alt="Price with the McGinley Dynamic and a 14-bar EMA through a selloff and rebound" width="840" height="430">
</picture>
<figcaption>Synthetic data, zoomed to the end of the range, the selloff and the rebound. The McGinley Dynamic (pink) and the 14-bar EMA (teal) are almost the same line: both bottomed at bar 257, at 91.7 and 92.2. In the 100-bar range the McGinley Dynamic crossed price 16 times, against 14 for the EMA.</figcaption>
</figure>

Read it as any moving average: slope for direction, price against the line for position, crossovers for signals. Keep its lopsidedness in mind: it is quick to follow price down and slow to follow it up.

What it does not tell you: that its extra mechanism improves signals. In the sample, it crossed price 16 times in the 100-bar range, against 14 for a 14-bar EMA.

## Best used when

- You want an average that **adapts without extra settings**.
- You are **long-biased** and care more about not getting left behind when price falls.

## Avoid when

- You need **symmetric** behavior. It is not symmetric.
- You expect a **big difference from an EMA**. There usually is not one.
- Price is **sideways**. As with any average, it keeps crossing price.

## Settings and tuning

- **Length 14** and **constant 0.6** are the usual values. The length sets the overall speed.
- The constant scales the speed too: a smaller value makes the line faster.
- The fourth power in the formula is fixed, which means the speed changes sharply when price is far from the line.

## Implementation variations

- **Starting value.** It starts from the first price, and some tools start from an average. Early values depend on that choice.
- **The constant.** 0.6 is the figure usually given by its originator. A few tools expose it, and some fix it.
- **History.** It is usually credited to John McGinley. I have not confirmed the details.

## Is it useful?

**Redundant.** The idea, a line that slows down when price is running away from it and speeds up when price falls through it, is a pleasant one. But on the sample data, the distance of price from the McGinley Dynamic correlated 0.99 with its distance from a 14-bar EMA, and its low after the selloff came on the same bar (257, at 91.7 against 92.2). The asymmetry is real, but small in practice. If you have an EMA, you do not need this.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the fixed-speed version, which it nearly matches.
- [Kaufman Adaptive Moving Average](../kaufman-adaptive-moving-average/): a different kind of adaptive average, which adapts to how trending the market is.
- [Simple Moving Average](../simple-moving-average/): the plainest alternative.
