---
name: skill-inspector
description: >
  Inspect an existing skill and iteratively improve it. Load the skill file,
  interview the user about their goals, then build, revise, or rewrite the skill.
  Use when the user wants to improve, debug, refactor, or extend an existing skill.
  Triggers include: "inspect this skill", "improve this skill", "iterate on skill",
  "skill needs work", "fix this skill", "rewrite skill", or any invocation like
  "/skill-inspector [skill-name]".
---

# Skill Inspector

Helps you understand a skill and improve it through structured goal-setting and iteration.

## Core principle

You have two modes:
1. **Goal mode** — ask questions, say nothing about the skill's quality
2. **Inspection mode** — only entered when user explicitly asks for it ("flag issues", "what's wrong with it", "inspect it", "share your findings")

Never volunteer observations, critique, or findings during goal mode. That information is held internally until requested.

---

## Phase 1 — Load and Inspect (silent)

Before saying anything to the user, do this silently:

1. Read the target skill's SKILL.md using `view`
2. Check for bundled resources: `bash ls <skill-path>/` — if scripts/, references/, or agents/ exist, read any scripts that the SKILL.md references by name (they often contain the real logic and constraints)
3. Build an internal model of the skill covering:
   - What it does and when it triggers
   - Its execution steps and structure
   - What the bundled scripts actually do vs. what the SKILL.md claims
   - Things that look ambiguous, missing, fragile, or inconsistent
   - Things that are working well

Do NOT share this inspection. Proceed to Phase 2.

---

## Phase 2 — Goal Elicitation (relentless)

Ask the user questions until you have clear answers to ALL of these:

**Required before proceeding:**

1. **Trigger intent** — What prompted this session? ("something broke", "adding a new feature", "vague feeling it could be better", "full rewrite")
2. **Scope** — Narrow fix, targeted improvement, or ground-up rewrite?
3. **Success condition** — How will you know the improved skill is working correctly?
4. **Priority** — If multiple things are wrong or can be improved, what matters most?
5. **Constraints** — Anything that must stay the same? (interface, name, structure, bundled scripts)

Ask these as a conversation, not a form. One or two questions at a time. If the user's answer to one question resolves another, skip it. If answers are vague, probe further.

**Do not move to Phase 3 until all five are resolved.**

---

## Phase 3 — Inspection Share (only when explicitly requested)

If at any point the user says something like "flag issues", "what did you find", "what's wrong with it", "share your observations" — transition here.

Present your findings from Phase 1 in this format:

```
## Skill Inspection: <skill-name>

### Structure
- <1-line summary of what the skill does>
- Files: SKILL.md [+ any bundled resources found]

### Strengths
- <bullet per thing working well>

### Issues / Gaps
- <bullet per ambiguity, missing piece, or fragility>
  - Severity: low / medium / high
  - Why it matters: <one sentence>

### Open questions
- <anything you need the user to answer before you can form a full opinion>
```

Then ask: "Want to address any of these, or proceed with the goals we've already established?"

---

## Phase 4 — Build / Improve / Iterate

Once goals are clear (and optionally inspection shared), proceed:

1. **If narrow fix**: make the targeted change, show diff, confirm
2. **If targeted improvement**: propose the change approach first, get sign-off, then implement
3. **If rewrite**: draft a new version based on goals, present side-by-side with the original structure, iterate

For all cases:
- Show changes explicitly (before/after or diff-style)
- After each iteration, ask: "Does this meet your goal, or do you want to adjust?"
- Repeat until the user confirms it's done

---

## Phase 5 — Package

When the user is satisfied:

1. Ensure the final SKILL.md is written to `/tmp/<skill-name>/SKILL.md`
2. Copy any unchanged bundled resources (scripts/, references/) from the original skill path
3. Package:
   ```bash
   cd /tmp && zip -r /mnt/user-data/outputs/<skill-name>.skill <skill-name>/
   ```
4. Call `present_files` with the `.skill` zip path

---

## Rules

- **Never** volunteer inspection findings during Phase 2
- **Never** start implementing before goals are clear
- **Always** wait for user confirmation before moving to the next phase
- If the user skips ahead ("just fix it"), ask the minimum clarifying questions needed, then proceed
- If the user says "just vibe with me", drop the structure and follow their lead
