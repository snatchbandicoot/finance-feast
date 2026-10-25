---
title: Price Zone Oscillator
aliases: [PZO]
category: momentum
summary: An oscillator that adds today's close when price rose and subtracts it when price fell, smooths that, and expresses it as a share of the smoothed close. It reads as a measure of how one-sided the recent moves have been.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: situational
status: draft
related: [relative-strength-index, disparity-index, money-flow-index]
overlaps:
  - with: relative-strength-index
    strength: partial
    corr: 0.73
    note: "Both measure how one-sided recent up and down moves have been. The Price Zone Oscillator counts only the direction of each move and not its size. The correlation is between the two lines."
---

> **In plain English.** Each day, look only at the direction: did price close up or down? If up, take the close as a positive number, and if down, a negative one. Smooth these, and divide by the smoothed close. The result is near +100 when nearly every day closed up, near -100 when nearly every day closed down, and near zero when ups and downs balance. Size of the move does not matter, only the direction.
>
> **Good for:** a direction-counting oscillator that is not thrown off by one huge day.
>
> **Watch out for:** its odd scale. It rarely reaches the ±100 ends, and the usual levels (±40, ±60) come from convention.

## What it measures

The balance of up-days and down-days, weighted slightly by price level, smoothed. A single large move counts no more than a small one.

## Calculation

$$
\text{signed}_t = \begin{cases} +P_t & \text{if } P_t > P_{t-1} \\ -P_t & \text{otherwise} \end{cases} \qquad \text{PZO}_t = 100 \times \frac{\text{EMA}_N(\text{signed})_t}{\text{EMA}_N(P)_t}
$$

**Worked example.** Suppose the smoothed signed close is 2 and the smoothed close is 10:

$$
100 \times \frac{2}{10} = +20
$$

With a length of 1 the smoothing disappears, and the oscillator is exactly +100 on an up-day and -100 on a down-day. The check script confirms this.

```python
def price_zone_oscillator(close, n=14):
    signed = close.where(close.diff() > 0, -close).where(close.diff().notna())
    return 100 * signed.ewm(span=n, adjust=False).mean() / close.ewm(span=n, adjust=False).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/price-zone-oscillator-dark.svg">
<img src="../../charts/price-zone-oscillator-light.svg" alt="Price above, and the Price Zone Oscillator below with lines at -40, 0 and 40" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Price Zone Oscillator ranged from -76.3 to +71.3, and was above +40 on 7% of scored bars and below -40 on 7%. At the price low (bar 249) it read -38.2.</figcaption>
</figure>

- **Above zero**: up-days have been outnumbering down-days. **Below zero**: the reverse.
- **±40** are commonly used to mark a strong move, and **±60** an extreme. On the sample it was above +40 on 7% of scored bars and below -40 on 6.5%, and above +60 on only 1.5%.
- **Crossing zero** is the simplest signal, and it happens often.

What it does not tell you: how big the moves were. Twenty tiny up-days outrank one big down-day.

## Best used when

- You want a **direction count** that ignores the size of moves.
- Outlier days (news, gaps) distort your other oscillators.

## Avoid when

- Size matters to you, as in momentum or volatility work.
- You need a **bounded** range with fixed overbought and oversold levels.

## Settings and tuning

- **14** is the usual length. A shorter length is jumpier.
- **±40** and **±60** are conventions, not derived.

## Implementation variations

- **Unchanged closes.** This page counts a close equal to the previous one as a down-day. Some tools treat it as neutral.
- **Smoothing.** Exponential here.
- **History.** It is usually credited to Walid Khalil and David Steckler. I have not confirmed the details.

## Is it useful?

**Situational.** It offers something RSI does not: a pure count of direction, deaf to the size of moves. On the sample it was above zero on 78% of the uptrend's scored bars, 47% of the range's, 44% of the selloff's and 69% of the rebound's. Note the selloff figure: because it counts days and not points, a market can fall hard while still having many up-days, and the reading read -38.2 at the price low (bar 249), not an extreme. It correlated 0.73 with RSI. Treat it as a second opinion on RSI, particularly where single days can distort the picture.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): the size-sensitive version of the same idea.
- [Disparity Index](../disparity-index/): distance from an average.
- [Money Flow Index](../money-flow-index/): another up-versus-down measure, with volume.
