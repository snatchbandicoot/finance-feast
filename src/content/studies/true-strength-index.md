---
title: True Strength Index
aliases: [TSI]
category: momentum
summary: A momentum line built from price changes smoothed twice, divided by the same smoothing of the changes' size, so it runs from -100 to +100 and is easy to read as a share of direction.
display: panel
inputs:
  - { name: long smoothing, default: 25 }
  - { name: short smoothing, default: 13 }
  - { name: signal length, default: 7 }
verdict: redundant
status: draft
related: [macd, relative-strength-index, rate-of-change, know-sure-thing]
overlaps:
  - with: macd
    strength: near
    corr: 0.98
    note: "Both smooth price changes with exponential averages and cross zero when the trend turns. The TSI normalizes the result to a share of -100 to +100. The correlation is between the two lines."
---

> **In plain English.** Take each day's price change. Smooth it twice. Then divide by the same smoothing applied to the *size* of each change, ignoring direction. What is left is a number from -100 to +100: how much of the recent movement has been in one direction. +100 would mean every move was up. Zero means ups and downs cancel.
>
> **Good for:** a smooth, readable momentum line with built-in scale, where zero is a trend-direction line.
>
> **Watch out for:** how closely it matches MACD. On the sample it correlated 0.98, so the two mostly agree about everything.

## What it measures

The net directional share of recent price movement. If most of the movement was up, it is high and positive. If it was evenly split, it is near zero.

## Calculation

Let $\Delta_t = P_t - P_{t-1}$ be the change in price. Smooth it, and its absolute value, twice with exponential averages (a long one, then a short one):

$$
\text{TSI}_t = 100 \times \frac{\text{EMA}_{s}(\text{EMA}_{l}(\Delta))}{\text{EMA}_{s}(\text{EMA}_{l}(|\Delta|))}
$$

The signal line is an exponential average of the TSI, 7 bars by default.

**Worked example** (with both smoothings set to 3 bars so the arithmetic stays short; the smoothing weight is $\alpha = 2/(3+1) = 0.5$). Closes of 10, 12, 13 and 12 give changes of +2, +1 and -1. Each exponential average starts at the first value:

| Step | Bar 1 | Bar 2 | Bar 3 |
|---|---|---|---|
| Change | 2 | 1 | -1 |
| First average of change | 2 | 1.5 | 0.25 |
| Second average of change (numerator) | 2 | 1.75 | 1.0 |
| First average of $|\text{change}|$ | 2 | 1.5 | 1.25 |
| Second average of $|\text{change}|$ (denominator) | 2 | 1.75 | 1.5 |

On bar 3 the TSI is $100 \times 1.0 / 1.5 = 66.7$. The latest down move reduced it from 100, but the up moves still dominate.

```python
def tsi(close, long=25, short=13, signal=7):
    change = close.diff()

    def twice(x):
        return x.ewm(span=long, adjust=False).mean().ewm(span=short, adjust=False).mean()

    line = 100 * twice(change) / twice(change.abs())
    return line, line.ewm(span=signal, adjust=False).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/true-strength-index-dark.svg">
<img src="../../charts/true-strength-index-light.svg" alt="Price above, and the True Strength Index with its signal line below, with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The TSI ranged from -60.8 to +41.6. It was above zero on all of the uptrend's scored bars, 59% of the range's, 2% of the selloff's and 71% of the rebound's. Its low came on bar 249, the price low.</figcaption>
</figure>

- **Zero line.** Above zero means up-moves have dominated recently. Below zero means down-moves have.
- **Signal crossovers.** The TSI crossing its signal line is a faster cue than the zero cross, and noisier: 14 times in the 100-bar range.
- **Extremes.** There are no official overbought or oversold levels. ±25 is a common eyeballed guide, but in the sample the TSI never got above +42.
- **Divergence.** Price making a new low while the TSI does not is the usual caution.

What it does not tell you: how big the moves were in absolute terms, only the direction-share. A quiet drift and a violent rally can read alike.

## Best used when

- You want **MACD-like information with a built-in scale**.
- You compare **across instruments**, where the percentage-like scale helps.

## Avoid when

- **You already use MACD.** The two lines correlated 0.98 on the sample.
- The market is **choppy**. The signal crosses back and forth.
- You need a **very early** signal. Two long smoothings delay it.

## Settings and tuning

- **25 / 13 / 7** are the usual values. The long smoothing does most of the work.
- **Shorter smoothings** react sooner and wobble more.
- With a very short window it behaves like a smoothed version of the up-share of changes.

## Implementation variations

- **Seeding.** The early values depend on how the exponential averages start. The first reading here is -100 for that reason. The chart hides the first 60 bars.
- **Signal.** Some tools omit the signal line or use different lengths.
- **Scale.** Some tools plot ±1 instead of ±100.
- **History.** It is usually credited to William Blau, from the 1990s. I have not confirmed the details.

## Is it useful?

**Redundant.** The construction is tidy, and the result is easy to read. But the TSI correlated 0.98 with MACD's line on the sample, and 0.86 with RSI. In the range it crossed zero 5 times, as MACD did. In the selloff it was positive on only 2% of bars, and its low of -60.8 came on bar 249, the price low itself. If you want a scale-free MACD, use the [PPO](../percentage-price-oscillator/) or this. Otherwise, MACD already does the job.

## Pairs well with / See also

- [MACD](../macd/): the near twin.
- [Relative Strength Index](../relative-strength-index/): another bounded read of up versus down movement.
- [Rate of Change](../rate-of-change/): the unsmoothed version of the same idea.
- [Know Sure Thing](../know-sure-thing/): another smoothed momentum line.
