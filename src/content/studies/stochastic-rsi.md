---
title: Stochastic RSI
aliases: [StochRSI, Stoch RSI]
category: momentum
summary: The Stochastic formula applied to RSI instead of price, showing where RSI sits within its own recent range. It swings between 0 and 100 far more often than RSI does.
display: panel
inputs:
  - { name: rsi length, default: 14 }
  - { name: stochastic length, default: 14 }
  - { name: smooth K, default: 3 }
  - { name: smooth D, default: 3 }
verdict: situational
status: draft
related: [relative-strength-index, stochastic-oscillator, williams-percent-r]
overlaps:
  - with: stochastic-oscillator
    strength: partial
    corr: 0.82
    note: "Both place a value inside a recent high-low range and smooth it. One does it to price, the other to RSI. The correlation is between the two %K lines."
---

> **In plain English.** RSI tells you how strong recent gains were compared with recent losses. Stochastic RSI asks a different question of that number: *is RSI near the top or the bottom of where it has been lately?* The answer is a line between 0 and 100 that reaches both ends often. That makes it a sensitive timing tool, and also a noisy one.
>
> **Good for:** spotting short-term turns inside a market that is not trending hard, when ordinary RSI barely moves.
>
> **Watch out for:** how often it sits at an extreme. On this site's sample data it was above 80 on 23% of bars and below 20 on 28%, where RSI was above 70 on 6% and below 30 on 8%. A reading at an extreme is common, so by itself it says little.

## What it measures

The position of today's RSI within its own range over the last N bars. It is the Stochastic Oscillator's formula, with RSI as the input instead of price. It does not measure price momentum directly. It measures how unusual RSI is compared with itself.

## Calculation

First compute RSI (see [Relative Strength Index](../relative-strength-index/)). Then, over a window of $N$ bars:

$$
\text{raw}_t = 100 \times \frac{\text{RSI}_t - \min_N(\text{RSI})}{\max_N(\text{RSI}) - \min_N(\text{RSI})}
$$

$\%K$ is a short simple average of the raw value (3 bars by default) and $\%D$ is a short average of $\%K$ (3 bars again).

**Worked example.** Suppose today's RSI is 55, and over the last 14 bars RSI has ranged from 40 to 60:

$$
100 \times \frac{55 - 40}{60 - 40} = 75
$$

The raw value is 75: RSI is three quarters of the way up its recent range. Notice that an RSI of 55 is unremarkable on its own, yet here it reads 75.

**Undefined values.** If RSI has not changed at all over the window (for example during an unbroken climb that holds RSI at 100), the range is zero and the value is undefined. The snippet returns a missing value rather than dividing by zero.

```python
def stoch_rsi(close, n=14, smooth_k=3, smooth_d=3):
    r = rsi(close, n)
    low, high = r.rolling(n).min(), r.rolling(n).max()
    raw = 100 * (r - low) / (high - low).replace(0, np.nan)
    k = raw.rolling(smooth_k).mean()
    return k, k.rolling(smooth_d).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/stochastic-rsi-dark.svg">
<img src="../../charts/stochastic-rsi-light.svg" alt="Price above, and Stochastic RSI percent K and percent D below, with lines at 20 and 80" width="840" height="590">
</picture>
<figcaption>Synthetic data. %K was above 80 on 23% of scored bars and below 20 on 28%. In the selloff it was below 20 on 46% of bars, and at the price low (bar 249) it read 20.3. %K crossed %D 57 times.</figcaption>
</figure>

- **Above 80 and below 20** are the usual zones. Because the line reaches them so often, treat them as "stretched for now", not as signals.
- **%K crossing %D** is the usual timing cue. It happened 57 times over the sample, which is a lot.
- **Direction.** A rising line says RSI is climbing within its range. It does not say price is climbing.

What it does not tell you: whether a turn will last. It reacts to RSI's wobbles, which are themselves reacting to price.

## Best used when

- The market is **ranging or drifting** and you want an earlier, more sensitive signal than RSI gives.
- You want RSI **rescaled** so its extremes are always reachable.

## Avoid when

- The market is **trending strongly**. In the sample's first 40 scored bars of uptrend it was above 80 on 38% of bars and gave no useful "overbought" warning.
- You want **few signals**. It produces many.
- The input is **flat or one-directional**, so that RSI does not move and the range collapses.

## Settings and tuning

- **14 / 14 / 3 / 3** are the usual values. The RSI length and the window are often set equal.
- **Shorter windows** make it even jumpier. **Longer windows** make it behave more like RSI.
- Some tools skip the smoothing and plot the raw value, which is very jagged.

## Implementation variations

- **Scale.** Some tools show 0 to 1 and others 0 to 100. This page uses 0 to 100.
- **Smoothing.** %K is sometimes left unsmoothed, and the default smoothing differs between tools.
- **RSI seed.** The RSI inside it uses the same recursive average as [RSI](../relative-strength-index/), so the early values depend on the seed. The chart hides the first 60 bars.
- **History.** It is usually credited to Tushar Chande and Stanley Kroll, from the 1990s. I have not confirmed the details.

## Is it useful?

**Situational.** It is RSI with the volume turned up. On the sample data its %K tracked the ordinary Stochastic's %K at a correlation of 0.82, and it tracked RSI itself at only 0.55, which shows it is mostly telling you something different from RSI: where RSI is within its range. That has some value for timing short swings. It is also very busy, and the price low at bar 249 came with a reading of 20.3, not a clean extreme. Use it as a sensitive timer, not as a stand-alone signal, and expect false alarms.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): the input, and the better first choice.
- [Stochastic Oscillator](../stochastic-oscillator/): the same formula applied to price.
- [Williams %R](../williams-percent-r/): the same idea again, inverted.
