---
title: Moving Average Envelope
aliases: [MA Envelope, Percentage Envelope, Envelope]
category: volatility
summary: A moving average with two lines a fixed percentage above and below it, forming a channel of constant relative width.
display: overlay
inputs:
  - { name: length, default: 20 }
  - { name: percent, default: 2.5 }
verdict: situational
status: draft
related: [bollinger-bands, keltner-channels, simple-moving-average]
overlaps:
  - with: bollinger-bands
    strength: partial
    corr: 0.82
    note: "Both draw a channel around a 20-bar average. The envelope's width is a fixed percentage and Bollinger's follows volatility. The correlation is between where price sits inside each channel."
---

> **In plain English.** A moving average with a channel drawn a fixed percentage above and below it, such as 2.5% each way. It is the simplest envelope there is. Unlike Bollinger Bands or Keltner Channels, its width never changes: in a wild market and a quiet one it is exactly the same size. That makes it easy to understand and blind to volatility.
>
> **Good for:** a simple, fixed yardstick of "how far from the average is price, in percent".
>
> **Watch out for:** its fixed width. In a volatile stretch price spends most of its time outside the channel, and in a calm one it rarely gets near the edges.

## What it measures

How far price is from its moving average, as a fixed percentage. It does not measure volatility, because the channel does not respond to it.

## Calculation

$$
\text{Upper}_t = \text{SMA}_N(P)_t \times \left(1 + \tfrac{p}{100}\right) \qquad \text{Lower}_t = \text{SMA}_N(P)_t \times \left(1 - \tfrac{p}{100}\right)
$$

**Worked example.** If the 20-bar average is 100 and $p = 2.5$, the upper line is $100 \times 1.025 = 102.5$ and the lower line is $100 \times 0.975 = 97.5$. The channel is 5% wide, and remains 5% wide whatever happens.

```python
def envelope(close, n=20, percent=2.5):
    middle = close.rolling(n).mean()
    return middle, middle * (1 + percent / 100), middle * (1 - percent / 100)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/moving-average-envelope-dark.svg">
<img src="../../charts/moving-average-envelope-light.svg" alt="Price with a 2.5 percent moving average envelope and Bollinger Bands drawn together" width="840" height="440">
</picture>
<figcaption>Synthetic data. The envelope (pink) is exactly 5.0% of price wide throughout, while Bollinger's width (teal) averaged 5.8% in the range and 12.9% in the selloff. Price closed outside the envelope on 14% of the range's bars and 50% of the selloff's.</figcaption>
</figure>

- **Close above the upper line or below the lower line** means price is more than the chosen percentage from its average.
- **The width does not carry information.** It is constant, so the only thing to read is where price sits inside it.
- **Against a volatility channel.** Put it beside Bollinger Bands (as above) to see how a channel that follows volatility behaves differently.

What it does not tell you: whether being outside the channel is unusual. That depends on the market's current volatility, which the envelope ignores.

## Best used when

- You think in **fixed percentages**, for example "I want to see when price is more than 3% from its average".
- You want a **very simple** channel that is easy to explain.

## Avoid when

- Volatility **changes a lot**. A fixed percentage is too narrow in a volatile market and too wide in a calm one.
- You compare **different instruments**. A 2.5% move is large for some and trivial for others.

## Settings and tuning

- **Length 20** and **2.5%** are common defaults, but there is no standard.
- **The percentage** is the main choice, and it should suit the instrument: a quiet instrument needs a smaller percentage.
- **The average type** can be changed in many tools. A simple average is used here.

## Implementation variations

- **Average.** Many tools allow an exponential or weighted average for the middle line.
- **Percent or points.** A few tools offer a fixed number of points instead of a percentage, which is a different envelope.
- **Names.** "Envelope" and "percentage envelope" mean the same thing.

## Is it useful?

**Situational.** It does one thing and does it plainly. But a channel that cannot respond to volatility is a blunt tool. On the sample data, the envelope stayed exactly 5% wide in every stretch, while the Bollinger Bands widened from 5.8% of price in the range to 12.9% in the selloff. Price closed outside the envelope on 14% of the range's bars but 50% of the selloff's. Where volatility varies, a channel that adapts, such as [Bollinger Bands](../bollinger-bands/) or [Keltner Channels](../keltner-channels/), says more. The envelope earns its place when the fixed percentage is *the point*.

## Pairs well with / See also

- [Bollinger Bands](../bollinger-bands/): the same idea, with a width that follows volatility.
- [Keltner Channels](../keltner-channels/): a channel whose width follows the average true range.
- [Simple Moving Average](../simple-moving-average/): the middle line.
