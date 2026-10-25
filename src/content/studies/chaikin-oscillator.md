---
title: Chaikin Oscillator
aliases: [Chaikin A/D Oscillator, CO]
category: volume
summary: The difference between a fast and a slow average of the Accumulation/Distribution line. It shows whether buying and selling pressure is picking up or fading, and it is exactly a MACD run on the A/D line.
display: panel
inputs:
  - { name: fast, default: 3 }
  - { name: slow, default: 10 }
verdict: situational
status: draft
related: [accumulation-distribution, macd, chaikin-money-flow]
overlaps:
  - with: macd
    strength: identical
    note: "The Chaikin Oscillator is the MACD line (fast EMA minus slow EMA) computed on the Accumulation/Distribution line, with lengths 3 and 10."
  - with: chaikin-money-flow
    strength: partial
    corr: 0.71
    note: "Both come from the Accumulation/Distribution line, one as a momentum of it and one as a windowed share of it. The correlation is between the two lines."
---

> **In plain English.** The Accumulation/Distribution line goes up when volume lands on strong closes. The Chaikin Oscillator asks whether that line is currently speeding up or slowing down, by subtracting a slow average of it from a fast one. Above zero, the line is rising faster than its recent trend. Below zero, it is falling or losing steam.
>
> **Good for:** seeing shifts in buying and selling pressure a little earlier than the A/D line itself.
>
> **Watch out for:** how often it crosses zero. On the sample it crossed 27 times, so most crossings are noise.

## What it measures

The momentum of the Accumulation/Distribution line. It is not a measure of volume, and not of price.

## Calculation

$$
\text{CO}_t = \text{EMA}_3(\text{ADL})_t - \text{EMA}_{10}(\text{ADL})_t
$$

See [Accumulation/Distribution](../accumulation-distribution/) for the line.

**Worked example.** If the 3-bar average of the A/D line is 520 and the 10-bar average is 480, the oscillator reads $520 - 480 = +40$. The fast average is above the slow one, so the line has been climbing recently.

**An exact identity.** The formula is the same as the MACD line applied to the A/D line, with lengths 3 and 10. The check script confirms that the two agree to the last digit.

```python
def chaikin_oscillator(high, low, close, volume, fast=3, slow=10):
    line = accumulation_distribution(high, low, close, volume)
    return line.ewm(span=fast, adjust=False).mean() - line.ewm(span=slow, adjust=False).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/chaikin-oscillator-dark.svg">
<img src="../../charts/chaikin-oscillator-light.svg" alt="Price above, and the Chaikin Oscillator below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The oscillator ranged from -2.12 million (bar 244) to +2.01 million (bar 266) after the first 60 bars, and crossed zero 27 times. It was above zero on 68% of the uptrend's scored bars, 50% of the range's, 30% of the selloff's and 50% of the rebound's.</figcaption>
</figure>

- **Above zero**: buying pressure is rising. **Below zero**: it is fading.
- **Zero crossings** are the usual signals. They are frequent.
- **Divergence** from price is the usual caution.

What it does not tell you: how much volume is behind the move. Its scale depends on the volume of the instrument and cannot be compared across instruments.

## Best used when

- You already use the **A/D line** and want its momentum.
- You study **divergences** in volume-based pressure.

## Avoid when

- You want few, reliable signals. It crosses zero often.
- You compare **across instruments**. The units are shares.

## Settings and tuning

- **3 and 10** are the usual values.
- **Longer averages** give fewer crossings and later signals.

## Implementation variations

- **A/D start.** The oscillator depends on the A/D line's start only through the first few bars, so the chart hides the first 30.
- **Averages.** Exponential, as here. Some tools allow other types.
- **History.** It is usually credited to Marc Chaikin. I have not confirmed the details.

## Is it useful?

**Situational.** It adds a momentum read to a volume line, and because it is an exact MACD of the A/D line, you already know how it behaves. On the sample it was above zero on 68% of the uptrend's scored bars, 50% of the range's, 30% of the selloff's and 50% of the rebound's, which matches the story. It crossed zero 14 times in the range alone. Its swings correlated 0.71 with CMF, so the two are related but not the same. Treat it as a way to see the A/D line's turns sooner, and expect false ones.

## Pairs well with / See also

- [Accumulation/Distribution Line](../accumulation-distribution/): the line it differentiates.
- [MACD](../macd/): the same formula applied to price.
- [Chaikin Money Flow](../chaikin-money-flow/): another read of the same line.
