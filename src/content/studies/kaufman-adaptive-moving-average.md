---
title: Kaufman Adaptive Moving Average
aliases: [KAMA, Adaptive Moving Average, AMA]
category: trend
summary: A moving average that speeds up when price moves cleanly in one direction and slows down when price is choppy.
display: overlay
inputs:
  - { name: efficiency length, default: 10 }
  - { name: fast length, default: 2 }
  - { name: slow length, default: 30 }
verdict: situational
status: draft
related: [exponential-moving-average, simple-moving-average, average-directional-index]
overlaps:
  - with: exponential-moving-average
    strength: partial
    corr: 0.78
    note: "KAMA is an exponential-style average whose speed changes with how cleanly price is moving. The correlation is measured on how far price sits from each line."
---

> **In plain English.** A moving average that changes its own speed. When price has been moving cleanly in one direction, it follows closely. When price is jumping around without getting anywhere, it barely moves. It does this by measuring how *efficient* recent movement has been: the net distance price travelled, divided by the total distance it wandered. That ratio, between 0 and 1, sets how fast the average reacts.
>
> **Good for:** a trend line that stays close in a real trend and stays calm in noise.
>
> **Watch out for:** assuming it solves lag. It lags more in choppy markets, by design.

## What it measures

A smoothed price whose responsiveness depends on how trending the market is. In a straight line, it behaves like a fast exponential average. In a noisy range it behaves like a very slow one.

## Calculation

The **efficiency ratio** compares net movement with total movement over the last $N$ bars:

$$
ER_t = \frac{\lvert P_t - P_{t-N} \rvert}{\sum_{i=0}^{N-1} \lvert P_{t-i} - P_{t-i-1} \rvert}
$$

It is 1 when price moved in a straight line and near 0 when it zigzagged to nowhere. The smoothing constant then slides between a fast and a slow limit:

$$
SC_t = \left[ ER_t \left( \tfrac{2}{f+1} - \tfrac{2}{s+1} \right) + \tfrac{2}{s+1} \right]^2 \qquad \text{KAMA}_t = \text{KAMA}_{t-1} + SC_t\,(P_t - \text{KAMA}_{t-1})
$$

With the usual $f = 2$ and $s = 30$, $SC$ runs from $(2/31)^2 \approx 0.004$ (nearly frozen) to $(2/3)^2 \approx 0.44$ (very fast).

**Worked example.** Closes of 10, 11, 12, 13, 14, 15 with $N = 4$. At the last bar, net movement is $\lvert 15 - 11 \rvert = 4$ and total movement is 4, so $ER = 1$ and $SC \approx 0.44$: KAMA moves 44% of the way from 14 to 15. For closes zigzagging 10, 12, 10, 12, 10, 12, net movement over 4 bars is 0, so $ER = 0$ and $SC \approx 0.004$: KAMA hardly moves at all.

**On a steady climb**, KAMA trails by 1.25 bars. On flat data, a naive version breaks (0/0), so this one treats a flat window as zero efficiency. The check script covers both.

```python
def kama(close, n=10, fast=2, slow=30):
    change = (close - close.shift(n)).abs()
    path = close.diff().abs().rolling(n).sum()
    efficiency = (change / path.replace(0, np.nan)).fillna(0)
    fast_sc, slow_sc = 2 / (fast + 1), 2 / (slow + 1)
    smoothing = (efficiency * (fast_sc - slow_sc) + slow_sc) ** 2
    values = close.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    out[n] = values[n]
    for i in range(n + 1, len(values)):
        out[i] = out[i - 1] + smoothing.iloc[i] * (values[i] - out[i - 1])
    return pd.Series(out, index=close.index)
```

The first value is seeded with the price at bar $N$, an arbitrary choice that fades quickly.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/kaufman-adaptive-moving-average-dark.svg">
<img src="../../charts/kaufman-adaptive-moving-average-light.svg" alt="Price with a KAMA and a 20-bar EMA across four regimes" width="840" height="430">
</picture>
<figcaption>Synthetic data. KAMA (pink) stays smooth in the range, where its smoothing constant averaged 0.067, and follows closely in the selloff, where it averaged 0.132 (the 20-bar EMA's constant is 0.095). It bottomed at bar 249, the same bar as the price low, and crossed price 12 times in the 100-bar range, against 18 for the EMA.</figcaption>
</figure>

- **Slope and price against the line** read as for any average.
- **A flat KAMA** means price has been getting nowhere. Some traders use that as a built-in trend filter: flat means sideways, and sloping means trending.
- **Crossovers** are fewer than for a fast average, because the line barely moves in noise.

What it does not tell you: that a trend will continue, or when a quiet market will break out. It lags most exactly when a move starts out of a quiet stretch.

## Best used when

- Price alternates between **trends and ranges**, and you want one line to cope with both.
- You want fewer **whipsaws** than a fast average gives in a range.

## Avoid when

- You need a **fast** reaction at the start of a move from a quiet market. It will be slow.
- You want a line with a **simple, predictable** speed. This one's speed changes from bar to bar.

## Settings and tuning

- **10, 2 and 30** are the usual defaults: a 10-bar efficiency window, and fast and slow limits of 2 and 30 bars.
- **A longer efficiency window** gives a steadier ratio and slower changes of speed.
- **Wider fast and slow limits** make the speed range larger.

## Implementation variations

- **Seeding.** Some tools start from the previous close or from a simple average.
- **Squaring.** The smoothing constant is squared in the standard version, which makes it change faster at high efficiency. Variants omit it.
- **History.** It is usually credited to Perry Kaufman. I have not confirmed the details.

## Is it useful?

**Situational.** The idea is sound and the sample shows it working: its effective smoothing constant averaged 0.067 in the range (slower than a 20-bar EMA's 0.095) and 0.132 in the selloff (faster). It crossed price 12 times in the range, the same as a simple average and fewer than the EMA's 18, and it bottomed on the same bar as price. But it is still a lagging average with more moving parts, and its correlation with the EMA (measured on distance from price) is 0.78: related, not redundant. A reasonable choice if you want one average for both kinds of market.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the fixed-speed average it adapts.
- [Simple Moving Average](../simple-moving-average/): the plainest alternative.
- [Average Directional Index](../average-directional-index/): another way to ask whether a market is trending.
