---
title: Connors RSI
aliases: [CRSI]
category: momentum
summary: The average of three short-term measures, a very short RSI, an RSI of how many days in a row price has gone up or down, and the percentile rank of today's change. It is built for short-term pullbacks, not trends.
display: panel
inputs:
  - { name: price RSI length, default: 3 }
  - { name: streak RSI length, default: 2 }
  - { name: rank window, default: 100 }
verdict: situational
status: draft
related: [relative-strength-index, stochastic-rsi, relative-momentum-index]
overlaps:
  - with: relative-strength-index
    strength: partial
    corr: 0.85
    note: "One third of Connors RSI is a 3-bar RSI. The correlation is between Connors RSI and a 3-bar RSI, not the usual 14-bar one."
---

> **In plain English.** Three questions, averaged. How strongly has price gone up lately, counting only the last 3 bars? How many days in a row has it gone up or down, and how unusual is that streak? How big was today's move compared with the last 100? The average is a number from 0 to 100. Very low means a sharp short-term drop, very high a sharp short-term jump.
>
> **Good for:** short-term pullback and bounce ideas over days, not weeks.
>
> **Watch out for:** how rarely it reaches its extremes, and how little it has to do with the usual 14-bar RSI. On the sample it reached below 10 on 4% of bars and above 90 on 1%.

## What it measures

How stretched price is over the last few days, in three ways at once: the size of recent gains and losses, the length of the current up or down streak, and how big today's change is by comparison with history.

## Calculation

$$
\text{CRSI}_t = \frac{\text{RSI}_3(P)_t + \text{RSI}_2(\text{streak})_t + \text{PercentRank}_{100}(\text{ROC}_1)_t}{3}
$$

- **RSI of price.** An ordinary RSI with length 3.
- **The streak.** The count of consecutive up closes (+1, +2, ...) or down closes (-1, -2, ...), restarting at zero on an unchanged close. An RSI of length 2 is taken of this count.
- **Percent rank.** Of the previous 100 one-bar percentage changes, the share (0 to 100) that were smaller than today's.

**Worked example.** If the 3-bar RSI is 20, the streak RSI is 10 and today's change is bigger than 60 of the last 100 changes, then the average is:

$$
\frac{20 + 10 + 60}{3} = 30
$$

**Warm-up.** The rank needs 100 prior changes, so the first value appears on bar 101.

```python
def connors_rsi(close, rsi_n=3, streak_n=2, rank_n=100):
    streak = [0.0]
    for change in close.diff().iloc[1:]:
        if change > 0:
            streak.append(streak[-1] + 1 if streak[-1] > 0 else 1.0)
        elif change < 0:
            streak.append(streak[-1] - 1 if streak[-1] < 0 else -1.0)
        else:
            streak.append(0.0)
    streak = pd.Series(streak, index=close.index)
    daily = close.pct_change()
    rank = daily.rolling(rank_n + 1).apply(lambda w: 100 * (w[:-1] < w[-1]).mean(), raw=True)
    return (rsi(close, rsi_n) + rsi(streak, streak_n) + rank) / 3
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/connors-rsi-dark.svg">
<img src="../../charts/connors-rsi-light.svg" alt="Price above, and Connors RSI below, with lines at 10 and 90" width="840" height="590">
</picture>
<figcaption>Synthetic data. Connors RSI needs 101 bars before its first value. After that it was below 10 on 4% of bars and above 90 on 1%. At the price low (bar 249) it read 25.2.</figcaption>
</figure>

- **Below 10** and **above 90** are the commonly used extremes for oversold and overbought, in the short term.
- **Mid-range** readings mean little: it is a fast, jumpy line.
- **It is not a trend indicator.** It looks at a few days.

What it does not tell you: whether the move will keep going. Its usual use is the opposite assumption, that short-term extremes revert. This page has not tested that.

## Best used when

- You look for **short-term mean reversion** over a few days, usually in liquid stocks and indexes.
- You like a **combined** short-term read instead of one input.

## Avoid when

- The market is **trending hard** or **gapping**. Extremes can persist.
- You want **long-term** information: it has none.
- You have **fewer than about 100 bars** of history.

## Settings and tuning

- **3, 2 and 100** are the standard values.
- **A shorter rank window** makes the third piece jumpier. **A longer one** makes it steadier.
- **Thresholds** vary: 10 and 90, 5 and 95, and 15 and 85 all appear.

## Implementation variations

- **Percent rank.** Some tools use "less than or equal to", this page uses "less than". It matters only for ties.
- **Streak.** The treatment of an unchanged close varies.
- **Rank input.** A few tools rank the point change instead of the percentage change.
- **History.** It is usually credited to Larry Connors, of Connors Research, from the 2010s. I have not confirmed the details.

## Is it useful?

**Situational.** It is a well-defined short-term gauge, and its three parts are sensible. On the sample it correlated 0.85 with a 3-bar RSI and only 0.44 with the usual 14-bar RSI, so it reads like a fast RSI, not a stronger one. At the price low (bar 249) it read 25.2, short of its usual extreme of 10. Whether its extremes lead to profitable reversals depends on the market and the period, and this site's synthetic data cannot tell you. Treat it as a short-term stretch gauge and test it on your own markets.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): the first ingredient.
- [Stochastic RSI](../stochastic-rsi/): another sensitive variation built on RSI.
- [Relative Momentum Index](../relative-momentum-index/): RSI with a longer step.
