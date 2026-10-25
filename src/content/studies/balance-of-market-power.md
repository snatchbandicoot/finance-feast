---
title: Balance of Market Power
aliases: [BMP, Balance of Power, BOP]
category: volume
summary: Measures, for each bar, how much of its range the body covered, positive when the close was above the open and negative when below, then smooths it. It estimates whether buyers or sellers won each bar, without using volume.
display: panel
inputs:
  - { name: smoothing length, default: 14 }
verdict: situational
status: draft
related: [chaikin-money-flow, accumulation-distribution, relative-strength-index]
overlaps:
  - with: chaikin-money-flow
    strength: partial
    corr: 0.76
    note: "Both judge each bar by where it closed. The Balance of Market Power compares the close with the open, and CMF compares it with the bar's range, with volume as a weight. The correlation is between the two lines."
---

> **In plain English.** Each bar has a body (open to close) and a full range (high to low). If the close is well above the open, buyers dominated that bar, and if it is well below, sellers did. Divide the body by the range and you get a score between -1 and +1 for each bar. Average the last 14 and you have the Balance of Market Power. Despite the "market power" name, it uses no volume.
>
> **Good for:** a quick read on whether bars have mostly been closing in the direction of buyers or of sellers.
>
> **Watch out for:** its dependence on the open. In markets with big overnight gaps, the open is far from the previous close, and a bar can show strong buying that is really just recovering from a gap down.

## What it measures

The average share of each bar's range that was covered in the direction of the close, from the open.

## Calculation

$$
\text{BMP}_t = \text{SMA}_{14}\!\left(\frac{C_t - O_t}{H_t - L_t}\right)
$$

**Worked example.** A bar opens at 10, reaches a high of 12 and a low of 9, and closes at 11.5. The body is $11.5 - 10 = 1.5$, the range is $12 - 9 = 3$, so the score is $1.5/3 = +0.5$. A bar that opens at its low and closes at its high scores +1. A bar that opens and closes at the same price scores 0, whatever its range.

```python
def balance_of_market_power(open_, high, low, close, n=14):
    return ((close - open_) / (high - low).replace(0, np.nan)).rolling(n).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/balance-of-market-power-dark.svg">
<img src="../../charts/balance-of-market-power-light.svg" alt="Price above, and the 14-bar Balance of Market Power below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Balance of Market Power averaged +0.145 in the uptrend, -0.004 in the range, -0.122 in the selloff and +0.037 in the rebound. Its low of -0.453 came on bar 244, and it crossed zero 26 times.</figcaption>
</figure>

- **Above zero**: buyers have won more of the bars. **Below zero**: sellers have.
- **Zero crossings** are the usual signals. It crossed 26 times over the scored sample.
- **Extremes.** Beyond about ±0.3 is unusual in the sample.

What it does not tell you: how much volume was involved, or how far price moved from one bar to the next.

## Best used when

- You want a **volume-free** read of buying and selling pressure.
- Your market has **little gap risk**, so open-to-close is meaningful.

## Avoid when

- The market **gaps** a lot, or the open is an auction price that does not reflect the next session.
- You want a **volume-based** measure.

## Settings and tuning

- **14** is the usual smoothing.
- **Shorter** smoothing is jumpier.

## Implementation variations

- **Smoothing.** A simple average is used here, and some tools allow others.
- **Zero-range bars.** They are skipped, as the division is undefined.
- **Naming.** "Balance of Power" is the same indicator under another name.
- **History.** It is usually credited to Igor Livshin. I have not confirmed the details.

## Is it useful?

**Situational.** It is a plain and intuitive score for each bar. On the sample, it averaged +0.145 in the uptrend, -0.004 in the range, -0.122 in the selloff and +0.037 in the rebound, with its low of -0.453 on bar 244, and it correlated 0.76 with CMF. That agreement with a volume-based measure is a mild point in its favor, as it gets some of the same information without needing volume. But it sees only the open and close within a bar, and like all such averages, it lags. A reasonable extra view, with no particular edge.

## Pairs well with / See also

- [Chaikin Money Flow](../chaikin-money-flow/): a volume-weighted view of the close's position in the range.
- [Accumulation/Distribution Line](../accumulation-distribution/): the running-total version.
- [Relative Strength Index](../relative-strength-index/): another read of buying versus selling.
