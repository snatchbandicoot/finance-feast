---
title: Percentage Price Oscillator
aliases: [PPO, Percentage Price Oscillator]
category: momentum
summary: MACD expressed as a percentage of the slow average, so readings are comparable across instruments and across time.
display: panel
inputs:
  - { name: fast length, default: 12 }
  - { name: slow length, default: 26 }
  - { name: signal length, default: 9 }
verdict: situational
status: draft
related: [macd, exponential-moving-average, awesome-oscillator]
---

> **In plain English.** MACD tells you how many *price units* the fast average is above the slow one. PPO tells you how many *percent*. "The fast average is 0.7 above the slow one" becomes "the fast average is 0.67% above the slow one". That makes a reading mean the same thing on a cheap stock and an expensive one, and in a year when the price was low and one when it was high.
>
> **Good for:** comparing momentum across instruments, or across a long history over which the price level changed a lot.
>
> **Watch out for:** expecting it to look different from MACD on one instrument over a short stretch. When the price level barely moves, the two are almost the same line.

## What it measures

The same thing as MACD, how far a fast exponential average is from a slow one, but measured relative to the slow average's own level.

## Calculation

$$ \text{PPO}_t = 100 \times \frac{\text{EMA}_{12}(P)_t - \text{EMA}_{26}(P)_t}{\text{EMA}_{26}(P)_t} $$

The signal line and the histogram work as in MACD: the signal is a 9-bar exponential average of the PPO, and the histogram is the PPO minus the signal.

**The link to MACD.** Dividing MACD by the slow average and multiplying by 100 gives the PPO exactly:

$$ \text{PPO} = 100 \times \frac{\text{MACD}}{\text{EMA}_{26}} $$

The check script confirms this over hundreds of bars.

**Worked example.** Using the MACD page's numbers, with the fast average at 105.2 and the slow average at 104.5, MACD is $105.2 - 104.5 = 0.7$ and $\text{PPO} = 100 \times 0.7/104.5 \approx 0.67\%$.

**Scale.** Multiply every price by 3 and MACD triples, but PPO does not change at all. The check script confirms both.

```python
def ppo(close, fast=12, slow=26, signal=9):
    slow_ema = close.ewm(span=slow, adjust=False).mean()
    line = 100 * (close.ewm(span=fast, adjust=False).mean() - slow_ema) / slow_ema
    sig = line.ewm(span=signal, adjust=False).mean()
    return line, sig, line - sig
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/percentage-price-oscillator-dark.svg">
<img src="../../charts/percentage-price-oscillator-light.svg" alt="Price above, and the PPO, its signal line and histogram below" width="840" height="590">
</picture>
<figcaption>Synthetic data. The first 40 values are hidden while the averages settle. Prices in this sample stay between about 89 and 124, so PPO (in percent) and MACD (in price units) are almost the same line, with a correlation of 0.998. The two differ when the price level changes a lot, which this sample does not show.</figcaption>
</figure>

Read it as you would MACD, with the same caveats (see the [MACD](../macd/) page):

- **Above or below zero:** the fast average is above or below the slow one.
- **Signal-line crossovers** are the common trigger, and are noisy in a sideways market.
- **The histogram** shows whether the PPO is moving away from, or back toward, its own signal line.
- **Divergence** appears often and fails often.

The difference is in the *units*. A PPO of 2 means "2% above" anywhere, which makes it possible to rank instruments, set one threshold for many charts, or compare today with the same instrument a decade ago.

## Best used when

- You **compare instruments** or screen many at once.
- You look at a **long history** in which the price level changed a lot, such as a stock that has doubled.
- You want **one threshold** that means the same thing on every chart.

## Avoid when

- You look at **one instrument over a short period**. You will not see a practical difference from MACD.
- You want the value in **price units**, for example to set a stop distance.

## Settings and tuning

The same as MACD: 12, 26 and 9 are the defaults, and shorter lengths make it faster and noisier. Tuning the three numbers to fit past data is a good way to fool yourself.

## Implementation variations

- **The denominator.** This page divides by the slow average, which is the usual convention. Check the denominator if your tool's values differ.
- **Related studies.** The *Percentage Volume Oscillator* applies the same arithmetic to volume instead of price. It is a different study.
- **EMA starting values** differ between tools, so early values will not match.

## Is it useful?

**Situational.** It is MACD with a more portable scale. On this site's sample, where prices stay between about 89 and 124, the two lines had a correlation of 0.998, and the only visible difference is the units. It earns its place when the price level changes a lot or when you compare instruments. Otherwise there is no practical reason to prefer it to MACD, and no reason to use both.

## Pairs well with / See also

- [MACD](../macd/): the same study in price units.
- [Exponential Moving Average](../exponential-moving-average/): the two averages inside it.
- [Awesome Oscillator](../awesome-oscillator/): a similar idea in price units, built from simple averages of the midpoint.
