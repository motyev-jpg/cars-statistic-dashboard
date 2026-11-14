"""Fetch yearly passenger-car deliveries for the top 4 brands from data.gov.il.

"Delivered" = first on-road date (moed_aliya_lakvish) year, passenger cars only.
Output: data/deliveries.json
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

API = "https://data.gov.il/api/3/action/datastore_search"
RESOURCE = "053cea08-09bc-40ec-8f7a-156f0677aff3"
TOP_N = 4
CANDIDATES = 10  # brands by fleet size that are checked for yearly deliveries
END_YEAR = date.today().year
START_YEAR = END_YEAR - 9
OUT = Path(__file__).parent / "data" / "deliveries.json"

# Brands whose name is more than one word (everything else = first word).
MULTI_WORD = ("לנד רובר", "מרצדס בנץ", "אלפא רומיאו", "אלפא רומיאו", "דאצ'יה", "סאנג יונג", "רנו סמסונג", "מיני")


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
    name = name.strip()
    for b in MULTI_WORD:
        if name.startswith(b):
            return b
    return name.split(" ")[0]


def count(codes, months=None):
    filters = {"sug_degem": "P", "tozeret_cd": codes}
    if months:
        filters["moed_aliya_lakvish"] = months
    res = call({"resource_id": RESOURCE, "limit": 0, "filters": json.dumps(filters)})
    return res["total"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    # 1. manufacturer codes -> brand
    res = call({
        "resource_id": RESOURCE,
        "limit": 5000,
        "fields": "tozeret_cd,tozeret_nm",
        "distinct": "true",
        "filters": json.dumps({"sug_degem": "P"}),
    })
    codes = defaultdict(list)
    for rec in res["records"]:
        codes[brand_of(rec["tozeret_nm"])].append(rec["tozeret_cd"])
    print(len(codes), "brands")

    # 2. candidate brands by total fleet size
    fleet = {b: count(c) for b, c in codes.items()}
    candidates = sorted(fleet, key=fleet.get, reverse=True)[:CANDIDATES]
    print("candidates:", candidates)

    # 3. deliveries per year for candidates
    years = list(range(START_YEAR, END_YEAR + 1))
    data = {}
    for b in candidates:
        data[b] = {}
        for y in years:
            months = [f"{y}-{m}" for m in range(1, 13)]
            data[b][y] = count(codes[b], months)
        print(b, sum(data[b].values()))

    # 4. top brands by total deliveries in the period
    top = sorted(data, key=lambda b: sum(data[b].values()), reverse=True)[:TOP_N]
    out = {
        "source": "data.gov.il, vehicle registry (resource " + RESOURCE + ")",
        "definition": "Passenger cars (sug_degem=P) by year of first on-road date (moed_aliya_lakvish); currently registered vehicles only",
        "generated": date.today().isoformat(),
        "partial_year": END_YEAR,
        "years": years,
        "brands": [{"name": b, "deliveries": [data[b][y] for y in years]} for b in top],
    }
    OUT.parent.mkdir(exist_ok=True)
    text = json.dumps(out, ensure_ascii=False, indent=2)
    OUT.write_text(text, encoding="utf-8")
    # Same data as a script, so index.html also works when opened from disk.
    OUT.with_suffix(".js").write_text("window.DELIVERIES = " + text + ";\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
