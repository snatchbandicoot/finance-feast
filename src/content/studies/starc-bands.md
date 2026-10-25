---
title: STARC Bands
aliases: [Stoller Average Range Channels, STARC]
category: volatility
summary: A short moving average with bands set a multiple of the Average True Range above and below it. The average is fast and the bands are wide, so price touches them only in unusually strong moves.
display: overlay
inputs:
  - { name: average length, default: 6 }
  - { name: ATR length, default: 15 }
  - { name: multiplier, default: 2 }
verdict: situational
status: draft
related: [keltner-channels, bollinger-bands, average-true-range]
overlaps:
  - with: keltner-channels
    strength: partial
    corr: 0.94
    note: "Both are a moving average with bands a multiple of the ATR away. STARC uses a short simple average and a longer ATR, so its bands are wider and slower. The correlation is between the band widths as a share of the middle line."
---

> **In plain English.** Take a quick 6-bar average of closes and add and subtract two times the 15-bar Average True Range. Because the center line follows price closely and the bands are wide, price rarely reaches them. When it does, the move is unusual, and the idea is that it may be stretched.
>
> **Good for:** marking unusually large moves from a fast average, with a width that follows the market's volatility.
>
> **Watch out for:** how seldom it touches. On the sample, closes were above the upper band on 0.8% of bars and below the lower band on 1.2%.

## What it measures

How far price has moved from a fast average, in units of typical bar range. The band edge is the point where the move is unusually large for the recent volatility.

## Calculation

$$
\text{Middle}_t = \text{SMA}_6(C)_t \qquad \text{Upper}_t = \text{Middle}_t + 2 \times \text{ATR}_{15,t} \qquad \text{Lower}_t = \text{Middle}_t - 2 \times \text{ATR}_{15,t}
$$

The ATR here is a simple 15-bar average of the true range (see [Average True Range](../average-true-range/)).

**Worked example.** If the 6-bar average is 100 and the 15-bar ATR is 2, the upper band is $100 + 2 \times 2 = 104$ and the lower band is $100 - 2 \times 2 = 96$. With bars of constant size the check script reproduces exactly these numbers.

```python
def starc_bands(high, low, close, n=6, atr_n=15, k=2):
    prev_close = close.shift()
    true_range = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    atr = true_range.rolling(atr_n).mean()
    middle = close.rolling(n).mean()
    return middle, middle + k * atr, middle - k * atr
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/starc-bands-dark.svg">
<img src="../../charts/starc-bands-light.svg" alt="Price with STARC Bands, a 6-bar average plus and minus two times the 15-bar ATR" width="840" height="440">
</picture>
<figcaption>Synthetic data. Closes were above the upper band on 0.8% of scored bars and below the lower band on 1.2%. The band width averaged 6.0% of price in the uptrend and range, 8.9% in the selloff and 7.0% in the rebound.</figcaption>
</figure>

- **Price at or beyond the upper band** is read as overbought, and **below the lower band** as oversold. Many traders also read a push beyond a band as a trend start.
- **Band width** follows volatility. Wider after big moves, narrower in calm stretches.
- **The middle line** is a very short average, so it is nearly price itself.

What it does not tell you: whether a touch means "reversal" or "breakout". Strong trends can run along a band for a long time.

## Best used when

- You want a **fast, wide** channel that flags only large moves.
- You use bands as **profit targets** or **stretch warnings**.

## Avoid when

- You expect **frequent** touches. This setup produces few.
- You want a middle line that shows **trend**. A 6-bar average is too fast for that.

## Settings and tuning

- **6, 15 and 2** are the usual values. A larger multiplier gives rarer touches.
- **A longer average** slows the middle line and makes touches more frequent.

## Implementation variations

- **ATR smoothing.** A simple average of true range, as here. Some tools use Wilder's smoothing.
- **Middle line.** A simple average here. Some versions use another type.
- **History.** It is usually credited to Manning Stoller. I have not confirmed the details.

## Is it useful?

**Situational.** It is a reasonable wide-band tool, and it is related to Keltner Channels, which have a slower average and a shorter ATR (their widths, as a share of the middle line, correlated 0.94 on the sample). The difference is how often price touches: STARC's upper band was exceeded on 0.8% of the sample's scored bars, against 8.1% for the standard Keltner Channels' upper band. Its width averaged 6.0% of price in the uptrend and range, 8.9% in the selloff and 7.0% in the rebound. If you want bands that price visits often, use Bollinger or Keltner. For a stretch warning that fires rarely, this is it.

## Pairs well with / See also

- [Keltner Channels](../keltner-channels/): the closest relative, with tighter bands.
- [Bollinger Bands](../bollinger-bands/): bands set by standard deviation.
- [Average True Range](../average-true-range/): the volatility measure that sets the band width.
