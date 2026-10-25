---
title: Woodie's CCI
aliases: [Woodie CCI, Turbo CCI, Woodies CCI]
category: momentum
summary: Two Commodity Channel Index lines on one panel, a standard 14-bar one and a fast 6-bar "turbo" one, read together with a set of trading rules. The calculation is the ordinary CCI, and the rules are what make it Woodie's.
display: panel
inputs:
  - { name: main length, default: 14 }
  - { name: turbo length, default: 6 }
verdict: situational
status: draft
related: [commodity-channel-index, bollinger-bands, stochastic-oscillator]
overlaps:
  - with: commodity-channel-index
    strength: identical
    note: "The 14-bar line is exactly the Commodity Channel Index at length 14. The 6-bar turbo line is the same formula at a shorter length."
---

> **In plain English.** The Commodity Channel Index measures how far the typical price is from its average, scaled by how much it usually wanders. Woodie's version plots two of them: a slow 14-bar line for the trend and a fast 6-bar one for timing. The "system" is a set of rules for reading how the lines behave together, such as how many bars the slow line stays on one side of zero.
>
> **Good for:** short-term trading on a chart where you want a trend line and a trigger line side by side.
>
> **Watch out for:** the part that is not math. The formulas are ordinary CCI. The patterns and rules come from the author's method, and this page does not test them.

## What it measures

Exactly what the [Commodity Channel Index](../commodity-channel-index/) does, at two speeds.

## Calculation

For each length $n$, with the typical price $T = (H+L+C)/3$:

$$
\text{CCI}_n = \frac{T - \text{SMA}_n(T)}{0.015 \times \text{mean deviation}_n(T)}
$$

The 14-bar line is the main line, and the 6-bar line is the turbo line.

**A hard ceiling on the fast line.** With a short window, the CCI cannot go beyond a limit. If one bar jumps far from all the others, the reading reaches $n / (2 \times 0.015)$ and no further: 200 for 6 bars, and 466.7 for 14. So the turbo CCI pins at exactly ±200 when a window holds a single outlier. The check script confirms both ceilings.

```python
def woodies_cci(high, low, close, main=14, turbo=6):
    typical = (high + low + close) / 3

    def commodity_channel(n):
        mean = typical.rolling(n).mean()
        mean_dev = typical.rolling(n).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
        return (typical - mean) / (0.015 * mean_dev)

    return commodity_channel(main), commodity_channel(turbo)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/woodies-cci-dark.svg">
<img src="../../charts/woodies-cci-light.svg" alt="Price above, and the 14-bar and 6-bar Commodity Channel Index lines below with lines at -100, 0 and 100" width="840" height="590">
</picture>
<figcaption>Synthetic data. The 14-bar CCI (pink) ranged from -217 to +235. The 6-bar turbo CCI (teal) ranged exactly from -200 to +200, its mathematical ceiling. It crossed zero 46 times, against 28 for the 14-bar line.</figcaption>
</figure>

- **±100** are the usual overbought and oversold lines. On the sample, the 14-bar line was beyond them on 41% of scored bars, and the 6-bar line on 42%.
- **The turbo line** crosses zero often: 46 times in the sample, against 28 for the 14-bar line.
- **The trend** is read from how long the 14-bar line has stayed on one side of zero. Woodie's rules count the bars.

What it does not tell you: whether the rules, which this page does not test, add anything beyond what plain CCI gives.

## Best used when

- You trade **short-term** and like a two-speed view.
- You follow Woodie's method and want the standard lines.

## Avoid when

- You want a **simple** indicator. Two lines and a rulebook is a lot.
- You compare with a plain CCI and expect different numbers. The 14-bar line is the same.

## Settings and tuning

- **14 and 6** are the standard lengths.
- **A shorter turbo** has a lower ceiling and is noisier.

## Implementation variations

- **Mean deviation.** The standard CCI uses the mean absolute deviation from the average, as here.
- **Extra lines.** Some chart setups add a zero-line cross indicator and a histogram colored by trend.
- **History.** The "Woodie" is usually said to be Ken Wood. I have not confirmed the details.

## Is it useful?

**Situational.** The main line is the CCI you already know, so everything on the [CCI page](../commodity-channel-index/) applies. The turbo line adds a faster read at the cost of noise: it correlated 0.79 with the 14-bar line on the sample, and it flipped the sign of its reading far more often. Whether Woodie's rules turn the two lines into an edge is a matter for your own testing. As a pair of CCI lines on one panel, it is perfectly fine.

## Pairs well with / See also

- [Commodity Channel Index](../commodity-channel-index/): the line the system is built on.
- [Bollinger Bands](../bollinger-bands/): a closely related distance-from-average measure.
- [Stochastic Oscillator](../stochastic-oscillator/): another fast timing oscillator.
