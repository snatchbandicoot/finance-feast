---
title: Projection Bands
aliases: [Projection Oscillator, Widner Projection Bands]
category: volatility
summary: A channel that tilts with the trend. The highest and lowest highs and lows of the last 14 bars are projected forward along the slope of the trend, so the bands follow a drifting market. The Projection Oscillator shows where the close sits between them.
display: overlay
inputs:
  - { name: length, default: 14 }
verdict: situational
status: draft
related: [linear-regression, donchian-channels, stochastic-oscillator]
---

> **In plain English.** A Donchian channel marks the highest high and lowest low of the last 14 bars, as flat lines. That misleads in a trending market, since old extremes sit far from where price is now. Projection Bands tilt the old highs and lows along the trend's slope first, as if the trend had carried them forward to today. The bands follow a climbing or falling market, and the oscillator places the close between them, from 0 to 100.
>
> **Good for:** an envelope that tracks a drifting market, and an oscillator that is less thrown off by trends than a plain stochastic.
>
> **Watch out for:** the bands themselves. They contain the current bar, so price can never close beyond them. All the signal is in the oscillator.

## What it measures

The range of recent highs and lows after adjusting for the trend, and the position of the close inside it.

## Calculation

Let $m$ be the slope of the straight line fitted to the last $N$ closes (see [Linear Regression](../linear-regression/)). Each past high and low is moved forward by the trend, $m$ per bar:

$$
\text{Upper}_t = \max_{i=0}^{N-1}\bigl(H_{t-i} + m\,i\bigr) \qquad \text{Lower}_t = \min_{i=0}^{N-1}\bigl(L_{t-i} + m\,i\bigr)
$$

$$
\text{PO}_t = 100 \times \frac{C_t - \text{Lower}_t}{\text{Upper}_t - \text{Lower}_t}
$$

**Worked example.** With $N = 3$, closes 12, 13, 14 and bar ranges of ±0.5 around each close, the slope is $+1$. The upper band is the largest of $14.5 + 0$, $13.5 + 1$ and $12.5 + 2$, which is 14.5. The lower band is the smallest of $13.5 + 0$, $12.5 + 1$ and $11.5 + 2$, which is 13.5. The close is 14, so:

$$
\text{PO} = 100 \times \frac{14 - 13.5}{14.5 - 13.5} = 50
$$

**Why price never breaks them.** The $i = 0$ term is today's own high (for the upper band) and low (for the lower band), so the bands always contain the whole current bar. The check script confirms that no close in the data ever lies outside.

```python
def projection_bands(high, low, close, n=14):
    x = np.arange(n)
    slope = close.rolling(n).apply(lambda w: np.polyfit(x, w, 1)[0], raw=True)
    upper = pd.concat([high.shift(i) + slope * i for i in range(n)], axis=1).max(axis=1, skipna=False)
    lower = pd.concat([low.shift(i) + slope * i for i in range(n)], axis=1).min(axis=1, skipna=False)
    return upper, lower, 100 * (close - lower) / (upper - lower)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/projection-bands-dark.svg">
<img src="../../charts/projection-bands-light.svg" alt="Price with Projection Bands above, and the Projection Oscillator below with lines at 20 and 80" width="840" height="590">
</picture>
<figcaption>Synthetic data. No close lay outside the bands in all 320 bars. The oscillator ranged from 1.3 to 96.6 over the scored bars, and read 75.7 at the price low (bar 249).</figcaption>
</figure>

- **The oscillator near 100** means the close is at the top of the trend-adjusted range, and **near 0** at the bottom. 80 and 20 are the usual levels.
- **Band width** shows how wide the recent range has been, after the trend is removed.
- **Slope** of the bands shows the trend.

What it does not tell you: whether an extreme is a stretch or a start. And the oscillator reading at a price low can be well above zero, as the sample shows.

## Best used when

- You want a **trend-aware** range, in a market that drifts.
- You like the stochastic format and want the trend taken out.

## Avoid when

- You want bands that **price can break**. These cannot be broken by a close.
- The market is **choppy**: the slope is near zero and the bands become a plain Donchian channel.

## Settings and tuning

- **14** is the usual length. Longer is smoother and wider.

## Implementation variations

- **Slope source.** The slope of closes here. Some versions fit the highs and lows separately.
- **Two oscillators.** Some tools also draw a smoothed version of the oscillator.
- **History.** It is usually credited to Mel Widner. I have not confirmed the details.

## Is it useful?

**Situational.** The idea of projecting old extremes along the trend is sensible, and it removes much of a Donchian channel's trend bias. On the sample the oscillator averaged 50.7 in the uptrend, 48.3 in the range, 41.4 in the selloff and 55.3 in the rebound, and ranged from 1.3 to 96.6. But at the price low (bar 249) it read 75.7, which a trader hoping for an oversold reading would have missed, and it correlated only 0.47 with a plain Stochastic. The bands themselves cannot be broken by a close, so the oscillator is the only signal. A reasonable variation if you like range-based oscillators and want trend adjustment.

## Pairs well with / See also

- [Linear Regression](../linear-regression/): the source of the slope.
- [Donchian Channels](../donchian-channels/): the flat version of the same envelope.
- [Stochastic Oscillator](../stochastic-oscillator/): the plain position-in-range oscillator.
