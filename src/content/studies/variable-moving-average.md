---
title: Variable Moving Average
aliases: [VMA, VIDYA, Variable Index Dynamic Average]
category: trend
summary: An exponential average whose speed depends on how directional the market has been. It speeds up when moves are one-sided and slows down when they are choppy.
display: overlay
inputs:
  - { name: length, default: 21 }
  - { name: momentum window, default: 9 }
verdict: situational
status: draft
related: [kaufman-adaptive-moving-average, exponential-moving-average, chande-momentum-oscillator]
overlaps:
  - with: exponential-moving-average
    strength: partial
    corr: 0.94
    note: "With a perfectly one-sided market it is the EMA of the same length. In choppy markets it slows down. The correlation is with the distance of price from a 21-bar EMA."
---

> **In plain English.** A moving average has a fixed speed, which is too slow in a trend and too fast in chop. The Variable Moving Average adjusts its own speed. It measures how one-sided the last 9 moves were (using the Chande Momentum Oscillator). When nearly all were in one direction, it moves like a normal 21-bar EMA. When ups and downs cancel, it nearly freezes.
>
> **Good for:** a line that stays out of the way in sideways markets, and follows when a trend appears.
>
> **Watch out for:** its slowness in the first bars of a trend. It cannot know a trend has started until moves have turned one-sided.

## What it measures

A smoothed price level whose responsiveness follows the market's directional strength.

## Calculation

Let $k_t = |\text{CMO}_9|/100$ be the absolute Chande Momentum Oscillator, between 0 (ups and downs cancel) and 1 (all moves one way). With $\alpha = 2/(N+1)$ ($N = 21$):

$$
\text{VMA}_t = \alpha\,k_t\,P_t + (1 - \alpha\,k_t)\,\text{VMA}_{t-1}
$$

The line starts at the first price where $k$ can be computed.

**Worked example.** With $\alpha = 2/22 = 0.0909$ and $k = 0.5$, the effective speed is $0.0909 \times 0.5 = 0.0455$. If the line is at 100 and price is 110, it moves $0.0455 \times 10 = 0.45$, to 100.45. With $k = 1$, it would move $0.91$, as a normal 21-bar EMA does.

**An exact identity.** In a perfectly steady move $k = 1$ throughout, so the line is the EMA of the same length. The check script confirms it on a straight climb.

```python
def variable_ma(close, n=21, cmo_n=9):
    change = close.diff()
    up = change.clip(lower=0).rolling(cmo_n).sum()
    down = (-change).clip(lower=0).rolling(cmo_n).sum()
    strength = ((up - down) / (up + down)).abs()
    alpha = 2 / (n + 1)
    out, prev = [], np.nan
    for price, k in zip(close, strength):
        if np.isnan(k):
            out.append(np.nan)
            continue
        prev = price if np.isnan(prev) else alpha * k * price + (1 - alpha * k) * prev
        out.append(prev)
    return pd.Series(out, index=close.index)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/variable-moving-average-dark.svg">
<img src="../../charts/variable-moving-average-light.svg" alt="Price with the variable moving average and a 21-bar EMA through a selloff and rebound" width="840" height="430">
</picture>
<figcaption>Synthetic data, zoomed to the end of the range, the selloff and the rebound. The variable average (pink) stays closer to price in the chop of the late range and falls more slowly in the selloff than the EMA (teal). It crossed price 3 times in the selloff, against 7 for the EMA.</figcaption>
</figure>

- **Slope and price against the line**, as for any average.
- **Flat stretches** mean the market has been choppy. The line is saying "no direction here".
- **Crossovers** are fewer in chop than with an EMA, which is the point.

What it does not tell you: whether a flat line is about to start a trend. The first bars of a new trend barely move it.

## Best used when

- You want an average that **ignores chop** and follows trends.
- You use averages for **trailing stops** and want fewer false exits in ranges.

## Avoid when

- You need **quick** entries. On a noisy test with a sudden 10-point jump, it took 12 bars to cover half the move, against 7 for a 21-bar EMA. The check script confirms it.
- You want a **predictable** speed, such as one you can compare to an EMA length.

## Settings and tuning

- **21 and 9** are common choices. The first sets the maximum speed, and the second how many bars judge the direction.
- **A shorter momentum window** makes the speed jumpier.

## Implementation variations

- **The strength measure.** Most versions use the absolute Chande Momentum Oscillator, as here. Some use another efficiency measure.
- **Seeding.** The line starts at the first price once the window is full. Early values depend on that.
- **History.** It is usually credited to Tushar Chande, as VIDYA. I have not confirmed the details.

## Is it useful?

**Situational.** It is a reasonable adaptive average, close in spirit to [Kaufman's](../kaufman-adaptive-moving-average/) (their distances from price correlated only 0.68 on the sample, so they behave differently). Against a 21-bar EMA it correlated 0.94 and was smoother. It crossed price 3 times in the selloff, against 7 for the EMA, and 14 times in the range against 18. The cost is that in the rebound it crossed 13 times, against 11, as it lingered below price. Adaptive averages cut whipsaws in chop and add delay at turns. Whether that trade suits you is the question.

## Pairs well with / See also

- [Kaufman Adaptive Moving Average](../kaufman-adaptive-moving-average/): the other well-known adaptive average.
- [Exponential Moving Average](../exponential-moving-average/): its fixed-speed parent.
- [Chande Momentum Oscillator](../chande-momentum-oscillator/): where the speed signal comes from.
