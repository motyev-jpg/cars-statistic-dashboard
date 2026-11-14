# Cars Statistic Dashboard

Static dashboard showing how many new passenger cars were delivered in Israel each year, for the 4 leading brands, over the last 10 years (2017-2026, current year partial).

Live: https://motyev-jpg.github.io/cars-statistic-dashboard/

## Features
- Yearly deliveries per brand: grouped bar chart or line chart (toggle).
- Summary tiles with the 10-year total per brand.
- Table with yearly values and totals.
- Hebrew, RTL, light/dark aware. No backend.

## Data
- Source: [data.gov.il](https://data.gov.il) vehicle registry, resource `053cea08-09bc-40ec-8f7a-156f0677aff3`.
- "Delivered" = year of first on-road date (`moed_aliya_lakvish`), passenger cars only (`sug_degem = P`).
- Brands are merged across manufacturing countries. Top 4 = highest total deliveries in the period (currently Hyundai, Toyota, Kia, Skoda).
- Limitation: the registry holds only currently registered vehicles, so older years are slightly undercounted.

## Setup and run
Requires Python 3 (standard library only).

```
python fetch_data.py    # refreshes data/deliveries.json and data/deliveries.js
```

Then open `index.html` in a browser (Chart.js is loaded from a CDN, so internet access is needed).

## Configuration
Edit constants at the top of `fetch_data.py`: `TOP_N` (number of brands), `CANDIDATES` (brands checked), and the year range (last 10 years up to the current year).

## Structure
```
index.html          dashboard page
fetch_data.py       pulls counts from the data.gov.il API
data/deliveries.*   generated data (JSON and JS copy for opening from disk)
concept.md          what we build
practice.md         how we work
```
