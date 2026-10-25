---
title: Hull Moving Average
aliases: [HMA, Hull MA]
category: trend
summary: A fast, smooth moving average built from weighted averages so that its lag nearly disappears.
display: overlay
inputs:
  - { name: length, default: 21 }
verdict: situational
status: draft
related: [weighted-moving-average, double-exponential-moving-average, triple-exponential-moving-average]
---

> **In plain English.** A moving average designed to be both fast and smooth. It takes a weighted average over half the length and another over the full length, doubles the fast one and subtracts the slow one (which pushes the result forward), and then smooths that with a short weighted average. On a steady climb it trails price by less than a bar. Its price is the largest overshoot of the averages here.
>
> **Good for:** a very responsive trend line that is still smoother than a short average.
>
> **Watch out for:** overshoot and chop. In this site's sample it crossed price 24 times in the 100-bar range, more than any of the others.

## What it measures

A smoothed price with almost no lag. For $N = 21$, the line trails a steady climb by only 0.67 bars, where a simple average of the same length trails by 10.

## Calculation

With $\text{WMA}_n$ the weighted average of length $n$ (see the [Weighted Moving Average](../weighted-moving-average/) page):

$$
\text{HMA}_t = \text{WMA}_{\sqrt{N}}\!\left(2\,\text{WMA}_{N/2}(P) - \text{WMA}_{N}(P)\right)_t
$$

The half length is rounded down and the square root is rounded to the nearest whole number. For $N = 21$, that is 10 and 5.

**Step by step.** First, $2\,\text{WMA}_{N/2} - \text{WMA}_N$: the fast average, doubled, minus the slow one. This pushes the line forward and removes most of the lag, but it also makes it jumpy. Second, a short weighted average of that smooths the jumpiness.

**Worked example.** If the half-length WMA is 104 and the full-length WMA is 100, the first step gives $2 \times 104 - 100 = 108$, before the short smoothing.

**Overshoot.** After a jump from 100 to 110, the HMA peaks at 112.7, an overshoot of 2.7 points. The check script confirms this, and the lag.

```python
def hma(close, n=21):
    half = n // 2
    root = round(n ** 0.5)
    return wma(2 * wma(close, half) - wma(close, n), root)
```

This function uses `wma()` from the [Weighted Moving Average](../weighted-moving-average/) page.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/hull-moving-average-dark.svg">
<img src="../../charts/hull-moving-average-light.svg" alt="Price with a 21-bar Hull moving average and a 21-bar weighted moving average through a selloff and rebound" width="840" height="430">
</picture>
<figcaption>Synthetic data, zoomed to the end of the range, the selloff and the rebound. The HMA (pink) bottomed at bar 250 at 85.3, which is 3.5 below the price low of 88.8, where the WMA (teal) bottomed at 91.1 at bar 258. In the 100-bar range the HMA crossed price 24 times, against 14 for the WMA.</figcaption>
</figure>

Read it as any moving average. Because it is fast, a change in its slope is often used as a signal in its own right, and in practice many traders watch it turn up or down. That makes it a rapid but noisy signal.

What it does not tell you: whether a turn will last. In the sample it also dipped to 85.3 after the selloff, 3.5 below the actual low.

## Best used when

- You want a **fast but smooth** line to follow a trend.
- Price is **trending**, so that the early turns help more than they mislead.

## Avoid when

- Price is **sideways**. It crossed price 24 times in the sample's range, against 14 for a plain weighted average of similar length.
- You need **reliable price levels**. It overshoots at turns.
- You use it **mechanically** on every slope change. That is a way to collect many small losses.

## Settings and tuning

- **Length 21** is a common default. Other lengths are used for different speeds.
- **Shorter:** very fast and jumpy. **Longer:** smoother, and still faster than a simple average of the same length.

## Implementation variations

- **Rounding.** Tools round the half length and the square root differently, which shifts values slightly.
- **Weights.** It depends on linearly weighted averages. A version built from other averages is a different study.
- **History.** It is usually credited to Alan Hull, in the 2000s. I have not confirmed the details.

## Is it useful?

**Situational.** It delivers on its aim: a smooth line that sits close to price. But the lag is not removed for free, since the overshoot is the largest of the family, and in a sideways market it chops the most. As a visual aid to see the direction of a trend, it is good. As a source of trades on its own, it is no better than the simpler averages, and arguably worse in ranges.

## Pairs well with / See also

- [Weighted Moving Average](../weighted-moving-average/): the ingredient.
- [Double Exponential Moving Average](../double-exponential-moving-average/) and [Triple Exponential Moving Average](../triple-exponential-moving-average/): other ways to cut lag.
- [Exponential Moving Average](../exponential-moving-average/): the plain, slower alternative.
