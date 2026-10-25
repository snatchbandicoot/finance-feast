---
title: Momentum
aliases: [Momentum Indicator, Price Momentum, MOM, Percent Change]
category: momentum
summary: Today's price minus the price N bars ago, in price points. It is the plainest measure of how far and how fast price has moved, and the raw material of Rate of Change.
display: panel
inputs:
  - { name: length, default: 10 }
verdict: redundant
status: draft
related: [rate-of-change, macd, relative-strength-index]
overlaps:
  - with: rate-of-change
    strength: near
    corr: 1.0
    note: "Momentum is the price change in points, and Rate of Change is the same change as a percentage of the old price. The correlation on the sample is 0.997."
---

> **In plain English.** Subtract the price from 10 bars ago from today's price. That is momentum. A positive number says price is higher than it was; a negative number says lower. The bigger the number, the bigger the move. There is nothing hidden in it, and that is both its strength and its limit.
>
> **Good for:** the cleanest possible look at recent change, with no smoothing and no lag beyond the lookback itself.
>
> **Watch out for:** its units. It is in price points, so a 5-point move means different things on a 20 dollar stock and a 500 dollar one. For comparisons across instruments, use Rate of Change.

## What it measures

The change in price over the last $N$ bars. It looks at only two prices, today's and the one $N$ bars ago, and ignores everything between them.

## Calculation

$$
\text{MOM}_t = P_t - P_{t-N}
$$

**Worked example.** With $N = 2$ and closes of 100, 105 and 112, the last reading is $112 - 100 = +12$.

**An exact relationship.** Momentum equals the old price times the Rate of Change divided by 100. So it carries the same information as [Rate of Change](../rate-of-change/), scaled by the old price. The check script confirms this.

```python
def momentum(close, n=10):
    return close - close.shift(n)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/momentum-dark.svg">
<img src="../../charts/momentum-light.svg" alt="Price above, and 10-bar Momentum below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. Momentum ranged from -20.3 (bar 244) to +9.9 over the scored bars. It was above zero on 75% of the uptrend's scored bars, 50% of the range's, 24% of the selloff's and 73% of the rebound's, and crossed zero 16 times in the range.</figcaption>
</figure>

- **Above zero**: price is higher than $N$ bars ago. **Below zero**: lower. The zero line is the whole signal.
- **Rising** means the gap over the last $N$ bars is widening.
- **Because it drops one price off the back each bar**, a big old move leaving the window makes the line fall sharply even if price did nothing today. This is a known quirk of any fixed-lookback change.

What it does not tell you: what happened in between. A spike nine bars ago leaving the window moves the line as much as a spike today entering it.

## Best used when

- You want a **bare-bones** momentum reading on one instrument.
- You use it as a **building block** for something else.

## Avoid when

- You compare **different instruments**. Use Rate of Change.
- You want a **smooth** line. Use MACD or TRIX.

## Settings and tuning

- **10** is the usual default. Shorter is jumpier. Longer shows the bigger swing.
- **Zero** is the only fixed reference level.

## Implementation variations

- **Difference or ratio.** Some tools call a ratio ("price divided by price N bars ago", centred on 100) momentum. This page uses the difference.
- **Percent.** A percentage version is Rate of Change.
- **Smoothing.** Some tools add a moving average of momentum as a signal line.

## Is it useful?

**Redundant.** It is honest and simple, but it adds nothing to Rate of Change, which is the same measurement without the unit problem. On the sample the two correlated 0.997. Momentum was above zero on 75% of the uptrend's scored bars, 50% of the range's, 24% of the selloff's and 73% of the rebound's, and crossed zero 16 times in the range alone. Its low of -20.3 came on bar 244, five bars before the price low. Use it to understand the idea, then use Rate of Change.

## Pairs well with / See also

- [Rate of Change](../rate-of-change/): the same measurement as a percentage.
- [MACD](../macd/): a smoothed momentum line.
- [Relative Strength Index](../relative-strength-index/): a bounded read of the same ingredients.
