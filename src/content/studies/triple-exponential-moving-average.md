---
title: Triple Exponential Moving Average
aliases: [TEMA, Triple EMA]
category: trend
summary: An exponential average built from three nested EMAs so that its lag cancels almost completely, at the cost of more overshoot.
display: overlay
inputs:
  - { name: length, default: 20 }
verdict: situational
status: draft
related: [double-exponential-moving-average, exponential-moving-average, hull-moving-average]
overlaps:
  - with: double-exponential-moving-average
    strength: partial
    corr: 0.85
    note: "Both cancel the EMA's lag by combining nested EMAs. The TEMA does it with three, so it follows price more closely and overshoots more."
---

> **In plain English.** The DEMA's idea, taken one step further. It combines three nested exponential averages (an EMA, an EMA of that, and an EMA of that again) so that on a steady move the lags cancel and the line sits on price. At turns it overshoots a little more than the DEMA does, and it chops more in sideways markets.
>
> **Good for:** a very responsive trend line that keeps up with a steady move.
>
> **Watch out for:** overshoot. On this site's sample it fell below the price low by 2.8 points after a sharp selloff.

## What it measures

A smoothed price with lag removed on steady moves. A 20-bar EMA trails a steady climb by 9.5 bars, and the TEMA trails it by zero.

## Calculation

With $E_1$ the EMA of price, $E_2$ the EMA of $E_1$ and $E_3$ the EMA of $E_2$, all of length $N$:

$$
\text{TEMA}_t = 3E_1 - 3E_2 + E_3
$$

**Worked example.** If $E_1 = 105$, $E_2 = 103$ and $E_3 = 101.5$, then $\text{TEMA} = 315 - 309 + 101.5 = 107.5$. The line is 2.5 above the plain EMA, because each deeper smoothing is further behind and the formula pushes forward by their accumulated gaps.

**Overshoot.** After a jump from 100 to 110, the TEMA peaks at 111.8 before settling, an overshoot of 1.8 points. The DEMA's was 1.2, and an ordinary EMA has none.

```python
def tema(close, n=20):
    first = close.ewm(span=n, adjust=False).mean()
    second = first.ewm(span=n, adjust=False).mean()
    third = second.ewm(span=n, adjust=False).mean()
    return 3 * first - 3 * second + third
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/triple-exponential-moving-average-dark.svg">
<img src="../../charts/triple-exponential-moving-average-light.svg" alt="Price with a 20-bar TEMA and a 20-bar EMA through a selloff and rebound" width="840" height="430">
</picture>
<figcaption>Synthetic data, zoomed to the end of the range, the selloff and the rebound. The TEMA (pink) bottomed at bar 250 at 86.0, which is 2.8 below the price low of 88.8 (it undershoots), where the EMA (teal) bottomed at 93.7 at bar 260. In the 100-bar range it crossed price 21 times, against 18 for the EMA.</figcaption>
</figure>

Read it as any moving average: slope for direction, price against the line, crossovers for signals. It turns very early, and its early turns are often right and often wrong.

What it does not tell you: whether the turn is real. At a sharp reversal it can swing past the actual extreme, as in the chart above.

## Best used when

- You want a **very fast** trend line and can live with overshoot.
- Price is **trending steadily**, so that the lag cancellation helps.

## Avoid when

- Price is **sideways**. In the sample it crossed price 21 times in the range, against 18 for the EMA.
- You use the line's value as a **price level**. At turns it can sit below the low or above the high that price actually made.
- You want **smoothness**. Three nested averages with cancelled lag are not smooth.

## Settings and tuning

- **Length 20** is a common default. Because the lag is cancelled, a given length is much faster than the same length of EMA.
- Shorter is faster and noisier, and longer is smoother and later.

## Implementation variations

- **Seeding.** All three EMAs need starting values, and early values depend on them.
- **Naming.** "TEMA" is sometimes confused with "triple smoothing" as used in TRIX, which is a different, much slower line.
- **History.** It is usually credited to Patrick Mulloy. I have not confirmed the details.

## Is it useful?

**Situational.** It is the most responsive of the EMA family, and for the same reason the most prone to overshoot and noise. The sample shows both sides: it turned at bar 250 (almost with price), but at a level of 86.0, which is below the real low of 88.8. It correlates 0.85 with the DEMA (measured on distance from price), so choose one or the other. If a fast line matters to you, either is a reasonable choice. If you want a trend line to *read*, an ordinary EMA is easier to trust.

## Pairs well with / See also

- [Double Exponential Moving Average](../double-exponential-moving-average/): the same idea with two nested averages.
- [Exponential Moving Average](../exponential-moving-average/): the building block.
- [Hull Moving Average](../hull-moving-average/): another low-lag average, built from weighted averages.
