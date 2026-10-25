---
title: Ultimate Oscillator
aliases: [UO, Larry Williams Ultimate Oscillator]
category: momentum
summary: A 0 to 100 reading of buying pressure that blends a short, medium and long window so no single time scale dominates.
display: panel
inputs:
  - { name: short length, default: 7 }
  - { name: medium length, default: 14 }
  - { name: long length, default: 28 }
verdict: situational
status: draft
related: [relative-strength-index, stochastic-oscillator, average-true-range]
overlaps:
  - with: relative-strength-index
    strength: partial
    corr: 0.81
    note: "Both give a bounded momentum reading. The Ultimate Oscillator blends three windows and counts gaps."
---

> **In plain English.** For each bar, it measures how far the close finished *above the bar's low* (counting any gap from the previous close), as a share of the bar's full range. It does this over three windows (7, 14 and 28 bars) and blends the three, giving the shortest the most weight. The result runs from 0 to 100, with 50 as the midpoint. It is usually credited to Larry Williams, who wanted to cut down the false signals a single window gives.
>
> **Good for:** a bounded momentum reading that is less jumpy than a single-window oscillator and takes gaps into account.
>
> **Watch out for:** the 70 and 30 lines. They are reached only in the strongest stretches. In this site's sample, the reading never went above 74 or below 20, and it was below 30 on 28% of the selloff's bars but above 70 on only 8% of the uptrend's.

## What it measures

The balance of "buying pressure" over three time scales. Buying pressure for a bar is how far the close is above the lower of the bar's low and the previous close. The bar's *true range* is the span between the higher of the bar's high and the previous close, and that same lower level. Close near the top of the true range means strong buying pressure.

Using the previous close (not just the bar's own low) is what lets it see gaps, which an oscillator built only from close-to-close changes, or from the bar alone, would not.

## Calculation

$$
BP_t = C_t - \min(L_t, C_{t-1}) \qquad TR_t = \max(H_t, C_{t-1}) - \min(L_t, C_{t-1})
$$

For each window length $n$, add up buying pressure and true range and take the ratio:

$$
A_n = \frac{\sum_{i=0}^{n-1} BP_{t-i}}{\sum_{i=0}^{n-1} TR_{t-i}} \qquad \text{UO} = 100 \times \frac{4A_7 + 2A_{14} + A_{28}}{7}
$$

**Worked example.** One bar has a previous close of 11, a high of 12, a low of 10.5 and a close of 11.8. Then $BP = 11.8 - \min(10.5, 11) = 1.3$ and $TR = \max(12, 11) - 10.5 = 1.5$, so this bar's ratio is $1.3/1.5 \approx 0.87$.

If the three window ratios come out at $A_7 = 0.6$, $A_{14} = 0.5$ and $A_{28} = 0.4$, then $\text{UO} = 100 \times (4 \times 0.6 + 2 \times 0.5 + 0.4)/7 \approx 54.3$.

```python
def ultimate(high, low, close, short=7, mid=14, long=28):
    prev_close = close.shift()
    low_ref = pd.concat([low, prev_close], axis=1).min(axis=1)
    high_ref = pd.concat([high, prev_close], axis=1).max(axis=1)
    buying = close - low_ref
    true_range = high_ref - low_ref

    def average(n):
        return buying.rolling(n).sum() / true_range.rolling(n).sum()

    return 100 * (4 * average(short) + 2 * average(mid) + average(long)) / 7
```

Because buying pressure can never exceed the true range, the result always stays between 0 and 100. The check script confirms this.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/ultimate-oscillator-dark.svg">
<img src="../../charts/ultimate-oscillator-light.svg" alt="Price above, and the Ultimate Oscillator below with lines at 30 and 70" width="840" height="590">
</picture>
<figcaption>Synthetic data. The oscillator ranged only from 20.7 to 73.6. It was above 70 on 8% of uptrend bars and below 30 on 28% of selloff bars, and nearly never elsewhere. Its low came at bar 244, five bars before the price low.</figcaption>
</figure>

- **Around 50** is balanced. Above 50, buying pressure has had the better of it over the blended windows.
- **The 70 and 30 lines** are the conventional overbought and oversold levels. Because the blend smooths three windows, the readings stay in a narrower band than RSI's, so these lines are reached less often.
- **Divergence.** Williams' own signal rules are built on divergence between price and the oscillator, with extra conditions. I describe the idea only, and I have not tested his full rules.

What it does not tell you: how far a move will run. As with other bounded oscillators, an extreme reading in a strong trend is not a reversal signal.

## Best used when

- You want a bounded oscillator that **respects gaps**.
- You are tired of a single window giving **whipsaws** and want a blended view.

## Avoid when

- You expect **frequent extremes**. In the sample the UO spent only 8% of the uptrend above 70.
- You **already use RSI**. They are correlated 0.81 in the sample.
- You want a **simple** indicator that is easy to explain. This has three windows and fixed weights.

## Settings and tuning

- **7, 14 and 28** are the standard lengths, each double the last.
- **The 4:2:1 weights** are fixed in the standard version. They give the fastest window the most say. Many tools do not let you change them.
- **Shorter lengths** make the line more jumpy and more likely to reach the lines.

## Implementation variations

- **Weights.** 4, 2 and 1 are standard.
- **Gaps.** Some simplified versions leave out the previous close, using only the bar's own high, low and close. That makes them blind to gaps.
- **Sums or averages.** Using sums or averages of the pressure and range gives the same result, because the window length cancels in the ratio.

## Is it useful?

**Situational.** The design is thoughtful. It includes gaps, blends time scales, and stays bounded. But the blending also makes the line narrow-ranged, so the conventional levels rarely trigger, and its readings track RSI closely (0.81 correlation in the sample). The extra machinery buys a smoother line, not a new kind of information. If you find RSI too jumpy and want gaps counted, it is a reasonable alternative. If you already use RSI and the stochastic, it will not add much.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): the closest relative among bounded oscillators.
- [Stochastic Oscillator](../stochastic-oscillator/): also based on the position of the close within a range.
- [Average True Range](../average-true-range/): the true range used here is the same one.
