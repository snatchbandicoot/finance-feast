---
title: Double Exponential Moving Average
aliases: [DEMA, Double EMA]
category: trend
summary: An exponential average with most of its lag removed, built as twice the EMA minus the EMA of that EMA.
display: overlay
inputs:
  - { name: length, default: 20 }
verdict: situational
status: draft
related: [exponential-moving-average, triple-exponential-moving-average, hull-moving-average]
overlaps:
  - with: exponential-moving-average
    strength: partial
    corr: 0.68
    note: "The DEMA is made from two EMAs and is meant to follow price more closely. The correlation is measured on how far price sits from each line, so it shows how differently they behave."
---

> **In plain English.** An exponential average that keeps up with price much better. It is computed as twice the EMA minus an EMA of that EMA. The second smoothing is further behind than the first, so subtracting it pushes the line forward and cancels the lag on a steady move. The catch is overshoot: at a sudden jump it flies past the new level before settling, and in sideways markets it crosses price more often. Despite the name, it is not simply an EMA applied twice. That would be a slower line, not a faster one.
>
> **Good for:** following a steady trend with less lag than an EMA.
>
> **Watch out for:** overshoot and extra whipsaws. On this site's test data, after a sudden 10-point jump it overshot the new level by 1.2 points.

## What it measures

The same thing as an EMA, a smoothed price, but with the lag deliberately cancelled out. On a steady climb it has no lag at all, where a 20-bar EMA trails by 9.5 bars.

## Calculation

Let $E_1$ be the EMA of price and $E_2$ the EMA of $E_1$, both with the same length $N$ (see the [Exponential Moving Average](../exponential-moving-average/) page):

$$
\text{DEMA}_t = 2E_1 - E_2
$$

**Why it works.** On a steady climb, $E_1$ trails price by some lag $L$, and $E_2$ trails $E_1$ by the same amount again, so it is $2L$ behind. Then $2E_1 - E_2$ is $2(P - L) - (P - 2L) = P$. The lag cancels.

**Worked example.** If the EMA is 105 and the EMA of that EMA is 103, the DEMA is $2 \times 105 - 103 = 107$. It is 2 above the EMA, pushed forward by the gap between the two smoothings.

**Overshoot.** After a jump from 100 to 110, an EMA approaches 110 from below and never passes it. The DEMA passes it, peaking at 111.2 before coming back. The check script confirms the lag and the overshoot.

```python
def dema(close, n=20):
    first = close.ewm(span=n, adjust=False).mean()
    second = first.ewm(span=n, adjust=False).mean()
    return 2 * first - second
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/double-exponential-moving-average-dark.svg">
<img src="../../charts/double-exponential-moving-average-light.svg" alt="Price with a 20-bar DEMA and a 20-bar EMA through a selloff and rebound" width="840" height="430">
</picture>
<figcaption>Synthetic data, zoomed to the end of the range, the selloff and the rebound. The DEMA (pink) turned much earlier than the EMA (teal): its low was 87.8 at bar 254, below the price low of 88.8, where the EMA's low was 93.7 at bar 260. In the 100-bar range it crossed price 22 times, against 18 for the EMA.</figcaption>
</figure>

Read it as you would an EMA: slope shows direction, price above or below the line shows its place against recent history, and crossovers are the usual signal. The difference is timing. It turns earlier, and it hugs price more closely, in both directions.

What it does not tell you: whether the early turn is real. A line that follows price closely is also pulled around by noise.

## Best used when

- Price is **trending steadily**, and you want a line that keeps up with it.
- You want a **faster** average without simply shortening an EMA.

## Avoid when

- Price is **sideways**. It crosses price more often than an EMA does.
- The market makes **sudden jumps**. The overshoot can put the line on the wrong side of price for a few bars.
- You expect it to be a **smooth** line. It gives up some smoothness for speed.

## Settings and tuning

- **Length 20** is the usual default.
- **Shorter:** faster and noisier. **Longer:** smoother and later.
- Shortening an ordinary EMA also reduces lag. The DEMA is a different way to make that trade, with overshoot as its particular side effect.

## Implementation variations

- **Seeding.** Both EMAs need starting values, and early values depend on them.
- **Naming.** "Double EMA" is sometimes used loosely for an EMA applied twice. That is a different, slower line.
- **History.** It is usually credited to Patrick Mulloy, in the mid-1990s. I have not confirmed the details.

## Is it useful?

**Situational.** It does what it says: it follows a steady trend with no lag. But what you gain in lag you pay for in overshoot and whipsaws. On the sample it crossed price 22 times in the 100-bar range, against 18 for the EMA and 12 for the SMA. It is a fair choice if you want a fast average and accept the trade-off, and it correlates only 0.68 with the EMA (measured on distance from price) because it behaves quite differently. It is not a free lunch.

## Pairs well with / See also

- [Exponential Moving Average](../exponential-moving-average/): the slower, smoother line it is built from.
- [Triple Exponential Moving Average](../triple-exponential-moving-average/): the same idea taken one step further.
- [Hull Moving Average](../hull-moving-average/): another way to cut lag.
