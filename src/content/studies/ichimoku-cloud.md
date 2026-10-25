---
title: Ichimoku Cloud
aliases: [Ichimoku, Ichimoku Kinko Hyo, Kumo, Tenkan-sen, Kijun-sen]
category: trend
summary: Five lines built from range midpoints, including a shaded cloud drawn 26 bars ahead, that together give a picture of trend, momentum and likely support and resistance.
display: overlay
inputs:
  - { name: conversion length, default: 9 }
  - { name: base length, default: 26 }
  - { name: span B length, default: 52 }
  - { name: displacement, default: 26 }
verdict: situational
status: draft
related: [donchian-channels, simple-moving-average, average-directional-index, aroon]
---

> **In plain English.** Five lines that all come from one simple idea: the midpoint between the highest high and lowest low over some window. Two of them (Tenkan and Kijun) act like fast and slow moving averages. Two more are drawn 26 bars into the future, and the shaded area between them is called the cloud. The fifth is today's close drawn 26 bars back. The idea is to read trend, momentum and support and resistance from one chart.
>
> **Good for:** a single, all-in-one picture of the trend, with a clear rule for what counts as above, inside or below the cloud.
>
> **Watch out for:** complexity and lag. Five lines on one chart make it easy to find a signal anywhere, and almost every line is built from past prices. The cloud is not a forecast: it is drawn ahead but computed from the past.

## What it measures

The position of price relative to the midpoints of its recent ranges over three time scales (short, medium and long). Three of the lines (Tenkan, Kijun and Senkou B) are each the middle of a high-low range, which is the same quantity as the middle line of a [Donchian channel](../donchian-channels/). Senkou A averages the first two. The two cloud lines are then plotted 26 bars ahead, so that the zone price might meet in the future is on the chart today.

## Calculation

With the standard settings of 9, 26 and 52 bars:

$$ \text{Tenkan}_t = \frac{HH_9 + LL_9}{2} \qquad \text{Kijun}_t = \frac{HH_{26} + LL_{26}}{2} $$

$$ \text{Senkou A}_t = \frac{\text{Tenkan}_t + \text{Kijun}_t}{2} \qquad \text{Senkou B}_t = \frac{HH_{52} + LL_{52}}{2} $$

$HH_n$ and $LL_n$ are the highest high and lowest low over the last $n$ bars. Senkou A and B are then **plotted 26 bars ahead**, and the area between them is the cloud (*kumo*). A fifth line, the lagging span (*Chikou*), is simply today's close **plotted 26 bars back**.

**Worked example** with shortened settings (2, 3 and 4 bars, displacement 2) on six bars with highs of 10, 12, 11, 13, 12, 14 and lows of 8, 9, 9, 10, 10, 11. At bar 3:

- Tenkan is the midpoint of bars 2 to 3: highest high 13 and lowest low 9, so $(13 + 9)/2 = 11$.
- Kijun is the midpoint of bars 1 to 3: highest high 13 and lowest low 9, so 11.
- Senkou A is $(11 + 11)/2 = 11$, drawn at bar 5.
- Senkou B is the midpoint of bars 0 to 3: highest high 13 and lowest low 8, so $10.5$, also drawn at bar 5.

```python
def ichimoku(high, low, close, conversion=9, base=26, span_b=52, shift=26):
    def midpoint(n):
        return (high.rolling(n).max() + low.rolling(n).min()) / 2

    tenkan = midpoint(conversion)
    kijun = midpoint(base)
    senkou_a = (tenkan + kijun) / 2
    senkou_b = midpoint(span_b)
    # Each series is labelled with the bar it is drawn at: the cloud `shift` bars ahead, the lagging span behind.
    senkou_a.index = senkou_a.index + shift
    senkou_b.index = senkou_b.index + shift
    chikou = close.copy()
    chikou.index = chikou.index - shift
    return tenkan, kijun, senkou_a, senkou_b, chikou
```

