"""Fetch yearly passenger-car deliveries from data.gov.il and find the top 4 brands per year.

"Delivered" = first on-road date (moed_aliya_lakvish) year, passenger cars only.
All brands are checked, so new entrants are not missed.
Output: data/deliveries.json and data/deliveries.js
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

API = "https://data.gov.il/api/3/action/datastore_search"
RESOURCE = "053cea08-09bc-40ec-8f7a-156f0677aff3"
TOP_N = 4
END_YEAR = date.today().year
START_YEAR = END_YEAR - 9
WORKERS = 8
OUT = Path(__file__).parent / "data" / "deliveries.json"

# Registry names are "<brand> <country>". Brands longer than one word, and spelling variants.
MULTI_WORD = ("ב מ וו", "בי ווי די", "מרצדס בנץ", "אלפא רומיאו", "מרוטי סוזוקי", "אף איי דבליו",
              "די אס", "לינק אנד קו", "קיי ג'י מובילי", "סאנג יונג")
ALIASES = {"אודי": "אאודי", "דאציה": "דאצ'יה", "מרוטי סוזוקי": "סוזוקי", "אלפא רומיאו_אי": "אלפא רומיאו",
           "ב מ וו": "BMW", "בי ווי די": "BYD", "אף איי דבליו": "FAW"}


def call(params):
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.load(r)["result"]
        except Exception as e:  # noqa: BLE001
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("API call failed: " + url)


def brand_of(name):
    name = name.strip().replace("-", " ")
    brand = next((b for b in MULTI_WORD if name.startswith(b)), name.split(" ")[0])
    return ALIASES.get(brand, brand)


def count(codes, months):
    filters = {"sug_degem": "P", "tozeret_cd": codes, "moed_aliya_lakvish": months}
    res = call({"resource_id": RESOURCE, "limit": 0, "filters": json.dumps(filters)})
    return res["total"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    res = call({
        "resource_id": RESOURCE,
        "limit": 5000,
        "fields": "tozeret_cd,tozeret_nm",
        "distinct": "true",
        "filters": json.dumps({"sug_degem": "P"}),
    })
    codes = defaultdict(set)
    for rec in res["records"]:
        codes[brand_of(rec["tozeret_nm"])].add(rec["tozeret_cd"])
    codes = {b: sorted(c) for b, c in codes.items()}
    print(len(codes), "brands")

    years = list(range(START_YEAR, END_YEAR + 1))
    jobs = [(b, y) for b in codes for y in years]

    def run(job):
        b, y = job
        return job, count(codes[b], [f"{y}-{m}" for m in range(1, 13)])

    data = defaultdict(dict)
    with ThreadPoolExecutor(WORKERS) as ex:
        for (b, y), n in ex.map(run, jobs):
            data[b][y] = n

    top_by_year = [sorted(data, key=lambda b: data[b][y], reverse=True)[:TOP_N] for y in years]
    in_top = {b for t in top_by_year for b in t}
    brands = sorted(in_top, key=lambda b: sum(data[b].values()), reverse=True)
    for y, t in zip(years, top_by_year):
        print(y, [(b, data[b][y]) for b in t])

    out = {
        "source": "data.gov.il, vehicle registry (resource " + RESOURCE + ")",
        "definition": "Passenger cars (sug_degem=P) by year of first on-road date (moed_aliya_lakvish); currently registered vehicles only",
        "generated": date.today().isoformat(),
        "partial_year": END_YEAR,
        "years": years,
        "brands": [{"name": b, "deliveries": [data[b][y] for y in years]} for b in brands],
        "top_by_year": top_by_year,
    }
    OUT.parent.mkdir(exist_ok=True)
    text = json.dumps(out, ensure_ascii=False, indent=2)
    OUT.write_text(text, encoding="utf-8")
    # Same data as a script, so index.html also works when opened from disk.
    OUT.with_suffix(".js").write_text("window.DELIVERIES = " + text + ";\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
