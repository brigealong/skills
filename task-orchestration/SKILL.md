---
name: task-orchestration
description: >-
  通用多 agent 任务治理框架。当任务复杂、可拆批、有风险且需要双角色（执行+审核）时触发。
  当用户明确说"你是编排者 / orchestrator"并要求把任务派给 executor、Execute MIMO、
  MIMO 执行、DeepSeek 执行、Opus review 或可见 Orca worker 时，也必须先用本 skill
  做派发分级和执行 contract；pane/worktree/terminal 操作交给 orca-cli，结构化消息/DAG/decision gate 交给 orchestration skill。
  核心理念：编排模型（Opus 等）写清楚约束文档，执行模型（便宜模型）照着跑完全程，不需要用户介入。
  适用于文件操作、代码重构、内容工作、数据处理、研究综合等任何可结构化的批次任务。
---

# Multi-Agent Task Orchestration

编排模型写约束文档，执行模型照着跑——约束文档的质量决定执行质量。

## 核心原则：写到能跑

**约束文档的目标是：执行 agent 拿到文档后能自主跑完全程，不需要停下来问用户。**

这意味着编排模型必须在文档里把以下内容写清楚：

| 必须写清楚的 | 写不清楚会怎样 |
|-------------|--------------|
| 任务目标和验收标准 | 执行 agent 不知道"做对了"长什么样 |
| 每个批次的具体执行项 | 执行 agent 自行猜测范围 → 漏做或多做 |
| 硬约束（红线） | 执行 agent 踩线后才知道 → 已经出事 |
| 命令/操作模板 | 执行 agent 自己编命令 → 平台不对、参数错误 |
| 升级条件 + 处置方式 | 遇到歧义时 agent 自决 → 结果不可控 |
| 阶段列和通过标准 | agent 不知道什么时候算"做完了一项" |
| 抽样验证方式 | 自检报告写"PASS"但没跑过验证命令 |

**反模式**：编排模型写了个大概 → 执行模型边做边猜 → 用户被迫每批都介入 → 失去自动化的意义。

## 派发分级：先选档，再决定要不要用本 skill

派发该写多少 spec，正比于 **复杂度 × 影响面 × 执行模型有多便宜/笨**。本 skill 是重档工具，**不是派发的必经闸门**。

| 档 | 何时 | 派发载荷 | 出自 |
|---|---|---|---|
| Tier 0 直派 | 轻、低风险、自明 | 一行 prompt；同端可连交接都省 | dispatch 决策（编排者口头判断） |
| Tier 1 仅交接 | 跨 agent/跨额度但活儿简单 | `agent-handoff` envelope 作为**载体**，但编排者必须确保其中含**内嵌最小契约**字段（见下"契约准入"） | `agent-handoff` skill（提供 envelope；不天然保证契约字段齐） |
| Tier 2 全编排 | 复杂、可拆批、有风险、要执行+审核环 | 完整约束文档（本 skill 三套模板） | 本 skill |

护栏：**默认走轻档，遇不可逆 / 宽影响面才升 Tier 2**；under-spec 让笨执行模型乱跑、返工烧的 token 往往比 spec 本身更多。
dispatch 决策还要选**派哪类目标**：Hermes 特化 profile（常驻，走 kanban）/ 现拉可见 Orca worker（pane/worktree/terminal 操作用 `orca-cli`，结构化消息/DAG/decision gate 用 `orchestration` skill）。

### 契约准入（Tier × 契约，与 making-contract 协议对齐）

派发前先确定契约来源，再看上游 `making-contract` 的终态，才决定能不能派：

| 档 | 契约要求 |
|---|---|
| Tier 0 / 1 | 派发 prompt / handoff envelope 里**内嵌最小契约**即可，不需独立文件。最小契约字段：目标、In/Out Scope、硬约束、验收标准、停机/升级条件、终态信号、权威冲突策略。 |
| Tier 2 | **必须**有 `making-contract` 产出的**独立 contract**；派发载荷带 `contract_ref`（路径）+ `contract_status`。无独立 contract 不得进 Tier 2。 |

**消费 making-contract 的三终态**（Gate 只有下游校验才成立）：

- `READY` → 可建模板 / 建执行卡 / 派发。
- `READY_WITH_ACCEPTED_RISKS` → 可派发，但**必须把风险清单（含接受者、补救责任人、期限）透传**进《执行任务说明》，不得静默丢弃。
- `BLOCKED` → **禁止**建模板、建执行卡或派发；先回 `making-contract` / 用户解未决项，再重新准入。

### 可见 Orca worker 路由原则

当用户明确任命当前 agent 为编排者，并要求把任务派给可见 worker（如 `Execute MIMO` / `MIMO 执行` / `DeepSeek 执行` / `Opus review` / executor pane）时：

