---
title: Weighted Moving Average
aliases: [WMA, Linearly Weighted Moving Average, LWMA]
category: trend
summary: An average in which each bar's weight rises steadily from the oldest bar to the newest, so recent prices count for more.
display: overlay
inputs:
  - { name: length, default: 20 }
verdict: redundant
status: draft
related: [simple-moving-average, exponential-moving-average, hull-moving-average]
overlaps:
  - with: simple-moving-average
    strength: near
    corr: 0.97
    note: "Both are averages of the last N prices. The weighted version leans a little toward recent bars, and the correlation is measured on how far price sits from each average."
  - with: exponential-moving-average
    strength: near
    corr: 0.96
    note: "Both give recent prices more weight, in different ways: steadily rising weights here, and geometrically shrinking weights in the EMA."
---

> **In plain English.** An average where recent bars count for more, in a straight-line way: the newest bar gets a weight of N, the one before it N − 1, and so on down to 1 for the oldest. It reacts sooner than a simple average of the same length, but it is still a smooth, ordinary moving average.
>
> **Good for:** a slightly quicker moving average, and as a building block, since the Hull moving average is made from it.
>
> **Watch out for:** treating it as a different kind of tool. On this site's sample data it behaved almost like the simple average (correlation 0.97) and the exponential average (0.96).

## What it measures

The same thing as the other moving averages: where price has been, on average, over the last $N$ bars. The only difference is the weighting. The simple average gives every bar the same say. The exponential average gives recent bars far more say, with weights that shrink geometrically. The weighted average sits between them, with weights that fall off in a straight line.

## Calculation

$$
\text{WMA}_t = \frac{\sum_{k=1}^{N} k \cdot P_{t-N+k}}{N(N+1)/2}
$$

The newest price has weight $N$ and the oldest has weight 1, and the weights add up to $N(N+1)/2$.

**Worked example.** With $N = 3$ and the last three closes 10, 11, 13 (oldest first), the weights are 1, 2, 3: $(1 \times 10 + 2 \times 11 + 3 \times 13)/6 = 71/6 \approx 11.83$. The simple average of the same prices is 11.33, so the weighted version has moved further toward the latest close.

**Lag.** On a steady climb, a simple or exponential average of length $N$ trails price by $(N-1)/2$ bars. The weighted average trails by $(N-1)/3$, so for $N = 20$ that is 6.3 bars against 9.5. The check script confirms both.

```python
def wma(close, n=20):
    weights = np.arange(1, n + 1)
    return close.rolling(n).apply(lambda w: np.dot(w, weights) / weights.sum(), raw=True)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/weighted-moving-average-dark.svg">
<img src="../../charts/weighted-moving-average-light.svg" alt="Price with a 20-bar weighted and a 20-bar simple moving average through a selloff and rebound" width="840" height="430">
</picture>
<figcaption>Synthetic data, zoomed to the end of the range, the selloff and the rebound. The WMA (pink) sits between price and the SMA (teal): its low was 91.0 at bar 257, against 91.1 at bar 261 for the SMA. In the 100-bar range it crossed price 14 times, against 12 for the SMA and 18 for the EMA.</figcaption>
</figure>

Read it as you would any moving average (see the [Simple Moving Average](../simple-moving-average/) page):

- **Slope** shows direction, and **price above or below the line** shows where price sits against its recent average.
- **Crossovers** with price or with a longer average are the usual signals, and they lag.
- It turns a little sooner than a simple average, and a little later than the Hull or the double and triple exponential averages.

What it does not tell you: where price goes next.

## Best used when

- You want a **modest** speed-up over a simple average, without the overshoot of the lower-lag averages.
- You are building a **second study** on top of an average, as the Hull moving average does.

## Avoid when

- Price is **sideways**. Like every average, it keeps crossing price, and every cross is noise.
- You expect it to be meaningfully **different** from the SMA or the EMA. In practice it is not.

## Settings and tuning

- **Length** works as for the other averages: shorter is faster and noisier, longer is smoother and later.
- There are no other settings, since the weights are fixed.

## Implementation variations

- **Weights.** The linear weights above are the standard. A few tools offer other weight shapes, which makes them different averages.
- **Names.** "Linearly weighted moving average" and "WMA" are used for the same thing.

## Is it useful?

**Redundant.** It is a moving average with a slightly different weight shape, and in practice it sits between the SMA and the EMA. On the sample data the distance of price from each correlated at 0.97 with the SMA and 0.96 with the EMA. If you already use either, the WMA adds almost nothing, apart from its role as the ingredient in the [Hull Moving Average](../hull-moving-average/).

## Pairs well with / See also

- [Simple Moving Average](../simple-moving-average/): equal weights.
- [Exponential Moving Average](../exponential-moving-average/): geometrically shrinking weights.
- [Hull Moving Average](../hull-moving-average/): built from weighted averages to cut lag.
