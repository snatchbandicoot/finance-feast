---
title: Supertrend
aliases: [Super Trend, ATR Supertrend]
category: trend
summary: A trailing stop set a multiple of the average true range from the middle of each bar, that ratchets in the trend's direction and flips when price closes through it.
display: overlay
inputs:
  - { name: ATR length, default: 10 }
  - { name: multiplier, default: 3 }
verdict: situational
status: draft
related: [parabolic-sar, average-true-range, keltner-channels]
overlaps:
  - with: parabolic-sar
    strength: partial
    corr: 0.66
    note: "Both are trailing stops that flip when price closes through them. Supertrend sits a multiple of the average true range away and the SAR tightens as a trend makes new extremes. The correlation is measured on how far price is from each line."
---

> **In plain English.** A trailing stop drawn as a single line. In an uptrend it sits below price, a few average bar-ranges away, and only moves up. In a downtrend it sits above price and only moves down. When price closes through the line, the study flips to the other side, and the line jumps to the opposite band. Because the distance is set by the average true range, it widens when the market gets jumpier.
>
> **Good for:** a simple trailing stop and trend-direction flag that adjusts to volatility.
>
> **Watch out for:** the late all-clear. On this site's sample it flagged the selloff within three bars, but did not turn back to long until 15 bars after the price low.

## What it measures

Which side of a volatility-sized band price is on. The band is the middle of the bar plus or minus a multiple of the [Average True Range](../average-true-range/), and it is only allowed to move in the trend's favor until price closes through it.

## Calculation

Let $mid = (H + L)/2$ and $ATR$ be the average true range of length $N$. The raw bands are:

$$
\text{Up}_t = mid_t - k \cdot ATR_t \qquad \text{Down}_t = mid_t + k \cdot ATR_t
$$

Then each band is ratcheted. The lower band ($\text{Up}$, used in an uptrend) can only rise while the previous close was above it, and the upper band ($\text{Down}$, used in a downtrend) can only fall while the previous close was below it. The trend flips to up when the close goes above the previous upper band, and to down when it goes below the previous lower band. The line is the lower band in an uptrend and the upper band in a downtrend.

**Worked example.** With $N = 1$ (so the ATR is just the true range) and $k = 1$, on five bars:

| Bar | High | Low | Close | Line | What happens |
|-----|------|-----|-------|------|--------------|
| 0 | 11 | 9 | 10 | 8 | start in an uptrend: mid 10 minus range 2 |
| 1 | 12 | 10 | 11.5 | 9 | the lower band rises from 8 to 9 and does not fall |
| 2 | 13 | 11 | 12.5 | 10 | the lower band rises to 10 |
| 3 | 12 | 8 | 8.5 | 14.5 | the close of 8.5 is below the previous lower band of 10, so it **flips to a downtrend**, and the line jumps to the upper band, 14.5 |
| 4 | 9 | 7 | 7.5 | 10 | the upper band falls to 10, in the downtrend's favor |

```python
def supertrend(high, low, close, n=10, k=3):
    mid = (high + low) / 2
    width = k * atr(high, low, close, n)
    basic_up, basic_down = (mid - width).to_numpy(), (mid + width).to_numpy()
    c = close.to_numpy(dtype=float)
    up, down, line = basic_up.copy(), basic_down.copy(), np.empty(len(c))
    trend = 1
    line[0] = up[0]
    for i in range(1, len(c)):
        if c[i - 1] > up[i - 1]:
            up[i] = max(basic_up[i], up[i - 1])
        if c[i - 1] < down[i - 1]:
            down[i] = min(basic_down[i], down[i - 1])
        if trend == -1 and c[i] > down[i - 1]:
            trend = 1
        elif trend == 1 and c[i] < up[i - 1]:
            trend = -1
        line[i] = up[i] if trend == 1 else down[i]
    return pd.Series(line, index=close.index)
```

This function uses `atr()` from the [Average True Range](../average-true-range/) page. The first values depend on how the ATR is started, and the study starts by assuming an uptrend, so treat the first few dozen bars as unreliable.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/supertrend-dark.svg">
<img src="../../charts/supertrend-light.svg" alt="Price with the Supertrend line, pink below price and teal above price" width="840" height="440">
</picture>
<figcaption>Synthetic data. Supertrend flipped 10 times in all: 2 in the uptrend, 5 in the range, 2 in the selloff and 1 in the rebound. It flipped short at bar 203, three bars into the selloff, and back to long at bar 264, 15 bars after the price low.</figcaption>
</figure>

- **The line below price** means long, and **above price** means short.
- **A flip** is the signal: price closed through the line.
- **As a stop.** Between flips the line only moves in the trend's favor, so it works as a trailing stop that never loosens.
- **The distance** is a multiple of recent bar size, so it widens automatically in a jumpy market.

What it does not tell you: whether the market is trending at all. In a sideways market the line is hit repeatedly.

## Best used when

- Price is **trending**, with pullbacks smaller than the stop distance.
- You want a trailing stop that **adapts to volatility**.
- You want a **simple long/short flag** for a trend-following rule.

## Avoid when

- Price is **choppy**. Every flip is a small loss or a missed continuation.
- You want an **early** exit. The multiplier of 3 makes the stop wide, so it is slow to flip.
- You compare **different tools' versions** without checking their definitions.

## Settings and tuning

- **10 and 3** are the usual defaults.
- **A larger multiplier:** a wider stop, fewer flips, and a later exit.
- **A smaller multiplier:** a tighter stop, more flips, and more whipsaws.
- **A longer ATR length:** a steadier distance.

## Implementation variations

- **Flip rule.** This page follows the version most charting platforms use, which compares the close with the *previous* bar's band. Other versions compare with the current bar's band.
- **ATR smoothing.** Wilder's smoothing is standard here. Some tools use a simple average of the true range.
- **Starting trend.** The start is an assumption and differs between tools.
- **History.** It is usually credited to Olivier Seban. I have not confirmed the details.

## Is it useful?

**Situational.** It is a sensible, volatility-aware trailing stop with a clear definition. Against the [Parabolic SAR](../parabolic-sar/), the contrast on the sample is sharp: Supertrend flipped 10 times in all (2 in the uptrend, 5 in the range, 2 in the selloff and 1 in the rebound), where the SAR flipped 33. That makes it calmer, and also slower: it flagged the selloff at bar 203 but did not turn long until bar 264. The two lines correlate 0.66 on distance from price. It is not a trading system by itself, since a wide stop in a sideways market still produces a string of flips.

## Pairs well with / See also

- [Parabolic SAR](../parabolic-sar/): a trailing stop that tightens as the trend extends, and flips far more often.
- [Average True Range](../average-true-range/): the source of the stop distance.
- [Keltner Channels](../keltner-channels/): a channel built the same way from an average and the ATR.
