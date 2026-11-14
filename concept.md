# Concept: cars-statistic-dashboard

A static dashboard showing how many new passenger cars were delivered in Israel each year, for the 4 leading brands of each year, over the last 10 years (2017-2026, current year partial).

## Data
- Source: data.gov.il, vehicle registry, resource `053cea08-09bc-40ec-8f7a-156f0677aff3`.
- "Delivered" = year of first on-road date (`moed_aliya_lakvish`), passenger cars only (`sug_degem = P`).
- Brands are merged across manufacturing countries (e.g. "Honda UK" + "Honda Japan").
- All brands are checked for every year, so new entrants are never missed. Top 4 is computed per year.
- Limitation: the registry holds only currently registered vehicles, so older years are slightly undercounted.

## Parts
- `fetch_data.py`: pulls counts for all brands and years into `data/deliveries.json` and `data/deliveries.js`.
- `index.html`: per-year top 4 bar chart (brand-colored), per-brand trend lines, and a table. No backend.

## Out of scope
Commercial vehicles, used-car transfers, prices.
