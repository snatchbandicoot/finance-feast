---
title: Detrended Price Oscillator
aliases: [DPO]
category: other
summary: Compares price from about half a cycle ago with today's moving average, which removes the trend so that the cycles are easier to see. It is a tool for measuring cycle length, not for generating timely signals.
display: panel
inputs:
  - { name: length, default: 20 }
verdict: skip
status: draft
related: [simple-moving-average, commodity-channel-index, awesome-oscillator]
---

> **In plain English.** A moving average follows price and hides the cycles in it. The Detrended Price Oscillator subtracts the average so that only the swings around the trend are left, and then it shifts price back in time to line up the swings with the average's midpoint. You use it to see how long the cycles are: peak to peak, trough to trough. You do not use it to see where price is going.
>
> **Good for:** measuring the rhythm of cycles in a market after the trend has been removed.
>
> **Watch out for:** its latest value. It compares today's average with a price from 11 bars ago, so it is not a statement about today's price. Do not use it as a timing signal.

## What it measures

The distance between a past price and the current moving average, with the trend taken out. It is a picture of the cycles in the past, not a reading of the present.

## Calculation

$$
\text{DPO}_t = P_{t - (N/2 + 1)} - \text{SMA}_N(P)_t
$$

Here $N$ is the length (20 by default). It subtracts today's $N$-bar average from the price $N/2 + 1$ bars ago (11 bars ago for $N = 20$).

**Why that shift?** A simple average of $N$ bars is centred on the price about $(N-1)/2$ bars ago. Looking at the price roughly $N/2 + 1$ bars back puts the price and the average on the same footing, so only the wiggles around the average are left.

**Worked example.** With $N = 4$, the shift is 3 bars. Take closes 10, 11, 12, 13, 14, 15. The 4-bar average at the last bar is $(12+13+14+15)/4 = 13.5$. The close 3 bars earlier is 12. So $\text{DPO} = 12 - 13.5 = -1.5$.

Two things follow, and the check script confirms both:

- **On a straight climb**, the DPO is a constant $-1.5$ times the slope, for any even length, so the trend is removed apart from a small constant.
- **On a perfect cycle** whose period equals the length, the average is flat at the midline, so the DPO is exactly the cycle, drawn 11 bars late.

```python
def dpo(close, n=20):
    return close.shift(n // 2 + 1) - close.rolling(n).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/detrended-price-oscillator-dark.svg">
<img src="../../charts/detrended-price-oscillator-light.svg" alt="Price with a 20-bar average above, and the Detrended Price Oscillator below, with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The DPO was above zero on 47% of scored bars. Its swings stayed within about ±5.3 points, and they show no regular cycle: the sample was not built to have one.</figcaption>
</figure>

- **Peaks and troughs.** Measure the distance between successive peaks (or troughs) to estimate the cycle length.
- **Above and below zero.** Above zero means the shifted price was above the average. It is not a trend or momentum reading.
- **Plot position.** Many tools plot each value at the bar of the price it uses (11 bars back), so that the line appears to lead. This page plots it at the bar where it can be computed. The shift is the whole point, so check which your tool does.

What it does not tell you: where price is now, or where it is going. The newest bars are not in the shifted half of the formula.

## Best used when

- You are **studying cycles** and want the trend out of the way.
- You are looking back at **history** to choose a cycle length for other tools.

## Avoid when

- You want a **signal today**. It has no present-tense information from price.
- The market has **no regular cycle**. The sample's DPO had a standard deviation of 1.5 to 2.6 points in every stretch, with no visible rhythm beyond noise.
- You compare across **instruments**. It is in price units.

## Settings and tuning

- **Length 20** is the usual default. Set it to the cycle you want to isolate.
- **An even length** gives the clean shift of $N/2 + 1$. Odd lengths round.

## Implementation variations

- **The shift.** Some tools use $N/2 + 1$, some $N/2$, and some a different centring.
- **The plotting position.** Some plot the value at the past bar (so it looks like a lead), others at the current bar.
- **The average.** An exponential average is sometimes used.
- **History.** I do not know who devised it, and have not confirmed the details.

## Is it useful?

**Skip,** for most people. It does one clear thing, which is to remove trend so that cycles show, and it does that exactly. But the cycles in real markets are irregular, and the indicator cannot be used as a signal because its newest value rests on an old price. On the sample, it had a correlation of -0.50 with today's distance from the same average, which tells you it is a different quantity from "where is price relative to its trend now". If you want that, use the distance from an average, or [CCI](../commodity-channel-index/). Keep the DPO for an analysis of cycles and nothing else.

## Pairs well with / See also

- [Simple Moving Average](../simple-moving-average/): the line it subtracts.
- [Commodity Channel Index](../commodity-channel-index/): a more usable read of the distance from an average.
- [Awesome Oscillator](../awesome-oscillator/): another difference between a price and an average.
