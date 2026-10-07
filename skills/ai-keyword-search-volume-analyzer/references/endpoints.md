# DataForSEO Endpoint — AI Keyword Search Volume

This skill uses **one** DataForSEO endpoint (plus one utility for locale validation).
Every tool name is prefixed with the DataForSEO MCP id in your session, e.g.
`mcp__<id>__ai_optimization_keyword_data_search_volume`.

---

## Main — AI Keyword Search Volume

**MCP tool:** `ai_optimization_keyword_data_search_volume`
**REST equivalent:** `POST https://api.dataforseo.com/v3/ai_optimization/ai_keyword_data/keywords_search_volume/live`

What it returns: for each keyword, its estimated usage inside AI assistants / LLMs
(`ai_search_volume`) and a month-by-month history (`ai_monthly_searches`).

Call it through whichever connected DataForSEO MCP exposes it. **Don't hardcode the tool
name or server prefix, and don't rely on the connector's local label** — identify the MCP
by the shape of its tools. More than one DFS MCP may be connected, in one of two shapes
(see SKILL.md Step 3a):

- **Generic-proxy MCP — preferred.** An `api_request` tool that calls any DataForSEO path.
  Call: `method: "POST"`,
  `path: "/v3/ai_optimization/ai_keyword_data/keywords_search_volume/live"`,
  `data: [ { "language_code", "location_name", "keywords": [...] } ]`
  (the body is the array shown below). It also ships `docs_search` / `docs_index` helpers
  for looking up any endpoint's parameters. Use this whenever it's connected.
- **Named-endpoint MCP — fallback.** A dedicated tool
  `ai_optimization_keyword_data_search_volume` (params `keywords`, `language_code`,
  `location_name`). Use it only when no proxy is connected.

Both hit the same endpoint and return the same data. Then save the response to a file and
let `scripts/build_report.py` extract the fields — don't transcribe the response by hand.
The script already tolerates both output shapes (the raw `tasks[].result[].items` envelope
that the proxy returns, and a flattened list), so it works no matter which variant
returned the data.

### Request parameters

| Parameter | Required | Notes |
|-----------|----------|-------|
| `keywords` | yes | Array of keyword strings. **Max 1000 per request** — batch beyond that. |
| `language_code` | yes | e.g. `en`, `es`, `de`. |
| `location_name` | no (default `United States`) | Full location name, e.g. `United States`, `United Kingdom`. |

Example MCP call:

```
keywords:      ["iphone", "seo"]
language_code: "en"
location_name: "United States"
```

Equivalent REST body:

```json
[
  { "language_code": "en", "location_code": 2840, "keywords": ["iphone", "seo"] }
]
```

(The MCP tool takes `location_name`; the REST API also accepts `location_code` — e.g.
`2840` = United States. Use `location_name` with the MCP tool.)

### Response — where the data lives

The per-keyword records are under **`tasks[0].result[0].items`**. The MCP tool may hand
you the parsed object directly — in that case, find the `items` array. For each item,
read exactly:

| Field | → Output |
|-------|----------|
| `keyword` | `Keyword` column |
| `ai_search_volume` | `AI SV` column (current AI search volume) |
| `ai_monthly_searches[]` | Monthly trend columns — each entry is `{ year, month, ai_search_volume }` |

Example item:

```json
{
  "keyword": "seo",
  "ai_search_volume": 13881,
  "ai_monthly_searches": [
    { "year": 2026, "month": 7, "ai_search_volume": 13881 },
    { "year": 2026, "month": 6, "ai_search_volume": 13560 },
    { "year": 2026, "month": 5, "ai_search_volume": 14628 }
  ]
}
```

`build_report.py` does this extraction in code: from the saved response it keeps only
`keyword`, `ai_search_volume` and `ai_monthly_searches` — the other fields
(`search_partners`, `location_code`, `language_code`, …) are dropped — then turns each
`ai_monthly_searches` entry into a column headed `AI SV <year>-<month>` (e.g.
`AI SV 2026-7`), unioned across all keywords and ordered newest month first. You don't
need to pick out fields yourself; just save the response and run the script.

---

## Utility — locations & languages (optional)

**MCP tool:** `ai_opt_kw_data_loc_and_lang` (no arguments)

Returns the valid locations and languages for the AI Keyword Data endpoint. Call it only
when a user's location or language is ambiguous or you're unsure it's supported — confirm
the match before spending credits. No need to call it for obvious cases like
`United States` / English.