- 必须先用本 skill 判断 Tier 0/1/2，并写出足够 worker 独立执行的派发 contract。
- 若任务是 Tier 2，全量使用本 skill 的三套模板；若是 Tier 0/1，也要在 prompt 中包含目标、范围、硬约束、验收和终态约定。
- **worker = 一个命名执行体，模型绑定在它身上**：优先用 OpenCode 命名 agent（`opencode --agent <name>`，模型/角色/工具绑在 agent 定义里）；Claude 变体走 Orca 借壳槽（按 agent-id 经本机 `agentCmdOverrides/Args/Env` 映射到真实 provider——这是本机 Orca 槽位配置规则）。**派发只认槽位映射的真实模型，不认 picker 标签**——标签会错位（如 `claude-agent-teams` 实跑 MiMo）。注意 `opencode --agent <name>`（OpenCode 角色名）与 `orca worktree create --agent <id>`（Orca agent-id）是两套不同的 `--agent`，勿混用。
- 启动走 Orca pane，不再用 cmux launcher。按是否需要监督环分路径：
  - 当前 worktree 加 worker：`orca terminal create --worktree active --command "<agent>" --json`
  - 现有 pane 旁分屏：`orca terminal split --terminal <handle> --direction horizontal --command "<agent>" --json`
  - **轻量交接到独立 checkout**：`orca worktree create --name <task> --agent <id> --prompt "<contract>" --json`——这是 full handoff，worker **不自动带 taskId/dispatchId、没有 worker_done 上下文**，收口靠 `orca terminal wait --terminal <handle> --for tui-idle`（常驻 TUI agent 不会 exit）或 `--for exit`（会退出的一次性命令），再 `read/show --json` 佐证。
  - **监督式 DAG**（要 worker_done / escalation / gate）：`orca worktree create --name <task> --agent <id> --json` → 取返回的 worktree id → `orca terminal list --worktree id:<newWorktreeId> --json` → `orca orchestration task-create` → `orca orchestration dispatch --inject` → `orca orchestration check --wait --types worker_done,escalation,decision_gate --timeout-ms <ms> --json`。
- 终态不用自定义 sentinel、也不用旧 cmux 的 `EXEC-DONE` marker。**按派发路径分**：监督式 `dispatch --inject` 才有 lifecycle，权威完成信号是 `orca orchestration` 的 `worker_done`（`escalation` / `decision_gate` 同为**消息类型**、非独立命令，用 `check --wait` 收）；轻量 handoff / 一次性 send 没有 worker_done 上下文，收口用 `orca terminal wait --terminal <handle> --for exit --timeout-ms <ms>`（TUI agent 用 `--for tui-idle`，spinner 偶发误判须复核），要权威信号就升级成 `dispatch`。terminal 元数据/输出只作佐证（`orca terminal show/read --terminal <handle> --json`），别当终态硬判据。另：worker 的 `Stop`/`SessionStart` hook **不具备完成语义**，别拿来当完成协议——hook 派生的 `claude --print` / memory 后台活动曾触发 phantom agent 或通知噪音（社区 #4630、#5518；PR #5543 专门过滤 print-mode hook 子进程）。
- pane / worktree / terminal 读屏、focus、切换用 `orca-cli`（`terminal list/read/show/switch`）；结构化消息、派发、决策门用 `orchestration` skill。**`wait`/`read`/`show` 一律显式带 `--terminal <handle>` + `--json`**，否则焦点变化时会等/读到当前 orchestrator pane。
- 工具无关护栏（删除安全 / 高风险门 / 不可逆确认见下文 Guardrails 节，这里补 Orca 特有的）：启动失败不宣称"已派发"（fail loud）；确认 worker 在正确 worktree/cwd 启动；默认不前台长阻塞（靠 worker_done/wait，不 tight-loop）；reviewer 用完关闭、不常驻。
- 布局默认从简：`<= 4` 个长期角色放同一 worktree，executor 按需 split；`> 4` 才拆 worktree。
- 启动后只做一次 `orca terminal read --terminal <handle> --json` 确认 worker 已接管 pane；之后靠 worker_done / wait 或慢速 re-check，不 tight-loop。
- **完成即推送（默认开）**：收到权威终态后——监督式的 `worker_done`、或轻量路径 `wait` 返回收口——推一条 ntfy 让用户在手机/安卓收到：`python3 ~/.claude/hooks/ntfy_push.py "worker done" "<worker/任务名> 完成 · <一句话结果>"`。这与原生 Task 子 agent 的 `SubagentStop` hook 互补：后者由 hook 自动触发，Orca worker 无该 hook，故在此由 orchestrator 显式推。**只在权威终态推**，别在每次 re-check / 中间态 / escalation 等待中推（会刷屏）；推送失败静默、不阻塞收口（`ntfy_push.py` 恒不抛错）。