Each series returned is labelled with the bar it is *drawn* at: the two cloud lines 26 bars ahead, and the lagging span 26 bars behind. This works for data indexed by bar number, as in this site's examples.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/ichimoku-cloud-dark.svg">
<img src="../../charts/ichimoku-cloud-light.svg" alt="Price with Ichimoku Tenkan, Kijun, and cloud, with the cloud extending past the last bar" width="840" height="480">
</picture>
<figcaption>Synthetic data. The cloud is drawn 26 bars ahead, so it runs past the last bar, to the right of the vertical line. The lagging span is not drawn, for clarity. Price closed below the cloud at bar 202, only 4% below its level when the selloff began, and stayed below it on 96% of the selloff's bars. It did not close back above until bar 309, sixty bars after the low. Tenkan crossed Kijun 11 times in the uptrend and 9 times in the range.</figcaption>
</figure>

- **Price against the cloud.** Above the cloud is read as an uptrend, below as a downtrend, and inside as no clear trend. This is the headline rule.
- **Cloud thickness** is read as the strength of the support or resistance it offers: a thick cloud is harder to pass through than a thin one. This is a convention and not something the math guarantees.
- **Cloud color or "twist".** When Senkou A is above Senkou B, the cloud is read as bullish, and when it crosses, the cloud twists. Some tools color the two cases differently.
- **Tenkan against Kijun.** Tenkan crossing above Kijun is the fast-over-slow crossover signal, as with two moving averages.
- **The lagging span (not drawn above, for clarity).** Today's close, plotted 26 bars back, is read against the price at that earlier point. If it is above price then, momentum is read as positive.

What it does not tell you: the future. The part of the cloud ahead of the last bar is computed entirely from past prices.

## Best used when

- Price is **trending**, on daily or weekly bars, where its slow lines can stay on one side of price.
- You want **one consistent set of rules** that combines several confirmations.
- You like **zones** in preference to single lines for support and resistance.

## Avoid when

- Price is **sideways**. Price sits inside or keeps crossing the cloud, and Tenkan and Kijun cross repeatedly. In the sample, they crossed 9 times in the 100-bar range.
- You **stack every signal** on one chart. With five lines, some will agree with whatever you hope for.
- You expect the **projected cloud** to predict. It does not.
- Your market has a **very different calendar**, so that the standard lengths mean something else.

## Settings and tuning

- **9, 26, 52 and 26** are the standard settings. They are often explained by the old Japanese trading week of six days (about one and a half weeks, one month and two months), a rationale I could not verify.
- Many traders use other lengths for markets that trade every day of the week. A longer set is common on slower charts.
- **Shorter lengths** make every line react faster, and the cloud thinner and less meaningful.

## Implementation variations

- **Displacement.** Most tools use 26 for both the cloud and the lagging span, though a few let you set them separately.
- **Drawing.** Some tools color the cloud by which span is on top, and some draw the lagging span.
- **Lengths.** Platforms differ in defaults, especially for markets that trade seven days a week.
- **History.** It is usually credited to Goichi Hosoda and was published in the late 1960s. I have not confirmed the details.

## Is it useful?

**Situational.** It is popular, and it does give a consistent, rule-based picture. But look at what is underneath: three of the lines are range midpoints (Donchian middle lines), the fourth averages two of them, and the cloud is two of these shifted forward. Most of its signals overlap with those of a moving-average crossover and a breakout rule. In the sample, the cloud flagged the selloff early: price closed below it at bar 202, with price only 4% down. But it did not give the all-clear until bar 309, sixty bars after the low. Treat it as a way to organise a trend view, not as a source of edge in itself.

## Pairs well with / See also

- [Donchian Channels](../donchian-channels/): three of the five Ichimoku lines are the middle of such a channel.
- [Simple Moving Average](../simple-moving-average/): Tenkan and Kijun act like a fast and a slow average.
- [Average Directional Index](../average-directional-index/): can tell you whether the market is trending enough for the cloud to matter.
- [Aroon](../aroon/): another trend reading, built from the timing of the extremes.
