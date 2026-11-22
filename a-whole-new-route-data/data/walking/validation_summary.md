# Google Maps validation

**Date:** 21 November 2026. **Sample:** 12 routes covering all 12 attractions, including short and long trips.

## Method

We requested Google Maps walking directions using the same origin and destination coordinates as the model. We recorded the first recommended route, retained every selected result, and compared its displayed distance and time with the existing matrix. Model time equals distance / 75 m/min. The matrix was not fitted to Google. Each linked route below includes the requested coordinates.

## Results

| Metric | Result |
|---|---:|
| Mean absolute distance difference | 19.0 m |
| Mean absolute percentage distance difference | 10.5% |
| Mean absolute time difference | 0.48 min |
| Routes within 1 minute | 11 / 12 |

| Route / Google query | Model m | Google m | Model min | Google min |
|---|---:|---:|---:|---:|
| [SM–TRON](https://www.google.com/maps/dir/?api=1&origin=28.4187622%2C-81.5783241&destination=28.4199514%2C-81.5772546&travelmode=walking) | 252.9 | 270.00 | 3.37 | 4 |
| [PP–IASW](https://www.google.com/maps/dir/?api=1&origin=28.4203952%2C-81.5818461&destination=28.4204094%2C-81.5820316&travelmode=walking) | 18.2 | 17.98 | 0.24 | 1 |
| [SDMT–POOH](https://www.google.com/maps/dir/?api=1&origin=28.4203578%2C-81.5805181&destination=28.4202086%2C-81.5802121&travelmode=walking) | 45.9 | 34.14 | 0.61 | 1 |
| [POTC–JC](https://www.google.com/maps/dir/?api=1&origin=28.4181032%2C-81.584234&destination=28.4180394%2C-81.5834779&travelmode=walking) | 99.7 | 76.00 | 1.33 | 1 |
| [HM–PP](https://www.google.com/maps/dir/?api=1&origin=28.4201572%2C-81.5828859&destination=28.4203952%2C-81.5818461&travelmode=walking) | 113.5 | 120.00 | 1.51 | 2 |
| [HM–POTC](https://www.google.com/maps/dir/?api=1&origin=28.4201572%2C-81.5828859&destination=28.4181032%2C-81.584234&travelmode=walking) | 353.6 | 350.00 | 4.71 | 5 |
| [TIANA–POTC](https://www.google.com/maps/dir/?api=1&origin=28.4196285%2C-81.5849644&destination=28.4181032%2C-81.584234&travelmode=walking) | 217.1 | 210.00 | 2.89 | 3 |
| [SM–SDMT](https://www.google.com/maps/dir/?api=1&origin=28.4187622%2C-81.5783241&destination=28.4203578%2C-81.5805181&travelmode=walking) | 331.4 | 350.00 | 4.42 | 5 |
| [SM–TIANA](https://www.google.com/maps/dir/?api=1&origin=28.4187622%2C-81.5783241&destination=28.4196285%2C-81.5849644&travelmode=walking) | 752.3 | 800.00 | 10.03 | 11 |
| [TRON–POTC](https://www.google.com/maps/dir/?api=1&origin=28.4199514%2C-81.5772546&destination=28.4181032%2C-81.584234&travelmode=walking) | 896.2 | 950.00 | 11.95 | 13 |
| [SM–BUZZ](https://www.google.com/maps/dir/?api=1&origin=28.4187622%2C-81.5783241&destination=28.418202%2C-81.5802262&travelmode=walking) | 224.6 | 250.00 | 2.99 | 3 |
| [BTMR–TIANA](https://www.google.com/maps/dir/?api=1&origin=28.4197246%2C-81.5845775&destination=28.4196285%2C-81.5849644&travelmode=walking) | 63.5 | 76.00 | 0.85 | 1 |

IDs and attraction names appear together in the workbook. PP–IASW and SDMT–POOH were displayed as 59 ft and 112 ft; these were converted using 1 ft = 0.3048 m. Extra decimal places do not imply measurement precision.

## Interpretation

The sample supports approximate network agreement at the requested coordinates. The largest percentage distance difference was **34.5%** for SDMT–POOH, equivalent to **11.8 m**. POTC–JC differed by **31.2%**, or **23.7 m**. These discrepancies were retained.

This is a purposive sample, not a test of all 66 attraction pairs. Google rounds displayed values and may snap coordinates to its network or label them as nearby businesses. Neither the true attraction entrance/exit locations nor Disney App estimates were independently validated. These results therefore support an initial planning model, not a claim of field accuracy.
