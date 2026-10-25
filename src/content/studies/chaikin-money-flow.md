---
title: Chaikin Money Flow
aliases: [CMF]
category: volume
summary: A reading from minus 1 to plus 1 of whether volume has been concentrated in bars that close near their highs or near their lows.
display: panel
inputs:
  - { name: length, default: 20 }
verdict: situational
status: draft
related: [on-balance-volume, volume-weighted-average-price, relative-strength-index]
---

> **In plain English.** For each bar, look at where the close landed between the high and the low. A close near the high counts as buying and a close near the low as selling. That share is applied to the bar's volume. Add that up over the last 20 bars, divide by the total volume, and you get a number from −1 (all selling) to +1 (all buying), where 0 is balanced.
>
> **Good for:** a quick read on whether volume has been piling up on strong closes or on weak ones.
>
> **Watch out for:** it only sees where the bar *closed*. It cannot see what happened inside the bar, and it ignores gaps from the previous close.

## What it measures

Whether the volume of the last $N$ bars has gone with strong closes or weak ones. A bar that closes at its high is counted as fully "bought" and one that closes at its low as fully "sold", with everything in between scaled proportionally. This is an assumption about what the close location means, not an observation of who traded.

It is a bounded, windowed cousin of [On-Balance Volume](../on-balance-volume/). OBV adds the *whole* bar's volume to one side depending on whether the close was up or down from the previous close. CMF instead splits volume according to the close's position *within the bar*, and only over a window.

## Calculation

For each bar, the money flow multiplier runs from −1 to +1:

$$ M_t = \frac{(C_t - L_t) - (H_t - C_t)}{H_t - L_t} $$

Multiply by volume to get the bar's money flow volume, then sum over the window and divide by the window's total volume:

$$ \text{CMF}_t = \frac{\sum_{i=0}^{N-1} M_{t-i}\,V_{t-i}}{\sum_{i=0}^{N-1} V_{t-i}} $$

**Worked example.** One bar has a high of 12, a low of 10, a close of 11.5 and a volume of 100. Its multiplier is $((11.5 - 10) - (12 - 11.5))/2 = 0.5$. A second bar closes at 10.5 with a volume of 300, so its multiplier is $((10.5 - 10) - (12 - 10.5))/2 = -0.5$. Over these two bars, $\text{CMF} = (0.5 \times 100 + (-0.5) \times 300)/(100 + 300) = -100/400 = -0.25$.

```python
def cmf(high, low, close, volume, n=20):
    spread = (high - low).replace(0, np.nan)
    multiplier = (((close - low) - (high - close)) / spread).fillna(0)
    flow = multiplier * volume
    return flow.rolling(n).sum() / volume.rolling(n).sum()
```

A bar with no range (high equal to low) has no close location to speak of, so it counts as zero instead of dividing by zero.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/chaikin-money-flow-dark.svg">
<img src="../../charts/chaikin-money-flow-light.svg" alt="Price above, and 20-bar Chaikin Money Flow below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. CMF was above zero on 75% of uptrend bars and 34% of selloff bars. It reached its low of -0.38 at bar 244, five bars before the price low. The sample builds volume and bar shapes from the same price moves, so its agreement with price is likely stronger than real data would show.</figcaption>
</figure>

- **Above zero** means volume has favored closes in the upper part of the bars, which is read as buying pressure. **Below zero** is the opposite.
- **The size** says how lopsided it has been. In the sample it ran from −0.38 to +0.35, and any threshold you draw inside that range is a rough guide, not a rule.
- **Divergence.** Price rising while CMF falls is read as buying fading behind the advance. As with other divergences, it appears often and fails often.
- **Zero crossings** are a common but noisy signal.

What it does not tell you: who was buying or selling. It infers it from the close's position, which is a proxy.

## Best used when

- You want a **bounded, comparable** volume reading, which stays between −1 and +1 whatever the instrument's volume.
- You use **instruments with reliable volume** (listed stocks and futures).
- You want to **check a price move** against the volume behind it.

## Avoid when

- The instrument has **no real volume**, such as spot currencies, where tick counts stand in for it.
- **Gaps** matter. A gap up that closes mid-range counts as neutral, whatever the volume.
- **One bar has huge volume**, such as an index rebalance or expiry. It dominates the window.
- You expect it to **lead** price. In the sample it was low at bar 244, five bars before the price low, but that is one example.

## Settings and tuning

- **Length 20** is the common default. Some sources use 21.
- **Shorter:** more sensitive and noisier.
- **Longer:** smoother and slower.

## Implementation variations

- **Length.** 20 and 21 are both seen.
- **Zero-range bars.** Tools differ on how to treat them. Here they count as zero.
- **Accumulation/Distribution.** The same money flow volume, added up without a window, gives the running total known as the Accumulation/Distribution line. It is not the same study.
- **Chaikin Oscillator.** A different study, built from moving averages of the Accumulation/Distribution line. It is not CMF.

## Is it useful?

**Situational.** The idea is sound: closes near the high on heavy volume are more bullish than closes near the low. It is a finer tool than OBV, which gives all of a bar's volume to one side. But it is still a proxy, and it ignores gaps and what happened inside the bar. On the sample data it correlated 0.84 with the 20-bar change in OBV. That overstates the usual overlap, because the sample's volume and bar shapes were both generated from the same price moves, but expect a good deal of agreement on real data too. If you already use OBV, CMF adds a different way of splitting volume, not a new source of information.

## Pairs well with / See also

- [On-Balance Volume](../on-balance-volume/): the cumulative cousin, which splits volume by the direction of the close.
- [Volume Weighted Average Price](../volume-weighted-average-price/): another use of volume, as a price reference.
- [Relative Strength Index](../relative-strength-index/): momentum from price alone, to set against the volume reading.
