---
title: Pivot Points
aliases: [Floor Trader Pivots, Classic Pivots, Pivots]
category: other
summary: Horizontal levels computed from the previous session's high, low and close, drawn on the next session as a pivot with two support and two resistance lines. They are fixed in advance, and many traders watch them.
display: overlay
inputs:
  - { name: period, default: "previous day" }
verdict: situational
status: draft
related: [donchian-channels, volume-weighted-average-price, average-true-range]
---

> **In plain English.** Before today opens, take yesterday's high, low and close. Average them for a central "pivot", and use a short formula to draw two lines above it and two below. Those five lines are fixed for the day. The idea is that price tends to pause, stall or bounce at them, partly because many traders have the same lines drawn.
>
> **Good for:** knowing in advance where today's reference prices are, with no lag and no repainting.
>
> **Watch out for:** treating them as magic. Their usefulness comes from other people watching them, which a chart of synthetic data cannot show.

## What it measures

Nothing about the market directly. The pivot is the average of the previous session's high, low and close, and the other levels are offsets from it based on the previous session's range. They are a ruler laid out at the start of the day.

## Calculation

Let $H$, $L$ and $C$ be the previous session's high, low and close.

$$
P = \frac{H + L + C}{3}
$$

$$
R_1 = 2P - L \qquad S_1 = 2P - H \qquad R_2 = P + (H - L) \qquad S_2 = P - (H - L)
$$

**Worked example.** With $H = 12$, $L = 8$ and $C = 11$:

| Level | Value |
|---|---|
| R2 | 14.33 |
| R1 | 12.67 |
| Pivot | 10.33 |
| S1 | 8.67 |
| S2 | 6.33 |

Notice that $R_1 - S_1 = H - L$ always: the first two lines are exactly the previous session's range apart, centred a little off the pivot. The check script confirms this.

```python
def pivot_points(high, low, close):
    """Levels for the NEXT period, from one period's high, low and close."""
    pivot = (high + low + close) / 3
    return pivot, 2 * pivot - low, 2 * pivot - high, pivot + (high - low), pivot - (high - low)
```

The function returns levels for the *next* period. On daily bars, shift by one bar so that each day uses the previous day's numbers.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/pivot-points-dark.svg">
<img src="../../charts/pivot-points-light.svg" alt="Price on 5-minute bars with the pivot, two resistance and two support levels from the previous session" width="840" height="460">
</picture>
<figcaption>Synthetic 5-minute data, three sessions. Levels are calculated from the previous session and drawn across the next. Price reached S1 in both the second and third sessions, did not reach R1 or either second level, and closed the third session below S1.</figcaption>
</figure>

- **Above the pivot** is read as a firmer day, and **below** as a weaker one.
- **R1 and S1** are the first targets or stalls. **R2 and S2** are the stretch levels.
- **Breaks.** A move through a level with force is read as a sign the day is trending.

What it does not tell you: that a level will hold. In the figure, price touched S1 in both the second and third sessions, and in the third it closed below S1.

## Best used when

- You trade **intraday**, from the prior day's numbers, in a liquid market that traders watch.
- You want **objective** reference levels that do not move during the day.

## Avoid when

- You use **long-term** charts. The levels reset every period, and a daily pivot on a monthly view means little.
- The market had a **gap** or news overnight. The levels may be far from where price now trades.

## Settings and tuning

- **The period** is the previous day for intraday use, the previous week for swing use, and the previous month for long-term use.
- **Session hours.** For markets that trade nearly all day, the choice of the session end changes the close used.

## Implementation variations

- **Other formulas.** Fibonacci, Woodie, Camarilla and DeMark pivots use different offsets from the same inputs. They are not the same levels as these.
- **Third level.** Many tools show R3 and S3 as well.
- **Using the open.** Woodie's version counts today's open, which this page does not.
- **History.** They come from floor traders, who calculated them on paper. I do not know who first used them.

## Is it useful?

**Situational.** The levels cost nothing, are known in advance and do not move. That is a real advantage over lines that lag. But what makes them useful is that other traders use them, and this site's synthetic data cannot test that. On the sample's daily bars, the high reached R1 on 47% of bars and the low reached S1 on 45%, so touching them is common, not special, which is expected because R1 and S1 are only one previous range apart. Treat them as a rough map, and see for yourself whether your market respects them.

## Pairs well with / See also

- [Donchian Channels](../donchian-channels/): another set of levels from past highs and lows.
- [Volume Weighted Average Price](../volume-weighted-average-price/): another intraday reference.
- [Average True Range](../average-true-range/): a way to judge whether a level is far or near.
