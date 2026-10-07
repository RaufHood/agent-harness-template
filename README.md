# agent-harness

A minimal, almost empty template for building your own AI agent.
Works with **Claude Code**, **Codex** and **Cursor**.
You fill it with your identity, skills, subagents and workflows — by chatting with it.

## Quickstart

```bash
git clone https://github.com/RaufHood/agent-harness-template.git my-agent
cd my-agent
```

Open the folder in your tool of choice:

| Tool | How to start | Reads |
|---|---|---|
| Claude Code | `claude` in the folder | `CLAUDE.md` → `AGENTS.md` |
| Codex | `codex` in the folder | `AGENTS.md` |
| Cursor | Open folder, use the Agent chat | `AGENTS.md` |

The `doc-creator` example skill needs Python 3.

Then open **[EXERCISE.md](EXERCISE.md)** and start with task 1.

## Structure

```
my-agent/
├── AGENTS.md        # The brain: identity, rules, index of everything below
├── CLAUDE.md        # Imports AGENTS.md + guardrails + Claude Code specifics
├── .claude/         # settings.json (hard guardrails) + links to skills/ and agents/
├── EXERCISE.md      # Workshop tasks
├── skills/          # Skills: skills/<name>/SKILL.md      (examples: doc-creator, ai-keyword-search-volume-analyzer)
├── agents/          # Subagents: agents/<name>.md        (examples: critic, researcher, writer)
├── workflows/       # Workflows: workflows/<name>.md     (example: research-and-write)
├── templates/       # Starting points for skills, subagents, workflows
└── output/          # Where workflows save their results
```

`.claude/skills` and `.claude/agents` link to `skills/` and `agents/`, so Claude Code also discovers them natively.
The links are already in this repo.
To create them yourself in another project, run these from the repo root.

macOS / Linux:

```bash
mkdir -p .claude
```

```bash
ln -s ../skills .claude/skills
```

```bash
ln -s ../agents .claude/agents
```

Windows (Command Prompt as admin, or with Developer Mode on):

```bat
mkdir .claude
```

```bat
mklink /D .claude\skills ..\skills
```

```bat
mklink /D .claude\agents ..\agents
```

The target `../skills` is relative to the link's folder (`.claude/`), not to where you run the command.
Check with `ls -la .claude` — you should see `skills -> ../skills`.
On Windows, clone with `git clone -c core.symlinks=true https://github.com/RaufHood/agent-harness-template.git` so the existing links work.

## The 4 building blocks

| Block | What it is | Example |
|---|---|---|
| **AGENTS.md** | Always-loaded memory: who the agent is, how it works | "You are Max, a marketing assistant…" |
| **Skill** | Reusable instructions, loaded only when needed | "How to write a LinkedIn post in my voice" |
| **Subagent** | Specialist with its own fresh context window | A critic that reviews any text |
| **Workflow** | Several agents in a fixed order | researcher → writer → reviewer |

## Don't start from zero

You can download ready-made skills and drop them into `skills/`:

- [DataForSEO AI skills](https://dataforseo.com/templates/ai-skills/) — SEO & keyword skills (our `ai-keyword-search-volume-analyzer` comes from there)

Read every downloaded skill before using it — it's instructions your agent will follow.

## AGENTS.md vs CLAUDE.md

- **AGENTS.md** = the one file all tools share. Put everything here.
- **CLAUDE.md** = imports AGENTS.md (`@AGENTS.md`) + only Claude-Code-specific notes. Claude Code reads only CLAUDE.md when it exists, so the import is required.
- **CLAUDE.local.md** = your personal notes for this project (gitignored).
- Keep instruction files short (under ~200 lines). Long procedures become skills.

Open `CLAUDE.md` for the full best-practice notes.

## Golden rule

Every new skill, subagent or workflow must be listed in `AGENTS.md`.
If it's not listed there, your agent won't know it exists.
