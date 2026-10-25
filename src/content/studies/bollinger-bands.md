---
title: Bollinger Bands
aliases: [BBands, BB, Bollinger Bands percent B, Bollinger Bandwidth]
category: volatility
summary: A moving average with a band above and below it that widens when price swings are large and narrows when they are small.
display: overlay
inputs:
  - { name: length, default: 20 }
  - { name: standard deviations, default: 2 }
verdict: situational
status: draft
related: [simple-moving-average, average-true-range, relative-strength-index, commodity-channel-index]
---

> **In plain English.** Three lines drawn on the price chart: an average in the middle, and a band above and below it. The bands sit a set number of standard deviations (a measure of how much prices have been scattered) away from the average. When prices have been jumpy, the bands spread out. When prices have been calm, they pull in. A price at the edge of a band is unusually far from its recent average. That is a description, not a prediction.
>
> **Good for:** seeing how volatile the market has been lately, and noticing when price is stretched or when volatility is unusually low.
>
> **Watch out for:** treating a touch of the upper or lower band as a signal to sell or buy. In a strong trend, price can ride along a band for a long time.

## What it measures

Two things at once:

1. **Where price is** relative to its recent average and typical spread.
2. **How wide that spread is**, which is the same as recent volatility.

The width of the bands comes from the standard deviation of recent closes, so it reflects how scattered prices have been in the window. The bands are not a forecast of where price must stay.

## Calculation

With length $N$ (default 20) and multiplier $k$ (default 2):

$$ \text{Middle}_t = \text{SMA}_N(P)_t \qquad \sigma_t = \sqrt{\tfrac{1}{N}\sum_{i=0}^{N-1}\left(P_{t-i} - \text{Middle}_t\right)^2} $$

$$ \text{Upper}_t = \text{Middle}_t + k\,\sigma_t \qquad \text{Lower}_t = \text{Middle}_t - k\,\sigma_t $$

Two derived readings are common:

$$ \%B = \frac{P - \text{Lower}}{\text{Upper} - \text{Lower}} \qquad \text{Bandwidth} = \frac{\text{Upper} - \text{Lower}}{\text{Middle}} $$

%B says where price sits inside the bands (1 at the upper band, 0 at the lower). Bandwidth says how wide the bands are as a share of the average.

**Worked example.** Take the last three closes, 12, 11, 13 (so $N = 3$) and $k = 2$.

- Middle: $(12 + 11 + 13)/3 = 12$.
- Deviations from 12 are 0, −1, +1, so $\sigma = \sqrt{(0 + 1 + 1)/3} = \sqrt{2/3} \approx 0.816$.
- Upper $= 12 + 2 \times 0.816 \approx 13.633$. Lower $= 12 - 2 \times 0.816 \approx 10.367$.
- If the latest price is 12.5: $\%B = (12.5 - 10.367)/(13.633 - 10.367) \approx 0.653$.
- Bandwidth $= (13.633 - 10.367)/12 \approx 0.272$, or about 27%.

```python
def bollinger(close, n=20, k=2):
    mid = close.rolling(n).mean()
    sd = close.rolling(n).std(ddof=0)
    return mid, mid + k * sd, mid - k * sd
```

Note `ddof=0`. See "Implementation variations" below.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/bollinger-bands-dark.svg">
<img src="../../charts/bollinger-bands-light.svg" alt="Price with Bollinger Bands, a 20-bar average and bands two standard deviations away" width="840" height="430">
</picture>
<figcaption>Synthetic data. Band width averaged about 6% of price in the range and 13% in the selloff, and it was narrowest (under 3%) around bar 284 during the rebound. The bands widen when volatility rises. They do not say which way price will go.</figcaption>
</figure>

- **Band width.** Wide bands mean volatility has been high. Narrow bands (a "squeeze") mean it has been low. Volatility tends to come in clusters, so low volatility has historically tended to be followed by higher volatility, and the reverse. A squeeze tells you a bigger move is *more likely* at some point. It does not tell you which direction.
- **Price at a band.** The price is unusually far from its recent average. In a range, that often precedes a move back toward the middle. In a trend, price can stay near one band for many bars ("walking the band"), and each touch is then a sign of strength.
- **%B.** The same information as band position, as a number. Above 1 means price closed above the upper band, below 0 means below the lower band.
- **Middle line.** It is just a simple moving average, so everything on that page applies.

What it does not tell you: the probability of a reversal, or that price must come back inside the bands.

A common claim is that two standard deviations contain "95% of prices". That figure holds only for a bell-curve distribution. Prices are not bell-curved: the bands are drawn around price *levels*, which trend, and price moves have heavier tails than a bell curve. Do not read the bands as a 95% interval.

## Best used when

- Price is **ranging**, so that a stretch to a band is more likely to revert toward the middle.
- You want a quick view of **volatility** changing, such as a squeeze or a sudden expansion.
- You want a **volatility-adjusted** sense of "stretched": a move to a band means different things in a calm market and a jumpy one.

## Avoid when

- Price is **trending strongly**. Selling at the upper band or buying at the lower band fights the trend, and price can hug the band the whole way.
- You treat the bands as **support and resistance**. They are a statistical envelope, and they move every bar.
- The window holds **one extreme bar**. One huge move inflates the standard deviation, so the bands widen sharply, and then they snap back when the bar leaves the window.
- You want to **compare instruments** using band width in price units. Use bandwidth (a percentage) for that.

## Settings and tuning

- **Length 20 and multiplier 2** are John Bollinger's defaults for daily charts.
- **Longer length:** smoother bands that react slowly.
- **Shorter length:** bands that follow price tightly and touch more often, with more false extremes.
- **Larger multiplier** (such as 2.5): wider bands, fewer touches. **Smaller multiplier:** the opposite.
- Bollinger himself recommends adjusting the multiplier when changing length, for example a bit above 2 for lengths longer than 20, and a bit below for shorter ones.

## Implementation variations

- **Standard deviation type.** Bollinger's original uses the *population* standard deviation (dividing by $N$). Some tools and libraries default to the *sample* version (dividing by $N-1$), which makes the bands slightly wider. That alone can make the same-looking study differ between two programs. This is the first thing to check when bands do not match.
- **Middle line.** The standard middle line is a simple average. Some versions use an EMA.
- **Name.** "Bollinger Bands" is a trademark of John Bollinger. The study itself is widely implemented.

## Is it useful?

**Situational.** It is among the more informative overlays, because it adds volatility information that a plain moving average lacks. As a *volatility* gauge it is solid. As a source of buy and sell signals it is weak on its own, because the band touch means something opposite in a range and in a trend. It overlaps with the Average True Range as a volatility measure, but it also tells you where price sits relative to that volatility, which ATR does not.

## Pairs well with / See also

- [Simple Moving Average](../simple-moving-average/): the middle line.
- [Average True Range](../average-true-range/): another volatility measure, in price units and not tied to the average.
- [Relative Strength Index](../relative-strength-index/): a momentum reading that helps separate a stretched range from a strong trend.
- [Commodity Channel Index](../commodity-channel-index/): very close to %B in what it measures. On the sample data the two correlated at 0.98.
