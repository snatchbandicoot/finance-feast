---
title: Keltner Channels
aliases: [Keltner Channel, Keltner Bands, Keltner]
category: volatility
summary: A moving average with a channel around it whose width comes from the Average True Range, which makes it steadier than Bollinger Bands.
display: overlay
inputs:
  - { name: length, default: 20 }
  - { name: ATR length, default: 10 }
  - { name: multiplier, default: 2 }
verdict: situational
status: draft
related: [bollinger-bands, average-true-range, exponential-moving-average, donchian-channels]
overlaps:
  - with: bollinger-bands
    strength: partial
    corr: 0.68
    note: "Both draw a channel around a moving average. Keltner sets its width from the average true range, and Bollinger from the standard deviation of closes. The correlation shown is between their widths."
---

> **In plain English.** A moving average with a channel above and below it. The channel's width is a multiple of the Average True Range, which tracks the size of whole bars (including gaps). Bollinger Bands set their width from how scattered the closing prices are, which reacts faster to a single big move. The Keltner channel is therefore smoother and steadier.
>
> **Good for:** a volatility-aware envelope that does not balloon after one big bar and does not collapse in a quiet patch.
>
> **Watch out for:** settings. There are many versions (simple or exponential average, different ATR lengths and multipliers), so two charts both labelled "Keltner" often disagree.

## What it measures

Where price sits relative to its recent average, in units of typical bar size. A close outside the channel means price has moved unusually far from its average compared with how big bars have recently been.

## Calculation

$$
\text{Middle}_t = \text{EMA}_N(C)_t \qquad \text{Upper}_t = \text{Middle}_t + k \cdot ATR_M(t) \qquad \text{Lower}_t = \text{Middle}_t - k \cdot ATR_M(t)
$$

$N$ is the average's length (default 20), $M$ is the ATR length (default 10) and $k$ is the multiplier (default 2). The ATR and the EMA are described on their own pages. See [Average True Range](../average-true-range/) and [Exponential Moving Average](../exponential-moving-average/).

**Worked example.** If the middle line is 100, the ATR is 2 and $k = 2$, the upper line is $100 + 2 \times 2 = 104$ and the lower line is $100 - 4 = 96$.

```python
def keltner(high, low, close, n=20, atr_n=10, k=2):
    mid = close.ewm(span=n, adjust=False).mean()
    width = k * atr(high, low, close, atr_n)
    return mid, mid + width, mid - width
```

This function uses `atr()` from the [Average True Range](../average-true-range/) page. As with other recursive averages, the first few dozen values depend on how the averages are started, so treat them as unreliable.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/keltner-channels-dark.svg">
<img src="../../charts/keltner-channels-light.svg" alt="Price with a Keltner channel and Bollinger Bands drawn together" width="840" height="440">
</picture>
<figcaption>Synthetic data, with the first 40 values hidden while the averages warm up. Keltner width averaged 8.5% of price in the selloff, where Bollinger width reached 12.9%, because the ATR-based channel reacts less to a sudden large move. The Bollinger Bands sat inside the Keltner Channel on 111 of 280 bars, so with these multipliers that condition was far from rare.</figcaption>
</figure>

- **Close above the upper line** means an unusually strong move relative to typical bar size. In a trend, price can stay outside or along the line for a long time.
- **Close back inside** after an excursion is often read as the move cooling off, though it is not a reversal signal.
- **Width.** Because it follows the ATR, the channel widens when bars get bigger and narrows when they get smaller, more gently than Bollinger Bands do.
- **Against Bollinger Bands.** Some traders watch for the Bollinger Bands moving *inside* the Keltner Channel as a sign of unusually low volatility, a "squeeze". Whether that happens often depends entirely on the multipliers used.

What it does not tell you: which direction price will go, or whether a move outside the channel will continue.

## Best used when

- You want an envelope that is **steady**, so that its width is comparable over time.
- You prefer a measure of volatility that **includes gaps** and the full size of bars.
- You compare it with Bollinger Bands to see **which kind of volatility** is changing: scatter of closes or size of bars.

## Avoid when

- You want the envelope to **react quickly** to a sudden move. Bollinger Bands do that better.
- You compare **charts from different tools** without checking their settings.
- You treat a **close outside the channel** as a reversal signal. In a trend it is a sign of strength.

## Settings and tuning

- **20 / 10 / 2** is a common modern default: a 20-bar EMA, a 10-bar ATR and a multiplier of 2.
- **Larger multiplier:** a wider channel and fewer excursions.
- **Longer ATR length:** a steadier width.
- **Shorter average length:** the middle line hugs price more closely.

## Implementation variations

- **Middle line.** Some versions use a simple average, or an average of the typical price, in place of an EMA of the close.
- **ATR length and multiplier.** Common choices vary from tool to tool. A multiplier of 1.5 is also common.
- **History.** The original version is usually credited to Chester Keltner, who used a 10-day average of the typical price and the average daily range. The ATR-and-EMA version used today is usually credited to a later trader, Linda Raschke. I have not been able to confirm these details.

## Is it useful?

**Situational.** It is a sensible envelope, and it differs from Bollinger Bands in a real way: its width follows bar size and not the scatter of closes, so it is steadier. On the sample data, Keltner's width varied far less than Bollinger's (a standard deviation of 1.3 percentage points of price, against 6.2). But the two are not independent, with a width correlation of 0.68, so using both mostly gives you two views of the same thing. If you already use Bollinger Bands, adding Keltner is useful mainly for the comparison between them.

## Pairs well with / See also

- [Bollinger Bands](../bollinger-bands/): the same idea with a different width. Chart both to see the difference.
- [Average True Range](../average-true-range/): the source of the channel's width.
- [Exponential Moving Average](../exponential-moving-average/): the middle line.
- [Donchian Channels](../donchian-channels/): an envelope from the extremes and not from volatility.
