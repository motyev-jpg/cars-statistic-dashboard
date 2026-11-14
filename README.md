# Cars Statistic Dashboard

Static dashboard showing how many new passenger cars were delivered in Israel each year, for the 4 leading brands of each year, over the last 10 years (2017-2026, current year partial).

Live: https://motyev-jpg.github.io/cars-statistic-dashboard/

## Features
- Top 4 brands per year: bar chart colored and labeled by brand.
- Trend view: lines per brand for every brand that reached the top 4 at least once.
- Summary tiles with the 10-year total per brand.
- Table with the top 4 and their values for each year.
- Hebrew, RTL, light/dark aware. No backend.

## Data
- Source: [data.gov.il](https://data.gov.il) vehicle registry, resource `053cea08-09bc-40ec-8f7a-156f0677aff3`.
- "Delivered" = year of first on-road date (`moed_aliya_lakvish`), passenger cars only (`sug_degem = P`).
- Brands are merged across manufacturing countries. All brands are checked for every year, so new entrants are never missed; the top 4 is computed per year (currently Hyundai, Toyota, Kia, Skoda, Mazda, BYD, Chery and Jaecoo appear).
- Limitation: the registry holds only currently registered vehicles, so older years are slightly undercounted.

## Setup and run
Requires Python 3 (standard library only).

```
python fetch_data.py    # refreshes data/deliveries.json and data/deliveries.js
```

Then open `index.html` in a browser (Chart.js is loaded from a CDN, so internet access is needed).

## Configuration
Edit constants at the top of `fetch_data.py`: `TOP_N` (brands per year), `WORKERS` (parallel API calls), and the year range (last 10 years up to the current year). Brand spelling variants are merged via `MULTI_WORD` and `ALIASES`.

## Structure
```
index.html          dashboard page
fetch_data.py       pulls counts for all brands from the data.gov.il API
data/deliveries.*   generated data (JSON and JS copy for opening from disk)
concept.md          what we build
practice.md         how we work
```
