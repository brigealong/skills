# Agent Workflow Skills

Three reusable skills for defining, coordinating, and transferring agent work.

| Skill | Use it when |
|---|---|
| [`making-contract`](making-contract/) | A design or goal needs explicit scope, acceptance examples, and PASS/FAIL criteria before execution. |
| [`agent-handoff`](agent-handoff/) | Work must move between agents, runtimes, repositories, or Feishu/Lark while preserving a resumable checkpoint. |
| [`task-orchestration`](task-orchestration/) | A complex, risky, multi-batch task needs an execution contract, progress tracking, and independent review. |

## Install

Clone the repository, then copy only the skill directories you need into your
agent's skill directory:

```bash
git clone https://github.com/brigealong/skills.git
mkdir -p ~/.agents/skills
cp -R skills/making-contract ~/.agents/skills/
cp -R skills/agent-handoff ~/.agents/skills/
cp -R skills/task-orchestration ~/.agents/skills/
```

Restart or reload your agent runtime after installation. Skill discovery and
invocation syntax depend on the runtime; each directory is self-contained and
starts with a `SKILL.md`.

## Requirements

- `making-contract`: no runtime dependency; it is an instruction-only skill.
- `agent-handoff`: Python 3.11+ and Git for `file-git` handoffs. Its optional
  Feishu transport expects an existing CC Connect installation and local
  workspace configuration.
- `task-orchestration`: instruction-only by default. Commands involving Orca,
  Hermes, Feishu, or other workers require those tools to be installed and
  configured separately.

Read each skill's `SKILL.md` and local references before use. Tool names and
paths in workflow examples are environment-specific; adapt them to the runtime
that will execute the work.

## License

[MIT](LICENSE)
