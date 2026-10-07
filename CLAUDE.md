# CLAUDE.md

<!--
Best practice (this comment is for humans; Claude Code strips it before loading, so it costs 0 tokens):

1. AGENTS.md is the single source of truth, shared with Codex and Cursor.
   Claude Code reads only CLAUDE.md when one exists, so we import AGENTS.md with the @ line below.
2. Put only Claude-Code-specific things in this file. Everything else goes in AGENTS.md.
3. Keep instruction files short (under ~200 lines). Concrete rules beat vague ones:
   "Max 5 bullet points" works, "be concise" doesn't.
4. Multi-step procedures don't belong here. Make them a skill (skills/<name>/SKILL.md).
5. Where instructions live:
   ~/.claude/CLAUDE.md   → you, in every project
   ./CLAUDE.md           → everyone on this project (committed)
   ./CLAUDE.local.md     → you, this project only (gitignored)
   <subfolder>/CLAUDE.md → loads only when Claude works in that folder
6. Guardrails here are instructions: the model follows them, but nothing enforces them.
   For a hard block, also add a deny rule in .claude/settings.json (we block reading .env files there).
-->

@AGENTS.md

## Guardrails

- Never read, print or edit `.env` files or other files with secrets. If you need a value, ask me.
- Always ask for my approval before anything that spends money (paid APIs, ads, purchases, cloud resources).
- Always ask before anything that leaves this computer: sending emails or messages, publishing, posting.
- Always ask before deleting files or anything else you can't undo.

## Claude Code specifics

- Skills in `skills/` and subagents in `agents/` are also linked into `.claude/`, so Claude Code loads them natively (`/agents` lists subagents).
- Run subagents with the Agent tool, one per step, passing only what that step needs.
- When I say "remember …", write it to the Memory section of `AGENTS.md`, not to Claude's own memory, so every tool sees it.
