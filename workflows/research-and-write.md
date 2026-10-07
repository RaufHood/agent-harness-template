---
name: research-and-write
description: Researches a topic, writes a text about it, and reviews it until it's good. Use when the user asks for a researched article, post, briefing or summary on a topic.
---

# Research and write

**Input:** a topic + format (e.g. "LinkedIn post about AI agents in retail")
**Output:** `output/<topic-slug>.md`

## Steps

| # | Who | Does | Hands over |
|---|---|---|---|
| 1 | `researcher` subagent | Finds 5-8 key facts + sources on the topic | research notes |
| 2 | `writer` subagent | Writes the text in the requested format from the notes | draft |
| 3 | `critic` subagent | Reviews the draft: `ship` or `revise` + max 3 fixes | feedback |
| 4 | `writer` subagent | If `revise`: applies the fixes, then back to step 3 | final text |

## Rules

- Each step is its own subagent (fresh context). Pass only the handover, not the whole chat.
- Max 2 review loops, then stop.
- Save the final text to the output path, then show me: the text, the critic's last verdict, and the sources.
- Want a PDF? Finish with the `doc-creator` skill.
