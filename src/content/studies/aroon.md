---
title: Aroon
aliases: [Aroon Up, Aroon Down, Aroon Oscillator]
category: trend
summary: Two lines that show how recently price set a new high and a new low, used to tell whether a trend is still making fresh extremes.
display: panel
inputs:
  - { name: length, default: 25 }
verdict: situational
status: draft
related: [average-directional-index, donchian-channels, parabolic-sar]
---

> **In plain English.** Aroon asks how long ago the highest price of the last 25 bars was set. If it was set just now, Aroon Up reads near 100. If it was set 25 bars ago, it reads 0. Aroon Down does the same for the lowest price. A healthy uptrend shows Up high and Down low. It measures timing and not size, so a new high by a hair counts the same as a breakout.
>
> **Good for:** telling whether a trend is still making fresh highs or lows, or has gone stale.
>
> **Watch out for:** its mechanical sawtooth shape. After a peak, each line falls by a fixed 4 points a bar for a 25-bar setting, whatever price does.

## What it measures

Time since the last extreme, not distance. Over a window of the last $N$ bars, how many bars ago was the highest high, and how many bars ago was the lowest low? Trends make new extremes often, so one line stays near the top. Sideways markets make them rarely and unevenly, so both lines wander.

This is a different kind of information from the moving-average studies, which measure *where* price is, and from [ADX](../average-directional-index/), which measures how *one-sided* movement is. Aroon only looks at the timing of the extremes.

## Calculation

Look at the last $N + 1$ bars (the current bar and the $N$ before it). Let the highest high in that window have been set $k_H$ bars ago (0 if it is the current bar), and the lowest low $k_L$ bars ago:

$$ \text{Aroon Up} = 100 \cdot \frac{N - k_H}{N} \qquad \text{Aroon Down} = 100 \cdot \frac{N - k_L}{N} $$

$$ \text{Aroon Oscillator} = \text{Aroon Up} - \text{Aroon Down} $$

**Worked example.** With $N = 4$, a window of five bars has highs of 10, 12, 11, 11.5, 11.2 and lows of 9, 10, 9.5, 9.8, 9.4. The highest high, 12, was set 3 bars ago, so Aroon Up $= 100 \times (4 - 3)/4 = 25$. The lowest low, 9, was set 4 bars ago, so Aroon Down $= 100 \times (4 - 4)/4 = 0$. The oscillator is $+25$.

```python
def aroon(high, low, n=25):
    up = high.rolling(n + 1).apply(lambda w: 100 * (n - np.argmax(w[::-1])) / n, raw=True)
    down = low.rolling(n + 1).apply(lambda w: 100 * (n - np.argmin(w[::-1])) / n, raw=True)
    return up, down, up - down
```

If the same extreme appears twice in the window, the most recent one counts.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/aroon-dark.svg">
<img src="../../charts/aroon-light.svg" alt="Price above, and Aroon Up and Aroon Down below with lines at 30 and 70" width="840" height="590">
</picture>
<figcaption>Synthetic data. In the selloff, Aroon Down reached 100 (a new 25-bar low) at bar 203, three bars after the selloff began, and Down was above 70 with Up below 30 on 54% of the selloff's bars. In the uptrend the matching Up-above-70, Down-below-30 condition held on only 16% of bars. The two lines crossed 7 times in the 100-bar range.</figcaption>
</figure>

- **Up near 100 and Down near 0** means price has just made new highs and not new lows, which is how an uptrend looks. A common rule of thumb calls Up above 70 with Down below 30 a confirmed uptrend, and the reverse a downtrend. These are conventions.
- **Up equal to 100** has an exact meaning: the current bar set a new 25-bar high (or tied the old one). That is the same event as a Donchian upper-channel breakout. The same holds for Down and a new 25-bar low.
- **Crossovers.** When Up crosses above Down, recent highs are more recent than recent lows, which is a shift toward an uptrend. In a sideways market the two cross repeatedly.
- **The oscillator** is just Up minus Down, from −100 to +100. Above zero favors the upside.

What it does not tell you: how big the moves were, or how long a trend will last.

## Best used when

- You want to know whether a trend is **still making progress** or has stalled, even before price turns.
- You want a trend reading that is **independent** of moving averages and of the size of moves, to compare with them.
- You pair it with [ADX](../average-directional-index/): ADX says how strong, Aroon says how fresh.

## Avoid when

- Price is **sideways**. The extremes are set at random, and the lines cross constantly.
- **Size matters.** A new high by one tick and a new high by ten percent look identical to Aroon.
- You use a **very short length**. The lines then swing between 0 and 100 on ordinary noise.

## Settings and tuning

- **Length 25** is the usual default.
- **Shorter** (such as 10 to 14): more sensitive, and the lines hit 0 and 100 constantly.
- **Longer** (such as 50): reacts only to major highs and lows, and lags.
- **The 70 and 30 lines** are conventions. Moving them to fit past charts is a good way to fool yourself.

## Implementation variations

- **Window length.** This page uses the last $N + 1$ bars, so that both 0 and 100 can be reached. Some tools use only $N$ bars, so the lines run from $100/N$ to 100.
- **Counting.** "Bars since the high" is counted slightly differently in some libraries, which shifts every value by one step ($100/N$ points).
- **Ties.** Handling of equal highs differs.

## Is it useful?

**Situational.** It is a clean, honest measure of whether a trend is still making fresh extremes, and it carries information that moving averages do not. In this site's sample, Aroon Down hit 100 (a new 25-bar low) at bar 203, only three bars after the selloff began, much earlier than ADX confirmed it. But it ignores size, it saws mechanically between 0 and 100, and a crossover in a sideways market means little. A Donchian breakout rule contains the same event as Aroon at 100, so if you already use that, Aroon mostly restates it with a countdown attached.

## Pairs well with / See also

- [Average Directional Index](../average-directional-index/): trend strength, where Aroon gives trend freshness.
- [Donchian Channels](../donchian-channels/): Aroon at 100 is the same event as a breakout of the channel.
- [Parabolic SAR](../parabolic-sar/): another study built on the timing of extremes, as a trailing stop.
