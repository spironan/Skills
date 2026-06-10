---
name: project-bootstrap
description: Bootstrap a new project's knowledge layer by interviewing the user across a fixed taxonomy of concerns, then generating a CONTEXT.md index and separate detail files. Use this skill whenever the user wants to set up a new project, bootstrap project context, create project documentation for LLM consumption, initialize a knowledge layer, or says "bootstrap this project", "set up project context", "new project setup". Also trigger when the user has a new codebase and wants to document its architecture, conventions, and decisions for future sessions.
---

# Project Bootstrap

Generate a project's knowledge layer through a structured interview, producing a stable CONTEXT.md index and separate detail files optimized for both human reading and LLM context caching.

## Why this structure matters

LLM context caching works on prefix stability — content that doesn't change stays cached. A single monolith file invalidates the entire cache on any edit. By splitting into a small, stable index (CONTEXT.md) and separate detail files, only the changed file costs tokens on re-read. The index stays in cache across almost every session.

## Output structure

```
project-root/
├── CONTEXT.md              ← stable index, rarely changes (~50-80 lines)
└── docs/
    ├── stack.md            ← languages, frameworks, runtimes
    ├── architecture.md     ← boundaries, data flow, state
    ├── data.md             ← storage, schemas, migrations, caching
    ├── conventions.md      ← naming, file structure, code style, commits, branching
    ├── testing.md          ← strategy, frameworks, coverage
    ├── deployment.md       ← environments, CI/CD, infra
    ├── team-workflow.md    ← PR process, review norms, ownership
    ├── constraints.md      ← performance, compliance, accessibility, platform
    └── adr/
        └── 0001-<title>.md ← one file per architectural decision
```

Not every project needs every file. If a domain has no decisions yet, skip the file entirely — don't generate stubs. CONTEXT.md only links to files that exist.

## CONTEXT.md format

```markdown
# <Project Name>

<One paragraph: what this is, who it's for, what problem it solves.>

## Quick reference

| Concern | Detail |
|---------|--------|
| Stack | [docs/stack.md](docs/stack.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| ... | ... |

## Decisions

| ID | Date | Decision | Detail |
|----|------|----------|--------|
| ADR-0001 | YYYY-MM-DD | <short title> | [docs/adr/0001-<title>.md](docs/adr/0001-<title>.md) |

## Open items

- <thing explicitly not yet decided, with enough context to revisit later>
```

The quick reference table only includes rows for files that were generated. Keep this file under 80 lines. It is an index, not a summary — don't duplicate content from detail files.

## Detail file format

Each detail file follows the same pattern:

```markdown
# <Concern>

<2-3 sentence summary of the current state.>

## Decisions

- <Decision>: <rationale in one sentence>

## Specifics

<The actual content — concrete, not aspirational. What IS, not what SHOULD BE.>
```

Write detail files in concrete, factual language. "We use PostgreSQL 16 on RDS" not "A relational database should be considered." If something is undecided, it belongs in CONTEXT.md's open items, not in a detail file as a hedge.

## ADR format

```markdown
# ADR-<NNNN>: <Title>

**Date**: YYYY-MM-DD
**Status**: accepted | proposed | superseded by ADR-NNNN

## Context

<What forced this decision.>

## Decision

<What was decided.>

## Consequences

<What follows from this — both positive and negative.>
```

Generate an ADR for any decision where the rationale is non-obvious or where the team might later ask "why did we do it this way?" Not every decision needs an ADR — only the ones worth explaining.

## Interview process

Walk through the following domains in order. Ask one question at a time. For each domain, provide a recommended answer based on what you've learned so far — the user can accept, modify, or reject.

If a question can be answered by exploring an existing codebase (checking package.json, reading folder structure, inspecting config files), do that instead of asking.

### Domain sequence

1. **Project identity** — name, purpose, problem it solves, target users
2. **Stack** — languages, frameworks, runtimes, package managers, key dependencies
3. **Architecture** — monolith/microservices, module boundaries, data flow, state management
4. **Data** — storage engines, schema approach, migrations, caching
5. **Conventions** — naming, file/folder structure, code style tools, commit format, branching model
6. **Testing** — strategy (unit/integration/e2e), frameworks, coverage targets
7. **Deployment** — environments, CI/CD, hosting, infra-as-code
8. **Team workflow** — PR process, review expectations, ownership model
9. **Constraints** — performance budgets, compliance requirements, accessibility, platform/browser support
10. **Open decisions** — things explicitly deferred, with context on why and when to revisit

### Interview rules

- One question per turn. Wait for the answer before moving on.
- If the user's answer is ambiguous, follow up on that specific point before advancing.
- If the user says "skip" or "not applicable", drop the domain — don't generate a file for it.
- If the user says "default" or "you decide", pick a reasonable default and state it clearly. The user can override.
- Track which domains are complete. When all 10 are resolved (answered or skipped), move to generation.
- Before generating, present a summary of all decisions and let the user confirm or amend.

### Codebase inference

If a codebase already exists, read it before starting the interview:

1. Check for package.json, Cargo.toml, go.mod, pyproject.toml, etc. — infer stack.
2. Scan folder structure — infer architecture patterns.
3. Check for .eslintrc, prettier, .editorconfig — infer conventions.
4. Check for CI configs (.github/workflows, Jenkinsfile, etc.) — infer deployment.
5. Check for test directories and config — infer testing approach.

Present inferences as "Here's what I found — confirm or correct" rather than re-asking what's already visible.

## Generation phase

After the interview is confirmed:

1. Create `docs/` directory and `docs/adr/` if any ADRs are needed.
2. Generate each detail file for domains that were not skipped.
3. Generate ADRs for decisions with non-obvious rationale.
4. Generate CONTEXT.md last — it references the files above.
5. Present all files for review.

### Regeneration rules

If the user wants to change a decision after generation:

- Regenerate only the affected detail file(s).
- Update CONTEXT.md's table rows only if a file was added or removed.
- Do not regenerate unaffected files. State which files were changed and why.

This keeps token cost proportional to the change, not the project size.
