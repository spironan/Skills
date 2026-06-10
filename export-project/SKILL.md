---
name: export-project
description: >
  Export all project knowledge — instructions, uploaded files, and chat history —
  into a downloadable package optimized for a target LLM platform (Claude.ai,
  Claude Code, ChatGPT, or Cursor). Use this skill whenever the user wants to
  back up a project, migrate, share context, or hand off to another LLM.
  Triggers include: "export project", "backup project", "zip project",
  "migrate project", "share project context", "export everything",
  "export for ChatGPT", "export for Cursor", "export for Claude Code",
  "package project for another account".
---

# Export Project

Produces a structured export package containing all project knowledge,
formatted for the target platform. No skills are included in exports.

## Supported platforms

| Platform | Primary artifact | How to use |
|----------|-----------------|------------|
| `claude` | Folder of files | Upload each file to Claude.ai project → Files |
| `claude-code` | `CLAUDE.md` | Drop in project root |
| `chatgpt` | `system_prompt.md` + `knowledge/` | Paste prompt; upload knowledge files |
| `cursor` | `.cursorrules` + `context/` | Drop in project root |

---

## Step 0 — Select platform

If the user hasn't already specified a platform, ask:
> "Which platform are you exporting for — Claude.ai, Claude Code, ChatGPT, or Cursor?"

Use their answer to determine output structure in Step 2.

---

## Step 1 — Collect static assets

```bash
python /mnt/skills/user/export-project/scripts/bundle.py \
  --staging-dir /tmp/project-export-stage
```

Wait for output. Note what was found (uploads count, transcripts count).

---

## Step 2 — Write platform content

### Platform: `claude`

Output structure:
```
project-export/
├── IMPORT.md
├── instructions.md
├── chat_history.md
└── uploads/           ← already staged by bundle.py
```

**Write `instructions.md`** from your system prompt / project instructions context:
```markdown
# Project Instructions

> Exported from: <project name if known, otherwise "Claude.ai project">
> Exported at: <timestamp from meta.json>

<verbatim instructions text>
```

**Write `chat_history.md`** — see Chat History section below.

**Write `IMPORT.md`**:
```markdown
# Project Export — Claude.ai Import Guide

Exported: <timestamp>

## Steps
1. Create a new project in Claude.ai
2. Paste `instructions.md` content into Settings → Project Instructions
3. Upload all files from `uploads/` to the project Files section
4. Upload `chat_history.md` to the project Files section
5. Start a conversation and ask Claude to summarise what it knows

## Notes
- Sensitive values (API keys, secrets) may be present — review before sharing.
- Chat history is a lossy compaction; verbatim exchanges are not preserved.
```

---

### Platform: `claude-code`

Output structure:
```
project-export/
├── CLAUDE.md          ← single consolidated context file; drop in project root
└── uploads/           ← reference files, if any
```

**Write `CLAUDE.md`** — merge instructions + chat summary into one file:
```markdown
# Project Context

> Platform: Claude Code
> Exported at: <timestamp>

## Instructions
<verbatim project instructions>

## Chat History (Compacted)
<compact summary — same format as chat_history.md below>

## Reference Files
<list any files in uploads/ with one-line description each>
```

No IMPORT.md needed — just drop `CLAUDE.md` in the project root and place
`uploads/` alongside it or reference them as needed.

---

### Platform: `chatgpt`

Output structure:
```
project-export/
├── IMPORT.md
├── system_prompt.md
└── knowledge/
    ├── project_context.md
    └── chat_history.md
```

**Write `system_prompt.md`** — distill instructions into a ChatGPT-style system prompt:
```markdown
# System Prompt

<Rewrite project instructions as a direct, second-person system prompt.
 E.g. "You are an assistant working on X. Your conventions are Y. Always do Z.">
```

**Write `knowledge/project_context.md`** — key project context as a knowledge document:
```markdown
# Project Context

> Exported at: <timestamp>

## Overview
<1–3 paragraph summary of what this project is and its current state>

## Key Decisions
<bullet list of architectural/design decisions>

## Conventions
<bullet list of naming, style, structural conventions>
```

**Write `knowledge/chat_history.md`** — see Chat History section below.

**Write `IMPORT.md`**:
```markdown
# Project Export — ChatGPT Import Guide

Exported: <timestamp>

## Steps
1. Open ChatGPT → Your Projects (or GPT Builder for a custom GPT)
2. Paste `system_prompt.md` content into the Instructions field
3. Upload both files from `knowledge/` as knowledge files
4. Start a conversation and ask it to summarise the project

## Notes
- ChatGPT knowledge files are searched, not always fully loaded — keep them concise.
- Sensitive values may be present — review before sharing.
```

---

### Platform: `cursor`

Output structure:
```
project-export/
├── IMPORT.md
├── .cursorrules
└── context/
    └── chat_history.md
```

**Write `.cursorrules`** — combine instructions + key conventions into Cursor rules format:
```
# Project Rules

## Overview
<2–3 sentence summary of what this project is>

## Instructions
<project instructions, rewritten as imperative rules>

## Conventions
<bullet list of coding, naming, structural conventions>

## Key Decisions
<bullet list of important prior decisions the AI should respect>
```

**Write `context/chat_history.md`** — see Chat History section below.

**Write `IMPORT.md`**:
```markdown
# Project Export — Cursor Import Guide

Exported: <timestamp>

## Steps
1. Drop `.cursorrules` into your project root
2. Optionally add `context/chat_history.md` to your project for additional background
3. Open Cursor — it will automatically pick up `.cursorrules`

## Notes
- `.cursorrules` is loaded on every request; keep it focused and avoid bloat.
- Sensitive values may be present — review before sharing.
```

---

## Chat History format (all platforms)

Check `/tmp/project-export-stage/transcripts_raw/` for transcript files.

**If transcripts exist**, produce a compact information-dense summary:
```markdown
# Chat History (Compacted)

> Sessions: N  |  Compacted at: <timestamp>

## Session <date>

### Decisions
- <bullet per architectural/design decision>

### Work Done
- <bullet per completed task with key outcome>

### Key Artifacts
- <file/path created or modified — one-liner>

### Open Items
- <anything left explicitly unresolved>
```

Rules:
- Omit pleasantries, clarifications, tool output verbatim dumps
- Preserve: decisions, rationale, file paths, error resolutions, open questions
- Each session ≤ 50 lines unless unusually dense

**If no transcripts exist**, write:
```markdown
# Chat History (Compacted)

No prior chat history found at export time.
```

---

## Step 3 — Zip and present

```bash
python /mnt/skills/user/export-project/scripts/zip_stage.py \
  --staging-dir /tmp/project-export-stage \
  --output /mnt/user-data/outputs/project-export-<platform>.zip
```

Then call `present_files` with the zip path.

---

## Edge cases

| Situation | Handling |
|-----------|----------|
| No uploads | `uploads/` absent from zip; note in IMPORT.md |
| No transcripts | `chat_history.md` / relevant file contains placeholder |
| No project instructions | Write placeholder noting none were set |
| Very large uploads | Copy as-is; warn user zip may be large |
| Platform not specified | Ask before proceeding |
