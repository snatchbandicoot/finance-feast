---
title: Exponential Moving Average
aliases: [EMA, Exponentially Weighted Moving Average, EWMA]
category: trend
summary: A moving average that weights recent prices more heavily, so it reacts sooner than a simple average of the same length.
display: overlay
inputs:
  - { name: length, default: 20 }
verdict: situational
status: draft
related: [simple-moving-average, relative-strength-index]
---

> **Takeaway.** An exponential moving average is a simple average that listens more to recent prices. It turns sooner than a simple average of the same length, at the cost of more false turns. It is a tuning choice, not a different kind of information.

## What it measures

A smoothed price where every past bar still counts, but each older bar counts a little less than the one after it. Weights fall off geometrically, so recent prices dominate and old prices fade without ever dropping out abruptly.

That is the main practical difference from the [simple moving average](../simple-moving-average/), which weights every bar in the window equally and then forgets the oldest one all at once.

## Calculation

Each new value blends the newest close with the previous EMA:

$$ \text{EMA}_t = \alpha P_t + (1 - \alpha)\,\text{EMA}_{t-1}, \qquad \alpha = \frac{2}{N + 1} $$

$P_t$ is the close, $N$ is the length, and $\alpha$ is the weight given to the newest close. A length of 20 gives $\alpha = 2/21 \approx 0.095$, so each new bar contributes about 9.5% of the value.

The recursion needs a starting value. A common choice, used below, is the first close. Some tools start from the simple average of the first $N$ bars. The two differ at the beginning and converge after a few multiples of $N$.

**Worked example.** Closes of 10, 11, 12, 11, 13 with $N = 3$, so $\alpha = 0.5$ and the EMA starts at 10:

| Bar | Close | EMA |
|-----|-------|-----|
| 1 | 10 | 10 |
| 2 | 11 | 0.5 × 11 + 0.5 × 10 = 10.5 |
| 3 | 12 | 0.5 × 12 + 0.5 × 10.5 = 11.25 |
| 4 | 11 | 0.5 × 11 + 0.5 × 11.25 = 11.125 |
| 5 | 13 | 0.5 × 13 + 0.5 × 11.125 = 12.0625 |

For comparison, the simple average of the last three closes is 12. The EMA sits slightly higher here because the newest close, 13, carries more weight.

```python
def ema(close, n):
    return close.ewm(span=n, adjust=False).mean()
```

## How to read it

Read it the same way as a simple average: slope shows direction, price above or below the line shows where price sits relative to its recent weighted average, and a short line crossing a long one is a crossover.

The difference is timing. Because recent bars count more, the EMA changes direction earlier, and it stays closer to price after a sharp move.

What it does not tell you: whether the early turn is real. Reacting sooner also means reacting to noise.

## Best used when

- You want a trend line that is quicker to respond than a simple average, for example on shorter timeframes.
- You are using it as an input to another study. Several well-known studies are built from EMAs, including MACD.

## Avoid when

- Price is moving sideways. The EMA turns more readily than a simple average, so it chops back and forth even more.
- You treat its extra speed as extra accuracy. Speed and accuracy trade against each other here.
- You compare lengths across tools without checking how each one starts the recursion. Early values will not match, and a short history makes the mismatch visible.

## Settings and tuning

- **Length** works as in the simple average: shorter is faster and noisier, longer is smoother and later.
- **Equivalent speed.** An EMA of length $N$ is not the same speed as a simple average of length $N$. The EMA reacts faster, so a comparable lag needs a longer EMA length.

## Implementation variations

Two common differences change early values and, slightly, later ones:

- **Starting value:** first close, or the simple average of the first $N$ closes.
- **Smoothing constant:** some sources and tools define length differently, using $\alpha = 1/N$ (Wilder-style smoothing) instead of $2/(N+1)$. That produces a much slower line for the same stated length. If two EMAs of the "same" length disagree, check this first.

## Is it useful?

**Situational.** It is a perfectly good trend line, and it is the more common choice when speed matters. But it does not contain information the simple average lacks. It is mostly a faster dial on the same idea, and choosing between them is a tuning decision, not an edge. If you already use a simple average, adding an EMA of similar length mostly duplicates it.

## Pairs well with / See also

- [Simple Moving Average](../simple-moving-average/): the equal-weight version, slower and smoother.
- [Relative Strength Index](../relative-strength-index/): uses the same kind of recursive smoothing on gains and losses.
