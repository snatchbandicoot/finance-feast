---
title: On-Balance Volume
aliases: [OBV]
category: volume
summary: A running total that adds a bar's volume when price closes up and subtracts it when price closes down.
display: panel
inputs: []
verdict: situational
status: draft
related: [volume-weighted-average-price, relative-strength-index, simple-moving-average]
---

> **In plain English.** Keep a running score. On a day price closes higher, add that day's volume. On a day it closes lower, subtract it. If price is unchanged, leave the score alone. The idea is that heavy volume on up days and light volume on down days shows buyers are in control, even before price makes it obvious.
>
> **Good for:** a rough check on whether volume is supporting a move or not.
>
> **Watch out for:** its crudeness. A tiny up-tick on enormous volume counts the same as a large rally. And the actual number is meaningless, only its direction matters.

## What it measures

Whether volume has been flowing into up-moves or into down-moves, summed over time. It is a cumulative measure. Each bar adds or subtracts its volume, and the total accumulates for as long as you have data.

It makes one simple assumption: that the whole bar's volume belongs to buyers when the close is up, and to sellers when it is down. That is a rough approximation of what actually happened inside the bar.

## Calculation

$$ OBV_t = OBV_{t-1} + \begin{cases} +V_t & \text{if } C_t > C_{t-1} \\ 0 & \text{if } C_t = C_{t-1} \\ -V_t & \text{if } C_t < C_{t-1} \end{cases} $$

$V_t$ is the bar's volume and $C_t$ its close.

**Worked example.** Closes of 10, 11, 10.5, 10.5, 12 with volumes of 100, 200, 150, 120, 300. Start at 0.

| Bar | Close vs. previous | Volume | OBV |
|-----|--------------------|--------|-----|
| 1 | (first bar) | 100 | 0 |
| 2 | up | 200 | +200 → 200 |
| 3 | down | 150 | −150 → 50 |
| 4 | unchanged | 120 | no change → 50 |
| 5 | up | 300 | +300 → 350 |

```python
def obv(close, volume):
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/on-balance-volume-dark.svg">
<img src="../../charts/on-balance-volume-light.svg" alt="Price above, and on-balance volume below" width="840" height="590">
</picture>
<figcaption>Synthetic data. OBV ends at a new high of about 25 million even though price is 17% below its range high. In this sample volume grew with the size of the moves, so the large rebound bars outweighed the selloff in the running total. This is why comparing OBV with an old price high is not a forecast.</figcaption>
</figure>

- **The level means nothing.** OBV depends on where you started counting. An OBV of 5 million tells you nothing on its own. Look at the *shape*: is it rising, falling or flat?
- **Confirmation.** Price and OBV both making new highs together says volume is backing the move.
- **Divergence.** Price makes a new high while OBV does not. This is read as "the move is not supported by volume". Like every divergence, it shows up often and fails often.
- **Trend of OBV.** A rising OBV in a sideways market is sometimes read as quiet accumulation. This is an interpretation and not something the calculation proves.

What it does not tell you: who was buying or selling, how large the real order flow was, or what happens next.

## Best used when

- You want a **quick check** on whether volume agrees with price.
- You work on **instruments with reliable volume**, like listed stocks and futures.
- You compare **its trend with price over weeks to months**, where the crudeness matters less.

## Avoid when

- The instrument has **no real volume data**, such as spot currencies. Tick counts make it a count of price changes, not trading.
- You read **the absolute number**, or compare OBV between instruments. It is not comparable.
- You depend on it for **short-term timing**. A single high-volume bar can swing the total.
- A bar has an **outsized volume** because of an index rebalance, an expiry or a news event. All of it counts as buying or selling based on the close alone, so one bar can dominate the line.

## Settings and tuning

There are no settings. The one thing you can change is where the line starts, which only shifts the level and not the shape.

Some people smooth OBV with a moving average, or compare it with its own moving average, to make direction clearer. These are additions, and not part of the original.

## Implementation variations

- **Start value.** Tools start at zero, at the first bar's volume, or at a user-set number. The shape is the same in all cases.
- **First bar.** Some include the first bar's volume as a plus. Others start from zero.
- **Unchanged closes.** The standard rule leaves OBV alone. Some variants split the bar's volume or carry the previous direction.

## Is it useful?

**Situational, and modest.** The idea that volume should back a move is sound, and OBV is the simplest way to check it. But it is a blunt measure. It assigns all volume to one side based on a single close-to-close comparison, so it can be misled by a thin up-tick or one oversized bar. Treat it as a quick sanity check on a move you already see in price, not as a source of signals. More refined volume studies exist that try to split volume within the bar. It is also easy to read too much into: a divergence between price and OBV is a hint, and not evidence.

## Pairs well with / See also

- [Volume Weighted Average Price](../volume-weighted-average-price/): a different use of volume, as a price average.
- [Relative Strength Index](../relative-strength-index/): momentum from price alone, so it can be set against OBV to see whether volume agrees with the momentum.
- [Simple Moving Average](../simple-moving-average/): sometimes applied to OBV itself, to help show its direction.
