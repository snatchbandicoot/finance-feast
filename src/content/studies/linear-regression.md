---
title: Linear Regression
aliases: [Linear Regression Line, Linear Regression Slope, Least Squares Moving Average, LSMA, Time Series Forecast, End Point Moving Average]
category: trend
summary: The straight line that best fits the last N prices, read at its latest point, together with the line's slope.
display: overlay
inputs:
  - { name: length, default: 20 }
verdict: situational
status: draft
related: [simple-moving-average, hull-moving-average, average-directional-index]
---

> **In plain English.** Take the last 20 closing prices, draw the straight line that fits them best (the one with the smallest total squared error), and read the value of that line at the latest bar. That is the regression value. The slope of the line says how fast price has been rising or falling per bar. On a perfectly straight climb, the regression value sits exactly on price, with no lag at all. The cost is overshoot at turns.
>
> **Good for:** a lag-free read on a steady trend, and a clean number for its direction and steepness (the slope).
>
> **Watch out for:** overshoot, and the temptation to extend the line forward as a forecast. It is a fit to the past, not a prediction.

## What it measures

Where the best-fitting straight line through recent prices ends up, and how steep it is. A simple average reports the *middle* of the window, which is behind price in a trend. The regression value reports the *end* of the fitted line, which is why it keeps up.

## Calculation

For the last $N$ bars, number them $x = 0, 1, \dots, N-1$ and let $\bar{x}$ and $\bar{y}$ be the averages of the bar numbers and the prices. The least-squares slope and the fitted value at the last bar are:

$$
b = \frac{\sum (x - \bar{x})(y - \bar{y})}{\sum (x - \bar{x})^2} \qquad \text{value} = \bar{y} + b\,(N - 1 - \bar{x})
$$

**Worked example.** Closes of 10, 11, 13, 14 over four bars: $\bar{x} = 1.5$ and $\bar{y} = 12$. The deviations of $x$ are $-1.5, -0.5, 0.5, 1.5$ and of $y$ are $-2, -1, 1, 2$, so the top of the slope is $3 + 0.5 + 0.5 + 3 = 7$ and the bottom is $2.25 + 0.25 + 0.25 + 2.25 = 5$. The slope is $7/5 = 1.4$ per bar. The fitted value at the last bar is $12 + 1.4 \times 1.5 = 14.1$. The latest close is 14, and the simple average is 12.

**Properties.** On a perfectly straight climb, the value equals price exactly and the slope equals the true rate of climb. After a sudden 10-point jump, it overshoots by 3.0 points. The check script confirms both, and confirms the formula against a separate least-squares routine.

```python
def linreg(close, n=20):
    x = np.arange(n)
    centered = x - x.mean()
    slope = close.rolling(n).apply(lambda y: (centered * (y - y.mean())).sum() / (centered ** 2).sum(), raw=True)
    value = close.rolling(n).mean() + slope * (n - 1 - x.mean())
    return value, slope
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/linear-regression-dark.svg">
<img src="../../charts/linear-regression-light.svg" alt="Price and the 20-bar linear regression value above, with the regression slope below" width="840" height="590">
</picture>
<figcaption>Synthetic data. The regression value (pink) is closer to price than the SMA (teal) on the way down, but it undershoots at the low: it reached 84.9 at bar 250, against a price low of 88.8. It crossed price 17 times in the 100-bar range, against 12 for the SMA. The slope was positive on 84% of uptrend bars and 6% of selloff bars.</figcaption>
</figure>

- **The line** follows a steady trend very closely. Price above it means price is above its fitted trend, and below means below.
- **The slope** is the headline number: positive for a rising fit, negative for a falling one, and its size is the steepness in price units per bar.
- **A change in sign of the slope** is the study's trend-change signal. It is quicker than a moving-average crossover and noisier.

What it does not tell you: where price goes next. Extending the line into the future assumes the trend continues, and that is the one thing a fit to the past cannot show.

## Best used when

- Price is **trending in a roughly straight line**.
- You want a **single number for trend direction and steepness**.
- You want an average that does not **lag** on a steady move.

## Avoid when

- Price is **sideways or curved**. The fit is poor, and the line swings with each new bar.
- A **sharp reversal** just happened. The line overshoots: in the sample it reached 84.9, which is 3.9 below the actual low of 88.8.
- You use it as a **forecast** of future prices.

## Settings and tuning

- **Length 20** is a common default. A longer window fits a longer trend and is smoother. A shorter window follows closely and is jumpy.
- The slope's scale depends on price level, so compare slopes across instruments only after converting to a percentage.

## Implementation variations

- **Names.** The regression value at the latest bar is also called the *time series forecast*, the *least squares moving average* and the *end point moving average*. They are all the same thing.
- **Channels.** Many platforms draw a *regression channel* around the line, at some number of standard deviations of the errors. That is an addition and not part of this study.
- **Forecast version.** Some tools plot the value projected a few bars ahead. That is an extrapolation.

## Is it useful?

**Situational.** It does something moving averages cannot: it has no lag on a steady trend, and it gives a direct reading of slope. On the sample, the slope was positive on 84% of the uptrend's bars and 6% of the selloff's. But the price of zero lag is overshoot and chop. It crossed price 17 times in the 100-bar range, against 12 for the simple average. It is not like the simple average: the distance of price from each correlated only 0.34. It suits a steady trend, and it is a poor choice for anything that curves.

## Pairs well with / See also

- [Simple Moving Average](../simple-moving-average/): reports the middle of the window, where this reports the end of a fitted line.
- [Hull Moving Average](../hull-moving-average/): another way of cutting lag, also with overshoot.
- [Average Directional Index](../average-directional-index/): a measure of how strong the trend is, to judge whether a straight-line fit makes sense.
