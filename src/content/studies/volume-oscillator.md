---
title: Volume Oscillator
aliases: [VO, Volume Rate of Change Oscillator]
category: volume
summary: The percentage difference between a fast and a slow average of volume. It tells you whether trading activity is picking up or fading, and says nothing about whether price is rising or falling.
display: panel
inputs:
  - { name: fast, default: 5 }
  - { name: slow, default: 10 }
verdict: situational
status: draft
related: [on-balance-volume, percentage-price-oscillator, accumulation-distribution]
overlaps:
  - with: percentage-price-oscillator
    strength: identical
    note: "The Volume Oscillator is the PPO line computed on volume instead of price."
---

> **In plain English.** Is trading busier than it has been lately, or quieter? The Volume Oscillator compares a short-term average of volume with a longer one, as a percentage. Above zero, volume is picking up. Below zero, it is drying up. It has no opinion on direction.
>
> **Good for:** checking whether a breakout or a move has participation behind it.
>
> **Watch out for:** reading it as bullish or bearish. High volume is neither.

## What it measures

The change in the pace of trading, relative to its recent norm.

## Calculation

$$
\text{VO}_t = 100 \times \frac{\text{EMA}_{5}(V)_t - \text{EMA}_{10}(V)_t}{\text{EMA}_{10}(V)_t}
$$

**Worked example.** If the 5-bar average volume is 1.2 million and the 10-bar average is 1.0 million:

$$
100 \times \frac{1.2 - 1.0}{1.0} = +20
$$

Recent volume is 20% above the longer-run pace.

**An exact identity.** This is the [PPO](../percentage-price-oscillator/) line applied to volume instead of price. The check script confirms that the two agree to the last digit.

```python
def volume_oscillator(volume, fast=5, slow=10):
    slow_avg = volume.ewm(span=slow, adjust=False).mean()
    return 100 * (volume.ewm(span=fast, adjust=False).mean() - slow_avg) / slow_avg
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/volume-oscillator-dark.svg">
<img src="../../charts/volume-oscillator-light.svg" alt="Price above, and the Volume Oscillator below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Volume Oscillator ranged from -12.6 to +13.6 and was above zero on 46% of the scored bars. It showed no clear link with the regimes: 50% in the uptrend, 40% in the range, 48% in the selloff, 50% in the rebound.</figcaption>
</figure>

- **Above zero**: volume is increasing. **Below zero**: it is decreasing.
- **A rising price with a rising oscillator** is read as a move with participation. **A rising price with a falling oscillator** is read as a move running out of interest.
- **Extreme readings** mark unusually busy or quiet spells.

What it does not tell you: whether the activity is buying or selling.

## Best used when

- You want to judge whether a move has **participation**.
- You study **breakouts**, which are expected to come with higher volume.

## Avoid when

- You use it as a **direction** signal.
- **Volume is unreliable** or missing.

## Settings and tuning

- **5 and 10** are the usual values. Longer pairs, such as 14 and 28, give a slower read.
- **Averages.** Exponential here. Some tools use simple averages.

## Implementation variations

- **Percent or difference.** Some tools show the plain difference instead of the percentage.
- **Smoothing type.** Simple or exponential.

## Is it useful?

**Situational.** It is an honest, simple measure of whether activity is rising. On the sample, it was above zero on 46% of the scored bars and showed no clear link with the regimes: it was above zero on 50% of the uptrend's bars, 40% of the range's, 48% of the selloff's and 50% of the rebound's. The sample's volume is synthetic and has only a weak link to price movement, so it cannot say whether real breakouts come with volume. In real markets, volume surges at turning points are common, and this is a tidy way to see them. Treat it as context for other signals, and never as a signal on its own.

## Pairs well with / See also

- [Percentage Price Oscillator](../percentage-price-oscillator/): the same formula on price.
- [On-Balance Volume](../on-balance-volume/): a running total of signed volume.
- [Accumulation/Distribution Line](../accumulation-distribution/): volume weighted by where the close sits.
