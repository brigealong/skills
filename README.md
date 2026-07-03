# Agent Workflow Skills

**Your agent can build the wrong thing — correctly.**

It follows the plan, passes its own checks, and still misses what you
actually wanted. Brainstorming skills sharpen the idea and planning skills
sequence the work, but nothing in between pins down *what "done" means*.
That's the gap these skills close.

## The flagship: `making-contract`

Before any plan is written or any work is dispatched, `making-contract`
turns intent into a one-page contract with five sections:

| Section | The question it answers |
|---|---|
| **Intent** | Why does this task exist? (purpose, never solution) |
| **Scope** | What's in — and what adjacent work is explicitly *out*? |
| **Acceptance** | What Must hold, checkable by command, human, or LLM judge? |
| **Examples** | At least one good and one bad sample — the anchor that draws the decision boundary |
| **Evaluation** | How each Must is checked, with three result states: PASS / CONDITIONAL PASS / FAIL |

A two-layer readiness gate catches the classic trap — a contract with all
five sections filled in that is still semantically empty — and every run
ends in an explicit state: **READY**, **READY WITH ACCEPTED RISKS**, or
**BLOCKED**. Never a vague "looks good".

TDD tests your code. A contract tests your intent. And once "done" is
verifiable, it becomes safe to hand execution to a cheaper model or an
unattended agent — the contract is what makes delegation cheap.

It slots into skill chains you may already run:

```text
brainstorming / grilling  →  making-contract  →  writing-plans / orchestration
      (explore)                 (pin down)              (execute)
```

## Companion skills

| Skill | Use it when |
|---|---|
| [`agent-handoff`](agent-handoff/) | Work must move between agents, runtimes, or repositories with a resumable checkpoint. |
| [`task-orchestration`](task-orchestration/) | A complex, risky, multi-batch task needs an execution brief, progress tracking, and independent review. The orchestrating model writes the constraints; a cheaper model runs the whole batch. |

## Install

Copy the skill directories you need into your agent's skill directory:

```bash
git clone https://github.com/brigealong/skills.git
mkdir -p ~/.agents/skills
cp -R skills/making-contract ~/.agents/skills/
```

Each directory is self-contained and starts with a `SKILL.md`; detail lives
in `references/` and is loaded on demand. Restart or reload your agent
runtime after installation.

- `making-contract` — instruction-only; no runtime dependency.
- `agent-handoff` — Python 3.11+ and Git for `file-git` handoffs; the
  optional Feishu transport expects an existing CC Connect setup.
- `task-orchestration` — instruction-only; backend-agnostic. Wire it to
  whatever dispatch mechanism your environment provides (sub-agents, terminal
  panes, a kanban, CI jobs) via your own `references/` backend file.

## License

[MIT](LICENSE)
