# Exercises

Four tasks, each building on the last.
You don't have to write anything by hand — ask your agent to do it.
Copy a prompt, paste it into Claude Code / Codex / Cursor, adapt it.

---

## Task 1 — Give your agent an identity (5 min)

Fill in sections 1, 2 and 7 of `AGENTS.md`: name, role, tone, about you, rules.

> **Prompt:**
> Interview me with 5 short questions, one at a time, then fill in sections 1, 2 and 7 of AGENTS.md with my answers.

**Done when:** you ask "Who are you?" and the agent answers with its new name and role.

---

## Task 2 — Create your first skill (15 min)

A skill = a reusable set of instructions in `skills/<name>/SKILL.md`.

👀 Look at the examples first:
- `skills/doc-creator/` — instructions + a script, branded as Blinkwise (try: *"Create a one-page PDF for Blinkwise users explaining the 20-20-20 rule"*)
- `skills/ai-keyword-search-volume-analyzer/` — downloaded from DataForSEO, uses an API via MCP (needs a DataForSEO account)

Then pick one idea below, bring your own, or download one (e.g. [DataForSEO AI skills](https://dataforseo.com/templates/ai-skills/)) and adapt it.

| Idea | What it does |
|---|---|
| `linkedin-post` | Turns a rough idea into a post in *your* voice |
| `meeting-notes` | Messy notes → decisions, action items, owners |
| `email-reply` | Drafts a reply in your tone, asks before anything is sent |

> **Prompt:**
> Create a skill called `<name>` using `templates/skill.md`. It should `<what it does>`. Ask me 3 questions first to make it specific to me. Save it to `skills/<name>/SKILL.md` and add it to the Skills table in AGENTS.md.

**Done when:** a new chat with a matching request (e.g. "write a LinkedIn post about …") uses your skill without you naming it.

> 💡 The `description` line decides whether the skill gets picked. If it doesn't trigger, improve that line.

---

## Task 3 — Create your first subagent (15 min)

A subagent = a specialist with its own fresh context, in `agents/<name>.md`.

👀 Look at the example first: `agents/critic.md` (try: *"Use the critic to review my AGENTS.md"*).
Then pick one idea below, or bring your own.

| Idea | What it does |
|---|---|
| `fact-checker` | Flags every claim that needs a source |
| `devils-advocate` | Argues against your plan |
| `simplifier` | Cuts any text by 50% without losing meaning |
| `customer-persona` | Reacts to your text as your target customer would |

> **Prompt:**
> Create a subagent called `<name>` using `templates/subagent.md`. It should `<what it does>`, and return `<format, e.g. max 3 bullet points>`. Save it to `agents/<name>.md` and add it to the Subagents table in AGENTS.md.

Then try it:

> Use the `<name>` subagent to review the skill you made in task 2.

**Done when:** you can see the subagent run separately (Claude Code shows it as a separate task).

---

## Task 4 — Build a workflow (20 min)

A workflow = several agents in a fixed order, each handing over to the next.
👀 Run the example first: `workflows/research-and-write.md` (**researcher → writer → critic**).

> Run the research-and-write workflow on "`<your topic>`" as a `<LinkedIn post / blog article / briefing>`.

Then build your own, reusing your skill and subagent from tasks 2 and 3:

> **Prompt:**
> Using `templates/workflow.md`, create a workflow called `<name>` that `<goal>`. Steps: `<agent A>` → `<agent B>` → `<my subagent from task 3>`. Create any missing subagents in `agents/`. Save it to `workflows/<name>.md` and register everything in AGENTS.md.

Ideas: *idea → critic → doc-creator PDF*, *meeting notes → action items → follow-up email*, *competitor research → SWOT → one-pager*.

**Done when:** your workflow runs end to end and saves a result in `output/`.

**Go further:** add a step (e.g. SEO reviewer), run steps in parallel, or let the writer use your skill from task 2.

---

## Bonus — Connect a tool via MCP: Context7

Context7 gives your agent up-to-date documentation for any library or tool.

**Claude Code** (in your terminal):

```bash
claude mcp add --transport http context7 https://mcp.context7.com/mcp
```

**Codex** (in your terminal):

```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

**Cursor:** create `.cursor/mcp.json`:

```json
{ "mcpServers": { "context7": { "url": "https://mcp.context7.com/mcp" } } }
```

Restart your tool, then try:

> Use context7 to look up how to build a simple chart in Python with matplotlib.

**Done when:** the agent calls a `context7` tool instead of guessing from memory.