### Hermes profile 路由

当 dispatch 决策选择 Hermes 时，编排者只做 Kanban 写入和路由，不直接模拟 worker。Hermes gateway 的 dispatcher 会在下一轮 tick 中按卡片 `assignee` 拉起对应 profile。

| Profile | 用途 | 不用于 |
|---|---|---|
| `personal-research` | 用户入口、任务图规划、根卡/审批门控、异常处置、汇总 | 普通执行 worker、独立最终审核 |
| `research-executor` | 文献采集、CNKI/浏览器、OCR、Zotero 写回、确定性文件处理、按 spec 执行卡片 | 最终学术判断、审批、独立验收 |
| `research-reviewer` | 独立核验、证据对账、里程碑/最终 review、质量审计 | 直接修改执行产物、替 executor 返工 |
| `work-assistant` | 工作域 hands-on：信息检索、内容整理、社媒发布、桌面/浏览器自动化、识图（computer use / browser / vision），经飞书协作 | 学术研究执行/审核（走 research-* ring）、独立学术验收 |

> `work-assistant` 是与 `personal-research` 并列的**工作域入口/动手 persona**，不在 research executor/reviewer 审核环内；派工作类 hands-on 卡时可作 `assignee`，但学术研究批次仍走三研究 profile。

派发模板：

```bash
# 1. 建卡时显式指定可 spawn 的 Hermes profile；先 blocked，避免规格未稳就被执行。
hermes kanban create "<title>" \
  --body "<self-contained task contract>" \
  --assignee research-executor \
  --initial-status blocked \
  --idempotency-key "<stable-key>"

# 2. 规格和审批门通过后再转 ready；ready 卡会被 gateway dispatcher 拾取。
hermes kanban assign <task_id> research-executor
hermes kanban unblock <task_id> --reason "<why ready>"
# 对 todo/triage 规格卡：hermes kanban promote <task_id> --reason "<why ready>"

# 3. 可手动预检一次；真实常态由 gateway tick 自动派发。
hermes kanban dispatch --dry-run --json
```

规则：
- `assignee` 必须是实际存在的 Hermes profile；非 Hermes lane 会被 dispatcher 归为 non-spawnable。
- 任务图里的 `agent_profile` 是 plan-time 建议属主；投影到 Kanban 后，以卡片 `assignee` 和运行期 attempt 的 `actual_runtime` 为准。
- 换 profile 等于换执行者：必须新记 attempt，并如实标 `actual_runtime`，不能静默把 executor/reviewer/orchestrator 角色塌缩到同一 profile。
- 高风险或外部副作用任务（下载、写 Zotero、写飞书、删除/覆盖）仍受本 skill 的高风险门约束；确认 profile 不等于批准副作用。
- **结构归属（防双 SOT）**：走 Hermes / 任务图时，节点、依赖、批次的**结构设计归 `task-graph-planner` 独占**；graph 批准后，本 skill **只为每个已批准节点编译执行 contract 与审核环**，不另立第二套结构。此路径下运行态 SOT 是 **Kanban + projection receipt + graph markers**，**不**用 `进度表.md` 当第二运行态（`进度表.md` 只用于非 Hermes 的本地批次执行）。任务图顶层可记 `user_contract_ref` + `contract_status`，但 graph 不得充当用户验收契约。

## Scope

Use this skill when:
- 任务可拆为多个批次，每批有独立的执行-自检-审核周期
- 涉及高风险或难以回退的操作
- 需要编排模型和执行模型分离（责任分离）
- 希望执行 agent 自主完成，不需要用户逐步确认

Do not use this skill for:
- Tier 0/1 任务（轻任务直派、或简单跨端只需 `agent-handoff` envelope）——见上"派发分级"
- 单 agent 简单任务（几项清单 + 无审计需求）
- 纯探索性任务（没有明确的"完成"标准）
- 已有测试框架全覆盖的纯代码开发

## Workflow

### 1. 理解任务并规划

编排模型在动手写文档前，先回答这些问题：

- **目标**：任务要达成什么结果？
- **工作单元**：什么是一项？（一个文件？一个模块？一篇文档？一条数据？）
- **批次划分**：怎么分批？按优先级、按类别、按模块？
- **风险点**：哪些操作不可逆？哪些会破坏现有系统？
- **执行环境**：什么平台？什么工具链？
- **验证方式**：怎么证明"做对了"？

### 2. 创建任务目录

在工作区中创建任务目录，路径由编排模型按实际决定。建议结构：

```
<任务目录>/
├── 执行任务说明.md    ← 模板 A
├── 进度表.md          ← 模板 B
├── 验收规范.md        ← 模板 C
├── <配套规则文件>     ← 任务特有的规则/映射
├── reports/           ← 自检报告
└── logs/              ← 执行日志（如适用）
```

