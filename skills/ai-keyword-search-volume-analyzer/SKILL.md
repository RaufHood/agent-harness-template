---
name: ai-keyword-search-volume-analyzer
description: >
  Pulls AI Search Volume for a keyword list from the DataForSEO AI Keyword Search
  Volume API and returns a prioritized opportunity list — keywords sorted by how
  often they're searched inside AI assistants (LLMs), highest first, with each
  keyword's monthly AI-search history spread across trend columns. Use whenever a
  user wants AI / LLM search volume for keywords: "pull AI search volume for these
  keywords", "how much are these terms searched in AI / ChatGPT", "AI keyword
  volume", "LLM search demand for my list", "rank these keywords by AI search
  volume", "which topics get the most AI searches", "AI SV for this list", or when
  they hand over a keyword list (pasted, or a .txt/.csv/.xlsx file) and ask which
  topics matter most for AI/LLM visibility. Prompts for the list, market and
  language, batches them to DataForSEO, then writes a sorted CSV plus a chat
  summary. This is AI/LLM search volume, not Google Ads search volume;
  for classic Google volume/CPC use a Google Ads skill.
---

# AI Keyword Search Volume Analyzer

## What This Skill Produces

| Output | What it is |
|--------|-----------|
| `ai_search_volume_[YYYYMMDD].csv` | One row per keyword — `Keyword, Location, Language, AI SV`, then one trend column per month (`AI SV 2026-7`, `AI SV 2026-6`, …), newest month first. **Sorted by AI SV, highest first** — the top rows are the biggest AI-search opportunities. |
| Chat summary | Keyword count, the top opportunities by AI SV, the month range covered, and the `Data collected via DataForSEO` note — printed in chat, not in the file. |

**What "AI SV" means:** `ai_search_volume` is DataForSEO's estimate of how often a
keyword is searched **inside AI assistants / LLMs** (e.g. ChatGPT-style tools) — a
demand signal for AI/GEO visibility work. It is a different metric from Google Ads
search volume; do not mix the two.

---

## The Workflow (at a glance)

```
Read keywords (paste / .txt / .csv / .xlsx)
   → confirm Location + Language
   → batch (≤1000 per request) → DataForSEO AI Keyword Search Volume API
   → extract keyword, ai_search_volume, ai_monthly_searches
   → sort by ai_search_volume DESC, pivot months into columns
   → write CSV + chat summary
```

**Keep the token cost down by doing the extraction in code.** The DataForSEO response is
verbose — a monthly history plus service fields per keyword. Do **not** re-read it,
hand-pick fields, or re-type it into a table. Instead, save what the MCP tool returned to
a file and let `scripts/build_report.py` pull out the three fields it needs, drop the
rest, pivot, sort, and write the CSV. Your only job with the response is to pass it
through to the file once.

---

## Prerequisites

- A **DataForSEO MCP** must be connected and authenticated. More than one DFS MCP may be
  connected — the skill finds the AI Keyword Search Volume tool by name rather than by a
  fixed prefix (Step 3a), so either variant works. If a tool call returns a 401 or
  credential error, stop and say: "Please connect and authenticate the DataForSEO MCP,
  then retry." Do not fabricate volumes.
- Python 3 (standard library only) builds the CSV.

---

## Interaction Rules

Ask for missing inputs **one at a time**, and wait for the answer before moving on — a
wrong market or language silently changes every number, so it's worth confirming rather
than guessing. Fixed choices (e.g. picking the resolved location from candidates) → use
`AskUserQuestion`. The keyword list and free-text answers → ask in plain text.

If the user's very first message already contains the keywords, the market, and the
language, don't re-ask — confirm you've got them and go.

---

## Step 1 — Read the Keywords

Accept any of these, in order of what the user offers:

- **Pasted text** — one keyword per line, or comma-separated.
- **A file path** in the project folder — `.txt`, `.csv`, or `.xlsx`. Read it and pull
  the keyword column (for CSV/XLSX, the column named `Keyword` if present, else the
  first column; skip the header row and blank cells).
