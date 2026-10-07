#!/usr/bin/env python3
"""Build a prioritized AI Search Volume report from DataForSEO
AI Keyword Search Volume results.

This owns *all* the deterministic work so it happens in code, not in the model's
head: it reads whatever the DataForSEO / MCP call returned, pulls out only
``keyword`` / ``ai_search_volume`` / ``ai_monthly_searches`` (dropping every other
field), pivots each keyword's monthly history into one column per month, sorts
keywords by current AI Search Volume (highest first), and writes a clean CSV. That
way the caller just saves the tool's response to a file and runs this — no
hand-extraction, no hand-built table.

Accepted --input shapes (any of these — the extraction is done here):

  * The raw response, with ``tasks[].result[].items`` (what the DataForSEO API /
    MCP tool returns).
  * A ``result`` object, or a list of ``result`` objects, each holding ``items``.
  * A bare list of item objects.
  * The compact shape ``{"location", "language", "items": [...]}``.

Any of the item objects may carry extra fields (``search_partners``,
``location_code``, …) — they're ignored. Each item needs ``keyword``,
``ai_search_volume``, and ``ai_monthly_searches`` (a list of
``{year, month, ai_search_volume}``).

Location / Language for the output columns come from ``--location`` / ``--language``
(preferred) or, if absent, from a compact-shape payload; else left blank.

Output columns:
    Keyword, Location, Language, AI SV, AI SV <YYYY-M> ...  (months, newest first)

Rows are sorted by AI SV descending. Keywords with no volume sort to the bottom
with a blank AI SV cell — values are never invented.

Usage:
    python build_report.py --input response.json --out ai_search_volume.csv \
        --location "United States" --language English
"""
import argparse
import csv
import json


def month_label(year, month):
    return f"AI SV {int(year)}-{int(month)}"


def _iter_raw_items(data):
    """Yield item dicts from any of the accepted shapes, digging through the
    DataForSEO envelope (tasks -> result -> items) when present."""
    if isinstance(data, list):
        for el in data:
            yield from _iter_raw_items(el)
        return
    if not isinstance(data, dict):
        return
    if "tasks" in data:
        for task in data.get("tasks") or []:
            for result in (task or {}).get("result") or []:
                yield from _iter_raw_items(result)
        return
    if "result" in data and "items" not in data:
        for result in data.get("result") or []:
            yield from _iter_raw_items(result)
        return
    if "items" in data:
        for it in data.get("items") or []:
            if isinstance(it, dict):
                yield it
        return
    # A single item object (has a keyword and no nesting).
    if "keyword" in data:
        yield data


def _extract(it):
    """Keep only the fields the report needs; drop everything else in code."""
    return {
        "keyword": it.get("keyword"),
        "ai_search_volume": it.get("ai_search_volume"),
        "ai_monthly_searches": [
            {
                "year": m.get("year"),
                "month": m.get("month"),
                "ai_search_volume": m.get("ai_search_volume"),
            }
            for m in (it.get("ai_monthly_searches") or [])
        ],
    }


def load_items(path, location=None, language=None):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    # Locale from the compact shape, unless overridden on the CLI.
    loc = location
    lang = language
    if isinstance(data, dict):
        loc = location if location is not None else data.get("location", "")
        lang = language if language is not None else data.get("language", "")
    items = [_extract(it) for it in _iter_raw_items(data)]
    return {"location": loc or "", "language": lang or "", "items": items}


def collect_month_columns(items):
    """Union of every (year, month) seen, sorted most-recent first."""
    seen = set()
    for it in items:
        for m in it.get("ai_monthly_searches") or []:
            y, mo = m.get("year"), m.get("month")
            if y is not None and mo is not None:
                seen.add((int(y), int(mo)))
    return sorted(seen, key=lambda ym: (ym[0], ym[1]), reverse=True)


def sort_key(it):
    """Highest AI SV first; missing volume sorts to the bottom."""
    v = it.get("ai_search_volume")
    return (0, 0) if v is None else (1, v)


def build_rows(payload):
    items = payload.get("items") or []
    location = payload.get("location", "") or ""
    language = payload.get("language", "") or ""
    months = collect_month_columns(items)

    header = ["Keyword", "Location", "Language", "AI SV"] + [month_label(y, m) for (y, m) in months]

    ordered = sorted(items, key=sort_key, reverse=True)
    rows = []
    for it in ordered:
        by_month = {}
        for m in it.get("ai_monthly_searches") or []:
            y, mo = m.get("year"), m.get("month")
            if y is not None and mo is not None:
                by_month[(int(y), int(mo))] = m.get("ai_search_volume")
        vol = it.get("ai_search_volume")
        row = [
            it.get("keyword", ""),
            location,
            language,
            "" if vol is None else vol,
        ]
        for (y, m) in months:
            val = by_month.get((y, m))
            row.append("" if val is None else val)
        rows.append(row)
    return header, rows


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True,
                    help="Path to the saved response / results JSON (any accepted shape).")
    ap.add_argument("--out", required=True, help="Path to write the CSV.")
    ap.add_argument("--location", help="Label for the Location column (e.g. 'United States').")
    ap.add_argument("--language", help="Label for the Language column (e.g. 'English').")
    args = ap.parse_args()

    payload = load_items(args.input, location=args.location, language=args.language)
    header, rows = build_rows(payload)
    write_csv(args.out, header, rows)

    month_cols = len(header) - 4
    with_data = sum(1 for r in rows if r[3] != "")
    print(f"Wrote {len(rows)} keywords x {month_cols} month column(s) to {args.out}")
    print(f"Keywords: {len(rows)} | with AI SV: {with_data}")
    if rows and rows[0][3] != "":
        print("Top by AI SV:")
        for r in rows[:10]:
            if r[3] == "":
                break
            print(f"  {r[3]}\t{r[0]}")


if __name__ == "__main__":
    main()
