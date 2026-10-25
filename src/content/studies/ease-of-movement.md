---
title: Ease of Movement
aliases: [EMV, EOM, Arms Ease of Movement]
category: volume
summary: Compares how far the midpoint of the bar moved with how much volume it took, per unit of range. A big move on light volume in a wide bar scores high, which is read as price moving easily.
display: panel
inputs:
  - { name: smoothing length, default: 14 }
  - { name: volume scale, default: "1,000,000" }
verdict: redundant
status: draft
related: [rate-of-change, chaikin-money-flow, force-index]
overlaps:
  - with: rate-of-change
    strength: partial
    corr: 0.90
    note: "The midpoint move is the main driver of both, and the volume and range terms change the scale. The correlation is with a 12-bar rate of change."
---

> **In plain English.** If price rose a lot and not much volume was needed, the market moved up easily, with little resistance. If price barely moved even on heavy volume, it was hard going. The Ease of Movement turns this into a number: the move in the bar's midpoint, divided by how much volume it took for the range of the bar. Above zero, price moved up easily. Below zero, it moved down easily.
>
> **Good for:** a rough read on whether price is rising or falling without much effort.
>
> **Watch out for:** its scale. The size depends on a volume scaling constant that tools pick differently, so the numbers on one platform do not match another's.

## What it measures

The midpoint movement of each bar relative to a "box ratio", which is volume divided by range. A small box ratio means price covered a lot of range on little volume.

## Calculation

$$
\text{distance}_t = \frac{H_t + L_t}{2} - \frac{H_{t-1} + L_{t-1}}{2} \qquad \text{box}_t = \frac{V_t / s}{H_t - L_t}
$$

$$
\text{EMV}_t = \text{SMA}_{14}\!\left(\frac{\text{distance}_t}{\text{box}_t}\right)
$$

where $s$ is a scaling constant (1,000,000 here) that only changes the size of the number.

**Worked example.** The previous bar had a high of 10 and a low of 8 (midpoint 9). This bar has a high of 12, a low of 9 (midpoint 10.5) and a volume of 2,000,000:

- distance $= 10.5 - 9 = 1.5$
- box ratio $= (2{,}000{,}000 / 1{,}000{,}000) / (12 - 9) = 2/3 = 0.667$
- raw value $= 1.5 / 0.667 = 2.25$

Doubling the volume halves every value, which the check script confirms.

```python
def ease_of_movement(high, low, volume, n=14, scale=1e6):
    midpoint_move = (high + low) / 2 - (high.shift() + low.shift()) / 2
    box_ratio = (volume / scale) / (high - low)
    return (midpoint_move / box_ratio).rolling(n).mean()
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/ease-of-movement-dark.svg">
<img src="../../charts/ease-of-movement-light.svg" alt="Price above, and the 14-bar Ease of Movement below with a zero line" width="840" height="590">
</picture>
<figcaption>Synthetic data. Ease of Movement ranged from -5.10 (bar 244) to +1.44 (bar 94) and crossed zero 22 times. It was above zero on 85% of the uptrend's scored bars and 20% of the selloff's.</figcaption>
</figure>

- **Above zero**: price is rising with little resistance. **Below zero**: falling with little resistance.
- **Near zero**: it takes a lot of volume to move price, as in a stuck market.
- **Zero crossings** are the usual signals. The sample's line crossed zero 22 times.

What it does not tell you: the absolute size of any move. Its scale depends on the volume constant.

## Best used when

- You want a **volume-aware** read of momentum and your market has meaningful volume.

## Avoid when

- You compare **across instruments or tools**, given the scaling.
- The bar has **almost no range**: a tiny range makes the ratio explode.
- You want a **simple** indicator.

## Settings and tuning

- **14** is the usual smoothing.
- **The volume scale** does not change the shape, only the size.

## Implementation variations

- **Scale.** Constants from 1,000 to 100,000,000 are used. The number you see depends on the choice.
- **Smoothing.** A simple average here, though some tools use others.
- **History.** It is usually credited to Richard Arms. I have not confirmed the details.

## Is it useful?

**Redundant.** The idea is neat, but on the sample the smoothed line correlated 0.90 with a 12-bar rate of change, so it behaves like price momentum with a volume adjustment. Its readings: above zero on 85% of the uptrend's scored bars, 52% of the range's, 20% of the selloff's and 69% of the rebound's. Its low of -5.10 came on bar 244, during the selloff. Those are all things the price momentum already says. If you want volume involved, the [Money Flow Index](../money-flow-index/) or [CMF](../chaikin-money-flow/) are easier to read and compare.

## Pairs well with / See also

- [Rate of Change](../rate-of-change/): what it mostly tracks.
- [Chaikin Money Flow](../chaikin-money-flow/): a volume-based pressure measure.
- [Force Index](../force-index/): another way of combining price change with volume.
