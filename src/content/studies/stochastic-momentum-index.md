---
title: Stochastic Momentum Index
aliases: [SMI, Stochastic Momentum, SMI Ergodic]
category: momentum
summary: A smoother cousin of the Stochastic Oscillator that measures how far the close is from the middle of the recent range, rather than from its bottom, and runs from -100 to +100.
display: panel
inputs:
  - { name: range length, default: 10 }
  - { name: first smoothing, default: 3 }
  - { name: second smoothing, default: 3 }
  - { name: signal length, default: 10 }
verdict: situational
status: draft
related: [stochastic-oscillator, stochastic-rsi, williams-percent-r]
overlaps:
  - with: stochastic-oscillator
    strength: partial
    corr: 0.90
    note: "Both place the close inside a recent high-low range. The Stochastic measures from the bottom of the range and the SMI from its midpoint, then smooths more. The correlation is between the SMI and the Stochastic's %K."
---

> **In plain English.** The Stochastic Oscillator asks how close the close is to the bottom or top of the recent range. The Stochastic Momentum Index asks how far the close is from the *middle* of that range, then smooths the answer twice. The result is a calmer line that runs from -100 to +100 and crosses zero when price crosses the middle of its recent range.
>
> **Good for:** a less jumpy take on overbought and oversold than the ordinary Stochastic.
>
> **Watch out for:** its extra smoothing, which delays it. It also reaches the ±40 zones on 58% of bars in the sample, so the usual thresholds are not rare.

## What it measures

How far the close is from the midpoint of the highest high and lowest low of the last N bars, as a share of half that range. Zero means the close is at the midpoint. +100 means the close is at the top of the range, and -100 means it is at the bottom.

## Calculation

Over the last $N$ bars, let $HH$ be the highest high and $LL$ the lowest low. Then:

$$
\text{offset}_t = C_t - \frac{HH + LL}{2} \qquad \text{span}_t = HH - LL
$$

$$
\text{SMI}_t = 100 \times \frac{\text{EMA}(\text{EMA}(\text{offset}))}{\tfrac{1}{2}\,\text{EMA}(\text{EMA}(\text{span}))}
$$

Both are smoothed twice with exponential averages. A signal line is an EMA of the SMI.

**Worked example** (with no smoothing, to show the shape). Two bars have highs of 12 and 13 and lows of 10 and 11, and the last close is 12.5. Over those two bars, $HH = 13$ and $LL = 10$, so the midpoint is 11.5. The offset is $12.5 - 11.5 = 1.0$ and the span is $3$:

$$
100 \times \frac{1.0}{3 / 2} = 66.7
$$

The close is two thirds of the way from the midpoint to the top of the range.

```python
def smi(high, low, close, n=10, smooth1=3, smooth2=3, signal=10):
    highest, lowest = high.rolling(n).max(), low.rolling(n).min()
    offset = close - (highest + lowest) / 2
    span = highest - lowest

    def twice(x):
        return x.ewm(span=smooth1, adjust=False).mean().ewm(span=smooth2, adjust=False).mean()

    line = 100 * twice(offset) / (twice(span) / 2)
    return line, line.ewm(span=signal, adjust=False).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/stochastic-momentum-index-dark.svg">
<img src="../../charts/stochastic-momentum-index-light.svg" alt="Price above, and the Stochastic Momentum Index with its signal line below, with lines at -40, 0 and 40" width="840" height="590">
</picture>
<figcaption>Synthetic data. The SMI was above +40 on 30% of scored bars and below -40 on 28%. In the selloff it was below -40 on 62% of bars, and it reached -87.5 at the price low (bar 249).</figcaption>
</figure>

- **Zero line.** Above zero means the close is above the middle of its recent range.
- **±40.** Common overbought and oversold levels. Readings beyond +40 or -40 mean the close is well into one half of the range.
- **Signal crossovers.** The SMI crossing its signal line is the usual timing cue.
- **Bounded.** It cannot go beyond ±100.

What it does not tell you: how long a move will last. In the sample's selloff it was below -40 on 62% of bars, so "oversold" persisted.

## Best used when

- You like the **Stochastic** but find it too jumpy.
- The market is **ranging**, where midpoints matter.

## Avoid when

- The market is **trending hard**. Like all bounded oscillators, it stays at an extreme.
- You need **quick** reactions. Two layers of smoothing cost speed.

## Settings and tuning

- **10 / 3 / 3** with a **10-bar signal** is a common default set. Many tools use different signal lengths.
- **A shorter range** makes it more sensitive.
- **±40** versus **±50** for the zones varies by source.

## Implementation variations

- **Smoothing type.** Some versions use simple averages in place of exponential ones.
- **Signal.** The signal length differs: 3, 9 and 10 all appear in the wild.
- **Scale.** Some tools show ±100 and others ±1.
- **History.** It is usually credited to William Blau, from the 1990s. I have not confirmed the details.

## Is it useful?

**Situational.** It is a sound, smoother reworking of the Stochastic. On the sample data its correlation with the Stochastic's %K was 0.90, so mostly the same information. Its reading of the middle of the range is a mildly different angle, and it gives fewer false flickers. It is a reasonable swap for the Stochastic if you find that too twitchy. It is not a new kind of information, and you do not need both.

## Pairs well with / See also

- [Stochastic Oscillator](../stochastic-oscillator/): the original, which it smooths.
- [Stochastic RSI](../stochastic-rsi/): another variation, applied to RSI.
- [Williams %R](../williams-percent-r/): the same range idea measured from the top.
