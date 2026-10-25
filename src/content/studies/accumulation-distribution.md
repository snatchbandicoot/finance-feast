---
title: Accumulation/Distribution Line
aliases: [A/D Line, ADL, Accumulation Distribution, A/D]
category: volume
summary: A running total that adds a share of each bar's volume when the close is in the upper part of its range and subtracts it when the close is in the lower part. It guesses at buying and selling pressure from where the bar closed.
display: panel
inputs: []
verdict: situational
status: draft
related: [on-balance-volume, chaikin-money-flow, chaikin-oscillator]
overlaps:
  - with: on-balance-volume
    strength: partial
    corr: 0.84
    note: "Both are running totals of signed volume. OBV signs the whole bar's volume by the close-to-close change, and the A/D line splits it by where the close sits in the bar's range. The correlation is between the 20-bar changes of the two."
  - with: chaikin-money-flow
    strength: identical
    note: "Chaikin Money Flow is exactly the 20-bar change in the A/D line divided by the 20-bar total volume."
---

> **In plain English.** Each bar, ask: where did it close, near the top of its range or near the bottom? A close at the top counts its volume as buying and adds it. A close at the bottom counts it as selling and subtracts it. A close in the middle adds nothing. The running total is the line. Rising means volume has been landing on strong closes.
>
> **Good for:** checking whether volume agrees with a price move, and spotting when it does not.
>
> **Watch out for:** its guesswork. It assumes that a close near the high means buyers took control, which is only a rough proxy, and it ignores gaps between bars.

## What it measures

The cumulative volume, weighted by where each close sits in its bar's high-low range. It is an estimate of money flowing into or out of the market, with all the roughness that implies.

## Calculation

$$
\text{position}_t = \frac{2C_t - H_t - L_t}{H_t - L_t}
$$

The numerator is the distance of the close above the low, minus its distance below the high: $(C - L) - (H - C)$.

$$
\text{ADL}_t = \text{ADL}_{t-1} + \text{position}_t \times V_t
$$

The position runs from +1 (close at the high) through 0 (close at the middle) to -1 (close at the low). A bar with no range (high equals low) counts as 0.

**Worked example.** A bar has a high of 12, a low of 8, a close of 11 and a volume of 1,000:

$$
\text{position} = \frac{22 - 12 - 8}{4} = 0.5
$$

The amount added to the line is 0.5 × 1000 = +500.

The check script confirms two limits: if every close is at the bar's high, the line equals the cumulative volume, and over any 20 bars the change in the line, divided by the 20-bar volume, is exactly [Chaikin Money Flow](../chaikin-money-flow/).

```python
def accumulation_distribution(high, low, close, volume):
    position = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    return (position.fillna(0) * volume).cumsum()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/accumulation-distribution-dark.svg">
<img src="../../charts/accumulation-distribution-light.svg" alt="Price above, and the Accumulation/Distribution line with On-Balance Volume below" width="840" height="590">
</picture>
<figcaption>Synthetic data. The A/D line peaked at 16.48 million on bar 201 and read 4.27 million at the price low (bar 249). During the rebound it rose 3.86 million, while OBV rose 16.07 million.</figcaption>
</figure>

- **Direction.** Rising means closes have mostly been strong. Falling means they have mostly been weak.
- **Divergence.** The line falling while price rises, or the reverse, is the usual caution.
- **The level means nothing.** Only the direction and the comparison with price matter, because the start point is arbitrary.

What it does not tell you: what the start point should be. It is a running total from the first bar loaded, so the same chart on a different start date looks different.

## Best used when

- You study **divergences** between volume and price.
- You prefer a measure that uses **where the bar closed**, not only whether it closed up or down.

## Avoid when

- The market **gaps a lot**. A gap-up bar that then closes low counts as selling even if the whole bar traded above the previous close.
- You compare **different start dates**. The level is not comparable.
- **Volume is unreliable**, as in many over-the-counter markets.

## Settings and tuning

- **No settings.** The line has none. Its smoothed version is the [Chaikin Oscillator](../chaikin-oscillator/).

## Implementation variations

- **Zero-range bars.** Counted as 0 here, and handled differently by some tools.
- **The start.** Some tools start at the first bar loaded, some at zero on a fixed date.
- **Gaps.** Some versions, such as the Williams variant, use the previous close, so they do respond to gaps.
- **History.** It is often credited to Marc Chaikin, and a different version to Larry Williams. I have not confirmed the details.

## Is it useful?

**Situational.** It is a sensible way to bring volume into a picture, and it is the building block for CMF and the Chaikin Oscillator. On the sample, the A/D line gained 3.84M shares in the uptrend, lost 10.23M in the selloff, and gained 3.86M in the rebound, while OBV gained 16.07M in the rebound. The two sets of numbers differ because they sign volume differently. Their 20-bar changes correlated 0.84, so they usually agree, and when they do not, one of them is reading something the other is not. The line peaked at 16.48M on bar 201 and was at 4.27M on bar 249, the price low. As with all volume tools, it is a clue and not a verdict.

## Pairs well with / See also

- [On-Balance Volume](../on-balance-volume/): the simpler running total.
- [Chaikin Money Flow](../chaikin-money-flow/): the same thing over a window.
- [Chaikin Oscillator](../chaikin-oscillator/): the momentum of this line.
