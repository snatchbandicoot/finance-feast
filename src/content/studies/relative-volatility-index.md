---
title: Relative Volatility Index
aliases: [RVI, Dorsey's RVI]
category: volatility
summary: RSI's formula, but fed with the standard deviation of price on up-days and down-days instead of the size of the price change. It reads as a measure of whether volatility is mostly happening on up-days or down-days.
display: panel
inputs:
  - { name: standard deviation length, default: 10 }
  - { name: smoothing length, default: 14 }
verdict: skip
status: draft
related: [relative-strength-index, standard-deviation, historical-volatility]
overlaps:
  - with: relative-strength-index
    strength: partial
    corr: 0.83
    note: "Same construction as RSI, with a standard deviation in place of the price change. The correlation is between the two lines."
---

> **In plain English.** RSI asks whether the price changes were mostly up or mostly down. The Relative Volatility Index asks the same of the *volatility*: on days when price closed up, how large was the spread, compared with days when it closed down? A reading above 50 means more of the spread came on up-days. It is not a measure of how volatile the market is, despite its name.
>
> **Good for:** nothing that RSI does not already do, on the evidence here.
>
> **Watch out for:** its name. It does not measure volatility. It is a direction gauge. It correlated 0.83 with RSI on the sample.

## What it measures

The share of recent price spread that happened on up-days. Close to 100 means almost all of it did.

## Calculation

Each bar, take the 10-bar standard deviation of the closes ($\sigma_t$). If the close is above the previous close, assign $\sigma_t$ to the "up" series (and 0 to "down"). If it is lower, assign it to "down" instead. Smooth both with Wilder's average (an exponential average with $\alpha = 1/14$). Then:

$$
\text{RVI}_t = 100 \times \frac{\text{avg up}_t}{\text{avg up}_t + \text{avg down}_t}
$$

**Worked example.** If the smoothed up-day spread is 1.2 and the smoothed down-day spread is 0.8:

$$
100 \times \frac{1.2}{1.2 + 0.8} = 60
$$

```python
def relative_volatility(close, std_n=10, n=14):
    sd = close.rolling(std_n).std(ddof=0)
    change = close.diff()
    up = sd.where(change > 0, 0.0).where(sd.notna())
    down = sd.where(change < 0, 0.0).where(sd.notna())
    avg_up = up.ewm(alpha=1 / n, adjust=False).mean()
    avg_down = down.ewm(alpha=1 / n, adjust=False).mean()
    return 100 * avg_up / (avg_up + avg_down)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/relative-volatility-index-dark.svg">
<img src="../../charts/relative-volatility-index-light.svg" alt="Price above, and the Relative Volatility Index and RSI below with a line at 50" width="840" height="590">
</picture>
<figcaption>Synthetic data. The RVI (pink) was above 50 on 88% of the uptrend's scored bars, 50% of the range's, 54% of the selloff's and 60% of the rebound's. At the price low (bar 249) it read 34.2, and RSI (teal) read 17.4.</figcaption>
</figure>

- **Above 50** means more of the spread came on up-days. **Below 50**, on down-days.
- **The usual levels.** Above 50 is taken as a bullish confirmation, and below 50 as bearish. Some authors use 70 and 30 as extremes.
- **As a filter.** Some use it to confirm signals from another indicator.

What it does not tell you: how volatile the market is. For that, use ATR or historical volatility.

## Best used when

- You want a **second opinion** on direction that also reflects spread.

## Avoid when

- You want a **volatility** measure. This is not one.
- You already use **RSI**. They agree most of the time.

## Settings and tuning

- **10 and 14** are the usual values: a 10-bar standard deviation, and a 14-bar smoothing.
- **A shorter smoothing** makes it jumpier.

## Implementation variations

- **Input.** Some versions use the standard deviation of highs and lows, or the standard deviation of the change. This page uses the closes.
- **Smoothing.** Wilder's average is the usual one, and the first values depend on the start.
- **History.** It is usually credited to Donald Dorsey, from the 1990s. I have not confirmed the details.

## Is it useful?

**Skip.** The name promises a volatility indicator, and what it delivers is a direction gauge that copies RSI. On the sample it correlated 0.83 with RSI, and it was above 50 on 88% of the uptrend's bars and 54% of the selloff's, which are readings RSI also gave. It read 34.2 at the price low (bar 249), where RSI read 17.4, a weaker signal. If you need direction, use RSI. If you need volatility, use ATR or historical volatility.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): the same construction on price changes, and more informative.
- [Standard Deviation](../standard-deviation/): the input.
- [Historical Volatility](../historical-volatility/): the volatility measure the name suggests.
