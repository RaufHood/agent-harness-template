---
name: <workflow-name>
description: <When to run this workflow.>
---

# <Workflow name>

**Input:** <e.g. a topic>
**Output:** <e.g. `output/<topic>.md`>

## Steps

| # | Who | Does | Hands over |
|---|---|---|---|
| 1 | `researcher` subagent | Finds 5 key facts + sources on the topic | research notes |
| 2 | `writer` subagent | Writes <format> from the notes | draft |
| 3 | `reviewer` subagent | Critiques the draft: verdict `ship` or `revise` + feedback | feedback |
| 4 | `writer` subagent | If `revise`: improves the draft, back to step 3 | final text |

## Rules

- Each step is its own subagent (fresh context). Pass only the handover, not the whole chat.
- Max 2 review loops, then stop and show me the result.
- Save the final result to the output path above.
