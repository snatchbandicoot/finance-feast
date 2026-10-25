---
title: Relative Momentum Index
aliases: [RMI]
category: momentum
summary: RSI with one change. Instead of comparing each bar with the one before, it compares each bar with the one several bars ago. The result is more responsive, and reaches overbought and oversold levels more often.
display: panel
inputs:
  - { name: length, default: 14 }
  - { name: momentum, default: 5 }
verdict: redundant
status: draft
related: [relative-strength-index, chande-momentum-oscillator, stochastic-rsi]
overlaps:
  - with: relative-strength-index
    strength: partial
    corr: 0.90
    note: "The RMI is RSI with a longer momentum step. With a step of 1 bar the two are identical. The correlation is for a 5-bar step."
---

> **In plain English.** RSI looks at how much price rose or fell from one bar to the next. The Relative Momentum Index looks at how much price rose or fell compared with *several* bars back (5 by default). That makes the gains and losses bigger and smoother, and pushes the line into the overbought and oversold zones more often.
>
> **Good for:** an RSI-style gauge with an extra dial for how far back to compare.
>
> **Watch out for:** the standard levels. On the sample the RMI was above 70 on 24% of bars, where RSI was above 70 on 6%, so 70 and 30 mean less than they do on RSI.

## What it measures

The balance of up-moves against down-moves, where each move is measured over a longer step than one bar. Like RSI, it is a share, between 0 and 100.

## Calculation

With momentum step $k$ and length $N$, let $\Delta_t = P_t - P_{t-k}$. Smooth the up-moves and down-moves with Wilder's average (an exponential average with $\alpha = 1/N$) and take the ratio:

$$
\text{RMI}_t = 100 - \frac{100}{1 + \text{avg gain}_t / \text{avg loss}_t}
$$

where the gains are $\max(\Delta, 0)$ and the losses are $\max(-\Delta, 0)$.

**An exact identity.** With $k = 1$, this is [RSI](../relative-strength-index/), the same numbers to the last digit. The check script confirms it. A longer step is the only difference.

**Worked example.** With $k = 5$, if price is now 105 and was 100 five bars ago, the bar contributes a gain of 5 (and a loss of 0). With RSI the same bar would contribute only the change from yesterday.

```python
def rmi(close, n=14, momentum=5):
    delta = close.diff(momentum)
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + avg_gain / avg_loss)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/relative-momentum-index-dark.svg">
<img src="../../charts/relative-momentum-index-light.svg" alt="Price above, and the Relative Momentum Index and RSI below, with lines at 30 and 70" width="840" height="590">
</picture>
<figcaption>Synthetic data. The RMI (pink) was above 70 on 24% of scored bars and below 30 on 14%, against 6% and 8% for RSI (teal). At the price low (bar 249) it read 5.4 and RSI read 17.4.</figcaption>
</figure>

- **Overbought and oversold.** Above 70 and below 30 are the usual levels, but this line reaches them more often than RSI does.
- **The 50 line.** Above 50 means recent gains outweigh recent losses, as for RSI.
- **Divergence.** The usual RSI caution applies.

What it does not tell you: why the step matters. It is another tuning dial, and it changes how often the thresholds trigger.

## Best used when

- You like RSI but want to **tune its responsiveness**.
- You want a line that **ignores one-bar noise**.

## Avoid when

- You can get what you need from **RSI** with a different length.
- You rely on the **same 30 and 70** you use for RSI. They do not carry over.

## Settings and tuning

- **14 and 5** are common defaults.
- **A step of 1** gives RSI exactly.
- **A longer step** produces larger swings and more time near the extremes.

## Implementation variations

- **Smoothing.** Wilder's average is standard. Some tools use a simple average.
- **Name.** Some tools label the step "momentum" and some "lookback".
- **History.** It is usually credited to Roger Altman, in the 1990s. I have not confirmed the details.

## Is it useful?

**Redundant.** It is a harmless variation on RSI, and it has one clean property: with a 1-bar step it is RSI exactly. At the default step of 5 the sample's RMI correlated 0.90 with RSI. At the price low (bar 249) the RMI read 5.4, against 17.4 for RSI, which is more extreme and no more informative. You can get most of the same effect by changing RSI's length. Keep RSI unless you have a reason to use the extra dial.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): the 1-bar version.
- [Chande Momentum Oscillator](../chande-momentum-oscillator/): another relative of RSI.
- [Stochastic RSI](../stochastic-rsi/): another variation built on RSI.
