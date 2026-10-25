---
title: TRIX
aliases: [TRIX, Triple Exponential Average, TRIX Oscillator]
category: momentum
summary: The one-bar percentage change of a triple-smoothed exponential average, which makes a very smooth momentum line.
display: panel
inputs:
  - { name: length, default: 15 }
verdict: situational
status: draft
related: [exponential-moving-average, macd, rate-of-change]
---

> **In plain English.** Smooth price with an exponential average, smooth that, and smooth it a third time. Then measure how fast the triple-smoothed line rose or fell in the last bar, as a percentage. The repeated smoothing filters out almost all short-term noise, so TRIX is a very smooth momentum line that crosses zero only rarely. The price of that smoothness is lag.
>
> **Good for:** a smooth read on the direction of momentum that ignores small wiggles.
>
> **Watch out for:** lateness. In this site's sample, TRIX reached its low three bars *after* the price did.

## What it measures

The speed of a heavily smoothed price. Three layers of exponential averaging remove cycles shorter than roughly the averaging length, so what is left is the underlying drift. TRIX is then the rate at which that drift is moving: positive when the smoothed line is rising, negative when it is falling.

## Calculation

Let $\text{EMA}^{3}$ be an exponential average applied three times in a row, each of length $N$ (see the [Exponential Moving Average](../exponential-moving-average/) page):

$$ \text{EMA}^{3}_t = \text{EMA}_N\!\left(\text{EMA}_N\!\left(\text{EMA}_N(P)\right)\right)_t \qquad \text{TRIX}_t = 100 \times \left( \frac{\text{EMA}^{3}_t}{\text{EMA}^{3}_{t-1}} - 1 \right) $$

**A sanity check.** If price rises by exactly 1% every bar, the triple-smoothed line also rises 1% per bar once it has settled, so TRIX reads 1.0. The check script confirms this. It also confirms that multiplying every price by 3 leaves TRIX unchanged, since it is a percentage.

```python
def trix(close, n=15):
    triple = close.ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean()
    return 100 * (triple / triple.shift(1) - 1)
```

Triple smoothing takes a long time to settle. The first three or four times the length (around 60 bars here) are unreliable and are hidden in the chart.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/trix-dark.svg">
<img src="../../charts/trix-light.svg" alt="Price above, and the TRIX line below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The first 60 values are hidden while the three averages settle. TRIX was positive on every uptrend bar shown and negative on every selloff bar, and it crossed zero 0 times in the uptrend, 3 times in the 100-bar range and 0 times in the selloff. Its low came at bar 252, three bars after the price low.</figcaption>
</figure>

- **Above or below zero.** Positive means the smoothed price is rising, and negative means it is falling. It is the main reading.
- **Zero-line crossings** are rare, which is the point, and they come late.
- **Signal line.** Many traders add a short average of TRIX (commonly 9 bars) and trade its crossovers. That is an addition that is not part of TRIX itself.
- **Divergence.** As with other oscillators, price making a new extreme while TRIX does not is often read as a warning. It appears often and fails often.

What it does not tell you: where price will turn. It is built to react slowly.

## Best used when

- You want to see the **underlying direction** of price with the noise removed.
- You want fewer **false zero-line crossings** than MACD or ROC give.
- You are looking at a **longer horizon**, where the delay matters less.

## Avoid when

- You need an **early** signal. Three layers of smoothing make it one of the laggier momentum studies.
- Price is moving **quickly and briefly**. The move can be over before TRIX registers it.
- You compare the **size** of readings between instruments without remembering it is a percentage per bar, which is small by nature.

## Settings and tuning

- **Length 15** is a common default. 14 is also seen, and some people use 9 or 12.
- **Shorter:** less smoothing, faster, and more crossings.
- **Longer:** very smooth and very slow.

## Implementation variations

- **Seeding.** Each of the three averages needs a starting value, and early values depend on it.
- **Log or percent.** Some tools compute the change of the *logarithm* of the triple average. The values are almost the same for small changes.
- **Signal line.** Many platforms draw one by default.
- **History.** It is usually credited to Jack Hutson. I have not confirmed the details.

## Is it useful?

**Situational.** It does one thing well: it gives a quiet, smooth momentum line. Over the same bars of the sample, TRIX crossed zero 4 times in total, the MACD line 8 times and 12-bar ROC 36 times. But it pays for that with lag, and it overlaps with MACD in purpose: both are trend-momentum readings derived from exponential averages. It suits a reader who wants to filter noise and accepts a late signal. It does not suit anyone who wants early warnings.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the building block, applied three times.
- [MACD](../macd/): also built from exponential averages. It is faster and noisier.
- [Rate of Change](../rate-of-change/): the unsmoothed version of the same idea, applied to price.
