---
title: Donchian Channels
aliases: [Donchian Channel, Price Channel, Highest-High Lowest-Low Channel]
category: trend
summary: The highest high and lowest low of the last N bars drawn as two lines, so that a close beyond either one is a breakout.
display: overlay
inputs:
  - { name: length, default: 20 }
verdict: situational
status: draft
related: [bollinger-bands, keltner-channels, aroon, average-true-range]
---

> **In plain English.** Two lines on the chart: the highest high of the last 20 bars and the lowest low, with a middle line halfway between. A close above the upper line is a 20-bar breakout, and a close below the lower line is a breakdown. It is the simplest breakout rule there is, and everything about it fits in one sentence.
>
> **Good for:** defining breakouts and stop levels in a way anyone can check by eye.
>
> **Watch out for:** false breakouts in sideways markets. On this site's sample data, 14 of the 22 closes above the prior 20-bar high were lower 10 bars later.

## What it measures

The recent trading range, as a pair of price levels and not as a width. It does not average anything, so it has no smoothing lag: the upper line jumps the instant a new high is made. The cost is that it is driven by single bars. One extreme bar sets the line, and it holds it there until the bar leaves the window.

## Calculation

$$
\text{Upper}_t = \max(H_{t-N+1}, \dots, H_t) \qquad \text{Lower}_t = \min(L_{t-N+1}, \dots, L_t) \qquad \text{Middle}_t = \frac{\text{Upper}_t + \text{Lower}_t}{2}
$$

**A breakout is a close beyond the *previous* bar's channel.** The current bar's own high is part of its own channel, so a close can never exceed the same bar's upper line: it can at most reach it. The check script confirms the channel always contains the current bar's high and low.

**Worked example.** If the highest high of the last $N$ bars is 14 and the lowest low is 8, the middle is $(14 + 8)/2 = 11$. If the next bar closes at 14.5, it is above yesterday's upper line of 14, which is a breakout.

```python
def donchian(high, low, n=20):
    upper = high.rolling(n).max()
    lower = low.rolling(n).min()
    return upper, (upper + lower) / 2, lower
```

In code, test a breakout with `close > upper.shift(1)`, so that it compares with yesterday's line.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/donchian-channels-dark.svg">
<img src="../../charts/donchian-channels-light.svg" alt="Price with a 20-bar Donchian channel across four regimes" width="840" height="440">
</picture>
<figcaption>Synthetic data. There were 22 closes above the prior 20-bar high (13 in the uptrend, 3 in the range, 1 in the selloff and 6 in the rebound), and 14 of them were lower 10 bars later. The channel was widest in the selloff, averaging 13.6% of price against 6.5% in the range. Closes below the prior 20-bar low happened 13 times in the selloff.</figcaption>
</figure>

- **Close above the prior upper line** is a breakout to the upside, and below the lower line a breakdown.
- **Channel width** shows how wide the recent range has been. A wide channel means volatile bars, and a narrow one means a tight range.
- **Middle line** is a rough center of the range. It is a crude trend reference, not a moving average.
- **Stair steps.** The lines move in steps, because they follow single bars. When an extreme bar leaves the window, the line can drop sharply.

What it does not tell you: whether a breakout will follow through. A breakout only says that price has left its recent range.

## Best used when

- You want a **rule you can state in one sentence** and check on any chart.
- Price is **trending**, so that breakouts tend to continue. Trend-following systems commonly use wide Donchian breakouts of this kind, and the "Turtle" traders are the best-known example.
- You need a **mechanical stop** level, such as the opposite channel line.

## Avoid when

- Price is **range-bound**. Breakouts fail, and each failure costs a loss. In the sample, 2 of the 3 range-bound breakouts were lower 10 bars later.
- You rely on a **single outlier bar**. It holds the line far from price, then removes it all at once 20 bars later.
- You compare **instruments** by width in price units. Use width as a percentage of price.

## Settings and tuning

- **Length 20** is a common default. Systems have used 20 for entries and 55 for slower ones.
- **Shorter:** more breakouts, more false ones.
- **Longer:** fewer, bigger breakouts, and later exits.
- Some systems use different lengths for entry and for exit.

## Implementation variations

- **Includes the current bar or not.** This page's channel includes the current bar. Some tools plot a channel that stops at the previous bar, which is equivalent to shifting the line by one. Check which one your tool uses before testing breakouts.
- **Highs and lows, or closes.** Some versions use the highest and lowest *close*, which is less sensitive to single spikes.
- **Middle line.** Not every tool draws it.

## Is it useful?

**Situational.** It is the most transparent breakout definition there is, and it is a sensible basis for a mechanical trend-following rule. It does not predict, and in sideways markets it generates false breakouts. On the sample data most upside breakouts were lower 10 bars later, though the sample is small (22) and synthetic, so treat that as an illustration. It overlaps with [Aroon](../aroon/), where Aroon Up at 100 is exactly a new high, and with Keltner and Bollinger as a way to draw an envelope, though a different one: those measure volatility and this measures the range.

## Pairs well with / See also

- [Aroon](../aroon/): "Aroon Up equals 100" and "a new channel high" are the same event.
- [Keltner Channels](../keltner-channels/) and [Bollinger Bands](../bollinger-bands/): envelopes built from volatility and not from the extremes.
- [Average True Range](../average-true-range/): a way to size a stop at the opposite line.
