---
title: Moving Average Ribbon
aliases: [EMA Ribbon, Rainbow Average, Multiple Moving Averages, GMMA]
category: trend
summary: Many moving averages of different lengths drawn together. When they fan out in order the trend is strong, and when they tangle the market has no trend. It is a picture, rather than a new calculation.
display: overlay
inputs:
  - { name: lengths, default: "10, 20, 30, 40, 50, 60, 70, 80" }
verdict: situational
status: draft
related: [exponential-moving-average, simple-moving-average, mcginley-dynamic]
overlaps:
  - with: exponential-moving-average
    strength: identical
    note: "Every line in the ribbon is an ordinary EMA. For example, the 20-bar line is exactly the 20-bar EMA."
---

> **In plain English.** One average is a line. Eight averages of different speeds make a ribbon. In a strong trend, the fast ones run ahead of the slow ones, and the ribbon fans out in a clean order. When the market stalls, the lines bunch together and cross over each other. The width and the ordering of the ribbon tell you about the trend's strength and age without any new math.
>
> **Good for:** seeing trend strength and trend change at a glance, with no signal rules to memorize.
>
> **Watch out for:** its lag. Every line is a moving average, so every line is late, and the ribbon can keep showing a trend long after it ended.

## What it measures

The agreement between averages of different speeds. If all are in order, the trend has been steady across all time scales. If they are crossed, the scales disagree.

## Calculation

Draw an EMA for each of several lengths (here, 10 to 80 in steps of 10). Two simple summaries are useful:

- **Width:** the fastest line minus the slowest, $\text{EMA}_{10} - \text{EMA}_{80}$. Positive and large means a strong uptrend, negative and large a strong downtrend.
- **Order:** whether the lines are in strict order, fastest above slowest (up) or fastest below slowest (down).

**Worked example.** If the 10-bar EMA is 105 and the 80-bar EMA is 100, the width is $105 - 100 = +5$.

```python
def ema_ribbon(close, lengths=(10, 20, 30, 40, 50, 60, 70, 80)):
    lines = {n: close.ewm(span=n, adjust=False).mean() for n in lengths}
    ribbon = pd.DataFrame(lines)
    width = ribbon[min(lengths)] - ribbon[max(lengths)]
    return ribbon, width
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/moving-average-ribbon-dark.svg">
<img src="../../charts/moving-average-ribbon-light.svg" alt="Price with a ribbon of eight EMAs from 10 to 80 bars, fast lines in pink and slow lines in teal" width="840" height="460">
</picture>
<figcaption>Synthetic data. The ribbon was fully in up-order on 90% of the uptrend's scored bars and 52% of the range's, and in down-order on 58% of the selloff's. Over the rebound it was in strict up-order on none of its bars.</figcaption>
</figure>

- **Fanning out in order** means a strong trend. The wider the fan, the stronger the trend has been.
- **Twisting or bunching** means the trend is ending or absent.
- **The fastest line crossing the slowest** is the usual trend-change cue, and by then the move is well under way.

What it does not tell you: how long the trend will go on, or when the fan will turn.

## Best used when

- You want a **visual** read on trend strength across time scales.
- You trade trends and like to see them mature.

## Avoid when

- You need **timely** signals. The slow lines move last.
- The chart gets too **busy** for you. Eight lines hide the price.

## Settings and tuning

- **Number and spacing** of the lines are free choices. Six to twelve lines is typical.
- **A two-group ribbon** (a few fast and a few slow, drawn in two colors) is a popular layout. The figure uses it.
- **EMAs or SMAs** are both used. EMAs are used here.

## Implementation variations

- **Different sets.** The best-known version, usually associated with Daryl Guppy, uses two groups of six averages with specific lengths. This page uses a plain evenly spaced set.
- **The average type.** Simple, exponential or weighted.
- **Coloring.** Many charts shade the lines from fast to slow to make the order easy to see.

## Is it useful?

**Situational.** It teaches the lag structure of averages better than most tools. On the sample, the ribbon was fully in up-order on 90% of the uptrend's scored bars. In the sideways range it was still in up-order on 52% of bars, since the slow lines were still catching up to a higher level. In the selloff, it was in down-order on 58% of bars, and in the rebound it was in strict up-order on none, and in down-order on 23%, though price had been rising for 70 bars. The average width was +5.3 in the uptrend, +3.4 in the range, -4.9 in the selloff and -5.6 in the rebound. It is a good way to see the trend's history. As a way to catch turns, it is slow.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the line it repeats.
- [Simple Moving Average](../simple-moving-average/): the other ribbon building block.
- [McGinley Dynamic](../mcginley-dynamic/): a single line that adapts instead.
