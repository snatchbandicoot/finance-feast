---
title: Coppock Curve
aliases: [Coppock, Coppock Indicator]
category: momentum
summary: A smoothed sum of two rates of change, designed to flag the turn up from deep lows in long-term charts. It is slow on purpose and meant to be read on weekly or monthly bars.
display: panel
inputs:
  - { name: long ROC, default: 14 }
  - { name: short ROC, default: 11 }
  - { name: WMA length, default: 10 }
verdict: situational
status: draft
related: [rate-of-change, know-sure-thing, macd]
overlaps:
  - with: rate-of-change
    strength: partial
    corr: 0.86
    note: "The Coppock Curve adds two rates of change and smooths them. The correlation is between the Coppock Curve and a 12-bar rate of change."
---

> **In plain English.** Add the percentage change over 14 bars to the percentage change over 11 bars, then smooth the sum with a weighted average. The result is a slow wave that dips deep below zero after big declines. The classic signal is simple: when the wave is below zero and *turns up*, a long-term low may be near.
>
> **Good for:** spotting recoveries from deep declines on long-term (weekly or monthly) charts.
>
> **Watch out for:** its design. It was made to find bottoms, not to produce regular signals, and it says nothing about tops.

## What it measures

Smoothed momentum over roughly one to two periods. A deep negative reading means the market has fallen a lot recently. A turn upward from there means the fall is slowing.

## Calculation

$$
\text{Coppock}_t = \text{WMA}_{10}\!\left(100 \times \left(\frac{P_t}{P_{t-14}} - 1\right) + 100 \times \left(\frac{P_t}{P_{t-11}} - 1\right)\right)
$$

WMA is a weighted moving average with the newest value weighted most (see [Weighted Moving Average](../weighted-moving-average/)).

**Worked example** (with a 3-bar WMA, to keep the arithmetic short). Say the 14-bar change is +10% and the 11-bar change is +6%. Their sum is 16. If the last three sums were 10, 12 and 16, the weighted average with weights 1, 2, 3 is:

$$
\frac{1 \times 10 + 2 \times 12 + 3 \times 16}{6} = 13.67
$$

If price grew a steady 1% a bar, the Coppock Curve would equal the sum of the 14-bar and 11-bar growth rates, since the average of a constant is that constant. The check script confirms this.

```python
def coppock(close, long_roc=14, short_roc=11, wma_n=10):
    total = 100 * (close / close.shift(long_roc) - 1) + 100 * (close / close.shift(short_roc) - 1)
    weights = np.arange(1, wma_n + 1)
    return total.rolling(wma_n).apply(lambda w: (w * weights).sum() / weights.sum(), raw=True)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/coppock-curve-dark.svg">
<img src="../../charts/coppock-curve-light.svg" alt="Price above, and the Coppock Curve below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The curve was above zero on 78% of the uptrend's scored bars, 55% of the range's, 6% of the selloff's and 80% of the rebound's. It bottomed at -35.1 on bar 246 and turned up on bar 247, two bars before the price low (bar 249). It crossed back above zero on bar 260.</figcaption>
</figure>

- **The classic signal.** The curve is below zero and turns up. It does not need to cross zero.
- **Zero line.** Above zero means the blended recent change is positive.
- **Depth.** A deeper dip means a bigger recent decline. It does not mean a bigger rebound is due.

What it does not tell you: whether the rebound will hold, or when to sell. The original design has no sell rule.

## Best used when

- You use **long-term** charts (weekly or monthly) and want a rough "the worst may be over" cue.
- You look at **broad indexes**, where deep declines are rare and meaningful.

## Avoid when

- You want **frequent** signals. It was made to be rare.
- You trade **short time frames**. The settings come from monthly charts and the line is slow.
- You want a **sell** signal.

## Settings and tuning

- **14, 11 and 10** are the traditional values, and they were meant to be periods (months), not bars on every chart.
- **Shorter versions** exist for daily charts, but they are not the original.

## Implementation variations

- **Time frame.** The original was for monthly data. Daily versions with the same numbers measure much shorter spans.
- **The average.** The weighted average is standard, but some tools use other smoothing.
- **History.** It is usually credited to Edwin Coppock, from an article in the 1960s. I have not confirmed the details.

## Is it useful?

**Situational.** The idea, that a slowing decline marks a low, is plain and easy to follow. On the sample data the curve bottomed at -35.1 on bar 246, turned up on bar 247, two bars before the price low on bar 249, and crossed above zero on bar 260. That is a decent result on a single example, and one example does not show the method works. The curve also correlated 0.86 with a 12-bar rate of change, so it is mostly a smoothed momentum line. Treat it as a slow, long-term bottom cue and nothing more.

## Pairs well with / See also

- [Rate of Change](../rate-of-change/): the building block.
- [Know Sure Thing](../know-sure-thing/): another blend of smoothed rates of change.
- [MACD](../macd/): a smoothed momentum line with a signal.
