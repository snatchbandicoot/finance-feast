---
title: Price Volume Trend
aliases: [PVT, Volume Price Trend, VPT]
category: volume
summary: A running total that adds each bar's volume multiplied by its percentage price change. It is like On-Balance Volume, except that a big move counts for more than a small one.
display: panel
inputs: []
verdict: redundant
status: draft
related: [on-balance-volume, rate-of-change, accumulation-distribution]
overlaps:
  - with: on-balance-volume
    strength: partial
    corr: 0.78
    note: "Both are running totals of volume signed by the direction of the close-to-close change. The PVT also scales by the size of the change. The correlation is between the 20-bar changes of the two."
  - with: rate-of-change
    strength: near
    corr: 0.98
    note: "With volume that varies only moderately, the PVT mostly follows price momentum. The correlation is between its 20-bar change and a 20-bar rate of change."
---

> **In plain English.** On-Balance Volume adds a bar's full volume if price rose and subtracts it if price fell, however small the move. The Price Volume Trend is a refinement: it adds the volume times the percentage change. A 3% rise on heavy volume adds a lot, and a 0.1% rise on heavy volume adds almost nothing.
>
> **Good for:** a more proportionate version of OBV.
>
> **Watch out for:** how little it adds. With ordinary volume it mostly tracks price. On the sample, its 20-bar change correlated 0.98 with a 20-bar rate of change.

## What it measures

A cumulative sum of volume, weighted by the percentage price move.

## Calculation

$$
\text{PVT}_t = \text{PVT}_{t-1} + V_t \times \left(\frac{P_t}{P_{t-1}} - 1\right)
$$

**Worked example.** Closes are 100, 102 and 101, with volumes of 500, 1,000 and 2,000. On day 2, price rose 2% on volume of 1,000, adding $0.02 \times 1000 = +20$. On day 3, price fell 0.98% on volume of 2,000, adding $-0.0098 \times 2000 = -19.6$. The total is $20 - 19.6 = 0.4$. OBV would have said $+1000 - 2000 = -1000$, a very different picture.

```python
def price_volume_trend(close, volume):
    return (close.pct_change().fillna(0.0) * volume).cumsum()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/price-volume-trend-dark.svg">
<img src="../../charts/price-volume-trend-light.svg" alt="Price above, and the Price Volume Trend below" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Price Volume Trend rose 0.10 million over the uptrend and fell 0.36 million in the selloff. It peaked at 0.30 million on bar 175, bottomed at -0.08 million on bar 244 and ended at 0.13 million.</figcaption>
</figure>

- **Direction.** Rising means volume has been landing on up-moves in proportion to their size.
- **Divergence.** The line failing to confirm a new price high or low is the usual caution.
- **The level** has no meaning of its own, since it depends on the start.

What it does not tell you: anything much that price does not. It shows the same turns, with some extra weight on volume.

## Best used when

- You like OBV but find its **equal weighting** of tiny and huge moves unhelpful.

## Avoid when

- You want **new information**. It mostly follows price.
- **Volume is unreliable.**
- Price has **gaps**. A large gap adds a large amount, which may or may not be meaningful.

## Settings and tuning

- **No settings.**

## Implementation variations

- **Start.** It starts at zero here, and some tools start at the first bar's volume.
- **Simple or percentage change.** Percentages here.
- **Naming.** "Volume Price Trend" is the same indicator under another name.

## Is it useful?

**Redundant.** It is a reasonable refinement of OBV. On the sample, its 20-bar change correlated 0.78 with OBV's and 0.98 with a 20-bar rate of change, and the line itself correlated 0.985 with the close. It gained 0.10 million over the uptrend and lost 0.36 million over the selloff, which is only what price did. For a volume view you can use that is truly different from price, try OBV, CMF or the A/D line, or the Money Flow Index.

## Pairs well with / See also

- [On-Balance Volume](../on-balance-volume/): the simpler cousin.
- [Rate of Change](../rate-of-change/): what it mostly follows.
- [Accumulation/Distribution Line](../accumulation-distribution/): volume weighted by the close's position.
