---
title: Force Index
aliases: [FI, Elder Force Index]
category: volume
summary: Multiplies each bar's price change by its volume, then smooths the result. It combines how far price moved and how much traded behind it into one number, positive in up-moves and negative in down-moves.
display: panel
inputs:
  - { name: smoothing length, default: 13 }
verdict: situational
status: draft
related: [on-balance-volume, rate-of-change, money-flow-index]
overlaps:
  - with: on-balance-volume
    strength: partial
    corr: 0.69
    note: "Both sign volume by the direction of the close-to-close change. The Force Index also scales it by the size of the change, and smooths it. The correlation is with the 13-bar change in OBV."
  - with: rate-of-change
    strength: partial
    corr: 0.87
    note: "The Force Index is a smoothed price change with volume as a weight. The correlation is with a 12-bar rate of change."
---

> **In plain English.** A big move on heavy volume has more force than a big move on light volume, and more than a small move on heavy volume. The Force Index puts that into one number: the change in price times the volume, smoothed over 13 bars. Positive means rising prices with weight behind them. Negative means falling prices with weight behind them.
>
> **Good for:** judging whether a move had conviction, in terms of volume.
>
> **Watch out for:** how closely it follows price momentum. On the sample, it correlated 0.87 with a plain 12-bar rate of change.

## What it measures

The weight of each bar's move, as price change times volume, smoothed. Volume amplifies large moves.

## Calculation

$$
\text{raw}_t = (C_t - C_{t-1}) \times V_t \qquad \text{FI}_t = \text{EMA}_{13}(\text{raw})_t
$$

**Worked example.** Price rises from 10 to 12 on volume of 1,500: the raw force is $2 \times 1500 = +3000$. Next, price falls from 12 to 11 on volume of 2,000: the raw force is $-1 \times 2000 = -2000$. The smoothing then blends these raw numbers, with the newest weighted most.

```python
def force_index(close, volume, n=13):
    return (close.diff() * volume).ewm(span=n, adjust=False).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/force-index-dark.svg">
<img src="../../charts/force-index-light.svg" alt="Price above, and the 13-bar Force Index below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Force Index ranged from -2.47 million (bar 243) to +1.10 million (bar 85) and crossed zero 42 times. It was above zero on 80% of the uptrend's scored bars and 30% of the selloff's.</figcaption>
</figure>

- **Above zero**: the weight is behind buyers. **Below zero**: behind sellers.
- **Zero crossings** signal a change in who has the weight. The sample's line crossed zero 42 times, which is a lot.
- **Extremes.** A very large reading, relative to recent history, shows a forceful move. The sample's lowest reading was in the selloff, at bar 243.
- **Short smoothing (2)** is used by some traders for timing, and the 13-bar for trend.

What it does not tell you: whether the force will continue. Its scale is in share-price units, so compare it only with its own recent past.

## Best used when

- You want to judge **conviction** behind a move.
- You use **divergences**: price making a new high on weaker force.

## Avoid when

- You compare **across instruments**: the units differ.
- **Volume is unreliable.**
- You want a simple signal. The zero line is crossed very often.

## Settings and tuning

- **13** is the usual smoothing. **2** is the faster version.
- **Longer smoothing** gives fewer crossings.

## Implementation variations

- **Raw or smoothed.** The unsmoothed series is the raw force, and is very jumpy.
- **Start.** The first value uses the first available change.
- **History.** It is usually credited to Alexander Elder. I have not confirmed the details.

## Is it useful?

**Situational.** The product of price change and volume is a natural way to say "how big, and how backed". On the sample, the line was above zero on 80% of the uptrend's scored bars, 46% of the range's, 30% of the selloff's and 71% of the rebound's. But it correlated 0.87 with a plain rate of change and 0.69 with the change in OBV, so much of what it shows is already visible in price. Its value is the volume weighting. Where volume is meaningful, it is a decent conviction gauge. Where not, it is a rate of change with extra steps.

## Pairs well with / See also

- [On-Balance Volume](../on-balance-volume/): signed volume as a running total.
- [Rate of Change](../rate-of-change/): the price-only version.
- [Money Flow Index](../money-flow-index/): another volume-weighted oscillator.
