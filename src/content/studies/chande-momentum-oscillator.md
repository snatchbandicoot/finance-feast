---
title: Chande Momentum Oscillator
aliases: [CMO, Chande Momentum]
category: momentum
summary: The balance of up-moves against down-moves over the last N bars, on a scale from minus 100 to plus 100.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: redundant
status: draft
related: [relative-strength-index, rate-of-change, stochastic-oscillator]
---

> **In plain English.** Add up all the up-moves over the last N bars, add up all the down-moves, and ask how much bigger one total is than the other. If every move was up, the reading is +100. If every move was down, it is −100. Zero means up and down were equal. It is the RSI idea on a symmetric scale, with no smoothing, usually credited to Tushar Chande.
>
> **Good for:** seeing the balance of up and down movement on a scale centered on zero.
>
> **Watch out for:** treating it as different from RSI. It is *exactly* RSI's unsmoothed cousin, rescaled. On this site's sample it correlated 0.85 with the standard RSI.

## What it measures

Of all the price movement in the last $N$ bars, how much was upward and how much was downward? It looks at the *total distance* travelled up against the total distance travelled down, ignoring the order.

## Calculation

Let $SU$ be the sum of all up-moves (the positive close-to-close changes) over the last $N$ bars, and $SD$ the sum of the sizes of all down-moves:

$$ \text{CMO}_t = 100 \times \frac{SU - SD}{SU + SD} $$

**Worked example.** Closes of 10, 12, 11, 14, 12 give four changes: +2, −1, +3, −2. With $N = 4$: $SU = 2 + 3 = 5$ and $SD = 1 + 2 = 3$. Then $\text{CMO} = 100 \times (5 - 3)/(5 + 3) = 25$.

**The link to RSI.** The RSI page mentions a version that uses plain sums in place of Wilder's smoothing, sometimes called Cutler's RSI. That version is $100 \times SU/(SU + SD)$, which is 62.5 for the example above. And:

$$ \text{CMO} = 2 \times \text{Cutler's RSI} - 100 $$

For the example, $2 \times 62.5 - 100 = 25$. The check script confirms this identity over hundreds of bars.

```python
def cmo(close, n=14):
    change = close.diff()
    up = change.clip(lower=0).rolling(n).sum()
    down = (-change).clip(lower=0).rolling(n).sum()
    return 100 * (up - down) / (up + down)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/chande-momentum-oscillator-dark.svg">
<img src="../../charts/chande-momentum-oscillator-light.svg" alt="Price above, and the Chande Momentum Oscillator below with lines at -50 and +50" width="840" height="590">
</picture>
<figcaption>Synthetic data. CMO was above +50 on 21% of uptrend bars and below -50 on 28% of selloff bars, with a low of -89.5 at bar 244, five bars before the price low. It moves with RSI (correlation 0.85) and is exactly Cutler's RSI rescaled.</figcaption>
</figure>

- **Above zero**, up-moves have outweighed down-moves, and below zero, the reverse.
- **The plus and minus 50 lines** are commonly used as overbought and oversold levels, on this scale. They carry the same caution as RSI's 70 and 30: an extreme reading in a trend is not a reversal signal.
- **Divergence.** As with other oscillators, it appears often and fails often.

What it does not tell you: when a move ends.

## Best used when

- You prefer a scale **centered on zero**, with equal room above and below.
- You want the **unsmoothed** balance of movement over a fixed window.

## Avoid when

- You **already use RSI**. It carries the same information.
- You want a **smooth** line. Because there is no smoothing, the oldest bar leaving the window can make the reading jump.
- Price is **trending strongly**. It can sit beyond ±50 for a long time.

## Settings and tuning

- **Length 14** is used here. 9 and 20 are also seen.
- **Shorter:** more sensitive and more extremes.
- **Longer:** smoother, and rarely beyond ±50.

## Implementation variations

- **Smoothing.** Standard CMO uses plain sums, as above. Some tools smooth the sums in Wilder's way, which makes it $2 \times \text{Wilder's RSI} - 100$ instead. Check which one your tool uses before comparing values.
- **Scale.** The −100 to +100 scale is standard. Some tools show 0 to 100.

## Is it useful?

**Redundant.** It is Cutler's RSI with the scale shifted and stretched, so it adds no information to a chart that has RSI. The scale around zero is a matter of taste. The one real difference, no smoothing, is a mild disadvantage: the reading jumps when large old bars drop out of the window. Pick RSI, or CMO if you strongly prefer a symmetric scale, and do not use both.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): the same ingredients, usually smoothed.
- [Rate of Change](../rate-of-change/): another simple, unsmoothed look at momentum.
- [Stochastic Oscillator](../stochastic-oscillator/): momentum from position in the range instead.