### 3. 填写三套模板

从 `references/` 下复制三套模板到任务目录：

- **模板 A**：`references/template-execution.md` → `执行任务说明.md`
  - 写清楚任务目标、范围、硬约束、命令模板、升级条件
  - **关键**：命令模板必须是可直接执行的，不能写"自行选择合适的命令"

- **模板 B**：`references/template-progress.md` → `进度表.md`
  - 列出所有执行项，按批次分组
  - 定义阶段列（参考模板中的"阶段列设计"节）
  - 预留冲突队列和待澄清队列

- **模板 C**：`references/template-acceptance.md` → `验收规范.md`
  - 自检 6 项检查已定义好框架，根据任务填写具体验证方式
  - 审核方命令式复核——写出具体要跑什么命令

详见 `references/templates.md`。

### 4. 启动执行循环

```
执行 agent 按批次推进
  → 每项：按阶段列逐列完成
  → 每批：自检 → 写报告 → 申请审核
审核 agent 命令式复核
  → 三态结论：PASS / CONDITIONAL PASS / FAIL
  → 若 CONDITIONAL PASS：出整改单
执行 agent 整改
  → 写整改自检报告
  → 审核方复核
最后一批通过后
  → 整任务终验
  → 签收
```

**三态结论语义（与上游 contract / making-contract Evaluation 同一套，不得错位）：**

- **PASS**：满足 contract 全部 Must。
- **CONDITIONAL PASS**：**仅当**遗留项落在 contract 明确定义的可接受遗留范围内（即 `READY_WITH_ACCEPTED_RISKS` 或 contract 里标为可缺的 Should），且记录**批准者、责任人、期限**才成立。它是"可批准的条件接受"，不是"待整改"。
- **FAIL**：结果不合规。**遗留项超出 contract 可接受范围但可修的，走 FAIL（如需区分可标 `REMEDIATION_REQUIRED`）并出整改单——不要把这种情况复用成 CONDITIONAL PASS。**

### 5. 审核方命令式复核

审核方不只读报告，要现场跑命令验证。核心验证命令见 `references/check-commands.md`。

**计数校验 + 完整性检查是性价比最高的验证**——一行命令发现多个问题。

### 6. 整改分类

不是所有问题都需要返工：

| 类型 | 准则 | 动作 |
|---|---|---|
| 结果不合规 | 目标态错误 | 必须返工 |
| 结果合规 + 流程偏离 | 目标对但过程偏 | 记教训不返工 |
| 文档不一致 | 报告/索引与实际不符 | 改文档不动实际产出 |
| 治理产物缺失 | README/索引漏建 | 补建即可 |

## Guardrails

### 高风险门

以下动作需用户确认（这是唯一的用户介入点）：
- 实际删除/销毁数据
- 修改不属于任务范围的系统/结构
- 跨批次执行（跳过当前批次直接做下一批）
- 超出原始任务范围的扩展

### 删除安全规则

- **所有删除/清理动作必须进入系统回收站**，禁止永久删除。
- macOS：使用 `trash` 命令。
- Windows：使用回收站 API（`Shell32` 或 `Microsoft.VisualBasic`）。
- 如果无法确认回收站支持，**停止删除动作并请求用户确认**。

### 安全默认

- 所有操作默认不覆盖已有产出
- 冲突默认进队列，不自动处理
- hold 项默认保持 hold，不自动释放
- 软约束默认视为可选——关键约束必须写在硬约束段

### 子 agent 启动边界

- **默认不自动 spawn**：若用户未明确要求，按"执行角色 → 审核角色"在同一个 agent 上顺序模拟。
- **显式授权才 spawn**：只有当用户明确要求多 agent 时才 spawn。
- **spawn 后仍受 guardrails 约束**：删除安全、高风险门、安全默认对所有子 agent 生效。

## Anti-Patterns

启动新任务前，务必阅读 `references/anti-patterns.md` 中的 9 条反模式和快速检查表。

核心教训：
- 软约束 = 会被忽略 → 关键项升级为硬约束
- 文档约束没有执行硬门 → 关键条件做成可执行脚本
- 自检报告掩盖问题 → 审核方必须独立验证
- 二态验收导致过度返工 → 用三态结论
- 派发机制选错 → 完成信号/await 机制是一等决策（监督式用 worker_done，轻量用后台 wait，不前台轮询）

## References

- `references/templates.md` — 模板索引与占位符说明
- `references/template-execution.md` — 模板 A：执行任务说明
- `references/template-progress.md` — 模板 B：进度表
- `references/template-acceptance.md` — 模板 C：验收规范
- `references/check-commands.md` — 验证命令模式库（双平台）
- `references/anti-patterns.md` — 反模式清单（从真实任务中提炼）
