---
title: Parabolic SAR
aliases: [SAR, PSAR, Stop and Reverse, Parabolic Stop and Reverse]
category: trend
summary: A trailing stop drawn as dots that sit below price in an uptrend and above it in a downtrend, and flip sides when price breaks through.
display: overlay
inputs:
  - { name: acceleration step, default: 0.02 }
  - { name: maximum acceleration, default: 0.2 }
verdict: situational
status: draft
related: [average-directional-index, average-true-range, simple-moving-average]
---

> **In plain English.** A trailing stop, drawn as a row of dots. In an uptrend the dots sit below price and creep upward, moving faster each time price makes a new high. When price falls through the dots, the study flips: the dots jump to the other side of price and start trailing it downward. It is always either long or short and never says "stay out".
>
> **Good for:** setting a trailing stop that tightens as a trend ages.
>
> **Watch out for:** sideways or choppy markets, where it flips back and forth. On this site's sample data it reversed about once every 9 bars in every kind of market.

## What it measures

Where a trailing stop should sit if you are following a trend. It tracks the most extreme price reached since the trend began, and moves the stop toward that extreme at an increasing rate. When price touches the stop, the trend is declared over and the study reverses to the other side.

## Calculation

In an uptrend, let $EP$ (the *extreme point*) be the highest high since the trend began, and $AF$ (the *acceleration factor*) start at 0.02. Each new bar:

$$
SAR_t = SAR_{t-1} + AF \cdot (EP - SAR_{t-1})
$$

- Each time a new extreme point is set, $AF$ increases by 0.02, up to a maximum of 0.2.
- The SAR is never allowed above the lows of the previous two bars.
- If the bar's low falls below the SAR, the trend reverses. The new SAR is the old $EP$, the new $EP$ is the extreme of the new trend (this bar's low), and $AF$ resets to 0.02.

A downtrend is the mirror image.

**Worked example.** Six bars, with SAR starting at the first low:

| Bar | High | Low | SAR | What happens |
|-----|------|-----|-----|--------------|
| 0 | 10 | 8 | 8 | start (uptrend), $EP = 10$, $AF = 0.02$ |
| 1 | 11 | 9 | 8 | raw $8.04$ is held down to the prior low of 8. New high: $EP = 11$, $AF = 0.04$ |
| 2 | 12 | 10 | 8 | raw $8.12$ is held down to 8. $EP = 12$, $AF = 0.06$ |
| 3 | 13 | 11 | 8.24 | $8 + 0.06 \times (12 - 8)$. $EP = 13$, $AF = 0.08$ |
| 4 | 14 | 12 | 8.6208 | $8.24 + 0.08 \times (13 - 8.24)$. $EP = 14$, $AF = 0.10$ |
| 5 | 13 | 7 | 14 | raw $9.159$, but the low of 7 is below it, so it **reverses**. SAR becomes the old $EP$ of 14 |

```python
def psar(high, low, step=0.02, step_max=0.2):
    h, l = high.to_numpy(), low.to_numpy()
    n = len(h)
    sar = np.empty(n)
    uptrend = h[1] >= h[0]
    ep = h[0] if uptrend else l[0]
    sar[0] = l[0] if uptrend else h[0]
    af = step
    for i in range(1, n):
        sar[i] = sar[i - 1] + af * (ep - sar[i - 1])
        if uptrend:
            sar[i] = min(sar[i], l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            if l[i] < sar[i]:
                uptrend, sar[i], ep, af = False, ep, l[i], step
            elif h[i] > ep:
                ep, af = h[i], min(af + step, step_max)
        else:
            sar[i] = max(sar[i], h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            if h[i] > sar[i]:
                uptrend, sar[i], ep, af = True, ep, h[i], step
            elif l[i] < ep:
                ep, af = l[i], min(af + step, step_max)
    return pd.Series(sar, index=high.index)
```

The first two bars decide the starting direction (`uptrend = h[1] >= h[0]`), which is an arbitrary rule. The first few values are therefore a guess, and different tools guess differently.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/parabolic-sar-dark.svg">
<img src="../../charts/parabolic-sar-light.svg" alt="Price with Parabolic SAR dots across four regimes" width="840" height="430">
</picture>
<figcaption>Synthetic data. The SAR reversed 11 times in the 100-bar uptrend and 10 times in the 100-bar range, about once every 9 bars on average in every regime. Around the top of the selloff it flipped six times in 34 bars (bars 198 to 232) before it stayed short, and it turned long again at bar 253, four bars after the price low.</figcaption>
</figure>

- **Dots below price** mean the study is long, and **dots above** mean it is short.
- **A flip** is the signal: price has broken through the stop.
- **Distance from price** is the current stop distance. It shrinks as a trend keeps making new extremes, because each one raises $AF$ toward its cap. A trend that stalls stops tightening.
- **As a stop.** If you hold a position in the trend's direction, the SAR is a stop that never loosens.

What it does not tell you: whether the market is trending at all. It follows price whichever way it is going, and flips as soon as price pulls back far enough.

## Best used when

- Price is **trending smoothly**, with shallow pullbacks that do not reach the dots.
- You want a **mechanical trailing stop** for a position you already hold.
- You pair it with a **trend filter** such as [ADX](../average-directional-index/), so you only act on its flips when a trend is present.

## Avoid when

- Price is **choppy**. The dots are hit again and again, and each flip is a small loss or a missed continuation.
- You use it as a **standalone system**. Because it always holds a position, it never sits out the sideways stretches.
- Price **gaps through** the dot. The reversal happens at the extreme point, not at the gap price, so the real exit can be much worse than the dot suggests.

## Settings and tuning

- **0.02 and 0.2** are Wilder's defaults.
- **A larger step** (such as 0.03): the stop tightens faster, so it keeps more profit and flips more often.
- **A smaller step** (such as 0.01): a looser stop that gives price more room and flips less often.
- **The maximum** caps how tight the stop can get. A lower cap leaves more room at the end of a long trend.

## Implementation variations

- **Initial direction.** Tools pick the starting trend differently, so the first dozen values may not match.
- **Reversal bar.** Here the SAR on the reversal bar is the old extreme point. Some tools plot the new SAR on the following bar instead, shifting every dot by one bar.
- **Two-bar clamp.** The rule that holds the SAR back to the prior two lows (or highs) is not applied the same way everywhere.

## Is it useful?

**Situational.** As a trailing stop for a trend you are already in, it is a reasonable mechanical rule, and it tightens in a way ATR-based stops do not: the SAR closes in each time price makes a new extreme, regardless of volatility. As a trading system by itself it is poor, because it has no way to tell a trend from noise. The sample data makes that plain: 11 reversals in the uptrend and 10 in the range.

## Pairs well with / See also

- [Average Directional Index](../average-directional-index/): says whether there is a trend, which is the question the SAR cannot answer.
- [Average True Range](../average-true-range/): a stop that stays a fixed number of typical ranges away, in place of one that tightens as the trend extends.
- [Simple Moving Average](../simple-moving-average/): a slower, smoother way to follow the same trend.
