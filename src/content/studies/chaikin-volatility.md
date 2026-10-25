---
title: Chaikin Volatility
aliases: [CV, Chaikin's Volatility]
category: volatility
summary: The percentage change in a smoothed measure of each day's high-to-low range, over 10 bars. It tells you whether ranges are widening or narrowing, not how wide they are.
display: panel
inputs:
  - { name: smoothing length, default: 10 }
  - { name: rate of change, default: 10 }
verdict: skip
status: draft
related: [average-true-range, historical-volatility, bollinger-bands]
overlaps:
  - with: average-true-range
    strength: partial
    corr: 0.90
    note: "Both smooth the bar's range. Chaikin Volatility is the percentage change of that smoothed range over 10 bars. The correlation is with the 10-bar percentage change in ATR."
---

> **In plain English.** Take each day's high-to-low range and smooth it. Then ask: is that smoothed range bigger or smaller than 10 bars ago, and by what percentage? A positive reading means ranges are expanding. A negative one means they are shrinking. It tells you the change in volatility, not its level.
>
> **Good for:** noticing that bars are getting wider or narrower.
>
> **Watch out for:** how noisy a change-of-a-change is. On the sample it swung from -53% to +97%, and its level had almost nothing in common with ATR's level (correlation 0.28).

## What it measures

The rate of change of the smoothed daily range. If the typical range 10 bars ago was 2.0 and is now 3.0, the reading is +50.

## Calculation

$$
\text{CV}_t = 100 \times \left(\frac{\text{EMA}_{10}(H-L)_t}{\text{EMA}_{10}(H-L)_{t-10}} - 1\right)
$$

**Worked example.** If the smoothed range was 2 ten bars ago and is 3 now:

$$
100 \times (3/2 - 1) = +50
$$

If it fell from 3 to 2, the reading would be $100 \times (2/3 - 1) = -33$. Ranges that double read +100, while ranges that halve read only -50, so the scale is lopsided.

```python
def chaikin_volatility(high, low, n=10, change=10):
    smoothed = (high - low).ewm(span=n, adjust=False).mean()
    return 100 * (smoothed / smoothed.shift(change) - 1)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/chaikin-volatility-dark.svg">
<img src="../../charts/chaikin-volatility-light.svg" alt="Price above, and Chaikin Volatility below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. Chaikin Volatility ranged from -53.3 to +97.1, with the peak on bar 202. Its average was +4.8 in the uptrend, +1.2 in the range, +13.5 in the selloff and -7.3 in the rebound.</figcaption>
</figure>

- **Above zero** means ranges are widening. **Below zero** means they are narrowing.
- **Sharp rises** often come with sharp price moves, in either direction. The sample's peak of +97% came on bar 202, as the selloff began.
- **Extended negative readings** mean the market is quieting down.

What it does not tell you: the level of volatility, or the direction of price.

## Best used when

- You want to see **volatility expanding or contracting**, as a rough "something is changing" flag.

## Avoid when

- You want to know **how volatile** a market is. Use ATR or historical volatility.
- You want a **smooth** line. The 10-bar comparison adds noise to the smoothed range.

## Settings and tuning

- **10 and 10** are the usual settings.
- **A longer rate-of-change span** compares with a more distant past.

## Implementation variations

- **Range.** The plain high-low range is usual. Some tools use the true range.
- **Smoothing.** An exponential average is typical. Others use simple averages.
- **History.** It is usually credited to Marc Chaikin. I have not confirmed the details.

## Is it useful?

**Skip.** The idea is sound, but you can get it more cleanly elsewhere. Its swings correlated 0.90 with a 10-bar percentage change in ATR on the sample, so it is a close cousin of that, and its mean values by stretch were +4.8 in the uptrend, +1.2 in the range, +13.5 in the selloff and -7.3 in the rebound, which fits what happened. But the reading is lopsided and jumpy, and "volatility is rising" is easier to see by looking at ATR or the Bollinger Band width directly. Use those.

## Pairs well with / See also

- [Average True Range](../average-true-range/): the level of the range, which this differentiates.
- [Historical Volatility](../historical-volatility/): another measure of how much price is moving.
- [Bollinger Bands](../bollinger-bands/): their width shows expansion and contraction directly.
