---
title: Rate of Change
aliases: [ROC, Price Rate of Change]
category: momentum
summary: How much price has changed over the last N bars, as a percentage.
display: panel
inputs:
  - { name: length, default: 12 }
verdict: situational
status: draft
related: [relative-strength-index, macd, simple-moving-average]
overlaps:
  - with: macd
    strength: partial
    corr: 0.71
    note: "Both measure momentum from price levels. ROC compares two prices, and MACD compares two smoothed averages."
---

> **In plain English.** How much price has changed over the last N bars, as a percentage. A reading of +5 means price is 5% higher than N bars ago, and −5 means it is 5% lower. It is about the simplest momentum measure there is: one number comparing now with then.
>
> **Good for:** seeing the pace of a move and whether it is speeding up or slowing, and comparing the pace across instruments, since it is a percentage.
>
> **Watch out for:** the fact that it compares only two prices, today's and the one N bars ago. When a big bar leaves the window, ROC can jump even though nothing happened today.

## What it measures

Momentum in its plainest form: the change in price over a fixed look-back, expressed relative to the starting price. Positive means price is higher than it was, and negative means lower. It is not smoothed, so it responds to a new price at once, and it also reacts to the old price dropping out of the window.

## Calculation

$$
ROC_t = 100 \times \left( \frac{P_t}{P_{t-N}} - 1 \right)
$$

$P_t$ is the close and $N$ is the length.

**Worked example.** With $N = 12$, a close of 11.5 and a close of 10.0 twelve bars earlier: $ROC = 100 \times (11.5/10.0 - 1) = +15$.

```python
def roc(close, n=12):
    return 100 * (close / close.shift(n) - 1)
```

The first $N$ bars have no value, because there is no price $N$ bars earlier.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/rate-of-change-dark.svg">
<img src="../../charts/rate-of-change-light.svg" alt="Price above, and 12-bar rate of change below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. ROC bottomed at -20.8% at bar 244, five bars before price did. It was above zero on 74% of uptrend bars but only 14% of selloff bars, and it crossed zero 16 times in the 100-bar range.</figcaption>
</figure>

- **Above or below zero.** Above zero, price is higher than $N$ bars ago. This is the plainest reading, and the one most worth trusting.
- **Direction of ROC itself.** A rising ROC means the pace of gains is picking up, and a falling ROC means it is easing, even if it is still positive.
- **Extremes.** A very high or very low reading compared with the study's own history means the move has been unusually fast. That is context. It is not a reversal signal.
- **The drop-off effect.** ROC compares only two bars. When an unusually large bar leaves the window, ROC can fall sharply even if the latest price barely moved. Check what left the window before reading a sudden change as meaningful.

What it does not tell you: what happens next, or anything about the path price took between the two bars.

## Best used when

- You want a **plain, explainable** measure of pace.
- You compare **several instruments** on the same footing, as a percentage.
- You want a simple **momentum filter**, for example "only look at longs where ROC is above zero".

## Avoid when

- You want something **smooth**. It is noisy by construction.
- You read a **sudden jump** without checking the drop-off effect.
- You use a **very short length** (such as 2 to 3). It then mostly measures the last bar or two.

## Settings and tuning

- **Length 12** is a common default. Some platforms use 10 or 14, and 125 (about six months of daily bars) is used for longer-term ranking.
- **Shorter:** more sensitive and noisier.
- **Longer:** smoother and slower, and the drop-off effect jumps less often but at longer intervals.

## Implementation variations

- **Percent, ratio or difference.** This page uses the percentage change. Some tools use the plain ratio $P_t/P_{t-N}$, centred on 1, and others use the plain difference $P_t - P_{t-N}$, often called *Momentum*. The shape is similar, but the scale differs, and the plain difference is not comparable across instruments.
- **Naming.** "ROC" and "Momentum" are used for different formulas by different platforms.

## Is it useful?

**Situational.** It is transparent and easy to reason about, and it has no smoothing lag. That makes it a good teaching tool and a reasonable simple filter. But it overlaps heavily with other momentum studies: on the sample data it correlated at 0.71 with the MACD line and 0.84 with RSI. The raw ROC is also noisy, with 16 zero crossings in the 100-bar range alone. Treat it as a quick pace gauge and not a signal source.

## Pairs well with / See also

- [Relative Strength Index](../relative-strength-index/): momentum from gains and losses, which smooths out the two-price sensitivity of ROC.
- [MACD](../macd/): momentum from moving averages, which smooths the same idea.
- [Simple Moving Average](../simple-moving-average/): the slower trend line that ROC's zero line is often compared with.
