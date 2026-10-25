---
title: Heikin-Ashi
aliases: [Heiken Ashi, Heikin Ashi Candles, HA]
category: trend
summary: A way of drawing candles from averaged prices, so that runs of the same color are longer and trends look cleaner. The prices on the candles are not real prices, so it is for looking, not for placing orders.
display: overlay
inputs: []
verdict: situational
status: draft
related: [exponential-moving-average, supertrend, parabolic-sar]
---

> **In plain English.** Ordinary candles flip color whenever a bar closes a little lower than it opened, even inside a strong rise. Heikin-Ashi candles are built from averaged prices, including the previous candle, so they smooth that out. A rising market becomes a long run of same-colored candles. It is easier on the eye, and it is also slower and not literally true.
>
> **Good for:** staying with a trend instead of reacting to every counter-move.
>
> **Watch out for:** the numbers on the candles. A Heikin-Ashi close is not the real close, and a stop or entry cannot be placed from it.

## What it measures

Nothing new. It re-draws the same bars with an averaging step applied. The color shows the direction of the smoothed move, and the length of the bodies and wicks shows how one-sided it has been.

## Calculation

For each bar, with the real open $O$, high $H$, low $L$ and close $C$:

$$
HA_C = \frac{O + H + L + C}{4} \qquad HA_O = \frac{HA_{O,t-1} + HA_{C,t-1}}{2}
$$

$$
HA_H = \max(H,\ HA_O,\ HA_C) \qquad HA_L = \min(L,\ HA_O,\ HA_C)
$$

The first Heikin-Ashi open is $(O + C)/2$. A candle is up when $HA_C \ge HA_O$.

**Worked example.** The first bar has $O=10$, $H=12$, $L=9$, $C=11$. Its HA close is $(10+12+9+11)/4 = 10.5$, and its HA open is $(10+11)/2 = 10.5$. The second bar has $O=11$, $H=13$, $L=10.5$, $C=12.5$:

- HA close: $(11 + 13 + 10.5 + 12.5)/4 = 11.75$
- HA open: $(10.5 + 10.5)/2 = 10.5$
- HA high: $\max(13, 10.5, 11.75) = 13$
- HA low: $\min(10.5, 10.5, 11.75) = 10.5$

A bar whose HA open and HA low are equal has no lower wick, which signals a strong move up.

```python
def heikin_ashi(open_, high, low, close):
    ha_close = (open_ + high + low + close) / 4
    ha_open = ha_close.copy()
    ha_open.iloc[0] = (open_.iloc[0] + close.iloc[0]) / 2
    for i in range(1, len(close)):
        ha_open.iloc[i] = (ha_open.iloc[i - 1] + ha_close.iloc[i - 1]) / 2
    ha_high = pd.concat([high, ha_open, ha_close], axis=1).max(axis=1)
    ha_low = pd.concat([low, ha_open, ha_close], axis=1).min(axis=1)
    return ha_open, ha_high, ha_low, ha_close
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/heikin-ashi-dark.svg">
<img src="../../charts/heikin-ashi-light.svg" alt="Ordinary candles above and Heikin-Ashi candles below, for the same 100 bars" width="840" height="640">
</picture>
<figcaption>Synthetic data, bars 190 to 290, covering the selloff and the start of the rebound. Over the whole sample the ordinary candle color flipped 129 times and the Heikin-Ashi color 56 times.</figcaption>
</figure>

- **Color runs.** A run of same-colored candles is a trend. A color change is the first hint that it is ending.
- **No lower wick** on up-candles shows a strong up-trend, and **no upper wick** on down-candles a strong down-trend.
- **Small bodies with wicks both sides** show indecision.

What it does not tell you: the real prices, or how large the real bar's move was.

## Best used when

- You **follow trends** and want to avoid reacting to every pullback.
- You use it as a **visual filter** alongside the ordinary chart.

## Avoid when

- You need **exact prices**. A Heikin-Ashi close can differ from the real close by a lot: by 0.47 on average in the sample, and 2.89 at most.
- The market is **choppy**, where its lag delays every signal.
- You trade gaps or the open. The averaged open hides them.

## Settings and tuning

- **No settings.** The formula is fixed.
- **Time frame** is the only choice, and a longer one gives smoother candles.

## Implementation variations

- **First candle.** Tools differ in how they start the first HA open, which affects only the first few candles.
- **Real prices.** Some platforms show the real last price next to the Heikin-Ashi candle for this reason.
- **History.** The name is usually said to mean "average bar" in Japanese. I have not confirmed its origin.

## Is it useful?

**Situational.** It does what it claims: in the sample's bars 60 to 319 the ordinary candle color flipped 129 times and the Heikin-Ashi color 56 times, and the average run of same-colored candles was 4.6 bars against 2.0. That is a cleaner picture. The cost is that every candle is a blend of the previous ones, so it responds late, and it throws away the real prices. It is a view to read a trend with, and it is not a signal in itself. Use it next to the real chart.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): another way to smooth the picture.
- [Supertrend](../supertrend/): a trend-following overlay with a similar goal.
- [Parabolic SAR](../parabolic-sar/): a trend-following overlay that flips.
