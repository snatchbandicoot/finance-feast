---
title: Historical Volatility
aliases: [HV, Realized Volatility, Statistical Volatility]
category: volatility
summary: How much the price has been moving, as the annualized standard deviation of daily percentage changes. It is the number that options traders compare with implied volatility.
display: panel
inputs:
  - { name: length, default: 20 }
  - { name: periods per year, default: 252 }
verdict: situational
status: draft
related: [average-true-range, standard-deviation, bollinger-bands]
overlaps:
  - with: average-true-range
    strength: partial
    corr: 0.87
    note: "Both measure how much price has been moving. Historical volatility uses closing changes in percent, ATR uses the bar's range in price units. The correlation is between the two lines."
  - with: standard-deviation
    strength: partial
    corr: 0.63
    note: "Historical volatility is a standard deviation of returns, and the Standard Deviation indicator is one of prices. The correlation is with the price standard deviation as a percentage of price."
---

> **In plain English.** Take the daily percentage changes over the last 20 days and ask how spread out they are. Scale the answer to a year, so it reads like "this market is moving at 18% a year". A bigger number means bigger swings. It says nothing about direction.
>
> **Good for:** comparing how wild different markets or different periods are, on one scale, and sizing positions.
>
> **Watch out for:** its lag. It describes the last 20 days, and it can stay high after the storm has passed. On the sample, it peaked on bar 255, six bars after the price low.

## What it measures

The typical size of daily percentage moves, over a window, scaled to a year. It is backward-looking, which is why it is called "historical" to distinguish it from the volatility an options market implies for the future.

## Calculation

Take the log return each bar, $r_t = \ln(P_t / P_{t-1})$. Over the last $N$ bars, take the sample standard deviation $s$ of those returns, then scale it:

$$
\text{HV}_t = 100 \times s \times \sqrt{252}
$$

The 252 is the number of trading days in a year. The scaling uses the square root because independent daily moves add up in squares.

**Worked example.** If daily returns have a standard deviation of 1%, then:

$$
100 \times 0.01 \times \sqrt{252} = 15.87
$$

so annualized volatility is about 15.9%. As a rule of thumb, divide the annual figure by about 16 to get the typical daily move.

The sample standard deviation divides by $N - 1$ (not $N$). Some tools use $N$.

```python
def historical_volatility(close, n=20, periods_per_year=252):
    returns = np.log(close / close.shift())
    return 100 * returns.rolling(n).std(ddof=1) * np.sqrt(periods_per_year)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/historical-volatility-dark.svg">
<img src="../../charts/historical-volatility-light.svg" alt="Price above, and annualized historical volatility below" width="840" height="590">
</picture>
<figcaption>Synthetic data. Average historical volatility was 15.2% in the uptrend, 15.5% in the range, 23.4% in the selloff and 17.6% in the rebound. It peaked at 28.2% on bar 255, six bars after the price low (bar 249).</figcaption>
</figure>

- **High versus low.** Compare today's value with its own history. There is no universal "high".
- **Rising volatility** often accompanies falling prices in stocks, but not always.
- **Across markets.** Because it is a percentage, you can compare a calm instrument with a wild one.

What it does not tell you: where price is going. Volatility is direction-free.

## Best used when

- You **size positions** so that each carries similar risk.
- You compare **different instruments** on a common scale.
- You want to compare realized movement with the **implied** volatility from options.

## Avoid when

- You want a **leading** signal. It lags.
- The data has **gaps or splits** that have not been adjusted: they create fake returns.
- You use too **short a window**. With 5 or 10 bars it is very noisy.

## Settings and tuning

- **20** bars (about one month) is common. Some use 10, 30 or 60.
- **252** is the usual number of periods per year. Use 365 for markets that trade every day, 52 for weekly bars, 12 for monthly.
- **A longer window** is steadier and slower.

## Implementation variations

- **Log or simple returns.** Close for small moves, and slightly different for large ones. This page uses log returns.
- **Divisor.** $N-1$ (sample) or $N$ (population).
- **Annualizing.** The number of periods varies by market and by data frequency.
- **Naming.** "Realized volatility" and "statistical volatility" mean the same thing.

## Is it useful?

**Situational.** For risk and position sizing, it is the standard measure, and it is easy to interpret. It averaged 15.2% in the sample's uptrend, 15.5% in the range, 23.4% in the selloff and 17.6% in the rebound, which matches what happened. It correlated 0.87 with ATR, so if you already use ATR you have most of the same information. The difference is that HV is in percent, which makes it comparable across instruments, and that is the reason to prefer it. It is not a trading signal.

## Pairs well with / See also

- [Average True Range](../average-true-range/): volatility in price units, from the bar's range.
- [Standard Deviation](../standard-deviation/): the spread of prices rather than of returns.
- [Bollinger Bands](../bollinger-bands/): bands whose width follows the standard deviation of price.
