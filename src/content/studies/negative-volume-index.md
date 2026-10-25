---
title: Negative Volume Index
aliases: [NVI]
category: volume
summary: A price index that only moves on days when volume fell from the day before. The idea is that quiet days are when informed investors act, while busy days are driven by the crowd.
display: panel
inputs:
  - { name: starting value, default: 1000 }
verdict: situational
status: draft
related: [positive-volume-index, on-balance-volume, price-volume-trend]
---

> **In plain English.** Start an index at 1,000. On each day when volume was lower than the previous day, move the index by that day's percentage price change. On days when volume was higher, leave it where it is. The index therefore tracks only what price did on quiet days. The theory is that "smart money" trades quietly, so this shows what they have been doing.
>
> **Good for:** testing the idea that quiet-day moves tell you something that busy-day moves do not.
>
> **Watch out for:** the theory. It is old, plausible, and not demonstrated on this site's data, where volume is synthetic and nearly random.

## What it measures

The cumulative price change on days of falling volume. The level is arbitrary, so only the direction and the comparison with price are read.

## Calculation

$$
\text{NVI}_t =
\begin{cases}
\text{NVI}_{t-1} \times \dfrac{P_t}{P_{t-1}} & \text{if } V_t < V_{t-1} \\[6pt]
\text{NVI}_{t-1} & \text{otherwise}
\end{cases}
$$

with $\text{NVI}_0 = 1000$.

**Worked example.** Closes are 100, 102, 101 and volumes are 10, 9, 11. On day 2, volume fell (9 is below 10), so the index moves by +2%: $1000 \times 1.02 = 1020$. On day 3, volume rose, so the index stays at 1020 even though price fell to 101.

**An exact relationship.** Every day's price change goes into exactly one of the two indexes, the Negative Volume Index or the [Positive Volume Index](../positive-volume-index/), unless volume was unchanged. So, multiplied together and divided by 1,000, they equal the price index exactly. The check script confirms this.

```python
def negative_volume_index(close, volume, start=1000.0):
    change = close.pct_change().where(volume < volume.shift(), 0.0).fillna(0.0)
    return start * (1 + change).cumprod()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/negative-volume-index-dark.svg">
<img src="../../charts/negative-volume-index-light.svg" alt="Price above, and the Negative Volume Index below, with a price index for comparison" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Negative Volume Index (pink) gained 12.8% in the range while the price index (grey) gained 1.5%, and lost 17.2% in the selloff against a price fall of 27.0%. It finished at 1,040 against a price index of 1,039.</figcaption>
</figure>

- **Rising** means price has been gaining on quiet days.
- **Against price.** The usual use is to compare it with price, or with its own long average. The classic rule says that the index above its 255-day average signals a bull market. This page does not test that rule.
- **The level** has no meaning of its own.

What it does not tell you: that quiet days are in fact when informed traders act. That is an assumption.

## Best used when

- You study **long-term** market direction, as the original use suggests, with daily data and a long history.

## Avoid when

- You want **timely** signals. It moves slowly and only on about half the days.
- You apply it to a market where **volume** is not meaningful.

## Settings and tuning

- **The starting value** (1,000 here) changes nothing about its shape.
- **A long average of it** (often 255 days) is the usual companion.

## Implementation variations

- **Start.** 1,000 is common, and some tools start at 100.
- **Volume ties.** A day with exactly the same volume as the day before counts for neither index.
- **History.** It is usually credited to Paul Dysart in the 1930s, and Norman Fosback popularized it much later. I have not confirmed the details.

## Is it useful?

**Situational.** It is a clean idea that is easy to compute, and it has a long history. But nothing here can confirm it. On the sample, the index gained 12.8% in the range while price gained only 1.5%, and lost 17.2% in the selloff against a price fall of 27.0%. The synthetic volume has only a weak link to price moves, so those numbers say nothing about real markets. If you are curious, test it on a long history of an index you trade. If not, it is safe to skip.

## Pairs well with / See also

- [Positive Volume Index](../positive-volume-index/): the same construction on days when volume rose.
- [On-Balance Volume](../on-balance-volume/): another way to bring volume into the picture.
- [Price Volume Trend](../price-volume-trend/): a volume-weighted running total of price change.
