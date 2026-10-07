# AI Keyword Search Volume Analyzer

Sends a keyword list to the **DataForSEO AI Keyword Search Volume API** and turns the
result into a **prioritized opportunity list** — keywords sorted by how often they're
searched inside AI assistants (LLMs), highest first, with each keyword's monthly AI-search
history spread across trend columns.

"AI SV" here is **AI/LLM search demand** (a GEO / AI-visibility signal), *not* Google Ads
search volume — a different metric with a different endpoint.

---

## What it does

```
Read keywords (paste / .txt / .csv / .xlsx)
   → confirm Location + Language
   → batch (≤1000/request) → DataForSEO AI Keyword Search Volume API
   → extract keyword, ai_search_volume, ai_monthly_searches   (done in code)
   → sort by AI SV DESC, pivot months into columns
   → write CSV + chat summary
```

**Extraction happens in code.** The DataForSEO response is verbose (a monthly history plus
service fields per keyword). Rather than re-read it or hand-build the table, the skill
saves the MCP tool's response to a file and lets `scripts/build_report.py` keep only the
three fields it needs, drop the rest, pivot, sort, and write the CSV — so the model spends
no tokens transcribing numbers, and only a short summary comes back.

**Output per run:**

| Output | What it is |
|--------|-----------|
| `ai_search_volume_[YYYYMMDD].csv` | `Keyword, Location, Language, AI SV`, then one column per month (`AI SV 2026-7`, `AI SV 2026-6`, …), newest first. Sorted by AI SV, highest first. |
| Chat summary | Keyword count, top opportunities, month range, DataForSEO note. |

---

## Prerequisites

- A **DataForSEO MCP** connected and authenticated. A 401 means: connect/re-authenticate, then retry.
- Python 3 (standard library) — the CSV is written directly, no extra packages.

**Works with either DataForSEO MCP variant** — the skill identifies the MCP by the *shape
of its tools* (not the connector's local name) and finds the tool at runtime, so it doesn't
matter which connector you have or how it's labelled. If both are connected, the generic
proxy is preferred:

| MCP shape | Priority | How the skill calls it |
|-----------|----------|------------------------|
| **Generic proxy** (`api_request` tool) | preferred | `api_request` → `POST /v3/ai_optimization/ai_keyword_data/keywords_search_volume/live` |
| **Named-endpoint** (per-endpoint tools) | fallback | the `ai_optimization_keyword_data_search_volume` tool |

Both hit the same endpoint and return the same data; `build_report.py` parses either output shape.

---

## How to trigger it

- *"Pull AI search volume for these keywords"*
- *"How much are these terms searched in AI / ChatGPT?"*
- *"Rank this keyword list by AI search volume"*
- *"Which of these topics get the most AI searches?"*
- *"AI SV for this list — United States, English"*

The skill asks for the market and language if you don't give them, and confirms an
ambiguous locale before spending credits.

---

## Inputs

| Input | Default | Notes |
|-------|---------|-------|
| Keywords | — | Required. Paste (one per line / comma-separated) or a `.txt`/`.csv`/`.xlsx` path. |
| Location | United States | Full country name (`location_name`). |
| Language | — | e.g. English → `en`. |
| Output | current project folder | CSV. |

Google Sheets is read directly when there's a way in — a connected Sheets/Drive tool, a
signed-in browser session, or a link-shared/public sheet's CSV export. Only if none of
those reach the sheet do you paste or export it. (The DataForSEO tool never touches
Sheets; it's the *reading* that needs access.)

---

## Files

```
ai-keyword-search-volume-analyzer/
├── SKILL.md                  — skill instructions (read by Claude Code)
├── README.md                 — this file
├── references/
│   └── endpoints.md          — the AI Keyword Search Volume endpoint + field paths
└── scripts/
    └── build_report.py       — extracts fields, pivots months into columns, sorts, writes the CSV
```

## The script, standalone

`build_report.py` reads the saved DataForSEO/MCP response (raw `tasks[].result[].items`
envelope, a `result` object, a bare list of items, or the compact
`{location, language, items}` shape — extraction is done in code) and writes the sorted
sheet:

```bash
python scripts/build_report.py --input response.json --out ai_search_volume.csv \
  --location "United States" --language English
```