- **Google Sheets** — read it directly if you have any way in, and only ask the user to
  paste/export as a last resort. In order of preference: (1) a connected Google
  Sheets / Drive tool, if one is available in the session; (2) the browser, when the user
  is signed in to Google — open the sheet URL and read the keyword column; (3) a
  link-shared or public sheet — fetch its CSV export
  (`https://docs.google.com/spreadsheets/d/<ID>/export?format=csv&gid=<GID>`). Only if
  none of these reach the sheet (no connector, no signed-in browser, link not shared) ask
  the user to paste the keywords or share/export the sheet. Note: it's *reading the sheet*
  that needs the access — the DataForSEO tool itself never touches Sheets.

Normalize lightly: trim whitespace, drop blank lines and exact duplicates. Keep the
user's wording otherwise — these are the exact strings sent to the API. Store as
`keywords` and remember `input_count`.

If no usable keyword remains, stop and ask for a real list — never send an empty request.

## Step 2 — Confirm Location & Language

The API needs a **location** and a **language**. Ask for them (unless already given):

- **Location** — a full country/location name, e.g. `United States`, `United Kingdom`.
  The API parameter is `location_name` (default `United States`).
- **Language** — resolve to a `language_code`, e.g. English → `en`, Spanish → `es`.

If you're unsure a location or language is supported, call
`ai_opt_kw_data_loc_and_lang` (no arguments) to list the valid locations and languages,
and confirm the best match with the user via `AskUserQuestion` before spending credits.
Store `location_name`, `language_code`, and human-readable `location` / `language`
labels (these labels go into the output's Location/Language columns).

## Step 3 — Fetch via the MCP tool

### 3a. Find the AI Keyword Search Volume tool (works with either DataForSEO MCP)

More than one DataForSEO MCP may be connected, and the server-id prefix differs per
connection — so **don't hardcode a tool name or rely on the connector's local label**
(those are user-chosen and not portable). Identify the MCP by the *shape of the tools* it
exposes. Two shapes exist and this skill supports both:

- **Generic-proxy MCP — prefer this one.** It exposes an `api_request` tool that can call
  any DataForSEO path (plus `docs_*` helpers), rather than a tool per endpoint. It's the
  newer, more capable shape, so use it whenever it's connected. Call it as in **3b
  (generic proxy)** below.
- **Named-endpoint MCP — fallback.** It exposes a dedicated per-endpoint tool: match a
  tool whose name (after the `mcp__<server-id>__` prefix) is exactly
  `ai_optimization_keyword_data_search_volume`, or that contains both `ai_keyword_data`
  and `keywords_search_volume`. Use it as in **3b (named tool)** below.

**Selection rule:** if an `api_request` proxy tool is connected, use it. Otherwise use the
named-endpoint tool. To check, run a quick tool search for `api_request` (finds the proxy)
and for `ai_keyword_data keywords_search_volume` (finds the named tool). If neither is
available, stop and tell the user no AI Keyword Search Volume tool is available on any
connected DataForSEO MCP.

### 3b. Call it (batch to ≤1000 keywords)

The API accepts **up to 1000 keywords per request**. If `keywords` has more than 1000,
split into batches of 1000 and call once per batch — one call per batch, either way.

**Generic proxy (`api_request`) — preferred.** POST the endpoint path with the DataForSEO
task body (note: `data` is an **array of task objects**):

```
<the api_request tool>
  method: "POST"
  path:   "/v3/ai_optimization/ai_keyword_data/keywords_search_volume/live"
  data:   [ { "language_code": "<language_code>",
             "location_name":  "<location_name>",
             "keywords":       [ ...up to 1000 keywords... ] } ]
```

**Named tool — fallback (when no proxy is connected):**

```
<the matched tool>
  keywords:       [ ...up to 1000 keywords... ]
  location_name:  "<location_name>"      # e.g. "United States"
  language_code:  "<language_code>"      # e.g. "en"
```

The proxy returns the raw REST response (`tasks[].result[].items`); the named tool returns
the same data, sometimes already flattened. Either way, save what comes back and let
`scripts/build_report.py` extract it — it handles both shapes.

**Parameter variants:** most builds take `keywords` + `language_code` + `location_name`.
If a build instead wants `location_code` (e.g. `2840` = United States) or `language_name`
(e.g. `English`), supply those — resolve codes via `ai_opt_kw_data_loc_and_lang` (named
MCP) or a `docs_search` lookup (proxy). Pass only the fields the chosen call actually
accepts.

## Step 4 — Save the Response and Build the CSV (extraction in code)

Don't parse the response by hand — the build script does the extraction, so you spend
no tokens transcribing monthly numbers into a table.

Save what the tool returned to a JSON file (e.g. `response.json`). **Pass it through as-is
— do not hand-edit or re-key it.** The script accepts the response in whatever shape the
tool gives you: the raw envelope with `tasks[].result[].items`, a `result` object, or a
bare list of items. It keeps only `keyword`, `ai_search_volume`, and
`ai_monthly_searches`, drops every other field, pivots the months into columns, sorts by
AI SV descending, and puts any no-volume keyword at the bottom with blank cells.

- **One batch:** save the tool result to `response.json`.
- **Several batches:** collect the returned items into one JSON list `[ item, item, … ]`
  and save that — the script reads a bare list too.

Then run (`--location` / `--language` are the labels for the CSV's Location / Language
columns — use the human-readable values from Step 2):

```bash
python scripts/build_report.py \
  --input response.json \
  --out ai_search_volume_[YYYYMMDD].csv \
  --location "<location>" \
  --language "<language>"
```

The script prints a compact summary (keyword count, how many had AI SV, the top keywords)
— read that; you don't need to open the CSV or re-read the response. Save the file to the
user's chosen folder (default: current project folder).

If the API returns no data for a keyword, it's kept with an empty AI SV — never guess.
See `references/endpoints.md` for the request/response shape and field paths.

The output columns are `Keyword, Location, Language, AI SV`, then one column per month
present in the data (`AI SV 2026-7`, `AI SV 2026-6`, …) newest first.

## Step 5 — Deliver the Summary

Print a short summary in chat (keep the file itself clean — no notes or takeaway rows in
the CSV):

```
─────────────────────────────────────────────
AI SEARCH VOLUME — [location] / [language]
[run_date]
─────────────────────────────────────────────
Keywords:      [input_count] in  →  [output_count] with data
Month range:   [oldest] … [newest]

TOP OPPORTUNITIES (by AI Search Volume)
  #   Keyword                       AI SV
  ─────────────────────────────────────────
  1.  [keyword]                     [ai_sv]
  ...  (up to 10)

[if any keyword had no data: "[n] keyword(s) returned no AI search volume — kept at the
bottom of the sheet with blank values."]

File: [csv_path]

Data collected via DataForSEO
─────────────────────────────────────────────
```

---

## Error Handling

| Situation | Action |
|-----------|--------|
| No AI Keyword Search Volume tool on any connected DFS MCP | Stop. Tell the user no matching tool is available and ask them to connect a DataForSEO MCP that exposes it. |
| DataForSEO 401 / credential error | Stop immediately. Ask the user to connect/re-authenticate the DataForSEO MCP, then retry. |
| Empty keyword list after Step 1 | Stop. Do not call the API. Ask for a real list. |
| Location or language won't resolve | Call `ai_opt_kw_data_loc_and_lang`, present valid options, confirm before spending credits. |
| >1000 keywords | Split into batches of 1000; one MCP call per batch; save the combined items as one JSON list for the script. |
| A keyword returns no `ai_search_volume` | Keep it, leave the AI SV cell blank, count it in the summary — never estimate. |
| Google Sheets as input | Read it directly if you can (Sheets/Drive tool, signed-in browser, or a link-shared/public CSV export). Only ask the user to paste or export when none of those reach the sheet. Output stays CSV. |

---

## Reference Files

- `references/endpoints.md` — the DataForSEO AI Keyword Search Volume endpoint: request
  parameters, batching limit, and the exact response field paths. Read it before the
  first fetch.
