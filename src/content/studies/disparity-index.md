---
title: Disparity Index
aliases: [DI, Disparity, Percent Distance From Moving Average]
category: momentum
summary: How far price is from its moving average, as a percentage of that average. Positive means above the average, negative below.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: redundant
status: draft
related: [exponential-moving-average, commodity-channel-index, bollinger-bands]
overlaps:
  - with: exponential-moving-average
    strength: near
    corr: 1.0
    note: "The Disparity Index is the distance from an EMA, as a percentage. The correlation is with the plain distance from the 14-bar EMA, which is 0.997 on the sample."
---

> **In plain English.** A moving average is a "typical recent price". The Disparity Index asks how far today's price is from it, in percent. Plus 3 means price is 3% above its average, and minus 5 means 5% below. When price strays a long way from the average, the idea is that it tends to come back.
>
> **Good for:** a simple, unit-free gauge of how stretched price is from its trend.
>
> **Watch out for:** treating "stretched" as a reason to bet against the move. In a strong trend price stays stretched for a long time.

## What it measures

The percentage gap between the close and a moving average. It is not smoothed, and it is not bounded.

## Calculation

$$
\text{DI}_t = 100 \times \frac{P_t - \text{EMA}_N(P)_t}{\text{EMA}_N(P)_t}
$$

**Worked example.** If the close is 103 and the 14-bar EMA is 100:

$$
100 \times \frac{103 - 100}{100} = +3\%
$$

```python
def disparity_index(close, n=14):
    average = close.ewm(span=n, adjust=False).mean()
    return 100 * (close - average) / average
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/disparity-index-dark.svg">
<img src="../../charts/disparity-index-light.svg" alt="Price above, and the 14-bar Disparity Index below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Disparity Index averaged +1.58 in the uptrend, +0.10 in the range, -3.04 in the selloff and +0.60 in the rebound. Its low of -11.6 came on bar 244.</figcaption>
</figure>

- **Above zero**: price is above its average. **Below zero**: below.
- **Large readings** mark stretched price. What counts as large depends on the instrument: compare today's value with the instrument's own history.
- **Returning to zero** is the usual "mean reversion" idea, and it is not a guarantee.

What it does not tell you: whether the stretch will keep growing. In the sample's selloff the reading went as low as -11.6.

## Best used when

- You want a **percentage** distance from an average, comparable across instruments.
- The market is **ranging**, where stretches tend to fade.

## Avoid when

- The market is **trending**. A stretch can persist, or grow.
- You already use **Bollinger Bands** or **CCI**, which scale the distance by volatility.

## Settings and tuning

- **14** is the usual length. A longer average gives bigger, slower swings.
- **The average type.** This page uses an EMA. A simple average is also common.

## Implementation variations

- **Average.** EMA, as here, or a simple average. Some tools offer both.
- **Ratio form.** Some tools plot the ratio of price to average, centred on 100, instead of the percentage gap.
- **History.** I do not know who devised it.

## Is it useful?

**Redundant.** It is a clean idea, but it is just the distance from an EMA divided by the EMA. On the sample it correlated 0.997 with the plain distance from the same EMA, so any signal it gives, the average itself already gave. Its readings averaged +1.58 in the uptrend, +0.10 in the range, -3.04 in the selloff and +0.60 in the rebound, and read -6.2 at the price low (bar 249). Its one real advantage is the percentage scale. For a distance that adjusts for volatility, look at [Bollinger %B](../bollinger-bands/) or [CCI](../commodity-channel-index/).

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the line it measures from.
- [Commodity Channel Index](../commodity-channel-index/): the distance from an average, scaled by volatility.
- [Bollinger Bands](../bollinger-bands/): the distance from an average, scaled by volatility, drawn on price.
