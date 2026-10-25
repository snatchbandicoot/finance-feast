---
title: Relative Strength Index
aliases: [RSI, Wilder's RSI]
category: momentum
summary: A 0 to 100 gauge of how much of recent price movement has been up versus down.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: situational
status: draft
related: [simple-moving-average, exponential-moving-average, stochastic-oscillator]
---

> **In plain English.** A score from 0 to 100 for how much of the recent price movement was up versus down. Above 50 means gains have been winning, below 50 means losses have. Think of it as a momentum meter, not a buy or sell switch.
>
> **Good for:** judging momentum, and spotting stretched moves in a sideways market.
>
> **Watch out for:** strong trends, where "overbought" can last a long time. Selling every reading above 70 tends to lose to the trend.

## What it measures

Of the price movement over the last N bars, how much of it was up? Add up the typical size of the up-moves, add up the typical size of the down-moves, and express the up share as a number from 0 to 100.

- Near 100: almost all recent movement was upward.
- Near 0: almost all recent movement was downward.
- Near 50: gains and losses have been about equally large.

It uses closes only. It does not know about volume, volatility, or what the market "should" do. It is a rescaled summary of recent price changes.

## Calculation

Take the change from each close to the next. Split changes into gains (positive ones, otherwise zero) and losses (the size of negative ones, otherwise zero). Smooth each with Wilder's method, an exponential average with $\alpha = 1/N$:

$$ \overline{G}_t = \left(1 - \tfrac{1}{N}\right)\overline{G}_{t-1} + \tfrac{1}{N}\,G_t \qquad \overline{L}_t = \left(1 - \tfrac{1}{N}\right)\overline{L}_{t-1} + \tfrac{1}{N}\,L_t $$

$$ RS = \frac{\overline{G}}{\overline{L}}, \qquad \text{RSI} = 100 - \frac{100}{1 + RS} = 100 \cdot \frac{\overline{G}}{\overline{G} + \overline{L}} $$

The last form shows what RSI really is: the smoothed gains as a share of all smoothed movement.

**Worked example.** If the average gain is 0.6 and the average loss is 0.4, then $RS = 1.5$ and $\text{RSI} = 100 - 100/2.5 = 60$. Equivalently, gains are $0.6 / (0.6 + 0.4) = 60\%$ of the movement.

```python
def rsi(close, n=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + avg_gain / avg_loss)
```

This starts the averages at the first change. Wilder's original starts with the simple average of the first $N$ changes. The two differ early on, and the difference fades fast: on test data the two agreed to within 0.001 after about 200 bars. Treat the first few dozen values of any RSI as unreliable.

## How to read it

- **Above 50 or below 50.** Gains outweigh losses, or the reverse, over the window. This is the plainest and most reliable reading.
- **The 70 and 30 lines.** Conventionally called overbought and oversold. They mark a *stretched* move, not a turning point. In a strong trend RSI can sit above 70 for a long time while price keeps rising.
- **Shifted ranges in trends.** Some practitioners (Constance Brown is a commonly cited source) describe RSI tending to stay roughly between 40 and 80 in an uptrend and 20 to 60 in a downtrend. In that view a dip to 40 in an uptrend is a pullback, not a warning. Treat this as a useful rule of thumb that has not been established as a law.
- **Divergence.** Price makes a new high while RSI makes a lower high. It is often described as a warning of fading momentum. It shows up often and fails often, and it can persist for a long time before price turns, if it ever does.

What it does not tell you: when a move will end. A reading is a description of the recent past.

## Best used when

- Price is **ranging**. Extremes near 30 and 70 then mark moves that have been stretched in one direction, and a reversal toward the middle is more plausible.
- You want a quick **momentum** gauge. Is a trend still being driven by strong closes, or have the gains thinned out?
- You use it as **context** alongside a trend study, for example to tell a pullback inside an uptrend from a real change of direction.

## Avoid when

- Price is **trending strongly**. Selling every move above 70 in an uptrend, or buying every move below 30 in a downtrend, repeatedly works against the trend.
- You treat a single threshold as a **signal**. Thresholds describe a state, not an event.
- You use a very **short length** and expect stable readings. With a length of 2 or 3, RSI jumps across the whole range on ordinary noise.
- The instrument has **gaps or illiquid closes**. One odd close moves the average and can distort RSI for many bars.

## Settings and tuning

- **Length 14** is Wilder's original and the usual default.
- **Shorter** (such as 7): more sensitive, reaches 70 and 30 often, and gives more false extremes.
- **Longer** (such as 21 or more): smoother, rarely reaches the extremes, and responds later.
- **Thresholds.** Moving the lines to 80 and 20 in a trend, or using 60 and 40 as momentum filters, are common adjustments. Each trades fewer signals against later ones. Choosing thresholds by looking at past charts until they fit is a good way to fool yourself.

## Implementation variations

- **Smoothing.** Wilder's smoothing, an EMA with $\alpha = 1/N$, is standard. Some tools use a plain moving average of gains and losses instead (sometimes called "Cutler's RSI"). It gives different values, and a version with a plain average is not the same indicator.
- **Starting values.** As noted above, the seed differs between tools, so early values differ.

If an RSI on one chart disagrees with another tool's RSI of the same length, these two are the first places to look.

## Is it useful?

**Situational.** As a momentum gauge and as context in a range, it earns its place. As a standalone buy/sell trigger, it is weak, and the overbought/oversold reading is the single most misused rule in popular technical analysis.

Its relatives overlap with it substantially. The [stochastic oscillator](../stochastic-oscillator/) and similar bounded momentum indicators mostly restate the same recent-price-position information, so using several together adds less than it appears to.

## Pairs well with / See also

- [Simple Moving Average](../simple-moving-average/) and [Exponential Moving Average](../exponential-moving-average/): the average sets the direction, and RSI shows whether the move is gathering or losing pace.
- Wilder's smoothing is the same recursion as an EMA with $\alpha = 1/N$. See the EMA page for how that speed compares with the standard $2/(N+1)$.
