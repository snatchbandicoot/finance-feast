---
title: Displaced EMA
aliases: [Displaced Moving Average, DMA, Shifted EMA]
category: trend
summary: An exponential average plotted several bars late. It pushes the line away from price so that it acts as a delayed trend filter, and it is nothing more than an EMA with a lag added.
display: overlay
inputs:
  - { name: length, default: 20 }
  - { name: displacement, default: 5 }
verdict: redundant
status: draft
related: [exponential-moving-average, simple-moving-average, ichimoku-cloud]
overlaps:
  - with: exponential-moving-average
    strength: near
    corr: 0.99
    note: "The displaced line is the same EMA, drawn later. The correlation is with the distance of price from the undisplaced EMA, which is 0.991 on the sample."
---

> **In plain English.** Take an ordinary exponential average and shift it to the right by a few bars, so that today's line shows what the average was 5 bars ago. It makes the line trail price more and cross price less often. Nothing is added to the information. The only change is the extra delay.
>
> **Good for:** a deliberately slow reference line, such as a trend filter or a stop that should give price room.
>
> **Watch out for:** the delay, which is not a feature of the market. You are choosing to see old data.

## What it measures

The EMA as it stood a few bars ago. The shift changes timing only.

## Calculation

$$
\text{DEMA}_t = \text{EMA}_N(P)_{t - s}
$$

with a length $N$ (20) and a displacement $s$ (5).

**Worked example.** If the 20-bar EMA was 100 five bars ago and is 104 now, the displaced line shows 100 today. On a steady climb of 1 point a bar, the EMA trails price by about 9.5 bars, so the displaced line trails by $9.5 + 5 = 14.5$. The check script confirms the arithmetic on such a climb.

**Looking ahead.** A displacement the other way, plotting the line into the future, would need data that does not exist yet. Tools draw it on the chart to the right, but it cannot be known in advance. This page uses only the delay that can be computed in real time.

```python
def displaced_ema(close, n=20, shift=5):
    return close.ewm(span=n, adjust=False).mean().shift(shift)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/displaced-ema-dark.svg">
<img src="../../charts/displaced-ema-light.svg" alt="Price with a 20-bar EMA displaced by 5 bars and the plain 20-bar EMA through a selloff and rebound" width="840" height="430">
</picture>
<figcaption>Synthetic data, zoomed to the end of the range, the selloff and the rebound. The displaced line (pink) is the plain EMA (teal) drawn 5 bars later. Price crossed it 12 times in the range, against 18 for the plain EMA.</figcaption>
</figure>

- **Price against the line**: above is bullish, below bearish, as with any average. The cross comes later than the EMA's.
- **The gap** between price and the displaced line is wider than to the EMA, so a cross means a larger reversal.
- **As a stop** it gives price room.

What it does not tell you: anything the EMA did not. It has the same information, arriving later.

## Best used when

- You want a **slow filter** and prefer to get it by delaying a familiar line.

## Avoid when

- You can get the same effect from a **longer EMA**, with a smoother line and no artificial delay.
- You want **timely** signals.

## Settings and tuning

- **20 and 5** are typical. A larger displacement is slower.
- **Zero** displacement is the plain EMA.

## Implementation variations

- **Displacement direction.** Most tools plot forward in time. This page computes only the backward-looking version.
- **Average type.** Some tools allow other averages. This page uses an EMA.
- **History.** I do not know who devised it.

## Is it useful?

**Redundant.** It is a plain EMA with a delay, and the distance from it correlated 0.991 with the distance from the undisplaced EMA. The delay does cut crossovers: price crossed it 12 times in the range against 18 for the EMA, and 5 times in the rebound against 11. But those are the signals that came late, or never. A longer EMA gives a similar result with a smoother line. Unless a method you follow calls for it, use an EMA of the length you want.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the line it displaces.
- [Simple Moving Average](../simple-moving-average/): another basic average.
- [Ichimoku Cloud](../ichimoku-cloud/): a system that also shifts lines in time.
