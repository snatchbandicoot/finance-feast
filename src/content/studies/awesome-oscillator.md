---
title: Awesome Oscillator
aliases: [AO, Bill Williams Awesome Oscillator]
category: momentum
summary: The difference between a fast and a slow simple moving average of each bar's midpoint, drawn as bars that change color when the value rises or falls.
display: panel
inputs:
  - { name: fast length, default: 5 }
  - { name: slow length, default: 34 }
verdict: redundant
status: draft
related: [macd, percentage-price-oscillator, simple-moving-average]
---

> **In plain English.** Take the midpoint of each bar (halfway between its high and low), average the last 5 of them and the last 34 of them, and subtract the slow average from the fast one. Above zero, recent bars have been higher than the longer-term average, and below zero, lower. The bars are colored by whether the value rose or fell from the previous bar. It is usually credited to Bill Williams.
>
> **Good for:** a simple read on momentum, and on whether it is building or fading.
>
> **Watch out for:** thinking it is different from MACD. It is the same idea, a fast average minus a slow one, built with simple averages on the midpoint. On this site's sample data it moved almost exactly with the MACD line (correlation 0.98).

## What it measures

The gap between a short-term and a long-term average of the bars' midpoints. When price has been rising, the fast average sits above the slow one and the gap is positive. When the gap grows, momentum is building, and when it shrinks, momentum is fading, even if it is still positive.

Because it is built from price levels, it is in **price units**. A reading of 5 means something very different on a stock priced at 20 and one priced at 2,000.

## Calculation

With the midpoint $M_t = (H_t + L_t)/2$:

$$ \text{AO}_t = \text{SMA}_5(M)_t - \text{SMA}_{34}(M)_t $$

**Worked example.** With shortened settings of 2 and 4 bars, four bars have midpoints of 9, 11, 13, 12. The fast average of the last two is $(13 + 12)/2 = 12.5$. The slow average of all four is $(9 + 11 + 13 + 12)/4 = 11.25$. So $\text{AO} = 12.5 - 11.25 = 1.25$.

```python
def awesome(high, low, fast=5, slow=34):
    median = (high + low) / 2
    return median.rolling(fast).mean() - median.rolling(slow).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/awesome-oscillator-dark.svg">
<img src="../../charts/awesome-oscillator-light.svg" alt="Price above, and the Awesome Oscillator as bars below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The oscillator was above zero on 88% of uptrend bars and only 8% of selloff bars. It reached its low of -17.7 at bar 247, two bars before the price low, and it crossed zero only 3 times in the 100-bar range. Pink bars are higher than the previous bar, and teal bars are lower.</figcaption>
</figure>

- **Above or below zero.** Above zero, the fast average is above the slow one. This is the plain reading.
- **Bar color.** Each bar is colored by whether the value is higher or lower than the previous bar. It shows the *change*, not the sign, so a negative bar can still be "rising".
- **Zero-line crossing** is the same event as a crossover of the two averages.
- **Named patterns.** Williams described setups such as the "saucer" (the value changing direction while it stays on one side of zero) and "twin peaks". They are interpretations of the shape, and I have not tested them.

What it does not tell you: how large the move is relative to the instrument's price, or what happens next.

## Best used when

- You want a **momentum** readout from the *midpoint* of bars, which includes the high and low, not only the close.
- You prefer **simple** averages to exponential ones.

## Avoid when

- You already use **MACD**. It is nearly the same line.
- You **compare instruments** or look at a long history over which the price level changed a lot. The values are in price units. See the [Percentage Price Oscillator](../percentage-price-oscillator/).
- Price is **sideways**. The line hovers near zero and wanders across it.

## Settings and tuning

- **5 and 34** are the standard settings.
- **Shorter lengths** make it react faster and cross zero more often.
- **Longer lengths** make it smoother and later.
- The two lengths set how far apart the "fast" and "slow" views are. Widening the gap makes the line larger and slower.

## Implementation variations

- **Midpoint or close.** The standard version uses the midpoint of each bar. Some tools allow the close.
- **Coloring.** The rise-or-fall coloring is the usual convention. Some tools color by sign instead.
- **Average type.** Simple averages are standard. An exponential version is effectively a MACD.

## Is it useful?

**Redundant.** It is the difference of two simple moving averages, which is what MACD is, apart from using exponential averages. On the sample data it correlated 0.98 with the MACD line, and 0.998 with the plain difference between a 5-bar and a 34-bar average of the close. The midpoint adds a little, and the rise-or-fall coloring is a nice display, but neither is new information. If you use MACD, you can skip this. If you prefer simple averages and the bar-color display, it is a fair alternative.

## Pairs well with / See also

- [MACD](../macd/): the same idea with exponential averages.
- [Percentage Price Oscillator](../percentage-price-oscillator/): the same idea as a percentage, which makes it comparable across instruments.
- [Simple Moving Average](../simple-moving-average/): the two averages inside it.
