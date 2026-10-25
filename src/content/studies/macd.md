---
title: Moving Average Convergence Divergence
aliases: [MACD, MACD histogram]
category: momentum
summary: The gap between a fast and a slow exponential average, plus a smoothed copy of that gap, used to judge whether a trend is gaining or losing steam.
display: panel
inputs:
  - { name: fast length, default: 12 }
  - { name: slow length, default: 26 }
  - { name: signal length, default: 9 }
verdict: situational
status: draft
related: [exponential-moving-average, simple-moving-average, relative-strength-index]
---

> **In plain English.** MACD subtracts a slow moving average from a fast one. When the fast average pulls away from the slow one, the gap grows and the trend has momentum. When the two squeeze back together, the gap shrinks and the trend is tiring. A second, smoothed line and a bar chart of the difference between the two make the turns easier to see.
>
> **Good for:** judging whether a trend is strengthening or fading, rather than just which way it points.
>
> **Watch out for:** sideways markets, where it flips back and forth. Also, its value is in price units, so you cannot compare MACD readings between a $5 stock and a $500 one.

## What it measures

How far a short-term average of price has moved away from a long-term average. A fast average follows recent prices closely, a slow one follows them loosely, so their gap is large when price has moved quickly in one direction lately, and near zero when price has gone nowhere.

It has three parts:

- **MACD line:** fast EMA minus slow EMA.
- **Signal line:** a smoothed (EMA) version of the MACD line.
- **Histogram:** MACD line minus signal line. It shows whether the MACD line is moving away from its own average or back toward it.

## Calculation

$$ \text{MACD}_t = \text{EMA}_{12}(P)_t - \text{EMA}_{26}(P)_t $$

$$ \text{Signal}_t = \text{EMA}_{9}(\text{MACD})_t \qquad \text{Histogram}_t = \text{MACD}_t - \text{Signal}_t $$

The numbers 12, 26 and 9 are the standard defaults, and they are the lengths of exponential moving averages. See the [exponential moving average](../exponential-moving-average/) page for how those are computed.

**Worked example.** Suppose the 12-bar EMA is 105.2 and the 26-bar EMA is 104.5. Then MACD is $105.2 - 104.5 = 0.7$. If the signal line is 0.5, the histogram is $0.7 - 0.5 = 0.2$. A positive, growing histogram says the gap is widening.

```python
def macd(close, fast=12, slow=26, signal=9):
    line = close.ewm(span=fast, adjust=False).mean() - close.ewm(span=slow, adjust=False).mean()
    sig = line.ewm(span=signal, adjust=False).mean()
    return line, sig, line - sig
```

## How to read it

- **Above or below zero.** MACD above zero means the fast average is above the slow one, which is how an uptrend looks in averages. Crossing zero is *exactly* the moment the 12 and 26 EMAs cross. It adds no information beyond a two-average crossover. It is the same event shown differently.
- **Line crossing the signal line.** This happens earlier than a zero cross, because the signal line trails the MACD line. It is the most common trigger, and it is a signal that momentum has turned, not that price will follow.
- **Histogram.** Bars shrinking toward zero show the gap is closing, so momentum is fading, often before the lines cross. This is the earliest of the three readings and also the noisiest.
- **Divergence.** Price makes a new high while MACD makes a lower high. It is often read as fading momentum. As with RSI, it appears often, fails often, and can persist for a long time.

What it does not tell you: how far price will go, or how reliable the crossing is. It is built from moving averages, so every reading lags price.

## Best used when

- Price is **trending**, and you want to know whether the trend is accelerating or running out of energy.
- You want a **single panel** that summarises two averages and their trend. It is a compact way to watch a crossover.

## Avoid when

- Price is **moving sideways**. The averages sit close together, MACD hovers near zero, and the lines cross constantly. Each cross is noise.
- You want to **compare instruments**. MACD is measured in price units, so a larger price gives a larger number. Use the percentage version (see below) to compare across instruments.
- You trade **every crossover** as a buy or sell. In a choppy market this reliably produces a string of small losses. The signal says momentum has turned, and in a range it turns constantly.

## Settings and tuning

- **12 / 26 / 9** are the defaults, from Gerald Appel, the study's creator. They are often explained as roughly two and four trading weeks on daily charts, but I have not been able to confirm that was his reasoning. Nothing makes them optimal today.
- **Shorter lengths** make MACD react sooner and cross more often, with more false signals.
- **Longer lengths** make it smoother and later.
- **Signal length** controls how quickly the signal line follows MACD. A shorter signal line gives more crossovers.

Tuning the three numbers to fit past data is the most direct way to build a system that looks good on old charts and fails on new ones.

## Implementation variations

- **Percentage version (PPO).** Dividing the gap by the slow average, $100 \times (\text{EMA}_{12} - \text{EMA}_{26}) / \text{EMA}_{26}$, gives the *percentage price oscillator*. It is comparable across instruments and across time, and it is what to use when the price level changes a lot.
- **Signal line type.** Standard MACD smooths the signal line with an EMA. Some tools offer a simple average instead, which gives different crossover timing.
- **Histogram scaling.** Some platforms multiply the histogram or draw it on a different axis. The shape is the same.
- **EMA starting values** differ between tools, so the first few dozen bars will not match across them.

## Is it useful?

**Situational.** It is a tidy way to watch two moving averages and their relationship, and the histogram is a reasonable early read on fading momentum. But it is *derived entirely from moving averages*, so it contains no information that the averages do not. If you already watch a fast and a slow EMA, MACD mostly redraws them. It is more useful as a way to see acceleration than as a source of new signals.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the building block. The zero-line cross is the cross of two EMAs.
- [Simple Moving Average](../simple-moving-average/): the equal-weight alternative.
- [Relative Strength Index](../relative-strength-index/): another momentum reading. RSI is bounded (0 to 100) and comparable across instruments. MACD is not.
