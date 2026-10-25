---
title: Stochastic Oscillator
aliases: [Stochastic, Stochastics, "%K %D", Slow Stochastic, Full Stochastic]
category: momentum
summary: A 0 to 100 reading of where the latest close sits within the recent high-to-low range.
display: panel
inputs:
  - { name: length, default: 14 }
  - { name: "%K smoothing", default: 3 }
  - { name: "%D smoothing", default: 3 }
verdict: situational
status: draft
related: [relative-strength-index, simple-moving-average, macd, williams-percent-r]
overlaps:
  - with: relative-strength-index
    strength: partial
    corr: 0.81
    note: "Both are 0 to 100 oscillators, but the stochastic measures where the close sits in the recent range, and RSI measures the balance of gains and losses."
---

> **In plain English.** Look back over the last N bars and find the highest high and the lowest low. The stochastic tells you where the latest close sits between them, from 0 (at the bottom of the range) to 100 (at the top). Closes near the top of the range score high, closes near the bottom score low. A second, smoother line follows it so you can spot turns.
>
> **Good for:** seeing whether price is closing near the top or bottom of its recent range, especially in a sideways market.
>
> **Watch out for:** strong trends, where it can sit at the top or bottom of its scale for a long time. Calling that "overbought" or "oversold" and trading against the trend is the usual mistake.

## What it measures

Position within a range. Not speed, not gains versus losses, but *where the close landed* between the recent low and the recent high.

In an uptrend, closes tend to land near the top of the range, so the stochastic stays high. In a downtrend it stays low. When price drifts sideways, closes land all over the range and the stochastic swings between the extremes.

This is a different question from the one [RSI](../relative-strength-index/) asks. RSI compares the size of up-moves with down-moves. The stochastic compares the close with the recent range. They often move together, but they are not the same measurement.

## Calculation

Over the last $N$ bars, let $HH$ be the highest high and $LL$ the lowest low. The raw reading is:

$$
\text{raw }\%K_t = 100 \times \frac{C_t - LL_t}{HH_t - LL_t}
$$

Then two layers of smoothing, with simple moving averages:

$$
\%K_t = \text{SMA}_{3}\!\left(\text{raw }\%K\right)_t \qquad \%D_t = \text{SMA}_{3}\!\left(\%K\right)_t
$$

The version without the first smoothing step (raw $\%K$ smoothed once to make $\%D$) is called the *fast* stochastic. The version above, with both, is the *slow* (or *full*) stochastic and is the usual default.

**Worked example.** Over the last 14 bars the highest high is 20 and the lowest low is 10. The latest close is 16. Then raw $\%K = 100 \times (16 - 10)/(20 - 10) = 60$: the close sits 60% of the way up the range.

Smoothing: if the last three raw readings are 60, 70 and 80, the slow $\%K$ is their average, 70.

```python
def stochastic(high, low, close, n=14, smooth_k=3, smooth_d=3):
    lowest = low.rolling(n).min()
    highest = high.rolling(n).max()
    raw_k = 100 * (close - lowest) / (highest - lowest)
    k = raw_k.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    return raw_k, k, d
```

If the highest high equals the lowest low over the window (a completely flat range), the formula divides by zero. Tools handle that differently, so expect a gap or a fixed value there.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/stochastic-oscillator-dark.svg">
<img src="../../charts/stochastic-oscillator-light.svg" alt="Price above, and slow stochastic %K and %D below with lines at 20 and 80" width="840" height="590">
</picture>
<figcaption>Synthetic data. In the selloff %K was below 20 on more than half the bars while price kept falling, so a low reading was not a buy signal. In the range it swung between the extremes again and again, which is where the stochastic is most at home.</figcaption>
</figure>

- **Level.** Above about 80 means closes have been landing near the top of the recent range, and below about 20 means the bottom. These are conventions, like RSI's 70 and 30. They say "near an edge", not "about to reverse".
- **Crossovers.** When $\%K$ crosses above $\%D$, the close is moving up within its range, and the reverse for a cross below. This is the common trigger, and in a sideways market it fires constantly.
- **Divergence.** Price makes a new high but the stochastic makes a lower high. As with other oscillators, it is described as a warning and it often fails.
- **In trends.** In a persistent uptrend, the stochastic can stay above 80 for many bars while price keeps rising. Treat the high reading as confirmation of strength, not a sell signal. The more useful read is a *dip* in an uptrend that recovers back through the upper levels.

What it does not tell you: how large a move will be, or when the range will break. It also forgets everything older than $N$ bars, so a new high that leaves the window lowers the top of the range and shifts every reading.

## Best used when

- Price is **ranging**, and you want to see closes pushing toward the top or bottom of the range.
- You want to **time an entry inside a trend** you have already identified with another study, for example waiting for a dip in an uptrend to recover.

## Avoid when

- Price is **trending strongly**. Selling every reading above 80 in an uptrend fights the trend.
- You use it as the **only reason** for a trade. It gives a lot of crossovers, and most of them mean little.
- The range is **very narrow**. A tiny high-to-low range makes the denominator small, so small price moves swing the reading across the whole scale.
- You use a **very short length** and expect stable readings. It will jump around.

## Settings and tuning

- **14 / 3 / 3** are the common defaults on most charting platforms. George Lane is usually credited with developing the study.
- **Shorter length:** more sensitive, more crossovers, more false signals.
- **Longer length:** smoother, fewer extremes, slower.
- **More smoothing** on $\%K$ and $\%D$ reduces noise and delays signals. The fast version (no first smoothing) is much jumpier.

## Implementation variations

- **Fast, slow and full.** These names are used inconsistently across tools. Check what smoothing a given chart applies before comparing it with another.
- **Smoothing type.** Simple averages are standard, but some tools offer exponential ones, which changes the values.
- **Flat ranges.** Handling of the zero-range case varies.

## Is it useful?

**Situational.** It is a reasonable way to see where price is closing within its range, and it works best in a sideways market. As a standalone buy-or-sell signal it is weak, for the same reason RSI is: an extreme reading in a trend is not a reversal. It overlaps with RSI and with other bounded oscillators. If you already watch RSI, adding the stochastic mostly repeats it, with a different look and a bit more noise.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): the other widely used bounded momentum gauge. RSI measures gains versus losses, and the stochastic measures close versus range.
- [Simple Moving Average](../simple-moving-average/): both smoothing steps are simple moving averages.
- [MACD](../macd/): another momentum study, built from moving averages and not from the range.
- [Williams %R](../williams-percent-r/): the same measurement as the raw reading here, shifted onto a negative scale.
