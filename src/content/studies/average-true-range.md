---
title: Average True Range
aliases: [ATR, Wilder's ATR]
category: volatility
summary: The typical distance price travels in one bar, counting overnight gaps, used to measure how big the moves are, not which way they go.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: essential
status: draft
related: [bollinger-bands, relative-strength-index, exponential-moving-average]
---

> **In plain English.** How far price typically moves in a single bar, including gaps between one bar's close and the next bar's open. A high reading means the market has been moving a lot. A low reading means it has been quiet. It says nothing about direction.
>
> **Good for:** sizing stops and positions to how much the market is actually moving, and comparing how volatile a market is now to how volatile it has been.
>
> **Watch out for:** reading it as a buy or sell signal. It has no direction. It is also in price units, so it cannot be compared between instruments without converting to a percentage.

## What it measures

The size of a typical bar, from low to high, extended to include any gap from the previous close. A plain high-minus-low range misses gaps: if a stock closes at 13 and opens the next day at 10, trading between 10 and 12, the high-minus-low range is only 2, but price really moved 3 from the last close. ATR counts that.

## Calculation

First the **true range** for each bar, the largest of three distances:

$$ TR_t = \max\bigl(H_t - L_t,\ |H_t - C_{t-1}|,\ |L_t - C_{t-1}|\bigr) $$

$H$, $L$ and $C$ are the bar's high, low and close, and $C_{t-1}$ is the previous close. Then smooth it with Wilder's method (an exponential average with $\alpha = 1/N$):

$$ ATR_t = \left(1 - \tfrac{1}{N}\right) ATR_{t-1} + \tfrac{1}{N}\, TR_t $$

**Worked example.** A bar has a high of 12 and a low of 10, and the previous close was 13. The three distances are $12 - 10 = 2$, $|12 - 13| = 1$, and $|10 - 13| = 3$. The true range is 3, the largest. It captures the gap down that the bar's own range misses.

```python
def atr(high, low, close, n=14):
    prev_close = close.shift()
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()
```

This starts the average at the first true range. Wilder's original starts with the simple average of the first $N$ true ranges. On test data the two agreed to within 0.001 after about 200 bars, so treat the first few dozen values of any ATR as unreliable.

## How to read it

- **Level.** A high ATR means bars have been large lately. A low ATR means they have been small. Compare it with its own history, not with a fixed number.
- **Rising ATR.** Volatility is increasing. This often accompanies sharp moves in either direction, and it is common around breakdowns and panics.
- **Falling ATR.** Volatility is shrinking, as in a quiet or consolidating market.
- **As a ruler.** The main use is converting "how far" into units of typical movement. A stop two ATRs away is at a distance the market normally covers in about two bars' typical travel.

What it does not tell you: whether the next move is up or down, or when volatility will change.

### Using it to size a position

If you risk a fixed amount per trade, and put your stop at $k$ ATRs from your entry, then:

$$ \text{shares} = \frac{\text{risk per trade}}{k \times ATR} $$

For example, risking \$100 with an ATR of \$2 and a stop at 2 ATRs gives $100 / (2 \times 2) = 25$ shares. When volatility doubles, the same risk buys half as many shares. That is the point: the position shrinks in jumpy markets, so the dollar risk stays the same.

The choice of $k$ is a judgment call. A tighter stop gets hit by ordinary noise. A looser one lets the loss grow, which forces a smaller position. There is no universally correct multiple.

## Best used when

- You need a **volatility-aware stop or position size**. This is where ATR earns its keep.
- You want to know whether the market is **calm or jumpy** compared with its recent past.
- You compare volatility **over time** for one instrument, for example before and after a news event.

## Avoid when

- You want a **directional signal**. ATR rises in both sharp rallies and sharp selloffs.
- You compare **different instruments** in price units. A \$500 stock with an ATR of 5 is calmer than a \$20 stock with an ATR of 2. Divide by price ($100 \times ATR / \text{Close}$) to compare.
- A single **huge bar or gap** just happened. It lifts ATR sharply, and the reading stays elevated for many bars while Wilder's smoothing slowly lets it fall.

## Settings and tuning

- **Length 14** is Wilder's default.
- **Shorter** (such as 5 to 7): follows recent volatility closely and jumps around more.
- **Longer** (such as 20 or more): steadier, and slower to notice a change.

## Implementation variations

- **Smoothing.** Wilder's smoothing ($\alpha = 1/N$) is standard. Some tools offer a simple, exponential ($2/(N+1)$) or other moving average of the true range. The values differ, so an ATR that does not match another tool is often using a different average.
- **Starting value.** As above, the first values depend on how the average is seeded.
- **Percentage form.** Some platforms offer a normalised ATR as a percentage of price.

## Is it useful?

**Essential**, as a tool for stops and sizing, and not as a signal. It is the standard answer to the question "how much does this thing typically move?", and risk control rests on that. Almost no one uses it to decide *what* to trade, and that is the right use. Among volatility measures it overlaps with Bollinger Bandwidth, which is also a volatility reading, but ATR counts gaps and is expressed in price units, which is what you need for a stop.

## Pairs well with / See also

- [Bollinger Bands](../bollinger-bands/): volatility shown as an envelope around a moving average, and a percentage-based bandwidth.
- [Exponential Moving Average](../exponential-moving-average/): ATR's smoothing is an EMA with $\alpha = 1/N$.
- [Relative Strength Index](../relative-strength-index/): Wilder's other well-known study, with the same smoothing.
