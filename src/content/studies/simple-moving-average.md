---
title: Simple Moving Average
aliases: [SMA, Moving Average, Arithmetic Moving Average]
category: trend
summary: The plain average of the last N closes, a smoothed line that shows which way price has been drifting.
display: overlay
inputs:
  - { name: length, default: 20 }
verdict: essential
status: draft
related: [exponential-moving-average, relative-strength-index]
---

> **In plain English.** The average price over the last N bars, recalculated on every new bar. It smooths out the day-to-day noise so you can see which way price has been drifting. It always trails price, so it describes the past and does not predict.
>
> **Good for:** seeing the broad direction, and as a reference line that many traders watch.
>
> **Watch out for:** sideways markets, where price keeps crossing the line and every cross misleads.

## What it measures

The average price over the last N bars. Each new bar adds one price and drops the oldest, so the line moves with the data. It answers one question: *where has price been, on average, over this window?*

Price above a rising average means recent prices are higher than the window's typical price. Price below a falling average means the opposite. That is all the line states.

## Calculation

Add the last N closes and divide by N.

$$ \text{SMA}_t = \frac{1}{N}\sum_{i=0}^{N-1} P_{t-i} $$

Here $P_t$ is the close at bar $t$ and $N$ is the length.

**Worked example.** Closes of 10, 11, 12, 11, 13 with $N = 3$. The latest SMA uses the last three closes: $(12 + 11 + 13) / 3 = 12$.

```python
def sma(close, n):
    return close.rolling(n).mean()
```

The first $N - 1$ bars have no value, since the window is not full yet.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/simple-moving-average-dark.svg">
<img src="../../charts/simple-moving-average-light.svg" alt="Price with a 20-bar and a 100-bar simple moving average across four regimes" width="840" height="430">
</picture>
<figcaption>Synthetic data in four regimes. In the uptrend the 20-bar average (blue) stays under price and follows it up. In the range, price crosses it 12 times. In the selloff both averages turn only after price has already fallen, and the 100-bar average (orange) is smoother and later still.</figcaption>
</figure>

- **Slope.** A rising line says the average price of the window is climbing. A flat line says no trend over that window.
- **Price versus line.** Price above the line is above its recent average. Crossing the line is a *description* of what just happened, not a forecast.
- **Two averages.** A short average crossing a longer one is the common "crossover" signal. Both lines lag, so the cross shows up after a move is under way.
- **Widely watched lengths.** The 50 and 200 bar averages are followed by many traders. Where a lot of people look at the same line, it can matter for that reason alone. That is a statement about attention, not about the math.

What it does not tell you: how strong the trend is, how long it will last, or what happens next.

## Best used when

- Price is trending cleanly. The line follows along and stays on one side of price.
- You want a simple, transparent reference. Anyone can recompute it by hand.
- You need to filter noise before another step, for example to define a trend direction for a different study.

## Avoid when

- Price is moving sideways. Price crosses the line repeatedly and every cross is a false signal.
- You need an early warning. The average is built from old prices, so it turns after price has already turned.
- A single large bar sits in the window. It pulls the average up, and then pulls it back down when it falls out of the window, even if nothing changed at that moment. This produces a visible step in the line.

## Settings and tuning

- **Shorter length** (such as 10): hugs price, reacts sooner, crosses more often, and gives more false signals.
- **Longer length** (such as 100 or 200): smooth and slow, fewer signals, each one later.

There is no best length. A longer window trades responsiveness for stability, and which side of that trade is right depends on how you use the line. Fitting the length to past data until it looks good is a reliable way to fool yourself.

## Is it useful?

**Essential as a concept, modest as a signal.** You will meet it everywhere, and many other studies are built from it, so understanding it is not optional. On its own it is a lagging description, not a trading edge. Treat it as context for price, not as a reason to trade.

It overlaps heavily with the [exponential moving average](../exponential-moving-average/). For most purposes the two give similar pictures, and the difference is mainly how fast they react.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the same idea with more weight on recent prices.
- [Relative Strength Index](../relative-strength-index/): a momentum reading that complements a trend line, since the average shows direction and RSI shows pace.
