---
title: Elder Ray
aliases: [Bull and Bear Power, Bull Power, Bear Power, Elder-Ray Index]
category: momentum
summary: Splits each bar's reach into two measures, how far the high rose above a trend average (bull power) and how far the low fell below it (bear power), to show who is stronger, buyers or sellers.
display: panel
inputs:
  - { name: length, default: 13 }
verdict: situational
status: draft
related: [exponential-moving-average, commodity-channel-index, awesome-oscillator]
overlaps:
  - with: exponential-moving-average
    strength: near
    corr: 0.97
    note: "Both powers are measured from a 13-bar EMA. The average of bull and bear power is the distance from the EMA of the bar's middle. The correlation is with the close's distance from that EMA."
---

> **In plain English.** Draw a 13-bar exponential average as the "consensus value". Each bar, buyers push the high above it (bull power), and sellers push the low below it (bear power). If bull power is large, buyers are strong. If bear power is very negative, sellers are strong. The two bars of the pair together describe each bar's tug of war.
>
> **Good for:** looking at how far buyers and sellers each push away from the average, instead of just where the close ends up.
>
> **Watch out for:** mistaking it for something new. Both numbers are simply "high minus the EMA" and "low minus the EMA", so they are mostly a repackaged distance from the average.

## What it measures

The reach of each bar from a trend average. Bull power is the high's distance above it. Bear power is the low's distance from it (usually negative).

## Calculation

$$
\text{Bull Power}_t = H_t - \text{EMA}_N(C)_t \qquad \text{Bear Power}_t = L_t - \text{EMA}_N(C)_t
$$

with $N = 13$ by default.

**Worked example.** If the 13-bar EMA is 100, and the bar's high is 103 and low is 98:

- Bull power is $103 - 100 = 3$.
- Bear power is $98 - 100 = -2$.

The bar reached 3 above the average and 2 below it. Buyers had more reach this bar.

```python
def elder_ray(high, low, close, n=13):
    trend = close.ewm(span=n, adjust=False).mean()
    return high - trend, low - trend
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/elder-ray-dark.svg">
<img src="../../charts/elder-ray-light.svg" alt="Price with a 13-bar EMA above, and Bull Power and Bear Power as bars below, with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. Bull Power was above zero on 71% of scored bars and Bear Power on 38%. Bear Power reached its low of -12.15 on bar 243, in the selloff.</figcaption>
</figure>

- **The usual rule** pairs the powers with the trend: when the EMA is rising and bear power is negative but rising, that suggests buying. When the EMA is falling and bull power is positive but falling, that suggests selling. This page does not claim the rule is profitable.
- **Bull power above zero** is the normal state in an uptrend: the high sits above the average. In the sample it was above zero on 71% of scored bars.
- **Bear power above zero** means even the low was above the average. It happened on 38% of bars: 65% in the uptrend, 14% in the selloff.
- **Large negative bear power** shows selling pressure. The sample's worst was -12.15 on bar 243.

What it does not tell you: anything about volume, or why price reached where it did.

## Best used when

- You trade **with the trend** and want a way to time entries on pullbacks.
- You like seeing **both sides** of each bar separately.

## Avoid when

- You already use **distance from an EMA** in some form. The two powers average to exactly that.
- The market is **sideways**: both powers flip around zero.

## Settings and tuning

- **13** is the usual EMA length.
- **A longer EMA** gives a steadier reference, and bigger readings in trends.
- The scale is in price units, so values cannot be compared between instruments.

## Implementation variations

- **Average.** An EMA is standard, but some tools allow other averages.
- **Single or double window.** Some tools show the powers as two separate panels, and some on a single panel as bars.
- **History.** It is usually credited to Alexander Elder, who also uses the name "Elder-ray". I have not confirmed the details.

## Is it useful?

**Situational.** It is a clear way to see the push of each side of a bar. But the pair is a simple repackaging of an EMA, and the mean of the two powers correlated 0.97 with the close's distance from the same EMA. What it adds is the split between highs and lows, which tells you whether the bar's reach came from buyers or sellers. Whether that helps depends on your method. If you only want "is price above or below its average", the average alone says that.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the reference line for both powers.
- [Commodity Channel Index](../commodity-channel-index/): another distance-from-average oscillator.
- [Awesome Oscillator](../awesome-oscillator/): another difference between price and averages.
