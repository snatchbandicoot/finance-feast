---
title: Klinger Oscillator
aliases: [KVO, Klinger Volume Oscillator]
category: volume
summary: Builds a "volume force" for each bar from its volume, range and trend direction, and then takes the difference between a fast and a slow average of it. It aims to show long-term money flow while still responding to short-term swings.
display: panel
inputs:
  - { name: fast, default: 34 }
  - { name: slow, default: 55 }
  - { name: signal, default: 13 }
verdict: situational
status: draft
related: [chaikin-oscillator, on-balance-volume, accumulation-distribution]
overlaps:
  - with: chaikin-oscillator
    strength: partial
    corr: 0.64
    note: "Both are the difference between a fast and a slow average of a volume-based flow. They build the flow differently. The correlation is between the two oscillators."
---

> **In plain English.** Each bar gets a "force" number: its volume, scaled up when the bar's range is large compared with the recent trend's range, and signed by whether the bar's typical price rose or fell. The oscillator is a fast average of those forces minus a slow one, with a signal line. Above zero, force has been positive recently, and below zero, negative.
>
> **Good for:** a volume-based momentum line that looks at several weeks of flow at once.
>
> **Watch out for:** how many choices are hidden inside it. There are several versions of the formula in circulation, and the numbers differ between tools.

## What it measures

The trend in volume force. A bar's force is positive when the typical price rose from the previous bar and negative when it fell, and its size depends on volume and on how large the bar's range is compared with the range accumulated within the current trend direction.

## Calculation

Each bar has the following parts:

- **Trend** $T_t = +1$ if $H + L + C$ is greater than the previous bar's, and $-1$ otherwise.
- **Range** $dm_t = H_t - L_t$.
- **Cumulative range** $cm_t$: if the trend is the same as the previous bar's, $cm_t = cm_{t-1} + dm_t$. If the trend changed, $cm_t = dm_{t-1} + dm_t$.

$$
VF_t = V_t \times \left|\,2\,\frac{dm_t}{cm_t} - 1\,\right| \times T_t \times 100
$$

$$
\text{KVO}_t = \text{EMA}_{34}(VF)_t - \text{EMA}_{55}(VF)_t
$$

The signal line is a 13-bar exponential average of the KVO.

**Worked example.** A bar has a volume of 1,000, a range that is 0.75 of the accumulated range ($dm/cm = 0.75$), and an upward trend. Then $|2 \times 0.75 - 1| = 0.5$, so $VF = 1000 \times 0.5 \times 1 \times 100 = 50{,}000$. When a bar's range equals half the accumulated range the force is zero, and when the bar is most of it the force is large.

```python
def klinger(high, low, close, volume, fast=34, slow=55, signal=13):
    typical = high + low + close
    trend = np.where(typical > typical.shift(), 1.0, -1.0)
    spread = (high - low).to_numpy()
    cumulative = np.zeros(len(close))
    cumulative[0] = spread[0]
    for i in range(1, len(close)):
        same = trend[i] == trend[i - 1]
        cumulative[i] = (cumulative[i - 1] if same else spread[i - 1]) + spread[i]
    force = volume * np.abs(2 * spread / cumulative - 1) * trend * 100
    line = force.ewm(span=fast, adjust=False).mean() - force.ewm(span=slow, adjust=False).mean()
    return line, line.ewm(span=signal, adjust=False).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/klinger-oscillator-dark.svg">
<img src="../../charts/klinger-oscillator-light.svg" alt="Price above, and the Klinger Oscillator with its signal line below, with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Klinger Oscillator ranged from -16.45 million (bar 244) to +14.8 million (bar 64) over the scored bars, crossing zero 26 times and its signal line 39 times. It was above zero on 78% of the uptrend's scored bars and 22% of the selloff's.</figcaption>
</figure>

- **Above zero** means volume force has been positive over the recent past, and **below zero**, negative.
- **Signal crossovers** are the usual timing cues. They are frequent: 39 over the scored sample.
- **Divergence** from price is the usual caution.

What it does not tell you: the size of any move in price terms. The scale is in shares and cannot be compared across instruments.

## Best used when

- You want a **medium-term** volume read and accept its complexity.
- You study **divergences** between flow and price.

## Avoid when

- You compare **different tools**. The versions differ, so the numbers will not match.
- You want a **simple** indicator.
- **Volume is unreliable.**

## Settings and tuning

- **34, 55 and 13** are the usual values, which are Fibonacci numbers.
- **Shorter averages** make it jumpier.

## Implementation variations

- **The first bar.** It has no previous bar, so tools differ on its trend. Here, it counts as not rising.
- **The cumulative range.** Several published versions differ in details such as when it resets, and the formula here is one common reading of them.
- **Scaling.** The factor 100 only changes the size.
- **Averages.** Exponential, as in most versions.
- **History.** It is usually credited to Stephen Klinger. I have not confirmed the details.

## Is it useful?

**Situational.** The construction is elaborate for what it delivers. On the sample it was above zero on 78% of the uptrend's scored bars, 52% of the range's, 22% of the selloff's and 76% of the rebound's, which matches the story, and its low of -16.45 million came on bar 244, five bars before the price low. But it correlated only 0.64 with the Chaikin Oscillator, which shows that the two volume-flow constructions pick up different things, and neither is clearly better. Its extra machinery is hard to justify by what it adds. Try it if you like volume oscillators, and compare it with simpler ones before trusting it.

## Pairs well with / See also

- [Chaikin Oscillator](../chaikin-oscillator/): a simpler fast-minus-slow oscillator on a volume flow.
- [On-Balance Volume](../on-balance-volume/): the simplest signed volume total.
- [Accumulation/Distribution Line](../accumulation-distribution/): a flow weighted by where the close sits.
