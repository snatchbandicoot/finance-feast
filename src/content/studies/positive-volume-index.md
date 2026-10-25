---
title: Positive Volume Index
aliases: [PVI]
category: volume
summary: A price index that only moves on days when volume rose from the day before. The idea is that busy days show what the crowd is doing, so this index follows the crowd.
display: panel
inputs:
  - { name: starting value, default: 1000 }
verdict: skip
status: draft
related: [negative-volume-index, on-balance-volume, price-volume-trend]
---

> **In plain English.** The mirror image of the Negative Volume Index. Start at 1,000. On each day when volume was higher than the previous day, move the index by that day's percentage price change. Otherwise leave it alone. It tracks what price did on busy days, which the theory says is when the crowd, not the insiders, is in control.
>
> **Good for:** very little by itself. It is mainly useful as the other half of a pair with the Negative Volume Index.
>
> **Watch out for:** treating it as a separate signal. Together, the two indexes just split the price record in two.

## What it measures

The cumulative price change on days of rising volume. As with its twin, only the direction and the comparison with price carry meaning.

## Calculation

$$
\text{PVI}_t =
\begin{cases}
\text{PVI}_{t-1} \times \dfrac{P_t}{P_{t-1}} & \text{if } V_t > V_{t-1} \\[6pt]
\text{PVI}_{t-1} & \text{otherwise}
\end{cases}
$$

with $\text{PVI}_0 = 1000$.

**Worked example.** Closes are 100, 102, 101 and volumes are 10, 9, 11. On day 2, volume fell, so the index stays at 1,000. On day 3, volume rose from 9 to 11, so the index moves with the price change of $101/102 - 1 = -0.98\%$: $1000 \times 101/102 = 990.2$.

Multiplied by the [Negative Volume Index](../negative-volume-index/) and divided by 1,000, it gives the price index exactly. The check script confirms it.

```python
def positive_volume_index(close, volume, start=1000.0):
    change = close.pct_change().where(volume > volume.shift(), 0.0).fillna(0.0)
    return start * (1 + change).cumprod()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/positive-volume-index-dark.svg">
<img src="../../charts/positive-volume-index-light.svg" alt="Price above, and the Positive Volume Index below, with a price index for comparison" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Positive Volume Index (pink) gained 6.2% in the uptrend, lost 10.0% in the range (price gained 1.5%) and ended at 1,000 against a price index of 1,039.</figcaption>
</figure>

- **Rising** means price has been gaining on busy days.
- **Against price and its twin.** The usual use is to compare the two volume indexes with each other and with price.
- **The classic rule** is that the index above its long average (about 255 days) suggests a bull market. This page does not test it.

What it does not tell you: that crowd behavior on busy days predicts anything.

## Best used when

- You study the **pair** of indexes together, on long daily histories.

## Avoid when

- You want a **stand-alone** signal.
- Volume is **unreliable**.

## Settings and tuning

- **The starting value** changes nothing about its shape.
- **A 255-day average** is the usual companion.

## Implementation variations

- **Start.** 1,000 or 100.
- **Volume ties.** Days with unchanged volume count for neither index.
- **History.** It is usually credited to Paul Dysart in the 1930s, with Norman Fosback's later work making it known. I have not confirmed the details.

## Is it useful?

**Skip.** Its twin makes the case for "quiet days carry information". The PVI is the leftover: the part of price movement that happened on busy days. On the sample, it gained 6.2% in the uptrend, lost 10.0% in the range (while price gained 1.5%), and ended at 1,000 against a price index of 1,039. The index differs from price only in what it leaves out, and the volume driving that choice is synthetic here. Read the Negative Volume Index if you want the idea, and skip this one.

## Pairs well with / See also

- [Negative Volume Index](../negative-volume-index/): the same construction on quiet days.
- [On-Balance Volume](../on-balance-volume/): signed volume as a running total.
- [Price Volume Trend](../price-volume-trend/): price change weighted by volume.
