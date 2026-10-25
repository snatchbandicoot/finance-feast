---
title: Fisher Transform
aliases: [Fisher, Fisher Transform Indicator]
category: momentum
summary: Rescales where the recent price sits in its range and applies a mathematical stretch that makes turning points sharper. It swings above and below zero, and is read for its peaks, troughs and crossings.
display: panel
inputs:
  - { name: length, default: 10 }
verdict: situational
status: draft
related: [stochastic-oscillator, williams-percent-r, relative-strength-index]
overlaps:
  - with: stochastic-oscillator
    strength: partial
    corr: 0.75
    note: "Both place the price within its recent range. The Fisher Transform stretches the ends of that range. The correlation is between the Fisher Transform and the Stochastic's %K."
---

> **In plain English.** Take where the middle of today's bar sits within its recent high-low range, from the bottom (-1) to the top (+1). Then stretch the ends, so that readings near the edges become large numbers. The result has sharper peaks and troughs than a Stochastic would, which makes turning points easier to spot, and false alarms easier to produce.
>
> **Good for:** marking sharp turning points, when the market is swinging in a range.
>
> **Watch out for:** the claim that it makes prices "normally distributed". It does not. It is a re-scaling that exaggerates the ends of the range.

## What it measures

How extreme the current price is within its recent range, stretched so that extremes stand out. It has no fixed upper or lower limit, though in practice readings beyond ±2 are rare in a quiet market.

## Calculation

Let $m$ be the middle of each bar, $(H+L)/2$, and let $HH$ and $LL$ be the highest and lowest middles over $N$ bars.

$$
x_t = 2 \times \left(\frac{m_t - LL}{HH - LL} - 0.5\right)
$$

$$
v_t = 0.33\,x_t + 0.67\,v_{t-1} \quad (\text{kept between } -0.999 \text{ and } 0.999)
$$

$$
\text{Fisher}_t = 0.5 \ln\!\left(\frac{1 + v_t}{1 - v_t}\right) + 0.5\,\text{Fisher}_{t-1}
$$

The trigger line is the Fisher value from the previous bar.

**Worked example.** In a 10-bar window with a lowest middle of 100 and a highest of 110, today's middle is 107.5. Then $x = 2 \times (0.75 - 0.5) = 0.5$. With nothing before it ($v_{t-1} = 0$), $v = 0.33 \times 0.5 = 0.165$, and the Fisher value is:

$$
0.5 \ln\!\left(\frac{1.165}{0.835}\right) = 0.166
$$

The log stretch is gentle in the middle and steep at the edges: $v = 0.9$ gives about 1.47, and $v = 0.999$ gives about 3.8.

**An upper limit.** The 0.999 clip and the half-weight on the previous value together cap the line near 7.6. A straight climb reaches it. The check script confirms this.

```python
def fisher(high, low, n=10):
    mid = (high + low) / 2
    highest, lowest = mid.rolling(n).max(), mid.rolling(n).min()
    position = 2 * ((mid - lowest) / (highest - lowest).replace(0, np.nan) - 0.5)
    value, line = 0.0, 0.0
    out = []
    for x in position:
        if np.isnan(x):
            out.append(np.nan)
            continue
        value = max(-0.999, min(0.999, 0.33 * x + 0.67 * value))
        line = 0.5 * np.log((1 + value) / (1 - value)) + 0.5 * line
        out.append(line)
    out = pd.Series(out, index=mid.index)
    return out, out.shift(1)
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/fisher-transform-dark.svg">
<img src="../../charts/fisher-transform-light.svg" alt="Price above, and the Fisher Transform with its trigger line below, with lines at -2, 0 and 2" width="840" height="590">
</picture>
<figcaption>Synthetic data. The Fisher Transform ranged from -5.9 (bar 245) to +6.54 (bar 270), and was beyond ±2 on 31% of scored bars. It crossed its trigger line 39 times.</figcaption>
</figure>

- **Peaks and troughs.** A sharp peak followed by a turn down is the usual sell cue, and the mirror image for buying.
- **Crossing the trigger.** The Fisher line crossing the previous bar's value is the usual timing cue. Because the trigger is only one bar old, it crosses very often: 39 times over the scored sample.
- **±2.** A common "extreme" guide. On the sample it was exceeded on 31% of bars, so it is not rare.

What it does not tell you: whether a turn will last. It reports position within a range, and a trend simply pushes the range along.

## Best used when

- The market is **ranging**, with clear swings.
- You want **sharp** turning-point markers, and accept the false ones.

## Avoid when

- The market is **trending**. In the sample's rebound it stayed above +2 for many bars.
- You are tempted by the "Gaussian" claim. It is a marketing line, not a guarantee.

## Settings and tuning

- **Length 10** is the usual default. Shorter is jumpier.
- **The 0.33 and 0.67 smoothing weights** are built into the standard version.
- **The ±0.999 clip** is there only to keep the log finite.

## Implementation variations

- **Input.** Some versions use the close and some the middle of the bar. This page uses the middle.
- **Smoothing.** The weights 0.33 and 0.67 are standard but some versions differ.
- **Trigger.** The one-bar delay is standard, but some tools omit it.
- **History.** It is usually credited to John Ehlers. I have not confirmed the details.

## Is it useful?

**Situational.** It is a Stochastic-like measure with a sharper look. The correlation with the Stochastic's %K on the sample was 0.75, so it is related but not the same, and it did mark the sample's main turns: its low of -5.9 came on bar 245, four bars before the price low, and its high of 6.54 on bar 270. But it also crossed its trigger 39 times, and exceeded ±2 on 31% of bars. The sharpness is real and so are the false alarms. Use it with a trend filter, or not at all.

## Pairs well with / See also

- [Stochastic Oscillator](../stochastic-oscillator/): the plainer version of the same idea.
- [Williams %R](../williams-percent-r/): the same range idea.
- [Relative Strength Index](../relative-strength-index/): a different way to read momentum.
